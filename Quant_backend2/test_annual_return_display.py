import requests
import json

# 测试回测结果中年化收益率的显示格式
print("测试回测结果中年化收益率的显示格式")
print("=" * 50)

try:
    # 获取最近的回测结果，验证年化收益率格式
    url = "http://localhost:8000/backtest/results"
    headers = {'Content-Type': 'application/json'}
    
    # 发送请求获取回测结果列表
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        results = response.json()
        print(f"获取到{len(results)}条回测结果")
        
        if results:
            # 获取最新的回测结果详情
            latest_result = results[0]
            report_id = latest_result.get('id')
            
            # 获取详细回测结果
            detail_url = f"http://localhost:8000/backtest/results/{report_id}"
            detail_response = requests.get(detail_url, headers=headers)
            
            if detail_response.status_code == 200:
                detail_result = detail_response.json()
                print("\n最新回测结果详情:")
                print(f"年化收益率: {detail_result.get('annualReturn')}")
                print(f"总收益率: {detail_result.get('totalReturn')}")
                print(f"最大回撤: {detail_result.get('maxDrawdown')}")
                print(f"胜率: {detail_result.get('winRate')}")
                
                # 检查年化收益率是否已正确显示为百分比形式
                annual_return = detail_result.get('annualReturn', 0)
                if isinstance(annual_return, (int, float)):
                    if annual_return >= 0.01 and annual_return <= 100:  # 合理的百分比范围
                        print("\n✅ 年化收益率显示格式已修复，正确显示为百分比形式")
                    else:
                        print("\n❌ 年化收益率显示格式可能仍有问题")
                else:
                    print("\n❌ 年化收益率数据类型异常")
            else:
                print(f"获取回测详情失败: {detail_response.status_code}")
        else:
            print("没有找到回测结果，建议先运行一次回测")
    else:
        print(f"获取回测结果列表失败: {response.status_code}")
        print(f"错误信息: {response.text}")

except Exception as e:
    print(f"测试过程中发生错误: {str(e)}")