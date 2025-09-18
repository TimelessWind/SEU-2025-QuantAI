import pandas as pd
import numpy as np
import sys
import os

# 添加项目目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Quant_backend2.strategy_engine import BreakoutStrategy


def test_breakout_strategy():
    """测试突破策略是否能正确生成交易信号"""
    # 创建测试数据
    dates = pd.date_range(start='2023-01-01', periods=60)
    np.random.seed(42)  # 确保结果可重现
    
    # 创建一个有一些价格波动的DataFrame
    close_price = np.cumsum(np.random.randn(60)) + 100
    open_price = close_price + np.random.randn(60) * 0.5  # 开盘价略不同于收盘价
    high_price = np.maximum(open_price, close_price) + np.random.rand(60) * 2
    low_price = np.minimum(open_price, close_price) - np.random.rand(60) * 2
    
    # 故意在某些点创建突破情况
    high_price[20] = close_price[20] * 1.05  # 创建一个明显的高点
    high_price[40] = close_price[40] * 1.03  # 另一个高点
    close_price[21] = high_price[20] * 1.01  # 收盘价突破前高
    close_price[41] = high_price[40] * 1.01  # 另一个突破
    
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
    print("突破策略测试结果：")
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
        print("\n查看最近几天的数据以分析原因：")
        print(signals.tail(10)[['trade_date', 'close_price', 'high_max', 'low_min', 'upper_threshold', 'lower_threshold']])
    
    return signals


if __name__ == "__main__":
    test_breakout_strategy()