import pandas as pd
import numpy as np
from datetime import datetime
import pymysql
import json

# 连接数据库获取实际数据
def get_real_stock_data():
    """从数据库获取实际的股票数据"""
    try:
        # 数据库连接参数
        db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '123456',  # 假设密码是123456
            'database': 'stock_data',
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }
        
        # 连接数据库
        connection = pymysql.connect(**db_config)
        print("成功连接数据库")
        
        # 查询数据
        query = """
        SELECT stock_code, trade_date, open_price, high_price, low_price, close_price, volume 
        FROM stock_daily 
        WHERE stock_code = %s AND trade_date BETWEEN %s AND %s 
        ORDER BY trade_date
        """
        
        stock_code = '600519.SH'
        start_date = '2025-01-02'
        end_date = '2025-06-30'
        
        with connection.cursor() as cursor:
            cursor.execute(query, (stock_code, start_date, end_date))
            results = cursor.fetchall()
            
        print(f"获取了{len(results)}条数据")
        
        # 转换为DataFrame
        df = pd.DataFrame(results)
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        
        return df
        
    except Exception as e:
        print(f"获取数据失败: {e}")
        return None
    finally:
        if 'connection' in locals():
            connection.close()

# 模拟策略执行过程
def simulate_strategy_execution(df):
    """模拟策略执行过程"""
    # 复制数据
    df_copy = df.copy()
    
    # 初始化信号和仓位
    df_copy['signal'] = 0
    df_copy['position'] = 0
    
    # 计算均线
    short_window = 5
    long_window = 20
    df_copy['short_ma'] = df_copy['close_price'].rolling(window=short_window).mean()
    df_copy['long_ma'] = df_copy['close_price'].rolling(window=long_window).mean()
    
    # 应用当前策略的信号生成逻辑
    start_idx = max(short_window, long_window)  # 使用较大的窗口长度
    current_position = 0
    
    # 跟踪应该生成信号的位置
    signal_count = 0
    
    # 打印数据概览
    print("\n数据概览:")
    print(f"数据长度: {len(df_copy)}")
    print(f"开始日期: {df_copy['trade_date'].min().date()}")
    print(f"结束日期: {df_copy['trade_date'].max().date()}")
    
    # 打印一些关键数据点
    print("\n部分数据样例 (包含均线):")
    sample_df = df_copy[['trade_date', 'close_price', 'short_ma', 'long_ma']].iloc[start_idx-5:start_idx+10]
    print(sample_df.to_string(index=False))
    
    # 尝试生成信号并记录过程
    print("\n信号生成过程:")
    for i in range(start_idx, len(df_copy)):
        short_ma = df_copy['short_ma'].iloc[i]
        long_ma = df_copy['long_ma'].iloc[i]
        date = df_copy['trade_date'].iloc[i].date()
        
        # 打印一些点来调试
        if i % 20 == 0:
            print(f"日期: {date}, 短期均线: {short_ma:.2f}, 长期均线: {long_ma:.2f}, 当前仓位: {current_position}")
        
        # 应用信号生成逻辑
        if pd.notna(short_ma) and pd.notna(long_ma):
            if short_ma > long_ma and current_position == 0:
                # 应该生成买入信号
                signal_count += 1
                print(f"✅ 买入信号: 日期={date}, short_ma={short_ma:.2f} > long_ma={long_ma:.2f}")
                current_position = 1
            elif short_ma < long_ma and current_position == 1:
                # 应该生成卖出信号
                signal_count += 1
                print(f"✅ 卖出信号: 日期={date}, short_ma={short_ma:.2f} < long_ma={long_ma:.2f}")
                current_position = 0
    
    print(f"\n总共应该生成{signal_count}个信号")
    
    # 分析均线关系
    analyze_ma_relationship(df_copy, start_idx)
    
    return signal_count

# 分析均线关系
def analyze_ma_relationship(df, start_idx):
    """分析均线之间的关系"""
    # 计算短期均线在长期均线上方的比例
    valid_data = df.iloc[start_idx:]
    valid_data = valid_data[valid_data['short_ma'].notna() & valid_data['long_ma'].notna()]
    
    if len(valid_data) == 0:
        print("没有有效的均线数据")
        return
    
    above_count = len(valid_data[valid_data['short_ma'] > valid_data['long_ma']])
    below_count = len(valid_data[valid_data['short_ma'] < valid_data['long_ma']])
    equal_count = len(valid_data[valid_data['short_ma'] == valid_data['long_ma']])
    
    above_ratio = above_count / len(valid_data) * 100
    below_ratio = below_count / len(valid_data) * 100
    
    print(f"\n均线关系分析:")
    print(f"有效数据点: {len(valid_data)}")
    print(f"短期均线在长期均线上方的比例: {above_ratio:.2f}% ({above_count}个点)")
    print(f"短期均线在长期均线下方的比例: {below_ratio:.2f}% ({below_count}个点)")
    print(f"短期均线等于长期均线的点: {equal_count}个")
    
    # 检查是否有趋势
    if above_ratio > 70:
        print("📈 市场呈现明显的上升趋势")
    elif below_ratio > 70:
        print("📉 市场呈现明显的下降趋势")
    else:
        print("📊 市场呈现震荡行情")

