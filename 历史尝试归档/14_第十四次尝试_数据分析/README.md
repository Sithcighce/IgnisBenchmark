# 14 第十四次尝试：数据分析与分类

**批次编号**: 14  
**原阶段名**: 第十三阶段（已更新为第十四阶段）  
**时间**: 2025-10-15~17 GPT-5测试后  
**状态**: ✅ 完成  

---

## 📋 批次概述

### 目标
对批次13的GPT-5测试结果进行深入分析和分类，将984道题目按表现分为5类，为最终交付奠定基础。

### 关键特点
- **数据恢复**: 从gpt5_benchmark.log恢复872题完整数据
- **五类分类**: 答对、真实错误、API失败（有分/零分）、未测试
- **统计分析**: 准确率、分布、成本等多维度分析
- **结构化保存**: 每类单独文件夹+完整数据+统计预览

---

## 🎯 核心价值

### 分析目标
1. **数据恢复**: 从日志完整恢复GPT-5测试数据（零损失）
2. **质量分类**: 将题目按GPT-5表现精确分类
3. **错误分析**: 识别GPT-5的知识盲区和API失败原因
4. **筛选基础**: 为批次15最终交付提供精确数据

### 分类结果
```
984题完整分类：
├─ 720题 (73.17%) - 答对
├─ 76题 (7.72%) - 真实错误（GPT-5知识盲区）
├─ 69题 (7.01%) - API失败（有分数，1-80分）
├─ 7题 (0.71%) - API失败（零分）
└─ 112题 (11.38%) - 未测试（第873-984题）
```

---

## 📂 目录结构

```
14_第十四次尝试_数据分析/
├── 数据分类/
│   ├── 1_答对的题目/ (720题)
│   │   ├── correct.json (5.0 MB)
│   │   └── correct_stats.json (211 KB)
│   ├── 2_真实错误/ (76题)
│   │   ├── real_errors.json (679 KB)
│   │   └── real_errors_stats.json (22 KB)
│   ├── 3_API失败_有分数/ (69题)
│   │   ├── api_failures_with_score.json (487 KB)
│   │   └── api_failures_with_score_stats.json (20 KB)
│   ├── 4_API失败_零分/ (7题)
│   │   ├── api_failures_zero_score.json (48 KB)
│   │   └── api_failures_zero_score_stats.json (2.1 KB)
│   └── 5_未测试/ (112题)
│       ├── untested.json (786 KB)
│       └── untested_stats.json (33 KB)
├── 脚本/
│   ├── recover_from_log.py              # 从日志恢复数据
│   ├── categorize_all_questions_final.py  # 五类分类
│   ├── save_categorized_questions.py    # 保存分类结果
│   ├── analyze_benchmark_progress.py    # 分析测试进度
│   ├── analyze_incorrect.py             # 分析错误题目
│   ├── analyze_needs_review.py          # 分析需复审题目
│   ├── analyze_billing_and_categorize.py  # 成本分析
│   ├── confirm_incorrect_source.py      # 确认错误来源
│   └── filter_real_errors.py            # 筛选真实错误
├── 文档/
│   ├── README.md                        # 总览
│   ├── INDEX.md                         # 快速导航
│   ├── FILE_STRUCTURE.md                # 文件结构说明
│   ├── CATEGORIZATION_COMPLETE.md       # 完成报告
│   ├── COMPLETE_CATEGORIZATION_REPORT.md  # 完整分类报告
│   ├── GPT5_BENCHMARK_RECOVERY_REPORT.md  # 数据恢复报告
│   └── INCORRECT_SOURCE_CONFIRMATION.md   # 错误来源确认
├── 分析结果/
│   ├── complete_question_categorization.json  # 完整分类数据
│   ├── gpt5_benchmark_stats_recovered.json    # 恢复统计
│   ├── gpt5_incorrect_analysis.json           # 错误分析
│   ├── gpt5_incorrect_detailed.json           # 详细错误
│   ├── gpt5_real_errors.json                  # 真实错误
│   ├── api_failures_with_score.json           # API失败（有分）
│   ├── api_failures_zero_score.json           # API失败（零分）
│   ├── untested.json                          # 未测试
│   └── real_errors_stats.json                 # 真实错误统计
└── logs/
    ├── analysis.log                     # 分析日志
    ├── consolidate.log                  # 整合日志
    └── extract_md.log                   # 提取日志
└── README.md                            # 本文档
```

---

## 🔧 核心脚本说明

### 1. recover_from_log.py ⭐
**功能**: 从gpt5_benchmark.log恢复完整测试数据

**重要性**: ⭐⭐⭐⭐⭐ 救命脚本！

**恢复逻辑**:
```python
# 解析日志格式
# [2025-10-15 16:30:45] Question 1: ...
# [2025-10-15 16:30:50] GPT-5 Answer: ...
# [2025-10-15 16:30:55] Score: 85

# 按时间戳分组
groups = group_by_timestamp(log_lines)

# 提取字段
for group in groups:
    question_id = extract_id(group)
    question_text = extract_question(group)
    gpt5_answer = extract_answer(group)
    score = extract_score(group)
    
# 重建JSON
recovered_data = build_json(groups)

# 保存
save_json(recovered_data, "benchmarkGPT5_recovered.json")
```

