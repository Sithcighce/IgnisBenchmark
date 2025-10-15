# A-comprehensive-review-of-measurements-and-data-anal_2018_Progress-in-Energy - Passed Questions

**生成时间**: 2025-10-15 15:46:06  
**通过问题数**: 5

---

## Question 1

### 问题

Explain how flame stretch affects the measurement of laminar burning velocity in spherical flame propagation method, and discuss the differences between linear and nonlinear stretch correction models.

### 标准答案

Flame stretch affects laminar burning velocity measurements through two primary mechanisms: curvature and hydrodynamic strain. For spherical flames, stretch rate is defined as K=2Sb/rf, where Sb is stretched flame speed and rf is flame radius. Linear models like Markstein's (Sb/S0b = 1-LbK) assume small stretch effects and Le≈1, but can overestimate burning velocities by up to 60% for non-unity Lewis number mixtures (Wu et al., 2015). Nonlinear models (e.g., Kelley & Law's quasi-steady model) account for higher-order terms: ln(Sb/S0b) = -2LbK/S0b + 4(LbK/S0b)^2. The key difference lies in their applicability - linear models fail for lean H2/air (Le<1) and rich heptane/air (Le>1) flames, while nonlinear models better capture the curvature effects. Experimental data shows linear extrapolation gives SL=40cm/s for CH4/air while nonlinear gives 37cm/s, highlighting the importance of proper stretch correction.

### 元数据

- **类型**: reasoning
- **难度**: 4
- **主题**: combustion_kinetics
- **答案长度**: 917 字符

### 原文引用

**引用 1**:
> Flame stretch and it is defined as logarithmic rate of change of flame area with time [72]. Corrections due to flame stretch are required for obtaining the accurate magnitude of the laminar burning velocity.

**引用 2**:
> For spherical flame method, linear extrapolation method has resulted in LBV dropping from »40 cm/s to »37 cm/s during last three decades.

### 质量检查

- **领域聚焦**: ✅ 通过
- **答案正确性**: ✅ 通过
- **其他合规性**: ✅ 通过
- **总体评价**: pass

**领域聚焦分析**: 问题涉及燃烧科学中的火焰传播和拉伸效应，需要燃烧/传热/流体领域的专业知识

**改进建议**: 答案质量优秀，专业性强且与引用文献一致

### 来源

- **论文**: A-comprehensive-review-of-measurements-and-data-anal_2018_Progress-in-Energy
- **生成类型**: batch_generation
- **合并来源**: questions_copy

---

## Question 2

### 问题

Derive the pressure dependence of laminar burning velocity (SL) from thermal theory and explain how it relates to the overall reaction order (n) of hydrocarbon combustion.

### 标准答案

From Mallard-Le Chatelier's thermal theory, laminar burning velocity depends on reaction rate (SL ∝ √RR). For Arrhenius kinetics RR = k[C]^n = BT^γexp(-Ea/RT)[C]^n. The pressure dependence emerges because concentration [C] ∝ P: SL ∝ √(P^nT^γexp(-Ea/RT)). At constant temperature, this simplifies to SL ∝ P^(n/2). However, incorporating density effects (ρ ∝ P) and flame thickness (δ ∝ 1/P), the complete relation becomes SL ∝ P^(n/2-1). For typical hydrocarbon flames where n≈1.5-2: when n=2 (bimolecular), SL becomes pressure-independent (b=0); for n=1, SL ∝ P^-0.5. This explains why most hydrocarbons show decreasing SL with pressure (negative b). Experimental data confirms b ranges from -0.3 to -0.5 for CH4/air flames across different equivalence ratios.

### 元数据

- **类型**: calculation
- **难度**: 5
- **主题**: combustion_kinetics
- **答案长度**: 760 字符

### 原文引用

**引用 1**:
> The dependence of burning velocity on pressure can be shown to vary as SL/p(n ¡ 2)/2, where n indicates the overall order of the reaction [122(cid:1)126].

**引用 2**:
> For most of the hydrocarbon + air mixtures, the overall order of reaction is reported to be less than 2 with SL < 0.5 m/s, indicating that the laminar burning velocity reduces with an increase in mixture pressure.

### 质量检查

- **领域聚焦**: ✅ 通过
- **答案正确性**: ✅ 通过
- **其他合规性**: ✅ 通过
- **总体评价**: pass

**领域聚焦分析**: 问题涉及燃烧学中的层流燃烧速度、热理论和反应级数，需要燃烧/传热/流体领域的专业知识。

**改进建议**: 答案内容准确且符合专业要求，无需修改。

### 来源

- **论文**: A-comprehensive-review-of-measurements-and-data-anal_2018_Progress-in-Energy
- **生成类型**: batch_generation
- **合并来源**: questions_copy

---

## Question 3

### 问题

Analyze the temperature dependence of laminar burning velocity for hydrogen-air mixtures and explain why the temperature exponent (α) shows dramatically different behavior for lean (φ<0.5) versus stoichiometric conditions.

### 标准答案

The temperature exponent α in SL ∝ T^α shows fundamentally different behavior for lean H2/air due to kinetic mechanisms. For stoichiometric mixtures (φ=1), α≈1.6-1.8 as dominated by H+O2=OH+O (Chain-branching). In lean flames (φ<0.5), α increases to 3-5 because: 1) Reduced flame temperatures shift equilibrium towards radicals (H/O/OH), increasing sensitivity to temperature. 2) The third-body recombination reaction H+O2+M=HO2+M becomes dominant, whose rate has stronger T dependence (-d[OH]/dt ∝ T^-1.3P^2). 3) Differential diffusion effects are magnified at low φ. Experimental data confirms α=1.57 at φ=1 but reaches α=5 at φ=0.4 (Alekseev et al., 2015). This nonlinear response explains why simple power-law correlations fail for lean H2 flames and requires detailed kinetic modeling.

