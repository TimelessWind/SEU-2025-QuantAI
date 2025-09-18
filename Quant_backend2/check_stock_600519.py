# -*- coding: utf-8 -*-
"""
检查数据库中600519.SH股票数据是否存在的测试脚本
"""

import pymysql
import pandas as pd
from datetime import datetime, timedelta

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


def test_stock_data_exists():
    """测试数据库中是否存在特定股票的数据"""
    connection = None
    cursor = None
    
    try:
        # 连接数据库
        print(f"\n===== 开始检查股票{STOCK_CODE}的数据 =====")
        print("连接数据库...")
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        print("数据库连接成功")
        
        # 检查StockMarketData表是否存在
        cursor.execute("SHOW TABLES LIKE 'StockMarketData'")
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            print("❌ 错误: StockMarketData表不存在")
            return False
        
        print("✓ StockMarketData表存在")
        
        # 检查表结构
        cursor.execute("SHOW COLUMNS FROM StockMarketData")
        columns = [row[0] for row in cursor.fetchall()]
        print(f"表结构: {', '.join(columns)}")
        
        # 检查是否有600519.SH的数据
        print(f"\n查询股票{STOCK_CODE}的数据...")
        
        # 查询总记录数
        sql_count = "SELECT COUNT(*) FROM StockMarketData WHERE stock_code = %s"
        cursor.execute(sql_count, (STOCK_CODE,))
        total_count = cursor.fetchone()[0]
        print(f"股票{STOCK_CODE}的总记录数: {total_count}")
        
        if total_count == 0:
            print("❌ 未找到该股票的数据")
            
            # 检查是否有其他股票数据
            cursor.execute("SELECT COUNT(DISTINCT stock_code) FROM StockMarketData")
            total_stocks = cursor.fetchone()[0]
            print(f"数据库中共有{total_stocks}只不同的股票")
            
            if total_stocks > 0:
                # 显示部分其他股票代码
                cursor.execute("SELECT DISTINCT stock_code FROM StockMarketData LIMIT 5")
                sample_stocks = [row[0] for row in cursor.fetchall()]
                print(f"示例股票代码: {', '.join(sample_stocks)}")
            
            return False
        
        # 查询最近的10条记录
        sql_recent = """
        SELECT stock_code, trade_date, open_price, high_price, low_price, close_price, volume 
        FROM StockMarketData 
        WHERE stock_code = %s 
        ORDER BY trade_date DESC 
        LIMIT 10
        """
        cursor.execute(sql_recent, (STOCK_CODE,))
        recent_data = cursor.fetchall()
        
        # 显示最近的数据
        print(f"\n最近的10条交易数据:")
        print("{:<12} {:<12} {:<10} {:<10} {:<10} {:<10} {:<12}".format(
            'stock_code', 'trade_date', 'open', 'high', 'low', 'close', 'volume'))
        print("-" * 80)
        
        for row in recent_data:
            print("{:<12} {:<12} {:<10.2f} {:<10.2f} {:<10.2f} {:<10.2f} {:<12,d}".format(
                row[0], str(row[1]), row[2], row[3], row[4], row[5], row[6]))
        
        # 检查数据时间范围
        cursor.execute("""
        SELECT MIN(trade_date), MAX(trade_date) 
        FROM StockMarketData 
        WHERE stock_code = %s
        """, (STOCK_CODE,))
        date_range = cursor.fetchone()
        print(f"\n数据时间范围: {date_range[0]} 至 {date_range[1]}")
        
        # 检查是否有最近一个月的数据
        one_month_ago = datetime.now() - timedelta(days=30)
        cursor.execute("""
        SELECT COUNT(*) 
        FROM StockMarketData 
        WHERE stock_code = %s AND trade_date >= %s
        """, (STOCK_CODE, one_month_ago.strftime('%Y-%m-%d')))
        recent_month_count = cursor.fetchone()[0]
        print(f"最近一个月的数据量: {recent_month_count}")
        
        print("\n✓ 股票数据检查完成")
        return True
        
    except Exception as e:
        print(f"❌ 检查过程中发生错误: {str(e)}")
        return False
    
    finally:
        # 关闭数据库连接
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            print("数据库连接已关闭")


if __name__ == "__main__":
    success = test_stock_data_exists()
    
    if success:
        print("\n✅ 股票数据检查成功")
    else:
        print("\n❌ 股票数据检查失败")
        print("\n建议的解决方案:")
        print("1. 确认数据库中是否存在600519.SH的股票数据")
        print("2. 如果不存在，可能需要使用数据获取脚本导入数据")
        print("3. 检查策略回测时使用的日期范围是否在数据库数据范围内")
        print("4. 验证股票代码格式是否正确（例如'SH'后缀是否正确）")