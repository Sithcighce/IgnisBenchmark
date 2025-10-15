# Fundamentals-of-window-ejected-fire-plumes-from-unde_2023_Progress-in-Energy - Passed Questions

**生成时间**: 2025-10-15 15:46:06  
**通过问题数**: 4

---

## Question 1

### 问题

基于论文中关于'Regime I'火灾的理论，详细推导并解释临界热释放率（HRR）为何是1500A√H kW，并分析在亚大气压（如拉萨64 kPa）条件下该临界值如何变化及其物理机理。

### 标准答案

临界HRR 1500A√H kW的推导基于'Regime I'火灾的通风控制燃烧机理。首先，根据伯努利方程和质量守恒，通过窗户进入的新鲜空气质量流量为ṁₐ ≈ 0.5A√H kg/s。空气中氧气质量分数y_O₂ ≈ 23%，单位质量空气消耗释放的热量ΔH_ox = ΔH_O₂·y_O₂ = 13100 kJ/kg × 0.23 ≈ 3000 kJ/kg。因此，室内燃烧的HRR为ṁₐ·ΔH_ox = 0.5A√H × 3000 = 1500A√H kW。当实际HRR超过此值时，室内氧气不足，未燃燃料通过窗户上部喷出形成外部火焰。在亚大气压条件下（如拉萨64 kPa），空气密度ρ_∞降低（从1.293降至0.829 kg/m³），导致质量流量ṁₐ减小。根据ṁₐ ∝ ρ_∞A√H，临界HRR变为1050A√H kW，降幅约30%。这源于浮力驱动流动减弱和氧气供应减少，使得火灾更容易达到通风不足状态，外部火焰更早形成。

### 元数据

- **类型**: calculation
- **难度**: 4
- **主题**: combustion_kinetics
- **答案长度**: 411 字符

### 原文引用

**引用 1**:
> The HRR inside the compartment (Q̇inside) reads [57,127]: Q̇inside = ṁₐ·ΔH_ox = 1500A√H kW

**引用 2**:
> For sub-atmospheric pressure, the air density, and hence the air/oxygen mass inflow rate of the sub-atmospheric pressure effect, is lower, and the critical HRR for flame ejection becomes [101]: Q̇inside = 0.133ΔH_ox /(c_pT_∞) ρ_∞A g^(1/2)H^(1/2) = 3000 × 0.35A√H = 1050A√H kW

### 质量检查

- **领域聚焦**: ✅ 通过
- **答案正确性**: ✅ 通过
- **其他合规性**: ✅ 通过
- **总体评价**: pass

**领域聚焦分析**: 问题涉及火灾动力学、通风控制燃烧、伯努利方程、质量守恒、热释放率计算、亚大气压条件下的燃烧特性等，需要燃烧科学、流体力学、传热学和火灾安全工程等领域的专业知识。

**改进建议**: 无需改进，问题和答案均符合质量要求。

### 来源

- **论文**: Fundamentals-of-window-ejected-fire-plumes-from-unde_2023_Progress-in-Energy
- **生成类型**: deepseek_generation
- **合并来源**: question_reverse

---

## Question 2

### 问题

推导并解释面向风对窗户喷出火焰高度的影响，基于论文提出的新组合特征空气卷吸长度尺度l_w = l₁(1 + α₃ U_W/√(gH)) + 2λl₂(1 - α₃ U_W/√(gH))，其中α₃ = 0.8 Q̇*_ex^(2/5) - 0.76。

### 标准答案

