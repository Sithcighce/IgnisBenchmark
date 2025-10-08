"""
系统测试脚本 - 验证所有组件是否正常工作
"""

import os
import sys
from pathlib import Path
import requests

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils import load_config, setup_logging, load_env_variables


def test_config():
    """测试配置文件"""
    print("\n[1/6] 测试配置文件...")
    try:
        config = load_config()
        print("  ✓ config.yaml 加载成功")
        
        required_keys = [
            "lm_studio_endpoint", "lm_studio_model_name",
            "generation_model", "grading_model",
            "benchmark_bank_path", "validation_set_path",
            "env_file_path", "lm_studio_concurrency", "few_shot_count"
        ]
        
        for key in required_keys:
            if key not in config:
                print(f"  ✗ 缺少配置项: {key}")
                return False
        
        print("  ✓ 所有必需配置项存在")
        return True
    except Exception as e:
        print(f"  ✗ 配置文件加载失败: {e}")
        return False


def test_env():
    """测试环境变量"""
    print("\n[2/6] 测试环境变量...")
    try:
        if not os.path.exists(".env"):
            print("  ✗ .env 文件不存在")
            return False
        
        load_env_variables()
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key.startswith("sk-"):
            print("  ✗ GOOGLE_API_KEY 未正确设置")
            return False
        
        print("  ✓ 环境变量加载成功")
        print(f"  ✓ GOOGLE_API_KEY 已设置 (长度: {len(api_key)})")
        return True
    except Exception as e:
        print(f"  ✗ 环境变量加载失败: {e}")
        return False


def test_dependencies():
    """测试Python依赖"""
    print("\n[3/6] 测试Python依赖...")
    required_packages = ["litellm", "dotenv", "yaml", "requests", "flask"]
    
    all_installed = True
    for package in required_packages:
        try:
            if package == "dotenv":
                __import__("dotenv")
            elif package == "yaml":
                __import__("yaml")
            else:
                __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} 未安装")
            all_installed = False
    
    return all_installed


def test_lm_studio():
    """测试LM Studio连接"""
    print("\n[4/6] 测试LM Studio连接...")
    config = load_config()
    endpoint = config["lm_studio_endpoint"]
    
    models_url = endpoint.replace("/chat/completions", "/models").replace("/v1/chat/completions", "/v1/models")
    
    try:
        response = requests.get(models_url, timeout=5)
        if response.status_code == 200:
            print(f"  ✓ LM Studio 连接成功")
            data = response.json()
            if "data" in data and len(data["data"]) > 0:
                print(f"  ✓ 可用模型: {len(data['data'])} 个")
            return True
        else:
            print(f"  ✗ LM Studio 响应异常 (状态码: {response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print(f"  ✗ 无法连接到 LM Studio ({models_url})")
        print(f"  提示: 请确保 LM Studio 已启动并运行在端口 1234")
        return False
    except Exception as e:
        print(f"  ✗ LM Studio 测试失败: {e}")
        return False


def test_google_api():
    """测试Google API连接"""
    print("\n[5/6] 测试Google Gemini API...")
    
    try:
        from litellm import completion
        
        response = completion(
            model="gemini/gemini-2.0-flash-exp",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        
        if response and response.choices:
            print("  ✓ Google Gemini API 连接成功")
            return True
        else:
            print("  ✗ API响应异常")
            return False
            
    except Exception as e:
        print(f"  ✗ Google API 测试失败: {e}")
        return False


def test_file_structure():
    """测试文件结构"""
    print("\n[6/6] 测试文件结构...")
    
    required_files = [
        "config.yaml", ".env", "requirements.txt",
        "main.py", "web_ui.py",
        "src/__init__.py", "src/models.py", "src/utils.py",
        "src/prompt_manager.py", "src/question_generator.py",
        "src/answering_module.py", "src/grading_module.py",
        "src/data_persistence.py",
        "docs/生成题Prompt.md", "docs/判题Prompt.md", "docs/解题Prompt.md"
    ]
    
    required_dirs = ["data", "logs", "src", "docs"]
    
    all_exist = True
    
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} 缺失")
            all_exist = False
    
    for dir in required_dirs:
        if os.path.isdir(dir):
            print(f"  ✓ {dir}/")
        else:
            print(f"  ✗ {dir}/ 缺失")
            all_exist = False
    
    return all_exist


def main():
    """运行所有测试"""
    print("=" * 60)
    print("智能题库系统 - 配置测试")
    print("=" * 60)
    
    results = []
    
    results.append(("配置文件", test_config()))
    results.append(("环境变量", test_env()))
    results.append(("Python依赖", test_dependencies()))
    results.append(("LM Studio", test_lm_studio()))
    results.append(("Google API", test_google_api()))
    results.append(("文件结构", test_file_structure()))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name:15} {status}")
    
    print("-" * 60)
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统已准备就绪。")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请根据上述提示修复问题。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
