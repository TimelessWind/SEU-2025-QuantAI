#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
策略编辑器测试脚本
测试自定义策略编写、验证和回测功能
"""

import sys
import logging
from datetime import datetime

from strategy_editor import StrategyEditor, StrategyValidator, StrategyTemplate

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_strategy_validator():
    """测试策略验证器"""
    logger.info("=== 测试策略验证器 ===")
    
    # 测试有效代码
    valid_code = """
# 简单的双均线策略
df['ma_5'] = df['close_price'].rolling(window=5).mean()
df['ma_20'] = df['close_price'].rolling(window=20).mean()

for i in range(20, len(df)):
    if df.loc[i, 'ma_5'] > df.loc[i, 'ma_20'] and df.loc[i-1, 'ma_5'] <= df.loc[i-1, 'ma_20']:
        df.loc[i, 'signal'] = 1
        df.loc[i, 'position'] = 1
    elif df.loc[i, 'ma_5'] < df.loc[i, 'ma_20'] and df.loc[i-1, 'ma_5'] >= df.loc[i-1, 'ma_20']:
        df.loc[i, 'signal'] = -1
        df.loc[i, 'position'] = 0
    else:
        df.loc[i, 'position'] = df.loc[i-1, 'position']
"""
    
    is_valid, error_msg = StrategyValidator.validate_strategy_code(valid_code)
    logger.info(f"有效代码验证: {'通过' if is_valid else '失败'} - {error_msg}")
    
    # 测试无效代码（包含危险函数）
    invalid_code = """
import os
os.system('rm -rf /')
"""
    
    is_valid, error_msg = StrategyValidator.validate_strategy_code(invalid_code)
    logger.info(f"无效代码验证: {'通过' if is_valid else '失败'} - {error_msg}")
    
    return is_valid


def test_strategy_templates():
    """测试策略模板"""
    logger.info("\n=== 测试策略模板 ===")
    
    templates = StrategyTemplate.get_templates()
    logger.info(f"可用模板数量: {len(templates)}")
    
    for name, template in templates.items():
        logger.info(f"- {template['name']}: {template['description']}")
        logger.info(f"  参数: {list(template['parameters'].keys())}")
    
    return len(templates) > 0


def test_strategy_editor():
    """测试策略编辑器"""
    logger.info("\n=== 测试策略编辑器 ===")
    
    try:
        editor = StrategyEditor()
        
        # 测试获取模板
        templates_result = editor.get_strategy_templates()
        logger.info(f"获取模板: {'成功' if templates_result['success'] else '失败'}")
        
        # 测试策略验证
        test_code = """
# 简单的价格突破策略
df['ma_20'] = df['close_price'].rolling(window=20).mean()
df['ma_5'] = df['close_price'].rolling(window=5).mean()

for i in range(20, len(df)):
    if df.loc[i, 'ma_5'] > df.loc[i, 'ma_20'] and df.loc[i-1, 'ma_5'] <= df.loc[i-1, 'ma_20']:
        df.loc[i, 'signal'] = 1
        df.loc[i, 'position'] = 1
    elif df.loc[i, 'ma_5'] < df.loc[i, 'ma_20'] and df.loc[i-1, 'ma_5'] >= df.loc[i-1, 'ma_20']:
        df.loc[i, 'signal'] = -1
        df.loc[i, 'position'] = 0
    else:
        df.loc[i, 'position'] = df.loc[i-1, 'position']
"""
        
        validation_result = editor.validate_strategy(test_code)
        logger.info(f"策略验证: {'成功' if validation_result['success'] else '失败'}")
        if not validation_result['success']:
            logger.info(f"验证错误: {validation_result['message']}")
        
        # 测试保存策略
        save_result = editor.save_custom_strategy(
            name="测试策略",
            code=test_code,
            parameters={"period": 20},
            description="这是一个测试策略"
        )
        logger.info(f"策略保存: {'成功' if save_result['success'] else '失败'}")
        if save_result['success']:
            logger.info(f"策略ID: {save_result['data']['strategy_id']}")
        
        return True
        
    except Exception as e:
        logger.error(f"策略编辑器测试失败: {e}")
        return False


def test_custom_strategy_backtest():
    """测试自定义策略回测"""
    logger.info("\n=== 测试自定义策略回测 ===")
    
    try:
        editor = StrategyEditor()
        
        # 简单的自定义策略
        custom_code = """
