#!/usr/bin/env python3
"""
合并所有问题到question_all，并补全缺失的文献
"""

import os
import json
import shutil
import logging
from pathlib import Path
from typing import Set, Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from src.utils import setup_logging, load_env_variables
from batch_detail_q_generator import DetailQBatchProcessor

logger = logging.getLogger(__name__)


def get_all_processed_files() -> Dict[str, List[Path]]:
    """获取所有已处理的文件"""
    sources = {
        "questions": Path("questions"),
        "question_reverse": Path("question_reverse"),
        "questions_copy": Path("questions copy")
    }
    
    processed = {}
    for source_name, source_path in sources.items():
        if not source_path.exists():
            logger.warning(f"{source_path} not found, skipping")
            continue
        
        subfolders = [f for f in source_path.iterdir() if f.is_dir()]
        processed[source_name] = subfolders
        logger.info(f"{source_name}: {len(subfolders)} folders")
    
    return processed


def merge_questions(filename: str, source_folders: Dict[str, Path]) -> tuple:
    """合并来自不同源的问题"""
    all_pass = []
    all_notpass = []
    
    for source_name, folder in source_folders.items():
        # 读取pass.json
        pass_file = folder / "pass.json"
        if pass_file.exists():
            try:
                with open(pass_file, 'r', encoding='utf-8') as f:
                    questions = json.load(f)
                    # 添加来源标记
                    for q in questions:
                        q['merge_source'] = source_name
                    all_pass.extend(questions)
                    logger.debug(f"  [{filename}] {source_name}/pass.json: {len(questions)} questions")
            except Exception as e:
                logger.error(f"  [{filename}] Error reading {pass_file}: {e}")
        
        # 读取not_pass.json
        notpass_file = folder / "not_pass.json"
        if notpass_file.exists():
            try:
                with open(notpass_file, 'r', encoding='utf-8') as f:
                    questions = json.load(f)
                    for q in questions:
                        q['merge_source'] = source_name
                    all_notpass.extend(questions)
                    logger.debug(f"  [{filename}] {source_name}/not_pass.json: {len(questions)} questions")
            except Exception as e:
                logger.error(f"  [{filename}] Error reading {notpass_file}: {e}")
    
    return all_pass, all_notpass


def consolidate_all_questions():
    """步骤1: 合并所有已有问题到question_all"""
    logger.info("=" * 80)
    logger.info("STEP 1: Consolidating all questions to question_all/")
    logger.info("=" * 80)
    
    output_dir = Path("question_all")
    output_dir.mkdir(exist_ok=True)
    
    # 获取所有已处理的文件
    processed = get_all_processed_files()
    
    # 按文件名组织
    all_files = {}
    for source_name, folders in processed.items():
        for folder in folders:
            filename = folder.name
            if filename not in all_files:
                all_files[filename] = {}
            all_files[filename][source_name] = folder
    
    logger.info(f"Found {len(all_files)} unique files across all sources")
    
    # 合并每个文件
    stats = {"total": 0, "with_pass": 0, "with_notpass": 0, "total_pass_q": 0, "total_notpass_q": 0}
    
    for filename, sources in sorted(all_files.items()):
        logger.info(f"[{filename}] Merging from {len(sources)} sources...")
        
        # 合并问题
        all_pass, all_notpass = merge_questions(filename, sources)
        
        # 创建输出文件夹
        output_folder = output_dir / filename
        output_folder.mkdir(exist_ok=True)
        
        # 复制txt文件（从任一源）
        txt_copied = False
        for source_path in sources.values():
            txt_file = source_path / f"{filename}.txt"
            if txt_file.exists():
                shutil.copy(txt_file, output_folder / f"{filename}.txt")
                txt_copied = True
                break
        
        if not txt_copied:
            # 尝试从compliant复制
            compliant_txt = Path("compliant") / f"{filename}.txt"
            if compliant_txt.exists():
                shutil.copy(compliant_txt, output_folder / f"{filename}.txt")
        
        # 保存合并后的问题
        if all_pass:
            with open(output_folder / "pass.json", 'w', encoding='utf-8') as f:
                json.dump(all_pass, f, ensure_ascii=False, indent=2)
            stats["with_pass"] += 1
            stats["total_pass_q"] += len(all_pass)
        
        if all_notpass:
            with open(output_folder / "not_pass.json", 'w', encoding='utf-8') as f:
                json.dump(all_notpass, f, ensure_ascii=False, indent=2)
            stats["with_notpass"] += 1
            stats["total_notpass_q"] += len(all_notpass)
        
        stats["total"] += 1
        logger.info(f"[{filename}] ✅ Merged: {len(all_pass)} pass, {len(all_notpass)} not_pass")
    
    logger.info("=" * 80)
    logger.info(f"Consolidation complete:")
    logger.info(f"  Total files: {stats['total']}")
    logger.info(f"  Files with pass questions: {stats['with_pass']}")
    logger.info(f"  Files with notpass questions: {stats['with_notpass']}")
    logger.info(f"  Total pass questions: {stats['total_pass_q']}")
    logger.info(f"  Total notpass questions: {stats['total_notpass_q']}")
    logger.info("=" * 80)
    
    return all_files.keys()


