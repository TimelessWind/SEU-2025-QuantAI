#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

print(f"Python解释器路径: {sys.executable}")
print(f"Python版本: {sys.version}")
print(f"当前工作目录: {os.getcwd()}")
print(f"模块搜索路径: {sys.path}")

# 尝试导入tushare
try:
    import tushare as ts
    print(f"tushare库导入成功！版本: {ts.__version__}")
    
    # 检查tushare安装路径
    print(f"tushare安装路径: {ts.__file__}")
    
    print("\n测试成功！tushare库可以正常使用。")
except ImportError as e:
    print(f"导入tushare失败: {e}")
    print("\n可能的解决方案：")
    print("1. 确认是否在正确的Python环境中运行")
    print("2. 尝试使用'pip install tushare --upgrade'更新库")
    print("3. 检查是否有模块命名冲突（是否有文件名为tushare.py）")
except Exception as e:
    print(f"发生其他错误: {e}")