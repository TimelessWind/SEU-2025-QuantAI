@echo off

:: 设置编码为UTF-8，确保中文正常显示
chcp 65001 >nul

:: 检查当前目录
set CURRENT_DIR=%~dp0

:: 激活虚拟环境
call "%CURRENT_DIR%.venv\Scripts\activate.bat"

if %errorLevel% neq 0 (
    echo 错误：无法激活虚拟环境。
    echo 请尝试手动激活虚拟环境并运行脚本。
    pause
    exit /b 1
)

:: 运行stock_analysis_workflow.py脚本
python "%CURRENT_DIR%stock_analysis_workflow.py"

:: 检查脚本运行是否成功
if %errorLevel% neq 0 (
    echo 错误：脚本运行失败。
    pause
    exit /b 1
)

:: 脚本运行成功
pause