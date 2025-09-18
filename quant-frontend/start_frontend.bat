@echo off
echo === 量化交易系统前端启动器 ===

REM 检查是否在正确的目录
if not exist "package.json" (
    echo 错误: 请在quant-frontend目录下运行此脚本
    pause
    exit /b 1
)

REM 检查node_modules是否存在
if not exist "node_modules" (
    echo 正在安装前端依赖...
    call npm install
    if errorlevel 1 (
        echo 依赖安装失败
        pause
        exit /b 1
    )
)

echo 正在启动前端开发服务器...
call npm run dev

pause





