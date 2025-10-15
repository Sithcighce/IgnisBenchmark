# New-concepts-in-biomass-gasificat_2015_Progress-in-Energy-and-Combustion-Sci - Passed Questions

**生成时间**: 2025-10-15 15:46:06  
**通过问题数**: 4

---

## Question 1

### 问题

分析超临界水气化中水的物性变化对传热和反应动力学的影响，解释为何在374°C、22.1MPa以上条件能实现高效湿生物质气化。从热力学和输运性质角度详细说明。

### 标准答案

超临界水在临界点(374°C, 22.1MPa)以上经历剧烈的物性变化：密度从~1000 kg/m³降至~100 kg/m³，粘度从~0.1 mPa·s降至~0.03 mPa·s，热导率出现峰值(~0.7 W/m·K)。这些变化显著影响传热和反应：1) 传热系数h ∝ k^0.6ρ^0.8Cp^0.4/μ^0.4，超临界条件下h提高3-5倍，促进快速加热；2) 扩散系数D ∝ T/μ，增加约10倍，加速反应物传输；3) 介电常数从~80降至~5，使水从极性溶剂变为非极性溶剂，有机物的溶解度提高数个数量级。从反应动力学看，超临界水作为反应介质和反应物参与反应：C_nH_mO_k + (2n-k)H_2O → nCO_2 + (2n+m/2-k)H_2，反应速率常数k = Aexp(-Ea/RT)，在超临界条件下Ea降低20-30%。热力学分析显示，在600°C以上，水煤气变换反应CO + H_2O ⇌ CO_2 + H_2的平衡常数K_p > 1，促进H_2生成。这些特性使得湿生物质无需干燥即可直接气化，能量效率达40-50%。

### 元数据

- **类型**: concept
- **难度**: 4
- **主题**: heat_transfer
- **答案长度**: 470 字符

### 原文引用

**引用 1**:
> Water in its supercritical condition has unique properties as solvent and as reactant. Solubility of organic materials and gases is significantly increased

**引用 2**:
> At reaction temperatures below 450°C, CH4 is the main component in the produced gas, whereas at reaction temperatures above 600°C hydrogen is dominant

### 质量检查

- **领域聚焦**: ✅ 通过
- **答案正确性**: ✅ 通过
- **其他合规性**: ✅ 通过
- **总体评价**: pass

**领域聚焦分析**: 问题涉及超临界水气化、水的物性变化、传热和反应动力学分析，需要燃烧/传热/流体/能源领域的专业知识，特别是热力学和输运性质的专业知识

### 来源

- **论文**: New-concepts-in-biomass-gasificat_2015_Progress-in-Energy-and-Combustion-Sci
- **生成类型**: deepseek_generation
- **合并来源**: question_reverse

---

## Question 2

### 问题

建立双流化床气化器的CFD模型，考虑气固两相流动、传热和化学反应。列出控制方程并说明如何耦合求解气体组分输运、颗粒运动和反应动力学。

### 标准答案

双流化床气化器的CFD模型基于欧拉-欧拉多相流框架，控制方程包括：连续性方程∂(α_gρ_g)/∂t + ∇·(α_gρ_gv_g) = S_m，动量方程∂(α_gρ_gv_g)/∂t + ∇·(α_gρ_gv_gv_g) = -α_g∇p + ∇·τ_g + α_gρ_gg + K_gs(v_s-v_g)，能量方程∂(α_gρ_gH_g)/∂t + ∇·(α_gρ_gv_gH_g) = ∇·(α_gk_g∇T_g) + Q_gs + Q_chem。化学反应包括生物质热解：Biomass → Char + Volatiles，焦油重整：C_nH_m + nH_2O → nCO + (n+m/2)H_2，水煤气变换：CO + H_2O ⇌ CO_2 + H_2。采用有限速率/涡耗散模型计算反应速率。颗粒相采用动能理论封闭应力项。耦合求解策略：1) 求解流动场获得速度压力分布；2) 求解能量方程获得温度场；3) 求解组分输运方程更新浓度；4) 更新反应源项；迭代至收敛。关键参数：气体速度0.5-2 m/s，颗粒直径200-500 μm，操作温度800-900°C，固含率0.2-0.4。模型验证需与实验测量的温度分布和气体组成对比。

### 元数据

- **类型**: calculation
- **难度**: 5
- **主题**: CFD_modeling
- **答案长度**: 521 字符

### 原文引用

**引用 1**:
> Dual fluidized bed (DFB) systems physically separate gasification and combustion reactions and utilize the mineral particle bed to transfer heat between them

**引用 2**:
> The gasifier is a bubbling bed fluidized by steam, where the biomass feedstock is devolatilized, and organic vapours and char are properly steam reformed

### 质量检查

- **领域聚焦**: ✅ 通过
- **答案正确性**: ✅ 通过
- **其他合规性**: ✅ 通过
- **总体评价**: pass

**领域聚焦分析**: 问题涉及双流化床气化器的CFD建模，需要燃烧工程、多相流、传热传质、化学反应动力学等专业领域的深入知识，包括控制方程建立、耦合求解策略和反应机理描述

**改进建议**: 答案质量优秀，无需修改。涵盖了控制方程、耦合求解策略、关键反应机理和模型验证方法，技术细节准确完整

### 来源

- **论文**: New-concepts-in-biomass-gasificat_2015_Progress-in-Energy-and-Combustion-Sci
- **生成类型**: deepseek_generation
- **合并来源**: question_reverse

