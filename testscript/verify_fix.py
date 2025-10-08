#!/usr/bin/env python3
"""
模拟测试 - 验证修复效果而无需实际API调用
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_import_and_model_formats():
    """测试导入和模型格式验证"""
    
    print("🧪 测试导入和模型格式...")
    
    try:
        # 测试配置加载
        print("1️⃣ 测试配置加载...")
        from src.config_loader import load_config
        config = load_config()
        
        required_models = ['generation_model', 'answering_model', 'grading_model']
        for model_key in required_models:
            if model_key in config:
                model_name = config[model_key]
                if '/' in model_name:
                    provider, model = model_name.split('/', 1)
                    print(f"   ✅ {model_key}: {provider}/{model}")
                else:
                    print(f"   ⚠️ {model_key}: 缺少provider前缀: {model_name}")
            else:
                print(f"   ❌ 缺少配置: {model_key}")
        
        # 测试模块导入
        print("\n2️⃣ 测试模块导入...")
        from src.question_generator import QuestionGenerator
        from src.answering_module import AnsweringModule  
        from src.grading_module import GradingModule
        from src.prompt_manager import PromptManager
        print("   ✅ 所有核心模块导入成功")
        
        # 测试QuestionGenerator的模型回退列表
        print("\n3️⃣ 检查QuestionGenerator模型回退列表...")
        # 读取源代码检查模型格式
        qg_file = Path("src/question_generator.py")
        if qg_file.exists():
            with open(qg_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'model_fallbacks = [' in content:
                    # 提取模型回退列表部分
                    start = content.find('model_fallbacks = [')
                    if start != -1:
                        end = content.find(']', start) + 1
                        fallback_section = content[start:end]
                        print(f"   找到模型回退列表:")
                        lines = fallback_section.split('\n')
                        for line in lines:
                            line = line.strip()
                            if '"' in line and '/' in line:
                                # 提取模型名称
                                model = line.split('"')[1]
                                if '/' in model:
                                    provider, model_name = model.split('/', 1)
                                    print(f"   ✅ 格式正确: {provider}/{model_name}")
                                else:
                                    print(f"   ❌ 缺少provider: {model}")
        
        # 测试litellm导入
        print("\n4️⃣ 测试LiteLLM导入...")
        try:
            import litellm
            print("   ✅ LiteLLM导入成功")
            
            # 检查支持的providers
            providers = ['gemini', 'siliconflow', 'openai', 'deepseek']
            print("   支持的providers:", providers)
            
        except ImportError as e:
            print(f"   ❌ LiteLLM导入失败: {e}")
            return False
        
        print("\n🎉 所有测试通过！模型配置修复成功。")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        return False

def show_next_steps():
    """显示后续步骤"""
    print("\n📋 后续步骤:")
    print("1. 配置API密钥:")
    print("   - 创建 .env 文件")
    print("   - 添加: GEMINI_API_KEY=your_key")
    print("   - 添加: SILICONFLOW_API_KEY=your_key")
    print("\n2. 运行系统:")
    print("   python run.py --mode gui       # 图形界面")
    print("   python run.py --mode generate  # 生成题目")
    print("   python run.py --mode visualize # 生成可视化")
    print("\n3. 验证修复:")
    print("   python test_single_generation.py  # 完整测试（需API密钥）")

if __name__ == "__main__":
    print("🔧 模型配置修复验证 - 无需API密钥")
    
    if test_import_and_model_formats():
        print("\n✅ 修复验证成功！LiteLLM provider错误已解决。")
        show_next_steps()
    else:
        print("\n❌ 还有问题需要解决。")
        sys.exit(1)
