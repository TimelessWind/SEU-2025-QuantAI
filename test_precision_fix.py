#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试小数精度修复效果
"""

import requests
import json

# API端点
BACKEND_URL = "http://localhost:8000"
BACKTEST_DETAIL_URL = f"{BACKEND_URL}/backtest/detail/"
BACKTEST_HISTORY_URL = f"{BACKEND_URL}/backtest/history"

# 假设使用前面查询到的报告ID
test_report_id = "RPT_20250916_173517_600519.SH"

# 从数据库查询结果中获取的原始值参考
# 年化收益率: 0.1115
# 胜率: 0.1368
# 总收益率: 0.0508
# 最大回撤: 0.0309


def test_backtest_detail_precision():
    """测试回测详情接口的精度"""
    print("\n=== 测试回测详情接口精度 ===")
    
    try:
        # 添加认证头信息（假设使用固定token进行测试）
        headers = {
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiIxIiwiZXhwIjoxNzI5MDQ3MzIwfQ.joD2e9Z7s7T3L7xV7cFz4a8b2d5e7f1g3h5j8k9l0m2n4o7p9q0r3t6u8v9w1y2z4'  # 示例token
        }
        
        # 调用接口
        url = f"{BACKTEST_DETAIL_URL}{test_report_id}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                backtest_data = data.get('data', {})
                
                print(f"回测报告ID: {backtest_data.get('id')}")
                print(f"年化收益率: {backtest_data.get('annualReturn')}")
                print(f"总收益率: {backtest_data.get('totalReturn')}")
                print(f"胜率: {backtest_data.get('winRate')}")
                print(f"最大回撤: {backtest_data.get('maxDrawdown')}")
                print(f"夏普比率: {backtest_data.get('sharpeRatio')}")
                
                # 检查小数位数
                for key in ['annualReturn', 'totalReturn', 'winRate', 'maxDrawdown', 'sharpeRatio']:
                    value = backtest_data.get(key)
                    if value is not None:
                        # 转换为字符串检查小数位数
                        value_str = f"{value:.4f}"
                        print(f"{key} (4位小数格式): {value_str}")
            else:
                print(f"获取回测详情失败: {data.get('message')}")
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"测试出错: {e}")


def test_backtest_history_precision():
    """测试回测历史接口的精度"""
    print("\n=== 测试回测历史接口精度 ===")
    
    try:
        # 添加认证头信息
        headers = {
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiIxIiwiZXhwIjoxNzI5MDQ3MzIwfQ.joD2e9Z7s7T3L7xV7cFz4a8b2d5e7f1g3h5j8k9l0m2n4o7p9q0r3t6u8v9w1y2z4'  # 示例token
        }
        
        # 调用接口
        response = requests.get(BACKTEST_HISTORY_URL, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                records = data.get('records', [])
                print(f"获取到 {len(records)} 条历史记录")
                
                if records:
                    # 显示第一条记录的精度信息
                    first_record = records[0]
                    print(f"第一条记录ID: {first_record.get('id')}")
                    print(f"总收益率: {first_record.get('totalReturn')}")
                    print(f"最大回撤: {first_record.get('maxDrawdown')}")
                    print(f"夏普比率: {first_record.get('sharpeRatio')}")
                    
                    # 检查小数位数
                    for key in ['totalReturn', 'maxDrawdown', 'sharpeRatio']:
                        value = first_record.get(key)
                        if value is not None:
                            # 转换为字符串检查小数位数
                            value_str = f"{value:.4f}"
                            print(f"{key} (4位小数格式): {value_str}")
            else:
                print(f"获取回测历史失败: {data.get('message')}")
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"测试出错: {e}")


if __name__ == "__main__":
    print("开始测试小数精度修复效果...")
    test_backtest_detail_precision()
    test_backtest_history_precision()
    print("\n测试完成！")