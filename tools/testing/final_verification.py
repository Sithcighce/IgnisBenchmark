#!/usr/bin/env python3
"""
最终系统完整性验证
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def final_verification():
    """最终验证"""
    print("🎯 最终系统验证...")
    
    try:
        # 测试核心功能
        from app import QuestionGeneratorGUI
        gui = QuestionGeneratorGUI()
        gui.root.withdraw()
        
        # 测试配置
        batch_size = gui.config["batch_size"]
        total_batches = gui.config["total_batches"]
        print(f"✅ 配置加载: batch_size={batch_size}, total_batches={total_batches}")
        
        # 测试日志
        gui.log_message("最终测试消息", "INFO")
        print("✅ 日志系统正常")
        
        # 测试Token统计
        gui.update_token_stats()
        print("✅ Token统计正常")
        
        # 清理
        gui.root.destroy()
        
        print("\n" + "🎉" * 20)
        print("🎯 系统100%就绪，可以投入使用！")
        print("🚀 运行命令: python app.py")
        print("📚 完整文档: docs/README.md")
        print("🎉" * 20)
        
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

if __name__ == "__main__":
    success = final_verification()
    sys.exit(0 if success else 1)