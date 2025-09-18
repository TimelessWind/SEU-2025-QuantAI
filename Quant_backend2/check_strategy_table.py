import pymysql

try:
    # 连接数据库
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='123456',
        database='quantitative_trading',
        charset='utf8mb4'
    )
    
    # 创建游标
    cursor = conn.cursor()
    
    # 查询strategy表结构
    print("Strategy表结构:")
    cursor.execute('DESCRIBE strategy')
    result = cursor.fetchall()
    for row in result:
        print(row)
    
    # 查询策略数据（如果有）
    print("\nStrategy表中的数据:")
    cursor.execute('SELECT strategy_id, strategy_name, strategy_type FROM strategy LIMIT 5')
    data = cursor.fetchall()
    for row in data:
        print(row)
    
finally:
    # 关闭游标和连接
    if cursor:
        cursor.close()
    if conn:
        conn.close()