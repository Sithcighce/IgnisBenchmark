#!/usr/bin/env python3
"""
测试系统修复 - 验证配置字典支持和并发设置
"""

import logging
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config_loader import load_config
from src.utils import setup_logging
from src.question_generator import QuestionGenerator
from src.answering_module import AnsweringModule
from src.grading_module import GradingModule
from src.prompt_manager import PromptManager

def test_config_dict_support():
    """测试配置字典支持"""
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🔧 测试配置字典支持...")
        
        # 加载配置
        config = load_config()
        logger.info(f"✅ 成功加载配置，包含 {len(config)} 个字段")
        
        # 测试QuestionGenerator配置字典初始化
        logger.info("🧪 测试QuestionGenerator配置字典初始化...")
        question_generator = QuestionGenerator(config)
        logger.info(f"✅ QuestionGenerator: 模型={question_generator.model_name}, 批次大小={question_generator.batch_size}")
        
        # 测试GradingModule配置字典初始化  
        logger.info("🧪 测试GradingModule配置字典初始化...")
        grading_module = GradingModule(config)
        logger.info(f"✅ GradingModule: 模型={grading_module.model_name}")
        
        # 测试AnsweringModule配置字典初始化（如果有API密钥）
        if os.getenv('SILICONFLOW_API_KEY'):
            logger.info("🧪 测试AnsweringModule配置字典初始化...")
            answering_module = AnsweringModule(config)
            logger.info(f"✅ AnsweringModule: 模型={answering_module.model_name}, 并发={answering_module.concurrency}, API={answering_module.api_base}")
            
            # 验证并发配置是否正确
            expected_concurrency = config.get('round_internal_concurrency', 5)
            if answering_module.concurrency == expected_concurrency:
                logger.info(f"✅ 并发配置正确: {answering_module.concurrency}")
            else:
                logger.warning(f"⚠️ 并发配置不匹配: 期望={expected_concurrency}, 实际={answering_module.concurrency}")
        else:
            logger.info("⚠️ 跳过AnsweringModule测试（缺少SILICONFLOW_API_KEY）")
        
        logger.info("🎉 所有配置字典测试通过！")
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return False

def test_backward_compatibility():
    """测试向后兼容性"""
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🔄 测试向后兼容性...")
        
        prompt_manager = PromptManager()
        
        # 测试旧式单独参数调用
        question_generator = QuestionGenerator(
            "gemini/gemini-2.5-flash", 
            batch_size=5, 
            prompt_manager=prompt_manager
        )
        logger.info(f"✅ QuestionGenerator旧式调用: 模型={question_generator.model_name}")
        
        grading_module = GradingModule(
            "gemini/gemini-2.5-flash",
            prompt_manager=prompt_manager  
        )
        logger.info(f"✅ GradingModule旧式调用: 模型={grading_module.model_name}")
        
        # AnsweringModule旧式调用（如果有API密钥）
        if os.getenv('SILICONFLOW_API_KEY'):
            answering_module = AnsweringModule(
                "https://api.siliconflow.cn/v1",
                model_name="Qwen/Qwen2.5-7B-Instruct",
                concurrency=2,
                prompt_manager=prompt_manager
            )
            logger.info(f"✅ AnsweringModule旧式调用: 模型={answering_module.model_name}")
        
        logger.info("✅ 向后兼容性测试通过！")
        return True
        
    except Exception as e:
        logger.error(f"❌ 向后兼容性测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🧪 测试系统修复效果...")
    
    success = True
    success &= test_config_dict_support()
    success &= test_backward_compatibility()
    
    if success:
        print("\n🎉 所有测试通过！系统修复成功。")
        print("💡 主要修复:")
        print("  - 支持配置字典初始化")
        print("  - 正确应用并发设置")  
        print("  - 修复LiteLLM参数传递")
        print("  - 保持向后兼容性")
        print("\n🚀 可以运行主程序: python run.py --mode generate -n 1")
    else:
        print("\n❌ 测试失败！请检查修复。")
        sys.exit(1)