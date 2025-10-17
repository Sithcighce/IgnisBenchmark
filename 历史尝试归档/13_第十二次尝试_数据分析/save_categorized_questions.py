#!/usr/bin/env python3
"""
将所有题目按分类保存到对应的文件夹中
"""

import json
import os
from pathlib import Path

# 文件路径
CATEGORIZATION_JSON = r"c:\Users\13031\Desktop\workspace\distillation_generation\验证\complete_question_categorization.json"
BEST_JSON = r"c:\Users\13031\Desktop\workspace\distillation_generation\验证\best.json"
OUTPUT_DIR = r"c:\Users\13031\Desktop\workspace\distillation_generation\验证\gpt验证结果分类"

def load_data():
    """加载分类数据和完整题目"""
    with open(CATEGORIZATION_JSON, 'r', encoding='utf-8') as f:
        categorization = json.load(f)
    
    with open(BEST_JSON, 'r', encoding='utf-8') as f:
        all_questions = json.load(f)
    
    # 创建题目ID到完整题目的映射
    question_map = {q['question_id']: q for q in all_questions}
    
    return categorization, question_map

def save_category(category_name, questions, question_map, output_path):
    """保存一个分类的题目"""
    full_questions = []
    
    for item in questions:
        qid = item['question_id']
        if qid in question_map:
            # 获取完整题目
            full_q = question_map[qid].copy()
            # 添加分类信息
            full_q['category_info'] = item
            full_questions.append(full_q)
    
    # 保存到文件
    output_file = os.path.join(output_path, f"{category_name}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(full_questions, f, ensure_ascii=False, indent=2)
    
    # 同时保存一个统计文件
    stats = {
        'category': category_name,
        'total_count': len(full_questions),
        'questions': [
            {
                'question_id': q['question_id'],
                'difficulty': q['difficulty'],
                'topic': q['topic'],
                'type': q['type'],
                'score': q.get('category_info', {}).get('score', 'N/A'),
                'question_preview': q['question_text'][:100] + '...'
            }
            for q in full_questions
        ]
    }
    
    stats_file = os.path.join(output_path, f"{category_name}_stats.json")
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    return len(full_questions)

def categorize_and_save():
    """分类并保存所有题目"""
    print("=" * 70)
    print("📂 分类保存题目到文件夹")
    print("=" * 70)
    
    categorization, question_map = load_data()
    categories = categorization['categories']
    
    # 1. 答对的题目
    dir_correct = os.path.join(OUTPUT_DIR, "1_答对的题目")
    count = save_category("correct", categories['correct'], question_map, dir_correct)
    print(f"\n✅ 答对的题目: {count} 题")
    print(f"   保存到: {dir_correct}")
    
    # 2. 真实错误
    dir_real_errors = os.path.join(OUTPUT_DIR, "2_真实错误")
    count = save_category("real_errors", categories['real_errors'], question_map, dir_real_errors)
    print(f"\n❌ 真实错误（有实质回答但答错）: {count} 题")
    print(f"   保存到: {dir_real_errors}")
    
    # 3. API失败 - 有分数
    api_failures_with_score = [q for q in categories['api_failures'] if q.get('score', 0) > 0]
    dir_api_with_score = os.path.join(OUTPUT_DIR, "3_API失败_有分数")
    count = save_category("api_failures_with_score", api_failures_with_score, question_map, dir_api_with_score)
    print(f"\n⚠️  API失败（有分数）: {count} 题")
    print(f"   保存到: {dir_api_with_score}")
    
    # 4. API失败 - 零分
    api_failures_zero_score = [q for q in categories['api_failures'] if q.get('score', 0) == 0]
    dir_api_zero = os.path.join(OUTPUT_DIR, "4_API失败_零分")
    count = save_category("api_failures_zero_score", api_failures_zero_score, question_map, dir_api_zero)
    print(f"\n⚠️  API失败（零分）: {count} 题")
    print(f"   保存到: {dir_api_zero}")
    
    # 5. 未测试
    dir_untested = os.path.join(OUTPUT_DIR, "5_未测试")
    count = save_category("untested", categories['untested'], question_map, dir_untested)
    print(f"\n⏭️  未测试: {count} 题")
    print(f"   保存到: {dir_untested}")
    
    # 创建总览README
    readme_content = f"""# GPT-5验证结果分类

## 📊 分类统计

### 1. ✅ 答对的题目 ({len(categories['correct'])} 题)
- **占比**: {len(categories['correct'])/984*100:.2f}% (总题目)
- **准确率**: {len(categories['correct'])/872*100:.2f}% (已测试)
- **说明**: GPT-5正确回答的题目

### 2. ❌ 真实错误 ({len(categories['real_errors'])} 题)
- **占比**: {len(categories['real_errors'])/872*100:.2f}% (已测试)
- **说明**: GPT-5给出实质性回答（≥500字符），但DeepSeek判定为错误
- **特点**: 这些是GPT-5真正的知识盲区

### 3. ⚠️ API失败（有分数） ({len(api_failures_with_score)} 题)
- **占比**: {len(api_failures_with_score)/872*100:.2f}% (已测试)
- **分数范围**: 1-80分
- **说明**: 可能是部分返回或回答太短（<500字符）

### 4. ⚠️ API失败（零分） ({len(api_failures_zero_score)} 题)
- **占比**: {len(api_failures_zero_score)/872*100:.2f}% (已测试)
- **说明**: 很可能是完全API失败，无返回数据

### 5. ⏭️ 未测试 ({len(categories['untested'])} 题)
- **占比**: {len(categories['untested'])/984*100:.2f}% (总题目)
- **说明**: 脚本中断前未测试的题目（第873-984题）

---

## 📁 文件说明

每个分类文件夹包含：
- `[category_name].json` - 完整题目数据
- `[category_name]_stats.json` - 统计和预览信息

---

## 🎯 关键数据

- **调整后准确率**: 90.45% (720 / 796有效测试)
- **真实错误率**: 9.55% (76 / 796有效测试)
- **API失败率**: 8.72% (76 / 872已测试)

---

生成时间: 2025-10-17
"""
    
    readme_file = os.path.join(OUTPUT_DIR, "README.md")
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"\n" + "=" * 70)
    print(f"📝 总览文件已创建: {readme_file}")
    print("=" * 70)
    
    print(f"\n✨ 所有题目已成功分类保存！")
    print(f"\n分类目录: {OUTPUT_DIR}")
    print(f"\n每个文件夹包含:")
    print(f"  - [分类名].json (完整题目)")
    print(f"  - [分类名]_stats.json (统计信息)")
    
    # 验证总数
    total = (len(categories['correct']) + len(categories['real_errors']) + 
             len(categories['api_failures']) + len(categories['untested']))
    print(f"\n验证: 总题目数 = {total} (应为984)")

if __name__ == '__main__':
    categorize_and_save()
