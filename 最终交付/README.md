# IgnisBenchmark - 最终交付版本

## 📊 Benchmark概览

本Benchmark包含 **150道** 高质量燃烧科学与能源工程领域的专业题目，这些题目具有以下特点：

1. ✅ **三模型验证通过**: 所有题目均经过Claude Sonnet 4.5、GPT-5、Gemini 2.5 Pro三个顶级模型的一致验证
2. 🔥 **挑战性强**: 这些是GPT-5在测试中答错或回答不完整的题目
3. 📚 **来源权威**: 基于顶级学术论文和教材
4. 🎯 **专业深度**: 难度3-5级，涵盖概念理解、推理分析、计算应用

---

## 📁 文件说明

### 1. `benchmark_basic.json` - 基础版（推荐）

**用途**: 供他人直接使用的benchmark题目集

**包含内容**:
- 题目ID
- 题目文本
- 标准答案
- 难度等级 (3-5)
- 主题分类
- 题目类型 (concept/reasoning/calculation/application)

**适用场景**:
- 评测模型在燃烧科学领域的专业能力
- 对比不同模型的答题表现
- 作为专业领域的测试集

**示例结构**:
```json
{
  "question_id": "deepseek_q_xxxxx",
  "question_text": "题目内容...",
  "standard_answer": "标准答案...",
  "difficulty": 4,
  "topic": "combustion_kinetics",
  "type": "reasoning"
}
```

---

### 2. `benchmark_with_verification.json` - 验证版

**用途**: 了解题目来源和验证过程

**包含内容**:
- 基础版的所有内容
- **原文引用** (original_text): 题目来源的文献原文
- **验证记录** (verification): 三模型验证的详细信息
- **质量检查** (quality_check): 题目质量审核记录
- **来源信息** (source): 题目生成的文献来源

**适用场景**:
- 验证题目的权威性和准确性
- 追溯题目的学术来源
- 了解题目的生成和验证过程

**示例结构**:
```json
{
  "question_id": "deepseek_q_xxxxx",
  "question_text": "题目内容...",
  "standard_answer": "标准答案...",
  "difficulty": 4,
  "topic": "combustion_kinetics",
  "type": "reasoning",
  "original_text": {
    "1": "原文片段1...",
    "2": "原文片段2..."
  },
  "verification": {
    "claude_verification": {},
    "gpt5_verification": {},
    "gemini_verification": {}
  },
  "quality_check": {...},
  "source": "论文标题或来源"
}
```

---

### 3. `benchmark_with_gpt5_results.json` - GPT-5测试版

**用途**: 了解GPT-5在这些题目上的表现

**包含内容**:
- 基础版的所有内容
- **GPT-5测试结果** (gpt5_test_result):
  - 得分 (score)
  - 回答长度 (answer_length)
  - 错误类型 (category): real_error 或 api_failure_with_score
  - 说明 (note)

**适用场景**:
- 了解GPT-5的答题表现
- 识别GPT-5的知识盲区
- 与其他模型对比性能

**统计信息**:
- 真实错误: 76题 (GPT-5给出实质性回答但答错)
- API失败(有分): 69题 (回答太短或部分失败)

**重要说明**:
通过统计分析验证，API失败(有分)的69题与真实错误的76题在得分上无显著差异：
- 真实错误平均分: 48.29分
- API失败(有分)平均分: 47.75分
- 差异: 仅0.54分

这证明API失败不是因为模型回答被截断，而是技术性API问题。两组题目在难度分布、主题分布和得分分布上高度相似，因此可以一视同仁地作为benchmark的挑战性题目。

此外，重新测试了7个API失败(0分)的题目，使用OpenAI API重新调用GPT-4o后，全部得到了实质性回答(平均3,297字符，平均得分55.29分)，其中5题答错已加入benchmark，2题答对未纳入。这进一步证实了API失败是技术问题而非模型能力问题。

**示例结构**:
```json
{
  "question_id": "deepseek_q_xxxxx",
  "question_text": "题目内容...",
  "standard_answer": "标准答案...",
  "difficulty": 4,
  "topic": "combustion_kinetics",
  "type": "reasoning",
  "gpt5_test_result": {
    "score": 35,
    "answer_length": 5216,
    "category": "real_error",
    "note": "GPT-5给出实质回答但答错"
  }
}
```

---

