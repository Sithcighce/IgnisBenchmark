# 04 第四次尝试：详细问题生成

## 📋 基本信息

- **时间**: 2024年10月（在03之后）
- **目标**: 生成更详细、更深入的题目，答案要求300+字符
- **方法**: 牺牲题目数量换取单题质量
- **模型**: `openai/deepseek-ai/DeepSeek-V3` (via SiliconFlow)
- **数据规模**: 1篇论文 → 5道详细题（而非20道）

---

## 🎯 尝试目标

在01-03的基础上，尝试新策略：
1. **提升答案深度** - 要求生成300+字符的详细答案
2. **增加题目复杂度** - 覆盖更多知识点
3. **测试质量vs数量权衡** - 验证少而精的策略是否更有效
4. **继续保留原文引用** - 延续03的可追溯性思路

---

## 🔧 技术细节（从脚本确认）

### 模型配置
- **生成模型**: `openai/deepseek-ai/DeepSeek-V3` (via SiliconFlow)
- **质检模型**: `openai/deepseek-ai/DeepSeek-V3` (same as generation)
- **参数**:
  - `min_answer_length=300` (答案最少300字符)
  - `citation_similarity_threshold=0.85` (原文引用相似度阈值)
  - `temperature=0.8`

### Prompt核心要求
```
# GOAL
Generate 5 high-quality, domain-specific questions with detailed answers (300+ chars)

# FOCUS
Combustion, Heat Transfer, Fluid Mechanics, CFD, Energy and their applications

# REQUIREMENTS
1. Detailed Answers (300+ characters):
   - Must include principles, mechanisms, examples
   - Must explain WHY and HOW, not just WHAT
   
2. Citation Verification:
   - Each question should reference specific paper content
   - Citation similarity threshold: 0.85

3. Domain-Specific:
   - Focus on combustion science, heat transfer, fluid mechanics
   - Require deep domain knowledge
```

**对比01/02/03的变化**：
- **题目数量**：从20题减少到5题
- **答案长度**：明确要求300+字符（01/02/03只要求"详细"）
- **原文验证**：引入citation_similarity_threshold=0.85，自动验证引用真实性
- **模型切换**：从Gemini切换到DeepSeek-V3

---

## � 文件结构

```
04_第四次尝试_详细问题/
├── data/
│   ├── milestone1_detail_Q.jsonl        # 生成的5道详细题（确认）
│   ├── milestone1_detail_Q_raw.txt      # 原始响应
│   └── milestone1_detail_Q_report.md    # 生成报告
├── scripts/
│   └── milestone1_detail_Q_generator.py # 生成脚本（含完整prompt）
├── prompts/
│   └── 生成题Prompt_higherlever.md     # 高级prompt模板
├── 辅助脚本/                            # 批处理工具
│   ├── batch_auto_run.py
│   ├── run_full_batch.py
│   ├── monitor_batch.py
│   └── ...
├── 数据工具/                            # 数据处理工具
├── 题目数据_md格式/                     # Markdown格式题目
├── 题目数据_question_all/               # 所有题目汇总
├── BATCH_DETAIL_Q_README.md            # 批处理说明
└── README.md                           # 本文档
```

---

## 📊 生成结果

- **生成题目**: 5道详细题（验证：data/milestone1_detail_Q.jsonl 正好5行）
- **论文来源**: 1篇PECS综述
- **答案长度**: 显著增加（300+字符要求）
- **题目特点**: 深度优先，强调机理解释

---

## 💡 主要发现（与01/02/03对比）

### ✅ 改进点
1. **答案深度大幅提升** - 300+字符的强制要求确保了答案详细度
2. **原文验证机制** - citation_similarity_threshold=0.85自动验证引用真实性
3. **模型切换** - 从Gemini切换到DeepSeek-V3，测试不同模型效果
4. **质量vs数量策略** - 5题详细 vs 20题普通，验证"少而精"思路

### ❌ 仍存在的问题
1. **题目数量骤减** - 从20题减少到5题，不适合大规模benchmark建设
2. **批处理需求** - 单篇论文5题太少，需要批量处理多篇论文
3. **原文验证阈值** - 0.85可能过于严格或过于宽松，需要调优

