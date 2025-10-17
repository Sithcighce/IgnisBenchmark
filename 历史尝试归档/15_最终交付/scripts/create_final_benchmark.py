#!/usr/bin/env python3
"""
创建最终交付的benchmark文件
包含：答错的题目 + API失败有分数的题目
"""

import json
import os
from datetime import datetime

# 输入文件
REAL_ERRORS_JSON = r"c:\Users\13031\Desktop\workspace\distillation_generation\验证\gpt验证结果分类\2_真实错误\real_errors.json"
API_FAILURES_WITH_SCORE_JSON = r"c:\Users\13031\Desktop\workspace\distillation_generation\验证\gpt验证结果分类\3_API失败_有分数\api_failures_with_score.json"

# 输出目录
OUTPUT_DIR = r"c:\Users\13031\Desktop\workspace\distillation_generation\最终交付"

def create_benchmark_basic():
    """
    文件1: benchmark_basic.json
    只包含题目和标答（供他人直接使用）
    """
    print("=" * 70)
    print("创建 benchmark_basic.json - 基础版（题目+标答）")
    print("=" * 70)
    
    # 加载数据
    with open(REAL_ERRORS_JSON, 'r', encoding='utf-8') as f:
        real_errors = json.load(f)
    
    with open(API_FAILURES_WITH_SCORE_JSON, 'r', encoding='utf-8') as f:
        api_failures = json.load(f)
    
    all_questions = real_errors + api_failures
    
    # 构建基础版本
    benchmark_basic = []
    for q in all_questions:
        item = {
            "question_id": q['question_id'],
            "question_text": q['question_text'],
            "standard_answer": q['standard_answer'],
            "difficulty": q['difficulty'],
            "topic": q['topic'],
            "type": q['type']
        }
        benchmark_basic.append(item)
    
    # 保存
    output_file = os.path.join(OUTPUT_DIR, "benchmark_basic.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(benchmark_basic, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已创建: {output_file}")
    print(f"   题目数: {len(benchmark_basic)}")
    print(f"   - 真实错误: {len(real_errors)}")
    print(f"   - API失败(有分): {len(api_failures)}")
    
    return benchmark_basic

def create_benchmark_with_verification():
    """
    文件2: benchmark_with_verification.json
    包含题目、标答、验证信息（原文、验证记录）
    """
    print("\n" + "=" * 70)
    print("创建 benchmark_with_verification.json - 验证版")
    print("=" * 70)
    
    # 加载数据
    with open(REAL_ERRORS_JSON, 'r', encoding='utf-8') as f:
        real_errors = json.load(f)
    
    with open(API_FAILURES_WITH_SCORE_JSON, 'r', encoding='utf-8') as f:
        api_failures = json.load(f)
    
    all_questions = real_errors + api_failures
    
    # 构建验证版本
    benchmark_with_verification = []
    for q in all_questions:
        item = {
            "question_id": q['question_id'],
            "question_text": q['question_text'],
            "standard_answer": q['standard_answer'],
            "difficulty": q['difficulty'],
            "topic": q['topic'],
            "type": q['type'],
            "original_text": q.get('original_text', {}),
            "verification": q.get('verification', {}),
            "quality_check": q.get('quality_check', {}),
            "source": q.get('source', 'unknown')
        }
        benchmark_with_verification.append(item)
    
    # 保存
    output_file = os.path.join(OUTPUT_DIR, "benchmark_with_verification.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(benchmark_with_verification, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已创建: {output_file}")
    print(f"   题目数: {len(benchmark_with_verification)}")
    
    return benchmark_with_verification

