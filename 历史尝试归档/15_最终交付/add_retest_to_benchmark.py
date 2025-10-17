#!/usr/bin/env python3
"""
将重测答错的5个题目加入benchmark
从145题扩展到150题
"""
import json
import os
from pathlib import Path
from datetime import datetime

# Paths
VERIFY_DIR = Path(r'c:\Users\13031\Desktop\workspace\distillation_generation\验证')
OUTPUT_DIR = Path(r'c:\Users\13031\Desktop\workspace\distillation_generation\最终交付')

RETEST_RESULTS = VERIFY_DIR / 'retest_zero_score_results.json'
BENCHMARK_RECOVERED = VERIFY_DIR / 'benchmarkGPT5_recovered.json'

# 当前的4个benchmark文件
BENCHMARK_BASIC = OUTPUT_DIR / 'benchmark_basic.json'
BENCHMARK_WITH_VERIFICATION = OUTPUT_DIR / 'benchmark_with_verification.json'
BENCHMARK_WITH_GPT5 = OUTPUT_DIR / 'benchmark_with_gpt5_results.json'
BENCHMARK_COMPLETE = OUTPUT_DIR / 'benchmark_complete.json'


def load_retest_results():
    """加载重测结果"""
    with open(RETEST_RESULTS, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_benchmark_recovered():
    """加载完整的benchmarkGPT5_recovered.json"""
    with open(BENCHMARK_RECOVERED, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_incorrect_question_ids():
    """获取答错的5个题目ID"""
    retest_results = load_retest_results()
    incorrect_ids = [q['question_id'] for q in retest_results if not q.get('correct', False)]
    print(f"答错的题目: {len(incorrect_ids)} 个")
    for qid in incorrect_ids:
        print(f"  - {qid}")
    return incorrect_ids


def get_question_data(question_id, all_questions):
    """从benchmarkGPT5_recovered.json获取题目完整数据"""
    for q in all_questions:
        if q['question_id'] == question_id:
            return q
    raise ValueError(f"Question {question_id} not found in benchmarkGPT5_recovered.json")


def get_retest_result(question_id, retest_results):
    """获取重测结果"""
    for r in retest_results:
        if r['question_id'] == question_id:
            return r
    return None


def add_to_benchmark_basic(new_questions):
    """添加到 benchmark_basic.json"""
    print(f"\n更新 benchmark_basic.json")
    
    with open(BENCHMARK_BASIC, 'r', encoding='utf-8') as f:
        existing = json.load(f)
    
    for q in new_questions:
        item = {
            "question_id": q['question_id'],
            "question_text": q['question_text'],
            "standard_answer": q['standard_answer'],
            "difficulty": q['difficulty'],
            "topic": q['topic'],
            "type": q['type']
        }
        existing.append(item)
    
    with open(BENCHMARK_BASIC, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    
    print(f"  添加 {len(new_questions)} 题 → 总计 {len(existing)} 题")


def add_to_benchmark_with_verification(new_questions):
    """添加到 benchmark_with_verification.json"""
    print(f"\n更新 benchmark_with_verification.json")
    
    with open(BENCHMARK_WITH_VERIFICATION, 'r', encoding='utf-8') as f:
        existing = json.load(f)
    
    for q in new_questions:
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
            "source": q.get('source', '')
        }
        existing.append(item)
    
    with open(BENCHMARK_WITH_VERIFICATION, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    
    print(f"  添加 {len(new_questions)} 题 → 总计 {len(existing)} 题")


def add_to_benchmark_with_gpt5(new_questions, retest_results):
    """添加到 benchmark_with_gpt5_results.json"""
    print(f"\n更新 benchmark_with_gpt5_results.json")
    
    with open(BENCHMARK_WITH_GPT5, 'r', encoding='utf-8') as f:
        existing = json.load(f)
    
    for q in new_questions:
        retest = get_retest_result(q['question_id'], retest_results)
        
        item = {
            "question_id": q['question_id'],
            "question_text": q['question_text'],
            "standard_answer": q['standard_answer'],
            "difficulty": q['difficulty'],
            "topic": q['topic'],
            "type": q['type'],
            "gpt5_test_result": {
                "score": retest['score'],
                "answer_length": retest['gpt_answer_length'],
                "category": "api_failure_zero_score_retest",
                "note": f"原API失败0分，重测得分{retest['score']}分，答错"
            }
        }
        existing.append(item)
    
    with open(BENCHMARK_WITH_GPT5, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    
    print(f"  添加 {len(new_questions)} 题 → 总计 {len(existing)} 题")


def add_to_benchmark_complete(new_questions, retest_results):
    """添加到 benchmark_complete.json"""
    print(f"\n更新 benchmark_complete.json")
    
    with open(BENCHMARK_COMPLETE, 'r', encoding='utf-8') as f:
        existing = json.load(f)
    
    for q in new_questions:
        retest = get_retest_result(q['question_id'], retest_results)
        
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
            "source": q.get('source', ''),
            "gpt5_test_result": {
                "score": retest['score'],
                "answer_length": retest['gpt_answer_length'],
                "category": "api_failure_zero_score_retest",
                "note": f"原API失败0分，重测得分{retest['score']}分，答错"
            },
            "benchmark_category": "api_failure_zero_score_retest",
            "benchmark_note": f"原API失败0分，OpenAI重测得分{retest['score']}，答错但有分"
        }
        existing.append(item)
    
    with open(BENCHMARK_COMPLETE, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    
    print(f"  添加 {len(new_questions)} 题 → 总计 {len(existing)} 题")


def main():
    """主函数"""
    print("=" * 80)
    print("将重测答错的5题加入benchmark (145 → 150)")
    print("=" * 80)
    
    # 获取答错的题目ID
    incorrect_ids = get_incorrect_question_ids()
    
    # 加载完整数据
    print(f"\n加载完整题目数据...")
    all_questions = load_benchmark_recovered()
    retest_results = load_retest_results()
    
    # 获取这5题的完整数据
    new_questions = []
    for qid in incorrect_ids:
        q_data = get_question_data(qid, all_questions)
        new_questions.append(q_data)
    
    print(f"获取到 {len(new_questions)} 题完整数据")
    
    # 添加到4个benchmark文件
    add_to_benchmark_basic(new_questions)
    add_to_benchmark_with_verification(new_questions)
    add_to_benchmark_with_gpt5(new_questions, retest_results)
    add_to_benchmark_complete(new_questions, retest_results)
    
    print(f"\n{'='*80}")
    print("✓ 完成！benchmark已从145题扩展到150题")
    print("=" * 80)
    
    # 统计信息
    with open(BENCHMARK_BASIC, 'r', encoding='utf-8') as f:
        total = len(json.load(f))
    
    print(f"\n最终统计:")
    print(f"  总题目数: {total}")
    print(f"  新增题目: {len(new_questions)}")
    print(f"  类别: API失败(0分)重测答错")
    print(f"  平均得分: {sum(r['score'] for r in retest_results if not r.get('correct', False)) / len(incorrect_ids):.1f}")


if __name__ == "__main__":
    main()
