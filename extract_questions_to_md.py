#!/usr/bin/env python3
"""
从question_all的JSON提取为人类可读的Markdown
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)


def format_question_md(question: Dict, index: int) -> str:
    """格式化单个问题为Markdown"""
    md = f"""## Question {index}

### 问题

{question.get('question_text', 'N/A')}

### 标准答案

{question.get('standard_answer', 'N/A')}

### 元数据

- **类型**: {question.get('type', 'N/A')}
- **难度**: {question.get('difficulty', 'N/A')}
- **主题**: {question.get('topic', 'N/A')}
- **答案长度**: {question.get('metadata', {}).get('answer_length', 'N/A')} 字符

"""
    
    # 原文引用
    original_text = question.get('original_text', {})
    if original_text:
        md += "### 原文引用\n\n"
        for key, value in original_text.items():
            md += f"**引用 {key}**:\n> {value}\n\n"
    
    # 质量检查结果
    quality_check = question.get('quality_check', {})
    if quality_check:
        md += "### 质量检查\n\n"
        md += f"- **领域聚焦**: {'✅ 通过' if quality_check.get('domain_focused') else '❌ 未通过'}\n"
        md += f"- **答案正确性**: {'✅ 通过' if quality_check.get('answer_correct') else '❌ 未通过'}\n"
        md += f"- **其他合规性**: {'✅ 通过' if quality_check.get('other_compliant') else '❌ 未通过'}\n"
        md += f"- **总体评价**: {quality_check.get('overall_verdict', 'N/A')}\n\n"
        
        if quality_check.get('domain_reasoning'):
            md += f"**领域聚焦分析**: {quality_check.get('domain_reasoning')}\n\n"
        
        if quality_check.get('answer_issues'):
            md += f"**答案问题**: {', '.join(quality_check.get('answer_issues'))}\n\n"
        
        if quality_check.get('recommendation'):
            md += f"**改进建议**: {quality_check.get('recommendation')}\n\n"
    
    # 来源信息
    source = question.get('source', {})
    if source:
        md += "### 来源\n\n"
        md += f"- **论文**: {source.get('paper_title', 'N/A')}\n"
        md += f"- **生成类型**: {source.get('type', 'N/A')}\n"
    
    merge_source = question.get('merge_source')
    if merge_source:
        md += f"- **合并来源**: {merge_source}\n"
    
    md += "\n---\n\n"
    
    return md


def extract_single_file(folder: Path):
    """提取单个文件夹的问题为MD"""
    filename = folder.name
    
    # 读取pass.json
    pass_questions = []
    pass_file = folder / "pass.json"
    if pass_file.exists():
        try:
            with open(pass_file, 'r', encoding='utf-8') as f:
                pass_questions = json.load(f)
        except Exception as e:
            logger.error(f"Error reading {pass_file}: {e}")
    
    # 读取not_pass.json
    notpass_questions = []
    notpass_file = folder / "not_pass.json"
    if notpass_file.exists():
        try:
            with open(notpass_file, 'r', encoding='utf-8') as f:
                notpass_questions = json.load(f)
        except Exception as e:
            logger.error(f"Error reading {notpass_file}: {e}")
    
    # 创建输出目录
    output_dir = Path("question_all_md")
    output_dir.mkdir(exist_ok=True)
    
    # 生成pass.md
    if pass_questions:
        pass_md_file = output_dir / f"{filename}.md"
        with open(pass_md_file, 'w', encoding='utf-8') as f:
            f.write(f"""# {filename} - Passed Questions

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**通过问题数**: {len(pass_questions)}

---

""")
            
            for i, question in enumerate(pass_questions, 1):
                f.write(format_question_md(question, i))
        
        logger.info(f"[{filename}] Exported {len(pass_questions)} passed questions to {pass_md_file.name}")
    
    # 生成notpass.md
    if notpass_questions:
        notpass_md_file = output_dir / f"{filename}_notpass.md"
        with open(notpass_md_file, 'w', encoding='utf-8') as f:
            f.write(f"""# {filename} - Not Passed Questions

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**未通过问题数**: {len(notpass_questions)}

---

""")
            
            for i, question in enumerate(notpass_questions, 1):
                f.write(format_question_md(question, i))
        
        logger.info(f"[{filename}] Exported {len(notpass_questions)} not-passed questions to {notpass_md_file.name}")


def main():
    """主函数"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 80)
    print("Extracting Questions to Markdown")
    print("=" * 80)
    
    question_all_dir = Path("question_all")
    if not question_all_dir.exists():
        print("❌ question_all/ not found!")
        return
    
    folders = [f for f in question_all_dir.iterdir() if f.is_dir()]
    logger.info(f"Found {len(folders)} folders in question_all/")
    
    # 处理每个文件夹
    stats = {"total": 0, "pass_files": 0, "notpass_files": 0}
    
    for folder in sorted(folders):
        try:
            extract_single_file(folder)
            stats["total"] += 1
            
            if (folder / "pass.json").exists():
                stats["pass_files"] += 1
            if (folder / "not_pass.json").exists():
                stats["notpass_files"] += 1
        except Exception as e:
            logger.error(f"Error processing {folder.name}: {e}")
    
    print("=" * 80)
    print(f"Extraction complete:")
    print(f"  Total folders: {stats['total']}")
    print(f"  Files with passed questions: {stats['pass_files']}")
    print(f"  Files with not-passed questions: {stats['notpass_files']}")
    print(f"  Output: question_all_md/")
    print("=" * 80)


if __name__ == "__main__":
    main()
