#!/usr/bin/env python3
"""
分析API失败（有分数）题目的特征
对比真实错误，判断是否因为答案被截断
"""

import json
import statistics

def load_stats(filepath):
    """加载stats JSON文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_score_distribution(questions, title):
    """分析分数分布"""
    scores = [q['score'] for q in questions]
    
    print(f'\n{title}:')
    print(f'  题目数量: {len(questions)}')
    print(f'  平均分: {statistics.mean(scores):.2f}')
    print(f'  中位数: {statistics.median(scores):.2f}')
    print(f'  最高分: {max(scores)}')
    print(f'  最低分: {min(scores)}')
    if len(scores) > 1:
        print(f'  标准差: {statistics.stdev(scores):.2f}')
    
    # 分数区间分布
    ranges = {
        '0-20': 0,
        '21-40': 0,
        '41-60': 0,
        '61-80': 0,
        '81-99': 0
    }
    for score in scores:
        if score <= 20:
            ranges['0-20'] += 1
        elif score <= 40:
            ranges['21-40'] += 1
        elif score <= 60:
            ranges['41-60'] += 1
        elif score <= 80:
            ranges['61-80'] += 1
        else:
            ranges['81-99'] += 1
    
    print(f'\n  分数区间分布:')
    for range_name, count in ranges.items():
        percentage = count / len(questions) * 100
        print(f'    {range_name}: {count} 题 ({percentage:.1f}%)')
    
    return scores

def analyze_difficulty_topic(questions, title):
    """分析难度和主题分布"""
    difficulties = {}
    topics = {}
    types = {}
    
    for q in questions:
        # 难度
        diff = q.get('difficulty', 'unknown')
        difficulties[diff] = difficulties.get(diff, 0) + 1
        
        # 主题
        topic = q.get('topic', 'unknown')
        topics[topic] = topics.get(topic, 0) + 1
        
        # 类型
        qtype = q.get('type', 'unknown')
        types[qtype] = types.get(qtype, 0) + 1
    
    print(f'\n{title} - 难度分布:')
    for diff in sorted(difficulties.keys()):
        count = difficulties[diff]
        percentage = count / len(questions) * 100
        print(f'  Level {diff}: {count} 题 ({percentage:.1f}%)')
    
    print(f'\n{title} - 类型分布:')
    for qtype, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
        percentage = count / len(questions) * 100
        print(f'  {qtype}: {count} 题 ({percentage:.1f}%)')
    
    print(f'\n{title} - Top 10 主题:')
    for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True)[:10]:
        percentage = count / len(questions) * 100
        print(f'  {topic}: {count} 题 ({percentage:.1f}%)')

def main():
    print('=' * 80)
    print('API失败（有分数）vs 真实错误 - 完整对比分析')
    print('=' * 80)
    
    # 加载数据
    api_failures_stats = load_stats('验证/gpt验证结果分类/3_API失败_有分数/api_failures_with_score_stats.json')
    real_errors_stats = load_stats('验证/gpt验证结果分类/2_真实错误/real_errors_stats.json')
    
    api_questions = api_failures_stats['questions']
    real_questions = real_errors_stats['questions']
    
    print(f'\n📊 基本统计:')
    print(f'  API失败（有分数）: {len(api_questions)} 题')
    print(f'  真实错误: {len(real_questions)} 题')
    
    # 分析分数分布
    print('\n' + '=' * 80)
    print('1️⃣ 分数分布对比')
    print('=' * 80)
    
    api_scores = analyze_score_distribution(api_questions, 'API失败（有分数）')
    real_scores = analyze_score_distribution(real_questions, '真实错误')
    
    # 统计学对比
    print('\n📈 统计学对比:')
    api_mean = statistics.mean(api_scores)
    real_mean = statistics.mean(real_scores)
    diff = abs(api_mean - real_mean)
    print(f'  平均分差异: {diff:.2f} ({api_mean:.2f} vs {real_mean:.2f})')
    
    if api_mean < real_mean:
        print(f'  ⚠️ API失败题目平均分更低，差距 {real_mean - api_mean:.2f} 分')
        print(f'     可能原因：答案被截断导致质量下降')
    else:
        print(f'  ✅ API失败题目平均分相近或更高')
        print(f'     可能原因：仅是API中断，不影响答题质量')
    
    # 分析难度和主题
    print('\n' + '=' * 80)
    print('2️⃣ 难度和主题分布')
    print('=' * 80)
    
    analyze_difficulty_topic(api_questions, 'API失败（有分数）')
    analyze_difficulty_topic(real_questions, '真实错误')
    
    # 显示样本
    print('\n' + '=' * 80)
    print('3️⃣ API失败样本（前5题）')
    print('=' * 80)
    
    for i, q in enumerate(api_questions[:5]):
        print(f'\n  案例 {i+1}:')
        print(f'  ID: {q["question_id"]}')
        print(f'  分数: {q["score"]}')
        print(f'  难度: {q.get("difficulty", "N/A")} | 主题: {q.get("topic", "N/A")} | 类型: {q.get("type", "N/A")}')
        print(f'  题目: {q["question_preview"]}')
    
    print('\n' + '=' * 80)
    print('4️⃣ 真实错误样本（前5题）')
    print('=' * 80)
    
    for i, q in enumerate(real_questions[:5]):
        print(f'\n  案例 {i+1}:')
        print(f'  ID: {q["question_id"]}')
        print(f'  分数: {q["score"]}')
        print(f'  难度: {q.get("difficulty", "N/A")} | 主题: {q.get("topic", "N/A")} | 类型: {q.get("type", "N/A")}')
        print(f'  题目: {q["question_preview"]}')
    
    # 最终结论
    print('\n' + '=' * 80)
    print('📝 结论')
    print('=' * 80)
    
    print('\n基于分数分布分析:')
    if abs(api_mean - real_mean) < 5:
        print('  ✅ 两组平均分非常接近（差异<5分）')
        print('  ✅ 说明：API失败不是因为答案被截断')
        print('  ✅ 可能原因：API中断发生在答题完成后')
        print('  ✅ 建议：这69题可以加入最终benchmark')
    elif api_mean < real_mean - 5:
        print('  ⚠️ API失败组平均分明显更低')
        print('  ⚠️ 说明：可能存在答案截断问题')
        print('  ⚠️ 建议：需要人工复查这些题目')
    else:
        print('  📊 API失败组平均分相近或更高')
        print('  📊 说明：API失败没有显著影响答题质量')
        print('  📊 建议：可以放心使用这些题目')
    
    print('\n' + '=' * 80)
    print('✅ 分析完成！')
    print('=' * 80)

if __name__ == '__main__':
    main()
