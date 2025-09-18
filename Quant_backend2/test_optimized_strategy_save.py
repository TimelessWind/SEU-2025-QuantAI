import pymysql
import requests
import json
import time

# 配置信息
API_URL = "http://127.0.0.1:8000/api/strategy-editor/save"
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'quantitative_trading',
    'charset': 'utf8mb4'
}

# 测试策略数据
test_strategy = {
    "name": "测试策略_" + str(int(time.time())),
    "code": "def strategy(df):\n    # 简单双均线策略\n    df['MA5'] = df['close'].rolling(window=5).mean()\n    df['MA20'] = df['close'].rolling(window=20).mean()\n    df['signal'] = 0\n    df['signal'][5:] = np.where(df['MA5'][5:] > df['MA20'][5:], 1, 0)\n    df['position'] = df['signal'].diff()\n    return df",
    "description": "这是一个用于测试策略保存功能的测试策略",
    "parameters": {
        "short_period": 5,
        "long_period": 20
    }
}

def test_strategy_save():
    print("开始测试策略保存功能...")
    
    # 1. 发送保存请求到后端API
    print(f"发送保存请求到: {API_URL}")
    print(f"测试数据: {json.dumps(test_strategy, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            API_URL,
            headers={'Content-Type': 'application/json'},
            data=json.dumps(test_strategy, ensure_ascii=False)
        )
        
        print(f"API响应状态码: {response.status_code}")
        print(f"API响应内容: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"完整的响应数据: {response_data}")
            
            if response_data.get('success'):
                # 根据实际响应格式提取strategy_id
                strategy_id = response_data.get('data', {}).get('strategy_id')
                print(f"策略保存成功! 策略ID: {strategy_id}")
                
                # 2. 检查数据库中是否存在该策略
                if strategy_id:
                    check_database(strategy_id)
                else:
                    print("警告: 响应中未包含有效的strategy_id")
            else:
                print(f"策略保存失败: {response_data.get('message')}")
        else:
            print(f"API请求失败，状态码: {response.status_code}")
            
    except Exception as e:
        print(f"发送请求时发生错误: {str(e)}")

def check_database(strategy_id):
    print("\n检查数据库中是否存在该策略...")
    
    try:
        # 连接数据库
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 查询策略记录
        query = """
        SELECT `strategy`.`strategy_id`, 
            `strategy`.`strategy_name`, 
            `strategy`.`strategy_type`, 
            `strategy`.`creator_id`, 
            `strategy`.`strategy_desc`, 
            `strategy`.`strategy_code`, 
            `strategy`.`strategy_params`, 
            `strategy`.`create_time`, 
            `strategy`.`update_time` 
        FROM `quantitative_trading`.`strategy` 
        WHERE strategy_id = %s
        """
        
        cursor.execute(query, (strategy_id,))
        result = cursor.fetchone()
        
        if result:
            print("策略已成功保存到数据库!")
            print("数据库记录信息:")
            print(f"  strategy_id: {result['strategy_id']}")
            print(f"  strategy_name: {result['strategy_name']}")
            print(f"  strategy_type: {result['strategy_type']}")
            print(f"  creator_id: {result['creator_id']}")
            print(f"  strategy_desc: {result['strategy_desc']}")
            print(f"  create_time: {result['create_time']}")
        else:
            print("警告: 数据库中未找到该策略记录!")
            
        # 查询所有自定义策略以确认总数
        cursor.execute("""
        SELECT COUNT(*) as count 
        FROM `quantitative_trading`.`strategy` 
        WHERE strategy_type = 'custom'
        """)
        custom_strategy_count = cursor.fetchone()['count']
        print(f"\n当前数据库中自定义策略总数: {custom_strategy_count}")
        
    except Exception as e:
        print(f"查询数据库时发生错误: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    test_strategy_save()