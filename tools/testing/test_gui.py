#!/usr/bin/env python3
"""
GUI功能测试脚本
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_gui_import():
    """测试GUI模块导入"""
    try:
        from app import QuestionGeneratorGUI
        print("✅ GUI模块导入成功")
        return True
    except Exception as e:
        print(f"❌ GUI模块导入失败: {e}")
        return False

def test_config_loading():
    """测试配置加载"""
    try:
        from src.config_loader import load_config
        config = load_config()
        print(f"✅ 配置加载成功: batch_size={config['batch_size']}, total_batches={config.get('total_batches', '未设置')}")
        return True
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False

def test_logging_setup():
    """测试日志设置"""
    try:
        from src.utils import setup_logging
        import logging
        
        logger = setup_logging()
        logger.info("测试日志消息")
        print("✅ 日志设置成功")
        return True
    except Exception as e:
        print(f"❌ 日志设置失败: {e}")
        return False

def test_all_modules():
    """测试所有模块导入"""
    try:
        from src.question_generator import QuestionGenerator
        from src.answering_module import AnsweringModule
        from src.grading_module import GradingModule
        from src.data_persistence import DataPersistence
        from src.token_tracker import token_tracker
        from src.models import QuestionUnit, GradingResult, BenchmarkEntry
        
        print("✅ 所有核心模块导入成功")
        return True
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_gui_initialization():
    """测试GUI初始化（不显示窗口）"""
    try:
        import tkinter as tk
        # 创建隐藏的根窗口进行测试
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        
        from app import QuestionGeneratorGUI
        
        # 创建GUI实例但不运行mainloop
        gui = QuestionGeneratorGUI()
        gui.root.withdraw()  # 确保隐藏
        
        # 测试一些基本方法
        gui.log_message("测试消息", "INFO")
        gui.update_token_stats()
        
        print("✅ GUI初始化和基本功能测试成功")
        
        # 清理
        gui.root.destroy()
        root.destroy()
        
        return True
    except Exception as e:
        print(f"❌ GUI初始化失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("🧪 开始GUI功能测试...")
    print("=" * 50)
    
    tests = [
        ("模块导入测试", test_gui_import),
        ("配置加载测试", test_config_loading), 
        ("日志设置测试", test_logging_setup),
        ("核心模块测试", test_all_modules),
        ("GUI初始化测试", test_gui_initialization)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"⚠️ {test_name} 失败")
    
    print("\n" + "=" * 50)
    print(f"🎯 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！GUI可以正常运行")
        return True
    else:
        print("💥 有测试失败，请检查错误信息")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)