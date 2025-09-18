import pandas as pd
import numpy as np
import sys
import os

# 添加项目目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Quant_backend2.strategy_engine import BreakoutStrategy


def create_test_data():
    """创建带有明显趋势和突破的测试数据"""
    # 创建测试数据 - 100天的数据
    dates = pd.date_range(start='2023-01-01', periods=100)
    np.random.seed(42)  # 确保结果可重现
    
    # 创建一个有明显趋势和突破的DataFrame
    base_price = 100.0
    close_price = []
    
    # 第一部分：横盘震荡（前40天）
    for i in range(40):
        close_price.append(base_price + np.random.randn() * 2)
    
    # 第二部分：明显上升趋势和突破（接下来30天）
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
    
    # 第三部分：再次横盘震荡（最后30天）
    last_price = close_price[-1]
    for i in range(30):
        close_price.append(last_price + np.random.randn() * 3)
    
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
    
    return test_data


def test_breakout_backtest():
    """测试突破策略的完整回测流程"""
    # 创建测试数据
    test_data = create_test_data()
    
    # 初始化突破策略（使用用户配置的参数）
    strategy = BreakoutStrategy(lookback_period=20, breakout_threshold=0.0)
    
    # 生成信号
    signals = strategy.generate_signals(test_data)
    
    # 初始化回测引擎
    # 由于我们只是测试回测逻辑，不实际连接数据库
    class MockBacktestEngine:
        def simulate_trading(self, signals_df, initial_capital=100000.0, commission_rate=0.001):
            # 简化版的模拟交易实现，仅用于测试
            class MockResult:
                pass
            
            result = MockResult()
            result.initial_capital = initial_capital
            
            # 初始化
            capital = initial_capital
            position = 0  # 持仓数量
            entry_price = 0.0
            trades = []
            equity_curve = [initial_capital]
            
            for i, row in signals_df.iterrows():
                current_price = row['close_price']
                signal = row['signal']
                
                # 计算当前市值
                current_value = capital + position * current_price
                equity_curve.append(current_value)
                
                # 处理交易信号
                if signal == 1 and position == 0:  # 买入信号且无持仓
                    # 计算可买入数量
                    available_capital = capital * 0.95  # 保留5%现金
                    shares_to_buy = int(available_capital / current_price)
                    
                    if shares_to_buy > 0:
                        # 计算手续费
                        commission = shares_to_buy * current_price * commission_rate
                        total_cost = shares_to_buy * current_price + commission
                        
                        if total_cost <= capital:
                            position = shares_to_buy
                            capital -= total_cost
                            entry_price = current_price
                            
                            trades.append({
                                'date': row['trade_date'],
                                'action': 'buy',
                                'price': current_price,
                                'shares': shares_to_buy,
                            })
                
                elif signal == -1 and position > 0:  # 卖出信号且有持仓
                    # 卖出所有持仓
                    proceeds = position * current_price
                    commission = proceeds * commission_rate
                    net_proceeds = proceeds - commission
                    
                    capital += net_proceeds
                    
                    # 记录交易
                    trade_return = (current_price - entry_price) / entry_price
                    trades.append({
                        'date': row['trade_date'],
                        'action': 'sell',
                        'price': current_price,
                        'shares': position,
                        'trade_return': trade_return
                    })
                    
                    position = 0
                    entry_price = 0.0
            
            # 最后一天如果还有持仓，按收盘价卖出
            if position > 0:
                final_price = signals_df.iloc[-1]['close_price']
                proceeds = position * final_price
                commission = proceeds * commission_rate
                net_proceeds = proceeds - commission
                capital += net_proceeds
                
                trade_return = (final_price - entry_price) / entry_price
                trades.append({
                    'date': signals_df.iloc[-1]['trade_date'],
                    'action': 'sell',
                    'price': final_price,
                    'shares': position,
                    'trade_return': trade_return
                })
            
            # 设置结果
            result.final_capital = capital
            result.trades = trades
            result.equity_curve = equity_curve
            result.trade_count = len([t for t in trades if t['action'] == 'sell'])
            result.total_return = (capital - initial_capital) / initial_capital
            
            return result
    
    # 使用模拟回测引擎
    mock_engine = MockBacktestEngine()
    backtest_result = mock_engine.simulate_trading(signals)
    
    # 输出回测结果
    print("突破策略回测结果：")
    print(f"初始资金: {backtest_result.initial_capital:.2f}元")
    print(f"最终资金: {backtest_result.final_capital:.2f}元")
    print(f"总收益率: {backtest_result.total_return*100:.2f}%")
    print(f"交易次数: {backtest_result.trade_count}")
    print(f"生成的信号数量: {len(signals[signals['signal'] != 0])}")
    print(f"其中买入信号: {len(signals[signals['signal'] == 1])}")
    print(f"其中卖出信号: {len(signals[signals['signal'] == -1])}")
    
    if backtest_result.trades:
        print("\n交易记录摘要：")
        for i, trade in enumerate(backtest_result.trades[:5]):  # 只显示前5条交易记录
            print(f"交易{i+1}: {trade['date']} - {trade['action']} @ {trade['price']:.2f}")
        if len(backtest_result.trades) > 5:
            print(f"... 还有{len(backtest_result.trades)-5}条交易记录")
    
    return backtest_result


if __name__ == "__main__":
    test_breakout_backtest()