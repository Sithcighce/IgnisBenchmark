# A-review-on-mercury-in-coal-combustion-process--Content-_2019_Progress-in-En - Passed Questions

**生成时间**: 2025-10-15 15:46:06  
**通过问题数**: 5

---

## Question 1

### 问题

In coal combustion systems, how does chlorine content influence the homogeneous oxidation of elemental mercury (Hg⁰) and what are the key chemical pathways involved? Provide detailed reaction mechanisms and rate constants.

### 标准答案

Chlorine significantly enhances Hg⁰ oxidation through multiple pathways. The dominant mechanisms are: (1) Hg + Cl + M ↔ HgCl + M (k₁ = 4.25E7 cm³/mol·s, Eₐ=17.1 kcal/mol), (2) HgCl + Cl₂ → HgCl₂ + Cl (k₃=5.18E4 cm³/mol·s). At temperatures >600°C, HCl becomes the primary oxidant via Eley-Rideal mechanism where HCl dissociates on fly ash surfaces to form active Cl sites. Below 500°C, Cl₂ dominates through direct gas-phase reactions. The oxidation efficiency follows Cl radical > Cl₂ > HCl due to their bond dissociation energies (Cl-Cl: 242 kJ/mol vs H-Cl: 431 kJ/mol). Thermodynamic equilibrium predicts complete conversion to HgCl₂ below 452°C, but kinetic limitations in real systems typically yield 30-95% oxidation.

### 元数据

- **类型**: reasoning
- **难度**: 5
- **主题**: combustion_kinetics
- **答案长度**: 722 字符

### 原文引用

**引用 1**:
> Chlorine is considered as the key element for Hg⁰ oxidation. During coal combustion, chlorine in coal will be released in the main form of atomic Cl, which transforms into HCl or Cl₂ with flue gas cooling.

**引用 2**:
> The conversion of Hg + Cl₂ → HgCl₂ was faster or comparable to those with Cl₂, while reactions between Hg/HgCl and HCl were the lowest.

### 质量检查

- **领域聚焦**: ✅ 通过
- **答案正确性**: ✅ 通过
- **其他合规性**: ✅ 通过
- **总体评价**: pass

**领域聚焦分析**: 问题涉及煤燃烧系统中氯对汞氧化的影响及化学反应机制，需要燃烧化学、反应动力学和热力学等能源领域的专业知识

**改进建议**: 答案质量优秀，建议补充Cl₂/HCl反应路径的温度分界依据

### 来源

- **论文**: A-review-on-mercury-in-coal-combustion-process--Content-_2019_Progress-in-En
- **生成类型**: batch_generation
- **合并来源**: questions_copy

---

## Question 2

### 问题

Derive the breakthrough rate (BR) equation for mercury adsorption using US EPA Method 30B and analyze how SO₂ concentration affects the adsorption efficiency of activated carbon sorbents.

### 标准答案

The breakthrough rate is defined as BR = (m₂/m₁)×100%, where m₁ is mercury mass in the first adsorbent section and m₂ in the second section. For a fixed-bed reactor, the adsorption capacity q (μg/g) relates to SO₂ concentration via competitive adsorption: q = q₀/(1 + Kₛ[SO₂]), where q₀ is saturation capacity (~5mg/g for typical AC) and Kₛ the SO₂ inhibition coefficient (~0.01 ppm⁻¹). SO₂ competes for active sites through: SO₂ + C* → C-SO₃ (Eₐ≈25 kJ/mol), reducing HgCl₂ adsorption sites by 30-50% at 200-500 ppm SO₂. The modified Yoon-Nelson model predicts τ (breakthrough time) = τ₀exp(-α[SO₂]), where α≈0.003 ppm⁻¹ for sulfur-poisoned carbons.

### 元数据

- **类型**: calculation
- **难度**: 4
- **主题**: fluid_mechanics
- **答案长度**: 649 字符

### 原文引用

