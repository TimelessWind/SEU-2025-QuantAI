import pymysql
import json
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

try:
    # 创建游标
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # 执行查询
    cursor.execute('''
        SELECT report_id, annual_return, win_rate, trade_count, final_fund, total_return 
        FROM BacktestReport 
        ORDER BY report_generate_time DESC 
        LIMIT 10
    ''')
    
    # 获取结果
    results = cursor.fetchall()
    
    # 打印结果
    print(json.dumps(results, ensure_ascii=False, default=str))
    
except Exception as e:
    print(f"查询出错: {e}")
finally:
    # 关闭游标和连接
    if cursor:
        cursor.close()
    if conn:
        conn.close()