# 01 第一次尝试：基础生成

## 📋 基本信息

- **时间**: 2024年10月
- **目标**: 验证从PECS论文自动生成题目的可行性
- **方法**: 使用基础prompt直接生成
- **模型**: `gemini/gemini-2.5-flash` (主) + `DeepSeek-V3` (备用，via SiliconFlow)
- **数据规模**: 1篇论文 → 20道题目

## 🎯 尝试目标

这是整个项目的**第一次尝试**，主要验证：
1. AI能否从专业论文中理解内容并生成题目
2. 生成的题目是否符合燃烧科学领域
3. 摸索prompt设计方向

---

## 🔧 技术细节

### 模型配置（从脚本确认）
- **主模型**: `gemini/gemini-2.5-flash`
- **备用**: `openai/deepseek-ai/DeepSeek-V3`
- **参数**: 
  - `temperature=0.8`
  - `max_tokens=8000`
  - `timeout=180s`
  - `response_format="json_object"` (强制JSON格式)

### Prompt核心要求（从脚本提取）
```
# ROLE
你是燃烧科学和工程热物理领域的资深专家

# TASK
生成20道高质量问题

## 题目要求：
1. 基于论文内容：问题必须源于论文的核心概念、理论或实验发现
2. 深度优先：避免简单定义题，应测试对概念的深层理解和应用能力
3. 类型多样：concept/reasoning/application/calculation
4. 难度分级（1-5）：
   - 1-2: 基础概念
   - 3: 中等难度
   - 4-5: 高难度，需深入分析
5. 标准答案：必须详细、准确，包含核心论点、支撑理由、必要公式
```

**输出格式**: JSON对象，包含questions数组，每题含：
- topic（子领域）
- difficulty（难度1-5）
- type（concept/reasoning/application/calculation）
- question_text（问题文本）
- standard_answer（详细标准答案，至少100字）

**输入**: 论文前50000字符

---

## 📂 文件结构

```
01_第一次尝试_基础生成/
├── data/
│   ├── milestone1_candidates.jsonl    # 生成的20道题目（确认）
│   ├── milestone1_raw_response.txt    # 模型原始响应
│   └── milestone1_report.md           # 生成报告
├── scripts/
│   └── milestone1_generator.py        # 生成脚本（含完整prompt）
├── prompts/                           # Prompt存档
├── MILESTONE1_DELIVERY.md             # 第一版交付报告
├── COMPARISON.md                      # 对比分析文档
└── README.md                          # 本文档
```

## 📊 生成结果

- **生成题目**: 20道（验证：data/milestone1_candidates.jsonl 正好20行）
- **论文来源**: 1篇PECS综述
- **成功率**: 100%（模型响应正常，JSON格式正确）

## 💡 主要发现

### ✅ 证明了可行性
- AI能够理解专业论文内容
- 能够生成符合领域的题目
- JSON格式输出可以正常解析
- Gemini模型表现稳定，DeepSeek备用机制有效

### ❌ 发现的问题
1. **缺乏原文依据** - 生成的题目无法追溯到论文具体段落，可能含"幻觉"
2. **质量难评估** - 没有建立客观的质量评估标准
3. **无验证机制** - 缺少后续的人工或自动质量检查流程

## 🔄 后续改进

基于这次探索，催生了后续尝试：
- **02次**: 增加对比策略，尝试不同prompt变体
- **03次**: 保留原文引用，要求题目附带原文段落（解决可追溯性）
- **04次**: 详细答案要求，进一步提升质量
- **批量生成**: 验证了基础架构，为大规模生成（07/08）铺平道路

## 📝 关键经验

1. **Prompt需要详细化** - 虽然已包含4类型、5难度，但缺少原文引用要求
2. **需要质量验证机制** - 不能只生成不验证（启发了后续多模型验证）
3. **模型配置很重要** - temperature=0.8在创造性和准确性间取得平衡
4. **强制JSON格式有效** - `response_format="json_object"`避免了格式解析问题

---

*这次尝试虽然题目未进入最终benchmark，但验证了技术路线的可行性，为后续所有工作奠定了基础。*