### 🤔 实验结论
- **少而精 vs 多而快**：两种策略各有优劣，最终需要结合
- **催生批处理方案**：5题/篇太少 → 需要批量处理多篇论文 → 产生了`辅助脚本/`中的批处理工具
- **为09铺路**：04的批处理工具和"详细答案"思路直接影响了09_批量详细题目

---

## 🔄 后续影响

基于这次尝试：
- **批处理工具诞生** - `辅助脚本/`中的batch系统成为后续大规模生成的基础
- **05-06洞察生成** - 继续探索其他生成策略（洞察式生成）
- **09批量详细题目** - 将04的"详细答案"策略扩展到批量场景
- **质量标准明确** - 300+字符成为后续答案长度的参考标准

---

## 📝 关键经验

1. **质量vs数量权衡** - 5题详细质量高，但不适合大规模benchmark；20题覆盖面广，但单题深度有限
2. **原文验证重要** - citation_similarity_threshold机制有效防止"幻觉"
3. **批处理必要性** - 单篇论文生成太少，需要批处理多篇论文才能达到目标规模
4. **模型选择影响** - DeepSeek-V3在详细答案生成上的表现需要与Gemini对比评估

---

*这次尝试确立了"详细答案"标准（300+字符），虽然题目未进入最终benchmark，但批处理工具和质量标准为后续工作提供了重要支撑。*

- **数据处理工具**：
  - `analyze_questions.py` - 统计分析
  - `extract_questions_to_md.py` - 导出Markdown
  - `count_questions.py` - 题目计数

### 交付文档
- `BATCH_DETAIL_Q_README.md` - 详细使用说明

---

## ✅ 关键发现

### 优点
1. **答案质量显著提升**：详细答案更有价值
2. **深度增加**：覆盖更多机制和原理
3. **更具挑战性**：适合benchmark用途

### 权衡
1. **数量大幅减少**：1篇论文只能生成5题（原来是20题）
2. **生成时间增加**：详细答案需要更多token
3. **成本上升**：每题API调用成本增加

### 重要澄清 ⚠️

**来时路文档中的错误**：
- ❌ 错误：原文档称"04生成1398题，处理298篇论文"
- ✅ 实际：04只是**单篇测试**，生成了**5道详细题**
- 📌 1398题应该是后续某个批量生成阶段的数据（可能是硅基流动批次）

---

## 💡 经验教训

### 成功经验
1. **详细答案确实质量更高**
2. **适合benchmark场景**（需要挑战性和深度）
3. **批处理工具很有价值**（为后续大规模生成奠定基础）

### 需要改进
1. **平衡数量与质量**：可以考虑混合策略（部分详细+部分普通）
2. **成本控制**：详细生成成本较高，需要优化
3. **自动化工具完善**：批处理系统在后续大规模生成中会用到

### 为批量生成铺路
本阶段开发的**批处理工具**（batch_auto_run等）为后续的大规模批量生成（07-08）提供了基础设施。

---

## 📁 文件结构

```
04_第四次尝试_详细问题/
├── README.md                           # 本文件
├── BATCH_DETAIL_Q_README.md            # 批处理说明
├── milestone1_detail_Q_generator.py    # 主脚本
├── scripts/
│   └── milestone1_detail_Q_generator.py  # 脚本副本
├── 辅助脚本/
│   ├── batch_auto_run.py               # 自动批处理
│   ├── run_full_batch.py               # 全速运行
│   ├── monitor_batch.py                # 进度监控
│   ├── batch_restart.py                # 失败重启
│   ├── test_batch_2files.py            # 小规模测试
│   └── run_batch_detail_q.py           # 批量运行入口
├── 数据工具/
│   ├── analyze_questions.py            # 统计分析
│   ├── extract_questions_to_md.py      # MD导出
│   └── count_questions.py              # 题目计数
└── prompts/
    └── 生成题Prompt_higherlever.md     # 高级prompt
```

---

## 🔗 相关尝试

- **上一步**: [03 保留原文](../03_第三次尝试_保留原文/)
- **下一步**: [05 洞察生成](../05_第五次尝试_洞察生成/)
- **批量应用**: 07-08 DeepSeek批量生成（使用相似策略大规模生成）
