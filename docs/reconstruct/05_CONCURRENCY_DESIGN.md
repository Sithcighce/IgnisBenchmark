# 并发控制详细设计

**设计日期**: 2025-10-14  
**目标**: 清晰、高效、可控的并发架构

---

## 🎯 核心问题

### 当前问题诊断

**config.yaml的混乱**:
```yaml
# 问题1: 配置项名称不清晰
rounds_concurrency: 3              # 是什么的并发？
round_internal_concurrency: 5      # "内部"指什么？

# 问题2: 实际行为不匹配
# 配置说 round_internal_concurrency: 5
# 但 QuestionGenerator 是串行的！（只有1个API调用）
# 只有 AnsweringModule 用了 ThreadPoolExecutor(5)

# 问题3: 层次不清
max_concurrent_requests: 10        # 这是哪一层的？
```

**代码中的混乱**:
```python
# main.py - 完全串行
for round_num in range(total_rounds):
    questions = generator.generate()     # 串行
    for q in questions:
        q = answerer.answer(q)           # 内部并发(5)
    for q in questions:
        result = grader.grade(q)         # 串行
```

---

## 🏗️ 新并发模型

### 三层并发架构

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: Batch Level (批次级并发)                      │
│  控制多少个"批次"同时处理                                │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Paper 1  │  │ Paper 2  │  │ Paper 3  │  ← 3并发    │
│  │ (20题)   │  │ (20题)   │  │ (20题)   │             │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘             │
└───────┼─────────────┼─────────────┼────────────────────┘
        │             │             │
        ▼             ▼             ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 2: Stage Level (阶段级并发)                      │
│  控制每个阶段内的并发度                                  │
│                                                          │
│  Paper 1 的处理流程：                                    │
│  ┌──────────┐                                           │
│  │ 生成阶段  │  ← 1个LLM调用 → 20题                     │
│  └────┬─────┘                                           │
│       │                                                  │
│  ┌────▼─────────────────────────────────────┐          │
│  │ 解题阶段 (20题并发处理)                  │          │
│  │ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐              │          │
│  │ │Q1│ │Q2│ │Q3│ │Q4│ │Q5│ ← 5并发       │          │
│  │ └──┘ └──┘ └──┘ └──┘ └──┘              │          │
│  └────┬─────────────────────────────────────┘          │
│       │                                                  │
│  ┌────▼─────────────────────────────────────┐          │
│  │ 判题阶段 (20题并发处理)                  │          │
│  │ ┌──┐ ┌──┐ ┌──┐                          │          │
│  │ │Q1│ │Q2│ │Q3│ ← 3并发                  │          │
│  │ └──┘ └──┘ └──┘                          │          │
│  └────┬─────────────────────────────────────┘          │
└───────┼──────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 3: Request Level (请求级限流)                    │
│  全局控制所有API请求的总并发数和速率                     │
│                                                          │
│  ┌─────────────────────────────────────────┐           │
│  │  Semaphore(10)  - 最多10个并发请求      │           │
│  │  RateLimiter(5/s) - 每秒最多5个请求     │           │
│  └─────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 详细配置设计

### 新config.yaml结构

```yaml
concurrency:
  # ===== Layer 1: 批次级并发 =====
  batch_level:
    # 同时处理多少篇论文/批次
    max_concurrent_batches: 3
    
    # 每批的题目数量
    questions_per_batch: 20
    
    # 批次调度策略
    scheduling: "fair"  # fair | priority | round_robin
  
  # ===== Layer 2: 阶段级并发 =====
  stage_level:
    # 生成阶段
    generation:
      # 生成不并发（1个API调用生成N题）
      concurrency: 1
      # 是否启用批量生成
      batch_mode: true
    
    # 解题阶段
    answering:
      # 同时解答多少道题
      concurrency: 5
      # 超时时间（秒）
      timeout: 120
      # 是否允许部分失败
      allow_partial_failure: true
    
    # 判题阶段
    grading:
      # 同时判多少道题
      concurrency: 3
      # 超时时间（秒）
      timeout: 60
      # 是否允许部分失败
      allow_partial_failure: true
  
  # ===== Layer 3: 请求级限流 =====
  request_level:
    # 全局最大并发请求数（跨所有阶段）
    max_concurrent_requests: 10
    
    # 速率限制
    rate_limit:
      # 每秒最多发送多少个请求
      requests_per_second: 5.0
      # 突发容量（令牌桶大小）
      burst_size: 10
    
    # 连接池配置
    connection_pool:
      size: 20
      keepalive: 30
      timeout: 300
```