def find_missing_files(existing_files: Set[str]) -> List[Path]:
    """找出compliant中缺失的文件"""
    logger.info("=" * 80)
    logger.info("STEP 2: Finding missing files in compliant/")
    logger.info("=" * 80)
    
    compliant_dir = Path("compliant")
    all_txt_files = list(compliant_dir.glob("*.txt"))
    
    missing = []
    for txt_file in all_txt_files:
        filename = txt_file.stem
        if filename not in existing_files:
            missing.append(txt_file)
    
    logger.info(f"Total files in compliant: {len(all_txt_files)}")
    logger.info(f"Already processed: {len(existing_files)}")
    logger.info(f"Missing: {len(missing)}")
    
    if missing:
        logger.info(f"First 10 missing files:")
        for f in missing[:10]:
            logger.info(f"  - {f.stem}")
    
    return missing


def classify_failures(question_all_dir: Path) -> Dict[str, List[str]]:
    """分类失败原因：窗口超限 vs 程序异常"""
    logger.info("=" * 80)
    logger.info("STEP 3: Classifying failures")
    logger.info("=" * 80)
    
    window_exceeded = []
    program_errors = []
    incomplete_generation = []  # 生成了但不足5题
    
    for folder in question_all_dir.iterdir():
        if not folder.is_dir():
            continue
        
        filename = folder.name
        pass_file = folder / "pass.json"
        notpass_file = folder / "not_pass.json"
        
        # 统计问题数
        pass_count = 0
        notpass_count = 0
        
        if pass_file.exists():
            try:
                with open(pass_file, 'r', encoding='utf-8') as f:
                    pass_count = len(json.load(f))
            except:
                pass
        
        if notpass_file.exists():
            try:
                with open(notpass_file, 'r', encoding='utf-8') as f:
                    notpass_count = len(json.load(f))
            except:
                pass
        
        total_questions = pass_count + notpass_count
        
        # 检查txt文件大小
        txt_file = folder / f"{filename}.txt"
        file_size = 0
        if txt_file.exists():
            file_size = txt_file.stat().st_size
        
        # 分类
        if total_questions == 0:
            # 没有任何问题
            if file_size > 500000:  # >500KB 可能是窗口超限
                window_exceeded.append(filename)
            else:
                program_errors.append(filename)
        elif total_questions < 5:
            # 生成了但不足5题
            incomplete_generation.append(filename)
    
    logger.info(f"Window exceeded (>500KB, 0 questions): {len(window_exceeded)}")
    logger.info(f"Program errors (small file, 0 questions): {len(program_errors)}")
    logger.info(f"Incomplete generation (<5 questions): {len(incomplete_generation)}")
    
    if window_exceeded:
        logger.info(f"  Window exceeded samples: {window_exceeded[:5]}")
    if program_errors:
        logger.info(f"  Program error samples: {program_errors[:5]}")
    if incomplete_generation:
        logger.info(f"  Incomplete samples: {incomplete_generation[:5]}")
    
    return {
        "window_exceeded": window_exceeded,
        "program_errors": program_errors,
        "incomplete_generation": incomplete_generation
    }


def generate_missing_questions(missing_files: List[Path], retry_files: List[str]):
    """步骤4: 使用DeepSeek生成缺失的问题"""
    logger.info("=" * 80)
    logger.info("STEP 4: Generating questions for missing/retry files")
    logger.info("=" * 80)
    
    # 合并需要处理的文件
    files_to_process = []
    
    # 缺失的文件
    for f in missing_files:
        files_to_process.append(("missing", f))
    
    # 需要重试的文件
    question_all_dir = Path("question_all")
    for filename in retry_files:
        txt_file = question_all_dir / filename / f"{filename}.txt"
        if not txt_file.exists():
            # 从compliant复制
            compliant_file = Path("compliant") / f"{filename}.txt"
            if compliant_file.exists():
                txt_file.parent.mkdir(exist_ok=True)
                shutil.copy(compliant_file, txt_file)
        
        if txt_file.exists():
            files_to_process.append(("retry", txt_file))
    
    logger.info(f"Total files to process: {len(files_to_process)}")
    logger.info(f"  - Missing files: {len(missing_files)}")
    logger.info(f"  - Retry files: {len(retry_files)}")
    
    if not files_to_process:
        logger.info("No files to process!")
        return
    
    # 使用DeepSeek生成器
    generator = DetailQBatchProcessor(input_dir="compliant", output_dir="question_all")
    
    # 并发处理
    MAX_CONCURRENT = 20
    results = {"success": 0, "failed": 0}
    
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT) as executor:
        futures = {
            executor.submit(generator.process_single_file, file_path): (file_type, file_path)
            for file_type, file_path in files_to_process
        }
        
        for future in as_completed(futures):
            file_type, file_path = futures[future]
            try:
                result = future.result()
                if result["status"] == "success":
                    results["success"] += 1
                else:
                    results["failed"] += 1
                
                logger.info(f"[{file_type}] {file_path.stem}: {result['status']}")
            except Exception as e:
                results["failed"] += 1
                logger.error(f"[{file_type}] {file_path.stem}: ERROR - {str(e)[:200]}")
    
    logger.info("=" * 80)
    logger.info(f"Generation complete:")
    logger.info(f"  Success: {results['success']}")
    logger.info(f"  Failed: {results['failed']}")
    logger.info("=" * 80)


