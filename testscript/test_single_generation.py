#!/usr/bin/env python3
"""
完整系统测试 - 生成一道题目验证整个流程
"""

import logging
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config_loader import load_config
from src.utils import setup_logging, load_env_variables
from src.question_generator import QuestionGenerator
from src.prompt_manager import PromptManager

def test_single_question_generation():
    """测试生成单道题目"""
    
    # 加载环境变量
    load_env_variables()
    
    # 设置日志
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🚀 开始单题目生成测试...")
        
        # 加载配置
        config = load_config()
        
        # 初始化prompt管理器
        prompt_manager = PromptManager()
        
        # 初始化题目生成器
        question_generator = QuestionGenerator(
            config['generation_model'],
            batch_size=1,  # 只生成一道题
            prompt_manager=prompt_manager
        )
        
        logger.info("🎯 开始生成题目...")
        
        # 生成题目（不使用few-shot示例）
        questions = question_generator.generate_questions()
        
        if questions:
            logger.info(f"✅ 成功生成 {len(questions)} 道题目！")
            
            # 显示生成的题目
            for i, question in enumerate(questions, 1):
                logger.info(f"\n📝 题目 {i}:")
                logger.info(f"主题: {question.topic}")
                logger.info(f"难度: {question.difficulty}")
                logger.info(f"类型: {question.type}")
                logger.info(f"题目: {question.question_text[:100]}...")
                logger.info(f"答案: {question.standard_answer[:100]}...")
                
            return True
        else:
            logger.error("❌ 题目生成失败！")
            return False
            
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return False

def check_env_setup():
    """检查环境设置"""
    logger = logging.getLogger(__name__)
    
    logger.info("🔍 检查环境设置...")
    
    # 检查.env文件
    env_file = Path(".env")
    if env_file.exists():
        logger.info("✅ 找到.env文件")
    else:
        logger.warning("⚠️ 未找到.env文件")
    
    # 检查关键环境变量
    required_vars = ["GEMINI_API_KEY", "SILICONFLOW_API_KEY"]
    found_vars = 0
    
    for var in required_vars:
        if os.getenv(var):
            logger.info(f"✅ {var}: 已设置")
            found_vars += 1
        else:
            logger.warning(f"⚠️ {var}: 未设置")
    
    if found_vars == 0:
        logger.error("❌ 没有找到任何API密钥！")
        logger.info("💡 请创建.env文件并添加API密钥:")
        logger.info("   GEMINI_API_KEY=your_gemini_key")
        logger.info("   SILICONFLOW_API_KEY=your_siliconflow_key")
        return False
    
    return True

if __name__ == "__main__":
    print("🧪 完整系统测试 - 单题目生成")
    
    if not check_env_setup():
        print("❌ 环境设置检查失败！请配置API密钥。")
        sys.exit(1)
    
    if test_single_question_generation():
        print("\n🎉 测试成功！系统正常工作。")
        print("💡 现在可以运行完整程序: python run.py --mode gui")
    else:
        print("\n❌ 测试失败！请检查日志和配置。")
        sys.exit(1)