### 配置说明

#### Batch Level - 适用场景
- **Milestone 2**: 100篇论文，设置`max_concurrent_batches: 3`
  - 同时处理3篇论文
  - 每篇论文独立完成"生成→解题→判题"流程

#### Stage Level - 每个阶段的策略
- **Generation** (生成): `concurrency: 1`
  - 原因：1次LLM调用生成20题，无需并发
  - 批次间并发已在Batch Level控制
  
- **Answering** (解题): `concurrency: 5`
  - 20道题分5组并发处理
  - 每组处理时间约30秒
  - 总时间：30秒 × 4组 = 2分钟
  
- **Grading** (判题): `concurrency: 3`
  - 20道题分7组并发处理
  - 每组处理时间约20秒
  - 总时间：20秒 × 7组 = 2.3分钟

#### Request Level - 全局保护
- **为什么需要？**
  - 防止过多请求压垮API
  - 遵守API提供商的速率限制
  - 控制成本（某些API按请求数计费）

- **如何工作？**
  ```python
  # 所有阶段共享一个Semaphore
  global_semaphore = asyncio.Semaphore(10)
  
  # 发送任何请求前都要获取许可
  async with global_semaphore:
      response = await call_api()
  ```

---

## 🔧 实现细节

### 1. 批次级并发实现

```python
class BatchProcessor:
    """批次级并发处理器"""
    
    def __init__(self, config: ConcurrencyConfig):
        self.max_concurrent = config.batch_level.max_concurrent_batches
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
    
    async def process_batches(
        self, 
        papers: List[Paper]
    ) -> List[Result]:
        """
        并发处理多个批次
        
        示例：100篇论文，max_concurrent=3
        - 第1批: Paper 1, 2, 3 (并发)
        - 第2批: Paper 4, 5, 6 (并发)
        - ...
        """
        
        tasks = []
        for paper in papers:
            task = asyncio.create_task(
                self._process_single_batch(paper)
            )
            tasks.append(task)
        
        # 等待所有完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    
    async def _process_single_batch(self, paper: Paper) -> Result:
        """处理单个批次（带并发控制）"""
        
        # 获取批次级许可
        async with self.semaphore:
            logger.info(f"开始处理: {paper.id}")
            
            # 完整的流水线
            result = await self.pipeline.process(paper)
            
            logger.info(f"完成处理: {paper.id}")
            return result
```

### 2. 阶段级并发实现

```python
class StageConcurrencyManager:
    """阶段级并发管理器"""
    
    def __init__(self, config: StageLevelConfig):
        # 每个阶段独立的并发控制
        self.generation_sem = asyncio.Semaphore(
            config.generation.concurrency
        )
        self.answering_sem = asyncio.Semaphore(
            config.answering.concurrency
        )
        self.grading_sem = asyncio.Semaphore(
            config.grading.concurrency
        )
    
    async def run_stage(
        self,
        stage: PipelineStage,
        tasks: List[Callable]
    ) -> List[Result]:
        """运行某个阶段的所有任务"""
        
        # 选择对应的信号量
        if stage == PipelineStage.GENERATION:
            semaphore = self.generation_sem
        elif stage == PipelineStage.ANSWERING:
            semaphore = self.answering_sem
        else:  # GRADING
            semaphore = self.grading_sem
        
        # 并发执行
        async def run_with_sem(task):
            async with semaphore:
                return await task()
        
        results = await asyncio.gather(
            *[run_with_sem(task) for task in tasks],
            return_exceptions=True
        )
        
        return results
```

### 3. 请求级限流实现

```python
class GlobalRateLimiter:
    """全局速率限制器（单例）"""
    
    _instance = None
    
    def __new__(cls, config: RequestLevelConfig):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init(config)
        return cls._instance
    
    def _init(self, config: RequestLevelConfig):
        # 全局信号量
        self.global_semaphore = asyncio.Semaphore(
            config.max_concurrent_requests
        )
        
        # 令牌桶限流器
        self.rate_limiter = TokenBucket(
            rate=config.rate_limit.requests_per_second,
            capacity=config.rate_limit.burst_size
        )
    
    async def acquire(self):
        """获取请求许可（会阻塞直到有资源）"""
        
        # 1. 获取并发槽位
        await self.global_semaphore.acquire()
        
        # 2. 获取速率令牌
        await self.rate_limiter.acquire()
        
        return RequestPermit(self)
    
    def release(self):
        """释放请求许可"""
        self.global_semaphore.release()

class RequestPermit:
    """请求许可（上下文管理器）"""
    
    def __init__(self, limiter: GlobalRateLimiter):
        self.limiter = limiter
    
    async def __aenter__(self):
        # 已经在acquire()中获取了
        return self
    
    async def __aexit__(self, *args):
        self.limiter.release()


# 使用示例
rate_limiter = GlobalRateLimiter(config)

async def call_api():
    async with await rate_limiter.acquire():
        response = await http_client.post(...)
        return response
```

