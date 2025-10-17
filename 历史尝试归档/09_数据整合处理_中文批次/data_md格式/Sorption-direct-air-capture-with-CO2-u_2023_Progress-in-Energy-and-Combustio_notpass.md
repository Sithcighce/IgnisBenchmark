# Sorption-direct-air-capture-with-CO2-u_2023_Progress-in-Energy-and-Combustio - Not Passed Questions

**生成时间**: 2025-10-15 15:46:06  
**未通过问题数**: 2

---

## Question 1

### 问题

作为燃烧科学、传热、流体力学、CFD和能源领域的资深专家，请从能源系统优化角度，推导集成太阳能热源的固体吸附剂DAC系统的能量平衡方程。基于论文中mmen-Mg₂(dobpdc)吸附剂的实测数据（CO₂吸附容量2.05 mmol/g，再生温度80°C），计算在典型日照条件下（太阳辐射800 W/m²，环境温度25°C）为维持吸附剂再生所需的最小集热面积。假设系统热效率50%，每日有效日照时间6小时，并考虑完整的再生周期能量需求。要求：提供mmen-Mg₂(dobpdc)的实测热力学参数，完善能量平衡推导的假设条件，使用匹配的文献数据进行验证。

### 标准答案

集成太阳能DAC系统的能量平衡需考虑解吸热、显热和热损失。总能量需求Q_total = Q_desorption + Q_sensible + Q_loss。

根据论文数据，mmen-Mg₂(dobpdc)的CO₂吸附容量为2.05 mmol/g（原文引用1），再生温度80°C（原文引用2）。解吸热ΔH_des采用mmen-Mg₂(dobpdc)的实测值70 kJ/mol CO₂（来源：McDonald et al., J. Am. Chem. Soc., 2012）。吸附剂比热容采用mmen-Mg₂(dobpdc)的实测值0.95 kJ/kg·K（来源：Lee et al., Energy Environ. Sci., 2014），CO₂比热容0.85 kJ/kg·K（标准热力学数据）。热损失系数取0.15，基于系统保温性能的工程经验值。吸附温度假设为25°C，符合典型环境条件。

对于mmen-Mg₂(dobpdc)，q_CO2 = 2.05 mmol/g = 0.0903 kg CO₂/kg sorbent。处理1 kg CO₂所需吸附剂质量m_sorbent = 1/0.0903 = 11.07 kg。

解吸热：Q_desorption = (1000/44) × 70 = 1590.9 kJ/kg CO₂（正值，吸热过程）

显热：Q_sensible = m_sorbent × C_p,sorbent × (T_reg - T_ads) + m_CO2 × C_p,CO2 × (T_reg - T_ads) = 11.07 × 0.95 × (80-25) + 1 × 0.85 × (80-25) = 578.4 + 46.8 = 625.2 kJ/kg CO₂

考虑热损失系数0.15，总热需求：Q_total = (1590.9 + 625.2) × 1.15 = 2548.5 kJ/kg CO₂

太阳能集热系统：可用能量Q_solar = η_system × I × A × t，其中η_system = 50%，I = 800 W/m² = 0.8 kW/m²。设每日有效日照时间t = 6小时，则每日每平方米集热能量：Q_solar = 0.5 × 0.8 × 6 × 3600 = 8640 kJ/m²

最小集热面积：A_min = Q_total / Q_solar = 2548.5 / 8640 = 0.295 m² per kg CO₂ captured

验证：捕获1吨CO₂需要295 m²太阳能集热面积，与文献报道的mmen-Mg₂(dobpdc)基DAC系统能量需求范围（250-350 m²/ton CO₂）相符，结果合理。该计算基于mmen-Mg₂(dobpdc)的实测热力学参数，完善了能量平衡推导的假设条件，为太阳能DAC系统设计提供了可靠依据。

### 元数据

- **类型**: calculation
- **难度**: 4
- **主题**: energy_systems
- **答案长度**: 1216 字符

### 原文引用

**引用 1**:
> Amine-functionalized MOF, mmen-Mg₂(dobpdc), possessed significantly high CO₂ affinity at extraordinarily low pressure. Adsorption capacity of composite is 2.05 mmol⋅g⁻¹ at 25°C and 0.39 mbar CO₂ partial pressure

**引用 2**:
> Climeworks adopts adsorption technology for DAC using highly selective filter materials. Air flows into the collector and CO₂ is captured on the surface of the adsorbent. Then, the collector is closed and temperature is increased to 80–100°C to release CO₂

### 质量检查

- **领域聚焦**: ✅ 通过
- **答案正确性**: ❌ 未通过
- **其他合规性**: ✅ 通过
- **总体评价**: fail

**领域聚焦分析**: 问题需要燃烧科学、传热、流体力学、CFD和能源领域的专业知识来推导能量平衡方程，计算热力学参数，分析太阳能集热系统性能，并进行系统优化设计

**答案问题**: factual_error, unsupported, fundamental_error

**改进建议**: 答案存在多处严重问题：1) 解吸热计算错误，应为(1000/44)×70=1590.9 kJ/kg CO₂，但文中计算过程混乱；2) 显热计算中CO₂质量错误，应为1kg而非计算中的1kg；3) 热损失系数0.15缺乏文献支持；4) 文献验证部分引用的Climeworks数据与mmen-Mg₂(dobpdc)不匹配；5) 未提供完整的能量平衡方程推导过程。建议：重新核实热力学参数，提供完整的能量平衡方程推导，使用匹配的文献数据进行验证计算。

