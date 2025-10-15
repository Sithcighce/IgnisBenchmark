#!/usr/bin/env python3
"""
重启批处理任务
- 清理已失败的输出文件夹
- 降低并发数到5
- 添加请求延迟避免TPM限流
"""

import os
import shutil
import logging
from pathlib import Path
from batch_detail_q_generator import DetailQBatchProcessor
from src.utils import setup_logging, load_env_variables

# 设置日志
log_file = Path("logs") / "batch_restart.log"
log_file.parent.mkdir(exist_ok=True)

# 配置日志（直接使用logging）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_env_variables()

def clean_failed_outputs(output_dir: str):
    """清理失败的输出文件夹"""
    output_path = Path(output_dir)
    if output_path.exists():
        logger.info(f"Cleaning previous failed outputs in {output_dir}")
        for folder in output_path.iterdir():
            if folder.is_dir() and folder.name != "BATCH_SUMMARY.md":
                # 检查是否有pass.json或not_pass.json
                pass_json = folder / "pass.json"
                not_pass_json = folder / "not_pass.json"
                
                if not pass_json.exists() and not not_pass_json.exists():
                    logger.info(f"Removing incomplete folder: {folder.name}")
                    shutil.rmtree(folder)
    
    # 删除旧的BATCH_SUMMARY.md
    summary_file = output_path / "BATCH_SUMMARY.md"
    if summary_file.exists():
        summary_file.unlink()
        logger.info("Removed old BATCH_SUMMARY.md")

def main():
    logger.info("="*80)
    logger.info("RESTARTING BATCH DETAIL Q GENERATION")
    logger.info("="*80)
    logger.info("Configuration:")
    logger.info("  - Concurrent files: 5 (reduced from 20)")
    logger.info("  - Request delay: 1.0 seconds")
    logger.info("  - Mode: Quality check only, no citation verification")
    logger.info("="*80)
    
    # 清理失败的输出
    clean_failed_outputs("questions")
    
    # 启动批处理
    processor = DetailQBatchProcessor(
        input_dir="compliant",
        output_dir="questions"
    )
    
    processor.process_all_files()
    
    logger.info("="*80)
    logger.info("BATCH PROCESSING COMPLETED")
    logger.info("="*80)

if __name__ == "__main__":
    main()
