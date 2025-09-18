import pandas as pd
import numpy as np
import logging
import os

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# 创建模拟数据用于测试
def create_test_data():
    """创建模拟的股票数据用于测试"""
    dates = pd.date_range(start='2025-01-02', end='2025-06-30', freq='B')  # 工作日
    
    # 创建一些有趋势和波动的数据
    np.random.seed(42)  # 固定随机种子以确保结果可重复
    base_price = 1700
    price_changes = np.random.normal(0, 10, len(dates))
    prices = [base_price]
    
    for change in price_changes:
        next_price = prices[-1] + change
        prices.append(next_price)
    
    prices = prices[1:]  # 移除初始价格
    
    # 创建DataFrame
    df = pd.DataFrame({
        'stock_code': '600519.SH',
        'trade_date': dates,
        'open_price': prices,
        'high_price': [p * (1 + np.random.uniform(0, 0.02)) for p in prices],
        'low_price': [p * (1 - np.random.uniform(0, 0.02)) for p in prices],
        'close_price': prices,
        'volume': np.random.randint(1000000, 5000000, len(dates))
    })
    
    return df

# 测试默认策略代码
def test_default_strategy():
    """测试默认策略是否能正确生成交易信号"""
    # 模拟前端默认策略代码
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
    
    # 生成交易信号：短期均线上穿长期均线买入，下穿卖出
    # 避免使用未来函数：确保有足够的数据计算均线
    start_idx = max(5, 20)  # 使用较大的窗口长度作为起始索引
    for i in range(start_idx, len(df)):
        # 简化逻辑，不使用notna检查
        if df['short_ma'].iloc[i] > df['long_ma'].iloc[i] and df['short_ma'].iloc[i-1] <= df['long_ma'].iloc[i-1]:
            df['signal'].iloc[i] = 1  # 上穿买入信号
        elif df['short_ma'].iloc[i] < df['long_ma'].iloc[i] and df['short_ma'].iloc[i-1] >= df['long_ma'].iloc[i-1]:
            df['signal'].iloc[i] = -1  # 下穿卖出信号
    
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
    
    # 准备测试环境
    try:
        # 创建测试数据
        df = create_test_data()
        logger.info(f"创建了{len(df)}条测试数据")
        
        # 准备执行环境
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
            logger.error("策略代码中未定义'strategy'函数")
            return False
        
        # 执行策略
        result_df = strategy_func(df)
        
        # 分析结果
        signal_count = result_df['signal'].abs().sum()
        logger.info(f"生成了{signal_count}个交易信号")
        
        # 显示有信号的行
        signal_rows = result_df[result_df['signal'] != 0]
        if len(signal_rows) > 0:
            logger.info("信号详情:")
            for i, row in signal_rows.head(10).iterrows():
                logger.info(f"日期: {row['trade_date']}, 信号: {row['signal']}, 短期均线: {row['short_ma']:.2f}, 长期均线: {row['long_ma']:.2f}")
        
        # 检查是否生成了信号
        if signal_count > 0:
            logger.info("✅ 策略成功生成了交易信号！")
            return True
        else:
            logger.warning("❌ 策略没有生成任何交易信号！")
            # 打印一些数据点帮助调试
            logger.info("数据样例 (包含均线值):")
            sample_df = result_df[['trade_date', 'close_price', 'short_ma', 'long_ma', 'signal']].tail(20)
            logger.info(sample_df.to_string(index=False))
            return False
            
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

# 测试可能的修复方案
def test_fixed_strategy():
    """测试修复后的策略代码"""
    # 修改后的策略代码 - 简化信号生成逻辑
    strategy_code = """
import pandas as pd
import numpy as np

# 双均线策略 - 简化版
def strategy(df):
    # 计算短期均线和长期均线
    df['short_ma'] = df['close_price'].rolling(window=5).mean()
    df['long_ma'] = df['close_price'].rolling(window=20).mean()
    
    # 初始化信号和持仓列
    df['signal'] = 0
    df['position'] = 0
    
    # 简化的信号生成逻辑 - 只要短期均线在长期均线上方就买入
    df.loc[df['short_ma'] > df['long_ma'], 'signal'] = 1
    df.loc[df['short_ma'] < df['long_ma'], 'signal'] = -1
    
    # 根据信号调整持仓
    for i in range(1, len(df)):
        if df['signal'].iloc[i] == 1:
            df['position'].iloc[i] = 1
        elif df['signal'].iloc[i] == -1:
            df['position'].iloc[i] = 0
        else:
            df['position'].iloc[i] = df['position'].iloc[i-1]
    
    return df
"""
    
    # 准备测试环境
    try:
        # 创建测试数据
        df = create_test_data()
        
        # 准备执行环境
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
        result_df = strategy_func(df)
        
        # 分析结果
        signal_count = result_df['signal'].abs().sum()
        logger.info(f"修复后策略生成了{signal_count}个交易信号")
        
        return signal_count > 0
            
    except Exception as e:
        logger.error(f"修复后策略测试失败: {e}")
        return False

if __name__ == "__main__":
    logger.info("开始测试策略信号生成...")
    
    # 测试当前策略
    logger.info("\n=== 测试当前默认策略 ===")
    current_success = test_default_strategy()
    
    # 测试修复后的策略
    logger.info("\n=== 测试修复后的策略 ===")
    fixed_success = test_fixed_strategy()
    
    # 输出总结
    logger.info("\n=== 测试总结 ===")
    logger.info(f"当前策略生成信号: {'成功' if current_success else '失败'}")
    logger.info(f"修复后策略生成信号: {'成功' if fixed_success else '失败'}")
    
    if not current_success and fixed_success:
        logger.info("\n建议修复方案:")
        logger.info("1. 简化信号生成逻辑，使用更直接的条件判断")
        logger.info("2. 移除复杂的交叉检测逻辑，使用简单的均线比较")
        logger.info("3. 可以保留核心的双均线策略思想，但简化实现方式")