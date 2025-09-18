#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查看数据库表结构
"""

import pymysql
from backtest_engine import DB_DEFAULTS


def check_table_structure():
    """检查BacktestReport表的结构"""
    try:
        # 连接数据库
        conn = pymysql.connect(
            host=DB_DEFAULTS["host"],
            port=DB_DEFAULTS["port"],
            user=DB_DEFAULTS["user"],
            password=DB_DEFAULTS["password"],
            database=DB_DEFAULTS["database"],
            charset=DB_DEFAULTS["charset"]
        )
        
        # 创建游标
        cursor = conn.cursor()
        
        # 查询表结构
        cursor.execute('DESCRIBE BacktestReport')
        
        # 打印结果
        print("BacktestReport表结构:")
        print("--------------------------------------")
        print("字段名		数据类型	键	额外信息")
        print("--------------------------------------")
        for row in cursor.fetchall():
            field_name = row[0]
            data_type = row[1]
            key = row[2]
            extra = row[5]
            print(f"{field_name}		{data_type}	{key}	{extra}")
        
        # 关闭连接
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"查询表结构失败: {e}")


if __name__ == "__main__":
    check_table_structure()