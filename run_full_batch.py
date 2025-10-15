#!/usr/bin/env python3
"""
批量处理所有298个txt文件
生成 298 × 5 = 1490 道详细问题
无质量检查，全速运行
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
    print("BATCH DETAIL Q GENERATOR - FULL RUN")
    print("=" * 80)
    print(f"Input folder: compliant/")
    print(f"Output folder: questions/")
    print(f"Model: openai/deepseek-ai/DeepSeek-V3")
    print(f"Concurrency: 20 files in parallel")
    print(f"Rate limits: RPM=30,000 | TPM=5,000,000")
    print(f"Mode: Fast (No quality check)")
    print("=" * 80)
    print(f"Expected output: ~298 files × 5 questions = 1,490 questions")
    print(f"Estimated time: ~2-3 hours")
    print("=" * 80)
    
    confirm = input("\nStart processing all 298 files? (yes/no): ").strip().lower()
    
    if confirm not in ['yes', 'y']:
        print("Cancelled.")
        return
    
    print("\nStarting batch processing...\n")
    
    # 创建处理器并运行
    processor = DetailQBatchProcessor("compliant", "questions")
    processor.process_all_files()
    
    print("\n" + "=" * 80)
    print("BATCH PROCESSING COMPLETED!")
    print("=" * 80)
    print("Check the 'questions/' folder for results.")
    print("Summary report: questions/BATCH_SUMMARY.md")
    print("=" * 80)


if __name__ == "__main__":
    main()
