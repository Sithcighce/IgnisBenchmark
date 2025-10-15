# 新架构设计方案

**设计日期**: 2025-10-14  
**架构版本**: v2.0  
**目标**: 可插拔、鲁棒、高并发

---

## 🎯 设计原则

### 1. SOLID原则
- **S**ingle Responsibility: 每个类只做一件事
- **O**pen/Closed: 对扩展开放，对修改关闭
- **L**iskov Substitution: 子类可替换父类
- **I**nterface Segregation: 接口细分
- **D**ependency Inversion: 依赖抽象而非具体

### 2. 可插拔设计
- 使用**Protocol**定义接口
- 使用**依赖注入**解耦
- 使用**策略模式**支持多种实现

### 3. 并发分层
- **论文级并发**: 批处理层
- **题目级并发**: 流水线层
- **请求级并发**: API调用层

---

## 🏗️ 核心架构

### 整体分层

```
┌─────────────────────────────────────────────────────┐
│                  Application Layer                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐    │
│  │ Milestone1 │  │ Milestone2 │  │ Milestone3 │    │
│  │  Script    │  │  Script    │  │  Script    │    │
│  └────────────┘  └────────────┘  └────────────┘    │
└───────────────────────┬─────────────────────────────┘
                        │
┌───────────────────────┴─────────────────────────────┐
│                  Pipeline Layer                      │
│  ┌───────────────────────────────────────────────┐  │
│  │            QuestionPipeline                   │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  │  │
│  │  │Generator │→ │Answerer  │→ │Grader    │  │  │
│  │  └──────────┘  └──────────┘  └──────────┘  │  │
│  └───────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────┘
                        │
┌───────────────────────┴─────────────────────────────┐
│                  Service Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │ ModelClient  │  │ConcurrencyMgr│  │DataRepo  │  │
│  │  (统一API)   │  │  (并发控制)  │  │ (存储)   │  │
│  └──────────────┘  └──────────────┘  └──────────┘  │
└───────────────────────┬─────────────────────────────┘
                        │
┌───────────────────────┴─────────────────────────────┐
│                 Infrastructure Layer                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │  LiteLLM     │  │  Asyncio     │  │  JSONL   │  │
│  │  (LLM SDK)   │  │  (异步IO)    │  │  (文件)  │  │
│  └──────────────┘  └──────────────┘  └──────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## 📦 核心组件设计

### 1. ModelClient - 统一模型调用

```python
from typing import Protocol, List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ModelProvider(Enum):
    GEMINI = "gemini"
    SILICONFLOW = "siliconflow"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

@dataclass
class ModelConfig:
    """模型配置"""
    name: str                    # 模型名称
    provider: ModelProvider      # 提供商
    priority: int                # 优先级 (越小越优先)
    max_retries: int = 2         # 最大重试次数
    timeout: int = 120           # 超时时间（秒）
    temperature: float = 0.8     # 温度参数
    max_tokens: int = 8000       # 最大token数

@dataclass
class ModelResponse:
    """统一响应格式"""
    content: str                 # 响应内容
    model: str                   # 实际使用的模型
    usage: Dict[str, int]        # Token使用统计
    metadata: Dict[str, Any]     # 其他元数据

class IModelClient(Protocol):
    """模型客户端接口"""
    
    def call(
        self, 
        messages: List[Dict[str, str]], 
        config: ModelConfig
    ) -> ModelResponse:
        """同步调用"""
        ...
    
    async def call_async(
        self, 
        messages: List[Dict[str, str]], 
        config: ModelConfig
    ) -> ModelResponse:
        """异步调用"""
        ...