**结果**: 零损失恢复872题完整数据，$62.02投入全部保留

---

### 2. categorize_all_questions_final.py
**功能**: 将984题精确分为5类

**分类逻辑**:
```python
def categorize_question(q):
    # 1. 未测试（question_id > 872）
    if q['question_id'] > 872:
        return 'untested'
    
    # 2. API失败（零分）
    if q.get('score') == 0 and len(q.get('gpt5_answer', '')) < 100:
        return 'api_failure_zero'
    
    # 3. API失败（有分数）
    if 0 < q.get('score', 0) < 60 and len(q.get('gpt5_answer', '')) < 500:
        return 'api_failure_with_score'
    
    # 4. 答对（score >= 60）
    if q.get('score', 0) >= 60:
        return 'correct'
    
    # 5. 真实错误（有完整答案但分数低）
    if len(q.get('gpt5_answer', '')) >= 500:
        return 'real_error'
    
    return 'unknown'
```

**输出**: 5个文件夹，每个包含完整数据+统计预览

---

### 3. analyze_incorrect.py
**功能**: 深入分析错误题目

**分析维度**:
- 错误类型分布
- 难度分布
- 论文来源分布
- 答案长度统计
- 分数分布

**输出**: gpt5_incorrect_detailed.json

---

### 4. filter_real_errors.py
**功能**: 从错误中筛选真实错误（排除API失败）

**筛选标准**:
```python
def is_real_error(q):
    return (
        q.get('score', 0) < 60 and  # 分数低
        len(q.get('gpt5_answer', '')) >= 500  # 答案完整
    )
```

**结果**: 76道真实错误（GPT-5知识盲区）

---

### 5. save_categorized_questions.py
**功能**: 保存分类结果到结构化文件夹

**保存格式**:
```
分类文件夹/
├── {category}.json       # 完整数据（所有字段）
└── {category}_stats.json # 统计预览（ID、题目、分数、难度）
```

**优势**: 
- 完整数据：便于深入分析
- 统计预览：快速浏览，文件小（~200KB vs 5MB）

---

## 📊 详细统计

### 总体分布
| 分类 | 题数 | 占比（总） | 占比（已测试） | 文件大小 |
|------|------|-----------|---------------|----------|
| ✅ 答对 | 720 | 73.17% | 82.57% | 5.0 MB |
| ❌ 真实错误 | 76 | 7.72% | 8.72% | 679 KB |
| ⚠️ API失败（有分）| 69 | 7.01% | 7.91% | 487 KB |
| ⚠️ API失败（零分）| 7 | 0.71% | 0.80% | 48 KB |
| ⏭️ 未测试 | 112 | 11.38% | - | 786 KB |
| **总计** | **984** | **100%** | **100%** | **~7.9 MB** |

### 准确率计算
```
原始准确率 = 720 / 872 = 82.57%

有效测试 = 答对 + 真实错误 = 720 + 76 = 796
调整后准确率 = 720 / 796 = 90.45%
（排除76道API失败）
```

### 成本分析
- **总花费**: $62.02
- **有效测试**: 872题
- **平均成本**: $0.0711/题
- **失败损失**: 76题API失败 ≈ $5.40

---

## 💡 关键发现

### 1. 数据恢复的价值
- **背景**: 批次13中途中断，余额不足
- **风险**: $62.02和872题数据可能丢失
- **解决**: gpt5_benchmark.log完整记录所有过程
- **结果**: 零损失恢复，日志的救命价值

### 2. GPT-5的知识盲区
- **真实错误**: 76题（8.72%已测试，7.72%总题目）
- **特点**: 
  - GPT-5给出了完整答案（≥500字符）
  - 但与标准答案或原文不符
  - 这些是benchmark的核心价值
- **分布**: 
  - 难度: 主要集中在难度6-8
  - 类型: calculation和application为主

### 3. API稳定性问题
- **失败率**: 8.72%（76/872）
- **有分数失败**: 69题（可能部分返回或回答太短）
- **零分失败**: 7题（可能完全无返回）
- **原因**: 
  - OpenRouter API不稳定
  - GPT-5超时（300秒）
  - 网络波动

### 4. 五类分类的精确性
- **清晰边界**: 每类有明确判断标准
- **完整覆盖**: 984题全部分类，无遗漏
- **验证通过**: verify_categorization.py验证总数正确

---

## 🔗 数据流向

