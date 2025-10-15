#!/usr/bin/env python3
"""
问题数据集示例脚本
展示如何使用question_all数据
"""

import json
from pathlib import Path
from collections import Counter
from typing import List, Dict

def load_all_questions(question_dir: Path = Path("question_all")) -> tuple:
    """加载所有问题"""
    pass_questions = []
    notpass_questions = []
    
    for folder in question_dir.iterdir():
        if not folder.is_dir():
            continue
        
        # 读取pass.json
        pass_file = folder / "pass.json"
        if pass_file.exists():
            try:
                with open(pass_file, 'r', encoding='utf-8') as f:
                    pass_questions.extend(json.load(f))
            except:
                pass
        
        # 读取not_pass.json
        notpass_file = folder / "not_pass.json"
        if notpass_file.exists():
            try:
                with open(notpass_file, 'r', encoding='utf-8') as f:
                    notpass_questions.extend(json.load(f))
            except:
                pass
    
    return pass_questions, notpass_questions


def analyze_questions(questions: List[Dict]) -> Dict:
    """分析问题特征"""
    # 类型分布
    types = Counter(q.get('type', 'unknown') for q in questions)
    
    # 难度分布
    difficulties = Counter(q.get('difficulty', 0) for q in questions)
    
    # 主题分布
    topics = Counter(q.get('topic', 'unknown') for q in questions)
    
    # 答案长度统计
    answer_lengths = [
        q.get('metadata', {}).get('answer_length', 0) 
        for q in questions
    ]
    avg_length = sum(answer_lengths) / len(answer_lengths) if answer_lengths else 0
    
    return {
        "total": len(questions),
        "types": dict(types),
        "difficulties": dict(difficulties),
        "topics": dict(topics),
        "avg_answer_length": avg_length
    }


def find_best_questions(questions: List[Dict], top_n: int = 10) -> List[Dict]:
    """找出最好的问题（基于答案长度和难度）"""
    scored = []
    for q in questions:
        score = 0
        
        # 答案长度加分
        length = q.get('metadata', {}).get('answer_length', 0)
        score += min(length / 100, 10)  # 最多10分
        
        # 难度加分
        difficulty = q.get('difficulty', 0)
        score += difficulty * 2  # 最多10分
        
        # 质量检查全通过加分
        qc = q.get('quality_check', {})
        if all([
            qc.get('domain_focused'),
            qc.get('answer_correct'),
            qc.get('other_compliant')
        ]):
            score += 5
        
        scored.append((score, q))
    
    # 按分数降序排序
    scored.sort(reverse=True, key=lambda x: x[0])
    
    return [q for _, q in scored[:top_n]]


def generate_statistics_report():
    """生成统计报告"""
    print("=" * 80)
    print("Question Dataset Statistics")
    print("=" * 80)
    
    # 加载问题
    pass_q, notpass_q = load_all_questions()
    print(f"\nData Overview:")
    print(f"  Pass questions: {len(pass_q)}")
    print(f"  Not-pass questions: {len(notpass_q)}")
    print(f"  Total: {len(pass_q) + len(notpass_q)}")
    print(f"  Pass rate: {len(pass_q)/(len(pass_q)+len(notpass_q))*100:.1f}%")
    
    # 分析通过的问题
    print(f"\nPass Questions Analysis:")
    pass_stats = analyze_questions(pass_q)
    
    print(f"\n  Types:")
    for type_name, count in sorted(pass_stats['types'].items(), key=lambda x: -x[1]):
        print(f"    - {type_name}: {count} ({count/pass_stats['total']*100:.1f}%)")
    
    print(f"\n  Difficulties:")
    for diff, count in sorted(pass_stats['difficulties'].items()):
        print(f"    - Level {diff}: {count} ({count/pass_stats['total']*100:.1f}%)")
    
    print(f"\n  Topics (Top 10):")
    for topic, count in sorted(pass_stats['topics'].items(), key=lambda x: -x[1])[:10]:
        print(f"    - {topic}: {count}")
    
    print(f"\n  Average answer length: {pass_stats['avg_answer_length']:.1f} characters")
    
    # 找出最好的问题
    print(f"\nTop 10 Best Questions:")
    best_questions = find_best_questions(pass_q, top_n=10)
    for i, q in enumerate(best_questions, 1):
        title = q.get('question_text', 'N/A')[:80]
        difficulty = q.get('difficulty', 0)
        length = q.get('metadata', {}).get('answer_length', 0)
        print(f"\n  {i}. [Level {difficulty}] {title}...")
        print(f"     Answer length: {length} chars")
        print(f"     Type: {q.get('type', 'N/A')}")
        print(f"     Source: {q.get('source', {}).get('paper_title', 'N/A')[:60]}")
    
    print("\n" + "=" * 80)


def export_sample_questions(output_file: str = "sample_questions.json"):
    """导出样本问题"""
    pass_q, _ = load_all_questions()
    
    # 每种类型导出2个最好的
    samples = {}
    for q_type in ['reasoning', 'calculation', 'concept']:
        type_questions = [q for q in pass_q if q.get('type') == q_type]
        best = find_best_questions(type_questions, top_n=2)
        samples[q_type] = best
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)
    
    print(f"Sample questions exported to: {output_file}")


def search_by_keyword(keyword: str, max_results: int = 5):
    """按关键词搜索问题"""
    pass_q, _ = load_all_questions()
    
    results = []
    for q in pass_q:
        question_text = q.get('question_text', '').lower()
        answer_text = q.get('standard_answer', '').lower()
        
        if keyword.lower() in question_text or keyword.lower() in answer_text:
            results.append(q)
    
    print(f"\nSearch results for '{keyword}': {len(results)} found")
    for i, q in enumerate(results[:max_results], 1):
        print(f"\n  {i}. {q.get('question_text', 'N/A')[:100]}...")
        print(f"     Source: {q.get('source', {}).get('paper_title', 'N/A')[:60]}")


if __name__ == "__main__":
    # 生成统计报告
    generate_statistics_report()
    
    # 导出样本
    print("\nExporting sample questions...")
    export_sample_questions()
    
    # 示例搜索
    print("\n" + "=" * 80)
    search_by_keyword("combustion", max_results=3)
    search_by_keyword("CFD", max_results=3)
    search_by_keyword("heat transfer", max_results=3)
