#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查数据库中回测结果的精度问题
"""

import pymysql
import json

# 数据库配置
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "database": "quantitative_trading",
    "charset": "utf8mb4",
}


def check_backtest_data_precision():
    """检查回测数据的精度"""
    try:
        # 连接数据库
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # 查询最近的回测结果，获取原始精度数据
        query = """
        SELECT 
            report_id,
            CAST(annual_return AS CHAR) AS annual_return_str,
            CAST(win_rate AS CHAR) AS win_rate_str,
            CAST(total_return AS CHAR) AS total_return_str,
            CAST(max_drawdown AS CHAR) AS max_drawdown_str
        FROM BacktestReport
        ORDER BY report_generate_time DESC
        LIMIT 5
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        print("数据库中回测结果的精度检查:")
        print("----------------------------------------")
        
        for row in results:
            report_id = row[0]
            annual_return_str = row[1]
            win_rate_str = row[2]
            total_return_str = row[3]
            max_drawdown_str = row[4]
            
            print(f"报告ID: {report_id}")
            print(f"年化收益率原始值: {annual_return_str}")
            print(f"胜率原始值: {win_rate_str}")
            print(f"总收益率原始值: {total_return_str}")
            print(f"最大回撤原始值: {max_drawdown_str}")
            print("----------------------------------------")
        
        # 查看表结构，确认字段类型
        cursor.execute("DESCRIBE BacktestReport")
        table_structure = cursor.fetchall()
        
        print("\nBacktestReport表结构:")
        print("----------------------------------------")
        for field in table_structure:
            field_name, field_type = field[0], field[1]
            if field_name in ['annual_return', 'win_rate', 'total_return', 'max_drawdown']:
                print(f"字段: {field_name}, 类型: {field_type}")
        
    except Exception as e:
        print(f"查询失败: {e}")
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    check_backtest_data_precision()