### 4. 令牌桶算法实现

```python
import time
import asyncio

class TokenBucket:
    """令牌桶限流器"""
    
    def __init__(self, rate: float, capacity: int):
        """
        Args:
            rate: 每秒生成的令牌数
            capacity: 桶容量（突发大小）
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.monotonic()
        self.lock = asyncio.Lock()
    
    async def acquire(self, tokens: int = 1):
        """获取令牌（阻塞直到有足够令牌）"""
        
        async with self.lock:
            while True:
                # 补充令牌
                now = time.monotonic()
                elapsed = now - self.last_update
                self.tokens = min(
                    self.capacity,
                    self.tokens + elapsed * self.rate
                )
                self.last_update = now
                
                # 检查是否有足够令牌
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return
                
                # 计算需要等待的时间
                needed = tokens - self.tokens
                wait_time = needed / self.rate
                
                # 释放锁并等待
                await asyncio.sleep(wait_time)
```

---

## 📊 并发控制示例

### 示例1: 单篇论文处理

```python
# 配置
config = ConcurrencyConfig(
    batch_level=BatchLevelConfig(max_concurrent_batches=1),
    stage_level=StageLevelConfig(
        answering=StageConfig(concurrency=5),
        grading=StageConfig(concurrency=3)
    ),
    request_level=RequestLevelConfig(max_concurrent_requests=10)
)

# 执行流程
async def process_one_paper():
    paper = load_paper("paper_001.txt")
    
    # 生成阶段 (1个请求)
    questions = await generator.generate(paper)  # 20题
    
    # 解题阶段 (5并发)
    # 第1轮: Q1-Q5  (同时)
    # 第2轮: Q6-Q10 (同时)
    # 第3轮: Q11-Q15(同时)
    # 第4轮: Q16-Q20(同时)
    answered = await answerer.answer_batch(questions)
    
    # 判题阶段 (3并发)
    # 第1轮: Q1-Q3  (同时)
    # 第2轮: Q4-Q6  (同时)
    # ...
    # 第7轮: Q19-Q20(同时)
    results = await grader.grade_batch(answered)
```

### 示例2: 100篇论文批量处理

```python
# 配置
config = ConcurrencyConfig(
    batch_level=BatchLevelConfig(max_concurrent_batches=3),
    # stage_level 和 request_level 同上
)

# 执行流程
async def process_100_papers():
    papers = load_papers(100)
    
    processor = BatchProcessor(config)
    results = await processor.process_batches(papers)
    
    # 实际执行：
    # 时刻0: 启动 Paper1, Paper2, Paper3 (3并发)
    # 时刻T: Paper1完成，启动 Paper4
    # 时刻2T: Paper2完成，启动 Paper5
    # ...
    # 直到所有100篇处理完成
```

### 示例3: 请求级限流效果

```python
# 配置
request_level = RequestLevelConfig(
    max_concurrent_requests=10,
    rate_limit=RateLimitConfig(
        requests_per_second=5.0,
        burst_size=10
    )
)

# 场景：3篇论文并发，每篇20题解答
# Paper1: 解题阶段 5并发 → 5个请求
# Paper2: 解题阶段 5并发 → 5个请求
# Paper3: 解题阶段 5并发 → 5个请求
# 总共: 15个请求想要同时发出

# 实际执行：
# 1. max_concurrent_requests=10 限制：只有10个能同时执行
# 2. rate_limit=5/s 限制：每秒最多5个请求
#    - 第1秒: 发出5个请求 (令牌桶: 10 → 5)
#    - 第2秒: 发出5个请求 (令牌桶: 10 → 5)
#    - 第3秒: 发出5个请求 (令牌桶: 10 → 5)
```

---

## 📈 性能分析

### 时间计算

#### 场景：处理1篇论文（20题）

