#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import logging
from datetime import datetime, timedelta
from index_calculate import TechnicalIndicatorCalculator

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_indicator_calculator(db_password: str):
    """
    测试TechnicalIndicatorCalculator类的功能
    
    Args:
        db_password: 数据库密码
    """
    try:
        logger.info("开始测试指标计算器...")
        
        # 创建计算器实例
        calculator = TechnicalIndicatorCalculator(db_password)
        
        # 连接数据库测试
        calculator.connect_database()
        logger.info("数据库连接测试通过")
        
        # 获取最近30天的日期范围
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        
        logger.info(f"测试日期范围: {start_date} 到 {end_date}")
        
        # 测试获取行情数据
        stock_code = "600519.SH"  # 贵州茅台作为测试股票
        logger.info(f"测试获取股票{stock_code}的行情数据...")
        market_df = calculator.get_stock_market_data(stock_code, start_date, end_date)
        
        if not market_df.empty:
            logger.info(f"成功获取{len(market_df)}条行情数据")
            logger.info(f"行情数据样例:\n{market_df.head(3).to_string()}")
        else:
            logger.warning("未获取到行情数据，可能是日期范围或股票代码问题")
            # 尝试使用用户提供的示例日期
            logger.info("尝试使用示例日期2024-01-02测试...")
            market_df = calculator.get_stock_market_data(stock_code, "2024-01-02", "2024-01-02")
            if not market_df.empty:
                logger.info(f"使用示例日期成功获取数据:\n{market_df.to_string()}")
        
        # 测试获取估值数据
        logger.info(f"测试获取股票{stock_code}的估值数据...")
        valuation_df = calculator.get_stock_valuation_data(stock_code, start_date, end_date)
        
        if not valuation_df.empty:
            logger.info(f"成功获取{len(valuation_df)}条估值数据")
            logger.info(f"估值数据样例:\n{valuation_df.head(3).to_string()}")
        else:
            logger.warning("未获取到估值数据")
            # 尝试使用用户提供的示例日期
            valuation_df = calculator.get_stock_valuation_data(stock_code, "2024-01-02", "2024-01-02")
            if not valuation_df.empty:
                logger.info(f"使用示例日期成功获取数据:\n{valuation_df.to_string()}")
        
        # 测试指标计算功能
        if not market_df.empty:
            logger.info("测试计算移动平均线...")
            ma_df = calculator.calculate_moving_average(market_df, periods=[5, 10])
            logger.info(f"移动平均线计算结果:\n{ma_df.tail(3)[['trade_date', 'close_price', 'ma5', 'ma10']].to_string()}")
            
            logger.info("测试计算RSI指标...")
            rsi_df = calculator.calculate_rsi(market_df)
            logger.info(f"RSI计算结果:\n{rsi_df.tail(3)[['trade_date', 'close_price', 'rsi14']].to_string()}")
            
            logger.info("测试计算MACD指标...")
            macd_df = calculator.calculate_macd(market_df)
            logger.info(f"MACD计算结果:\n{macd_df.tail(3)[['trade_date', 'close_price', 'macd_line', 'signal_line', 'macd_hist']].to_string()}")
            
            logger.info("测试计算布林带指标...")
            bb_df = calculator.calculate_bollinger_bands(market_df)
            logger.info(f"布林带计算结果:\n{bb_df.tail(3)[['trade_date', 'close_price', 'bb_upper', 'bb_mid', 'bb_lower']].to_string()}")
            
            logger.info("测试计算KDJ指标...")
            kdj_df = calculator.calculate_kdj(market_df)
            logger.info(f"KDJ计算结果:\n{kdj_df.tail(3)[['trade_date', 'close_price', 'kdj_k', 'kdj_d', 'kdj_j']].to_string()}")
        
        # 关闭数据库连接
        calculator.close_database()
        
        # 提示如何进行完整测试
        logger.info("\n测试完成!\n")
        logger.info("若要运行完整的指标分析和可视化，请执行:")
        logger.info(f"python index_calculate.py {db_password}")
        logger.info("\n您可以修改index_calculate.py中的主函数来调整:")
        logger.info("- 股票代码")
        logger.info("- 日期范围")
        logger.info("- 要计算的指标列表")
        logger.info("- 是否保存图表")
        
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        raise


def main():
    """主函数"""
    try:
        # 从命令行参数获取数据库密码，默认使用123456
        db_password = sys.argv[1] if len(sys.argv) > 1 else "123456"
        
        # 运行测试
        test_indicator_calculator(db_password)
        
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()