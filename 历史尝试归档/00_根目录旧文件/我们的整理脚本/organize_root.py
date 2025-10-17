#!/usr/bin/env python3
"""
整理根目录 - 将已归档的文件移动到归档目录
"""

import os
import shutil
from pathlib import Path

# 定义要移动的文件（这些已经在归档中了）
FILES_TO_MOVE = {
    "旧脚本": [
        "milestone1_generator.py",
        "milestone1_compare_generator.py",
        "milestone1_withtext_generator.py",
        "milestone1_detail_Q_generator.py",
        "milestone1_insights_generator.py",
        "milestone1_insights_pro_generator.py",
        "deepseek_english_generator.py",
        "deepseek_intelligent_generator.py",
        "batch_detail_q_generator.py",
        "create_final_benchmark.py",
        "analyze_api_failures.py",
    ],
    "旧文档": [
        "MILESTONE1_DELIVERY.md",
        "MILESTONE1_COMPARE_SUMMARY.md",
        "MILESTONE1_WITHTEXT_DELIVERY.md",
        "MILESTONE1_DETAIL_INSIGHTS_DELIVERY.md",
        "MILESTONE1_INSIGHTS_PRO_DELIVERY.md",
        "BATCH_DETAIL_Q_README.md",
        "WITHTEXT_STATUS.md",
        "FINAL_COMPLETION_REPORT.md",
        "COMPARISON.md",
    ],
    "旧日志": [
        "milestone1_withtext.log",
        "milestone1_withtext_run.log",
    ],
    "旧生成数据": [
        # questions目录已经合并到question_all
        # 保留question_all作为主数据集
    ],
    "辅助脚本": [
        "archive_history.py",  # 旧版归档脚本
        "batch_auto_run.py",
        "batch_restart.py",
        "monitor_batch.py",
        "run_batch_detail_q.py",
        "run_full_batch.py",
        "test_batch_2files.py",
        "consolidate_and_complete.py",
        "extract_questions_to_md.py",
        "analyze_questions.py",
    ]
}

# 保留在根目录的重要文件
KEEP_IN_ROOT = [
    # 核心项目文件
    "README.md",
    "PROJECT_COMPLETION_SUMMARY.md",
    "PROJECT_STATUS.md",
    "requirements.txt",
    "config.yaml",
    ".gitignore",
    ".env.example",
    
    # 核心目录
    "src/",
    "scripts/",
    "prompts/",
    "docs/",
    "data/",
    "logs/",
    "compliant/",
    
    # 最终交付
    "最终交付/",
    "验证/",
    "历史尝试归档/",
    
    # 主数据集
    "question_all/",
    "question_all_md/",
    
    # 当前工作脚本（如果还在用）
    "main.py",
    "run.py",
    "app_international.py",
    
    # 新的归档脚本
    "archive_history_complete.py",
]

def create_archive_folder(name):
    """创建归档子文件夹"""
    folder = Path("历史尝试归档") / "00_根目录旧文件" / name
    os.makedirs(folder, exist_ok=True)
    return folder

def move_files():
    """移动文件到归档"""
    print('🗂️  整理根目录...\n')
    
    moved_count = 0
    skipped_count = 0
    
    for category, files in FILES_TO_MOVE.items():
        if not files:
            continue
            
        print(f'📁 {category}:')
        archive_folder = create_archive_folder(category)
        
        for file in files:
            if os.path.exists(file):
                try:
                    dst = archive_folder / os.path.basename(file)
                    shutil.move(file, str(dst))
                    print(f'   ✅ {file} → 归档/{category}/')
                    moved_count += 1
                except Exception as e:
                    print(f'   ⚠️  {file}: {e}')
                    skipped_count += 1
            else:
                print(f'   ⏭️  {file} (不存在)')
                skipped_count += 1
        print()
    
    # 创建README说明这些文件
    readme_content = """# 根目录旧文件归档

这个目录保存了项目开发过程中在根目录产生的旧文件。

## 为什么移动这些文件？

这些文件已经被整理到对应的历史阶段目录中了，为了保持根目录整洁，移动到这里归档。

## 目录说明

- **旧脚本/**: 各阶段的生成器脚本
- **旧文档/**: 各阶段的交付文档
- **旧日志/**: 运行日志文件
- **辅助脚本/**: 辅助工具脚本

## 注意

这些文件在对应的历史阶段目录中也有副本，这里只是额外的备份。

如果需要查看某个阶段的完整文件，请访问：
- 历史尝试归档/01_第一次尝试_基础生成/
- 历史尝试归档/02_第二次尝试_对比生成/
- ... 等等
"""
    
    readme_path = Path("历史尝试归档") / "00_根目录旧文件" / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print('✨ 整理完成！\n')
    print(f'📊 统计:')
    print(f'   移动文件数: {moved_count}')
    print(f'   跳过文件数: {skipped_count}')
    print(f'   归档位置: 历史尝试归档/00_根目录旧文件/\n')
    
    # 显示根目录现在的状态
    print('📁 根目录当前保留的重要文件和目录:')
    important_items = []
    for item in os.listdir('.'):
        if item in ['.git', '__pycache__', '.env', 'backup']:
            continue
        if any(item.startswith(keep.rstrip('/')) for keep in KEEP_IN_ROOT):
            important_items.append(item)
    
    for item in sorted(important_items):
        if os.path.isdir(item):
            print(f'   📂 {item}/')
        else:
            print(f'   📄 {item}')

if __name__ == '__main__':
    print('=' * 80)
    print('整理根目录 - 移动已归档文件')
    print('=' * 80)
    print()
    
    move_files()
    
    print('\n' + '=' * 80)
    print('✅ 整理完成！根目录现在更整洁了')
    print('=' * 80)
