# Milestone 1 Insights Pro - Quality Report

**Generation Time**: 2025-10-14 23:59:03  
**Model**: openai/deepseek-ai/DeepSeek-V3  
**Total Insights**: 5

---

## 📊 OVERALL RESULTS

| Metric | Count | Percentage |
|--------|-------|------------|
| **Citations Verified** | 0/5 | 0.0% |

---

## 📏 INSIGHT LENGTH STATISTICS

| Metric | Value |
|--------|-------|
| **Average Length** | 131 characters |
| **Shortest Insight** | 119 characters |
| **Longest Insight** | 160 characters |

---

## 🎯 DOMAIN DISTRIBUTION

| Domain | Count |
|--------|-------|
| combustion_modeling | 1 |
| combustion_dynamics | 1 |
| emission_modeling | 1 |
| combustion_diagnostics | 1 |
| turbulence_combustion | 1 |

---

## 📋 DETAILED INSIGHTS


### Insight 1 ❌

**Text**: 灰盒模型的关键创新在于在物理约束下学习数据模式。这是因为纯ML模型缺乏对燃烧基本物理原理的约束（如质量/能量守恒），而灰盒模型通过嵌入关键物理方程（如Arrhenius反应速率）作为正则化项，从而解决了小样本燃烧数据上的过拟合问题，同时避免了高保真CFD的计算瓶颈。这对复杂燃烧模式（如RCCI）的实时控制具有重要意义。

**Domain**: combustion_modeling

**Tags**: hybrid_modeling, physics-informed_ML, combustion_control

**Length**: 160 chars

**Citations verified**: ❌ (0/2)

**Citation issues**:
  - Citation 1: 66.2% similarity
  - Citation 2: 0.0% similarity

**Original Text**:
1. ML-based grey-box approach is proposed as a solution that combines the benefits from physics-based and ML-based models to provide robust and high fidelity solutions
2. These phenomena include: turbulent air and fuel flow mixing inside the combustion chamber; large number of thermo-kinetic nonlinear reactions


### Insight 2 ❌

**Text**: 循环变动预测需要捕捉压力振荡的高阶统计特征。这是因为传统CA50指标无法表征HCCI燃烧的随机性本质，而通过希尔伯特-黄变换（HHT）提取缸压信号的瞬时频率成分，结合高斯过程回归，可以量化压力振荡的混沌特性。这为不稳定燃烧模式的闭环控制提供了关键状态变量。

**Domain**: combustion_dynamics

**Tags**: cyclic_variability, pressure_oscillations, HCCI

**Length**: 128 chars

**Citations verified**: ❌ (0/2)

**Citation issues**:
  - Citation 1: 30.7% similarity
  - Citation 2: 65.4% similarity

**Original Text**:
1. combustion instability and cyclic variability control...require capturing the high frequency changes of in-cylinder pressure waves
2. GP was used in our previous work for classifying the regions of combustion phasing (CA50) cyclic variability


### Insight 3 ❌

**Text**: 排放物形成的多尺度特性决定了分层建模的必要性。这是因为NOx生成受宏观混合尺度主导，而碳烟形成依赖于燃油液滴尺度的微物理过程，需要分别采用大涡模拟（LES）和离散多相模型耦合数据驱动方法。这种多尺度方法显著提升了瞬态工况下的排放预测精度。

**Domain**: emission_modeling

**Tags**: multi-scale_modeling, soot_formation, NOx_prediction

**Length**: 119 chars

**Citations verified**: ❌ (0/2)

**Citation issues**:
  - Citation 1: 0.0% similarity
  - Citation 2: 0.0% similarity

**Original Text**:
1. Predicting the exact amount of emissions...is quite difficult since there are many factors that can affect formation of these species
2. These factors include: air-fuel distribution, combustion kinetics, local fuel-air equivalence ratio, in-cylinder temperature and pressure gradients


### Insight 4 ❌

**Text**: 爆震检测的物理本质在于末端气体自燃引发的压力波共振。这是因为通过短时傅里叶变换（STFT）提取缸压信号的特定频带能量（5-15kHz），比单纯监测最大压力升高率（PRR）更能区分正常燃烧与爆震。这种频域特征提取方法显著提高了爆震边界的识别精度。

**Domain**: combustion_diagnostics

**Tags**: knock_detection, pressure_oscillations, frequency_analysis

**Length**: 122 chars

**Citations verified**: ❌ (0/2)

**Citation issues**:
  - Citation 1: 0.0% similarity
  - Citation 2: 0.0% similarity

**Original Text**:
1. knock detection...requires capturing all the physical phenomena that affect the high frequency changes of in-cylinder pressure waves
2. combustion knock detection and control...has not been completely addressed by conventional ICE control approaches


### Insight 5 ❌

**Text**: 湍流-化学反应相互作用需要通过概率密度函数（PDF）方法建模。这是因为传统RANS模型无法解析湍流脉动对局部当量比的随机影响，而通过机器学习构建条件矩封闭的PDF输运方程，可以准确预测部分预混火焰的局部熄火现象。这对预测低负荷工况下的HC排放至关重要。

**Domain**: turbulence_combustion

**Tags**: PDF_method, turbulence-chemistry_interaction, partial_premix

**Length**: 126 chars

**Citations verified**: ❌ (0/2)

**Citation issues**:
  - Citation 1: 31.8% similarity
  - Citation 2: 0.0% similarity

**Original Text**:
1. turbulent air and fuel flow mixing inside the combustion chamber...exhibit highly nonlinear interactions
2. formation of particulate matters and gaseous emission...are affected by complex fluid-surface interactions

