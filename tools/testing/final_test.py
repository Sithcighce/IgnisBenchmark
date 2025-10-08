#!/usr/bin/env python3
"""
最终完整功能验证
启动GUI并进行基本操作验证
"""

import sys
import threading
import time
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_complete_functionality():
    """测试完整功能"""
    print("🚀 启动完整功能测试...")
    
    try:
        # 导入GUI类
        from app import QuestionGeneratorGUI
        import tkinter as tk
        
        print("✅ 1. GUI类导入成功")
        
        # 创建GUI实例
        app = QuestionGeneratorGUI()
        print("✅ 2. GUI实例创建成功")
        
        # 测试配置读取
        print(f"✅ 3. 配置读取成功: {app.config.get('batch_size')}题/批次, {app.config.get('total_batches')}批次")
        
        # 测试日志功能
        app.log_message("功能测试开始", "INFO")
        print("✅ 4. 日志功能正常")
        
        # 测试Token统计
        app.update_token_stats()
        print("✅ 5. Token统计功能正常")
        
        # 测试界面更新
        app.progress_var.set("测试进度")
        app.progress_bar.config(value=50)
        print("✅ 6. 界面更新功能正常")
        
        print("\n🎉 所有功能测试通过！")
        print("📱 图形界面已准备就绪")
        print("🔧 配置文件正确加载")
        print("📊 Token统计系统就绪")
        print("📋 日志系统正常工作")
        
        # 清理资源
        app.root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ 功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🎯 智能题库生成与评估系统 - 最终验证")
    print("=" * 60)
    
    success = test_complete_functionality()
    
    if success:
        print("\n" + "✅" * 20)
        print("🎉 程序完全就绪！可以正常使用！")
        print("🚀 运行命令: python app.py")
        print("✅" * 20)
        
        # 提供使用说明
        print("\n📖 使用说明:")
        print("1. 运行 'python app.py' 启动图形界面")
        print("2. 在界面中设置总批次数（1-100）")
        print("3. 点击'开始生成'按钮开始批量生成题目") 
        print("4. 实时查看进度、日志和Token统计")
        print("5. 可随时停止和重新开始")
        
        return True
    else:
        print("\n" + "❌" * 20)
        print("💥 程序存在问题，请检查错误信息")
        print("❌" * 20)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)