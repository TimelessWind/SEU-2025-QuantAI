# -*- coding: utf-8 -*-
"""
测试各种策略的信号生成情况
"""

import pandas as pd
import numpy as np
import logging
from strategy_engine import StrategyEngine, MovingAverageStrategy, BreakoutStrategy, RSIMeanReversionStrategy
from backtest_engine import BacktestEngine

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def test_strategy_signals():
    """测试不同策略的信号生成情况"""
    try:
        # 创建策略引擎
        strategy_engine = StrategyEngine()
        strategy_engine.connect_database()
        
        # 获取股票数据，使用数据库中实际存在的时间范围
        stock_code = "600519.SH"
        start_date = "2025-01-02"  # 数据库中实际的开始日期
        end_date = "2025-06-30"    # 数据库中实际的结束日期
        
        data = strategy_engine.get_stock_data(stock_code, start_date, end_date)
        if data.empty:
            logger.error(f"未获取到股票{stock_code}的数据")
            return
        
        logger.info(f"获取到{len(data)}条股票数据")
        
        # 测试双均线策略
        logger.info("\n=== 测试双均线策略 ===")
        ma_strategy = MovingAverageStrategy(
            short_period=5,
            long_period=20,
            buy_threshold=1.01,  # 原始阈值
            sell_threshold=1.0
        )
        ma_signals = ma_strategy.generate_signals(data)
        
        logger.info(f"双均线策略信号总数: {len(ma_signals)}")
        logger.info(f"买入信号数: {len(ma_signals[ma_signals['signal'] == 1])}")
        logger.info(f"卖出信号数: {len(ma_signals[ma_signals['signal'] == -1])}")
        
        # 检查ma_ratio分布，找出合适的阈值
        ma_signals['ma_ratio'] = ma_signals['short_ma'] / ma_signals['long_ma']
        logger.info(f"ma_ratio统计: 最小值={ma_signals['ma_ratio'].min():.4f}, 最大值={ma_signals['ma_ratio'].max():.4f}, 平均值={ma_signals['ma_ratio'].mean():.4f}")
        logger.info(f"ma_ratio大于1.01的比例: {len(ma_signals[ma_signals['ma_ratio'] >= 1.01])/len(ma_signals):.4%}")
        logger.info(f"ma_ratio大于1.005的比例: {len(ma_signals[ma_signals['ma_ratio'] >= 1.005])/len(ma_signals):.4%}")
        logger.info(f"ma_ratio大于1.00的比例: {len(ma_signals[ma_signals['ma_ratio'] > 1.00])/len(ma_signals):.4%}")
        
        # 测试突破策略
        logger.info("\n=== 测试突破策略 ===")
        breakout_strategy = BreakoutStrategy(
            lookback_period=20,
            breakout_threshold=0.02
        )
        breakout_signals = breakout_strategy.generate_signals(data)
        
        logger.info(f"突破策略信号总数: {len(breakout_signals)}")
        logger.info(f"买入信号数: {len(breakout_signals[breakout_signals['signal'] == 1])}")
        logger.info(f"卖出信号数: {len(breakout_signals[breakout_signals['signal'] == -1])}")
        
        # 检查突破情况
        breakout_signals['above_upper'] = breakout_signals['close_price'] > breakout_signals['upper_threshold']
        breakout_signals['below_lower'] = breakout_signals['close_price'] < breakout_signals['lower_threshold']
        logger.info(f"突破上轨的比例: {breakout_signals['above_upper'].mean():.4%}")
        logger.info(f"突破下轨的比例: {breakout_signals['below_lower'].mean():.4%}")
        
        # 测试RSI策略
        logger.info("\n=== 测试RSI均值回归策略 ===")
        rsi_strategy = RSIMeanReversionStrategy(
            rsi_period=14,
            oversold_threshold=30,
            overbought_threshold=70
        )
        rsi_signals = rsi_strategy.generate_signals(data)
        
        logger.info(f"RSI策略信号总数: {len(rsi_signals)}")
        logger.info(f"买入信号数: {len(rsi_signals[rsi_signals['signal'] == 1])}")
        logger.info(f"卖出信号数: {len(rsi_signals[rsi_signals['signal'] == -1])}")
        
        # 检查RSI分布
        logger.info(f"RSI统计: 最小值={rsi_signals['rsi'].min():.2f}, 最大值={rsi_signals['rsi'].max():.2f}, 平均值={rsi_signals['rsi'].mean():.2f}")
        logger.info(f"RSI小于30的比例: {len(rsi_signals[rsi_signals['rsi'] < 30])/len(rsi_signals):.4%}")
        logger.info(f"RSI大于70的比例: {len(rsi_signals[rsi_signals['rsi'] > 70])/len(rsi_signals):.4%}")
        
        # 使用修改后的参数测试双均线策略
        logger.info("\n=== 测试修改参数后的双均线策略 ===")
        modified_ma_strategy = MovingAverageStrategy(
            short_period=5,
            long_period=20,
            buy_threshold=1.002,  # 降低阈值，更容易触发信号
            sell_threshold=0.998  # 增加对称的卖出阈值
        )
        modified_ma_signals = modified_ma_strategy.generate_signals(data)
        
        logger.info(f"修改参数后的双均线策略买入信号数: {len(modified_ma_signals[modified_ma_signals['signal'] == 1])}")
        logger.info(f"修改参数后的双均线策略卖出信号数: {len(modified_ma_signals[modified_ma_signals['signal'] == -1])}")
        
        # 使用修改后的参数测试突破策略（修复未来函数问题）
        logger.info("\n=== 测试修复未来函数后的突破策略 ===")
        # 创建一个临时的修复版突破策略
        class FixedBreakoutStrategy(BreakoutStrategy):
            def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
                if not self.validate_data(data):
                    raise ValueError("数据格式不正确")
                
                df = data.copy()
                df = df.sort_values('trade_date').reset_index(drop=True)
                
                # 修复未来函数问题：使用shift(1)确保不使用当前周期的数据
                df['high_max'] = df['high_price'].rolling(window=self.lookback_period).max().shift(1)
                df['low_min'] = df['low_price'].rolling(window=self.lookback_period).min().shift(1)
                
                # 计算突破阈值
                df['upper_threshold'] = df['high_max'] * (1 + self.breakout_threshold)
                df['lower_threshold'] = df['low_min'] * (1 - self.breakout_threshold)
                
                # 初始化信号
                df['signal'] = 0
                df['position'] = 0
                
                # 生成交易信号
                start_idx = max(self.lookback_period, 1)  # 从第一个有效的high_max开始
                for i in range(start_idx, len(df)):
                    if pd.isna(df.loc[i, 'high_max']) or pd.isna(df.loc[i, 'low_min']):
                        continue
                    
                    # 向上突破买入
                    if df.loc[i, 'close_price'] > df.loc[i, 'upper_threshold']:
                        df.loc[i, 'signal'] = 1  # 买入
                        df.loc[i, 'position'] = 1
                    # 向下突破卖出
                    elif df.loc[i, 'close_price'] < df.loc[i, 'lower_threshold']:
                        df.loc[i, 'signal'] = -1  # 卖出
                        df.loc[i, 'position'] = 0
                    # 保持仓位
                    else:
                        df.loc[i, 'position'] = df.loc[i-1, 'position']
                
                return df
        
        fixed_breakout_strategy = FixedBreakoutStrategy(
            lookback_period=20,
            breakout_threshold=0.02
        )
        fixed_breakout_signals = fixed_breakout_strategy.generate_signals(data)
        
        logger.info(f"修复未来函数后的突破策略买入信号数: {len(fixed_breakout_signals[fixed_breakout_signals['signal'] == 1])}")
        logger.info(f"修复未来函数后的突破策略卖出信号数: {len(fixed_breakout_signals[fixed_breakout_signals['signal'] == -1])}")
        
        # 运行回测验证修改后的策略
        logger.info("\n=== 运行回测验证修改后的策略 ===")
        backtest_engine = BacktestEngine()
        
        # 回测修改后的双均线策略 - 正确传递参数格式
        try:
            ma_backtest_result = backtest_engine.run_backtest(
                stock_code=stock_code,
                start_date=start_date,
                end_date=end_date,
                strategy_type="moving_average",
                initial_capital=100000.0,
                commission_rate=0.001,
                strategy_params={
                    'short_period': 5,
                    'long_period': 20,
                    'buy_threshold': 1.002,  # 使用修改后的阈值
                    'sell_threshold': 0.998
                }
            )
            
            logger.info("修改后的双均线策略回测结果:")
            logger.info(f"- 初始资金: ¥{ma_backtest_result.initial_capital:,.2f}")
            logger.info(f"- 最终资金: ¥{ma_backtest_result.final_capital:,.2f}")
            logger.info(f"- 总收益率: {ma_backtest_result.total_return:.2%}")
            logger.info(f"- 年化收益率: {ma_backtest_result.annual_return:.2%}")
            logger.info(f"- 交易次数: {ma_backtest_result.trade_count}")
        except Exception as e:
            logger.error(f"回测修改后的双均线策略时出错: {e}")
        
        # 注意：由于突破策略的修改无法通过现有接口传递，这里只打印信号数量
        logger.info(f"修复后的突破策略生成了{len(fixed_breakout_signals[fixed_breakout_signals['signal'] == 1])}个买入信号")
        
    except Exception as e:
        logger.error(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if strategy_engine.connection:
            strategy_engine.close_database()

if __name__ == "__main__":
    test_strategy_signals()