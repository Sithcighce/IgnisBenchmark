#!/usr/bin/env python3
"""
批量处理所有298个txt文件 - 直接运行版本
生成 298 × 5 = 1490 道详细问题
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
    print("BATCH DETAIL Q GENERATOR - AUTO RUN")
    print("=" * 80)
    print(f"Processing ~298 txt files from compliant/")
    print(f"Expected output: 1,490 questions (298 × 5)")
    print(f"Estimated time: 2-3 hours")
    print("=" * 80)
    print("\nStarting...\n")
    
    # 直接运行
    processor = DetailQBatchProcessor("compliant", "questions")
    processor.process_all_files()
    
    print("\n" + "=" * 80)
    print("COMPLETED!")
    print("=" * 80)
    print(f"Check: questions/BATCH_SUMMARY.md")
    print("=" * 80)


if __name__ == "__main__":
    main()