class ModelClient:
    """统一模型客户端实现"""
    
    def __init__(self, configs: List[ModelConfig]):
        """
        初始化客户端
        
        Args:
            configs: 模型配置列表（按优先级排序）
        """
        self.configs = sorted(configs, key=lambda x: x.priority)
        self.retry_manager = RetryManager()
        self.metrics = MetricsCollector()
    
    async def call_with_fallback(
        self, 
        messages: List[Dict[str, str]],
        response_format: Optional[Dict] = None
    ) -> ModelResponse:
        """
        使用回退策略调用模型
        
        Args:
            messages: 消息列表
            response_format: 响应格式要求（如{"type": "json_object"}）
        
        Returns:
            ModelResponse
        
        Raises:
            ModelCallError: 所有模型都失败时抛出
        """
        last_error = None
        
        for config in self.configs:
            try:
                response = await self.retry_manager.with_retry(
                    func=self._call_single_model,
                    config=config,
                    messages=messages,
                    response_format=response_format
                )
                
                # 记录成功
                self.metrics.record_success(config.name)
                return response
                
            except Exception as e:
                last_error = e
                self.metrics.record_failure(config.name, str(e))
                logger.warning(f"模型 {config.name} 失败: {e}")
                continue
        
        # 所有模型都失败
        raise ModelCallError(f"所有模型都失败了，最后错误: {last_error}")
    
    async def _call_single_model(
        self,
        config: ModelConfig,
        messages: List[Dict[str, str]],
        response_format: Optional[Dict] = None
    ) -> ModelResponse:
        """调用单个模型"""
        
        import litellm
        
        # 构建调用参数
        kwargs = {
            "model": self._format_model_name(config),
            "messages": messages,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "timeout": config.timeout
        }
        
        if response_format:
            kwargs["response_format"] = response_format
        
        # 添加provider特定参数
        if config.provider == ModelProvider.SILICONFLOW:
            kwargs["api_base"] = os.getenv("SILICONFLOW_BASE_URL")
            kwargs["api_key"] = os.getenv("SILICONFLOW_API_KEY")
        
        # 调用LiteLLM
        response = await litellm.acompletion(**kwargs)
        
        # 解析响应
        return ModelResponse(
            content=response.choices[0].message.content,
            model=config.name,
            usage=response.usage.__dict__ if hasattr(response, 'usage') else {},
            metadata={"provider": config.provider.value}
        )
    
    def _format_model_name(self, config: ModelConfig) -> str:
        """格式化模型名称以适配LiteLLM"""
        if config.provider == ModelProvider.SILICONFLOW:
            return f"openai/{config.name}"
        return config.name
```

### 2. RetryManager - 重试管理

```python
import asyncio
from typing import TypeVar, Callable, Optional
from dataclasses import dataclass

T = TypeVar('T')

@dataclass
class RetryConfig:
    """重试配置"""
    max_attempts: int = 3          # 最大尝试次数
    base_delay: float = 1.0        # 基础延迟（秒）
    max_delay: float = 60.0        # 最大延迟（秒）
    exponential_base: float = 2.0  # 指数退避基数
    jitter: bool = True            # 是否添加随机抖动