面向风通过改变空气卷吸模式影响火焰高度。风增强垂直于立面的前方卷吸（特征长度尺度l₁增加），同时抑制平行于立面的侧向卷吸（特征长度尺度l₂减少）。新组合长度尺度l_w量化了这种效应：l_w = l₁(1 + α₃ U_W/√(gH)) + 2λl₂(1 - α₃ U_W/√(gH))，其中U_W/√(gH)是弗劳德数，表示风惯性力与浮力的竞争。α₃ = 0.8 Q̇*_ex^(2/5) - 0.76是风效应系数，随过剩HRR增加而增加，表明高HRR时风影响更显著。λ = 0.317 Q̇*_ex^(2/5) - 0.352是卷吸强度差异系数。由于前方卷吸主导（l₁项权重更大），总体卷吸增强，导致火焰高度Z_f,v降低。无量纲因子K₂ = Z_f,v / Z_f,0 = (l₁ + 2λl₂) / [l₁(1 + α₃ U_W/√(gH)) + 2λl₂(1 - α₃ U_W/√(gH))]描述高度减少。例如，当U_W = 2 m/s, H = 1 m, Q̇*_ex = 2时，α₃ ≈ 0.8×2^(0.4) - 0.76 ≈ 0.45，l_w增加，K₂ < 1，火焰高度降低。风还改变温度分布，垂直温度相关系数κ_w随风速减小（K₃ = κ_w/κ₀ = -0.31 U_W + 1）。

### 元数据

- **类型**: calculation
- **难度**: 5
- **主题**: fluid_mechanics
- **答案长度**: 551 字符

### 原文引用

**引用 1**:
> A new combined characteristic air entrainment length scale (or an 'effective flame entrainment perimeter') under facing wind was proposed as follows: l_w = l₁(1 + α₃ U_W/√(gH)) + 2λl₂(1 - α₃ U_W/√(gH))

**引用 2**:
> The coefficient α₃, characterizing the effect of ambient wind, was found to relate to the dimensionless excess HRR (Q̇*_ex) as α₃ = 0.8 Q̇*_ex^(2/5) - 0.76

### 质量检查

- **领域聚焦**: ✅ 通过
- **答案正确性**: ✅ 通过
- **其他合规性**: ✅ 通过
- **总体评价**: pass

**领域聚焦分析**: 问题涉及燃烧科学、流体力学、传热学等专业领域，需要理解火焰动力学、空气卷吸机制、无量纲分析（弗劳德数）、热释放率参数等专业知识，属于典型的燃烧与火灾科学研究范畴。

**改进建议**: 答案质量较高，无需修改。

### 来源

- **论文**: Fundamentals-of-window-ejected-fire-plumes-from-unde_2023_Progress-in-Energy
- **生成类型**: deepseek_generation
- **合并来源**: question_reverse

---

## Question 3

### 问题

分析外部侧壁约束对窗户喷出火焰高度和温度分布的影响机理，并解释无量纲参数K = (l₁ + 2λl₂)/(l₁ + 2λl₂(1 - l₁/D))如何表征侧壁分离距离D的约束效应。

### 标准答案

外部侧壁约束通过限制侧向空气卷吸改变火焰形态。对于'半轴对称火灾'（Q̇*_ex > 1.3），侧向卷吸显著，侧壁减小有效卷吸周长，导致火焰高度增加。无量纲参数K量化了这种约束：分子(l₁ + 2λl₂)表示无侧壁时的总卷吸长度，其中l₁为前方特征长度，l₂为侧向特征长度，λ=0.317 Q̇*_ex^(2/5) - 0.352为前后卷吸强度差异系数。分母(l₁ + 2λl₂(1 - l₁/D))表示有侧壁时的有效卷吸长度，侧壁分离距离D减小则(1 - l₁/D)项减小，分母减小，K增大，火焰高度Z_f,D增加。温度分布也受影响，垂直温度剖面ΔT_z / T_∞与归一化高度Z* = (z - H_n)/l₁ · Q̇*_conv^(-2/5)相关，K修正后分为连续火焰区（Z* < 1.75）、间歇火焰区（1.75 ≤ Z* ≤ 3.12）和浮力羽流区（Z* > 3.12），约束导致温度升高和火焰高度扩展。当D足够大（D > l₃）时，约束可忽略；当D < l₃时，火焰高度显著增加。

### 元数据

- **类型**: reasoning
- **难度**: 4
- **主题**: fluid_mechanics
- **答案长度**: 447 字符

### 原文引用

**引用 1**:
> The flame height is shown to increase with decreasing separation distance between the side walls. A dimensionless model in relation to the characteristic length scales l₁ and l₂, the dimensionless excess HRR (Q̇*_ex, or the flame height ejected from the window, Z_f,D, Z_f) and the separation distance of side walls (D), was introduced: Z_f,D / Z_f = [l₁·(l₁ + 2λl₂)/(l₁ + 2λl₂(1 - l₁/D))] for Q̇*_ex > 1.3

