#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试交易次数计算功能
直接运行自定义策略并输出交易次数和详细交易记录
"""

import pandas as pd
import numpy as np
from strategy_editor import StrategyEditor, CustomStrategy
from strategy_engine import StrategyEngine
from backtest_engine import BacktestEngine
import logging
import json

# 配置日志
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def test_trade_count_calculation():
    """测试交易次数计算功能"""
    logger.info("开始测试交易次数计算功能")
    
    try:
        # 创建策略引擎和回测引擎实例并确保连接数据库
        db_password = '123456'
        
        # 创建策略引擎并连接数据库
        strategy_engine = StrategyEngine(db_password)
        strategy_engine.connect_database()
        
        # 创建回测引擎
        backtest_engine = BacktestEngine(db_password)
        
        # 创建策略编辑器实例，传入已连接的策略引擎和回测引擎
        editor = StrategyEditor(db_password)
        editor.strategy_engine = strategy_engine
        editor.backtest_engine = backtest_engine
        
        # 修复后的双均线策略代码 - 使用允许的pandas方法
        default_strategy_code = """import pandas as pd 
import numpy as np 

# 双均线策略 - 注意：不要使用函数包装器，直接操作df

# 计算短期均线和长期均线 - 注意数据库中字段名为close_price
df['short_ma'] = df['close_price'].rolling(window=5).mean()
df['long_ma'] = df['close_price'].rolling(window=20).mean()

# 初始化持仓状态
current_position = 0

# 使用较大的窗口长度作为起始索引
start_idx = max(5, 20)

# 生成交易信号
for i in range(start_idx, len(df)):
    if i < len(df) and 'short_ma' in df.columns and 'long_ma' in df.columns:
        # 简化的信号生成逻辑
        # 跳过NaN值检查，使用try-except替代
        try:
            if df.loc[i, 'short_ma'] > df.loc[i, 'long_ma'] and current_position == 0:
                df.loc[i, 'signal'] = 1  # 买入信号
                current_position = 1
            elif df.loc[i, 'short_ma'] < df.loc[i, 'long_ma'] and current_position == 1:
                df.loc[i, 'signal'] = -1  # 卖出信号
                current_position = 0
        except:
            pass

# 根据信号调整持仓
for i in range(1, len(df)):
    if df.loc[i, 'signal'] == 1:
        df.loc[i, 'position'] = 1  # 买入并持有
    elif df.loc[i, 'signal'] == -1:
        df.loc[i, 'position'] = 0  # 卖出并空仓
    else:
        df.loc[i, 'position'] = df.loc[i-1, 'position']  # 保持之前的持仓
