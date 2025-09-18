#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import sys
import os

def install_requirements():
    """安装Flask依赖"""
    print("正在安装Flask依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "flask_requirements.txt"])
        print("Flask依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"依赖安装失败: {e}")
        return False

def start_flask_app():
    """启动Flask应用"""
    print("正在启动Flask后端服务...")
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n后端服务已停止")

def main():
    """主函数"""
    print("=== 量化交易系统后端启动器 ===")
    
    # 检查是否在正确的目录
    if not os.path.exists("app.py"):
        print("错误: 请在Quant_backend2目录下运行此脚本")
        return
    
    # 安装依赖
    if not install_requirements():
        print("依赖安装失败，请手动安装")
        return
    
    # 启动应用
    start_flask_app()

if __name__ == "__main__":
    main()