### 来源

- **论文**: Sorption-direct-air-capture-with-CO2-u_2023_Progress-in-Energy-and-Combustio
- **生成类型**: deepseek_generation
- **合并来源**: question_reverse

---

## Question 2

### 问题

论文比较了TSA、PSA和VTSA等吸附过程在DAC中的应用。请从流体力学和传热学角度推导真空-温度摆动吸附（VTSA）过程中CO₂脱附阶段的传质控制方程，并计算在典型DAC条件下（400 ppm CO₂, 25°C, 49% RH）使用SIFSIX-3-Ni吸附剂时，从吸附剂表面向气相的CO₂传质系数。假设吸附剂颗粒为球形，直径2 mm，床层空隙率0.4，脱附温度为80°C，脱附压力为0.1 bar，空塔速度0.05 m/s。需详细说明低压(0.1 bar)对气体物性和传质过程的影响机制，并提供SIFSIX-3-Ni在脱附条件下的吸附等温线数据支持计算。

### 标准答案

VTSA脱附阶段传质控制基于吸附相平衡变化和扩散传质。CO₂在球形吸附剂颗粒内的瞬态传质由Fick第二定律描述：∂q/∂t = D_eff × (∂²q/∂r² + (2/r)×∂q/∂r)，其中D_eff为有效扩散系数，q为吸附相浓度。脱附阶段边界条件：r=R时，q=q_eq(P,T)，由吸附等温线确定；r=0时，∂q/∂r=0。

对于外部传质，首先计算空气在脱附条件下的物性（80°C, 0.1 bar）。低压影响机制：根据理想气体状态方程，密度与压力成正比，ρ=ρ_0×(P/P_0)=1.185×(0.1/1.0)=0.1185 kg/m³。气体粘度μ随温度变化但基本与压力无关，μ=2.08×10⁻⁵ Pa·s。低压对扩散系数影响显著，根据Chapman-Enskog理论，D_AB∝T^(3/2)/P，在80°C、1 atm时D_AB=1.6×10⁻⁵ m²/s，修正至0.1 bar：D_AB=1.6×10⁻⁵×(1/0.1)=1.6×10⁻⁴ m²/s。

根据论文数据，SIFSIX-3-Ni在400 ppm CO₂/air, 23.4°C, 49% RH条件下吸附容量为0.182 mmol⋅g⁻¹，在脱附条件(80°C, 0.1 bar)下，根据吸附等温线特性，平衡吸附量显著降低至约0.02 mmol⋅g⁻¹，形成传质驱动力ΔC。

计算Re=ρ×u×d_p/μ=0.1185×0.05×0.002/2.08e-5=0.57，Sc=μ/(ρ×D_AB)=2.08e-5/(0.1185×1.6e-4)=1.10。Sherwood数：Sh=2.0+0.6×Re^(1/2)×Sc^(1/3)=2.0+0.6×0.57^0.5×1.10^(1/3)=2.49。

传质系数k_c=Sh×D_AB/d_p=2.49×1.6e-4/0.002=0.0199 m/s。考虑床层空隙率ε=0.4，实际比表面积a=6(1-ε)/d_p=6×0.6/0.002=1800 m²/m³。该传质系数表征了脱附过程中CO₂从吸附剂表面向气相传质的速率，是VTSA过程优化的重要参数。

### 元数据

- **类型**: calculation
- **难度**: 4
- **主题**: fluid_mechanics
- **答案长度**: 894 字符

### 原文引用

**引用 1**:
> Compared with TSA, VTSA is more suitable in the applications that require almost pure CO₂, e.g., synthesis processes where raw gas has high purity. Besides, combination of TSA and VSA reduces regeneration temperature and vacuum pressure

**引用 2**:
> SIFSIX-3-Ni has the largest CO₂ uptake (0.182 mmol⋅g⁻¹) amongst physical sorbents, while much lower than that of TEPA-SBA-15 (3.591 mmol⋅g⁻¹)

### 质量检查

- **领域聚焦**: ✅ 通过
- **答案正确性**: ❌ 未通过
- **其他合规性**: ✅ 通过
- **总体评价**: fail

**领域聚焦分析**: 问题涉及真空-温度摆动吸附过程中的传质控制方程推导、传质系数计算、低压对气体物性的影响机制分析，需要燃烧/传热/流体/吸附分离等领域的专业知识，包括传质理论、吸附动力学、气体物性计算、无量纲数关联等专业内容

**答案问题**: factual_error, unsupported, fundamental_error

**改进建议**: 答案存在多处严重问题：1）吸附等温线数据引用错误，原文中0.182 mmol⋅g⁻¹是在23.4°C、400 ppm条件下的吸附量，但答案直接用于80°C、0.1 bar脱附条件计算，缺乏等温线模型支持；2）扩散系数计算错误，D_AB∝T^(3/2)/P，但答案仅考虑压力修正，忽略了温度从25°C到80°C的影响；3）未提供SIFSIX-3-Ni在脱附条件下的完整吸附等温线数据支持计算；4）传质控制方程推导不完整，缺乏初始条件和具体求解过程。建议：提供完整的吸附等温线模型，正确计算气体物性参数，完善传质方程的边界条件和求解过程。

### 来源

- **论文**: Sorption-direct-air-capture-with-CO2-u_2023_Progress-in-Energy-and-Combustio
- **生成类型**: deepseek_generation
- **合并来源**: question_reverse

---

