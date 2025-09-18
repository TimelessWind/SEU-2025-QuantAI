import pymysql
from strategy_engine import DB_DEFAULTS

# 连接数据库
conn = pymysql.connect(
    host=DB_DEFAULTS['host'],
    port=DB_DEFAULTS['port'],
    user=DB_DEFAULTS['user'],
    password=DB_DEFAULTS['password'],
    database=DB_DEFAULTS['database'],
    charset=DB_DEFAULTS['charset']
)

# 查询最近5条回测记录
print('最近5条回测记录:')
try:
    with conn.cursor() as cursor:
        # 查询记录数量
        cursor.execute('SELECT COUNT(*) FROM BacktestReport')
        total_count = cursor.fetchone()[0]
        print(f'总记录数: {total_count}')
        
        # 查询最近5条记录
        cursor.execute('SELECT report_id, user_id, stock_code, total_return, report_status FROM BacktestReport ORDER BY report_generate_time DESC LIMIT 5')
        results = cursor.fetchall()
        
        # 打印结果
        print('\n最近5条回测记录:')
        for row in results:
            print(f'report_id: {row[0]}, user_id: {row[1]}, stock_code: {row[2]}, total_return: {row[3]}, status: {row[4]}')
finally:
    # 关闭连接
    conn.close()