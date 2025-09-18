import pymysql
import os
import hashlib
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库连接配置
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '123456'),
    'database': os.getenv('DB_NAME', 'quantitative_trading'),
    'port': int(os.getenv('DB_PORT', '3306'))
}

def hash_password(password):
    # 使用MD5哈希算法，与后端保持一致
    return hashlib.md5(password.encode()).hexdigest()

def reset_user_password(username, new_password):
    conn = None
    try:
        # 连接数据库
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        
        # 检查用户是否存在
        cursor.execute("SELECT user_account, user_password FROM user WHERE user_account = %s", (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"用户 '{username}' 不存在")
            return False
        
        user_account, current_password = user
        print(f"\n用户 '{user_account}' 当前密码哈希: {current_password}")
        
        # 生成新密码的哈希
        hashed_password = hash_password(new_password)
        print(f"新密码哈希: {hashed_password}")
        
        # 更新密码
        cursor.execute(
            "UPDATE user SET user_password = %s, login_attempts = 0, locked_until = NULL WHERE user_account = %s",
            (hashed_password, username)
        )
        conn.commit()
        
        print(f"\n✅ 用户 '{username}' 的密码已成功重置为: '{new_password}'")
        print(f"请使用新密码登录系统")
        return True
        
    except Exception as e:
        print(f"操作失败: {str(e)}")
        return False
    finally:
        # 关闭连接
        if conn:
            conn.close()

if __name__ == "__main__":
    # 重置test_user的密码为'123456'
    reset_user_password('test_user', '123456')