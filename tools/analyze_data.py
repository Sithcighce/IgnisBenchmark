"""
数据分析工具 - 分析错题库和验证集的统计信息
"""
import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Any

# 添加src到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

import yaml


def analyze_benchmark(benchmark_path: Path) -> Dict[str, Any]:
    """分析错题库"""
    
    if not benchmark_path.exists():
        return {"error": "错题库文件不存在"}
    
    entries = []
    with open(benchmark_path, 'r', encoding='utf-8') as f:
        line_num = 0
        for line in f:
            line_num += 1
            if line.strip():
                try:
                    entry_dict = json.loads(line)
                    entries.append(entry_dict)
                except json.JSONDecodeError as e:
                    print(f"警告: 第{line_num}行JSON解析错误: {e}")
                    print(f"内容: {line[:100]}...")
                    continue
    
    if not entries:
        return {"count": 0, "message": "错题库为空"}
    
    # 统计信息
    stats = {
        "total_count": len(entries),
        "topics": Counter(),
        "difficulties": Counter(),
        "types": Counter(),
        "error_patterns": defaultdict(int),
        "avg_attempts": 0
    }
    
    for entry in entries:
        # 兼容两种格式：简单QuestionUnit或完整BenchmarkEntry
        if "question_data" in entry:
            q = entry["question_data"]
        else:
            q = entry
        
        # 主题统计
        topic = q.get("topic", "Unknown")
        stats["topics"][topic] += 1
        
        # 难度统计
        difficulty = q.get("difficulty", 0)
        stats["difficulties"][difficulty] += 1
        
        # 类型统计
        qtype = q.get("type", "Unknown")
        stats["types"][qtype] += 1
    
    # 转换Counter为普通字典
    stats["topics"] = dict(stats["topics"])
    stats["difficulties"] = dict(stats["difficulties"])
    stats["types"] = dict(stats["types"])
    
    return stats


def analyze_validation(validation_path: Path) -> Dict[str, Any]:
    """分析验证集"""
    
    if not validation_path.exists():
        return {"error": "验证集文件不存在"}
    
    questions = []
    with open(validation_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                q_dict = json.loads(line)
                questions.append(q_dict)
    
    if not questions:
        return {"count": 0, "message": "验证集为空"}
    
    # 统计信息
    stats = {
        "total_count": len(questions),
        "topics": Counter(),
        "difficulties": Counter(),
        "types": Counter(),
        "avg_difficulty": 0
    }
    
    total_difficulty = 0
    
    for q in questions:
        # 主题统计
        topic = q.get("topic", "Unknown")
        stats["topics"][topic] += 1
        
        # 难度统计
        difficulty = q.get("difficulty", 0)
        stats["difficulties"][difficulty] += 1
        total_difficulty += difficulty
        
        # 类型统计
        qtype = q.get("type", "Unknown")
        stats["types"][qtype] += 1
    
    stats["avg_difficulty"] = total_difficulty / len(questions) if questions else 0
    
    # 转换Counter为普通字典
    stats["topics"] = dict(stats["topics"])
    stats["difficulties"] = dict(stats["difficulties"])
    stats["types"] = dict(stats["types"])
    
    return stats


def print_report(benchmark_stats: Dict, validation_stats: Dict):
    """打印分析报告"""
    
    print("\n" + "="*70)
    print(" "*20 + "数据分析报告")
    print("="*70)
    
    # 错题库分析
    print("\n【错题库分析】")
    print("-"*70)
    
    if "error" in benchmark_stats:
        print(f"  {benchmark_stats['error']}")
    elif benchmark_stats.get("count") == 0:
        print(f"  {benchmark_stats.get('message', '无数据')}")
    else:
        print(f"  总题目数: {benchmark_stats['total_count']}")
        
        print(f"\n  主题分布:")
        for topic, count in sorted(benchmark_stats["topics"].items(), key=lambda x: -x[1]):
            percentage = (count / benchmark_stats['total_count']) * 100
            print(f"    {topic}: {count} ({percentage:.1f}%)")
        
        print(f"\n  难度分布:")
        for difficulty in sorted(benchmark_stats["difficulties"].keys()):
            count = benchmark_stats["difficulties"][difficulty]
            percentage = (count / benchmark_stats['total_count']) * 100
            print(f"    难度 {difficulty}: {count} ({percentage:.1f}%)")
        
        print(f"\n  类型分布:")
        for qtype, count in sorted(benchmark_stats["types"].items(), key=lambda x: -x[1]):
            percentage = (count / benchmark_stats['total_count']) * 100
            print(f"    {qtype}: {count} ({percentage:.1f}%)")
    
    # 验证集分析
    print("\n【验证集分析】")
    print("-"*70)
    
    if "error" in validation_stats:
        print(f"  {validation_stats['error']}")
    elif validation_stats.get("count") == 0:
        print(f"  {validation_stats.get('message', '无数据')}")
    else:
        print(f"  总题目数: {validation_stats['total_count']}")
        print(f"  平均难度: {validation_stats['avg_difficulty']:.2f}")
        
        print(f"\n  主题分布:")
        for topic, count in sorted(validation_stats["topics"].items(), key=lambda x: -x[1]):
            percentage = (count / validation_stats['total_count']) * 100
            print(f"    {topic}: {count} ({percentage:.1f}%)")
        
        print(f"\n  难度分布:")
        for difficulty in sorted(validation_stats["difficulties"].keys()):
            count = validation_stats["difficulties"][difficulty]
            percentage = (count / validation_stats['total_count']) * 100
            print(f"    难度 {difficulty}: {count} ({percentage:.1f}%)")
        
        print(f"\n  类型分布:")
        for qtype, count in sorted(validation_stats["types"].items(), key=lambda x: -x[1]):
            percentage = (count / validation_stats['total_count']) * 100
            print(f"    {qtype}: {count} ({percentage:.1f}%)")
    
    # 总体统计
    print("\n【总体统计】")
    print("-"*70)
    
    total_benchmark = benchmark_stats.get("total_count", 0)
    total_validation = validation_stats.get("total_count", 0)
    total = total_benchmark + total_validation
    
    if total > 0:
        print(f"  总题库规模: {total}")
        print(f"  错题库: {total_benchmark} ({(total_benchmark/total)*100:.1f}%)")
        print(f"  验证集: {total_validation} ({(total_validation/total)*100:.1f}%)")
        
        if total_benchmark > 0 and total_validation > 0:
            ratio = total_benchmark / total_validation
            print(f"  错题/验证比: {ratio:.2f}")
    else:
        print(f"  暂无数据")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    # 加载配置
    config_path = project_root / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    benchmark_path = project_root / config["benchmark_bank_path"]
    validation_path = project_root / config["validation_set_path"]
    
    # 分析两个数据集
    print("\n正在分析数据...")
    benchmark_stats = analyze_benchmark(benchmark_path)
    validation_stats = analyze_validation(validation_path)
    
    # 打印报告
    print_report(benchmark_stats, validation_stats)
