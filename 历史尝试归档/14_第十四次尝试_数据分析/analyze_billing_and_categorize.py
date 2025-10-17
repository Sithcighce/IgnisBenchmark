#!/usr/bin/env python3
"""
分析OpenRouter账单记录，确认GPT-5请求的真实返回情况
并整理所有题目的完整分类：答对、真实错误、API失败、未测试
"""

import json
import csv
from collections import defaultdict
from datetime import datetime

# 文件路径
BILLING_CSV = r"c:\Users\13031\Desktop\workspace\distillation_generation\验证\openrouter_activity_2025-10-17.csv"
LOG_FILE = r"c:\Users\13031\Desktop\workspace\distillation_generation\验证\gpt5_benchmark.log"
RECOVERED_JSON = r"c:\Users\13031\Desktop\workspace\distillation_generation\验证\benchmarkGPT5_recovered.json"
BEST_JSON = r"c:\Users\13031\Desktop\workspace\distillation_generation\验证\best.json"
OUTPUT_JSON = r"c:\Users\13031\Desktop\workspace\distillation_generation\验证\complete_question_categorization.json"

def parse_billing_csv():
    """解析账单CSV，提取GPT-5请求的详细信息"""
    print("=" * 70)
    print("解析OpenRouter账单记录")
    print("=" * 70)
    
    billing_data = []
    failed_requests = []
    
    with open(BILLING_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 只关注GPT-5的请求
            if 'gpt-5' in row.get('model_permaslug', '').lower():
                # 提取关键信息
                record = {
                    'generation_id': row['generation_id'],
                    'created_at': row['created_at'],
                    'cost_total': float(row['cost_total']) if row['cost_total'] else 0,
                    'tokens_prompt': int(row['tokens_prompt']) if row['tokens_prompt'] else 0,
                    'tokens_completion': int(row['tokens_completion']) if row['tokens_completion'] else 0,
                    'tokens_reasoning': int(row['tokens_reasoning']) if row['tokens_reasoning'] else 0,
                    'finish_reason_raw': row['finish_reason_raw'],
                    'finish_reason_normalized': row['finish_reason_normalized'],
                    'cancelled': row['cancelled'] == 'true',
                    'generation_time_ms': int(row['generation_time_ms']) if row['generation_time_ms'] else 0,
                }
                
                billing_data.append(record)
                
                # 检测失败的请求
                if (record['tokens_completion'] == 0 or 
                    record['cancelled'] or 
                    record['finish_reason_normalized'] not in ['stop', 'completed']):
                    failed_requests.append(record)
    
    print(f"\n📊 GPT-5账单统计:")
    print(f"   总请求数: {len(billing_data)}")
    print(f"   失败/异常请求: {len(failed_requests)}")
    print(f"   成功完成: {len(billing_data) - len(failed_requests)}")
    
    # 统计finish_reason分布
    finish_reasons = defaultdict(int)
    for record in billing_data:
        finish_reasons[record['finish_reason_normalized']] += 1
    
    print(f"\n📈 完成状态分布:")
    for reason, count in sorted(finish_reasons.items(), key=lambda x: -x[1]):
        print(f"   {reason}: {count}")
    
    # 统计token分布
    total_prompt = sum(r['tokens_prompt'] for r in billing_data)
    total_completion = sum(r['tokens_completion'] for r in billing_data)
    total_reasoning = sum(r['tokens_reasoning'] for r in billing_data)
    
    print(f"\n🎯 Token统计:")
    print(f"   总Prompt tokens: {total_prompt:,}")
    print(f"   总Completion tokens: {total_completion:,}")
    print(f"   总Reasoning tokens: {total_reasoning:,}")
    print(f"   平均Completion tokens/请求: {total_completion/len(billing_data):.0f}")
    
    # 零completion token的请求
    zero_completion = [r for r in billing_data if r['tokens_completion'] == 0]
    print(f"\n⚠️  零Completion token请求: {len(zero_completion)}")
    
    return billing_data, failed_requests

def parse_log_for_question_timing():
    """从日志中解析每个题目的处理时间，用于匹配账单"""
    print("\n" + "=" * 70)
    print("从日志中提取题目处理时间")
    print("=" * 70)
    
    question_times = {}
    
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        current_question = None
        for line in f:
            # 匹配 Processing 行
            if 'Processing [' in line and '] deepseek_q_' in line:
                parts = line.split('] ')
                if len(parts) >= 2:
                    question_id = parts[1].split()[0]
                    # 提取时间戳 (格式: 2025-10-15 13:03:41,321)
                    timestamp_str = line.split(' - ')[0]
                    try:
                        # 去掉毫秒部分的逗号，改为点号
                        timestamp_str = timestamp_str.replace(',', '.')
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
                        question_times[question_id] = timestamp
                        current_question = question_id
                    except:
                        pass
    
    print(f"   找到 {len(question_times)} 个题目的处理时间")
    return question_times

def load_recovered_results():
    """加载已恢复的测试结果"""
    with open(RECOVERED_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_best_questions():
    """加载best.json中的所有题目"""
    with open(BEST_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)

def categorize_all_questions():
    """完整分类所有题目"""
    print("\n" + "=" * 70)
    print("完整题目分类分析")
    print("=" * 70)
    
    # 加载数据
    billing_data, failed_billing = parse_billing_csv()
    question_times = parse_log_for_question_timing()
    recovered = load_recovered_results()
    all_questions = load_best_questions()
    
    print(f"\n📚 数据加载:")
    print(f"   best.json总题目数: {len(all_questions)}")
    print(f"   已恢复测试结果: {len(recovered)}")
    print(f"   账单GPT-5请求: {len(billing_data)}")
    
    # 创建恢复结果的映射
    recovered_map = {item['question_id']: item for item in recovered}
    
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
            gpt5_answer = result.get('gpt5_answer', {})
            
            if grading.get('correct', False):
                # 答对了
                categories['correct'].append({
                    'question_id': qid,
                    'score': grading.get('score', 0),
                    'difficulty': question['difficulty'],
                    'topic': question['topic'],
                    'type': question['type'],
                    'answer_length': gpt5_answer.get('length', 'unknown') if isinstance(gpt5_answer, dict) else 'unknown'
                })
            else:
                # 答错了，需要区分真实错误还是API失败
                answer_length = gpt5_answer.get('length', 'unknown') if isinstance(gpt5_answer, dict) else 'unknown'
                score = grading.get('score', 0)
                
                if answer_length != 'unknown' and (isinstance(answer_length, int) and answer_length >= 500):
                    # 真实错误：有实质回答但答错
                    categories['real_errors'].append({
                        'question_id': qid,
                        'score': score,
                        'difficulty': question['difficulty'],
                        'topic': question['topic'],
                        'type': question['type'],
                        'answer_length': answer_length,
                        'question': question['question_text'][:100] + '...'
                    })
                else:
                    # API失败：无回答或回答太短
                    categories['api_failures'].append({
                        'question_id': qid,
                        'score': score,
                        'difficulty': question['difficulty'],
                        'topic': question['topic'],
                        'type': question['type'],
                        'answer_length': answer_length,
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
    print("题目分类结果")
    print("=" * 70)
    
    print(f"\n✅ 答对的题目: {len(categories['correct'])} 题")
    print(f"   占best.json总数: {len(categories['correct'])/len(all_questions)*100:.2f}%")
    
    print(f"\n❌ 真实错误（有实质回答但答错）: {len(categories['real_errors'])} 题")
    print(f"   占已测试题目: {len(categories['real_errors'])/len(recovered)*100:.2f}%")
    
    print(f"\n⚠️  API失败（无回答或回答太短）: {len(categories['api_failures'])} 题")
    print(f"   占已测试题目: {len(categories['api_failures'])/len(recovered)*100:.2f}%")
    
    print(f"\n⏭️  未测试的题目: {len(categories['untested'])} 题")
    print(f"   占best.json总数: {len(categories['untested'])/len(all_questions)*100:.2f}%")
    
    # 详细分析真实错误
    if categories['real_errors']:
        print(f"\n" + "=" * 70)
        print(f"真实错误详细分析 ({len(categories['real_errors'])} 题)")
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
        
        # 最差的10道题
        print(f"\n🔥 最差的10道题:")
        sorted_errors = sorted(categories['real_errors'], key=lambda x: x['score'])[:10]
        for i, item in enumerate(sorted_errors, 1):
            print(f"\n{i}. [{item['question_id']}] 得分: {item['score']}/100")
            print(f"   难度 {item['difficulty']} | {item['topic']} | {item['type']}")
            print(f"   回答长度: {item['answer_length']} chars")
            print(f"   问题: {item['question']}")
    
    # 详细分析API失败
    if categories['api_failures']:
        print(f"\n" + "=" * 70)
        print(f"API失败详细分析 ({len(categories['api_failures'])} 题)")
        print("=" * 70)
        
        # 统计有分数的API失败（可能部分返回了数据）
        with_score = [item for item in categories['api_failures'] if item['score'] > 0]
        zero_score = [item for item in categories['api_failures'] if item['score'] == 0]
        
        print(f"\n   有分数 (>0): {len(with_score)} 题 (可能部分返回)")
        print(f"   零分: {len(zero_score)} 题 (很可能完全失败)")
        
        if zero_score:
            print(f"\n   零分题目示例 (前5个):")
            for item in zero_score[:5]:
                print(f"   - {item['question_id']}: 长度={item['answer_length']}")
    
    # 保存结果
    output = {
        'summary': {
            'total_questions': len(all_questions),
            'tested': len(recovered),
            'untested': len(categories['untested']),
            'correct': len(categories['correct']),
            'real_errors': len(categories['real_errors']),
            'api_failures': len(categories['api_failures']),
            'accuracy_all': f"{len(categories['correct'])/len(recovered)*100:.2f}%" if recovered else "0%",
            'accuracy_excluding_failures': f"{len(categories['correct'])/(len(categories['correct'])+len(categories['real_errors']))*100:.2f}%" if (categories['correct'] or categories['real_errors']) else "0%",
            'real_error_rate': f"{len(categories['real_errors'])/len(recovered)*100:.2f}%" if recovered else "0%",
        },
        'categories': categories,
        'billing_summary': {
            'total_gpt5_requests': len(billing_data),
            'failed_requests': len(failed_billing),
            'zero_completion_tokens': len([r for r in billing_data if r['tokens_completion'] == 0])
        }
    }
    
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n" + "=" * 70)
    print(f"💾 完整分类结果已保存至:")
    print(f"   {OUTPUT_JSON}")
    print("=" * 70)
    
    return output

if __name__ == '__main__':
    categorize_all_questions()
