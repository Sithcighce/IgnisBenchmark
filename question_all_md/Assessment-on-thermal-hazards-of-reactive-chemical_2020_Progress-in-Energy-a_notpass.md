# Assessment-on-thermal-hazards-of-reactive-chemical_2020_Progress-in-Energy-a - Not Passed Questions

**生成时间**: 2025-10-15 15:46:06  
**未通过问题数**: 1

---

## Question 1

### 问题

Calculate the Self-Accelerating Decomposition Temperature (SADT) for a chemical with E_a=120 kJ/mol and T_on=200°C using the empirical correlation from Wang et al. (2010), and discuss how package size affects this parameter.

### 标准答案

Using Wang's linear correlation SADT = 0.2088T_on - 61.885 (T_in K): Convert T_on to Kelvin (473K), then SADT = 0.2088×473 - 61.885 = 36.9°C. Package size affects SADT through heat transfer parameters in the F-K theory: SADT ∝ 1/L² where L is characteristic length. Larger packages reduce surface-to-volume ratio, decreasing heat dissipation and lowering SADT. For cylindrical containers, critical radius r_c = √(λRT²/QE_aδ_c)exp(E_a/RT), showing explicit size dependence. Industrial-scale packages (e.g., 200L drums) typically exhibit SADT values 20-50°C lower than lab-scale tests due to this geometric effect, explaining why UN requires package-specific testing methods (H1-H4).

### 元数据

- **类型**: calculation
- **难度**: 4
- **主题**: heat_transfer
- **答案长度**: 681 字符

### 原文引用

**引用 1**:
> T M R ad = 0 . 2088 T on − 61 . 885 (9)

**引用 2**:
> SADT depends strongly on the ambient temperature, decomposition kinetics of substance, packaging shape, and the heat transfer properties of both substance and packaging.

### 质量检查

- **领域聚焦**: ✅ 通过
- **答案正确性**: ❌ 未通过
- **其他合规性**: ✅ 通过
- **总体评价**: fail

**领域聚焦分析**: 问题涉及化学反应动力学、热力学参数计算以及包装热传递效应，需要燃烧/传热/化工安全领域的专业知识

**答案问题**: factual_error, unsupported

**改进建议**: 答案存在两个关键问题：(1) 温度单位转换错误导致SADT计算结果不准确（未保持K→K转换的一致性）；(2) 临界半径公式未经文献支持。建议修正计算过程并补充F-K理论原始文献引用

### 来源

- **论文**: Assessment-on-thermal-hazards-of-reactive-chemical_2020_Progress-in-Energy-a
- **生成类型**: batch_generation
- **合并来源**: questions_copy

---

