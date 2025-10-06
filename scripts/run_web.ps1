# Windows启动脚本 - 运行Web监控界面

# 激活虚拟环境（如果存在）
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "激活虚拟环境..." -ForegroundColor Green
    .\venv\Scripts\Activate.ps1
}

Write-Host "启动Web监控界面..." -ForegroundColor Green
Write-Host "访问地址: http://localhost:5000" -ForegroundColor Cyan
Write-Host "按 Ctrl+C 停止服务`n" -ForegroundColor Yellow

python web_ui.py
