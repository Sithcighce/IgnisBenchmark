#!/usr/bin/env python3
"""
分析 needs_review 题目的 GPT-5 表现
"""
import json

def main():
    # 加载文件
    with open(r'c:\Users\13031\Desktop\workspace\distillation_generation\验证\notpass.json', 'r', encoding='utf-8') as f:
        notpass = json.load(f)
    
    with open(r'c:\Users\13031\Desktop\workspace\distillation_generation\验证\benchmarkGPT5_recovered.json', 'r', encoding='utf-8') as f:
        gpt5_results = json.load(f)
    
    # 创建 GPT-5 结果的映射
    gpt5_map = {r['question_id']: r for r in gpt5_results}
    
    print(f"\n{'='*70}")
    print(f"Needs Review 题目分析")
    print(f"{'='*70}\n")
    
    # 统计 notpass 中的状态
    status_counts = {}
    for q in notpass:
        status = q.get('verification', {}).get('status', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print(f"📊 notpass.json 状态分布:")
    for status, count in sorted(status_counts.items()):
        print(f"   {status}: {count}")
    
    # 提取 needs_review 题目
    needs_review = [q for q in notpass if q.get('verification', {}).get('status') == 'needs_review']
    
    print(f"\n⚠️  Needs Review 题目总数: {len(needs_review)}\n")
    
    # 检查有多少 needs_review 题目在 GPT-5 测试中
    tested = []
    not_tested = []
    
    for q in needs_review:
        qid = q['question_id']
        if qid in gpt5_map:
            tested.append({
                'question_id': qid,
                'question_text': q['question_text'][:100] + '...' if len(q['question_text']) > 100 else q['question_text'],
                'difficulty': q.get('difficulty'),
                'topic': q.get('topic'),
                'type': q.get('type'),
                'verification_reasons': [v.get('reasoning', '')[:150] for v in q.get('verification', {}).get('verifiers', [])],
                'gpt5_correct': gpt5_map[qid]['grading']['correct'],
                'gpt5_score': gpt5_map[qid]['grading']['score']
            })
        else:
            not_tested.append(qid)
    
    print(f"✅ 在 GPT-5 测试中: {len(tested)}")
    print(f"❌ 未测试（余额不足前未完成）: {len(not_tested)}\n")
    
    if tested:
        # 统计 GPT-5 在 needs_review 题目上的表现
        correct_count = sum(1 for t in tested if t['gpt5_correct'])
        accuracy = correct_count / len(tested) * 100
        avg_score = sum(t['gpt5_score'] for t in tested) / len(tested)
        
        print(f"🎯 GPT-5 在 Needs Review 题目上的表现:")
        print(f"   正确率: {accuracy:.2f}% ({correct_count}/{len(tested)})")
        print(f"   平均分: {avg_score:.2f}/100\n")
        
        # 按难度分析
        by_difficulty = {}
        for t in tested:
            diff = t['difficulty']
            if diff not in by_difficulty:
                by_difficulty[diff] = {'total': 0, 'correct': 0, 'scores': []}
            by_difficulty[diff]['total'] += 1
            if t['gpt5_correct']:
                by_difficulty[diff]['correct'] += 1
            by_difficulty[diff]['scores'].append(t['gpt5_score'])
        
        print(f"📈 按难度分析:")
        for diff in sorted(by_difficulty.keys()):
            data = by_difficulty[diff]
            acc = data['correct'] / data['total'] * 100
            avg = sum(data['scores']) / len(data['scores'])
            print(f"   难度 {diff}: {acc:.2f}% ({data['correct']}/{data['total']}) - 平均分: {avg:.2f}")
        
        # 显示答错的题目
        incorrect = [t for t in tested if not t['gpt5_correct']]
        if incorrect:
            print(f"\n❌ GPT-5 答错的 Needs Review 题目 ({len(incorrect)} 题):\n")
            for i, t in enumerate(incorrect, 1):
                print(f"{i}. [{t['question_id']}] (难度:{t['difficulty']}, 分数:{t['gpt5_score']})")
                print(f"   主题: {t['topic']}, 类型: {t['type']}")
                print(f"   问题: {t['question_text']}")
                print(f"   验证问题: {t['verification_reasons'][0][:100] if t['verification_reasons'] else 'N/A'}...\n")
        
        # 显示答对的题目
        correct = [t for t in tested if t['gpt5_correct']]
        if correct:
            print(f"\n✅ GPT-5 答对的 Needs Review 题目 ({len(correct)} 题):\n")
            for i, t in enumerate(correct[:10], 1):  # 只显示前10个
                print(f"{i}. [{t['question_id']}] (难度:{t['difficulty']}, 分数:{t['gpt5_score']})")
                print(f"   主题: {t['topic']}, 类型: {t['type']}")
                print(f"   问题: {t['question_text']}\n")
            if len(correct) > 10:
                print(f"   ... 还有 {len(correct) - 10} 题\n")
        
        # 保存详细结果
        output_path = r'c:\Users\13031\Desktop\workspace\distillation_generation\验证\gpt5_needs_review_analysis.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': {
                    'total_needs_review': len(needs_review),
                    'tested': len(tested),
                    'not_tested': len(not_tested),
                    'accuracy': round(accuracy, 2),
                    'average_score': round(avg_score, 2),
                    'correct': correct_count,
                    'incorrect': len(incorrect)
                },
                'by_difficulty': {str(k): {
                    'total': v['total'],
                    'correct': v['correct'],
                    'accuracy': round(v['correct'] / v['total'] * 100, 2),
                    'average_score': round(sum(v['scores']) / len(v['scores']), 2)
                } for k, v in by_difficulty.items()},
                'incorrect_questions': incorrect,
                'correct_questions': correct
            }, f, ensure_ascii=False, indent=2)
        
        print(f"💾 详细分析已保存至: {output_path}\n")
    
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
