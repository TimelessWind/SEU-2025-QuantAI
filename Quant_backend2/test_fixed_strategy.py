import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# 创建测试数据
def generate_test_data():
    # 生成一些模拟股票数据，确保有明确的均线交叉点
    dates = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(100)]
    
    # 创建一个有明确趋势变化的数据，确保出现均线交叉
    prices = []
    current_price = 100
    
    # 第一部分：上涨趋势
    for i in range(40):
        current_price += np.random.normal(0.5, 0.3)
        prices.append(current_price)
    
    # 第二部分：下跌趋势
    for i in range(30):
        current_price -= np.random.normal(0.5, 0.3)
        prices.append(current_price)
    
    # 第三部分：上涨趋势
    for i in range(30):
        current_price += np.random.normal(0.5, 0.3)
        prices.append(current_price)
    
    df = pd.DataFrame({
        'trade_date': dates,
        'close_price': prices
    })
    
    # 设置索引为整数索引，模拟前端实际使用的DataFrame结构
    df.index = range(len(df))
    
    print(f"生成测试数据: {len(df)}条记录")
    print(f"价格范围: {min(prices):.2f} - {max(prices):.2f}")
    return df

# 修复后的策略函数 - 使用.loc索引
def fixed_strategy(df):
    # 计算短期均线和长期均线
    df['short_ma'] = df['close_price'].rolling(window=5).mean()
    df['long_ma'] = df['close_price'].rolling(window=20).mean()
    
    # 初始化信号和持仓列
    df['signal'] = 0  # 0: 无操作, 1: 买入, -1: 卖出
    df['position'] = 0  # 0: 空仓, 1: 持仓
    
    # 生成交易信号
    start_idx = max(5, 20)  # 使用较大的窗口长度作为起始索引
    
    # 初始化持仓状态
    current_position = 0
    
    # 使用.loc索引避免SettingWithCopyWarning
    for i in range(start_idx, len(df)):
        # 检查均线值是否有效
        if not np.isnan(df.loc[i, 'short_ma']) and not np.isnan(df.loc[i, 'long_ma']):
            # 简化的信号生成逻辑
            if df.loc[i, 'short_ma'] > df.loc[i, 'long_ma'] and current_position == 0:
                df.loc[i, 'signal'] = 1  # 买入信号
                current_position = 1
                print(f"在索引 {i}, 日期 {df.loc[i, 'trade_date']} 生成买入信号")
            elif df.loc[i, 'short_ma'] < df.loc[i, 'long_ma'] and current_position == 1:
                df.loc[i, 'signal'] = -1  # 卖出信号
                current_position = 0
                print(f"在索引 {i}, 日期 {df.loc[i, 'trade_date']} 生成卖出信号")
    
    # 根据信号调整持仓 - 使用.loc索引
    for i in range(1, len(df)):
        if df.loc[i, 'signal'] == 1:
            df.loc[i, 'position'] = 1  # 买入并持有
        elif df.loc[i, 'signal'] == -1:
            df.loc[i, 'position'] = 0  # 卖出并空仓
        else:
            df.loc[i, 'position'] = df.loc[i-1, 'position']  # 保持之前的持仓
    
    return df

# 测试函数
def test_strategy():
    print("=== 开始测试修复后的策略 ===")
    
    # 生成测试数据
    df = generate_test_data()
    
    # 应用修复后的策略
    result_df = fixed_strategy(df.copy())
    
    # 分析结果
    signals = result_df[result_df['signal'] != 0]
    print(f"\n=== 策略测试结果 ===")
    print(f"生成的交易信号数量: {len(signals)}")
    print("信号详情:")
    if len(signals) > 0:
        print(signals[['trade_date', 'close_price', 'signal', 'position', 'short_ma', 'long_ma']])
        
        # 验证position列是否正确更新
        positions = result_df[result_df['position'] != 0]
        print(f"\n持仓天数: {len(positions)}")
    else:
        print("未生成任何交易信号")
        
        # 检查均线数据
        print("\n检查均线数据是否有效:")
        na_short_ma = result_df['short_ma'].isna().sum()
        na_long_ma = result_df['long_ma'].isna().sum()
        print(f"短期均线缺失值数量: {na_short_ma}")
        print(f"长期均线缺失值数量: {na_long_ma}")
        
        # 打印部分均线数据
        print("\n部分均线数据示例:")
        print(result_df[['trade_date', 'close_price', 'short_ma', 'long_ma']].tail(20))
    
    print("\n=== 测试完成 ===")
    
    # 保存结果用于查看
    result_df.to_csv('strategy_test_result.csv', index=False)
    print("测试结果已保存到 strategy_test_result.csv")

# 运行测试
if __name__ == "__main__":
    test_strategy()