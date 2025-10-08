# 系统检查和验证脚本
# 不使用 python -c 命令

Write-Host "🔍 开始系统检查..." -ForegroundColor Green

# 设置工作目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
Set-Location $ProjectDir

Write-Host "📁 项目目录: $ProjectDir" -ForegroundColor Cyan

# 检查Python环境
Write-Host "`n🐍 检查Python环境..." -ForegroundColor Yellow
if (Get-Command python -ErrorAction SilentlyContinue) {
    $PythonVersion = python --version 2>&1
    Write-Host "✅ $PythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ 未找到Python解释器" -ForegroundColor Red
    exit 1
}

# 检查关键文件
Write-Host "`n📄 检查关键文件..." -ForegroundColor Yellow
$RequiredFiles = @(
    "app.py",
    "config.yaml", 
    ".env",
    "requirements.txt",
    "src\models.py",
    "src\question_generator.py",
    "src\answering_module.py",
    "src\grading_module.py",
    "prompts\生成题Prompt.md",
    "prompts\解题Prompt.md", 
    "prompts\判题Prompt.md"
)

foreach ($File in $RequiredFiles) {
    if (Test-Path $File) {
        Write-Host "✅ $File" -ForegroundColor Green
    } else {
        Write-Host "❌ $File 不存在" -ForegroundColor Red
    }
}

# 检查数据文件
Write-Host "`n📊 检查数据文件..." -ForegroundColor Yellow
$DataFiles = @(
    "data\benchmark_bank.jsonl",
    "data\seed_examples.jsonl",
    "data\validation_set.jsonl"
)

foreach ($File in $DataFiles) {
    if (Test-Path $File) {
        $FileSize = (Get-Item $File).Length
        Write-Host "✅ $File (${FileSize} 字节)" -ForegroundColor Green
    } else {
        Write-Host "❌ $File 不存在" -ForegroundColor Red
    }
}

# 运行Python系统检查脚本
Write-Host "`n⚡ 运行深度系统检查..." -ForegroundColor Yellow
try {
    python scripts\system_check.py
    Write-Host "✅ 深度检查完成" -ForegroundColor Green
}
catch {
    Write-Host "❌ 深度检查失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 运行数据验证脚本
Write-Host "`n📋 运行数据验证..." -ForegroundColor Yellow
try {
    python scripts\validate_data.py
    Write-Host "✅ 数据验证完成" -ForegroundColor Green
}
catch {
    Write-Host "❌ 数据验证失败: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 系统检查完成!" -ForegroundColor Green