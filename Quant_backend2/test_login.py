#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import pprint

# 后端API地址
BASE_URL = "http://localhost:8000"

# 测试登录函数
def test_login():
    print("=== 登录功能测试 ===")
    
    # 测试账号信息（使用我们刚刚添加的测试账号）
    # 注意：根据API实现，参数名应该是 'account' 和 'password'
    test_credentials = {
        "account": "test_user",
        "password": "123456"
    }
    
    try:
        # 发送登录请求 - 尝试不同的请求格式
        print(f"发送登录请求到: {BASE_URL}/auth/login")
        print(f"测试账号: {test_credentials['account']}")
        
        # 尝试表单格式
        print("\n尝试使用表单格式发送请求...")
        response_form = requests.post(
            f"{BASE_URL}/auth/login",
            data=test_credentials
        )
        
        print(f"表单格式响应状态码: {response_form.status_code}")
        
        # 尝试JSON格式
        print("\n尝试使用JSON格式发送请求...")
        response_json = requests.post(
            f"{BASE_URL}/auth/login",
            json=test_credentials,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"JSON格式响应状态码: {response_json.status_code}")
        
        # 打印JSON格式响应内容
        try:
            response_data = response_json.json()
            print(f"JSON响应内容:")
            pprint.pprint(response_data)
            
            # 分析响应结果
            if response_json.status_code == 200:
                print("\n✅ 登录成功！数据库修复有效。")
                if 'access_token' in response_data:
                    print(f"获取到访问令牌: {response_data['access_token'][:20]}...")
            elif response_form.status_code == 200:
                # 如果表单格式成功
                response_data_form = response_form.json()
                print("\n✅ 登录成功（表单格式）！数据库修复有效。")
                if 'access_token' in response_data_form:
                    print(f"获取到访问令牌: {response_data_form['access_token'][:20]}...")
            else:
                print("\n❌ 登录失败。检查是否数据库修复正确或API格式是否匹配。")
        except json.JSONDecodeError:
            print(f"无法解析响应内容: {response_json.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    test_login()