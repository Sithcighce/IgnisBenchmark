#!/usr/bin/env python3
"""
紧急修复验证
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_logger_fix():
    """测试logger修复"""
    print("🔧 测试logger修复...")
    
    try:
        from app import QuestionGeneratorGUI
        import tkinter as tk
        
        # 创建GUI实例
        app = QuestionGeneratorGUI()
        app.root.withdraw()  # 隐藏窗口
        
        # 测试logger是否正确初始化
        print(f"Logger对象: {app.logger}")
        print(f"Logger类型: {type(app.logger)}")
        
        # 测试log_message方法
        print("测试log_message方法...")
        app.log_message("测试INFO消息", "INFO")
        app.log_message("测试ERROR消息", "ERROR") 
        app.log_message("测试WARNING消息", "WARNING")
        
        print("✅ 所有日志方法调用成功")
        
        # 清理
        app.root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_logger_fix()
    if success:
        print("🎉 Logger问题已完全修复！")
    else:
        print("💥 Logger问题仍然存在")
    
    sys.exit(0 if success else 1)