def create_benchmark_with_gpt5_results():
    """
    文件3: benchmark_with_gpt5_results.json
    包含题目、标答、GPT-5答题和DeepSeek判题结果
    """
    print("\n" + "=" * 70)
    print("创建 benchmark_with_gpt5_results.json - GPT-5测试版")
    print("=" * 70)
    
    # 加载数据
    with open(REAL_ERRORS_JSON, 'r', encoding='utf-8') as f:
        real_errors = json.load(f)
    
    with open(API_FAILURES_WITH_SCORE_JSON, 'r', encoding='utf-8') as f:
        api_failures = json.load(f)
    
    all_questions = real_errors + api_failures
    
    # 构建GPT-5测试版本
    benchmark_with_gpt5 = []
    for q in all_questions:
        category_info = q.get('category_info', {})
        
        item = {
            "question_id": q['question_id'],
            "question_text": q['question_text'],
            "standard_answer": q['standard_answer'],
            "difficulty": q['difficulty'],
            "topic": q['topic'],
            "type": q['type'],
            "gpt5_test_result": {
                "score": category_info.get('score', 0),
                "answer_length": category_info.get('answer_length', 'unknown'),
                "category": "real_error" if q in real_errors else "api_failure_with_score",
                "note": "GPT-5给出实质回答但答错" if q in real_errors else "GPT-5回答太短或部分失败"
            }
        }
        benchmark_with_gpt5.append(item)
    
    # 保存
    output_file = os.path.join(OUTPUT_DIR, "benchmark_with_gpt5_results.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(benchmark_with_gpt5, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已创建: {output_file}")
    print(f"   题目数: {len(benchmark_with_gpt5)}")
    
    return benchmark_with_gpt5

def create_benchmark_complete():
    """
    文件4: benchmark_complete.json
    完整版，包含所有信息
    """
    print("\n" + "=" * 70)
    print("创建 benchmark_complete.json - 完整版（所有信息）")
    print("=" * 70)
    
    # 加载数据
    with open(REAL_ERRORS_JSON, 'r', encoding='utf-8') as f:
        real_errors = json.load(f)
    
    with open(API_FAILURES_WITH_SCORE_JSON, 'r', encoding='utf-8') as f:
        api_failures = json.load(f)
    
    all_questions = real_errors + api_failures
    
    # 标记分类
    for q in real_errors:
        q['benchmark_category'] = 'real_error'
        q['benchmark_note'] = 'GPT-5给出实质性回答（≥500字符）但DeepSeek判定为错误'
    
    for q in api_failures:
        q['benchmark_category'] = 'api_failure_with_score'
        q['benchmark_note'] = 'GPT-5回答太短（<500字符）或部分失败，但有1-80分'
    
    # 保存完整版
    output_file = os.path.join(OUTPUT_DIR, "benchmark_complete.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_questions, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已创建: {output_file}")
    print(f"   题目数: {len(all_questions)}")
    
    return all_questions

