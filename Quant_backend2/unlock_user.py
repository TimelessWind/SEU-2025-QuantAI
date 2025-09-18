import pymysql
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库连接配置
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '123456'),
    'database': os.getenv('DB_NAME', 'quantitative_trading'), # 使用正确的数据库名称
    'port': int(os.getenv('DB_PORT', '3306'))
}

def check_and_unlock_user(username):
    conn = None
    try:
        # 连接数据库
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        
        # 检查用户状态
        cursor.execute("""SELECT user_id, user_account, user_status, login_attempts, locked_until 
                         FROM user WHERE user_account = %s""", (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"用户 '{username}' 不存在")
            return False
        
        user_id, user_account, user_status, login_attempts, locked_until = user
        print(f"\n用户信息:")
        print(f"用户ID: {user_id}")
        print(f"用户账户: {user_account}")
        print(f"状态: {'正常' if user_status == 'active' else user_status}")
        print(f"登录尝试次数: {login_attempts}")
        print(f"锁定时间: {locked_until}")
        
        # 如果账户被锁定或有登录失败记录，重置登录尝试次数
        if login_attempts > 0 or locked_until is not None:
            print(f"\n用户 '{user_account}' 有登录失败记录，正在重置...")
            
            # 重置登录尝试次数和锁定状态
            cursor.execute("""UPDATE user 
                             SET login_attempts = 0, locked_until = NULL 
                             WHERE user_id = %s""", (user_id,))
            conn.commit()
            
            print(f"用户 '{username}' 登录状态已重置成功")
            return True
        else:
            print(f"\n用户 '{username}' 状态正常，无需重置")
            return True
        
    except Exception as e:
        print(f"操作失败: {str(e)}")
        return False
    finally:
        # 关闭连接
        if conn:
            conn.close()

if __name__ == "__main__":
    # 重置test_user账户
    check_and_unlock_user('test_user')