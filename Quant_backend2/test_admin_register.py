#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json

def test_admin_register():
    """测试管理员注册功能"""
    base_url = 'http://localhost:8000'
    
    print('测试管理员注册功能:')
    print('=' * 50)
    
    # 测试注册管理员
    admin_data = {
        'account': 'admin_new',
        'email': 'admin_new@test.com',
        'phone': '13800138003',
        'password': '123456',
        'role': 'admin'
    }
    
    try:
        response = requests.post(f'{base_url}/auth/register', json=admin_data)
        data = response.json()
        print(f'管理员注册: {data.get("message", "未知错误")} (状态码: {response.status_code})')
        
        if response.status_code == 201:
            print('✅ 管理员注册成功！')
            
            # 测试管理员登录
            print('\n测试管理员登录:')
            login_data = {
                'account': 'admin_new',
                'password': '123456'
            }
            
            login_response = requests.post(f'{base_url}/auth/login', json=login_data)
            login_result = login_response.json()
            print(f'管理员登录: {login_result.get("message", "未知错误")} (状态码: {login_response.status_code})')
            
            if login_response.status_code == 200:
                print('✅ 管理员登录成功！')
                print(f'用户角色: {login_result.get("user", {}).get("role", "未知")}')
            else:
                print('❌ 管理员登录失败')
        else:
            print('❌ 管理员注册失败')
            
    except Exception as e:
        print(f'请求失败: {e}')

if __name__ == '__main__':
    test_admin_register()
