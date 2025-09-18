# -*- coding: utf-8 -*-
"""
测试自定义策略完整回测流程的脚本
用于排查为什么回测结果所有指标都是0的问题
"""
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# 添加项目路径到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategy_editor import CustomStrategy, StrategyEditor
from strategy_engine import StrategyEngine
from backtest_engine import BacktestEngine, BacktestResult

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("custom_strategy_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_test_data():
    """创建测试数据"""
    dates = [datetime(2023, 1, 1) + timedelta(days=i) for i in range(100)]
    np.random.seed(42)  # 设置随机种子以保证结果可重现
    prices = 100 + np.cumsum(np.random.normal(0, 1, 100))
    
    data = {
        'trade_date': dates,
        'open_price': prices,
        'high_price': prices + np.random.uniform(0, 2, 100),
        'low_price': prices - np.random.uniform(0, 2, 100),
        'close_price': prices + np.random.uniform(-1, 1, 100),
        'volume': np.random.randint(1000, 10000, 100)
    }
    
    return pd.DataFrame(data)

def test_custom_strategy_flow():
    """测试自定义策略的完整回测流程"""
    logger.info("开始测试自定义策略回测流程")
    
    # 创建测试数据
    test_data = create_test_data()
    logger.info(f"创建了测试数据，共{len(test_data)}条记录")
    
    # 定义一个简单的双均线策略代码
    # 简化版，确保生成明确的交易信号
    simple_ma_strategy_code = """
# 简单双均线策略
# 计算移动平均线
df['ma_short'] = df['close_price'].rolling(window=5).mean()
df['ma_long'] = df['close_price'].rolling(window=20).mean()

# 初始化信号
for i in range(20, len(df)):
    if df.loc[i, 'ma_short'] > df.loc[i, 'ma_long'] and df.loc[i-1, 'ma_short'] <= df.loc[i-1, 'ma_long']:
        df.loc[i, 'signal'] = 1
    elif df.loc[i, 'ma_short'] < df.loc[i, 'ma_long'] and df.loc[i-1, 'ma_short'] >= df.loc[i-1, 'ma_long']:
        df.loc[i, 'signal'] = -1
"""
    
    # 1. 测试CustomStrategy.generate_signals方法
    logger.info("测试CustomStrategy.generate_signals方法")
    custom_strategy = CustomStrategy("test_strategy", simple_ma_strategy_code)
    
    # 编译代码
    compiled = custom_strategy.compile_code()
    logger.info(f"代码编译结果: {'成功' if compiled else '失败'}")
    
    # 生成信号
    signals = custom_strategy.generate_signals(test_data)
    
    # 检查信号
    signal_count = len(signals[signals['signal'] != 0])
    logger.info(f"生成的非零信号数量: {signal_count}")
    logger.info(f"信号分布:\n{signals['signal'].value_counts()}")
    
    # 显示前几个有信号的行
    signal_rows = signals[signals['signal'] != 0].head()
    logger.info(f"信号示例:\n{signal_rows[['trade_date', 'close_price', 'ma_short', 'ma_long', 'signal']]}")
    
    # 2. 测试BacktestEngine.simulate_trading方法
    logger.info("测试BacktestEngine.simulate_trading方法")
    backtest_engine = BacktestEngine()
    
    # 模拟交易
    result = backtest_engine.simulate_trading(signals, initial_capital=100000.0, commission_rate=0.001)
    
    # 检查交易结果
    logger.info(f"交易次数: {len(result.trades)}")
    logger.info(f"初始资金: {result.initial_capital}")
    logger.info(f"最终资金: {result.final_capital}")
    logger.info(f"总收益率: {result.total_return:.4%}")
    logger.info(f"年化收益率: {result.annual_return:.4%}")
    logger.info(f"最大回撤: {result.max_drawdown:.4%}")
    logger.info(f"夏普比率: {result.sharpe_ratio:.4f}")
    logger.info(f"胜率: {result.win_rate:.4%}")
    
    # 如果有交易，显示前几个
    if result.trades:
        logger.info(f"交易示例:\n{pd.DataFrame(result.trades).head()}")
    
    # 3. 检查equity_curve和daily_returns
    logger.info(f"资金曲线长度: {len(result.equity_curve)}")
    logger.info(f"日收益率长度: {len(result.daily_returns)}")
    
    # 检查是否所有指标都是0
    all_zero = (result.total_return == 0 and 
               result.annual_return == 0 and 
               result.max_drawdown == 0 and 
               result.sharpe_ratio == 0 and 
               result.win_rate == 0 and 
               len(result.trades) == 0)
    
    if all_zero:
        logger.warning("警告: 所有回测指标都是0！")
    else:
        logger.info("回测指标正常，不是全0。")
    
    # 4. 测试StrategyEditor.run_custom_strategy方法 - 但使用模拟数据绕过数据库
    logger.info("测试StrategyEditor.run_custom_strategy方法 - 模拟版本")
    
    # 创建模拟数据
    mock_data = create_test_data()
    
    # 为了绕过数据库，我们需要直接测试CustomStrategy和BacktestEngine的组合
    editor = StrategyEditor()
    strategy = CustomStrategy("test_strategy", simple_ma_strategy_code)
    
    # 编译代码
    strategy.compile_code()
    
    # 生成信号
    signals = strategy.generate_signals(mock_data)
    
    # 模拟交易
    result = editor.backtest_engine.simulate_trading(signals, initial_capital=100000.0, commission_rate=0.001)
    
    # 检查结果
    logger.info(f"模拟策略编辑器返回的结果 - 交易次数: {len(result.trades)}")
    logger.info(f"模拟策略编辑器返回的结果 - 总收益率: {result.total_return:.4%}")
    logger.info(f"模拟策略编辑器返回的结果 - 年化收益率: {result.annual_return:.4%}")
    logger.info(f"模拟策略编辑器返回的结果 - 最大回撤: {result.max_drawdown:.4%}")
    logger.info(f"模拟策略编辑器返回的结果 - 夏普比率: {result.sharpe_ratio:.4f}")
    logger.info(f"模拟策略编辑器返回的结果 - 胜率: {result.win_rate:.4%}")
    
    # 检查是否所有指标都是0
    mock_all_zero = (result.total_return == 0 and 
                   result.annual_return == 0 and 
                   result.max_drawdown == 0 and 
                   result.sharpe_ratio == 0 and 
                   result.win_rate == 0 and 
                   len(result.trades) == 0)
    
    if mock_all_zero:
        logger.warning("警告: 模拟策略编辑器返回的所有回测指标都是0！")
    else:
        logger.info("模拟策略编辑器返回的回测指标正常，不是全0。")
    
    logger.info("自定义策略回测流程测试完成")

if __name__ == "__main__":
    test_custom_strategy_flow()