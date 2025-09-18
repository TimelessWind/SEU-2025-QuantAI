#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymysql
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'quantitative_trading',
    'charset': 'utf8mb4'
}

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        logger.info("成功连接到数据库")
        return connection
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        raise

def add_missing_columns():
    """向User表添加缺失的列"""
    connection = None
    cursor = None
    try:
        # 连接数据库
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 检查login_attempts列是否存在
        cursor.execute("SHOW COLUMNS FROM User LIKE 'login_attempts'")
        column_exists = cursor.fetchone()
        
        if not column_exists:
            # 添加缺失的列
            logger.info("向User表添加缺失的列...")
            
            # 添加login_attempts列
            cursor.execute("ALTER TABLE User ADD COLUMN login_attempts INT DEFAULT 0")
            logger.info("已添加login_attempts列")
            
            # 添加locked_until列
            cursor.execute("ALTER TABLE User ADD COLUMN locked_until DATETIME NULL")
            logger.info("已添加locked_until列")
            
            # 添加last_failed_login列
            cursor.execute("ALTER TABLE User ADD COLUMN last_failed_login DATETIME NULL")
            logger.info("已添加last_failed_login列")
            
            # 添加索引
            cursor.execute("CREATE INDEX idx_locked_until ON User(locked_until)")
            cursor.execute("CREATE INDEX idx_last_failed_login ON User(last_failed_login)")
            logger.info("已添加索引")
            
            connection.commit()
        else:
            logger.info("User表已经包含login_attempts列，无需添加")
        
        # 检查管理员用户是否存在
        cursor.execute("SELECT 1 FROM User WHERE user_account = 'admin'")
        admin_exists = cursor.fetchone()
        
        if not admin_exists:
            # 添加管理员用户
            logger.info("添加管理员用户...")
            admin_id = f"user_{int(datetime.now().timestamp() * 1000)}"
            cursor.execute("""
                INSERT INTO User (user_id, user_account, user_password, user_role, user_status, user_email, user_phone)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                admin_id, 'admin', 'e10adc3949ba59abbe56e057f20f883e', 'admin', 'active',
                'admin@example.com', '13800138000'
            ))
            logger.info("已添加管理员用户，账号: admin, 密码: 123456")
        else:
            logger.info("管理员用户已存在")
        
        # 检查测试用户是否存在
        cursor.execute("SELECT 1 FROM User WHERE user_account = 'test_user'")
        test_user_exists = cursor.fetchone()
        
        if not test_user_exists:
            # 添加测试用户
            logger.info("添加测试用户...")
            test_user_id = f"user_{int(datetime.now().timestamp() * 1000) + 1}"
            cursor.execute("""
                INSERT INTO User (user_id, user_account, user_password, user_role, user_status, user_email, user_phone)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                test_user_id, 'test_user', 'e10adc3949ba59abbe56e057f20f883e', 'analyst', 'active',
                'test@example.com', '13800138001'
            ))
            logger.info("已添加测试用户，账号: test_user, 密码: 123456")
        else:
            logger.info("测试用户已存在")
        
        connection.commit()
        logger.info("数据库修复完成！")
        
    except Exception as e:
        logger.error(f"数据库修复失败: {e}")
        if connection:
            connection.rollback()
        raise
    finally:
        # 关闭游标和连接
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def main():
    """主函数"""
    print("=== 量化交易系统数据库修复工具 ===")
    try:
        add_missing_columns()
        print("数据库修复成功！")
        print("\n重要提示：")
        print("- 已向User表添加缺失的登录相关列")
        print("- 管理员账号：admin，密码：123456")
        print("- 测试账号：test_user，密码：123456")
    except Exception as e:
        print(f"数据库修复失败: {e}")
        print("请检查数据库连接和权限")

if __name__ == "__main__":
    main()