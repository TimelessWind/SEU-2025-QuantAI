#!/bin/bash

echo "=== 量化交易系统前端启动器 ==="

# 检查是否在正确的目录
if [ ! -f "package.json" ]; then
    echo "错误: 请在quant-frontend目录下运行此脚本"
    exit 1
fi

# 检查node_modules是否存在
if [ ! -d "node_modules" ]; then
    echo "正在安装前端依赖..."
    npm install
    if [ $? -ne 0 ]; then
        echo "依赖安装失败"
        exit 1
    fi
fi

echo "正在启动前端开发服务器..."
npm run dev





