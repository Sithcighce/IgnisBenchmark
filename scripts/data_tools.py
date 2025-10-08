#!/usr/bin/env python3
"""
数据分析和批量处理工具
"""
import os
import sys
import json
import datetime
from pathlib import Path
from collections import defaultdict

def analyze_benchmark_data():
    """分析benchmark数据"""
    print("📊 分析Benchmark数据...")
    
    file_path = Path("data/benchmark_bank.jsonl")
    if not file_path.exists():
        print("❌ benchmark_bank.jsonl 文件不存在")
        return
    
    questions = []
    topics = defaultdict(int)
    difficulties = defaultdict(int)
    types = defaultdict(int)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            try:
                data = json.loads(line)
                questions.append(data)
                
                # 统计主题、难度、类型
                if 'topic' in data:
                    topics[data['topic']] += 1
                if 'difficulty' in data:
                    difficulties[data['difficulty']] += 1
                if 'type' in data:
                    types[data['type']] += 1
                    
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON解析错误: {e}")
    
    print(f"\n📈 数据统计:")
    print(f"  总题目数: {len(questions)}")
    
    print(f"\n🏷️ 主题分布:")
    for topic, count in sorted(topics.items()):
        print(f"  {topic}: {count}")
    
    print(f"\n⭐ 难度分布:")
    for difficulty, count in sorted(difficulties.items()):
        print(f"  难度{difficulty}: {count}")
    
    print(f"\n📋 类型分布:")
    for type_name, count in sorted(types.items()):
        print(f"  {type_name}: {count}")

def clean_failed_attempts():
    """清理失败的判题记录"""
    print("\n🧹 清理失败的判题记录...")
    
    file_path = Path("data/benchmark_bank.jsonl")
    if not file_path.exists():
        print("❌ benchmark_bank.jsonl 文件不存在")
        return
    
    backup_path = Path(f"data/benchmark_bank_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl")
    
    # 备份原文件
    print(f"💾 创建备份: {backup_path}")
    
    cleaned_lines = []
    removed_count = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            try:
                data = json.loads(line)
                
                # 检查是否有失败的判题记录
                if 'failed_attempt' in data:
                    grading_result = data.get('failed_attempt', {}).get('grading_result', {})
                    reasoning = grading_result.get('reasoning', '')
                    
                    if "判题系统错误: JSON解析失败" in reasoning or "cannot schedule new futures after shutdown" in reasoning:
                        print(f"🗑️ 移除失败记录: {data.get('question_data', {}).get('question_id', 'unknown')[:8]}...")
                        removed_count += 1
                        continue
                
                cleaned_lines.append(line)
                
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON解析错误，跳过该行: {e}")
                removed_count += 1
    
    if removed_count > 0:
        # 创建备份
        with open(file_path, 'r', encoding='utf-8') as src:
            with open(backup_path, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        
        # 写入清理后的数据
        with open(file_path, 'w', encoding='utf-8') as f:
            for line in cleaned_lines:
                f.write(line + '\n')
        
        print(f"✅ 已移除 {removed_count} 个失败记录")
        print(f"📁 备份文件: {backup_path}")
    else:
        print("✅ 未发现需要清理的失败记录")

def export_statistics():
    """导出统计信息"""
    print("\n📋 导出统计信息...")
    
    stats = {
        'generated_at': datetime.datetime.now().isoformat(),
        'files': {}
    }
    
    # 统计各个数据文件
    data_files = [
        'data/benchmark_bank.jsonl',
        'data/seed_examples.jsonl', 
        'data/validation_set.jsonl'
    ]
    
    for file_path in data_files:
        path = Path(file_path)
        if path.exists():
            line_count = 0
            valid_count = 0
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        line_count += 1
                        try:
                            json.loads(line)
                            valid_count += 1
                        except:
                            pass
            
            stats['files'][file_path] = {
                'exists': True,
                'total_lines': line_count,
                'valid_lines': valid_count,
                'size_bytes': path.stat().st_size
            }
        else:
            stats['files'][file_path] = {'exists': False}
    
    # 写入统计文件
    stats_file = Path("logs/data_statistics.json")
    stats_file.parent.mkdir(exist_ok=True)
    
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print(f"📊 统计信息已导出到: {stats_file}")

def main():
    """主函数"""
    # 确保在正确的工作目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    os.chdir(project_dir)
    
    print("🔧 数据分析和批量处理工具")
    print("=" * 50)
    
    analyze_benchmark_data()
    clean_failed_attempts()
    export_statistics()
    
    print("\n✅ 处理完成!")

if __name__ == "__main__":
    main()