---

## Question 3

### 问题

分析多联产系统中SOFC与生物质气化集成的热力学极限效率，考虑气体净化要求、电化学反应和热回收。推导系统㶲效率表达式并讨论主要损失来源。

### 标准答案

SOFC与生物质气化集成的系统㶲效率η_ex = W_net/(m_biomass·ex_biomass)，其中ex_biomass ≈ LHV_biomass·(1.044 + 0.016·(H/C) - 0.3493·(O/C)(1+0.0531·(H/C)) + 0.0493·(N/C))。SOFC电效率η_FC = V_cell/V_th·η_F，其中V_th为热力学电压，η_F为燃料利用率。系统包括：气化单元(η_gas≈0.7-0.8)、气体净化(Δp≈5-10 kPa)、SOFC(η_FC≈0.5-0.6)、余热回收。总㶲损失包括：1) 气化过程不可逆损失(约25%)，主要来自化学反应㶲损；2) 气体净化压降损失(约5%)；3) SOFC极化损失，包括活化极化η_act = (RT/αF)ln(j/j_0)、欧姆极化η_ohm = j·ASR、浓度极化η_conc = (RT/2F)ln(1-j/j_L)；4) 热损失(约10%)。理论最大㶲效率可达65%，实际系统约45-55%。优化方向：提高操作温度(降低活化极化)、优化气体组成(H_2/CO比)、改进热集成。气体净化要求：颗粒物<1 mg/m³，H_2S<1 ppm，卤化物<0.1 ppm，以满足SOFC长期稳定运行。

### 元数据

- **类型**: reasoning
- **难度**: 5
- **主题**: energy_systems
- **答案长度**: 552 字符

### 原文引用

**引用 1**:
> The combination of a SOFC and an MGT with a biomass gasifier offers a very efficient power production solution for small decentralized CHP plants

**引用 2**:
> Modelling studies showed an electrical efficiency of 58% and a CHP efficiency of 87.5% for an optimized process using the two stage Viking gasifier combined with a SOFC and an MGT

### 质量检查

- **领域聚焦**: ✅ 通过
- **答案正确性**: ✅ 通过
- **其他合规性**: ✅ 通过
- **总体评价**: pass

**领域聚焦分析**: 问题涉及固体氧化物燃料电池(SOFC)、生物质气化、热力学效率分析、㶲效率计算、电化学反应机理、气体净化要求等专业内容，需要燃烧工程、能源系统、热力学和电化学领域的专业知识

**改进建议**: 答案质量较高，提供了详细的㶲效率表达式、损失来源分析和优化方向，符合专业要求。建议可以进一步补充气体净化对系统效率的具体影响量化分析

### 来源

- **论文**: New-concepts-in-biomass-gasificat_2015_Progress-in-Energy-and-Combustion-Sci
- **生成类型**: deepseek_generation
- **合并来源**: question_reverse

---

## Question 4

### 问题

在UNIQUE气化炉中，催化过滤烛如何同时实现焦油重整和颗粒物脱除？请从化学反应动力学和流体力学角度分析其工作原理，并解释为何这种集成设计能提高整体效率。

### 标准答案

UNIQUE气化炉中的催化过滤烛通过多孔陶瓷结构实现物理过滤和催化反应的集成。从流体力学角度，气体以特定过滤速度（通常1-3 cm/s）通过多孔陶瓷壁面，根据达西定律ΔP = μvL/k，其中μ为气体粘度，v为过滤速度，L为壁厚，k为渗透率。颗粒物在壁面形成滤饼，通过周期性反吹清除。从化学反应动力学角度，Ni基催化剂促进焦油蒸汽重整反应：C_nH_m + nH_2O → nCO + (n+m/2)H_2，反应速率遵循Langmuir-Hinshelwood机理r = kθ_Tθ_S，其中θ_T和θ_S分别为焦油和蒸汽的表面覆盖率。在800-900°C操作温度下，焦油转化率可达95%以上。这种集成设计避免了传统工艺中的热量损失，因为反应热直接用于维持气化温度，同时颗粒物脱除防止了催化剂堵塞，延长了使用寿命。

### 元数据

- **类型**: reasoning
- **难度**: 4
- **主题**: energy_systems
- **答案长度**: 357 字符

### 原文引用

**引用 1**:
> Catalytic filter elements for particle and tar removal are directly integrated into the freeboard of a fluidized bed steam gasifier

**引用 2**:
> Tar content reduction is as high as 95%; at bench scale a greater methane conversion was obtained (with a maximum value of 40%)

### 质量检查

- **领域聚焦**: ✅ 通过
- **答案正确性**: ✅ 通过
- **其他合规性**: ✅ 通过
- **总体评价**: pass

**领域聚焦分析**: 问题涉及气化炉中的催化过滤烛工作原理，需要燃烧工程、化学反应动力学、流体力学、多相流、传质传热等专业领域知识，属于能源与化工工程范畴

**改进建议**: 答案质量优秀，无需修改。答案从流体力学（达西定律、过滤速度、滤饼形成）和化学反应动力学（Langmuir-Hinshelwood机理、反应速率方程）角度详细分析了催化过滤烛的工作原理，并正确解释了集成设计的效率优势，与论文摘录中的信息一致

### 来源

- **论文**: New-concepts-in-biomass-gasificat_2015_Progress-in-Energy-and-Combustion-Sci
- **生成类型**: deepseek_generation
- **合并来源**: question_reverse

---

