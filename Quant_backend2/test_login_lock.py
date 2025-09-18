#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json

def test_login_lock():
    """测试登录锁定功能"""
    base_url = 'http://localhost:8000'
    account = 'test_user'
    
    print('测试登录锁定功能:')
    print('=' * 50)
    
    # 测试多次错误登录
    for i in range(4):
        try:
            response = requests.post(f'{base_url}/auth/login', json={
                'account': account,
                'password': 'wrong_password'  # 故意使用错误密码
            })
            
            data = response.json()
            print(f'第{i+1}次错误登录: {data.get("message", "未知错误")} (状态码: {response.status_code})')
            
            if response.status_code == 423:
                print('✅ 用户已被锁定！')
                break
                
        except Exception as e:
            print(f'请求失败: {e}')
    
    print()
    print('测试正确登录:')
    try:
        response = requests.post(f'{base_url}/auth/login', json={
            'account': account,
            'password': '123456'  # 正确密码
        })
        
        data = response.json()
        print(f'正确登录: {data.get("message", "未知错误")} (状态码: {response.status_code})')
        
    except Exception as e:
        print(f'请求失败: {e}')

if __name__ == '__main__':
    test_login_lock()
