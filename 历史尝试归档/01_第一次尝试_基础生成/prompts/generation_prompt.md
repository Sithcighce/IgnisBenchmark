# ROLE
你是燃烧科学和工程热物理领域的资深专家，擅长基于科研文献设计高质量的教学题目。

# TASK
基于以下PECS（Progress in Energy and Combustion Science）综述论文，生成**20道**高质量问题。

## 题目要求：
1. **基于论文内容**：问题必须源于论文的核心概念、理论或实验发现
2. **深度优先**：避免简单定义题，应测试对概念的深层理解和应用能力
3. **类型多样**：
   - **concept（概念理解）**：测试对关键概念的理解
   - **reasoning（推理分析）**：需要逻辑推理和因果分析
   - **application（应用）**：将理论应用到实际场景
   - **calculation（计算）**：涉及定量分析和计算（如适用）

4. **难度分级**（1-5）：
   - 1-2: 基础概念
   - 3: 中等难度，需要综合理解
   - 4-5: 高难度，需要深入分析或跨领域知识

5. **标准答案**：必须详细、准确，包含：
   - 核心论点
   - 支撑理由/机理解释
   - 必要的公式或数据（如有）

## 论文内容：
{paper_text[:50000]}  

# OUTPUT FORMAT
输出必须是一个JSON对象，包含questions数组，每个问题包含以下字段：

```json
{
  "questions": [
    {
      "topic": "具体子领域（如ignition_theory, flame_propagation等）",
      "difficulty": 1-5,
      "type": "concept/reasoning/application/calculation",
      "question_text": "问题文本（中文或英文）",
      "standard_answer": "详细标准答案（中文或英文）"
    }
  ]
}
```

**重要**：
- 只返回JSON，不要包含任何其他文本、解释或markdown代码块
- 确保生成正好20道题
- 标准答案必须足够详细（至少100字）
