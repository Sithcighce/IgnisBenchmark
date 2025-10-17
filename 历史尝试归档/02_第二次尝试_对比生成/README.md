# 02 第二次尝试：对比生成（迭代质检机制）

## 📋 基本信息

- **时间**: 2024年10月（在01之后）
- **目标**: 通过对比不同生成策略 + 迭代质检机制改进题目质量
- **方法**: 生成 → 质检 → 反馈 → 重生成，最多3次迭代
- **模型**: `gemini/gemini-2.0-flash-exp`（生成 + 质检双重使用）
- **数据规模**: 1篇论文 → 20道题目

---

## 🎯 尝试目标

在第一次尝试的基础上，尝试通过**迭代质检机制**提升题目质量：
1. 生成题目后，用另一个模型进行质量检查
2. 将质检反馈注入prompt，重新生成
3. 设定接受率阈值（90%），最多迭代3次
4. 对比不同prompt策略的效果

---

## 🔧 技术细节（从脚本确认）

### 模型配置
- **生成模型**: `gemini/gemini-2.0-flash-exp`
- **质检模型**: `gemini/gemini-2.0-flash-exp`（与生成模型相同）
- **备用模型**: `openai/deepseek-ai/DeepSeek-V3` (via SiliconFlow)
- **参数**:
  - `max_iterations=3`（最多迭代3次）
  - `acceptance_threshold=0.90`（90%接受率才停止）
  - `temperature=0.8`
  - `response_format="json_object"`

### Prompt设计（英文版，从脚本提取）

**核心要求**：
```
# ROLE
You are a senior expert in combustion science and engineering thermophysics

# TASK
Generate 20 high-quality questions

✅ REQUIREMENTS:
1. Based on Paper but Independent of Paper
   - Questions based on concepts/principles from paper
   - ❌ DO NOT ask about the paper itself ("What does this article discuss?")
   - ✅ Questions should test domain knowledge, not reading comprehension

2. Clear and Determinable Answers
   - Must have clear correct/incorrect standards
   - Priority: calculation, judgment, causal reasoning
   - ❌ Avoid: open-ended discussion, trend prediction

3. Time-Independent
   - Based on physical principles, chemical mechanisms
   - ❌ Avoid: specific year applications, latest developments

4. Depth First
   - Require understanding WHY, MECHANISM, HOW TO DERIVE
   - ❌ Avoid: pure memorization definitions

� QUESTION TYPE DISTRIBUTION:
- reasoning (Reasoning Analysis) - 50%
  - Causal reasoning: "Why does X lead to Y?"
  - Mechanism explanation
  - Parameter influence analysis

- concept (Conceptual Understanding) - 25%
  - Deep meaning of key concepts (not simple definitions)
  - Relationships and differences between concepts

- application (Application) - 15%
  - Apply theory to practical scenarios
  - Design/Optimization problems

- calculation (Calculation) - 10%
  - Requires quantitative analysis
  - Can involve formula derivation
```

**迭代反馈机制**：
- 第1次生成后，质检模型检查每道题的质量
- 将不合格题目的反馈注入prompt："🔄 FEEDBACK FROM PREVIOUS ITERATION"
- 重新生成，直到达到90%接受率或3次迭代

---

## 📂 文件结构

```
02_第二次尝试_对比生成/
├── data/
│   ├── milestone1_compare.jsonl          # 生成的20道题目（确认）
│   ├── milestone1_compare_raw_iter1.txt  # 第1次迭代原始响应
│   └── milestone1_compare_report.md      # 生成报告
├── scripts/
│   └── milestone1_compare_generator.py   # 生成脚本（含完整prompt）
├── prompts/                              # Prompt存档
├── MILESTONE1_COMPARE_SUMMARY.md         # 对比总结
└── README.md                             # 本文档
```

---

## 📊 生成结果

- **生成题目**: 20道（验证：data/milestone1_compare.jsonl 正好20行）
- **论文来源**: 1篇PECS综述
- **迭代次数**: 1次（存在milestone1_compare_raw_iter1.txt，说明至少1次迭代）
- **题目特点**: 强调因果推理（reasoning 50%）+ 概念理解（concept 25%）

---

## 💡 主要发现

### ✅ 改进点（相比01）
1. **引入质检机制** - 生成后自动检查质量，不合格则重生成
2. **英文prompt** - 更详细的类型分布要求（reasoning 50%, concept 25%等）
3. **明确禁止项** - 不许问"论文说了什么"，不许开放题，不许时间相关题
4. **深度优先** - 要求问"为什么"、"机理是什么"，避免纯定义题

### ❌ 仍存在的问题
1. **质检模型与生成模型相同** - Gemini检查Gemini生成的内容，可能存在盲区
2. **迭代效果未知** - 无法确认迭代是否真正提升质量（缺乏01/02对比数据）
3. **仍缺乏原文依据** - 虽然提升了题目深度，但还是无法追溯到论文具体段落

---

## 🔄 后续改进

基于这次尝试，催生了后续尝试：
- **03次**: 保留原文引用，要求题目附带原文段落（解决可追溯性）
- **04-06**: 继续探索不同prompt变体和生成策略
- **07-08**: 批量生成时采用了本次的英文prompt风格

---

## 📝 关键经验

1. **迭代质检有价值** - 虽然质检模型与生成模型相同，但引入了"生成-检查-改进"循环
2. **英文prompt更详细** - 相比01的中文prompt，02的英文版对类型分布和禁止项描述更精确
3. **需要独立质检模型** - 后续应尝试不同模型交叉验证（如Gemini生成，DeepSeek质检）
4. **类型分布设计重要** - reasoning 50%的比重设计合理，因果推理题最能测试理解深度

---

*这次尝试引入了质检机制，虽然题目未进入最终benchmark，但"生成-检查-改进"的思路为后续多模型验证奠定了基础。*
2. **依然缺乏验证** - 答案正确性未检查
3. **生成不稳定** - 有时模型理解不准

## 🔄 经验总结

- 对比策略适合**综述性论文**
- 需要更通用的生成方法
- 质量验证机制仍然缺失

---

*对比策略是一个好方向，但不能作为唯一方法，需要结合其他策略。*
