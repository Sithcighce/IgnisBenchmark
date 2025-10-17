#!/usr/bin/env python3
"""
完整分类所有best.json题目：答对、真实错误、API失败、未测试
"""

import json
import csv
from collections import defaultdict

# 文件路径
BILLING_CSV = r"c:\Users\13031\Desktop\workspace\distillation_generation\验证\openrouter_activity_2025-10-17.csv"
RECOVERED_JSON = r"c:\Users\13031\Desktop\workspace\distillation_generation\验证\benchmarkGPT5_recovered.json"
BEST_JSON = r"c:\Users\13031\Desktop\workspace\distillation_generation\验证\best.json"
REAL_ERRORS_JSON = r"c:\Users\13031\Desktop\workspace\distillation_generation\验证\gpt5_real_errors.json"
INCORRECT_DETAILED_JSON = r"c:\Users\13031\Desktop\workspace\distillation_generation\验证\gpt5_incorrect_detailed.json"
OUTPUT_JSON = r"c:\Users\13031\Desktop\workspace\distillation_generation\验证\complete_question_categorization.json"

def parse_billing_csv():
    """解析账单CSV，提取GPT-5请求的详细信息"""
    print("=" * 70)
    print("📊 解析OpenRouter账单记录")
    print("=" * 70)
    
    billing_data = []
    
    with open(BILLING_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'gpt-5' in row.get('model_permaslug', '').lower():
                record = {
                    'generation_id': row['generation_id'],
                    'created_at': row['created_at'],
                    'cost_total': float(row['cost_total']) if row['cost_total'] else 0,
                    'tokens_prompt': int(row['tokens_prompt']) if row['tokens_prompt'] else 0,
                    'tokens_completion': int(row['tokens_completion']) if row['tokens_completion'] else 0,
                    'tokens_reasoning': int(row['tokens_reasoning']) if row['tokens_reasoning'] else 0,
                    'finish_reason': row['finish_reason_normalized'],
                    'cancelled': row['cancelled'] == 'true',
                }
                billing_data.append(record)
    
    print(f"   总GPT-5请求数: {len(billing_data)}")
    
    # 统计
    total_cost = sum(r['cost_total'] for r in billing_data)
    total_completion = sum(r['tokens_completion'] for r in billing_data)
    zero_completion = len([r for r in billing_data if r['tokens_completion'] == 0])
    
    print(f"   总花费: ${total_cost:.2f}")
    print(f"   总Completion tokens: {total_completion:,}")
    print(f"   平均Completion/请求: {total_completion/len(billing_data):.0f}")
    print(f"   零Completion请求: {zero_completion}")
    
    return billing_data

def categorize_all_questions():
    """完整分类所有题目"""
    print("\n" + "=" * 70)
    print("📚 完整题目分类分析")
    print("=" * 70)
    
    # 加载数据
    billing_data = parse_billing_csv()
    
    with open(RECOVERED_JSON, 'r', encoding='utf-8') as f:
        recovered = json.load(f)
    
    with open(BEST_JSON, 'r', encoding='utf-8') as f:
        all_questions = json.load(f)
    
    with open(REAL_ERRORS_JSON, 'r', encoding='utf-8') as f:
        real_errors_data = json.load(f)
    
    with open(INCORRECT_DETAILED_JSON, 'r', encoding='utf-8') as f:
        incorrect_detailed = json.load(f)
    
    print(f"\n   best.json总题目数: {len(all_questions)}")
    print(f"   已测试题目数: {len(recovered)}")
    print(f"   账单GPT-5请求: {len(billing_data)}")
    
    # 创建映射
    recovered_map = {item['question_id']: item for item in recovered}
    real_errors_ids = {q['question_id'] for q in real_errors_data['questions_with_substantial_answers']}
    
    # 从incorrect_detailed中找出所有错误的题目
    all_incorrect_ids = {q['question_id'] for q in incorrect_detailed['incorrect_questions_with_details']}
    api_failures_ids = all_incorrect_ids - real_errors_ids  # 所有错误题目 - 真实错误 = API失败
    
    # 分类
    categories = {
        'correct': [],           # 答对的
        'real_errors': [],       # 真实错误（有实质回答但答错）
        'api_failures': [],      # API失败（无回答或回答太短）
        'untested': []           # 未测试的
    }
    
    for question in all_questions:
        qid = question['question_id']
        
        if qid in recovered_map:
            result = recovered_map[qid]
            grading = result.get('grading', {})
            
            if grading.get('correct', False):
                # 答对了
                categories['correct'].append({
                    'question_id': qid,
                    'score': grading.get('score', 0),
                    'difficulty': question['difficulty'],
                    'topic': question['topic'],
                    'type': question['type'],
                    'question_text': question['question_text'][:100] + '...'
                })
            elif qid in real_errors_ids:
                # 真实错误
                # 从real_errors中找到完整信息
                real_error = next((q for q in real_errors_data['questions_with_substantial_answers'] if q['question_id'] == qid), None)
                if real_error:
                    categories['real_errors'].append(real_error)
            elif qid in api_failures_ids:
                # API失败
                # 从incorrect_detailed中找到信息
                api_failure_detail = next((q for q in incorrect_detailed['incorrect_questions_with_details'] if q['question_id'] == qid), None)
                if api_failure_detail:
                    gpt5_result = api_failure_detail.get('gpt5_result', {})
                    categories['api_failures'].append({
                        'question_id': qid,
                        'score': gpt5_result.get('score', 0),
                        'difficulty': question['difficulty'],
                        'topic': question['topic'],
                        'type': question['type'],
                        'answer_length': gpt5_result.get('answer_length', 'unknown'),
                        'question': question['question_text'][:100] + '...'
                    })
            else:
                # 其他错误情况
                categories['api_failures'].append({
                    'question_id': qid,
                    'score': grading.get('score', 0),
                    'difficulty': question['difficulty'],
                    'topic': question['topic'],
                    'type': question['type'],
                    'answer_length': 'unknown',
                    'question': question['question_text'][:100] + '...'
                })
        else:
            # 未测试
            categories['untested'].append({
                'question_id': qid,
                'difficulty': question['difficulty'],
                'topic': question['topic'],
                'type': question['type'],
                'question': question['question_text'][:100] + '...'
            })
    
    # 输出统计
    print("\n" + "=" * 70)
    print("📊 题目分类结果")
    print("=" * 70)
    
    print(f"\n✅ 答对的题目: {len(categories['correct'])} 题")
    print(f"   占best.json总数: {len(categories['correct'])/len(all_questions)*100:.2f}%")
    print(f"   占已测试题目: {len(categories['correct'])/len(recovered)*100:.2f}%")
    
    print(f"\n❌ 真实错误（有实质回答≥500字符但答错）: {len(categories['real_errors'])} 题")
    print(f"   占已测试题目: {len(categories['real_errors'])/len(recovered)*100:.2f}%")
    print(f"   真实错误率: {len(categories['real_errors'])/len(recovered)*100:.2f}%")
    
    print(f"\n⚠️  API失败（无回答或回答太短<500字符）: {len(categories['api_failures'])} 题")
    print(f"   占已测试题目: {len(categories['api_failures'])/len(recovered)*100:.2f}%")
    
    print(f"\n⏭️  未测试的题目: {len(categories['untested'])} 题")
    print(f"   占best.json总数: {len(categories['untested'])/len(all_questions)*100:.2f}%")
    
    # 调整后的准确率
    tested_valid = len(categories['correct']) + len(categories['real_errors'])
    if tested_valid > 0:
        adjusted_accuracy = len(categories['correct']) / tested_valid * 100
        print(f"\n🎯 调整后准确率（排除API失败）: {adjusted_accuracy:.2f}%")
        print(f"   基准: {len(categories['correct'])} 正确 / {tested_valid} 有效测试")
    
    # 真实错误详细分析
    if categories['real_errors']:
        print(f"\n" + "=" * 70)
        print(f"📉 真实错误详细分析 ({len(categories['real_errors'])} 题)")
        print("=" * 70)
        
        # 按分数段统计
        score_ranges = defaultdict(int)
        for item in categories['real_errors']:
            score = item['score']
            if score < 20:
                score_ranges['0-20'] += 1
            elif score < 40:
                score_ranges['21-40'] += 1
            elif score < 60:
                score_ranges['41-60'] += 1
            else:
                score_ranges['61-80'] += 1
        
        print(f"\n按分数段分布:")
        for range_name in ['0-20', '21-40', '41-60', '61-80']:
            count = score_ranges[range_name]
            if count > 0:
                print(f"   {range_name}分: {count} 题")
        
        # 按难度统计
        diff_stats = defaultdict(list)
        for item in categories['real_errors']:
            diff_stats[item['difficulty']].append(item['score'])
        
        print(f"\n按难度分布:")
        for diff in sorted(diff_stats.keys()):
            scores = diff_stats[diff]
            print(f"   难度 {diff}: {len(scores)} 题, 平均分 {sum(scores)/len(scores):.1f}")
        
        # 按主题统计
        topic_stats = defaultdict(list)
        for item in categories['real_errors']:
            topic_stats[item['topic']].append(item['score'])
        
        print(f"\n按主题分布 (Top 10):")
        sorted_topics = sorted(topic_stats.items(), key=lambda x: -len(x[1]))[:10]
        for topic, scores in sorted_topics:
            print(f"   {topic}: {len(scores)} 题, 平均分 {sum(scores)/len(scores):.1f}")
        
        # 平均回答长度
        avg_length = sum(item['answer_length'] for item in categories['real_errors']) / len(categories['real_errors'])
        print(f"\n平均回答长度: {avg_length:.0f} 字符")
        
        # 最差的10道题
        print(f"\n🔥 最差的10道题（有实质回答但得分最低）:")
        sorted_errors = sorted(categories['real_errors'], key=lambda x: x['score'])[:10]
        for i, item in enumerate(sorted_errors, 1):
            print(f"\n{i}. [{item['question_id']}] 得分: {item['score']}/100")
            print(f"   难度 {item['difficulty']} | {item['topic']} | {item['type']}")
            print(f"   回答长度: {item['answer_length']} chars")
            print(f"   问题: {item.get('question_text', item.get('question', 'N/A'))[:150]}...")
    
    # API失败详细分析
    if categories['api_failures']:
        print(f"\n" + "=" * 70)
        print(f"⚠️  API失败详细分析 ({len(categories['api_failures'])} 题)")
        print("=" * 70)
        
        zero_score = [item for item in categories['api_failures'] if item['score'] == 0]
        low_score = [item for item in categories['api_failures'] if 0 < item['score'] <= 40]
        mid_score = [item for item in categories['api_failures'] if 40 < item['score'] <= 80]
        
        print(f"\n分数分布:")
        print(f"   0分: {len(zero_score)} 题（很可能完全失败）")
        print(f"   1-40分: {len(low_score)} 题（可能部分返回）")
        print(f"   41-80分: {len(mid_score)} 题（可能回答太短）")
        
        if zero_score:
            print(f"\n零分题目示例 (前5个):")
            for item in zero_score[:5]:
                print(f"   - {item['question_id']}: answer_length={item.get('answer_length', 'unknown')}")
    
    # 未测试题目分析
    if categories['untested']:
        print(f"\n" + "=" * 70)
        print(f"⏭️  未测试题目分析 ({len(categories['untested'])} 题)")
        print("=" * 70)
        
        diff_counts = defaultdict(int)
        for item in categories['untested']:
            diff_counts[item['difficulty']] += 1
        
        print(f"\n按难度分布:")
        for diff in sorted(diff_counts.keys()):
            print(f"   难度 {diff}: {diff_counts[diff]} 题")
    
    # 保存结果
    output = {
        'summary': {
            'total_questions': len(all_questions),
            'tested': len(recovered),
            'untested': len(categories['untested']),
            'correct': len(categories['correct']),
            'real_errors': len(categories['real_errors']),
            'api_failures': len(categories['api_failures']),
            'raw_accuracy': f"{len(categories['correct'])/len(recovered)*100:.2f}%",
            'adjusted_accuracy': f"{len(categories['correct'])/(len(categories['correct'])+len(categories['real_errors']))*100:.2f}%" if (categories['correct'] or categories['real_errors']) else "0%",
            'real_error_rate': f"{len(categories['real_errors'])/len(recovered)*100:.2f}%",
            'api_failure_rate': f"{len(categories['api_failures'])/len(recovered)*100:.2f}%",
        },
        'categories': categories,
        'billing_summary': {
            'total_gpt5_requests': len(billing_data),
            'total_cost': f"${sum(r['cost_total'] for r in billing_data):.2f}",
            'total_completion_tokens': sum(r['tokens_completion'] for r in billing_data),
            'zero_completion_requests': len([r for r in billing_data if r['tokens_completion'] == 0])
        }
    }
    
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n" + "=" * 70)
    print(f"💾 完整分类结果已保存至:")
    print(f"   {OUTPUT_JSON}")
    print("=" * 70)
    
    print(f"\n" + "=" * 70)
    print("📈 关键结论")
    print("=" * 70)
    print(f"\n1. GPT-5在best.json上的表现:")
    print(f"   - 原始准确率: {len(categories['correct'])/len(recovered)*100:.2f}% ({len(categories['correct'])}/{len(recovered)})")
    print(f"   - 排除API失败后: {len(categories['correct'])/(len(categories['correct'])+len(categories['real_errors']))*100:.2f}% ({len(categories['correct'])}/{len(categories['correct'])+len(categories['real_errors'])})")
    print(f"\n2. 错误分类:")
    print(f"   - 真实知识错误: {len(categories['real_errors'])} 题 (GPT-5认真回答但答错)")
    print(f"   - API技术失败: {len(categories['api_failures'])} 题 (无回答或太短)")
    print(f"\n3. 账单分析:")
    print(f"   - 总花费: {output['billing_summary']['total_cost']}")
    print(f"   - 总GPT-5请求: {output['billing_summary']['total_gpt5_requests']}")
    print(f"   - 平均成本/题: ${sum(r['cost_total'] for r in billing_data)/len(recovered):.4f}")
    
    return output

if __name__ == '__main__':
    categorize_all_questions()
