#!/usr/bin/env python3
"""
从日志文件中恢复 GPT-5 基准测试结果
解析 gpt5_benchmark.log 并生成 benchmarkGPT5.json 和统计数据
"""
import json
import re
from datetime import datetime
from collections import defaultdict

def parse_log_file(log_path):
    """解析日志文件，提取所有成功完成的测试结果"""
    
    results = []
    current_question = None
    question_data = {}
    
    # 统计
    total_processed = 0
    successful = 0
    failed_api = 0
    
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # 匹配处理进度: Processing [123/984] deepseek_q_xxx
            process_match = re.search(r'Processing \[(\d+)/(\d+)\] (deepseek_q_\w+)', line)
            if process_match:
                # 保存上一个问题的数据（如果有）
                if current_question and 'grading' in question_data:
                    results.append(question_data.copy())
                
                # 开始新问题
                total_processed += 1
                current_question = process_match.group(3)
                question_data = {
                    'question_id': current_question,
                    'index': int(process_match.group(1)),
                    'gpt5_answer': None,
                    'grading': None
                }
                continue
            
            # 匹配 GPT-5 回答: ✓ GPT-5 answered (length: 1234 chars)
            if '✓ GPT-5 answered' in line:
                length_match = re.search(r'length: (\d+) chars', line)
                if length_match and current_question:
                    question_data['gpt5_answer_length'] = int(length_match.group(1))
                continue
            
            # 匹配判题结果: ✓ Graded: CORRECT/INCORRECT (Score: 95)
            graded_match = re.search(r'✓ Graded: (CORRECT|INCORRECT) \(Score: (\d+)\)', line)
            if graded_match and current_question:
                successful += 1
                question_data['grading'] = {
                    'correct': graded_match.group(1) == 'CORRECT',
                    'score': int(graded_match.group(2)),
                    'recovered_from_log': True
                }
                continue
            
            # 匹配API错误
            if '✗ Error: API Error 402' in line:
                failed_api += 1
                continue
    
    # 保存最后一个问题
    if current_question and 'grading' in question_data:
        results.append(question_data.copy())
    
    print(f"\n{'='*70}")
    print(f"日志解析完成")
    print(f"{'='*70}\n")
    print(f"📊 解析统计:")
    print(f"   总处理数: {total_processed}")
    print(f"   成功完成: {successful}")
    print(f"   API失败: {failed_api}")
    print(f"   有效结果: {len(results)}\n")
    
    return results

