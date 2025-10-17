# 11 第十一次尝试：三模型验证系统# 第九阶段：三模型验证系统



**批次编号**: 11  ## 时间

**原阶段名**: 第九阶段（已更新为第十一阶段）  批量生成完成后

**时间**: 2025-10-15 批量生成完成后  

**状态**: ✅ 完成  ## 目标

建立三模型（Claude/GPT-5/Gemini）验证机制

---

## 使用脚本

## 📋 批次概述- `src/question_generator.py` (包含验证逻辑)

- `scripts/run_100_questions_test.py`

### 目标- `testscript/test_single_generation.py`

建立三模型（Claude Sonnet 4.5 / GPT-5 / Gemini 2.5 Pro）验证机制，对批次10的1490道题目进行质量验证。

## 特点

### 关键特点- 三个顶级模型独立验证

- **三个顶级模型独立验证**: 每道题由三个模型分别判断- 检查原文忠实度、标答准确性、题目合理性

- **多维度检查**: 原文忠实度、标准答案准确性、题目合理性- all_correct标记表示三模型一致通过

- **all_correct标记**: 三模型一致通过才标记为最高质量

- **并发处理**: 50并发请求，处理1200+题目## 产出数据

- 通过验证的题目：`data/pass.json`

---- 未通过验证的题目：`data/notpass.json`



## 🎯 核心价值## 结果

- 大幅提高题目质量

### 验证维度- 建立了可信的质量保证体系

1. **事实准确性 (Factual Accuracy)**

   - 检查答案是否与原文矛盾## 经验教训

   - 物理/化学/热力学原理是否正确- 多模型验证是质量保证的关键

   - 一致性要求保证了题目的权威性

2. **逻辑一致性 (Logical Consistency)**
   - 推理过程是否合理
   - 因果关系是否正确
   
3. **完整性 (Completeness - 灵活)**
   - 是否回答了问题核心要点
   - 允许长短不一，核心机制覆盖即可

### 判断标准
- ✅ **correct = true**: 无事实错误、逻辑合理、核心要点完整
- ⚠️ **needs_review**: 边界情况，建议人工复审
- ❌ **correct = false**: 存在明显错误

---

## 📂 目录结构

```
11_第十一次尝试_三模型验证系统/
├── scripts/
│   └── batch_verification.py         # 批量验证脚本（50并发）
├── 验证数据/
│   ├── pass.json                     # 通过验证的题目
│   ├── notpass.json                  # 未通过验证的题目
│   ├── verification_results.json    # 完整验证结果
│   ├── verification_stats.json      # 统计信息
│   └── batch_verification.log       # 验证日志
└── README.md                         # 本文档
```

---

## 🔧 使用的模型

### 三大验证模型
```python
MODELS = [
    "anthropic/claude-sonnet-4.5",    # Claude - 逻辑推理强
    "openai/gpt-5",                    # GPT-5 - 综合能力强
    "google/gemini-2.5-pro"            # Gemini - 科学知识强
]
```

### 并发配置
- **MAX_CONCURRENT**: 50
- **REQUEST_TIMEOUT**: 180秒
- **API平台**: OpenRouter

---

## 📊 验证结果

### 统计数据
- **总题目数**: ~1490道（来自批次10）
- **通过验证**: 984道题目标记为 `all_correct = true`
- **需要复审**: 88道题目标记为 `needs_review` 或 `correct = false`

### 结果分布
```
验证数据/
├── pass.json          # 984题 - 三模型一致通过
└── notpass.json       # 88题 - 包含needs_review和错误题目
```

---

## 🎓 脚本说明

### batch_verification.py
**功能**: 并行批量验证题目

**核心特性**:
1. **三模型并行**: 对每道题，同时调用三个模型
2. **线程安全**: 使用Lock保护共享资源
3. **实时统计**: 记录每个模型的成功/失败率
4. **完整日志**: 所有验证过程记录到日志文件
5. **结果分流**: 自动将pass/notpass分别保存

