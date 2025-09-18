#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试自定义策略回测功能的脚本
用于验证修复后自定义策略是否能正常回测
"""

import json
import requests
import pymysql
from datetime import datetime

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'quantitative_trading',
    'charset': 'utf8mb4'
}

# 后端API地址
BACKEND_URL = 'http://127.0.0.1:8000'

# JWT Token（假设用户已登录）
JWT_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYWRtaW4iLCJleHAiOjE3NTg0NjM3MzZ9.3iY-5p4M2y5Sf8aF3g8x4d3c2b1a9s8r7q6p5o4n3m2l1k0j9i8h7g6f5e4d3c2b1a'


def connect_db():
    """连接数据库"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        print("成功连接到数据库")
        return connection
    except Exception as e:
        print(f"连接数据库失败: {e}")
        return None


def get_latest_custom_strategy():
    """获取最新的自定义策略"""
    connection = connect_db()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor()
        
        # 查询最新的自定义策略
        sql = "SELECT strategy_id, strategy_name, strategy_code, strategy_params FROM strategy WHERE strategy_type = 'custom' ORDER BY create_time DESC LIMIT 1;"
        cursor.execute(sql)
        
        result = cursor.fetchone()
        if result:
            strategy_id, strategy_name, strategy_code, strategy_params_str = result
            print(f"找到最新的自定义策略: ID={strategy_id}, 名称={strategy_name}")
            return {
                'id': strategy_id,
                'name': strategy_name,
                'code': strategy_code,
                'params': json.loads(strategy_params_str) if strategy_params_str else {}
            }
        else:
            print("未找到自定义策略")
            return None
    except Exception as e:
        print(f"查询自定义策略失败: {e}")
        return None
    finally:
        if connection:
            connection.close()


def run_backtest_for_strategy(strategy_id):
    """为指定策略ID运行回测"""
    print(f"\n开始为策略 {strategy_id} 运行回测...")
    
    # 构建回测请求数据
    backtest_data = {
        "strategyId": strategy_id,
        "type": "stock",
        "target": "600519.SH",  # 贵州茅台作为测试股票
        "startDate": "2024-01-01T00:00:00Z",
        "endDate": "2024-12-31T00:00:00Z",
        "initialFund": 100000,
        "commissionRate": 0.001
    }
    
    # 设置请求头
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {JWT_TOKEN}'
    }
    
    # 发送回测请求
    try:
        response = requests.post(f'{BACKEND_URL}/backtest/run', 
                               headers=headers,
                               data=json.dumps(backtest_data))
        
        # 检查响应状态
        if response.status_code == 200:
            result = response.json()
            print(f"回测成功!\n响应结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return True, result
        else:
            print(f"回测失败: HTTP状态码 {response.status_code}\n响应内容: {response.text}")
            return False, None
    except Exception as e:
        print(f"发送回测请求时发生错误: {e}")
        return False, None


def main():
    """主函数"""
    print("===== 自定义策略回测测试 ======")
    
    # 获取最新的自定义策略
    latest_strategy = get_latest_custom_strategy()
    
    if not latest_strategy:
        print("没有找到可用的自定义策略，无法进行回测测试。")
        return
    
    # 运行回测
    success, result = run_backtest_for_strategy(latest_strategy['id'])
    
    if success:
        print("\n===== 测试结果总结 =====")
        print(f"1. 自定义策略回测: {'成功' if success else '失败'}")
        print(f"2. 回测指标:")
        print(f"   - 总收益率: {result.get('totalReturn', 'N/A')}")
        print(f"   - 年化收益率: {result.get('annualReturn', 'N/A')}")
        print(f"   - 最大回撤: {result.get('maxDrawdown', 'N/A')}")
        print(f"   - 夏普比率: {result.get('sharpeRatio', 'N/A')}")
        print(f"   - 交易次数: {result.get('tradeCount', 'N/A')}")
        print(f"   - 资金曲线点数: {len(result.get('equityCurve', []))}")
        print(f"   - 交易记录数: {len(result.get('trades', []))}")
        print("\n测试完成！自定义策略回测功能已成功修复。")
    else:
        print("\n测试失败！自定义策略回测功能仍存在问题。")


if __name__ == '__main__':
    main()