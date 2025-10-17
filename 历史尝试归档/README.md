# IgnisBenchmark 历史尝试归档

本目录记录了IgnisBenchmark项目从最初尝试到最终交付的完整历程。

---

## 📋 项目历程总览

### 阶段1-8：题目生成探索
我们尝试了多种不同的生成策略，不断改进题目质量：

1. **基础生成** → 单模型直接生成
2. **对比生成** → 测试不同prompt策略
3. **增强生成** → 保留原文引用
4. **详细生成** → 增加题目复杂度
5. **洞察生成** → 基于论文关键洞察
6. **多模型尝试** → DeepSeek英文/智能生成
7. **批量生成** → 大规模题目积累

### 阶段9：质量保证革命
建立了三模型（Claude Sonnet 4.5 + GPT-5 + Gemini 2.5 Pro）验证系统：
- 每道题目必须三个模型一致通过
- 验证原文忠实度、标答准确性、题目合理性
- 产出：984道高质量题目（best.json）

### 阶段10：精选筛选
从通过验证的题目中筛选最优质的：
- 去除重复和边界情况
- 分类整理（pass.json, notpass.json）
- needs_review机制保留边界案例

### 阶段11：实战测试
GPT-5实际答题测试：
- 测试了872/984题（中断于余额不足）
- 花费$62.02
- 原始准确率：82.57%

### 阶段12：深度分析
数据恢复与深度分析：
- 从日志完整恢复872个结果
- 区分真实错误vs API失败
- 调整后准确率：90.45%
- 识别145道挑战性题目

### 阶段13：最终交付
创建可用的benchmark产品：
- 145道挑战性题目
- 4个版本满足不同需求
- 完整文档和使用说明

---

## 📊 关键数据

### 题目生成
- **生成轮次**: 8轮不同策略
- **候选题目**: 数千道
- **验证通过**: 984道（three-model consensus）
- **最终筛选**: 145道挑战性题目

### 质量保证
- **验证模型**: 3个顶级模型
- **验证维度**: 原文、标答、合理性
- **一致性要求**: 100%（all_correct）

### 性能测试
- **测试模型**: GPT-5
- **测试题目**: 872题
- **准确率**: 90.45%（排除API失败）
- **成本**: $62.02

### 最终产出
- **Benchmark题目**: 145道
- **难度范围**: 3-5级
- **主题覆盖**: 20+专业主题
- **文件版本**: 4个（basic/verification/gpt5/complete）

---

## 🎯 关键里程碑

1. ✅ **第一道题目生成** (01_第一次尝试)
2. ✅ **建立三模型验证** (09_三模型验证系统)
3. ✅ **筛选出984道高质量题目** (10_质量筛选)
4. ✅ **GPT-5实测完成** (11_GPT5答题测试)
5. ✅ **数据完整恢复** (12_数据恢复与分析)
6. ✅ **Benchmark正式发布** (13_最终交付)

---

## 📁 目录结构

```
历史尝试归档/
├── README.md                        # 本文件
├── 01_第一次尝试_基础生成/
│   ├── README.md
│   └── milestone1_generator.py
├── 02_对比生成尝试/
│   ├── README.md
│   └── milestone1_compare_generator.py
├── 03_增强生成_包含原文/
│   ├── README.md
│   └── milestone1_withtext_generator.py
├── 04_详细题目生成/
│   ├── README.md
│   └── milestone1_detail_Q_generator.py
├── 05_洞察生成/
│   ├── README.md
│   ├── milestone1_insights_generator.py
│   └── milestone1_insights_pro_generator.py
├── 06_DeepSeek英文生成/
│   ├── README.md
│   └── deepseek_english_generator.py
├── 07_DeepSeek智能生成/
│   ├── README.md
│   └── deepseek_intelligent_generator.py
├── 08_批量详细生成/
│   ├── README.md
│   └── batch_detail_q_generator.py
├── 09_三模型验证系统/
│   ├── README.md
│   └── src/question_generator.py
├── 10_质量筛选/
│   └── README.md
├── 11_GPT5答题测试/
│   ├── README.md
│   └── data/gpt5_benchmark.log
├── 12_数据恢复与分析/
│   ├── README.md
│   ├── recover_from_log.py
│   ├── filter_real_errors.py
│   ├── categorize_all_questions_final.py
│   └── data/
│       ├── benchmarkGPT5_recovered.json
│       ├── gpt5_real_errors.json
│       └── complete_question_categorization.json
└── 13_最终交付/
    ├── README.md
    ├── create_final_benchmark.py
    └── data/
        ├── benchmark_basic.json
        ├── benchmark_with_verification.json
        ├── benchmark_with_gpt5_results.json
        └── benchmark_complete.json
```

---

## 🔍 如何使用归档

### 查看特定阶段
每个文件夹包含：
- **README.md**: 该阶段的详细说明
- **脚本文件**: 当时使用的代码（已调整相对路径）
- **data/**: 该阶段产生的数据（如果有）

### 复现某个阶段
1. 进入相应文件夹
2. 阅读README了解背景
3. 查看脚本代码
4. （可选）运行脚本复现

### 学习项目演进
- 按数字顺序浏览各阶段
- 对比不同阶段的策略变化
- 理解每个决策的原因

---

## 💡 经验总结

### 题目生成
- ✅ 多轮迭代比一次性生成更有效
- ✅ 原文引用是质量保证的关键
- ✅ 不同策略适合不同类型的题目

### 质量保证
- ✅ 三模型验证是金标准
- ✅ 一致性要求确保权威性
- ✅ needs_review机制保留灵活性

### 实战测试
- ✅ 实测是验证质量的唯一方法
- ✅ 日志记录救了项目
- ✅ 需要区分技术失败和知识错误

### 项目管理
- ✅ 保留所有尝试记录很有价值
- ✅ 系统化整理降低理解成本
- ✅ 文档和代码同样重要

---

## 📈 项目统计

- **总开发时间**: 数月
- **代码文件**: 50+ 个脚本
- **生成题目**: 数千道候选
- **验证题目**: 984道通过
- **最终Benchmark**: 145道
- **测试成本**: $62.02
- **Git提交**: 100+ 次

---

**整理时间**: 2025-10-17  
**项目状态**: ✅ 已完成并发布
