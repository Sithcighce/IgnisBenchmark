#!/usr/bin/env python3
"""
系统状态检查脚本
"""
import os
import sys
from pathlib import Path

def check_environment():
    """检查环境配置"""
    print("🔧 检查环境配置...")
    
    # 检查.env文件
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env文件存在")
        
        # 检查关键环境变量
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            google_key = os.getenv("GOOGLE_API_KEY")
            silicon_key = os.getenv("SILICONFLOW_API_KEY")
            
            if google_key and len(google_key) > 10:
                print("✅ GOOGLE_API_KEY 已配置")
            else:
                print("⚠️ GOOGLE_API_KEY 未配置或过短")
                
            if silicon_key and len(silicon_key) > 10:
                print("✅ SILICONFLOW_API_KEY 已配置")
            else:
                print("⚠️ SILICONFLOW_API_KEY 未配置或过短")
                
        except ImportError:
            print("⚠️ python-dotenv 包未安装")
    else:
        print("❌ .env文件不存在")

def check_directories():
    """检查目录结构"""
    print("\n📁 检查目录结构...")
    
    required_dirs = [
        "src",
        "data", 
        "prompts",
        "logs",
        "scripts"
    ]
    
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✅ {dir_name}/ 目录存在")
        else:
            print(f"❌ {dir_name}/ 目录不存在")

def check_files():
    """检查关键文件"""
    print("\n📄 检查关键文件...")
    
    required_files = [
        "app.py",
        "config.yaml",
        "requirements.txt",
        "src/__init__.py",
        "src/models.py",
        "src/question_generator.py",
        "src/answering_module.py", 
        "src/grading_module.py",
        "prompts/生成题Prompt.md",
        "prompts/解题Prompt.md",
        "prompts/判题Prompt.md"
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} 不存在")

def check_imports():
    """检查关键模块导入"""
    print("\n📦 检查模块导入...")
    
    modules_to_test = [
        ("tkinter", "GUI框架"),
        ("litellm", "LLM API"),
        ("yaml", "配置文件解析"),
        ("concurrent.futures", "并发处理"),
    ]
    
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name} - {description}")
        except ImportError:
            print(f"❌ {module_name} - {description} (导入失败)")

def main():
    """主函数"""
    # 确保在正确的工作目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    os.chdir(project_dir)
    
    print("🔍 系统状态检查开始...\n")
    
    check_environment()
    check_directories()
    check_files()
    check_imports()
    
    print("\n✅ 系统状态检查完成")

if __name__ == "__main__":
    main()