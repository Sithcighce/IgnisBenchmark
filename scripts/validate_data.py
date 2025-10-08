#!/usr/bin/env python3
"""
数据验证和清理脚本
"""
import os
import sys
import json
from pathlib import Path

def validate_jsonl_file(file_path):
    """验证JSONL文件格式"""
    print(f"📁 验证文件: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    valid_lines = 0
    invalid_lines = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
                
            try:
                json.loads(line)
                valid_lines += 1
            except json.JSONDecodeError as e:
                print(f"❌ 第{line_num}行JSON格式错误: {e}")
                print(f"   内容: {line[:100]}...")
                invalid_lines += 1
    
    print(f"✅ 有效行数: {valid_lines}")
    print(f"❌ 无效行数: {invalid_lines}")
    return invalid_lines == 0

def clean_benchmark_data():
    """清理benchmark数据文件"""
    data_dir = Path("data")
    
    print("🧹 开始清理数据文件...")
    
    # 验证主要数据文件
    files_to_check = [
        data_dir / "benchmark_bank.jsonl",
        data_dir / "seed_examples.jsonl", 
        data_dir / "validation_set.jsonl"
    ]
    
    all_valid = True
    for file_path in files_to_check:
        if file_path.exists():
            is_valid = validate_jsonl_file(file_path)
            all_valid = all_valid and is_valid
        else:
            print(f"⚠️ 文件不存在: {file_path}")
    
    return all_valid

def main():
    """主函数"""
    # 确保在正确的工作目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    os.chdir(project_dir)
    
    print("🔍 开始数据验证和清理...")
    
    # 清理数据
    success = clean_benchmark_data()
    
    if success:
        print("✅ 所有数据文件验证通过")
        return 0
    else:
        print("❌ 发现数据文件错误，请检查上述输出")
        return 1

if __name__ == "__main__":
    exit(main())