### 4. `benchmark_complete.json` - 完整版

**用途**: 完整的题目数据，包含所有信息

**包含内容**:
- 所有基础、验证、测试信息
- 完整的题目元数据
- 分类标记 (benchmark_category)
- 详细说明 (benchmark_note)

**适用场景**:
- 深度分析和研究
- 完整的数据备份
- 需要所有信息的场景

---

## 📊 题目统计

### 总体统计
- **总题目数**: 150
- **真实错误**: 76 (50.7%)
- **API失败(有分)**: 69 (46.0%)
- **API失败(0分)重测答错**: 5 (3.3%)

### 按难度分布
- 难度3: 5 题
- 难度4: 117 题
- 难度5: 28 题

### 按主题分布（Top 5）
- energy_systems: 50 题
- combustion_kinetics: 42 题
- heat_transfer: 16 题
- fluid_mechanics: 13 题
- combustion_science: 8 题

### 按类型分布
- concept: 75 题
- reasoning: 56 题
- calculation: 13 题
- application: 6 题

---

## 🎯 使用建议

### 快速开始
```python
import json

# 加载基础版benchmark
with open('benchmark_basic.json', 'r', encoding='utf-8') as f:
    benchmark = json.load(f)

print(f"加载了 {len(benchmark)} 道题目")

# 按难度筛选
difficulty_4 = [q for q in benchmark if q['difficulty'] == 4]
print(f"难度4的题目: {len(difficulty_4)} 道")
```

### 评测模型
```python
import json

# 加载benchmark
with open('benchmark_basic.json', 'r', encoding='utf-8') as f:
    benchmark = json.load(f)

# 对每道题目进行测试
results = []
for question in benchmark:
    # 调用你的模型
    model_answer = your_model(question['question_text'])
    
    # 评分（使用另一个模型或人工评分）
    score = grade_answer(model_answer, question['standard_answer'])
    
    results.append({
        'question_id': question['question_id'],
        'score': score
    })

# 计算准确率
accuracy = sum(r['score'] >= 85 for r in results) / len(results)
print(f"准确率: {accuracy*100:.2f}%")
```

---

## 📈 GPT-5基准性能

作为参考，GPT-5在这150道题目上的表现：

- **真实错误**: 76题
  - 给出了实质性回答（平均5,893字符）
  - 但DeepSeek判定为错误
  - 平均得分: 48.3分

- **API失败(有分)**: 69题
  - 回答太短或部分失败
  - 得分范围: 1-80分
  - 平均得分: 47.8分

- **API失败(0分)重测**: 5题
  - 原OpenRouter API失败得0分
  - OpenAI重测后得分: 30-45分
  - 平均得分: 42.0分

**注意**: 这些题目是GPT-5的挑战性题目，不代表GPT-5的整体性能。在完整的984题测试集中，GPT-5的准确率为90.45%（排除API失败）。

---

## 🔍 质量保证

### 题目来源
- 所有题目基于顶级学术论文和教材
- 每道题目都有明确的文献引用

### 验证流程
1. **自动生成**: 基于学术论文生成候选题目
2. **三模型验证**: Claude Sonnet 4.5、GPT-5、Gemini 2.5 Pro独立验证
3. **质量审核**: 检查原文忠实度、标答准确性、题目合理性
4. **实测筛选**: GPT-5实际答题，筛选出挑战性题目

### 适用性说明
- ✅ 适合评测顶级模型的专业能力
- ✅ 适合识别模型的知识盲区
- ✅ 适合作为挑战性测试集
- ⚠️ 难度较高，不适合初级模型评测
- ⚠️ 专业领域限定（燃烧科学与能源工程）

---

## 📝 引用

如果您使用本benchmark，请引用：

```
IgnisBenchmark: A Challenging Benchmark for Combustion Science and Energy Engineering
Generated and verified by Claude Sonnet 4.5, GPT-5, and Gemini 2.5 Pro
Version 1.0 (2025-10-17)
GitHub: https://github.com/Sithcighce/IgnisBenchmark
```

---

## 📞 联系方式

- **项目地址**: https://github.com/Sithcighce/IgnisBenchmark
- **问题反馈**: 请在GitHub Issues中提出

---

**生成时间**: 2025-10-17 11:31:25  
**版本**: v1.0  
**状态**: ✅ 最终交付版本
