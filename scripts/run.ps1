# Windows启动脚本 - 运行主程序

# 激活虚拟环境（如果存在）
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "激活虚拟环境..." -ForegroundColor Green
    .\venv\Scripts\Activate.ps1
}

# 检查依赖
Write-Host "检查依赖..." -ForegroundColor Green
$packages = @("litellm", "python-dotenv", "pyyaml", "requests", "flask")
$missing = @()

foreach ($pkg in $packages) {
    $result = pip show $pkg 2>&1
    if ($LASTEXITCODE -ne 0) {
        $missing += $pkg
    }
}

if ($missing.Count -gt 0) {
    Write-Host "缺少以下依赖包: $($missing -join ', ')" -ForegroundColor Yellow
    Write-Host "正在安装..." -ForegroundColor Green
    pip install -r requirements.txt
}

# 检查.env文件
if (-not (Test-Path ".env")) {
    Write-Host "警告: .env文件不存在" -ForegroundColor Yellow
    Write-Host "请复制.env.example为.env并填入API密钥" -ForegroundColor Yellow
    pause
    exit
}

# 检查LM Studio
Write-Host "检查LM Studio服务..." -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "http://localhost:1234/v1/models" -Method GET -TimeoutSec 5
    Write-Host "✓ LM Studio服务正常运行" -ForegroundColor Green
} catch {
    Write-Host "✗ LM Studio服务未响应" -ForegroundColor Red
    Write-Host "请确保LM Studio已启动并运行在端口1234" -ForegroundColor Yellow
    $continue = Read-Host "是否继续？(y/n)"
    if ($continue -ne "y") {
        exit
    }
}

# 运行主程序
Write-Host "`n开始运行智能题库生成系统..." -ForegroundColor Green
Write-Host "================================`n" -ForegroundColor Green

python main.py

Write-Host "`n================================" -ForegroundColor Green
Write-Host "程序执行完成" -ForegroundColor Green
pause