def load_best_questions(best_json_path):
    """加载 best.json 获取完整问题信息"""
    with open(best_json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def merge_results(log_results, best_questions):
    """合并日志结果和完整问题信息"""
    
    # 创建问题ID到完整信息的映射
    question_map = {q['question_id']: q for q in best_questions}
    
    # 合并数据
    merged_results = []
    for log_result in log_results:
        qid = log_result['question_id']
        if qid in question_map and log_result.get('grading'):
            full_data = question_map[qid].copy()
            full_data['gpt5_answer'] = f"[恢复自日志 - 原始回答长度: {log_result.get('gpt5_answer_length', 'unknown')} chars]"
            full_data['grading'] = log_result['grading'].copy()
            full_data['grading']['note'] = '此结果从日志中恢复，GPT-5原始回答内容未保存'
            merged_results.append(full_data)
    
    return merged_results

def calculate_statistics(results):
    """计算统计数据"""
    
    total = len(results)
    correct = sum(1 for r in results if r['grading']['correct'])
    incorrect = total - correct
    accuracy = correct / total * 100 if total > 0 else 0
    
    # 计算平均分
    avg_score = sum(r['grading']['score'] for r in results) / total if total > 0 else 0
    
    # 按难度统计
    by_difficulty = defaultdict(lambda: {'total': 0, 'correct': 0, 'scores': []})
    for r in results:
        diff = r.get('difficulty', 'unknown')
        by_difficulty[diff]['total'] += 1
        if r['grading']['correct']:
            by_difficulty[diff]['correct'] += 1
        by_difficulty[diff]['scores'].append(r['grading']['score'])
    
    # 按主题统计
    by_topic = defaultdict(lambda: {'total': 0, 'correct': 0, 'scores': []})
    for r in results:
        topic = r.get('topic', 'unknown')
        by_topic[topic]['total'] += 1
        if r['grading']['correct']:
            by_topic[topic]['correct'] += 1
        by_topic[topic]['scores'].append(r['grading']['score'])
    
    # 按类型统计
    by_type = defaultdict(lambda: {'total': 0, 'correct': 0, 'scores': []})
    for r in results:
        qtype = r.get('type', 'unknown')
        by_type[qtype]['total'] += 1
        if r['grading']['correct']:
            by_type[qtype]['correct'] += 1
        by_type[qtype]['scores'].append(r['grading']['score'])
    
    # 构建统计对象
    stats = {
        'overall': {
            'total_questions': total,
            'correct': correct,
            'incorrect': incorrect,
            'accuracy': round(accuracy, 2),
            'average_score': round(avg_score, 2)
        },
        'by_difficulty': {},
        'by_topic': {},
        'by_type': {},
        'recovery_info': {
            'recovered_from': 'gpt5_benchmark.log',
            'recovery_date': datetime.now().isoformat(),
            'note': '由于API余额不足导致脚本中断，此结果从日志中恢复。GPT-5的原始回答内容未保存。'
        }
    }
    
    # 处理难度统计
    for diff, data in by_difficulty.items():
        stats['by_difficulty'][str(diff)] = {
            'total': data['total'],
            'correct': data['correct'],
            'accuracy': round(data['correct'] / data['total'] * 100, 2),
            'average_score': round(sum(data['scores']) / len(data['scores']), 2)
        }
    
    # 处理主题统计（只保留前10）
    topic_items = sorted(by_topic.items(), key=lambda x: x[1]['total'], reverse=True)[:10]
    for topic, data in topic_items:
        stats['by_topic'][topic] = {
            'total': data['total'],
            'correct': data['correct'],
            'accuracy': round(data['correct'] / data['total'] * 100, 2),
            'average_score': round(sum(data['scores']) / len(data['scores']), 2)
        }
    
    # 处理类型统计
    for qtype, data in by_type.items():
        stats['by_type'][qtype] = {
            'total': data['total'],
            'correct': data['correct'],
            'accuracy': round(data['correct'] / data['total'] * 100, 2),
            'average_score': round(sum(data['scores']) / len(data['scores']), 2)
        }
    
    return stats

def find_needs_review(results):
    """找出标记为 needs_review 的题目"""
    needs_review = []
    for r in results:
        # 检查验证结果中的状态
        if 'consensus' in r and r['consensus'].get('status') == 'needs_review':
            needs_review.append({
                'question_id': r['question_id'],
                'gpt5_correct': r['grading']['correct'],
                'gpt5_score': r['grading']['score'],
                'verification_issues': r['consensus'].get('reasons', [])
            })
    return needs_review

def print_summary(stats, needs_review_count):
    """打印漂亮的统计摘要"""
    
    print(f"\n{'='*70}")
    print(f"📊 GPT-5 基准测试结果（从日志恢复）")
    print(f"{'='*70}\n")
    
    print(f"⚠️  重要提示:")
    print(f"   由于 OpenRouter 余额不足，脚本在处理过程中中断")
    print(f"   此结果从日志文件中恢复，GPT-5 的原始回答内容未保存\n")
    
    overall = stats['overall']
    print(f"🎯 总体正确率: {overall['accuracy']}%")
    print(f"   总题目数: {overall['total_questions']}")
    print(f"   正确: {overall['correct']}")
    print(f"   错误: {overall['incorrect']}")
    print(f"   平均分: {overall['average_score']}/100\n")
    
    print(f"📈 按难度分析:")
    for diff, data in sorted(stats['by_difficulty'].items()):
        print(f"   难度 {diff}: {data['accuracy']}% ({data['correct']}/{data['total']}) - 平均分: {data['average_score']}")
    
    print(f"\n📚 按主题分析 (Top 10):")
    for topic, data in list(stats['by_topic'].items())[:10]:
        print(f"   {topic}: {data['accuracy']}% ({data['correct']}/{data['total']}) - 平均分: {data['average_score']}")
    
    print(f"\n🔍 按题型分析:")
    for qtype, data in stats['by_type'].items():
        print(f"   {qtype}: {data['accuracy']}% ({data['correct']}/{data['total']}) - 平均分: {data['average_score']}")
    
    if needs_review_count > 0:
        print(f"\n⚠️  Needs Review 题目: {needs_review_count}")
        print(f"   这些题目在验证阶段被标记为需要人工审查")
    
    print(f"\n{'='*70}\n")

def main():
    log_path = r'c:\Users\13031\Desktop\workspace\distillation_generation\验证\gpt5_benchmark.log'
    best_json_path = r'c:\Users\13031\Desktop\workspace\distillation_generation\验证\best.json'
    output_json_path = r'c:\Users\13031\Desktop\workspace\distillation_generation\验证\benchmarkGPT5_recovered.json'
    stats_json_path = r'c:\Users\13031\Desktop\workspace\distillation_generation\验证\gpt5_benchmark_stats_recovered.json'
    needs_review_path = r'c:\Users\13031\Desktop\workspace\distillation_generation\验证\gpt5_needs_review.json'
    
    print("🔄 开始从日志恢复数据...")
    
    # 解析日志
    log_results = parse_log_file(log_path)
    
    if not log_results:
        print("❌ 未能从日志中提取任何有效结果！")
        return
    
    # 加载完整问题信息
    print("📖 加载完整问题信息...")
    best_questions = load_best_questions(best_json_path)
    
    # 合并数据
    print("🔗 合并数据...")
    merged_results = merge_results(log_results, best_questions)
    
    # 计算统计
    print("📊 计算统计数据...")
    stats = calculate_statistics(merged_results)
    
    # 查找 needs_review 题目
    print("🔍 查找 needs_review 题目...")
    needs_review = find_needs_review(merged_results)
    
    # 保存结果
    print("💾 保存结果文件...")
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(merged_results, f, ensure_ascii=False, indent=2)
    
    with open(stats_json_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    if needs_review:
        with open(needs_review_path, 'w', encoding='utf-8') as f:
            json.dump(needs_review, f, ensure_ascii=False, indent=2)
    
    # 打印摘要
    print_summary(stats, len(needs_review))
    
    print(f"✅ 恢复完成！")
    print(f"\n生成的文件:")
    print(f"   1. {output_json_path}")
    print(f"   2. {stats_json_path}")
    if needs_review:
        print(f"   3. {needs_review_path} ({len(needs_review)} 题)\n")
    
    # 关于成本的说明
    print(f"\n💰 关于成本问题的分析:")
    print(f"{'='*70}")
    print(f"为什么会花费 $100？")
    print(f"\n1. GPT-5 (OpenRouter) 的定价:")
    print(f"   - 输入: $2.50 per 1M tokens")
    print(f"   - 输出: $10.00 per 1M tokens")
    print(f"\n2. 您的使用量估算:")
    print(f"   - 处理了约 {len(merged_results)} 道题目")
    print(f"   - 每题问题长度: 约 500-2000 tokens")
    print(f"   - 每题 GPT-5 回答: 平均 {sum(r.get('gpt5_answer_length', 0) for r in log_results) // len(log_results) if log_results else 0} 字符 (约 1500-3000 tokens)")
    print(f"   - 每题判题输入: 问题+标准答案+GPT-5回答 (约 2000-5000 tokens)")
    print(f"   - 每题判题输出: 约 200-500 tokens")
    print(f"\n3. 粗略计算:")
    print(f"   - GPT-5 回答: {len(merged_results)} × 2000 input + 2000 output")
    print(f"     ≈ {len(merged_results) * 2000 / 1_000_000:.2f}M input + {len(merged_results) * 2000 / 1_000_000:.2f}M output")
    print(f"     ≈ ${len(merged_results) * 2000 / 1_000_000 * 2.5:.2f} + ${len(merged_results) * 2000 / 1_000_000 * 10:.2f}")
    print(f"     ≈ ${len(merged_results) * 2000 / 1_000_000 * 12.5:.2f}")
    print(f"\n   - DeepSeek 判题: {len(merged_results)} × 4000 input + 300 output")
    print(f"     (DeepSeek 便宜很多，约 $0.14/1M input, $0.28/1M output)")
    print(f"     ≈ ${len(merged_results) * 4000 / 1_000_000 * 0.14:.2f} + ${len(merged_results) * 300 / 1_000_000 * 0.28:.2f}")
    print(f"     ≈ ${len(merged_results) * 4000 / 1_000_000 * 0.42:.2f}")
    print(f"\n   总计估算: ${len(merged_results) * 2000 / 1_000_000 * 12.5 + len(merged_results) * 4000 / 1_000_000 * 0.42:.2f}")
    print(f"\n4. 教训:")
    print(f"   - GPT-5 非常昂贵 (输出 $10/1M tokens!)")
    print(f"   - 应该先用少量题目测试成本")
    print(f"   - 考虑使用更便宜的模型 (如 GPT-4-turbo, Claude 3.5)")
    print(f"   - 或者只在难题上使用 GPT-5")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
