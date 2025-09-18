import pandas as pd
import numpy as np
import sys
import os

# 添加项目目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Quant_backend2.strategy_engine import BreakoutStrategy


def test_breakout_strategy_improved():
    """改进版的突破策略测试，创建更明显的突破模式"""
    # 创建测试数据 - 60天的数据
    dates = pd.date_range(start='2023-01-01', periods=60)
    np.random.seed(42)  # 确保结果可重现
    
    # 创建一个有明显趋势和突破的DataFrame
    base_price = 100.0
    close_price = []
    
    # 第一部分：横盘震荡（前30天）
    for i in range(30):
        close_price.append(base_price + np.random.randn() * 2)
    
    # 第二部分：明显上升趋势和突破（后30天）
    for i in range(30):
        if i < 10:
            # 缓慢上升
            close_price.append(close_price[-1] + np.random.rand() * 0.5)
        elif i == 10:
            # 明显突破
            close_price.append(close_price[-1] * 1.05)  # 5%的上涨突破
        else:
            # 继续上升
            close_price.append(close_price[-1] + np.random.rand() * 0.8)
    
    # 基于收盘价生成开盘价、最高价和最低价
    open_price = [p + np.random.randn() * 0.5 for p in close_price]
    high_price = [max(o, c) + np.random.rand() * 1.5 for o, c in zip(open_price, close_price)]
    low_price = [min(o, c) - np.random.rand() * 1.5 for o, c in zip(open_price, close_price)]
    
    test_data = pd.DataFrame({
        'trade_date': dates,
        'open_price': open_price,
        'high_price': high_price,
        'low_price': low_price,
        'close_price': close_price
    })
    
    # 初始化突破策略（使用用户配置的参数）
    strategy = BreakoutStrategy(lookback_period=20, breakout_threshold=0.0)
    
    # 生成信号
    signals = strategy.generate_signals(test_data)
    
    # 输出结果
    print("突破策略改进版测试结果：")
    print(f"总数据行数: {len(signals)}")
    print(f"买入信号数量: {len(signals[signals['signal'] == 1])}")
    print(f"卖出信号数量: {len(signals[signals['signal'] == -1])}")
    
    # 显示有信号的行
    signal_rows = signals[signals['signal'] != 0]
    if not signal_rows.empty:
        print("\n信号详情：")
        print(signal_rows[['trade_date', 'close_price', 'high_max', 'low_min', 'upper_threshold', 'lower_threshold', 'signal']])
    else:
        print("\n未生成任何交易信号！")
        # 查看可能应该有信号的位置
        print("\n查看突破点附近的数据：")
        print(signals.iloc[25:40][['trade_date', 'close_price', 'high_max', 'low_min', 'upper_threshold', 'lower_threshold']])
    
    return signals


if __name__ == "__main__":
    test_breakout_strategy_improved()