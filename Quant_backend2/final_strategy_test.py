import pandas as pd
import numpy as np

# 创建测试数据
def create_test_data():
    # 创建有明显趋势变化的数据，便于观察信号生成
    dates = pd.date_range(start='2025-01-02', end='2025-06-30', freq='B')
    
    # 创建模拟价格数据：先上涨，再下跌，最后上涨
    np.random.seed(42)
    base_price = 1700
    price_changes = np.zeros(len(dates))
    
    # 第一阶段：上涨趋势
    for i in range(int(len(dates) * 0.3)):
        price_changes[i] = np.random.normal(2, 1)
    
    # 第二阶段：下跌趋势
    for i in range(int(len(dates) * 0.3), int(len(dates) * 0.7)):
        price_changes[i] = np.random.normal(-2, 1)
    
    # 第三阶段：上涨趋势
    for i in range(int(len(dates) * 0.7), len(dates)):
        price_changes[i] = np.random.normal(2, 1)
    
    # 计算价格序列
    prices = [base_price]
    for change in price_changes:
        prices.append(prices[-1] + change)
    prices = prices[1:]
    
    df = pd.DataFrame({
        'trade_date': dates,
        'close_price': prices
    })
    
    return df

# 测试修复后的策略
def test_fixed_strategy():
    print("\n=== 测试修复后的策略 ===")
    
    # 获取测试数据
    df = create_test_data()
    print(f"创建了{len(df)}条测试数据")
    
    # 计算均线
    df['short_ma'] = df['close_price'].rolling(window=5).mean()
    df['long_ma'] = df['close_price'].rolling(window=20).mean()
    
    # 初始化信号和持仓列
    df['signal'] = 0  # 0: 无操作, 1: 买入, -1: 卖出
    df['position'] = 0  # 0: 空仓, 1: 持仓
    
    # 应用修复后的信号生成逻辑
    start_idx = max(5, 20)  # 使用较大的窗口长度作为起始索引
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
    
    # 分析结果
    signal_count = df['signal'].abs().sum()
    print(f"\n生成的信号数量: {signal_count}")
    
    # 显示有信号的行
    signal_rows = df[df['signal'] != 0]
    if len(signal_rows) > 0:
        print("\n信号详情:")
        # 只显示前5个和后5个信号
        if len(signal_rows) > 10:
            display_rows = pd.concat([signal_rows.head(5), signal_rows.tail(5)])
        else:
            display_rows = signal_rows
            
        for i, row in display_rows.iterrows():
            print(f"日期: {row['trade_date'].date()}, 信号: {row['signal']}, 短期均线: {row['short_ma']:.2f}, 长期均线: {row['long_ma']:.2f}")
    
    # 验证结果
    if signal_count > 0:
        print("\n✅ 修复后的策略成功生成了交易信号！")
        return True
    else:
        print("\n❌ 修复后的策略仍然没有生成交易信号！")
        return False

if __name__ == "__main__":
    print("开始测试修复后的策略...")
    success = test_fixed_strategy()
    
    if success:
        print("\n=== 修复总结 ===")
        print("1. 问题原因: 原策略的交叉检测逻辑过于严格，要求相邻时间点必须发生交叉")
        print("2. 解决方案: 简化了信号生成逻辑，使用current_position变量跟踪持仓状态")
        print("3. 关键改进: 只要短期均线在长期均线上方且当前为空仓就买入，反之则卖出")
        print("4. 避免了pd.notna()方法调用，符合后端验证要求")
    else:
        print("\n需要进一步调整策略参数或逻辑。")