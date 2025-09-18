import pandas as pd
import numpy as np

# 创建一个简单的测试数据集
def create_test_data():
    dates = pd.date_range(start='2025-01-02', end='2025-02-01', freq='B')
    
    # 创建有明显趋势的数据，以便于观察均线交叉
    prices = [1700, 1720, 1730, 1750, 1770, 1760, 1740, 1720, 1700, 1680, 1660, 1670, 1690, 1710, 1730]
    
    df = pd.DataFrame({
        'trade_date': dates[:len(prices)],
        'close_price': prices
    })
    return df

# 测试当前策略代码
def test_current_strategy():
    print("\n=== 测试当前默认策略 ===")
    
    # 获取测试数据
    df = create_test_data()
    print(f"测试数据:\n{df}\n")
    
    # 计算均线
    df['short_ma'] = df['close_price'].rolling(window=5).mean()
    df['long_ma'] = df['close_price'].rolling(window=10).mean()
    
    # 初始化信号
    df['signal'] = 0
    
    # 应用当前策略的信号生成逻辑
    start_idx = max(5, 10)  # 使用较大的窗口长度
    for i in range(start_idx, len(df)):
        # 简化条件，不使用notna
        if df['short_ma'].iloc[i] > df['long_ma'].iloc[i] and df['short_ma'].iloc[i-1] <= df['long_ma'].iloc[i-1]:
            df['signal'].iloc[i] = 1  # 买入信号
        elif df['short_ma'].iloc[i] < df['long_ma'].iloc[i] and df['short_ma'].iloc[i-1] >= df['long_ma'].iloc[i-1]:
            df['signal'].iloc[i] = -1  # 卖出信号
    
    # 打印结果
    print(f"策略应用后的数据:\n{df}\n")
    print(f"生成的信号数量: {df['signal'].abs().sum()}")
    print(f"信号详情:\n{df[df['signal'] != 0]}")
    
    return df

# 测试简化版策略
def test_simplified_strategy():
    print("\n=== 测试简化版策略 ===")
    
    # 获取测试数据
    df = create_test_data()
    
    # 计算均线
    df['short_ma'] = df['close_price'].rolling(window=5).mean()
    df['long_ma'] = df['close_price'].rolling(window=10).mean()
    
    # 初始化信号
    df['signal'] = 0
    
    # 使用简化的信号生成逻辑
    for i in range(10, len(df)):
        if df['short_ma'].iloc[i] > df['long_ma'].iloc[i]:
            df['signal'].iloc[i] = 1  # 买入信号
        else:
            df['signal'].iloc[i] = -1  # 卖出信号
    
    # 打印结果
    print(f"简化版策略应用后的数据:\n{df}\n")
    print(f"生成的信号数量: {df['signal'].abs().sum()}")
    print(f"信号详情:\n{df[df['signal'] != 0]}")
    
    return df

if __name__ == "__main__":
    print("开始测试策略信号生成...")
    
    # 测试当前策略
    current_df = test_current_strategy()
    
    # 测试简化版策略
    simplified_df = test_simplified_strategy()
    
    # 分析结果
    current_signals = current_df['signal'].abs().sum()
    simplified_signals = simplified_df['signal'].abs().sum()
    
    print("\n=== 测试总结 ===")
    print(f"当前策略生成信号: {'成功' if current_signals > 0 else '失败'}")
    print(f"简化版策略生成信号: {'成功' if simplified_signals > 0 else '失败'}")
    
    if current_signals == 0:
        print("\n问题分析:")
        print("1. 当前策略的交叉检测逻辑可能过于严格，难以满足条件")
        print("2. 建议简化信号生成逻辑，使用更直接的条件判断")
        print("3. 可以考虑使用pandas的shift()函数来检测交叉点")