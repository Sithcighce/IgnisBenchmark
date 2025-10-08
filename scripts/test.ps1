# 快速测试脚本
# 测试应用程序的核心功能，不使用 python -c 命令

Write-Host "🧪 开始快速测试..." -ForegroundColor Green

# 设置工作目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
Set-Location $ProjectDir

# 创建测试脚本文件
$TestScript = @"
#!/usr/bin/env python3
"""
快速功能测试
"""
import sys
import os

# 确保项目目录在路径中
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

def test_imports():
    """测试核心模块导入"""
    print("📦 测试模块导入...")
    
    try:
        from src.models import QuestionUnit, GradingResult
        print("✅ models模块导入成功")
    except Exception as e:
        print(f"❌ models模块导入失败: {e}")
        return False
    
    try:
        from src.prompt_manager import PromptManager
        print("✅ prompt_manager模块导入成功")
    except Exception as e:
        print(f"❌ prompt_manager模块导入失败: {e}")
        return False
    
    try:
        from src.data_persistence import DataPersistence
        print("✅ data_persistence模块导入成功")
    except Exception as e:
        print(f"❌ data_persistence模块导入失败: {e}")
        return False
    
    return True

def test_prompt_loading():
    """测试prompt加载"""
    print("\n📝 测试Prompt加载...")
    
    try:
        from src.prompt_manager import PromptManager
        pm = PromptManager()
        
        gen_prompt = pm.get_generation_prompt()
        if gen_prompt and len(gen_prompt) > 100:
            print("✅ 生成题Prompt加载成功")
        else:
            print("❌ 生成题Prompt加载失败或内容过短")
            
        solve_prompt = pm.get_answering_prompt()
        if solve_prompt and len(solve_prompt) > 100:
            print("✅ 解题Prompt加载成功")
        else:
            print("❌ 解题Prompt加载失败或内容过短")
            
        grade_prompt = pm.get_grading_prompt()
        if grade_prompt and len(grade_prompt) > 100:
            print("✅ 判题Prompt加载成功")
        else:
            print("❌ 判题Prompt加载失败或内容过短")
            
        return True
    except Exception as e:
        print(f"❌ Prompt加载测试失败: {e}")
        return False

def test_data_loading():
    """测试数据加载"""
    print("\n📊 测试数据加载...")
    
    try:
        from src.data_persistence import DataPersistence
        dp = DataPersistence()
        
        # 测试benchmark数据加载
        benchmark_data = dp.load_benchmark_bank()
        print(f"✅ Benchmark数据加载成功，共{len(benchmark_data)}条记录")
        
        # 测试随机采样
        if len(benchmark_data) > 0:
            samples = dp.get_random_samples(min(3, len(benchmark_data)))
            print(f"✅ 随机采样成功，获取{len(samples)}条样本")
        
        return True
    except Exception as e:
        print(f"❌ 数据加载测试失败: {e}")
        return False

def main():
    print("🚀 开始快速功能测试...")
    
    success = True
    success = success and test_imports()
    success = success and test_prompt_loading() 
    success = success and test_data_loading()
    
    if success:
        print("\n🎉 所有测试通过!")
        return 0
    else:
        print("\n❌ 部分测试失败")
        return 1

if __name__ == "__main__":
    exit(main())
"@

# 写入临时测试文件
$TempTestFile = "temp_test.py"
$TestScript | Out-File -FilePath $TempTestFile -Encoding UTF8

try {
    # 运行测试
    Write-Host "⚡ 执行功能测试..." -ForegroundColor Yellow
    python $TempTestFile
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 快速测试完成!" -ForegroundColor Green
    } else {
        Write-Host "❌ 测试发现问题!" -ForegroundColor Red
    }
}
catch {
    Write-Host "❌ 测试执行失败: $($_.Exception.Message)" -ForegroundColor Red
}
finally {
    # 清理临时文件
    if (Test-Path $TempTestFile) {
        Remove-Item $TempTestFile -Force
    }
}