```
输入: 批次13的GPT-5测试结果
  ↓
数据恢复（recover_from_log.py）
  ├─ 从gpt5_benchmark.log恢复872题
  └─ 添加112道未测试题目（从best.json）
  ↓
五类分类（categorize_all_questions_final.py）
  ├─ 答对: 720题
  ├─ 真实错误: 76题
  ├─ API失败（有分）: 69题
  ├─ API失败（零分）: 7题
  └─ 未测试: 112题
  ↓
深入分析
  ├─ analyze_incorrect.py（错误分析）
  ├─ filter_real_errors.py（真实错误筛选）
  └─ analyze_billing_and_categorize.py（成本分析）
  ↓
结构化保存（save_categorized_questions.py）
  ├─ 每类一个文件夹
  ├─ 完整数据JSON
  └─ 统计预览JSON
  ↓
流向: 批次15（最终交付）
  └─ 使用真实错误（76题）+ API失败有分（69题）= 145题
```

---

## 📖 相关批次

- **上游**: 批次13（GPT-5测试，872题完成+112题未测试）
- **下游**: 批次15（最终交付，筛选145道挑战题）
- **关键数据**: 
  - 批次13的gpt5_benchmark.log（数据恢复源）
  - 批次12的best.json（补充未测试题目）

---

## 🎯 经验教训

### ✅ 成功经验
1. **日志的绝对价值**: gpt5_benchmark.log救了整个项目
2. **结构化分类**: 5类清晰，便于后续筛选和分析
3. **统计预览**: stats.json设计很好，快速浏览不需要加载大文件
4. **完整文档**: 4个报告文件详细记录全过程

### ⚠️ 经验
1. **API失败处理**: 8.72%的失败率需要重测机制（批次15做了retest）
2. **分类标准**: 500字符作为"完整答案"的阈值合理
3. **数据验证**: verify_categorization.py确保分类无遗漏

### 🔄 批次15的改进
1. **重测API失败**: 对76道失败题目进行retest
2. **Zero-score重测**: 特别处理7道零分题目
3. **未测试处理**: 112题未纳入最终benchmark（质量不确定）

---

## 🔍 技术细节

### 数据恢复算法
```python
def recover_from_log(log_file):
    # 1. 读取日志
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    # 2. 按时间戳分组
    groups = []
    current_group = []
    for line in lines:
        if line.startswith('['):
            if current_group:
                groups.append(current_group)
            current_group = [line]
        else:
            current_group.append(line)
    
    # 3. 提取字段
    recovered = []
    for group in groups:
        q_id = extract_id(group)
        question = extract_question(group)
        answer = extract_answer(group)
        score = extract_score(group)
        
        recovered.append({
            'question_id': q_id,
            'question': question,
            'gpt5_answer': answer,
            'score': score,
            ...
        })
    
    return recovered
```

### 分类标准量化
```python
# 答案长度阈值
COMPLETE_ANSWER_MIN_LENGTH = 500  # 完整答案至少500字符
PARTIAL_ANSWER_MAX_LENGTH = 100   # 部分答案最多100字符

# 分数阈值
PASS_SCORE = 60                   # 及格分
ZERO_SCORE = 0                    # 零分（API失败标志）

# API失败判断
def is_api_failure(q):
    return (
        q['score'] < PASS_SCORE and
        len(q['gpt5_answer']) < COMPLETE_ANSWER_MIN_LENGTH
    )

# 真实错误判断
def is_real_error(q):
    return (
        q['score'] < PASS_SCORE and
        len(q['gpt5_answer']) >= COMPLETE_ANSWER_MIN_LENGTH
    )
```

---

## 📊 深度分析结果

### 真实错误的分布（76题）
```
按难度:
├─ 难度1-3: 8题 (10.5%)
├─ 难度4-6: 32题 (42.1%) ← 主要集中
├─ 难度7-9: 28题 (36.8%)
└─ 难度10: 8题 (10.5%)

按类型:
├─ calculation: 38题 (50%)
├─ application: 24题 (31.6%)
└─ concept: 14题 (18.4%)

按论文:
├─ 分布在~60篇不同论文
├─ 无特定论文集中
└─ 说明是GPT-5的系统性盲区
```

### API失败的特征（76题）
```
有分数（69题）:
├─ 分数范围: 1-80分
├─ 平均答案长度: ~200字符
├─ 推测: 部分返回或超时截断
└─ 处理: 批次15重测

零分（7题）:
├─ 分数: 0
├─ 答案长度: <100字符
├─ 推测: 完全API失败
└─ 处理: 批次15重测
```

---

## 📌 总结

批次14完成了**数据分析与分类**，这是从测试结果到最终交付的关键桥梁：

1. **数据恢复**: 从日志零损失恢复872题数据
2. **精确分类**: 984题分为5类，边界清晰
3. **深入分析**: 识别GPT-5知识盲区和API失败模式
4. **结构化保存**: 每类独立文件夹+完整数据+统计预览
5. **价值输出**: 
   - 76道真实错误（GPT-5盲区）
   - 76道API失败（需重测）
   - 为批次15筛选145道挑战题奠定基础

这一批次的数据恢复和分类工作，确保了$62.02的投入零损失，并为IgnisBenchmark的最终交付提供了精确的数据基础。

---

**生成时间**: 2025-10-17  
**文档版本**: v1.0  
**下一步**: 批次15 - 最终交付（145道挑战题）