**引用 2**:
> The dimensionless parameter K characterizes the air entrainment constraint effect for different side wall separation distances, as a function of the normalized vertical height as Z* = (z - H_n)/l₁· Q̇*_conv^(-2/5)

### 质量检查

- **领域聚焦**: ✅ 通过
- **答案正确性**: ✅ 通过
- **其他合规性**: ✅ 通过
- **总体评价**: pass

**领域聚焦分析**: 问题涉及燃烧动力学、火焰形态、空气卷吸机制、无量纲参数分析等专业内容，需要燃烧科学、传热传质、流体力学等领域的专业知识才能准确理解和回答

**改进建议**: 答案质量优秀，准确解释了外部侧壁约束对火焰高度和温度分布的影响机理，并正确解析了无量纲参数K的物理意义和数学表达，与原文引用和论文摘录内容一致

### 来源

- **论文**: Fundamentals-of-window-ejected-fire-plumes-from-unde_2023_Progress-in-Energy
- **生成类型**: deepseek_generation
- **合并来源**: question_reverse

---

## Question 4

### 问题

分析亚大气压（如64 kPa）对窗户喷出火焰温度分布和热通量的影响，并解释修正因子(α/α_Hefei)^(4/5) = 0.8在垂直温度剖面模型中的物理意义。

### 标准答案

亚大气压（64 kPa对比标准100 kPa）通过降低环境空气密度ρ_∞和减弱浮力影响火焰特性。空气密度从1.293降至0.829 kg/m³，导致空气卷吸系数α减少（α/α_Hefei = 0.8），因为卷吸由浮力驱动湍流控制，而浮力加速度与ρ_∞成反比。修正因子(α/α_Hefei)^(4/5) = 0.8用于垂直温度剖面模型：Θ = (ΔT_z l₁^(5/3)) / (Q̇^(2/3) T_∞/(c_p² ρ_z² g))^(1/2) = fcn((z - H_n - z_0)/l₁)。修正后，(z - H_n - z_0)/l₁ = 10.3 Θ - 1.69 × (α/α_Hefei)^(4/5) = 10.3 Θ - 1.35。这表示在相同无量纲高度下，亚大气压的温度ΔT_z更高，因为卷吸减少导致混合效率降低，未燃燃料需要更长时间燃烧。火焰高度增加（由于卷吸减少），热通量剖面沿立面扩展。例如，在z/Z_f = 0.5处，亚大气压的热通量可能更高，因为温度更高且火焰更贴近立面。总体而言，亚大气压增加火灾风险，需要更大的建筑间距来防止火势蔓延。

### 元数据

- **类型**: reasoning
- **难度**: 4
- **主题**: heat_transfer
- **答案长度**: 484 字符

### 原文引用

**引用 1**:
> A correction factor is thus recommended to account for the change in air entrainment at sub-atmospheric pressure, (α/α_Hefei)^(4/5) = 0.8, to describe the vertical temperature profile in ejected fire plumes, where α and α_Hefei are the air entrainment coefficient at sub-atmospheric and standard atmospheric pressure, respectively.

**引用 2**:
> The change in air entrainment also results in a change in flame height, which consequently leads to a change in heat flux profile upon the building facade. As the air entrainment is reduced, the fire plume flame height, and hence the extension of the heat flux profile upon the facade, is larger in the sub-atmospheric pressure than in standard atmospheric pressure.

### 质量检查

- **领域聚焦**: ✅ 通过
- **答案正确性**: ✅ 通过
- **其他合规性**: ✅ 通过
- **总体评价**: pass

**领域聚焦分析**: 问题涉及亚大气压下窗户喷出火焰的温度分布、热通量影响以及修正因子的物理意义，需要燃烧科学、流体力学、传热学和火灾动力学等领域的专业知识，包括空气卷吸机制、浮力驱动湍流、火焰高度模型和热通量剖面分析。

**改进建议**: 答案质量较高，无需修改。

### 来源

- **论文**: Fundamentals-of-window-ejected-fire-plumes-from-unde_2023_Progress-in-Energy
- **生成类型**: deepseek_generation
- **合并来源**: question_reverse

---

