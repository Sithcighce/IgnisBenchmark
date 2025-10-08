# API接口文档

## 🌐 外部API集成

### Gemini API (主要生成模型)

#### 配置参数
```yaml
generation_model: "gemini/gemini-2.5-flash"
grading_model: "gemini/gemini-2.5-flash"
```

#### 环境变量
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```

#### 调用示例 (题目生成)
```python
response = litellm.completion(
    model="gemini/gemini-2.5-flash",
    messages=[
        {"role": "user", "content": generation_prompt}
    ]
)
```

#### Token计费
- **输入**: $0.075 / 1M tokens
- **输出**: $0.30 / 1M tokens  
- **监控**: 实时统计在 `TokenTracker`

#### 错误处理
- **503 Service Unavailable** → 自动切换到DeepSeek
- **429 Rate Limit** → 指数退避重试
- **网络超时** → 3次重试机制

---

### DeepSeek API (备用生成模型)

#### 配置参数  
```yaml
siliconflow_base_url: "https://api.siliconflow.cn/v1"
siliconflow_model: "deepseek-ai/DeepSeek-V3"
```

#### 环境变量
```bash
SILICONFLOW_API_KEY=your_siliconflow_key_here
```

#### 调用示例
```python
response = litellm.completion(
    model='openai/deepseek-ai/DeepSeek-V3',
    messages=[{'role': 'user', 'content': prompt}],
    api_key=api_key,
    api_base='https://api.siliconflow.cn/v1'
)
```

#### 触发条件
- Gemini API返回503错误
- 自动无缝切换
- 保持相同的输入输出格式

---

### LM Studio API (本地解题模型)

#### 服务配置
```yaml
lm_studio_endpoint: "http://localhost:1234/v1/chat/completions"  
lm_studio_model_name: "qwen/qwen3-8b"
lm_studio_concurrency: 1
```

#### 服务要求
- **运行状态**: LM Studio必须启动并加载模型
- **端口**: 默认1234端口
- **模型**: 推荐qwen3-8b或同等性能模型

#### 调用示例
```python
response = requests.post(
    "http://localhost:1234/v1/chat/completions",
    json={
        "model": "qwen/qwen3-8b", 
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 2000
    },
    timeout=timeout
)
```

#### 重试机制
- **最大重试**: 3次
- **超时设置**: 60s → 120s → 180s (渐进)
- **退避策略**: 1s → 2s → 4s (指数)

---

## 🔄 内部API接口

### QuestionGenerator API

#### generate_questions()
```python
def generate_questions(
    self, 
    few_shot_examples: Optional[List[QuestionUnit]] = None
) -> List[QuestionUnit]:
    """
    生成一批题目
    
    Args:
        few_shot_examples: Few-shot示例列表
        
    Returns:
        生成的题目列表
    """
```

**输入格式**:
```python
few_shot_examples = [
    QuestionUnit(
        topic="数学", 
        difficulty=3,
        type="计算题",
        question_text="...",
        standard_answer="...",
        generation_model="manual_seed"
    )
]
```

**输出格式**:
```python
[
    QuestionUnit(
        question_id="uuid",
        topic="物理",
        difficulty=4, 
        type="概念题",
        question_text="...",
        standard_answer="...",
        generation_model="gemini/gemini-2.5-flash",
        creation_timestamp="2025-10-07T15:30:00"
    )
]
```

---

### AnsweringModule API  

#### answer_questions()
```python
def answer_questions(self, questions: List[QuestionUnit]) -> List[Tuple[QuestionUnit, str]]:
    """
    批量解答题目
    
    Args:
        questions: 待解答的题目列表
        
    Returns:  
        (题目, 答案) 元组列表
    """
```

**输入**: QuestionUnit列表  
**输出**: [(QuestionUnit, answer_text), ...] 

**并发控制**:
```python
with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
    results = list(executor.map(self._answer_single_question, questions))
```

---

### GradingModule API

#### grade_answer()
```python  
def grade_answer(
    self, 
    question: QuestionUnit, 
    candidate_answer: str
) -> GradingResult:
    """
    对答案进行评分
    
    Args:
        question: 原始题目
        candidate_answer: 待评估答案
        
    Returns:
        判题结果
    """
```

**输出格式**:
```python
GradingResult(
    is_correct=True,
    score=85.5,
    reasoning="答案基本正确，但缺少部分细节说明..."
)
```

---

### DataPersistence API

#### save_to_benchmark()
```python
def save_to_benchmark(self, entry: BenchmarkEntry):
    """保存到错题库"""
```

#### save_to_validation()  
```python
def save_to_validation(self, question: QuestionUnit):
    """保存到验证集"""
```

#### get_random_samples()
```python
def get_random_samples(self, count: int) -> List[QuestionUnit]:
    """从错题库随机抽取Few-shot样本"""
```

---

### TokenTracker API

#### track_generation_usage()
```python
def track_generation_usage(self, response):
    """统计生成题目的token使用"""
```

#### track_grading_usage()
```python  
def track_grading_usage(self, response):
    """统计判题的token使用"""
```

#### get_summary()
```python
def get_summary(self) -> Dict:
    """获取统计摘要"""
    return {
        "generation": {"prompt_tokens": 1234, "completion_tokens": 5678},
        "grading": {"prompt_tokens": 890, "completion_tokens": 1234}, 
        "total": {"total_tokens": 9036, "estimated_cost_usd": 0.0271}
    }
```

---

## 📋 数据格式规范

### QuestionUnit (题目单元)
```python
{
    "question_id": "uuid-string",
    "topic": "学科主题", 
    "difficulty": 1-5,           # 1=容易, 5=困难
    "type": "题目类型",          # 如"计算题", "概念题"等
    "question_text": "题目内容",
    "standard_answer": "标准答案",
    "generation_model": "生成模型名称",
    "creation_timestamp": "ISO格式时间戳"
}
```

### GradingResult (判题结果)
```python
{
    "is_correct": true,          # 是否正确
    "score": 85.5,               # 0-100分数  
    "reasoning": "详细判题理由"
}
```

### BenchmarkEntry (错题库条目)
```python
{
    "question_data": QuestionUnit,
    "failed_attempt": {
        "model_name": "qwen/qwen3-8b",
        "candidate_answer": "模型的错误回答",
        "grading_result": GradingResult
    }
}
```

---

## 🚨 错误码说明

### HTTP状态码处理
- **200 OK** - 正常响应
- **429 Too Many Requests** - 触发重试机制
- **503 Service Unavailable** - 触发API切换 (Gemini→DeepSeek)
- **timeout** - 触发超时重试

### 自定义错误
- **ConnectionError** - 网络连接失败  
- **JSONDecodeError** - 响应解析失败
- **ValidationError** - 数据格式验证失败

---

**📋 API文档完成**: 完整的内外部API接口规范  
**🎯 集成指南**: 标准化的调用方式和错误处理  
**🔧 扩展支持**: 易于添加新的API提供商