# 检查策略代码执行环境
def check_strategy_execution_env():
    """检查策略代码执行环境是否有问题"""
    print("\n=== 检查策略代码执行环境 ===")
    
    # 模拟前端策略代码
    strategy_code = """
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
    
    for i in range(start_idx, len(df)):
        # 简化的信号生成逻辑 - 不使用notna检查
        if df['short_ma'].iloc[i] > df['long_ma'].iloc[i] and current_position == 0:
            df['signal'].iloc[i] = 1  # 买入信号
            current_position = 1
        elif df['short_ma'].iloc[i] < df['long_ma'].iloc[i] and current_position == 1:
            df['signal'].iloc[i] = -1  # 卖出信号
            current_position = 0
    
    # 根据信号调整持仓
    for i in range(1, len(df)):
        if df['signal'].iloc[i] == 1:
            df['position'].iloc[i] = 1  # 买入并持有
        elif df['signal'].iloc[i] == -1:
            df['position'].iloc[i] = 0  # 卖出并空仓
        else:
            df['position'].iloc[i] = df['position'].iloc[i-1]  # 保持之前的持仓
    
    return df
"""
    
    # 创建一个简单的测试数据
    dates = pd.date_range(start='2025-01-02', end='2025-02-01', freq='B')
    prices = [1700, 1720, 1730, 1750, 1770, 1760, 1740, 1720, 1700, 1680, 1660, 1670, 1690, 1710, 1730]
    
    test_df = pd.DataFrame({
        'trade_date': dates[:len(prices)],
        'close_price': prices
    })
    
    # 模拟CustomStrategy中的执行环境
    try:
        # 初始化信号和仓位
        df = test_df.copy()
        df['signal'] = 0
        df['position'] = 0
        
        # 创建执行环境
        exec_globals = {
            'pd': pd,
            'np': np,
            'df': df,
            'len': len,
            'range': range,
            'enumerate': enumerate,
            'zip': zip,
            'min': min,
            'max': max,
            'sum': sum,
            'abs': abs,
            'round': round,
            'int': int,
            'float': float,
            'str': str,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'print': print,
            'sorted': sorted,
            'reversed': reversed,
        }
        
        # 编译和执行策略代码
        compiled_code = compile(strategy_code, '<strategy>', 'exec')
        exec(compiled_code, exec_globals)
        
        # 获取策略函数
        strategy_func = exec_globals.get('strategy')
        if strategy_func is None:
            print("❌ 策略代码中未定义'strategy'函数")
            return False
        
        # 执行策略
        result_df = strategy_func(df)
        
        # 检查结果
        signal_count = result_df['signal'].abs().sum()
        print(f"策略函数生成的信号数量: {signal_count}")
        print(f"信号详情:\n{result_df[result_df['signal'] != 0]}")
        
        if signal_count > 0:
            print("✅ 策略函数执行环境正常")
            return True
        else:
            print("❌ 策略函数执行环境有问题")
            return False
            
    except Exception as e:
        print(f"策略执行出错: {e}")
        return False

if __name__ == "__main__":
    print("开始调试策略信号生成问题...")
    
    # 1. 检查执行环境
    env_check = check_strategy_execution_env()
    
    # 2. 获取实际数据并测试
    if env_check:
        print("\n=== 使用实际数据测试策略 ===")
        df = get_real_stock_data()
        
        if df is not None and len(df) > 0:
            signal_count = simulate_strategy_execution(df)
            
            if signal_count == 0:
                print("\n结论: 市场数据可能不适合当前的双均线策略参数")
                print("建议: 尝试调整均线窗口长度或使用其他策略参数组合")
            else:
                print("\n结论: 策略逻辑本身没有问题，但在当前数据上可能因为某些原因没有生成信号")
                print("建议: 检查后端执行策略的完整流程")
    
    print("\n调试完成")