**旧架构（串行）**:
```
生成: 60s
解题: 20题 × 30s = 600s = 10分钟
判题: 20题 × 20s = 400s = 6.7分钟
总计: 17.7分钟
```

**新架构（并发）**:
```
生成: 60s                          (不变)
解题: 20题 / 5并发 × 30s = 120s = 2分钟
判题: 20题 / 3并发 × 20s = 134s = 2.2分钟
总计: 4.2分钟

加速比: 17.7 / 4.2 = 4.2x
```

#### 场景：处理100篇论文

**旧架构（串行）**:
```
总计: 17.7分钟 × 100 = 1770分钟 = 29.5小时
```

**新架构（3批次并发）**:
```
每批: 4.2分钟
批次数: 100 / 3 = 34批（向上取整）
总计: 4.2分钟 × 34 = 142.8分钟 = 2.4小时

加速比: 29.5 / 2.4 = 12.3x
```

### 资源利用率

| 资源 | 旧架构 | 新架构 | 说明 |
|------|--------|--------|------|
| **CPU** | 10% | 60% | 多线程解题/判题 |
| **网络** | 5% | 40% | 并发API调用 |
| **内存** | 200MB | 600MB | 缓存中间结果 |
| **磁盘IO** | 低 | 中 | 批量写入 |

---

## 🎯 配置推荐

### 开发环境

```yaml
concurrency:
  batch_level:
    max_concurrent_batches: 1    # 单篇测试
  stage_level:
    answering:
      concurrency: 2              # 低并发，方便调试
    grading:
      concurrency: 1              # 串行判题
  request_level:
    max_concurrent_requests: 5
    rate_limit:
      requests_per_second: 2.0
```

### 生产环境（Milestone 2）

```yaml
concurrency:
  batch_level:
    max_concurrent_batches: 3    # 3篇论文并发
  stage_level:
    answering:
      concurrency: 5              # 5题并发解答
    grading:
      concurrency: 3              # 3题并发判题
  request_level:
    max_concurrent_requests: 10
    rate_limit:
      requests_per_second: 5.0
```

### 高负载环境

```yaml
concurrency:
  batch_level:
    max_concurrent_batches: 5    # 更多并发
  stage_level:
    answering:
      concurrency: 10             # 高并发
    grading:
      concurrency: 5
  request_level:
    max_concurrent_requests: 20
    rate_limit:
      requests_per_second: 10.0
```

---

## 🔍 监控与调优

### 关键指标

```python
class ConcurrencyMetrics:
    """并发监控指标"""
    
    # 批次级
    active_batches: int           # 当前活跃批次数
    queued_batches: int           # 等待中的批次数
    
    # 阶段级
    answering_active: int         # 当前解题并发数
    grading_active: int           # 当前判题并发数
    
    # 请求级
    active_requests: int          # 当前活跃请求数
    request_rate: float           # 实际请求速率 (req/s)
    token_bucket_level: float     # 令牌桶水位 (0-1)
    
    # 性能指标
    avg_batch_duration: float     # 平均批次处理时间
    avg_stage_duration: Dict      # 各阶段平均耗时
    throughput: float             # 吞吐量 (题/分钟)
```

### 调优建议

| 瓶颈现象 | 可能原因 | 调优方案 |
|----------|----------|----------|
| **CPU空闲，吞吐量低** | 并发度不足 | ↑ `max_concurrent_batches`<br>↑ `answering.concurrency` |
| **内存占用高** | 批次过多 | ↓ `max_concurrent_batches` |
| **API限流错误** | 请求过快 | ↓ `requests_per_second`<br>↑ `burst_size` |
| **解题耗时长** | 模型慢 | ↑ `answering.timeout`<br>换更快模型 |

---

## 🚀 总结

### 清晰的层次

```
批次级 (Batch)    → 控制多少篇论文并发
  ↓
阶段级 (Stage)    → 控制每个阶段的并发度
  ↓
请求级 (Request)  → 全局限流保护
```

### 独立的控制

- **生成**: 不并发（1次调用→多题）
- **解题**: 可调并发（推荐5）
- **判题**: 可调并发（推荐3）
- **批次**: 可调并发（推荐3-5）

### 全局的保护

- Semaphore: 限制总并发数
- RateLimiter: 控制请求速率
- Timeout: 防止请求卡死

---

**设计者**: AI架构师  
**状态**: 设计完成  
**下一步**: 实现ConcurrencyManager
