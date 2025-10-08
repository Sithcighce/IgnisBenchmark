#!/usr/bin/env python3
"""
测试模型修复 - 验证模型名称格式和API调用
"""

import logging
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config_loader import load_config
from src.utils import setup_logging
from src.question_generator import QuestionGenerator
from src.answering_module import AnsweringModule
from src.grading_module import GradingModule
from src.prompt_manager import PromptManager

def test_model_configurations():
    """测试模型配置和API调用格式"""
    
    # 设置日志
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # 加载配置
        logger.info("🔧 加载配置文件...")
        config = load_config()
        
        # 验证配置中的模型字段
        required_fields = ['generation_model', 'answering_model', 'grading_model']
        for field in required_fields:
            if field not in config:
                logger.error(f"❌ 缺少配置字段: {field}")
                return False
            else:
                logger.info(f"✅ 找到配置字段 {field}: {config[field]}")
        
        # 验证模型名称格式（应该包含provider前缀）
        models_to_check = {
            'generation_model': config['generation_model'],
            'answering_model': config['answering_model'], 
            'grading_model': config['grading_model']
        }
        
        for model_type, model_name in models_to_check.items():
            if '/' not in model_name:
                logger.warning(f"⚠️ {model_type} 可能缺少provider前缀: {model_name}")
            else:
                provider, model = model_name.split('/', 1)
                logger.info(f"✅ {model_type} 格式正确: provider={provider}, model={model}")
        
        # 初始化各个模块（不实际调用API）
        logger.info("🧪 测试模块初始化...")
        
        prompt_manager = PromptManager()
        
        # 测试QuestionGenerator初始化
        try:
            question_generator = QuestionGenerator(
                model_name=config['generation_model'],
                batch_size=1,
                prompt_manager=prompt_manager
            )
            logger.info("✅ QuestionGenerator 初始化成功")
        except Exception as e:
            logger.error(f"❌ QuestionGenerator 初始化失败: {e}")
            return False
        
        # 测试AnsweringModule初始化（如果有API密钥）
        if os.getenv('SILICONFLOW_API_KEY'):
            try:
                answering_module = AnsweringModule(
                    model_name=config['answering_model'].split('/')[-1],  # 只取模型名部分
                    prompt_manager=prompt_manager
                )
                logger.info("✅ AnsweringModule 初始化成功")
            except Exception as e:
                logger.error(f"❌ AnsweringModule 初始化失败: {e}")
                return False
        else:
            logger.info("⚠️ 跳过AnsweringModule测试（缺少SILICONFLOW_API_KEY）")
        
        # 测试GradingModule初始化
        try:
            grading_module = GradingModule(
                model_name=config['grading_model'],
                prompt_manager=prompt_manager
            )
            logger.info("✅ GradingModule 初始化成功")
        except Exception as e:
            logger.error(f"❌ GradingModule 初始化失败: {e}")
            return False
        
        logger.info("🎉 所有模块配置验证通过！")
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        return False

def test_api_key_availability():
    """测试API密钥可用性"""
    logger = logging.getLogger(__name__)
    
    logger.info("🔑 检查API密钥...")
    
    # 检查各种API密钥
    api_keys = {
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
        'SILICONFLOW_API_KEY': os.getenv('SILICONFLOW_API_KEY'),
        'DEEPSEEK_API_KEY': os.getenv('DEEPSEEK_API_KEY')
    }
    
    available_keys = 0
    for key_name, key_value in api_keys.items():
        if key_value:
            logger.info(f"✅ {key_name}: 已配置 (长度: {len(key_value)})")
            available_keys += 1
        else:
            logger.warning(f"⚠️ {key_name}: 未配置")
    
    if available_keys == 0:
        logger.warning("⚠️ 没有可用的API密钥！仅测试配置格式。")
        return True  # 允许测试继续，只是不能实际调用API
    else:
        logger.info(f"✅ 找到 {available_keys} 个API密钥")
        return True

if __name__ == "__main__":
    print("🧪 测试模型配置修复...")
    
    success = True
    success &= test_api_key_availability()
    success &= test_model_configurations()
    
    if success:
        print("\n🎉 所有测试通过！系统应该可以正常运行了。")
        print("💡 可以尝试运行: python run.py --mode generate -n 1")
    else:
        print("\n❌ 测试失败！请检查配置和修复。")
        sys.exit(1)