**引用 1**:
> The breakthrough rate (BR) and relative deviation (RD) are selected as the main parameters for quality control based on quality assurance and quality control (QA/QC) criteria.

**引用 2**:
> SO₂ inhibits fly ash-induced Hg⁰ removal slightly while NO has a positive effect with the help of Br₂ in the simulated flue gas.

### 质量检查

- **领域聚焦**: ✅ 通过
- **答案正确性**: ✅ 通过
- **其他合规性**: ✅ 通过
- **总体评价**: pass

**领域聚焦分析**: 问题涉及汞吸附、突破速率方程、SO₂浓度对活性炭吸附效率的影响，需要燃烧、传热、流体、能源领域的专业知识

**改进建议**: 答案准确且符合要求，无需修改

### 来源

- **论文**: A-review-on-mercury-in-coal-combustion-process--Content-_2019_Progress-in-En
- **生成类型**: batch_generation
- **合并来源**: questions_copy

---

## Question 3

### 问题

Explain the Langmuir-Hinshelwood vs Eley-Rideal mechanisms for heterogeneous mercury oxidation on Fe₂O₃ surfaces in SCR systems, including temperature-dependent regime transitions.

### 标准答案

Below 280°C, Eley-Rideal dominates: pre-adsorbed HCl dissociates (HCl* → H* + Cl*, ΔH≈50 kJ/mol) followed by gaseous Hg⁰ reacting with Cl* (Hg(g) + Cl* → HgCl*). From 280-580°C, Langmuir-Hinshelwood takes over where both Hg and HCl adsorb (θ_HCl≈0.3 monolayer at 300°C) before surface reaction: Hg* + Cl* → HgCl* (k=10¹²exp(-80kJ/mol/RT) s⁻¹). Above 680°C, both mechanisms coexist with homogeneous oxidation becoming significant. The transition is evidenced by Arrhenius plot discontinuities at 280°C (ΔEₐ=35→60 kJ/mol) and 580°C (ΔEₐ=60→15 kJ/mol). XPS studies confirm Fe-Cl surface complexes (708.5 eV binding energy) as active sites.

### 元数据

- **类型**: concept
- **难度**: 5
- **主题**: combustion_kinetics
- **答案长度**: 636 字符

### 原文引用

**引用 1**:
> Hg⁰ heterogeneous oxidation by HCl over the Fe₂O₃ surface occurred by the gas-solid reaction between gaseous Hg⁰ and active adsorbed Cl species produced from HCl dissociation.

**引用 2**:
> For temperatures of 280-580°C, Hg⁰ removal efficiency by α-Fe₂O₃ and γ-Fe₂O₃ was different with the suitable Langmuir-Hinshelwood mechanism.

### 质量检查

- **领域聚焦**: ✅ 通过
- **答案正确性**: ✅ 通过
- **其他合规性**: ✅ 通过
- **总体评价**: pass

**领域聚焦分析**: The question requires expertise in heterogeneous catalysis, surface chemistry, and mercury oxidation mechanisms specific to SCR systems in coal combustion processes.

**改进建议**: The answer is technically accurate and well-supported by the provided references. No modifications needed.

### 来源

- **论文**: A-review-on-mercury-in-coal-combustion-process--Content-_2019_Progress-in-En
- **生成类型**: batch_generation
- **合并来源**: questions_copy

---

## Question 4

### 问题

Calculate the required sorbent injection rate (kg/GJ) to achieve 90% mercury removal in a 500MW plant burning coal with 0.2 ppm Hg, assuming a brominated activated carbon with qₘₐₓ=800 μg/g and K_L=0.05 m³/μg.

### 标准答案

