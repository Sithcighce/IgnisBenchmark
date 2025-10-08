#!/usr/bin/env python3
"""
启动应用程序脚本
"""
import os
import sys

def main():
    # 确保在正确的工作目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    os.chdir(project_dir)
    
    # 确保Python路径包含项目目录
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)
    
    # 导入并运行应用程序
    try:
        from app import main as app_main
        print("🚀 正在启动智能题库生成与评估系统...")
        app_main()
    except KeyboardInterrupt:
        print("\n👋 用户终止了应用程序")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())