import pymysql

def modify_strategy_table():
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
        
        # 查询是否已经有strategy_code和strategy_params列
        cursor.execute('DESCRIBE strategy')
        columns = [row[0] for row in cursor.fetchall()]
        
        # 添加strategy_code列（如果不存在）
        if 'strategy_code' not in columns:
            print("添加strategy_code列...")
            cursor.execute('ALTER TABLE strategy ADD COLUMN strategy_code LONGTEXT AFTER strategy_desc')
        
        # 添加strategy_params列（如果不存在）
        if 'strategy_params' not in columns:
            print("添加strategy_params列...")
            cursor.execute('ALTER TABLE strategy ADD COLUMN strategy_params LONGTEXT AFTER strategy_code')
        
        # 提交更改
        conn.commit()
        print("策略表修改成功！")
        
        # 显示修改后的表结构
        print("\n修改后的Strategy表结构:")
        cursor.execute('DESCRIBE strategy')
        result = cursor.fetchall()
        for row in result:
            print(row)
        
    except Exception as e:
        print(f"修改表结构失败: {e}")
        # 发生错误时回滚
        if conn:
            conn.rollback()
    finally:
        # 关闭游标和连接
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    modify_strategy_table()