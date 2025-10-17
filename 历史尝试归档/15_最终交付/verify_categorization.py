#!/usr/bin/env python3
"""验证分类文件"""
import json
import os

base = r'c:\Users\13031\Desktop\workspace\distillation_generation\验证\gpt验证结果分类'
categories = [
    ('1_答对的题目', 'correct.json', 720),
    ('2_真实错误', 'real_errors.json', 76),
    ('3_API失败_有分数', 'api_failures_with_score.json', 69),
    ('4_API失败_零分', 'api_failures_zero_score.json', 7),
    ('5_未测试', 'untested.json', 112),
]

print("验证分类文件:")
print("=" * 60)

total = 0
for dir_name, file_name, expected in categories:
    file_path = os.path.join(base, dir_name, file_name)
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    actual = len(data)
    status = "✅" if actual == expected else "❌"
    print(f"{status} {dir_name}: {actual} 题 (期望 {expected})")
    total += actual

print("=" * 60)
print(f"总计: {total} 题 (期望 984)")
print("✅ 验证通过！" if total == 984 else "❌ 验证失败！")