"""
        
        # 先直接测试策略的信号生成部分
        # 1. 获取股票数据
        data = strategy_engine.get_stock_data('600519.SH', '2025-01-02', '2025-06-30')
        if data.empty:
            logger.error("未能获取股票数据")
            return
        
        logger.debug(f"获取到的股票数据形状: {data.shape}")
        logger.debug(f"股票数据前5行:\n{data.head()}")
        
        # 2. 直接使用CustomStrategy测试信号生成
        custom_strategy = CustomStrategy("test_strategy", default_strategy_code)
        if not custom_strategy.compile_code():
            logger.error("策略编译失败")
            return
        
        # 3. 生成信号
        try:
            signals = custom_strategy.generate_signals(data)
            
            logger.info(f"生成的信号数据形状: {signals.shape}")
            logger.info(f"信号数据包含的列: {list(signals.columns)}")
            
            # 检查信号列是否存在
            if 'signal' not in signals.columns:
                logger.error("信号列不存在")
            else:
                logger.info(f"买入信号数量: {len(signals[signals['signal'] == 1])}")
                logger.info(f"卖出信号数量: {len(signals[signals['signal'] == -1])}")
                logger.info(f"总信号数量: {len(signals[signals['signal'] != 0])}")
                
                # 输出有信号的行
                signals_with_action = signals[signals['signal'] != 0]
                if not signals_with_action.empty:
                    logger.info(f"有信号的行:\n{signals_with_action[['trade_date', 'close_price', 'short_ma', 'long_ma', 'signal']]}")
                else:
                    logger.warning("策略没有生成任何交易信号！")
                    
                    # 查看原始数据的前10行和后10行
                    logger.info(f"原始数据前10行:\n{data[['trade_date', 'close_price']].head(10)}")
                    logger.info(f"原始数据后10行:\n{data[['trade_date', 'close_price']].tail(10)}")
                    
                    # 查看部分均线数据以分析原因
                    if 'short_ma' in signals.columns and 'long_ma' in signals.columns:
                        # 查看起始数据和中间数据的均线计算结果
                        logger.info(f"前30天均线数据:\n{signals[['trade_date', 'close_price', 'short_ma', 'long_ma']].head(30)}")
                        logger.info(f"后30天均线数据:\n{signals[['trade_date', 'close_price', 'short_ma', 'long_ma']].tail(30)}")
                        
                        # 计算均线交叉情况
                        signals['ma_cross'] = np.where(signals['short_ma'] > signals['long_ma'], 1, 0)
                        signals['cross_over'] = signals['ma_cross'].diff()
                        
                        cross_over_points = signals[signals['cross_over'] == 1]
                        cross_under_points = signals[signals['cross_over'] == -1]
                        
                        logger.info(f"金叉次数: {len(cross_over_points)}")
                        logger.info(f"死叉次数: {len(cross_under_points)}")
                        
                        # 输出所有均线关系
                        ma_relationship = signals[['trade_date', 'short_ma', 'long_ma']].copy()
                        ma_relationship['short_gt_long'] = ma_relationship['short_ma'] > ma_relationship['long_ma']
                        logger.info(f"均线关系前20行:\n{ma_relationship.head(20)}")
                        logger.info(f"均线关系后20行:\n{ma_relationship.tail(20)}")
                        
                        # 检查是否有金叉或死叉
                        if not cross_over_points.empty:
                            logger.info(f"金叉点:\n{cross_over_points[['trade_date', 'close_price', 'short_ma', 'long_ma']]}")
                        if not cross_under_points.empty:
                            logger.info(f"死叉点:\n{cross_under_points[['trade_date', 'close_price', 'short_ma', 'long_ma']]}")
                        else:
                            logger.warning("整个期间内没有发现金叉或死叉情况！")
                            # 计算整体均线趋势
                            short_mean = signals['short_ma'].mean()
                            long_mean = signals['long_ma'].mean()
                            logger.info(f"短期均线平均值: {short_mean}")
                            logger.info(f"长期均线平均值: {long_mean}")
                            logger.info(f"短期均线是否整体大于长期均线: {short_mean > long_mean}")
        except Exception as e:
            logger.error(f"生成信号时出错: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # 4. 运行回测
        try:
            result = editor.run_custom_strategy(
                stock_code='600519.SH',  # 茅台股票
                start_date='2025-01-02',  # 使用数据库中有效的起始日期
                end_date='2025-06-30',    # 使用数据库中有效的结束日期
                code=default_strategy_code,
                initial_capital=100000.0,
                commission_rate=0.001
            )
            
            # 输出回测结果
            if result['success']:
                data = result['data']
                logger.info(f"回测成功！")
                logger.info(f"交易次数: {data['trade_count']}")
                logger.info(f"交易记录数量: {len(data['trades'])}")
                logger.info(f"初始资金: ¥{data['initial_capital']:,.2f}")
                logger.info(f"最终资金: ¥{data['final_capital']:,.2f}")
                logger.info(f"总收益率: {data['total_return']*100:.2f}%")
                
                # 检查返回数据中是否包含trade_count字段
                logger.info(f"返回数据中是否包含trade_count: {'trade_count' in data}")
                logger.info(f"返回数据完整结构: {list(data.keys())}")
            else:
                logger.error(f"回测失败: {result['message']}")
        except Exception as e:
            logger.error(f"运行回测时出错: {str(e)}")
        
        # 关闭数据库连接
        strategy_engine.close_database()
            
    except Exception as e:
        logger.error(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_trade_count_calculation()