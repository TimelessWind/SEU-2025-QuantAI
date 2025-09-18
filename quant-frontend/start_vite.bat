@echo off
set NODE_PATH=C:\Program Files\nodejs\node.exe
set VITE_JS=node_modules\vite\bin\vite.js

REM 检查Node.js是否存在
if not exist "%NODE_PATH%" (
    echo 错误: 找不到Node.js
    pause
    exit /b 1
)

REM 检查vite.js是否存在
if not exist "%VITE_JS%" (
    echo 错误: 找不到vite.js，请先运行npm install
    pause
    exit /b 1
)

echo 正在启动Vite开发服务器...
"%NODE_PATH%" "%VITE_JS%"
pause