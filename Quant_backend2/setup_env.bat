@echo off

REM 批处理文件：用于运行PowerShell虚拟环境配置脚本

REM 设置编码为UTF-8，确保中文正常显示
chcp 65001 >nul

REM 检查是否以管理员身份运行
NET SESSION >nul 2>&1
if %errorLevel% neq 0 (
    echo 警告：建议以管理员身份运行此脚本，以获得更好的权限。
    echo 按任意键继续（或按Ctrl+C取消）...
    pause >nul
)

REM 运行PowerShell脚本
echo 正在启动虚拟环境配置脚本...
echo.
PowerShell -ExecutionPolicy Bypass -File "%~dp0setup_env.ps1"

REM 显示使用提示
cls
echo.
echo =======================================================
echo              环境配置已完成！
echo =======================================================
echo.
echo 重要提示：
echo 1. 请在激活虚拟环境的终端中运行Python脚本，而不是直接双击.py文件

echo 2. 如何激活虚拟环境并运行脚本：
echo    - 打开PowerShell或命令提示符

echo    - 导航到项目目录：cd d:\专业生产实习\Quant

echo    - 激活虚拟环境：.venv\Scripts\activate

echo    - 运行脚本：python stock_analysis_workflow.py

echo 3. 如果使用VS Code，请确保选择了正确的Python解释器（.venv\Scripts\python.exe）
echo =======================================================
echo.

pause