def generate_summary_report():
    """生成最终报告"""
    question_all_dir = Path("question_all")
    
    total_folders = 0
    folders_with_5plus = 0
    folders_with_questions = 0
    total_pass = 0
    total_notpass = 0
    window_exceeded = 0
    
    details = []
    
    for folder in sorted(question_all_dir.iterdir()):
        if not folder.is_dir():
            continue
        
        total_folders += 1
        filename = folder.name
        
        pass_count = 0
        notpass_count = 0
        
        pass_file = folder / "pass.json"
        notpass_file = folder / "not_pass.json"
        
        if pass_file.exists():
            try:
                with open(pass_file, 'r', encoding='utf-8') as f:
                    pass_count = len(json.load(f))
            except:
                pass
        
        if notpass_file.exists():
            try:
                with open(notpass_file, 'r', encoding='utf-8') as f:
                    notpass_count = len(json.load(f))
            except:
                pass
        
        total_questions = pass_count + notpass_count
        total_pass += pass_count
        total_notpass += notpass_count
        
        if total_questions > 0:
            folders_with_questions += 1
        
        if total_questions >= 5:
            folders_with_5plus += 1
        
        # 检查是否窗口超限
        txt_file = folder / f"{filename}.txt"
        file_size = 0
        if txt_file.exists():
            file_size = txt_file.stat().st_size
        
        status = "✅" if total_questions >= 5 else ("⚠️" if total_questions > 0 else "❌")
        if total_questions == 0 and file_size > 500000:
            status = "🚫 Window"
            window_exceeded += 1
        
        details.append({
            "filename": filename,
            "pass": pass_count,
            "notpass": notpass_count,
            "total": total_questions,
            "size": file_size,
            "status": status
        })
    
    # 生成Markdown报告
    report_file = question_all_dir / "CONSOLIDATION_REPORT.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"""# Question All - Consolidation Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 OVERALL SUMMARY

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total Folders** | {total_folders} | 100% |
| **Folders with ≥5 Questions** | {folders_with_5plus} | {folders_with_5plus/max(1,total_folders)*100:.1f}% |
| **Folders with Questions** | {folders_with_questions} | {folders_with_questions/max(1,total_folders)*100:.1f}% |
| **Window Exceeded (>500KB)** | {window_exceeded} | {window_exceeded/max(1,total_folders)*100:.1f}% |
| **Total Pass Questions** | {total_pass} | - |
| **Total Not-Pass Questions** | {total_notpass} | - |
| **Total Questions** | {total_pass + total_notpass} | - |

---

## 📋 DETAILED RESULTS

| File | Pass | Not-Pass | Total | Size (KB) | Status |
|------|------|----------|-------|-----------|--------|
""")
        
        for d in details:
            size_kb = d['size'] / 1024 if d['size'] > 0 else 0
            f.write(f"| {d['filename']} | {d['pass']} | {d['notpass']} | {d['total']} | {size_kb:.1f} | {d['status']} |\n")
    
    logger.info(f"Summary report saved to: {report_file}")
    logger.info("=" * 80)
    logger.info(f"FINAL STATISTICS:")
    logger.info(f"  Total folders: {total_folders}")
    logger.info(f"  Folders with ≥5 questions: {folders_with_5plus} ({folders_with_5plus/max(1,total_folders)*100:.1f}%)")
    logger.info(f"  Window exceeded: {window_exceeded}")
    logger.info(f"  Total questions: {total_pass + total_notpass} ({total_pass} pass + {total_notpass} not-pass)")
    logger.info("=" * 80)


def main():
    """主流程"""
    setup_logging()
    load_env_variables()
    
    print("=" * 80)
    print("Question Consolidation and Completion")
    print("=" * 80)
    
    # 步骤1: 合并所有问题
    existing_files = consolidate_all_questions()
    
    # 步骤2: 找出缺失的文件
    missing_files = find_missing_files(set(existing_files))
    
    # 步骤3: 分类失败原因
    failures = classify_failures(Path("question_all"))
    
    # 步骤4: 生成缺失的问题（跳过窗口超限，重试程序错误和不完整生成）
    retry_files = failures["program_errors"] + failures["incomplete_generation"]
    generate_missing_questions(missing_files, retry_files)
    
    # 步骤5: 生成最终报告
    generate_summary_report()
    
    print("\n✅ ALL DONE!")
    print("Check: question_all/CONSOLIDATION_REPORT.md")


if __name__ == "__main__":
    main()
