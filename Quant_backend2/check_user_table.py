#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查用户表中的用户ID
"""

import pymysql
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库连接配置
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '123456'),
    'database': os.getenv('DB_NAME', 'quantitative_trading'),
    'port': int(os.getenv('DB_PORT', '3306'))
}

def check_user_table():
    """检查用户表中的用户ID"""
    conn = None
    try:
        # 连接数据库
        conn = pymysql.connect(**db_config)
        print("成功连接到数据库")
        
        cursor = conn.cursor()
        
        # 查询用户表结构
        cursor.execute("DESCRIBE user")
        print("用户表结构:")
        for field in cursor.fetchall():
            print(field)
        
        # 查询用户表中的用户ID
        cursor.execute("SELECT user_id, user_account FROM user")
        users = cursor.fetchall()
        
        if users:
            print(f"\n发现 {len(users)} 个用户:")
            for user in users:
                user_id, user_account = user
                print(f"- 用户ID: {user_id}, 用户账号: {user_account}")
        else:
            print("\n用户表为空")
        
    except Exception as e:
        print(f"查询用户表失败: {e}")
    finally:
        # 关闭连接
        if conn:
            conn.close()

def main():
    """主函数"""
    check_user_table()

if __name__ == '__main__':
    main()