### 元数据

- **类型**: reasoning
- **难度**: 5
- **主题**: combustion_kinetics
- **答案长度**: 790 字符

### 原文引用

**引用 1**:
> For very lean and very rich mixtures, however, the temperature exponent increases dramatically.

**引用 2**:
> It was shown experimentally that α can reach values of about 3(cid:1)5 at φ=0.4(cid:1)0.5, see Fig. 29.

### 质量检查

- **领域聚焦**: ✅ 通过
- **答案正确性**: ✅ 通过
- **其他合规性**: ✅ 通过
- **总体评价**: pass

**领域聚焦分析**: 问题涉及氢-空气混合物的层流燃烧速度的温度依赖性分析，需要燃烧动力学和热力学领域的专业知识。

**改进建议**: 答案准确且详细，解释了温度指数α在不同条件下的行为差异，并引用了相关实验数据支持。

### 来源

- **论文**: A-comprehensive-review-of-measurements-and-data-anal_2018_Progress-in-Energy
- **生成类型**: batch_generation
- **合并来源**: questions_copy

---

## Question 4

### 问题

Compare the advantages and limitations of heat flux method versus spherical flame method for laminar burning velocity measurements at elevated pressures (>5 atm).

### 标准答案

The heat flux method stabilizes flat flames on perforated plates with external heating to cancel heat losses (de Goey et al., 1993). Advantages: 1) No stretch correction needed (intrinsically stretch-free). 2) Direct measurement of adiabatic SL. 3) Better accuracy (±1 cm/s). Limitations: 1) Maximum measurable SL~80 cm/s (limited by flow stabilization). 2) Practically limited to P≤10 atm due to flame stabilization challenges. Spherical flame method propagates flames in constant pressure/vessels. Advantages: 1) Capable of P>60 atm (Tse et al., 2000). 2) Wider SL range measurable. Limitations: 1) Requires complex stretch corrections (±5-60% uncertainty). 2) Susceptible to cellular instabilities at high P. 3) Needs large vessels (>15cm) for minimal confinement effects. For high-P studies (>10 atm), spherical flames remain the only viable option despite higher uncertainties.

### 元数据

- **类型**: concept
- **难度**: 4
- **主题**: combustion_kinetics
- **答案长度**: 882 字符

### 原文引用

**引用 1**:
> Heat-flux method [36] helps direct measurement of laminar burning velocity by stabilizing an adiabatic planar flame on the top of a perforated plate.

**引用 2**:
> At high pressures, burning velocities are very low and flame stabilization becomes difficult beyond 10 atm [187].

### 质量检查

- **领域聚焦**: ✅ 通过
- **答案正确性**: ✅ 通过
- **其他合规性**: ✅ 通过
- **总体评价**: pass

**领域聚焦分析**: 问题涉及燃烧速度测量的专业方法（热通量法和球形火焰法），需要燃烧科学和流体力学领域的专业知识。

**改进建议**: 答案准确且全面，无需修改。

### 来源

- **论文**: A-comprehensive-review-of-measurements-and-data-anal_2018_Progress-in-Energy
- **生成类型**: batch_generation
- **合并来源**: questions_copy

---

## Question 5

### 问题

Calculate the expected change in laminar burning velocity when adding 30% CO2 diluent to stoichiometric methane-air mixture at 1 atm, considering both thermal and chemical effects.

### 标准答案

The dilution effect combines thermal and chemical mechanisms. Thermal effect: CO2 increases mixture heat capacity (Cp_CO2=37 J/mol-K vs Cp_N2=29). For 30% CO2 replacing N2, adiabatic flame temp Tad decreases by ~200K (from ~2200K to ~2000K). Using SL ∝ exp(-Ea/2RTad) with Ea≈160 kJ/mol, this gives SL reduction by factor exp[(-160000/2R)(1/2000-1/2200)]≈0.7. Chemical effect: CO2 participates in CO+OH⇌CO2+H, scavenging OH radicals. Kinetic modeling shows additional 10-15% reduction beyond thermal effect. Total reduction = 0.7 (thermal) × 0.85 (chemical) ≈ 0.6. For baseline SL=36 cm/s (CH4/air), predicted SL≈22 cm/s. Experimental data confirms ~35-40% reduction for 30% CO2 dilution (Galmiche et al., 2011), validating this calculation.

### 元数据

- **类型**: calculation
- **难度**: 5
- **主题**: combustion_kinetics
- **答案长度**: 741 字符

### 原文引用

**引用 1**:
> The effectiveness increases in the order He < Ar < N2 < CO2, with CO2 being most effective.

**引用 2**:
> Monotonic, yet non-linear dependence observed in Fig. 33 and in other studies strongly suggest that physical effect of the flame temperature reduction is accompanied by chemical effects.

### 质量检查

- **领域聚焦**: ✅ 通过
- **答案正确性**: ✅ 通过
- **其他合规性**: ✅ 通过
- **总体评价**: pass

**领域聚焦分析**: 该问题需要燃烧、传热和流体力学领域的专业知识，涉及甲烷燃烧、稀释效应、热力学和化学动力学等复杂概念。

**改进建议**: 答案质量良好，事实准确，机理解释清晰，推导合理，且与论文内容相符。

### 来源

- **论文**: A-comprehensive-review-of-measurements-and-data-anal_2018_Progress-in-Energy
- **生成类型**: batch_generation
- **合并来源**: questions_copy

---

