#!/usr/bin/env python3
"""
整理旧的questions目录 - 这些都是早期生成数据，已经合并到question_all
"""

import os
import shutil
from pathlib import Path

# 要移动的旧问题目录
OLD_QUESTION_DIRS = [
    "questions",  # 第一批
    "questions copy",  # 第三批（副本）
    "questions_test",  # 测试
    "question_english",  # 英文版
    "question_english copy",  # 英文版副本
    "question_reverse",  # 倒序生成
]

def move_old_question_dirs():
    """移动旧的questions目录到归档"""
    archive_folder = Path("历史尝试归档") / "00_根目录旧文件" / "旧生成数据"
    os.makedirs(archive_folder, exist_ok=True)
    
    print('🗂️  整理旧的questions目录...\n')
    
    moved = []
    skipped = []
    
    for dirname in OLD_QUESTION_DIRS:
        if os.path.exists(dirname):
            try:
                dst = archive_folder / dirname
                print(f'📁 移动 {dirname}/ ...')
                
                # 检查大小
                if os.path.isdir(dirname):
                    file_count = sum(1 for _ in Path(dirname).rglob('*') if _.is_file())
                    print(f'   包含 {file_count} 个文件')
                
                shutil.move(dirname, str(dst))
                print(f'   ✅ {dirname}/ → 归档/旧生成数据/\n')
                moved.append(dirname)
            except Exception as e:
                print(f'   ⚠️  错误: {e}\n')
                skipped.append(dirname)
        else:
            print(f'⏭️  {dirname}/ (不存在)\n')
            skipped.append(dirname)
    
    # 更新README
    readme_path = archive_folder.parent / "README.md"
    with open(readme_path, 'a', encoding='utf-8') as f:
        f.write("""

## 旧生成数据说明

这些目录包含早期生成的题目数据，已经全部合并到 `question_all/` 和 `question_all_md/`。

### 目录说明
- **questions/**: 第一批生成（SiliconFlow API）
- **question_reverse/**: 倒序生成批次
- **questions copy/**: 第三批补全
- **question_english/**: 英文版生成尝试
- **question_english copy/**: 英文版副本
- **questions_test/**: 测试数据

### 当前主数据集
所有数据已经整理到：
- `question_all/`: JSON格式，按论文组织
- `question_all_md/`: Markdown格式，便于阅读

这些旧目录仅作备份保留。
""")
    
    print('✨ 整理完成！\n')
    print(f'📊 统计:')
    print(f'   移动目录数: {len(moved)}')
    print(f'   跳过目录数: {len(skipped)}')
    print(f'   归档位置: 历史尝试归档/00_根目录旧文件/旧生成数据/\n')
    
    if moved:
        print('✅ 已移动的目录:')
        for d in moved:
            print(f'   - {d}/')

if __name__ == '__main__':
    print('=' * 80)
    print('整理旧questions目录')
    print('=' * 80)
    print()
    
    # 先确认
    print('⚠️  这将移动以下目录到归档:')
    for d in OLD_QUESTION_DIRS:
        if os.path.exists(d):
            print(f'   📁 {d}/')
    print()
    
    response = input('是否继续？ (yes/no): ')
    if response.lower() in ['yes', 'y']:
        print()
        move_old_question_dirs()
        
        print('\n' + '=' * 80)
        print('✅ 整理完成！')
        print('=' * 80)
        print('\n💡 提示: 所有数据已在 question_all/ 和 question_all_md/ 中')
    else:
        print('❌ 取消操作')
