# 并发架构问题记录

## 当前架构问题

### 现状：分阶段批量并发
当前系统实现的是**分阶段批量并发**，流程如下：

```
阶段1：批量生成题目
├── 并发生成题目1
├── 并发生成题目2  
└── 并发生成题目N
         ↓ (等待全部完成)
阶段2：批量解答题目
├── 并发解答题目1
├── 并发解答题目2
└── 并发解答题目N
         ↓ (等待全部完成)
阶段3：批量判题
├── 并发判题1
├── 并发判题2
└── 并发判题N
         ↓ (等待全部完成)  
阶段4：批量写入数据库
```

### 期望：流水线并发
理想的架构应该是**流水线式并发**：

```
流水线1: 生成题目1 → 解答题目1 → 判题1 → 写入1
流水线2: 生成题目2 → 解答题目2 → 判题2 → 写入2  
流水线3: 生成题目3 → 解答题目3 → 判题3 → 写入3
```

## 问题分析

### 1. 现有架构的缺陷
- **资源浪费**: 生成阶段结束后，生成资源闲置
- **延迟高**: 必须等待整个批次完成才能进入下一阶段
- **内存占用**: 需要在内存中存储整个批次的中间结果
- **用户体验**: 用户需要等待很长时间才能看到结果

### 2. 流水线架构的优势
- **资源充分利用**: 各阶段可以并行工作
- **低延迟**: 第一个结果可以很快产出
- **内存友好**: 不需要存储大批次数据
- **实时反馈**: 用户可以实时看到进度

## 技术实现方案

### 方案1：基于队列的流水线
```python
import queue
import threading

# 创建阶段间队列
generation_queue = queue.Queue()
answering_queue = queue.Queue() 
grading_queue = queue.Queue()
output_queue = queue.Queue()

# 各阶段工作线程
def generation_worker():
    while True:
        # 生成题目
        question = generate_question()
        generation_queue.put(question)

def answering_worker():
    while True:
        question = generation_queue.get()
        answered_question = answer_question(question)
        answering_queue.put(answered_question)

def grading_worker():
    while True:
        answered_question = answering_queue.get()
        graded_result = grade_question(answered_question)
        grading_queue.put(graded_result)

def output_worker():
    while True:
        result = grading_queue.get()
        save_result(result)
```

### 方案2：基于 AsyncIO 的异步流水线
```python
import asyncio

async def pipeline_processor():
    async for question in generate_questions_async():
        answer = await answer_question_async(question)
        result = await grade_answer_async(answer)
        await save_result_async(result)
```

### 方案3：基于 Producer-Consumer 模式
```python
from concurrent.futures import ThreadPoolExecutor
import threading

class PipelineProcessor:
    def __init__(self, concurrency=3):
        self.concurrency = concurrency
        
    def process_pipeline(self, num_questions):
        with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            futures = []
            for i in range(num_questions):
                future = executor.submit(self.single_pipeline, i)
                futures.append(future)
            
            # 等待所有流水线完成
            for future in futures:
                future.result()
    
    def single_pipeline(self, question_id):
        # 单条流水线：生成→解答→判题→保存
        question = self.generate_question()
        answer = self.answer_question(question)  
        result = self.grade_answer(answer)
        self.save_result(result)
```

## 配置参数建议

```yaml
# 流水线并发配置
pipeline_config:
  # 并行流水线数量
  parallel_pipelines: 3
  
  # 各阶段超时配置
  timeouts:
    generation: 60    # 生成超时(秒)
    answering: 120    # 解答超时(秒) 
    grading: 60       # 判题超时(秒)
    
  # 队列大小限制
  queue_sizes:
    generation: 10    # 生成队列大小
    answering: 10     # 解答队列大小
    grading: 10       # 判题队列大小
    
  # 重试策略
  retry:
    max_attempts: 3
    backoff_factor: 2
```

## 实现优先级

1. **高优先级**: 方案3 - Producer-Consumer模式
   - 实现简单，改动较小
   - 可以快速验证效果
   
2. **中优先级**: 方案1 - 队列流水线  
   - 更灵活的控制
   - 更好的资源利用
   
3. **低优先级**: 方案2 - AsyncIO异步
   - 需要大量重构
   - 学习成本较高

## 后续工作

- [ ] 选择实现方案
- [ ] 设计详细接口
- [ ] 实现原型验证
- [ ] 性能对比测试
- [ ] 生产环境部署

---

**状态**: 📋 已记录，待实现  
**影响**: 🔄 显著提升并发性能和用户体验  
**复杂度**: ⭐⭐⭐ 中等（需要重构核心流程）