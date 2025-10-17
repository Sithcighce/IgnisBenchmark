#!/usr/bin/env python3
"""
快速启动批量处理
直接处理compliant文件夹中的所有txt文件
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from batch_detail_q_generator import DetailQBatchProcessor
from src.utils import setup_logging, load_env_variables

def main():
    """直接启动批量处理"""
    setup_logging()
    load_env_variables()
    
    # 固定路径
    input_dir = "compliant"
    output_dir = "questions"
    
    print("=" * 80)
    print("📚 Batch Detail Q Generator")
    print("=" * 80)
    print(f"Input folder: {input_dir}")
    print(f"Output folder: {output_dir}")
    print(f"Model: openai/deepseek-ai/DeepSeek-V3")
    print(f"Concurrency: 20 files in parallel")
    print(f"Rate limits: RPM=30,000 | TPM=5,000,000")
    print("=" * 80)
    
    confirm = input("\nReady to start? This will process ~298 txt files. (yes/no): ").strip().lower()
    
    if confirm not in ['yes', 'y']:
        print("Cancelled.")
        return
    
    print("\n🚀 Starting batch processing...\n")
    
    # 创建处理器并运行
    processor = DetailQBatchProcessor(input_dir, output_dir)
    processor.process_all_files()
    
    print("\n✅ All done! Check the 'questions/' folder for results.")
    print("📊 Summary report: questions/BATCH_SUMMARY.md")


if __name__ == "__main__":
    main()