class RetryManager:
    """统一重试管理器"""
    
    def __init__(self, config: RetryConfig = RetryConfig()):
        self.config = config
    
    async def with_retry(
        self,
        func: Callable[..., T],
        *args,
        **kwargs
    ) -> T:
        """
        使用重试策略执行函数
        
        Args:
            func: 要执行的异步函数
            *args, **kwargs: 函数参数
        
        Returns:
            函数返回值
        
        Raises:
            最后一次尝试的异常
        """
        last_exception = None
        
        for attempt in range(self.config.max_attempts):
            try:
                return await func(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                
                # 判断是否应该重试
                if not self._should_retry(e, attempt):
                    raise
                
                # 计算延迟时间
                delay = self._calculate_delay(attempt)
                
                logger.info(
                    f"尝试 {attempt + 1}/{self.config.max_attempts} 失败: {e}. "
                    f"等待 {delay:.2f}秒后重试..."
                )
                
                await asyncio.sleep(delay)
        
        # 所有尝试都失败
        raise last_exception
    
    def _should_retry(self, exception: Exception, attempt: int) -> bool:
        """判断是否应该重试"""
        
        # 最后一次尝试不重试
        if attempt >= self.config.max_attempts - 1:
            return False
        
        # 某些错误类型不重试
        no_retry_errors = [
            "invalid_api_key",
            "invalid_request",
            "authentication_error"
        ]
        
        error_msg = str(exception).lower()
        if any(err in error_msg for err in no_retry_errors):
            return False
        
        return True
    
    def _calculate_delay(self, attempt: int) -> float:
        """计算延迟时间（指数退避 + 抖动）"""
        
        # 指数退避
        delay = min(
            self.config.base_delay * (self.config.exponential_base ** attempt),
            self.config.max_delay
        )
        
        # 添加随机抖动
        if self.config.jitter:
            import random
            delay = delay * (0.5 + random.random())
        
        return delay
```

### 3. ConcurrencyManager - 并发控制

```python
import asyncio
from typing import List, TypeVar, Callable, Awaitable
from dataclasses import dataclass

T = TypeVar('T')

@dataclass
class ConcurrencyConfig:
    """并发配置"""
    max_concurrent: int = 10       # 最大并发数
    rate_limit_per_second: float = 5.0  # 每秒请求数限制
    burst_size: int = 10           # 突发大小

class ConcurrencyManager:
    """并发控制器"""
    
    def __init__(self, config: ConcurrencyConfig):
        self.config = config
        self.semaphore = asyncio.Semaphore(config.max_concurrent)
        self.rate_limiter = RateLimiter(
            rate=config.rate_limit_per_second,
            burst=config.burst_size
        )
    
    async def run_batch(
        self,
        tasks: List[Callable[[], Awaitable[T]]],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[T]:
        """
        并发执行任务批次
        
        Args:
            tasks: 任务列表（无参数的异步函数）
            progress_callback: 进度回调 (completed, total)
        
        Returns:
            结果列表
        """
        
        async def run_single(index: int, task: Callable) -> tuple[int, T]:
            """执行单个任务"""
            async with self.semaphore:
                await self.rate_limiter.acquire()
                result = await task()
                
                if progress_callback:
                    progress_callback(index + 1, len(tasks))
                
                return index, result
        
        # 创建所有任务
        coroutines = [
            run_single(i, task) 
            for i, task in enumerate(tasks)
        ]
        
        # 并发执行
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        # 按原始顺序排序
        sorted_results = sorted(
            [(i, r) for i, r in results if not isinstance(r, Exception)],
            key=lambda x: x[0]
        )
        
        return [r for _, r in sorted_results]

class RateLimiter:
    """令牌桶限流器"""
    
    def __init__(self, rate: float, burst: int):
        self.rate = rate
        self.burst = burst
        self.tokens = burst
        self.last_update = time.time()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """获取令牌（阻塞直到有令牌可用）"""
        async with self.lock:
            while self.tokens < 1:
                # 计算需要等待的时间
                wait_time = (1 - self.tokens) / self.rate
                await asyncio.sleep(wait_time)
                self._refill_tokens()
            
            self.tokens -= 1
    
    def _refill_tokens(self):
        """补充令牌"""
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(
            self.burst,
            self.tokens + elapsed * self.rate
        )
        self.last_update = now
```

### 4. QuestionPipeline - 流水线编排

```python
from typing import List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

class PipelineStage(Enum):
    GENERATION = "generation"
    ANSWERING = "answering"
    GRADING = "grading"

@dataclass
class PipelineConfig:
    """流水线配置"""
    generation_concurrency: int = 3
    answering_concurrency: int = 5
    grading_concurrency: int = 3
    enable_cache: bool = True
    save_intermediate: bool = True

class QuestionPipeline:
    """题目生成-解题-判题流水线"""
    
    def __init__(
        self,
        generator: IQuestionGenerator,
        answerer: IAnsweringModule,
        grader: IGradingModule,
        storage: IDataRepository,
        config: PipelineConfig
    ):
        """
        初始化流水线
        
        Args:
            generator: 题目生成器
            answerer: 解题模块
            grader: 判题模块
            storage: 数据仓库
            config: 配置
        """
        self.generator = generator
        self.answerer = answerer
        self.grader = grader
        self.storage = storage
        self.config = config
        
        # 并发控制器（每个阶段独立）
        self.gen_concurrency = ConcurrencyManager(
            ConcurrencyConfig(max_concurrent=config.generation_concurrency)
        )
        self.ans_concurrency = ConcurrencyManager(
            ConcurrencyConfig(max_concurrent=config.answering_concurrency)
        )
        self.grade_concurrency = ConcurrencyManager(
            ConcurrencyConfig(max_concurrent=config.grading_concurrency)
        )
    
    async def process_paper(
        self,
        paper: Paper,
        progress_callback: Optional[Callable] = None
    ) -> PipelineResult:
        """
        处理单篇论文的完整流程
        
        Args:
            paper: 论文对象
            progress_callback: 进度回调
        
        Returns:
            PipelineResult 包含成功/失败的题目
        """
        
        # 阶段1: 生成题目
        questions = await self._run_generation(paper, progress_callback)
        
        # 阶段2: 解题
        questions_with_answers = await self._run_answering(
            questions, progress_callback
        )
        
        # 阶段3: 判题
        graded_results = await self._run_grading(
            questions_with_answers, progress_callback
        )
        
        # 阶段4: 保存结果
        await self._save_results(graded_results)
        
        return graded_results
    
    async def _run_generation(
        self, 
        paper: Paper, 
        callback: Optional[Callable]
    ) -> List[Question]:
        """运行生成阶段"""
        
        logger.info(f"[生成] 处理论文: {paper.id}")
        
        if callback:
            callback(PipelineStage.GENERATION, 0, 1)
        
        # 调用生成器（单次调用生成多题）
        questions = await self.generator.generate(paper)
        
        # 保存中间结果
        if self.config.save_intermediate:
            await self.storage.save_intermediate(
                "generated_questions", questions
            )
        
        if callback:
            callback(PipelineStage.GENERATION, 1, 1)
        
        logger.info(f"[生成] 完成，生成 {len(questions)} 道题")
        return questions
    
    async def _run_answering(
        self, 
        questions: List[Question],
        callback: Optional[Callable]
    ) -> List[Question]:
        """运行解题阶段（并发）"""
        
        logger.info(f"[解题] 开始处理 {len(questions)} 道题")
        
        # 创建任务列表
        tasks = [
            lambda q=q: self.answerer.answer(q) 
            for q in questions
        ]
        
        # 并发执行
        def progress_wrapper(done, total):
            if callback:
                callback(PipelineStage.ANSWERING, done, total)
        
        results = await self.ans_concurrency.run_batch(
            tasks, progress_callback=progress_wrapper
        )
        
        logger.info(f"[解题] 完成")
        return results
    
    async def _run_grading(
        self,
        questions: List[Question],
        callback: Optional[Callable]
    ) -> PipelineResult:
        """运行判题阶段（并发）"""
        
        logger.info(f"[判题] 开始处理 {len(questions)} 道题")
        
        # 创建任务列表
        tasks = [
            lambda q=q: self.grader.grade(q)
            for q in questions
        ]
        
        # 并发执行
        def progress_wrapper(done, total):
            if callback:
                callback(PipelineStage.GRADING, done, total)
        
        grading_results = await self.grade_concurrency.run_batch(
            tasks, progress_callback=progress_wrapper
        )
        
        # 分类结果
        correct_questions = []
        wrong_questions = []
        error_questions = []
        
        for question, result in zip(questions, grading_results):
            if isinstance(result, Exception):
                error_questions.append((question, str(result)))
            elif result.is_correct:
                correct_questions.append(question)
            else:
                wrong_questions.append((question, result))
        
        logger.info(
            f"[判题] 完成 - "
            f"正确: {len(correct_questions)}, "
            f"错误: {len(wrong_questions)}, "
            f"异常: {len(error_questions)}"
        )
        
        return PipelineResult(
            correct=correct_questions,
            wrong=wrong_questions,
            errors=error_questions
        )
    
    async def _save_results(self, results: PipelineResult):
        """保存结果到仓库"""
        
        # 正确题目 → Validation集
        for q in results.correct:
            await self.storage.save_to_validation(q)
        
        # 错误题目 → Benchmark集
        for q, grading_result in results.wrong:
            await self.storage.save_to_benchmark(q, grading_result)
        
        # 错误记录 → 错误日志
        for q, error in results.errors:
            await self.storage.save_error(q, error)
```

---

## 🔌 接口定义

### Generator接口

```python
class IQuestionGenerator(Protocol):
    """题目生成器接口"""
    
    async def generate(
        self, 
        paper: Paper,
        few_shot_examples: Optional[List[Question]] = None
    ) -> List[Question]:
        """
        生成题目
        
        Args:
            paper: 论文对象
            few_shot_examples: Few-shot示例
        
        Returns:
            题目列表
        """
        ...
```

### Answerer接口

```python
class IAnsweringModule(Protocol):
    """解题模块接口"""
    
    async def answer(self, question: Question) -> Question:
        """
        解答问题
        
        Args:
            question: 问题对象
        
        Returns:
            包含答案的问题对象
        """
        ...
```

### Grader接口

```python
class IGradingModule(Protocol):
    """判题模块接口"""
    
    async def grade(
        self, 
        question: Question
    ) -> GradingResult:
        """
        判题
        
        Args:
            question: 包含候选答案的问题
        
        Returns:
            判题结果
        """
        ...
```

### Repository接口

```python
class IDataRepository(Protocol):
    """数据仓库接口"""
    
    async def save_to_validation(self, question: Question):
        """保存到验证集"""
        ...
    
    async def save_to_benchmark(
        self, 
        question: Question, 
        grading_result: GradingResult
    ):
        """保存到基准集"""
        ...
    
    async def get_few_shot_samples(self, count: int) -> List[Question]:
        """获取Few-shot样本"""
        ...
```

---

## 📊 配置文件结构

### 新config.yaml

```yaml
# 全局配置
project:
  name: "IgnisBenchmark"
  version: "2.0"

# 模型配置（分组清晰）
models:
  generation:
    configs:
      - name: "gemini/gemini-2.5-flash"
        provider: "gemini"
        priority: 1
        max_retries: 2
        timeout: 120
        temperature: 0.8
        max_tokens: 8000
      
      - name: "deepseek-ai/DeepSeek-V3"
        provider: "siliconflow"
        priority: 2
        max_retries: 2
        timeout: 180
  
  answering:
    configs:
      - name: "Qwen/Qwen2.5-7B-Instruct"
        provider: "siliconflow"
        priority: 1
        max_retries: 3
        timeout: 120
  
  grading:
    configs:
      - name: "gemini/gemini-2.5-flash"
        provider: "gemini"
        priority: 1
        max_retries: 2
        timeout: 120

# 并发配置（分层清晰）
concurrency:
  paper_level:          # 论文级（批处理）
    max_concurrent: 3
  
  question_level:       # 题目级（流水线内）
    generation: 1       # 生成不并发（1个API调用 → N题）
    answering: 5        # 解题并发
    grading: 3          # 判题并发
  
  request_level:        # 请求级（底层API）
    max_concurrent_requests: 10
    rate_limit_per_second: 5.0

# 重试配置
retry:
  max_attempts: 3
  base_delay: 1.0
  max_delay: 60.0
  exponential_base: 2.0
  jitter: true

# 数据配置
data:
  benchmark_path: "./data/benchmark_bank.jsonl"
  validation_path: "./data/validation_set.jsonl"
  error_log_path: "./data/errors.jsonl"
  cache_dir: "./cache"

# 流水线配置
pipeline:
  enable_cache: true
  save_intermediate: true
  questions_per_batch: 20

# 日志配置
logging:
  level: "INFO"
  file: "./logs/system.log"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

---

## 🎯 使用示例

### Milestone 1 (重构后)

```python
# milestone1_generator_v2.py
import asyncio
from core.pipeline import QuestionPipeline
from core.models import Paper
from adapters.legacy import LegacyGeneratorAdapter

async def main():
    # 加载配置
    config = load_config("config.yaml")
    
    # 初始化组件
    pipeline = build_pipeline(config)
    
    # 加载论文
    paper = Paper.from_file("main.txt", id="PECS_001")
    
    # 运行流水线
    def progress_callback(stage, done, total):
        print(f"[{stage.value}] {done}/{total}")
    
    result = await pipeline.process_paper(paper, progress_callback)
    
    # 生成报告
    report = generate_report(result)
    save_report(report, "data/milestone1_report.md")

if __name__ == "__main__":
    asyncio.run(main())
```

### Milestone 2 (批量处理)

```python
# milestone2_generator.py
import asyncio
from core.batch_processor import BatchPaperProcessor

async def main():
    config = load_config("config.yaml")
    
    # 批处理器
    processor = BatchPaperProcessor(
        pipeline=build_pipeline(config),
        concurrency=config.concurrency.paper_level.max_concurrent
    )
    
    # 加载100篇论文
    papers = load_papers_from_directory("papers/")
    
    # 批量处理（带进度条）
    results = await processor.process_batch(
        papers,
        progress_callback=print_progress
    )
    
    # 汇总报告
    summary = generate_summary(results)
    save_summary(summary, "data/milestone2_summary.md")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🔄 与现有代码的兼容

### 适配器模式

```python
# adapters/legacy.py
from src.question_generator import QuestionGenerator as OldGenerator
from core.interfaces import IQuestionGenerator

class LegacyGeneratorAdapter(IQuestionGenerator):
    """适配旧版生成器"""
    
    def __init__(self, old_generator: OldGenerator):
        self.old_generator = old_generator
    
    async def generate(
        self, 
        paper: Paper,
        few_shot_examples=None
    ) -> List[Question]:
        """适配接口"""
        
        # 转换paper为旧格式
        # 同步调用转异步
        import asyncio
        questions = await asyncio.to_thread(
            self.old_generator.generate_questions,
            few_shot_examples
        )
        
        return questions
```

---

## 📈 性能对比预测

### Milestone 2 (100篇论文)

| 场景 | 旧架构 | 新架构 | 提升 |
|------|--------|--------|------|
| **生成题目** | 100min (串行) | 33min (3并发) | **3x** |
| **解题** | 400min (串行) | 80min (5并发) | **5x** |
| **判题** | 300min (串行) | 100min (3并发) | **3x** |
| **总计** | ~800min | ~150min | **5.3x** |

### 资源利用率

| 指标 | 旧架构 | 新架构 |
|------|--------|--------|
| CPU利用率 | ~20% | ~70% |
| 网络带宽 | ~10% | ~60% |
| 内存占用 | ~200MB | ~500MB |

---

## 🚦 下一步

- ✅ 完成架构设计
- 📝 制定[迁移路线图](./03_MIGRATION_ROADMAP.md)
- 📝 编写[API文档](./04_API_DESIGN.md)
- 🔧 实现核心组件

---

**设计者**: AI架构师  
**审阅**: 待审核  
**状态**: 设计完成 → 下一步: 迁移计划
