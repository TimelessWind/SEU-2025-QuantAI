import pymysql

# 连接数据库
conn = pymysql.connect(
    host='localhost',
    port=3306,
    user='root',
    password='123456',
    database='quantitative_trading'
)

try:
    # 创建游标
    cursor = conn.cursor()
    
    # 查询StockMarketData表中的最大交易日期
    cursor.execute('SELECT MAX(trade_date) FROM StockMarketData')
    max_date = cursor.fetchone()[0]
    print('数据库中最新的交易日期:', max_date)
    
    # 查询指定日期范围的数据量
    cursor.execute("SELECT COUNT(*) FROM StockMarketData WHERE trade_date BETWEEN '2024-09-16' AND '2025-09-16'")
    count = cursor.fetchone()[0]
    print('2024-09-16到2025-09-16期间的数据量:', count)
    
    # 查询2025-01-06之后的数据量
    cursor.execute("SELECT COUNT(*) FROM StockMarketData WHERE trade_date > '2025-01-06'")
    count_after = cursor.fetchone()[0]
    print('2025-01-06之后的数据量:', count_after)
    
finally:
    # 关闭游标和连接
    cursor.close()
    conn.close()