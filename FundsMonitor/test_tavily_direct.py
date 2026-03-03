#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接使用Tavily SDK - 不通过litellm
"""
import os
import sys
import logging

# 配置API密钥
os.environ['TAVILY_API_KEY'] = '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'

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_tavily_direct():
    """直接测试Tavily SDK"""
    print('='*80)
    print('直接测试Tavily SDK - 不通过litellm')
    print('='*80)
    
    # 检查API密钥
    api_key = os.getenv('TAVILY_API_KEY')
    
    print(f'\n【API配置】')
    print(f'Tavily API密钥: {api_key[:15]}...{api_key[-5:]}')
    print(f'API密钥长度: {len(api_key)}')
    
    if not api_key:
        print('✗ API密钥未配置')
        return False
    
    print('✓ API密钥已配置')
    
    # 方法1：使用tavily-python SDK
    print(f'\n【方法1】使用tavily-python SDK')
    print('-'*80)
    
    try:
        from tavily import TavilyClient as Client
        import tavily
        
        # 检查SDK版本
        try:
            print(f'Tavily SDK版本: {tavily.__version__}')
        except AttributeError:
            print('Tavily SDK版本: 未知（无法获取__version__）')
        
        # 创建客户端（使用TavilyClient）
        client = Client(api_key=api_key)
        print('✓ Tavily客户端创建成功')
        
        # 搜索贵州茅台新闻
        print('\n搜索贵州茅台最新新闻...')
        result = client.search(
            query='贵州茅台 最新新闻 公告',
            search_depth="basic",
            max_results=3,
            topic="news"
        )
        
        print('✓ 新闻搜索成功')
        print(f'  返回结果类型: {type(result)}')
        
        if result:
            print(f'  返回结果: {result}')
            
            if 'results' in result:
                results = result['results']
                print(f'  找到 {len(results)} 条新闻')
                
                for i, news in enumerate(results, 1):
                    print(f'\n新闻 {i}:')
                    print(f'  标题: {news.get("title", "N/A")}')
                    print(f'  链接: {news.get("url", "N/A")}')
                    print(f'  摘要: {news.get("content", "N/A")[:100]}...')
            else:
                print('⚠️  未找到results字段')
                print(f'  原始返回: {result}')
        else:
            print('⚠️  未找到新闻结果')
        
    except ImportError as e:
        print(f'✗ 导入tavily失败: {e}')
        return False
    except Exception as e:
        print(f'✗ Tavily SDK调用失败: {e}')
        logger.error(f"[Tavily] 错误详情: {e}", exc_info=True)
        return False
    
    # 方法2：使用requests直接调用API
    print(f'\n【方法2】使用requests直接调用API')
    print('-'*80)
    
    try:
        import requests
        import json
        
        url = "https://api.tavily.com/search"
        
        params = {
            "api_key": api_key,
            "query": "贵州茅台 最新新闻 公告",
            "search_depth": "basic",
            "max_results": 3
        }
        
        print(f'请求URL: {url}')
        print(f'请求参数: {json.dumps(params, ensure_ascii=False, indent=2)}')
        
        response = requests.post(url, json=params)
        
        print(f'\n响应状态码: {response.status_code}')
        print(f'响应头: {dict(response.headers)}')
        
        if response.status_code == 200:
            result = response.json()
            print('✓ API调用成功')
            print(f'  响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}')
            
            if 'results' in result:
                results = result['results']
                print(f'  找到 {len(results)} 条新闻')
                
                for i, news in enumerate(results, 1):
                    print(f'\n新闻 {i}:')
                    print(f'  标题: {news.get("title", "N/A")}')
                    print(f'  链接: {news.get("url", "N/A")}')
                    print(f'  摘要: {news.get("content", "N/A")[:100]}...')
        else:
            print(f'✗ API调用失败')
            print(f'  错误响应: {response.text}')
            return False
            
    except ImportError as e:
        print(f'✗ 导入requests失败: {e}')
        return False
    except Exception as e:
        print(f'✗ API调用失败: {e}')
        logger.error(f"[Tavily] 错误详情: {e}", exc_info=True)
        return False
    
    print('\n' + '='*80)
    print('✅ Tavily SDK测试完成！')
    print('='*80)
    
    return True


if __name__ == '__main__':
    success = test_tavily_direct()
    
    if success:
        print('\n✅ Tavily SDK测试成功！')
        sys.exit(0)
    else:
        print('\n✗ Tavily SDK测试失败！')
        sys.exit(1)
