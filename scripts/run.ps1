# 启动应用程序的PowerShell脚本
# 不使用 python -c 命令

Write-Host "🚀 正在启动智能题库生成与评估系统..." -ForegroundColor Green

# 设置工作目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
Set-Location $ProjectDir

Write-Host "📁 工作目录: $ProjectDir" -ForegroundColor Cyan

# 检查Python环境
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ 未找到Python解释器" -ForegroundColor Red
    exit 1
}

# 显示Python版本
$PythonVersion = python --version 2>&1
Write-Host "🐍 $PythonVersion" -ForegroundColor Blue

# 运行应用程序
Write-Host "⚡ 启动应用程序..." -ForegroundColor Yellow
try {
    python app.py
}
catch {
    Write-Host "❌ 应用程序启动失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "👋 应用程序已退出" -ForegroundColor Green