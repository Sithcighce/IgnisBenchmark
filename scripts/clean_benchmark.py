#!/usr/bin/env python3
"""
从benchmark中清理判题系统错误的脚本
"""
import os
import sys
import json
import datetime
from pathlib import Path

def main():
    """主函数"""
    # 确保在正确的工作目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    os.chdir(project_dir)
    
    benchmark_file = Path("data/benchmark_bank.jsonl")
    if not benchmark_file.exists():
        print("❌ benchmark_bank.jsonl 文件不存在")
        return 1
    
    print("🧹 开始清理benchmark中的判题系统错误记录...")
    
    # 创建备份
    backup_file = Path(f"data/benchmark_bank_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl")
    print(f"💾 创建备份文件: {backup_file}")
    
    # 读取并分析数据
    clean_records = []
    error_records = []
    total_records = 0
    
    with open(benchmark_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            total_records += 1
            
            try:
                data = json.loads(line)
                
                # 检查是否包含判题系统错误
                is_grading_error = False
                
                # 检查failed_attempt中的grading_result
                if 'failed_attempt' in data:
                    failed_attempt = data['failed_attempt']
                    if 'grading_result' in failed_attempt:
                        grading_result = failed_attempt['grading_result']
                        reasoning = grading_result.get('reasoning', '')
                        
                        # 判断是否为判题系统错误
                        if any(keyword in reasoning for keyword in [
                            "判题系统错误",
                            "JSON解析失败",
                            "cannot schedule new futures after shutdown",
                            "重试"
                        ]):
                            is_grading_error = True
                            print(f"🗑️ 发现判题系统错误记录 (第{line_num}行): {reasoning[:50]}...")
                
                if is_grading_error:
                    error_records.append(data)
                else:
                    clean_records.append(line)
                    
            except json.JSONDecodeError as e:
                print(f"⚠️ 第{line_num}行JSON解析错误: {e}")
                # 损坏的JSON也算作错误记录
                error_records.append({"line": line, "error": str(e)})
    
    print(f"📊 分析完成:")
    print(f"  总记录数: {total_records}")
    print(f"  正常记录: {len(clean_records)}")
    print(f"  错误记录: {len(error_records)}")
    
    if len(error_records) > 0:
        # 创建备份
        with open(benchmark_file, 'r', encoding='utf-8') as src:
            with open(backup_file, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        
        # 写入清理后的数据
        with open(benchmark_file, 'w', encoding='utf-8') as f:
            for line in clean_records:
                f.write(line + '\n')
        
        # 保存错误记录到独立文件
        error_file = Path("data/removed_grading_errors.jsonl")
        with open(error_file, 'w', encoding='utf-8') as f:
            for error_record in error_records:
                if isinstance(error_record, dict):
                    json_str = json.dumps(error_record, ensure_ascii=False)
                    f.write(json_str + '\n')
        
        print(f"✅ 已从benchmark中移除 {len(error_records)} 个错误记录")
        print(f"📁 备份文件: {backup_file}")
        print(f"📁 错误记录文件: {error_file}")
    else:
        print("✅ 未发现需要清理的判题系统错误记录")
    
    return 0

if __name__ == "__main__":
    exit(main())