# 自定义策略：价格突破20日均线
df['ma_20'] = df['close_price'].rolling(window=20).mean()

for i in range(20, len(df)):
    if df.loc[i, 'close_price'] > df.loc[i, 'ma_20'] and df.loc[i-1, 'close_price'] <= df.loc[i-1, 'ma_20']:
        df.loc[i, 'signal'] = 1  # 买入
        df.loc[i, 'position'] = 1
    elif df.loc[i, 'close_price'] < df.loc[i, 'ma_20'] and df.loc[i-1, 'close_price'] >= df.loc[i-1, 'ma_20']:
        df.loc[i, 'signal'] = -1  # 卖出
        df.loc[i, 'position'] = 0
    else:
        df.loc[i, 'position'] = df.loc[i-1, 'position']
"""
        
        # 运行回测
        result = editor.run_custom_strategy(
            stock_code="600519.SH",
            start_date="2024-01-01",
            end_date="2024-12-31",
            code=custom_code,
            initial_capital=100000.0,
            commission_rate=0.001
        )
        
        if result['success']:
            data = result['data']
            logger.info("自定义策略回测结果:")
            logger.info(f"- 初始资金: ¥{data['initial_capital']:,.2f}")
            logger.info(f"- 最终资金: ¥{data['final_capital']:,.2f}")
            logger.info(f"- 总收益率: {data['total_return']:.2%}")
            logger.info(f"- 年化收益率: {data['annual_return']:.2%}")
            logger.info(f"- 最大回撤: {data['max_drawdown']:.2%}")
            logger.info(f"- 夏普比率: {data['sharpe_ratio']:.2f}")
            logger.info(f"- 交易次数: {data['trade_count']}")
            return True
        else:
            logger.error(f"回测失败: {result['message']}")
            return False
            
    except Exception as e:
        logger.error(f"自定义策略回测测试失败: {e}")
        return False


def main():
    """主测试函数"""
    logger.info("开始测试策略编辑器模块...")
    
    # 测试策略验证器
    validator_test_passed = test_strategy_validator()
    
    # 测试策略模板
    templates_test_passed = test_strategy_templates()
    
    # 测试策略编辑器
    editor_test_passed = test_strategy_editor()
    
    # 测试自定义策略回测
    backtest_test_passed = test_custom_strategy_backtest()
    
    # 总结测试结果
    logger.info("\n=== 测试结果总结 ===")
    logger.info(f"策略验证器测试: {'通过 ✓' if validator_test_passed else '失败 ✗'}")
    logger.info(f"策略模板测试: {'通过 ✓' if templates_test_passed else '失败 ✗'}")
    logger.info(f"策略编辑器测试: {'通过 ✓' if editor_test_passed else '失败 ✗'}")
    logger.info(f"自定义策略回测测试: {'通过 ✓' if backtest_test_passed else '失败 ✗'}")
    
    if all([validator_test_passed, templates_test_passed, editor_test_passed, backtest_test_passed]):
        logger.info("所有测试通过！策略编辑器功能正常 ✓")
        logger.info("\n🎉 研究员现在可以:")
        logger.info("1. 使用策略模板快速开始")
        logger.info("2. 编写自定义策略代码")
        logger.info("3. 验证策略代码安全性")
        logger.info("4. 运行策略回测")
        logger.info("5. 保存策略供后续使用")
        logger.info("\n📱 前端访问: 打开 strategy_editor_frontend.html")
        logger.info("🔗 API接口: http://localhost:5000/api/strategy-editor/*")
        return True
    else:
        logger.error("部分测试失败，请检查相关模块 ✗")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
        sys.exit(1)
