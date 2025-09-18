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
    
    # 查询一些股票代码示例
    cursor.execute('SELECT DISTINCT stock_code FROM StockMarketData LIMIT 5')
    stock_codes = [row[0] for row in cursor.fetchall()]
    print('数据库中的股票代码示例:', stock_codes)
    
    # 如果有股票代码，查询其中一个在2024-09-16到2025-09-16期间的数据范围
    if stock_codes:
        sample_stock = stock_codes[0]
        print(f'\n检查股票 {sample_stock} 的数据范围:')
        
        # 查询该股票的最小和最大交易日期
        cursor.execute('SELECT MIN(trade_date), MAX(trade_date) FROM StockMarketData WHERE stock_code = %s', (sample_stock,))
        min_date, max_date = cursor.fetchone()
        print(f'该股票的日期范围: {min_date} 到 {max_date}')
        
        # 查询该股票在2025-01-06到2025-06-30期间的数据量
        cursor.execute("SELECT COUNT(*) FROM StockMarketData WHERE stock_code = %s AND trade_date BETWEEN '2025-01-06' AND '2025-06-30'", (sample_stock,))
        count = cursor.fetchone()[0]
        print(f'该股票在2025-01-06到2025-06-30期间的数据量: {count}')
    
finally:
    # 关闭游标和连接
    cursor.close()
    conn.close()