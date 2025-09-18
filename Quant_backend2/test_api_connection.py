import requests
import json
import time
import pandas as pd
from datetime import datetime

# 设置API基本URL
BASE_URL = 'http://localhost:5000/api'

# 测试函数：直接调用后端API验证策略执行
def test_api_strategy_execution():
    print("=== 开始API接口测试 ===")
    print(f"API基础URL: {BASE_URL}")
    
    # 1. 准备策略代码
    strategy_code = '''
import pandas as pd
import numpy as np

# 双均线策略示例代码
def strategy(df):
    # 计算短期均线和长期均线 - 注意数据库中字段名为close_price
    df['short_ma'] = df['close_price'].rolling(window=5).mean()
    df['long_ma'] = df['close_price'].rolling(window=20).mean()
    
    # 初始化信号和持仓列
    df['signal'] = 0  # 0: 无操作, 1: 买入, -1: 卖出
    df['position'] = 0  # 0: 空仓, 1: 持仓
    
    # 生成交易信号：使用简化逻辑
    # 避免使用未来函数：确保有足够的数据计算均线
    start_idx = max(5, 20)  # 使用较大的窗口长度作为起始索引
    
    # 初始化持仓状态
    current_position = 0
    
    # 使用.loc索引避免SettingWithCopyWarning
    for i in range(start_idx, len(df)):
        # 简化的信号生成逻辑
        if df.loc[i, 'short_ma'] > df.loc[i, 'long_ma'] and current_position == 0:
            df.loc[i, 'signal'] = 1  # 买入信号
            current_position = 1
        elif df.loc[i, 'short_ma'] < df.loc[i, 'long_ma'] and current_position == 1:
            df.loc[i, 'signal'] = -1  # 卖出信号
            current_position = 0
    
    # 根据信号调整持仓 - 使用.loc索引
    for i in range(1, len(df)):
        if df.loc[i, 'signal'] == 1:
            df.loc[i, 'position'] = 1  # 买入并持有
        elif df.loc[i, 'signal'] == -1:
            df.loc[i, 'position'] = 0  # 卖出并空仓
        else:
            df.loc[i, 'position'] = df.loc[i-1, 'position']  # 保持之前的持仓
    
    return df
'''.strip()
    
    # 2. 构建请求参数
    request_data = {
        'stock_code': '600519.SH',
        'start_date': '2025-01-02',
        'end_date': '2025-06-30',
        'strategy_code': strategy_code,
        'initial_capital': 100000,
        'position_sizing': 'fixed',
        'params': {}
    }
    
    print("\n2. 发送策略执行请求...")
    print(f"请求股票代码: {request_data['stock_code']}")
    print(f"时间范围: {request_data['start_date']} 至 {request_data['end_date']}")
    
    # 3. 调用API执行策略
    try:
        response = requests.post(
            f'{BASE_URL}/strategy-editor/run',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(request_data)
        )
        
        print(f"\n3. API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n4. 分析API返回结果:")
            
            # 打印返回结果的结构
            print(f"返回结果类型: {type(result)}")
            print(f"返回结果键: {list(result.keys())}")
            
            # 检查是否有回测结果
            if 'backtest_result' in result:
                backtest_result = result['backtest_result']
                print("\n5. 回测结果详情:")
                print(f"回测结果键: {list(backtest_result.keys())}")
                
                # 提取并分析关键指标
                if 'metrics' in backtest_result:
                    metrics = backtest_result['metrics']
                    print("\n6. 回测指标:")
                    for key, value in metrics.items():
                        print(f"  {key}: {value}")
                
                # 检查交易次数
                if 'trade_count' in backtest_result:
                    print(f"\n7. 交易次数: {backtest_result['trade_count']}")
                else:
                    print("\n7. 未找到交易次数信息")
                
                # 检查信号数据
                if 'signals' in backtest_result:
                    signals = backtest_result['signals']
                    print(f"\n8. 信号数据: {len(signals)}条")
                    if len(signals) > 0:
                        print("信号示例:")
                        # 打印前3个信号
                        for i, signal in enumerate(signals[:3]):
                            print(f"  信号{i+1}: {signal}")
                    else:
                        print("  未生成任何交易信号")
                else:
                    print("\n8. 未找到信号数据")
                
                # 检查是否有错误信息
                if 'error' in backtest_result:
                    print(f"\n错误信息: {backtest_result['error']}")
            else:
                print("\n5. 未找到backtest_result字段")
                print(f"完整返回结果: {result}")
            
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"调用API时发生错误: {e}")
    
    print("\n=== API接口测试完成 ===")
    
# 测试函数：验证数据库连接
def test_database_connection():
    print("\n=== 测试数据库连接 ===")
    try:
        import sqlite3
        conn = sqlite3.connect('stock_data.db')
        cursor = conn.cursor()
        
        # 检查stock_daily表
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='stock_daily';")
        table_exists = cursor.fetchone()[0] > 0
        print(f"stock_daily表存在: {table_exists}")
        
        if table_exists:
            # 检查数据量
            cursor.execute("SELECT COUNT(*) FROM stock_daily WHERE stock_code='600519.SH';")
            count = cursor.fetchone()[0]
            print(f"股票600519.SH的数据条数: {count}")
            
            # 检查最近5条数据
            cursor.execute("SELECT trade_date, close_price FROM stock_daily WHERE stock_code='600519.SH' ORDER BY trade_date DESC LIMIT 5;")
            recent_data = cursor.fetchall()
            print("最近5条数据的收盘价:")
            for row in recent_data:
                print(f"  {row[0]}: {row[1]}")
        
        conn.close()
    except Exception as e:
        print(f"数据库连接测试失败: {e}")

# 主函数
def main():
    print("=== 前后端数据交互问题诊断 ===")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试API接口
    test_api_strategy_execution()
    
    # 测试数据库连接
    test_database_connection()
    
    # 输出可能的解决方案
    print("\n=== 可能的解决方案 ===")
    print("1. 检查前端接收数据的格式是否与后端返回的格式一致")
    print("2. 确认前端展示交易次数的逻辑是否正确处理了返回数据")
    print("3. 尝试使用不同的时间范围或股票代码进行测试")
    print("4. 考虑增加更明显的交易信号生成条件，确保在实际数据中能产生信号")
    print("5. 检查后端返回给前端的数据中是否正确包含了交易次数和信号信息")

if __name__ == "__main__":
    main()