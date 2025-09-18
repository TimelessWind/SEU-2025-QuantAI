#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试自定义策略的保存和回测功能
"""

import json
import pymysql
from datetime import datetime
from strategy_editor import StrategyEditor

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'quantitative_trading',
    'charset': 'utf8mb4'
}


def connect_db():
    """连接数据库"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        print("成功连接到数据库")
        return connection
    except Exception as e:
        print(f"连接数据库失败: {e}")
        return None


def check_custom_strategies():
    """检查数据库中的自定义策略"""
    connection = connect_db()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        # 查询所有自定义策略
        sql = "SELECT strategy_id, strategy_name, strategy_desc, strategy_type FROM strategy WHERE strategy_type = 'custom'";
        cursor.execute(sql)
        
        strategies = cursor.fetchall()
        if strategies:
            print(f"发现 {len(strategies)} 个自定义策略:")
            for strategy in strategies:
                strategy_id, strategy_name, strategy_desc, strategy_type = strategy
                print(f"- ID: {strategy_id}, 名称: {strategy_name}, 类型: {strategy_type}")
        else:
            print("没有发现自定义策略")
    except Exception as e:
        print(f"查询自定义策略失败: {e}")
    finally:
        if connection:
            connection.close()


def test_save_custom_strategy():
    """测试保存自定义策略"""
    print("\n开始测试保存自定义策略...")
    
    # 创建策略编辑器实例
    editor = StrategyEditor(db_password='123456')
    
    # 准备一个简单的测试策略代码
    test_code = """# 简单的测试策略
# 买入信号：价格上涨
# 卖出信号：价格下跌

# 计算价格变化
for i in range(1, len(df)):
    # 买入信号：价格上涨
    if df.loc[i, 'close_price'] > df.loc[i-1, 'close_price']:
        df.loc[i, 'signal'] = 1  # 买入
        df.loc[i, 'position'] = 1
    # 卖出信号：价格下跌
    elif df.loc[i, 'close_price'] < df.loc[i-1, 'close_price']:
        df.loc[i, 'signal'] = -1  # 卖出
        df.loc[i, 'position'] = 0
    # 保持仓位
    else:
        df.loc[i, 'position'] = df.loc[i-1, 'position']
"""
    
    # 测试参数
    test_params = {
        'param1': {'type': 'int', 'default': 10, 'min': 1, 'max': 100}
    }
    
    # 保存策略
    result = editor.save_custom_strategy(
        name="测试策略_" + datetime.now().strftime("%Y%m%d%H%M%S"),
        code=test_code,
        parameters=test_params,
        description="这是一个用于测试的简单自定义策略",
        creator_id="test_user"
    )
    
    print(f"保存策略结果: {result}")
    return result.get('data', {}).get('strategy_id')


def test_run_custom_strategy(strategy_id):
    """测试运行自定义策略回测"""
    if not strategy_id:
        print("没有有效的策略ID，无法测试回测")
        return
    
    print(f"\n开始测试策略ID为 {strategy_id} 的回测...")
    
    # 尝试从数据库加载策略
    connection = connect_db()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        # 查询策略代码和参数
        sql = "SELECT strategy_code, strategy_params FROM strategy WHERE strategy_id = %s";
        cursor.execute(sql, (strategy_id,))
        
        result = cursor.fetchone()
        if not result:
            print(f"未找到策略ID为 {strategy_id} 的策略")
            return
        
        strategy_code, strategy_params_str = result
        
        # 解析策略参数
        try:
            params = json.loads(strategy_params_str) if strategy_params_str else {}
        except json.JSONDecodeError:
            params = {}
        
        print(f"成功加载策略代码和参数")
        
        # 创建策略编辑器实例
        editor = StrategyEditor(db_password='123456')
        
        # 运行回测
        backtest_result = editor.run_custom_strategy(
            stock_code='000001.SZ',  # 上证指数
            start_date='2023-01-01',
            end_date='2023-12-31',
            code=strategy_code,
            parameters=params,
            initial_capital=100000.0,
            commission_rate=0.0003
        )
        
        print(f"回测结果: {backtest_result}")
        
        if backtest_result.get('success'):
            print(f"回测成功，最终资金: {backtest_result['data'].get('final_capital')}")
            print(f"总收益率: {backtest_result['data'].get('total_return')}%")
        
    except Exception as e:
        print(f"运行回测失败: {e}")
    finally:
        if connection:
            connection.close()


def main():
    """主函数"""
    print("开始测试自定义策略功能")
    
    # 检查当前数据库中的自定义策略
    check_custom_strategies()
    
    # 测试保存自定义策略
    strategy_id = test_save_custom_strategy()
    
    # 再次检查数据库中的自定义策略
    check_custom_strategies()
    
    # 测试运行自定义策略回测
    test_run_custom_strategy(strategy_id)
    
    # 也可以测试特定的策略ID，例如用户提到的"strategy_1758034949843"
    user_strategy_id = "strategy_1758034949843"
    print(f"\n尝试测试用户提到的策略ID: {user_strategy_id}")
    test_run_custom_strategy(user_strategy_id)


if __name__ == '__main__':
    main()