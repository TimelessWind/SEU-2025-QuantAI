import pymysql
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库连接配置（不指定数据库）
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '123456'),
    'port': int(os.getenv('DB_PORT', '3306'))
}

def list_all_databases():
    try:
        # 连接数据库但不指定具体数据库
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        
        # 查询所有数据库
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        
        print("系统中所有可用的数据库：")
        for db in databases:
            print(f"- {db[0]}")
        
        return True
    except Exception as e:
        print(f"操作失败: {str(e)}")
        return False
    finally:
        # 关闭连接
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    list_all_databases()