# -*- coding: utf-8 -*-
"""
用于在BacktestReport表中添加strategy_params字段的脚本
"""

import pymysql
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 数据库配置
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "database": "quantitative_trading",
    "charset": "utf8mb4",
}

def add_strategy_params_column():
    """在BacktestReport表中添加strategy_params字段"""
    connection = None
    try:
        # 连接数据库
        logger.info("连接数据库...")
        connection = pymysql.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            charset=DB_CONFIG["charset"],
            autocommit=False
        )
        logger.info("数据库连接成功")
        
        # 创建游标
        cursor = connection.cursor()
        
        # 执行ALTER TABLE语句添加字段
        alter_sql = "ALTER TABLE BacktestReport ADD COLUMN strategy_params LONGTEXT NULL COMMENT '策略参数，JSON格式'"
        cursor.execute(alter_sql)
        connection.commit()
        
        logger.info("成功在BacktestReport表中添加strategy_params字段")
        
    except Exception as e:
        # 如果字段已存在，也认为是成功的
        if "Duplicate column name" in str(e):
            logger.info("strategy_params字段已存在")
            if connection:
                connection.rollback()
        else:
            logger.error(f"添加字段失败: {e}")
            if connection:
                connection.rollback()
            raise
    finally:
        if connection:
            connection.close()
            logger.info("数据库连接已关闭")

if __name__ == "__main__":
    add_strategy_params_column()