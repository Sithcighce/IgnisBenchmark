#!/usr/bin/env python3
"""
批处理进度监控脚本
实时查看处理进度和统计
"""

import os
from pathlib import Path
import json
import time

def monitor_progress():
    """监控批处理进度"""
    questions_dir = Path("questions")
    
    if not questions_dir.exists():
        print("questions/ folder not found. Processing hasn't started yet.")
        return
    
    # 统计文件夹数量
    completed_folders = [d for d in questions_dir.iterdir() if d.is_dir()]
    total_questions = 0
    passed_questions = 0
    failed_questions = 0
    
    for folder in completed_folders:
        pass_file = folder / "pass.json"
        fail_file = folder / "not_pass.json"
        
        if pass_file.exists():
            with open(pass_file, 'r', encoding='utf-8') as f:
                passed = json.load(f)
                passed_questions += len(passed)
                total_questions += len(passed)
        
        if fail_file.exists():
            with open(fail_file, 'r', encoding='utf-8') as f:
                failed = json.load(f)
                failed_questions += len(failed)
                total_questions += len(failed)
    
    # 显示进度
    total_files = 298
    completed = len(completed_folders)
    progress = (completed / total_files) * 100 if total_files > 0 else 0
    
    print("=" * 80)
    print("BATCH PROCESSING PROGRESS")
    print("=" * 80)
    print(f"Files processed: {completed}/{total_files} ({progress:.1f}%)")
    print(f"Total questions: {total_questions}")
    print(f"  - Passed quality check: {passed_questions} ({passed_questions/max(1,total_questions)*100:.1f}%)")
    print(f"  - Failed quality check: {failed_questions} ({failed_questions/max(1,total_questions)*100:.1f}%)")
    print("=" * 80)
    
    if completed < total_files:
        print(f"\nEstimated remaining: ~{(total_files - completed) * 1.5:.0f} minutes")
        print("(Assuming ~1.5 min per file)")
    else:
        print("\nProcessing completed!")
        print(f"Check: questions/BATCH_SUMMARY.md")
    
    print("=" * 80)
    
    # 显示最近完成的5个文件
    if completed > 0:
        recent_folders = sorted(completed_folders, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
        print("\nRecently completed files:")
        for folder in recent_folders:
            pass_count = 0
            fail_count = 0
            if (folder / "pass.json").exists():
                with open(folder / "pass.json", 'r') as f:
                    pass_count = len(json.load(f))
            if (folder / "not_pass.json").exists():
                with open(folder / "not_pass.json", 'r') as f:
                    fail_count = len(json.load(f))
            print(f"  - {folder.name}: {pass_count} passed, {fail_count} failed")


def main():
    """主函数"""
    print("\nMonitoring batch processing...\n")
    monitor_progress()


if __name__ == "__main__":
    main()
