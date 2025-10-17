# 03 第三次尝试：保留原文引用

## 📋 概述

在02对比生成的基础上，进一步探索如何提高题目的可追溯性和学术严谨性。

**核心策略**：在生成题目时包含原文引用，确保每道题都有明确的文献依据。

---

## 🎯 目标

1. **提高可验证性**：题目答案能追溯到原文
2. **增强学术严谨性**：保留文献来源，符合学术规范
3. **便于质量检查**：可以对照原文验证答案准确性

---

## 🔧 实现方案

### 使用脚本
- `milestone1_withtext_generator.py`
- `scripts/milestone1_withtext_generator.py`（副本）

### 模型配置（从脚本确认）
- **生成模型**: `openai/deepseek-ai/DeepSeek-V3` (via SiliconFlow)
- **质检模型**: `openai/deepseek-ai/DeepSeek-V3`
- **参数**:
  - `citation_similarity_threshold=0.85` (原文引用相似度阈值)
  - `min_answer_length=100` (答案最少100字符)
  - `temperature=0.8`

### Prompt策略（从脚本提取的实际Prompt）

**核心要求**：
```
# ROLE
You are a senior expert in combustion science and engineering thermophysics

# TASK
Generate 20 high-quality questions WITH ORIGINAL TEXT CITATIONS

## ✅ REQUIREMENTS:

1. Based on Paper but Independent of Paper
   - Questions based on concepts/principles from paper
   - ❌ DO NOT ask about the paper itself
   - ✅ Test domain knowledge, not reading comprehension

2. **CRITICAL: Include Original Text Citations**
   - ✅ For EACH question, provide 1-3 EXACT QUOTES from the paper
   - ✅ Quotes must be VERBATIM (word-for-word), NOT paraphrased
   - ✅ Quotes should be substantial (at least 50 characters each)
   - ✅ Quotes must be directly relevant to question's scientific content

   Example:
   {
     "question_text": "Why does increasing pressure shorten ignition delay?",
     "standard_answer": "Increased pressure raises molecular number density...",
     "original_text": {
       "1": "The ignition delay time decreases with increasing pressure...",
       "2": "At elevated pressures, three-body reactions become more important..."
     },
     "type": "reasoning",
     "difficulty": 4
   }

3. Clear and Determinable Answers
4. Time-Independent (based on principles, not specific years)
5. Depth First (require understanding WHY, MECHANISM, HOW TO DERIVE)

📊 QUESTION TYPE DISTRIBUTION:
- reasoning (Reasoning Analysis) - 50%
- concept (Conceptual Understanding) - 25%
- calculation (Calculation) - 15%
- application (Application) - 10%

🎯 DIFFICULTY LEVELS:
- difficulty 3-4: 70% (main body)
- difficulty 5: 20% (challenging)
- difficulty 1-2: 10% (basic)
```

**对比01/02的关键改进**：
- **强制要求原文引用**：每题必须包含1-3条VERBATIM引用
- **引用验证机制**：citation_similarity_threshold=0.85自动验证引用真实性
- **引用格式规范**：original_text字段以字典形式存储多条引用

### 测试规模
- **1篇论文** → **20道题**
- 使用DeepSeek-V3模型

---

## 📊 产出数据

### 生成结果
- 包含原文引用的题目集
- 每道题带有 `original_text` 字段，记录引用的文献片段

### 日志文件
- `logs/milestone1_withtext.log`
- `logs/milestone1_withtext_run.log`

### 交付文档
- `MILESTONE1_WITHTEXT_DELIVERY.md` - 交付总结
- `WITHTEXT_STATUS.md` - 状态报告

---

## ✅ 关键发现

### 优点
1. **可追溯性大幅提升**：每道题都能找到原文依据
2. **质量检查更容易**：可以直接对照原文验证
3. **学术严谨性**：符合引用规范

### 问题发现 ⚠️

**重要Bug**：Prompt示例固定了2条原文引用

- **现象**：生成的题目总是包含**恰好2条**原文引用
- **原因**：Prompt中的示例固定展示2条，LLM学习了这个模式
- **影响**：限制了引用的灵活性，应该根据题目需要动态决定引用数量
- **启发**：**Prompt示例会强烈影响生成模式**，需要设计更灵活的示例

---

## 💡 经验教训

### 成功经验
1. **原文引用是质量保证的关键**
2. **可追溯性提升了用户信任度**
3. **便于后续的多模型验证**

### 需要改进
1. **Prompt示例设计**：避免固定数量，提供多样化示例
2. **引用长度控制**：需要平衡信息完整性和简洁性
3. **引用位置标注**：可以添加章节、页码等更精确的定位

### 未来方向
1. 开发更灵活的引用机制（允许0-N条引用）
2. 自动提取关键句子作为引用
3. 支持多级引用（主要论据 + 支持论据）

---

## 📁 文件结构

```
03_第三次尝试_保留原文/
├── README.md                           # 本文件
├── MILESTONE1_WITHTEXT_DELIVERY.md     # 交付总结
├── WITHTEXT_STATUS.md                  # 状态报告
├── milestone1_withtext_generator.py    # 主脚本
├── scripts/
│   └── milestone1_withtext_generator.py  # 脚本副本
├── logs/
│   ├── milestone1_withtext.log         # 运行日志
│   └── milestone1_withtext_run.log     # 详细日志
└── prompts/
    └── 生成题Prompt.md                 # 使用的prompt
```

---

## 🔗 相关尝试

- **上一步**: [02 对比生成](../02_第二次尝试_对比生成/)
- **下一步**: [04 详细问题生成](../04_第四次尝试_详细问题/)
- **改进版**: 07-08 DeepSeek批量生成（使用英文prompt解决了部分问题）
