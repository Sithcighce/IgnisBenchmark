#!/usr/bin/env python3
"""
测试批量处理 - 只处理前2个文件
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from batch_detail_q_generator import DetailQBatchProcessor
from src.utils import setup_logging, load_env_variables

def main():
    setup_logging()
    load_env_variables()
    
    print("=" * 80)
    print("Test Batch Detail Q Generator (2 files only)")
    print("=" * 80)
    
    # 创建处理器
    processor = DetailQBatchProcessor("compliant", "questions_test")
    
    # 只处理前2个文件
    txt_files = processor.find_txt_files()[:2]
    print(f"Testing with {len(txt_files)} files:")
    for f in txt_files:
        print(f"  - {f.name}")
    
    print("\nStarting test...\n")
    
    # 手动处理这2个文件
    results = []
    for txt_file in txt_files:
        result = processor.process_single_file(txt_file)
        results.append(result)
        print(f"\nDone: {txt_file.stem}: {result['status']}")
        if result['status'] == 'success':
            print(f"  Passed: {result['passed']}/5")
            print(f"  Failed: {result['failed']}/5")
    
    # 生成报告
    processor.stats["total_files"] = len(txt_files)
    processor.stats["completed"] = sum(1 for r in results if r['status'] == 'success')
    processor.stats["failed"] = sum(1 for r in results if r['status'] != 'success')
    processor.stats["total_questions"] = sum(r.get('total_questions', 0) for r in results)
    processor.stats["passed_questions"] = sum(r.get('passed', 0) for r in results)
    processor.stats["failed_questions"] = sum(r.get('failed', 0) for r in results)
    
    processor.generate_summary_report(results)
    
    print("\nTest complete! Check 'questions_test/' folder.")


if __name__ == "__main__":
    main()
