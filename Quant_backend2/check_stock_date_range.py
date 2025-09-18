# -*- coding: utf-8 -*-
"""
检查数据库中600519.SH股票数据的日期范围
"""

import pymysql

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'quantitative_trading',
    'charset': 'utf8mb4'
}

# 要检查的股票代码
STOCK_CODE = '600519.SH'


def check_date_range():
    """检查数据库中特定股票的数据日期范围"""
    try:
        # 连接数据库
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # 查询日期范围
        cursor.execute("SELECT MIN(trade_date), MAX(trade_date) FROM StockMarketData WHERE stock_code = %s", (STOCK_CODE,))
        date_range = cursor.fetchone()
        
        # 打印结果
        print("股票代码: " + STOCK_CODE)
        print("最小交易日期: " + str(date_range[0]))
        print("最大交易日期: " + str(date_range[1]))
        
        # 关闭连接
        cursor.close()
        connection.close()
        
    except Exception as e:
        print("发生错误: " + str(e))


if __name__ == "__main__":
    check_date_range()