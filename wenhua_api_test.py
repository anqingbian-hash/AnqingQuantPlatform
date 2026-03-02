#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文华财经API测试脚本
测试内容包括：登录、查找API、获取数据
"""

import requests
import time
import json

# 文华财经账号信息
USERNAME = "15162472220"
PASSWORD = "Baq19880219"

def test_login():
    """测试登录"""
    print("=== 测试1：文华财经登录 ===")
    print(f"会员号: {USERNAME}")
    
    # 尝试常见登录接口
    login_urls = [
        "https://api.wenhua.com/login",
        "https://www.wenhua.com/api/login",
        "https://member.wenhua.com/api/login",
        "https://passport.wenhua.com/login"
    ]
    
    for url in login_urls:
        try:
            print(f"\n尝试登录接口: {url}")
            response = requests.post(
                url,
                data={
                    "username": USERNAME,
                    "password": PASSWORD
                },
                timeout=10
            )
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    
                    # 检查是否有token
                    if "token" in data:
                        print(f"\n✅ 登录成功！获取到token: {data['token']}")
                        return True, data
                    elif "access_token" in data:
                        print(f"\n✅ 登录成功！获取到token: {data['access_token']}")
                        return True, data
                    elif "data" in data and "token" in data["data"]:
                        print(f"\n✅ 登录成功！获取到token: {data['data']['token']}")
                        return True, data
                    
                except:
                    print(f"响应内容: {response.text[:500]}")
            else:
                print(f"响应内容: {response.text[:500]}")
                
        except Exception as e:
            print(f"错误: {e}")
            continue
    
    print("\n❌ 所有登录接口都失败")
    return False, None

def find_api_documentation():
    """查找API文档"""
    print("\n=== 测试2：查找API文档 ===")
    
    # 常见API文档位置
    doc_urls = [
        "https://www.wenhua.com/api",
        "https://api.wenhua.com/docs",
        "https://member.wenhua.com/api/docs",
        "https://developer.wenhua.com/docs"
    ]
    
    for url in doc_urls:
        try:
            print(f"\n尝试访问API文档: {url}")
            response = requests.get(url, timeout=10)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ 找到API文档！")
                print(f"内容长度: {len(response.text)}")
                print(f"前500字: {response.text[:500]}")
                return url, response.text
            else:
                print(f"响应内容: {response.text[:200]}")
                
        except Exception as e:
            print(f"错误: {e}")
            continue
    
    print("\n❌ 所有API文档接口都失败")
    return None, None

def main():
    """主函数"""
    print("=== 文华财经API测试 ===")
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"会员号: {USERNAME}")
    print("")
    
    # 测试1：登录
    login_success, login_data = test_login()
    
    if not login_success:
        print("\n=== 登录失败，无法继续 ===")
        return
    
    # 测试2：查找API文档
    doc_url, doc_content = find_api_documentation()
    
    # 测试3：分析API文档
    if doc_content:
        print("\n=== 测试3：分析API文档 ===")
        print(f"正在分析API文档...")
        
        # 查找关键词
        keywords = [
            "期货", "持仓", "多空", "delta", "净量",
            "历史数据", "实时数据", "K线", "API", "接口"
        ]
        
        for keyword in keywords:
            if keyword in doc_content:
                print(f"✅ 找到关键词: {keyword}")
                # 提取包含关键词的行
                lines = doc_content.split('\n')
                for line in lines:
                    if keyword in line and len(line) < 200:
                        print(f"   {line.strip()}")
                        break
    
    print(f"\n=== 测试完成 ===")
    print(f"结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n接下来会:")
    print("1. 分析API文档结构")
    print("2. 查找数据接口")
    print("3. 测试数据接口")
    print("4. 设计数据模型")

if __name__ == "__main__":
    main()
