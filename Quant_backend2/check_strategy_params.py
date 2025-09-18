import pymysql

"""
检查strategy表中自定义策略的strategy_params列内容
"""

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
    
    # 查询自定义策略的详细信息，特别是strategy_params列
    print("自定义策略的详细信息:")
    cursor.execute('''
        SELECT strategy_id, strategy_name, strategy_params 
        FROM strategy 
        WHERE strategy_type = 'custom'
    ''')
    data = cursor.fetchall()
    
    for row in data:
        strategy_id, strategy_name, strategy_params = row
        print(f"策略ID: {strategy_id}")
        print(f"策略名称: {strategy_name}")
        print(f"策略参数: {strategy_params}")
        print("-" * 50)
    
    # 如果没有自定义策略，创建一个测试策略并查看结果
    if not data:
        print("没有找到自定义策略，创建一个测试策略...")
        
        # 插入一个测试策略
        test_params = "{\"param1\": 10, \"param2\": \"test\"}"
        cursor.execute('''
            INSERT INTO strategy 
            (strategy_id, strategy_name, strategy_type, creator_id, 
             strategy_desc, strategy_code, strategy_params)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (
            'test_strategy_params', 
            '测试策略参数', 
            'custom', 
            'system', 
            '测试策略参数保存',
            'print("test")',
            test_params
        ))
        conn.commit()
        
        # 查询刚刚插入的测试策略
        cursor.execute('''
            SELECT strategy_id, strategy_name, strategy_params 
            FROM strategy 
            WHERE strategy_id = 'test_strategy_params'
        ''')
        test_data = cursor.fetchone()
        if test_data:
            print(f"测试策略已创建:\n策略ID: {test_data[0]}\n策略名称: {test_data[1]}\n策略参数: {test_data[2]}")
    
finally:
    # 关闭游标和连接
    if cursor:
        cursor.close()
    if conn:
        conn.close()