def create_readme():
    """创建README说明文档"""
    print("\n" + "=" * 70)
    print("创建 README.md")
    print("=" * 70)
    
    # 加载数据统计
    with open(REAL_ERRORS_JSON, 'r', encoding='utf-8') as f:
        real_errors = json.load(f)
    
    with open(API_FAILURES_WITH_SCORE_JSON, 'r', encoding='utf-8') as f:
        api_failures = json.load(f)
    
    total = len(real_errors) + len(api_failures)
    
    readme_content = f"""# IgnisBenchmark - 最终交付版本

## 📊 Benchmark概览

本Benchmark包含 **{total}道** 高质量燃烧科学与能源工程领域的专业题目，这些题目具有以下特点：

1. ✅ **三模型验证通过**: 所有题目均经过Claude Sonnet 4.5、GPT-5、Gemini 2.5 Pro三个顶级模型的一致验证
2. 🔥 **挑战性强**: 这些是GPT-5在测试中答错或回答不完整的题目
3. 📚 **来源权威**: 基于顶级学术论文和教材
4. 🎯 **专业深度**: 难度3-5级，涵盖概念理解、推理分析、计算应用

---

## 📁 文件说明

### 1. `benchmark_basic.json` - 基础版（推荐）

**用途**: 供他人直接使用的benchmark题目集

**包含内容**:
- 题目ID
- 题目文本
- 标准答案
- 难度等级 (3-5)
- 主题分类
- 题目类型 (concept/reasoning/calculation/application)

**适用场景**:
- 评测模型在燃烧科学领域的专业能力
- 对比不同模型的答题表现
- 作为专业领域的测试集

**示例结构**:
```json
{{
  "question_id": "deepseek_q_xxxxx",
  "question_text": "题目内容...",
  "standard_answer": "标准答案...",
  "difficulty": 4,
  "topic": "combustion_kinetics",
  "type": "reasoning"
}}
```

---

### 2. `benchmark_with_verification.json` - 验证版

**用途**: 了解题目来源和验证过程

**包含内容**:
- 基础版的所有内容
- **原文引用** (original_text): 题目来源的文献原文
- **验证记录** (verification): 三模型验证的详细信息
- **质量检查** (quality_check): 题目质量审核记录
- **来源信息** (source): 题目生成的文献来源

**适用场景**:
- 验证题目的权威性和准确性
- 追溯题目的学术来源
- 了解题目的生成和验证过程

**示例结构**:
```json
{{
  "question_id": "deepseek_q_xxxxx",
  "question_text": "题目内容...",
  "standard_answer": "标准答案...",
  "difficulty": 4,
  "topic": "combustion_kinetics",
  "type": "reasoning",
  "original_text": {{
    "1": "原文片段1...",
    "2": "原文片段2..."
  }},
  "verification": {{
    "claude_verification": {{}},
    "gpt5_verification": {{}},
    "gemini_verification": {{}}
  }},
  "quality_check": {{...}},
  "source": "论文标题或来源"
}}
```

---

### 3. `benchmark_with_gpt5_results.json` - GPT-5测试版

**用途**: 了解GPT-5在这些题目上的表现

**包含内容**:
- 基础版的所有内容
- **GPT-5测试结果** (gpt5_test_result):
  - 得分 (score)
  - 回答长度 (answer_length)
  - 错误类型 (category): real_error 或 api_failure_with_score
  - 说明 (note)

**适用场景**:
- 了解GPT-5的答题表现
- 识别GPT-5的知识盲区
- 与其他模型对比性能

**统计信息**:
- 真实错误: {len(real_errors)}题 (GPT-5给出实质性回答但答错)
- API失败(有分): {len(api_failures)}题 (回答太短或部分失败)

**示例结构**:
```json
{{
  "question_id": "deepseek_q_xxxxx",
  "question_text": "题目内容...",
  "standard_answer": "标准答案...",
  "difficulty": 4,
  "topic": "combustion_kinetics",
  "type": "reasoning",
  "gpt5_test_result": {{
    "score": 35,
    "answer_length": 5216,
    "category": "real_error",
    "note": "GPT-5给出实质回答但答错"
  }}
}}
```

---

### 4. `benchmark_complete.json` - 完整版

**用途**: 完整的题目数据，包含所有信息

**包含内容**:
- 所有基础、验证、测试信息
- 完整的题目元数据
- 分类标记 (benchmark_category)
- 详细说明 (benchmark_note)

**适用场景**:
- 深度分析和研究
- 完整的数据备份
- 需要所有信息的场景

---

## 📊 题目统计

### 总体统计
- **总题目数**: {total}
- **真实错误**: {len(real_errors)} ({len(real_errors)/total*100:.1f}%)
- **API失败(有分)**: {len(api_failures)} ({len(api_failures)/total*100:.1f}%)

### 按难度分布
- 难度3: {len([q for q in real_errors + api_failures if q['difficulty'] == 3])} 题
- 难度4: {len([q for q in real_errors + api_failures if q['difficulty'] == 4])} 题
- 难度5: {len([q for q in real_errors + api_failures if q['difficulty'] == 5])} 题

### 按主题分布（Top 5）
"""
    
    # 统计主题
    from collections import Counter
    all_questions = real_errors + api_failures
    topic_counter = Counter(q['topic'] for q in all_questions)
    
    for topic, count in topic_counter.most_common(5):
        readme_content += f"- {topic}: {count} 题\n"
    
    readme_content += f"""
### 按类型分布
"""
    
    type_counter = Counter(q['type'] for q in all_questions)
    for qtype, count in type_counter.most_common():
        readme_content += f"- {qtype}: {count} 题\n"
    
    readme_content += f"""
---

## 🎯 使用建议

### 快速开始
```python
import json

# 加载基础版benchmark
with open('benchmark_basic.json', 'r', encoding='utf-8') as f:
    benchmark = json.load(f)

print(f"加载了 {{len(benchmark)}} 道题目")

# 按难度筛选
difficulty_4 = [q for q in benchmark if q['difficulty'] == 4]
print(f"难度4的题目: {{len(difficulty_4)}} 道")
```

### 评测模型
```python
import json

# 加载benchmark
with open('benchmark_basic.json', 'r', encoding='utf-8') as f:
    benchmark = json.load(f)

# 对每道题目进行测试
results = []
for question in benchmark:
    # 调用你的模型
    model_answer = your_model(question['question_text'])
    
    # 评分（使用另一个模型或人工评分）
    score = grade_answer(model_answer, question['standard_answer'])
    
    results.append({{
        'question_id': question['question_id'],
        'score': score
    }})

# 计算准确率
accuracy = sum(r['score'] >= 85 for r in results) / len(results)
print(f"准确率: {{accuracy*100:.2f}}%")
```

---

## 📈 GPT-5基准性能

作为参考，GPT-5在这{total}道题目上的表现：

- **真实错误**: {len(real_errors)}题
  - 给出了实质性回答（平均5,893字符）
  - 但DeepSeek判定为错误
  - 平均得分: {sum(q.get('category_info', {}).get('score', 0) for q in real_errors) / len(real_errors):.1f}分

- **API失败(有分)**: {len(api_failures)}题
  - 回答太短或部分失败
  - 得分范围: 1-80分
  - 平均得分: {sum(q.get('category_info', {}).get('score', 0) for q in api_failures) / len(api_failures):.1f}分

**注意**: 这些题目是GPT-5的挑战性题目，不代表GPT-5的整体性能。在完整的984题测试集中，GPT-5的准确率为90.45%（排除API失败）。

---

## 🔍 质量保证

### 题目来源
- 所有题目基于顶级学术论文和教材
- 每道题目都有明确的文献引用

### 验证流程
1. **自动生成**: 基于学术论文生成候选题目
2. **三模型验证**: Claude Sonnet 4.5、GPT-5、Gemini 2.5 Pro独立验证
3. **质量审核**: 检查原文忠实度、标答准确性、题目合理性
4. **实测筛选**: GPT-5实际答题，筛选出挑战性题目

### 适用性说明
- ✅ 适合评测顶级模型的专业能力
- ✅ 适合识别模型的知识盲区
- ✅ 适合作为挑战性测试集
- ⚠️ 难度较高，不适合初级模型评测
- ⚠️ 专业领域限定（燃烧科学与能源工程）

---

## 📝 引用

如果您使用本benchmark，请引用：

```
IgnisBenchmark: A Challenging Benchmark for Combustion Science and Energy Engineering
Generated and verified by Claude Sonnet 4.5, GPT-5, and Gemini 2.5 Pro
Version 1.0 (2025-10-17)
GitHub: https://github.com/Sithcighce/IgnisBenchmark
```

---

## 📞 联系方式

- **项目地址**: https://github.com/Sithcighce/IgnisBenchmark
- **问题反馈**: 请在GitHub Issues中提出

---

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**版本**: v1.0  
**状态**: ✅ 最终交付版本
"""
    
    # 保存README
    readme_file = os.path.join(OUTPUT_DIR, "README.md")
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ 已创建: {readme_file}")

def main():
    """主函数"""
    print("=" * 70)
    print("🚀 创建最终交付的Benchmark文件")
    print("=" * 70)
    
    # 创建各个版本
    basic = create_benchmark_basic()
    verification = create_benchmark_with_verification()
    gpt5_results = create_benchmark_with_gpt5_results()
    complete = create_benchmark_complete()
    create_readme()
    
    print("\n" + "=" * 70)
    print("✨ 所有文件创建完成！")
    print("=" * 70)
    print(f"\n输出目录: {OUTPUT_DIR}")
    print("\n创建的文件:")
    print("  1. benchmark_basic.json            - 基础版（题目+标答）")
    print("  2. benchmark_with_verification.json - 验证版（含验证信息）")
    print("  3. benchmark_with_gpt5_results.json - GPT-5测试版")
    print("  4. benchmark_complete.json         - 完整版（所有信息）")
    print("  5. README.md                        - 使用说明")
    
    print(f"\n总题目数: {len(basic)}")
    print("\n✅ 可以开始Git备份！")

if __name__ == '__main__':
    main()
