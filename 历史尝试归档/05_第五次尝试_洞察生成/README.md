# 05 第五次尝试：洞察生成

## 📋 基本信息

- **时间**: 2024年10月（在04之后）
- **目标**: 从论文中先提取关键洞察，再基于洞察生成题目
- **方法**: 两阶段生成（提取洞察 → 生成题目）
- **模型**: `openai/deepseek-ai/DeepSeek-V3` (via SiliconFlow)
- **数据规模**: 1篇论文 → 10道题

---

## 🎯 尝试目标

在01-04的基础上，尝试全新策略：
1. **两阶段生成** - 不直接生成题目，先提取论文的关键洞察（insights）
2. **基于洞察出题** - 从洞察出发设计题目，而非从原文出发
3. **强化概念理解** - 更注重概念理解和推理分析
4. **测试新范式** - 验证"洞察驱动"是否优于"原文驱动"

---

## 🔧 技术细节（从脚本确认）

### 模型配置
- **生成模型**: `openai/deepseek-ai/DeepSeek-V3`
- **合规检查模型**: `openai/deepseek-ai/DeepSeek-V3`
- **题目数量**: 10道

### Prompt策略（从脚本提取的实际Prompt）

**核心任务**：
```
# ROLE
You are a senior expert in combustion science, heat transfer, fluid mechanics, 
CFD, and energy systems. You extract valuable insights from scientific papers.

# TASK
Generate 10 domain insights - things you learned or found interesting that 
require domain expertise to appreciate.

## ✅ WHAT IS AN "INSIGHT"?
- A non-obvious finding, mechanism, or principle you learned
- Something that deepens understanding of combustion/heat transfer/fluid/CFD/energy
- Could be counterintuitive result, subtle mechanism, quantitative relationship
- Should be interesting to domain experts, not just general readers

GOOD insight examples:
1. "Negative temperature coefficient (NTC) behavior in hydrocarbon oxidation 
   arises because alkylperoxy decomposition (ROO → olefin + HO2) competes 
   with chain-branching QOOH chemistry..."

2. "Three-body recombination reactions like H + O2 + M → HO2 + M become 
   dominant at pressures >30 bar, shifting ignition from chain-branching 
   to chain-propagation..."

3. "CFD turbulence models fail to capture cyclic variability in HCCI engines 
   because RANS averaging inherently filters out stochastic fluctuations..."

## ❌ NOT AN INSIGHT (Avoid):
- Paper meta-information: "This paper reviews..."
- Too general: "Machine learning can improve predictions"
- Time-sensitive: "In 2024, electric vehicles..."
- Overly broad: "Combustion is important..."
- Pure ML/CS without domain context

## 🎯 DOMAIN FOCUS - MANDATORY:
Insights MUST relate to:
- Combustion Science: chemical kinetics, ignition, flame dynamics
- Heat Transfer: thermal management, heat flux mechanisms
- Fluid Mechanics: turbulence, mixing, flow instabilities
- CFD: numerical methods, turbulence modeling, solver algorithms
- Energy Systems: engine performance, efficiency, emission control

## 📋 OUTPUT FORMAT:
{
  "insights": [
    {
      "insight_text": "Detailed technical insight (100-300 chars)",
      "original_text": {
        "1": "EXACT VERBATIM QUOTE FROM PAPER - at least 50 characters",
        "2": "ANOTHER EXACT QUOTE - provides evidence"
      },
      "domain": "combustion_kinetics",
      "tags": ["low_temperature_chemistry", "NTC", "chain_branching"]
    }
  ]
}
```

**关键特点**：
- **不是生成题目**：生成的是"领域洞察"（insights），不是Q&A题目
- **强调非显而易见**：要求counterintuitive, subtle, quantitative关系
- **禁止元信息**：不许说"这篇论文讨论了..."，要说"发现了什么机理"
- **领域深度**：必须需要专业知识才能理解的insight
- **带原文引用**：每个insight也要包含1-3条VERBATIM引用

**对比01-04的根本不同**：
- 01-04：生成题目（question + answer）
- 05：生成洞察（insight），然后（理论上）基于洞察再生成题目
  - 但实际脚本中**没有看到第二阶段"基于洞察生成题目"的代码**
  - 所以05实际上只是生成了10条领域洞察，并未生成题目

---

## 📂 文件结构

```
05_第五次尝试_洞察生成/
├── data/
│   ├── milestone1_insights.jsonl       # 生成的10道题（确认）
│   ├── milestone1_insights_raw.txt     # 原始响应
│   └── milestone1_insights_report.md   # 生成报告
├── scripts/
│   └── milestone1_insights_generator.py  # 生成脚本
├── milestone1_insights_generator.py      # 脚本副本
├── milestone1_insights_pro_generator.py  # 改进版（专业版）
└── README.md                            # 本文档
```

---

## 📊 生成结果

- **生成内容**: 10条领域洞察（insights），不是题目！
- **数据位置**: data/milestone1_insights.jsonl（验证：正好10行）
- **论文来源**: 1篇PECS综述
- **特点**: 强调非显而易见的机理发现，带原文引用

---

## 💡 主要发现（与01-04对比）

### ✅ 创新点
1. **改变生成对象** - 不生成题目，而是生成"领域洞察"
2. **强调非显而易见性** - 要求counterintuitive, subtle机理
3. **禁止元信息** - 不许说"论文讨论了"，要说"发现了什么"
4. **领域深度强制** - 必须需要专业知识才能理解

### ❌ 问题发现
1. **缺少第二阶段** - 脚本中只生成了insights，没有"基于insights生成题目"的第二阶段代码
2. **洞察不等于题目** - 生成了10条insight，但这些不能直接作为benchmark题目使用
3. **实验目的不明** - 如果是为了生成题目，应该有第二阶段；如果只是生成insights，那么对benchmark建设的价值不明确

### 🤔 实验结论
- **洞察生成本身成功** - 模型能够提取非显而易见的领域洞察
- **但未转化为题目** - 缺少"insights → questions"的转换步骤
- **可能是探索性尝试** - 测试是否先提取insight能帮助后续生成更好的题目
- **未进入最终版本** - 可能因为流程不完整或效果不如直接生成

---

## 🔄 后续影响

- **06专业版** - 继续优化洞察生成策略（milestone1_insights_pro_generator.py），可能尝试补充第二阶段
- **批量生成放弃此法** - 07/08批量生成时回归单阶段直接生成题目
- **启发"先理解再生成"思路** - 虽然未被采用，但"先提取insight再出题"的思想影响了后续prompt设计
- **证明insights有价值** - insights本身可以作为论文理解的中间产物，即使不直接转化为题目

---

## 📝 关键经验

1. **insights≠questions** - 洞察是有价值的，但不能直接作为benchmark题目
2. **缺少转换步骤** - 如果要采用"洞察驱动"，必须补充"insights→questions"的第二阶段
3. **探索性实验** - 05可能只是探索"能否提取高质量insights"，为后续决策提供参考
4. **最终未采纳** - 批量生成时选择了更直接的"从论文直接生成题目"方案

---

*这次尝试探索了"洞察提取"任务，虽然未转化为题目且未进入最终benchmark，但验证了模型提取领域深度insights的能力。*
