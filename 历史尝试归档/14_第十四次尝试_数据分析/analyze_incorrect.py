#!/usr/bin/env python3
"""
分析 GPT-5 在 best.json 中答错的题目
"""
import json
from collections import defaultdict

def main():
    # 加载 GPT-5 测试结果
    with open(r'c:\Users\13031\Desktop\workspace\distillation_generation\验证\benchmarkGPT5_recovered.json', 'r', encoding='utf-8') as f:
        gpt5_results = json.load(f)
    
    print(f"\n{'='*70}")
    print(f"GPT-5 答错题目详细分析")
    print(f"{'='*70}\n")
    
    # 统计总体情况
    total = len(gpt5_results)
    correct = sum(1 for r in gpt5_results if r['grading']['correct'])
    incorrect = total - correct
    
    print(f"📊 总体统计:")
    print(f"   总题目数: {total}")
    print(f"   答对: {correct} ({correct/total*100:.2f}%)")
    print(f"   答错: {incorrect} ({incorrect/total*100:.2f}%)\n")
    
    # 提取答错的题目
    incorrect_questions = [r for r in gpt5_results if not r['grading']['correct']]
    
    # 按分数排序（从低到高）
    incorrect_questions.sort(key=lambda x: x['grading']['score'])
    
    print(f"❌ GPT-5 答错的 {len(incorrect_questions)} 道题目:\n")
    print(f"{'='*70}\n")
    
    # 按难度统计
    by_difficulty = defaultdict(list)
    for q in incorrect_questions:
        by_difficulty[q.get('difficulty', 'unknown')].append(q)
    
    print(f"📈 答错题目按难度分布:")
    for diff in sorted(by_difficulty.keys()):
        print(f"   难度 {diff}: {len(by_difficulty[diff])} 题")
    print()
    
    # 按主题统计
    by_topic = defaultdict(list)
    for q in incorrect_questions:
        by_topic[q.get('topic', 'unknown')].append(q)
    
    print(f"📚 答错题目按主题分布 (Top 10):")
    topic_sorted = sorted(by_topic.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    for topic, questions in topic_sorted:
        print(f"   {topic}: {len(questions)} 题")
    print()
    
    # 按类型统计
    by_type = defaultdict(list)
    for q in incorrect_questions:
        by_type[q.get('type', 'unknown')].append(q)
    
    print(f"🔍 答错题目按类型分布:")
    for qtype in sorted(by_type.keys()):
        print(f"   {qtype}: {len(by_type[qtype])} 题")
    print()
    
    # 按分数段统计
    score_ranges = {
        '0-20': [],
        '21-40': [],
        '41-60': [],
        '61-80': []
    }
    for q in incorrect_questions:
        score = q['grading']['score']
        if score <= 20:
            score_ranges['0-20'].append(q)
        elif score <= 40:
            score_ranges['21-40'].append(q)
        elif score <= 60:
            score_ranges['41-60'].append(q)
        else:
            score_ranges['61-80'].append(q)
    
    print(f"📊 答错题目按分数段分布:")
    for range_name, questions in sorted(score_ranges.items()):
        if questions:
            print(f"   {range_name}分: {len(questions)} 题")
    print()
    
    print(f"{'='*70}\n")
    print(f"详细列表（按分数从低到高）:\n")
    
    for i, q in enumerate(incorrect_questions, 1):
        print(f"{i}. [{q['question_id']}] 得分: {q['grading']['score']}/100")
        print(f"   难度: {q.get('difficulty')}, 主题: {q.get('topic')}, 类型: {q.get('type')}")
        print(f"   问题: {q['question_text'][:150]}{'...' if len(q['question_text']) > 150 else ''}")
        print(f"   标准答案: {q['standard_answer'][:150]}{'...' if len(q['standard_answer']) > 150 else ''}")
        print(f"   GPT-5回答长度: {q.get('gpt5_answer_length', 'unknown')} chars")
        
        # 显示原文引用
        if 'original_text' in q and q['original_text']:
            print(f"   原文引用: {len(q['original_text'])} 条")
        
        print()
    
    # 保存详细结果
    output = {
        'summary': {
            'total_tested': total,
            'total_incorrect': incorrect,
            'incorrect_rate': round(incorrect/total*100, 2)
        },
        'by_difficulty': {str(k): len(v) for k, v in by_difficulty.items()},
        'by_topic': {k: len(v) for k, v in sorted(by_topic.items(), key=lambda x: len(x[1]), reverse=True)[:20]},
        'by_type': {k: len(v) for k, v in by_type.items()},
        'by_score_range': {k: len(v) for k, v in score_ranges.items() if v},
        'incorrect_questions': [
            {
                'question_id': q['question_id'],
                'score': q['grading']['score'],
                'difficulty': q.get('difficulty'),
                'topic': q.get('topic'),
                'type': q.get('type'),
                'question_text': q['question_text'],
                'standard_answer': q['standard_answer'],
                'gpt5_answer_length': q.get('gpt5_answer_length', 'unknown'),
                'original_text': q.get('original_text', {})
            }
            for q in incorrect_questions
        ]
    }
    
    output_path = r'c:\Users\13031\Desktop\workspace\distillation_generation\验证\gpt5_incorrect_analysis.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"{'='*70}")
    print(f"💾 详细分析已保存至: {output_path}")
    print(f"{'='*70}\n")
    
    # 找出最差的10道题
    worst_10 = incorrect_questions[:10]
    print(f"\n🔥 得分最低的 10 道题:\n")
    for i, q in enumerate(worst_10, 1):
        print(f"{i}. [{q['question_id']}] 得分: {q['grading']['score']}/100")
        print(f"   难度 {q.get('difficulty')} | {q.get('topic')} | {q.get('type')}")
        print(f"   {q['question_text'][:100]}...\n")

if __name__ == "__main__":
    main()