**关键代码逻辑**:
```python
# 1. 加载判题prompt模板
prompt_template = load_prompt_template()

# 2. 格式化原文引用
formatted_text = format_original_text(original_text_dict)

# 3. 调用三个模型验证
results = []
for model in MODELS:
    result = call_openrouter_api(prompt, model)
    results.append(result)

# 4. 综合判断
all_correct = all(r.get('correct') == True for r in results)
```

---

## 📝 Prompt设计

### 判题Prompt结构
位置: `历史尝试归档/13_第十三次尝试_GPT5测试/判题prompt`

**输入信息**:
- Question: 题目文本
- Standard Answer: 待验证的标准答案
- Original Text: PECS综述原文（视为真理）

**验证任务**:
1. 检查事实准确性
2. 检查逻辑一致性
3. 检查完整性（灵活）

**输出格式**:
```json
{
  "correct": true/false,
  "explanation": "判断理由",
  "needs_review": false  // 边界情况标记
}
```

---

## 💡 关键发现

### 1. 多模型验证的必要性
- **单模型风险**: 可能有偏见或误判
- **三模型共识**: 大幅提高判断可信度
- **一致性价值**: all_correct = true 的题目质量极高

### 2. needs_review机制
- **边界情况**: 模型对某些复杂题目意见不一
- **人工介入**: 允许专家最终判断
- **质量保证**: 避免误杀好题或放过错题

### 3. 并发处理的效率
- **50并发**: 1490题 → 约30-40分钟完成
- **成本优化**: OpenRouter统一管理API调用
- **稳定性**: 重试机制应对偶发API失败

---

## 🔗 数据流向

```
输入: 批次10的1490道题目
  ↓
三模型并行验证（Claude/GPT-5/Gemini）
  ↓
综合判断 → all_correct标记
  ↓
分流输出:
  ├── pass.json (984题)
  └── notpass.json (88题)
  ↓
流向: 批次12（质量筛选）
```

---

## 📖 相关批次

- **上游**: 批次10（DeepSeek英文生成，1490道题）
- **下游**: 批次12（质量筛选，从984题中精选）
- **辅助**: 批次13（GPT-5测试，使用同一判题prompt）

---

## 🎯 经验教训

### ✅ 成功经验
1. **多模型验证**: 是质量保证的关键，单模型不足以保证可信度
2. **all_correct机制**: 三模型一致通过的题目，确实质量极高
3. **并发处理**: 大幅缩短验证时间，提高迭代速度
4. **详细日志**: 记录每个模型的判断，便于后续分析

### ⚠️ 注意事项
1. **成本控制**: 三模型验证成本是单模型的3倍
2. **prompt一致性**: 三个模型必须使用相同的验证标准
3. **API稳定性**: 需要处理偶发的API失败情况
4. **边界情况**: needs_review需要人工复审，不能完全自动化

### 🔄 后续改进
1. 考虑引入第四模型作为tie-breaker（当三模型意见不一致时）
2. 记录每个模型的判断理由，便于分析差异原因
3. 统计各模型的"严格度"（更倾向pass还是fail）

---

## 🔍 技术细节

### 线程安全设计
```python
stats_lock = Lock()
global_stats = {
    "total_questions": 0,
    "total_verifications": 0,
    "completed_verifications": 0,
    "failed_verifications": 0,
    "model_stats": {...}
}

def log_message(msg):
    with stats_lock:  # 确保多线程安全
        print(msg)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line)
```

### 重试机制
```python
def call_openrouter_api(prompt, model, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(...)
            return response.json()
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 指数退避
            else:
                raise
```

---

## 📌 总结

批次11建立了**三模型验证系统**，这是IgnisBenchmark质量保证的核心环节：

1. **输入**: 批次10的1490道英文题目
2. **过程**: Claude/GPT-5/Gemini三模型独立验证
3. **输出**: 984道all_correct题目
4. **价值**: 建立可信的质量保证体系

这一验证系统确保了benchmark的权威性和可信度，为后续的质量筛选（批次12）和GPT-5测试（批次13）奠定了基础。

---

**生成时间**: 2025-10-17  
**文档版本**: v1.0
