import requests
import json
import time

# 测试脚本：验证回测结果和回测详情中的小数位数一致性

# API基础URL
BASE_URL = "http://127.0.0.1:8000"

# 获取用户token（实际使用时替换为有效的token）
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3MzA0NDc2NDB9.5GjUvO7u9LpQ0eJ6vqQbZJdQ8Z1qX2wY3eR4tT5yU7iO8pA9sD1fG2hK3jL4kM5n"

# 请求头
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}

def test_equity_curve_decimal_format():
    """测试资金曲线数据的小数位数格式"""
    print("===== 开始测试资金曲线数据小数位数格式 =====")
    
    try:
        # 1. 获取回测结果列表
        print("正在获取回测结果列表...")
        results_url = f"{BASE_URL}/backtest/results?page=1&pageSize=5"
        response = requests.get(results_url, headers=headers)
        
        if response.status_code != 200:
            print(f"获取回测结果列表失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return
            
        results_data = response.json()
        if not results_data.get('success'):
            print(f"获取回测结果列表失败: {results_data.get('message')}")
            return
            
        results = results_data.get('data', {}).get('items', [])
        if not results:
            print("未找到回测结果数据")
            return
            
        print(f"成功获取到 {len(results)} 条回测结果")
        
        # 选择第一条回测结果进行详细测试
        first_result = results[0]
        report_id = first_result.get('id')
        
        if not report_id:
            print("未找到有效的回测报告ID")
            return
            
        print(f"选择回测报告ID: {report_id} 进行详细测试")
        
        # 2. 查看回测结果中的资金曲线数据
        print("\n=== 回测结果页面的资金曲线数据 ===")
        equity_curve = first_result.get('equityCurve', [])
        if equity_curve:
            print(f"资金曲线数据点数量: {len(equity_curve)}")
            
            # 检查小数位数
            decimal_places = []
            for point in equity_curve[:5]:  # 只检查前5个点
                value = point.get('value')
                if value is not None:
                    # 计算小数位数
                    decimal_str = str(value).split('.')[1] if '.' in str(value) else ''
                    decimal_places.append(len(decimal_str))
                    print(f"日期: {point.get('date')}, 数值: {value}, 小数位数: {len(decimal_str)}")
            
            if decimal_places:
                print(f"回测结果页面资金曲线数据的小数位数分布: {set(decimal_places)}")
        else:
            print("回测结果中未找到资金曲线数据")
            
        # 3. 获取回测详情
        print(f"\n正在获取回测详情 (ID: {report_id})...")
        detail_url = f"{BASE_URL}/backtest/results/{report_id}"
        response = requests.get(detail_url, headers=headers)
        
        if response.status_code != 200:
            print(f"获取回测详情失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return
            
        detail_data = response.json()
        if not detail_data.get('success'):
            print(f"获取回测详情失败: {detail_data.get('message')}")
            return
            
        detail = detail_data.get('data')
        if not detail:
            print("未找到回测详情数据")
            return
            
        # 4. 查看回测详情中的资金曲线数据
        print("\n=== 回测详情页面的资金曲线数据 ===")
        detail_equity_curve = detail.get('equityCurve', [])
        if detail_equity_curve:
            print(f"资金曲线数据点数量: {len(detail_equity_curve)}")
            
            # 检查小数位数
            detail_decimal_places = []
            for point in detail_equity_curve[:5]:  # 只检查前5个点
                value = point.get('value')
                if value is not None:
                    # 计算小数位数
                    decimal_str = str(value).split('.')[1] if '.' in str(value) else ''
                    detail_decimal_places.append(len(decimal_str))
                    print(f"日期: {point.get('date')}, 数值: {value}, 小数位数: {len(decimal_str)}")
            
            if detail_decimal_places:
                print(f"回测详情页面资金曲线数据的小数位数分布: {set(detail_decimal_places)}")
        else:
            print("回测详情中未找到资金曲线数据")
            
        # 5. 对比两个页面的小数位数是否一致
        print("\n=== 小数位数一致性检查 ===")
        if decimal_places and detail_decimal_places:
            if set(decimal_places) == set(detail_decimal_places):
                print("✅ 回测结果页面和回测详情页面的资金曲线数据小数位数一致！")
                print(f"小数位数: {set(decimal_places)}")
            else:
                print("❌ 回测结果页面和回测详情页面的资金曲线数据小数位数不一致！")
                print(f"回测结果页面: {set(decimal_places)}")
                print(f"回测详情页面: {set(detail_decimal_places)}")
        
        print("\n===== 测试完成 =====")
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")

if __name__ == "__main__":
    test_equity_curve_decimal_format()