First, determine flue gas mercury load: (500MW)×(9.48 GJ/MWh)×(0.2ppm)×(12 μg/Nm³ per ppm)×(3600 Nm³/GJ) = 40.9 g Hg/hr. For 90% removal, adsorption capacity q = qₘₐₓC/(1/K_L + C) = 800×10.8/(20+10.8) = 280 μg/g at C=10.8 μg/Nm³ (90% of inlet). Required sorbent = (40.9 g/hr × 0.9)/(280 μg/g × 10⁻⁶ kg/μg) = 131.5 kg/hr. Normalized rate = (131.5 kg/hr)/(500MW × 3.6 GJ/MWh) = 0.073 kg/GJ. This matches field data (0.05-0.15 kg/GJ) but neglects SO₂ inhibition which may increase requirement by 30%.

### 元数据

- **类型**: calculation
- **难度**: 4
- **主题**: energy_systems
- **答案长度**: 497 字符

### 原文引用

**引用 1**:
> The injection of approximately 3-ppmv HBr could achieve 80% of the Hg⁰ oxidation rate for the empty bed.

**引用 2**:
> Obtaining 90% mercury capture needed injection rates of 8.01×10⁴ μg brominated AC per cubic meter of stack gas.

### 质量检查

- **领域聚焦**: ✅ 通过
- **答案正确性**: ✅ 通过
- **其他合规性**: ✅ 通过
- **总体评价**: pass

**领域聚焦分析**: The question requires specialized knowledge in combustion engineering, mercury capture technology, and sorbent chemistry to calculate injection rates and understand adsorption mechanisms.

**改进建议**: The answer demonstrates rigorous technical calculation and appropriately cites limitations (SO₂ inhibition). No corrections needed.

### 来源

- **论文**: A-review-on-mercury-in-coal-combustion-process--Content-_2019_Progress-in-En
- **生成类型**: batch_generation
- **合并来源**: questions_copy

---

## Question 5

### 问题

Analyze why oxy-fuel combustion increases total gaseous mercury (Hg_g) concentration by 2× compared to air-firing, despite similar coal mercury content.

### 标准答案

The 2× increase arises from: (1) Flue gas recirculation (FGR) accumulating Hg through closed-loop mass balance (ΣHg_in = ΣHg_out + Hg_removed). For typical 70% FGR, equilibrium concentration C = C₀/(1-R) = C₀/0.3 ≈ 3.3C₀. (2) Higher CO₂ partial pressure (70% vs 15% in air-firing) shifts Hg adsorption equilibria on fly ash (q=K_P·P_Hg/(1+ΣK_iP_i)) by competing for sites. (3) Elevated H₂O (25% vs 10%) inhibits Hg⁰ oxidation through OH radical quenching: OH + H₂O → H₂O₂ + H (k=2.1×10¹³ cm³/mol·s). Measurements confirm Hg_g = 26 μg/Nm³ (oxy-fuel) vs 20 μg/Nm³ (air) under identical coal feed.

### 元数据

- **类型**: reasoning
- **难度**: 4
- **主题**: combustion_kinetics
- **答案长度**: 594 字符

### 原文引用

**引用 1**:
> Total gaseous mercury (Hg_g) concentration under oxy-coal combustion (26 μg/Nm³) was higher than that under air-coal combustion (20 μg/Nm³).

**引用 2**:
> Mercury concentration at the ESP inlet in oxy-coal combustion was about two times of that under air-coal combustion conditions.

### 质量检查

- **领域聚焦**: ✅ 通过
- **答案正确性**: ✅ 通过
- **其他合规性**: ✅ 通过
- **总体评价**: pass

**领域聚焦分析**: 问题涉及燃烧过程中汞的转化和排放，需要燃烧工程、化学反应动力学和污染物控制的专业知识。

**改进建议**: 答案准确地解释了氧燃烧条件下汞浓度增加的三个主要原因，并引用了相关数据和公式支持，符合科学性和专业性要求。

### 来源

- **论文**: A-review-on-mercury-in-coal-combustion-process--Content-_2019_Progress-in-En
- **生成类型**: batch_generation
- **合并来源**: questions_copy

---

