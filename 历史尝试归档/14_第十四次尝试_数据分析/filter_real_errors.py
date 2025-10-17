#!/usr/bin/env python3
"""
筛选出GPT-5有合理长度输出但得分很低的题目
排除因为API失败/余额不足导致的空回答
"""
import json
from collections import defaultdict

def main():
    # 加载数据
    with open(r'c:\Users\13031\Desktop\workspace\distillation_generation\验证\gpt5_incorrect_detailed.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    incorrect = data['incorrect_questions_with_details']
    
    print(f"\n{'='*70}")
    print(f"筛选真正的GPT-5错误（排除API失败）")
    print(f"{'='*70}\n")
    
    # 分类
    with_answer = []  # 有合理长度回答的
    without_answer = []  # 无回答记录或回答太短的
    
    MIN_LENGTH = 500  # 定义合理长度阈值（500字符约等于有实质内容）
    
    for q in incorrect:
        answer_length = q['gpt5_result']['answer_length']
        
        if answer_length == 'unknown':
            without_answer.append(q)
        elif isinstance(answer_length, int):
            if answer_length >= MIN_LENGTH:
                with_answer.append(q)
            else:
                without_answer.append(q)
        else:
            without_answer.append(q)
    
    print(f"📊 分类结果:")
    print(f"   有合理长度回答 (≥{MIN_LENGTH}字符): {len(with_answer)} 题")
    print(f"   无回答/回答太短 (<{MIN_LENGTH}字符): {len(without_answer)} 题\n")
    
    print(f"{'='*70}")
    print(f"有合理长度回答但答错的题目 ({len(with_answer)} 题)")
    print(f"{'='*70}\n")
    
    # 按分数排序
    with_answer_sorted = sorted(with_answer, key=lambda x: x['gpt5_result']['score'])
    
    # 按分数段统计
    score_ranges = {
        '0-20': [],
        '21-40': [],
        '41-60': [],
        '61-80': []
    }
    
    for q in with_answer_sorted:
        score = q['gpt5_result']['score']
        if score <= 20:
            score_ranges['0-20'].append(q)
        elif score <= 40:
            score_ranges['21-40'].append(q)
        elif score <= 60:
            score_ranges['41-60'].append(q)
        else:
            score_ranges['61-80'].append(q)
    
    print(f"按分数段分布:")
    for range_name, questions in score_ranges.items():
        if questions:
            print(f"   {range_name}分: {len(questions)} 题")
    print()
    
    # 详细列表
    print(f"{'='*70}")
    print(f"详细列表（按分数从低到高）")
    print(f"{'='*70}\n")
    
    for i, q in enumerate(with_answer_sorted, 1):
        print(f"{i}. [{q['question_id']}] 得分: {q['gpt5_result']['score']}/100")
        print(f"   难度 {q['difficulty']} | {q['topic']} | {q['type']}")
        print(f"   GPT-5回答长度: {q['gpt5_result']['answer_length']} chars")
        print(f"   问题: {q['question_text'][:120]}...")
        print(f"   标准答案: {q['standard_answer'][:120]}...")
        print()
    
    # 统计分析
    print(f"{'='*70}")
    print(f"统计分析")
    print(f"{'='*70}\n")
    
    # 平均回答长度
    avg_length = sum(q['gpt5_result']['answer_length'] for q in with_answer) / len(with_answer)
    print(f"平均回答长度: {avg_length:.0f} 字符\n")
    
    # 按难度统计
    by_difficulty = defaultdict(list)
    for q in with_answer:
        by_difficulty[q['difficulty']].append(q)
    
    print(f"按难度分布:")
    for diff in sorted(by_difficulty.keys()):
        questions = by_difficulty[diff]
        avg_score = sum(q['gpt5_result']['score'] for q in questions) / len(questions)
        print(f"   难度 {diff}: {len(questions)} 题, 平均分 {avg_score:.1f}")
    print()
    
    # 按主题统计
    by_topic = defaultdict(list)
    for q in with_answer:
        by_topic[q['topic']].append(q)
    
    print(f"按主题分布 (Top 10):")
    topic_sorted = sorted(by_topic.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    for topic, questions in topic_sorted:
        avg_score = sum(q['gpt5_result']['score'] for q in questions) / len(questions)
        print(f"   {topic}: {len(questions)} 题, 平均分 {avg_score:.1f}")
    print()
    
    # 找出最差的10题（有回答但得分最低）
    print(f"{'='*70}")
    print(f"🔥 最差的10道题（有实质回答但得分最低）")
    print(f"{'='*70}\n")
    
    worst_10 = with_answer_sorted[:10]
    for i, q in enumerate(worst_10, 1):
        print(f"{i}. [{q['question_id']}] 得分: {q['gpt5_result']['score']}/100")
        print(f"   难度 {q['difficulty']} | {q['topic']} | {q['type']}")
        print(f"   回答长度: {q['gpt5_result']['answer_length']} chars")
        print(f"   问题: {q['question_text'][:100]}...")
        print()
    
    # 保存筛选结果
    output = {
        'summary': {
            'total_incorrect': len(incorrect),
            'with_substantial_answer': len(with_answer),
            'without_answer_or_too_short': len(without_answer),
            'min_length_threshold': MIN_LENGTH,
            'note': '这些题目GPT-5给出了合理长度的回答（≥500字符），但仍被判错。说明是真正的知识错误，而非API失败。'
        },
        'statistics': {
            'average_answer_length': round(avg_length, 0),
            'score_distribution': {
                range_name: len(questions)
                for range_name, questions in score_ranges.items()
                if questions
            },
            'by_difficulty': {
                str(diff): {
                    'count': len(questions),
                    'avg_score': round(sum(q['gpt5_result']['score'] for q in questions) / len(questions), 1)
                }
                for diff, questions in by_difficulty.items()
            },
            'by_topic': {
                topic: {
                    'count': len(questions),
                    'avg_score': round(sum(q['gpt5_result']['score'] for q in questions) / len(questions), 1)
                }
                for topic, questions in topic_sorted
            }
        },
        'questions_with_substantial_answers': [
            {
                'question_id': q['question_id'],
                'score': q['gpt5_result']['score'],
                'answer_length': q['gpt5_result']['answer_length'],
                'difficulty': q['difficulty'],
                'topic': q['topic'],
                'type': q['type'],
                'question_text': q['question_text'],
                'standard_answer': q['standard_answer'],
                'original_text': q.get('original_text', {})
            }
            for q in with_answer_sorted
        ]
    }
    
    output_path = r'c:\Users\13031\Desktop\workspace\distillation_generation\验证\gpt5_real_errors.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"{'='*70}")
    print(f"💾 筛选结果已保存至: {output_path}")
    print(f"{'='*70}\n")
    
    # 对比分析
    print(f"{'='*70}")
    print(f"对比分析: 真实错误 vs API失败")
    print(f"{'='*70}\n")
    
    print(f"📊 真实的GPT-5错误 (有实质回答):")
    print(f"   数量: {len(with_answer)} 题")
    print(f"   占总错误: {len(with_answer)/len(incorrect)*100:.1f}%")
    print(f"   平均回答长度: {avg_length:.0f} 字符")
    print(f"   说明: GPT-5认真回答了，但答错了\n")
    
    print(f"❌ 可能的API失败/空回答:")
    print(f"   数量: {len(without_answer)} 题")
    print(f"   占总错误: {len(without_answer)/len(incorrect)*100:.1f}%")
    print(f"   说明: 可能是余额不足、API失败、或回答被截断\n")
    
    print(f"💡 关键发现:")
    print(f"   1. 有 {len(with_answer)} 题是GPT-5真正答错的")
    print(f"   2. 有 {len(without_answer)} 题可能因技术原因失败")
    print(f"   3. 真实错误率: {len(with_answer)/872*100:.2f}% (基于872题总数)")
    print(f"   4. 如果排除API失败，GPT-5实际正确率可能更高\n")
    
    # 统计无回答题目的分数分布
    without_answer_scores = defaultdict(int)
    for q in without_answer:
        score = q['gpt5_result']['score']
        if score == 0:
            without_answer_scores['0分'] += 1
        elif score <= 40:
            without_answer_scores['1-40分'] += 1
        elif score <= 80:
            without_answer_scores['41-80分'] += 1
    
    print(f"无回答/回答太短的题目分数分布:")
    for range_name, count in sorted(without_answer_scores.items()):
        print(f"   {range_name}: {count} 题")
    print(f"   → 注意: {without_answer_scores.get('0分', 0)} 题得0分，很可能是API失败\n")
    
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
