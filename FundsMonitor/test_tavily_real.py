#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Tavily API - 真实新闻搜索
"""
import os
import sys
from datetime import datetime

# 配置API密钥
os.environ['TAVILY_API_KEY'] = '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'

# 添加路径
sys.path.append('/root/.openclaw/workspace/FundsMonitor')
sys.path.append('/root/.openclaw/workspace/FundsMonitor/modules')

# 导入模块
from data_fetcher_v4 import DataFetcher

# 配置日志
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_tavily_real():
    """测试Tavily真实API"""
    print('='*80)
    print('测试Tavily API - 真实新闻搜索')
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
    
    # 创建DataFetcher实例
    print(f'\n【初始化】')
    print(f'创建DataFetcher实例...')
    fetcher = DataFetcher()
    print('✓ DataFetcher初始化完成')
    
    # 测试贵州茅台新闻
    print(f'\n【测试1】贵州茅台新闻搜索')
    print('-'*80)
    
    try:
        news_list = fetcher.fetch_stock_news(
            query='贵州茅台 业绩 公告',
            max_results=3,
            days=3
        )
        
        if news_list:
            print(f'✓ 新闻搜索成功: {len(news_list)} 条')
            
            for i, news in enumerate(news_list, 1):
                print(f'\n新闻 {i}:')
                print(f'  标题: {news.get("title", "N/A")}')
                print(f'  链接: {news.get("url", "N/A")}')
                print(f'  评分: {news.get("score", 0):.2f}')
                print(f'  摘要: {news.get("snippet", "N/A")[:100]}...')
        else:
            print('✗ 新闻搜索失败')
            return False
    except Exception as e:
        print(f'✗ 新闻搜索失败: {e}')
        return False
    
    # 测试AAPL新闻
    print(f'\n【测试2】AAPL新闻搜索')
    print('-'*80)
    
    try:
        news_list = fetcher.fetch_stock_news(
            query='Apple earnings report',
            max_results=3,
            days=3
        )
        
        if news_list:
            print(f'✓ 新闻搜索成功: {len(news_list)} 条')
            
            for i, news in enumerate(news_list, 1):
                print(f'\n新闻 {i}:')
                print(f'  标题: {news.get("title", "N/A")}')
                print(f'  链接: {news.get("url", "N/A")}')
                print(f'  评分: {news.get("score", 0):.2f}')
                print(f'  摘要: {news.get("snippet", "N/A")[:100]}...')
        else:
            print('✗ 新闻搜索失败')
            return False
    except Exception as e:
        print(f'✗ 新闻搜索失败: {e}')
        return False
    
    # 测试市场新闻
    print(f'\n【测试3】A股市场新闻')
    print('-'*80)
    
    try:
        news_list = fetcher.fetch_stock_news(
            query='A股 市场走势 资金流向',
            max_results=3,
            days=1
        )
        
        if news_list:
            print(f'✓ 新闻搜索成功: {len(news_list)} 条')
            
            for i, news in enumerate(news_list, 1):
                print(f'\n新闻 {i}:')
                print(f'  标题: {news.get("title", "N/A")}')
                print(f'  链接: {news.get("url", "N/A")}')
                print(f'  评分: {news.get("score", 0):.2f}')
                print(f'  摘要: {news.get("snippet", "N/A")[:100]}...')
        else:
            print('✗ 新闻搜索失败')
            return False
    except Exception as e:
        print(f'✗ 新闻搜索失败: {e}')
        return False
    
    # 保存新闻结果
    print(f'\n【保存新闻】')
    print('-'*80)
    
    output_dir = './output'
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存新闻结果到JSON
    all_news = []
    
    # 重新获取所有新闻
    queries = [
        ('贵州茅台 业绩 公告', 3, 3),
        ('Apple earnings report', 3, 3),
        ('A股 市场走势 资金流向', 3, 1)
    ]
    
    for query, max_results, days in queries:
        try:
            news_list = fetcher.fetch_stock_news(
                query=query,
                max_results=max_results,
                days=days
            )
            
            if news_list:
                all_news.extend(news_list)
        except Exception as e:
            print(f'✗ 搜索"{query}"失败: {e}')
    
    # 保存到JSON
    news_file = f'{output_dir}/tavily_news_real.json'
    
    import json
    with open(news_file, 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    
    print(f'✓ 新闻结果保存: {news_file}')
    print(f'  新闻总数: {len(all_news)} 条')
    
    print('\n' + '='*80)
    print('✅ Tavily API测试完成！真实新闻搜索成功！')
    print('='*80)
    
    return True


if __name__ == '__main__':
    success = test_tavily_real()
    
    if success:
        print('\n✅ Tavily API测试成功！')
        sys.exit(0)
    else:
        print('\n✗ Tavily API测试失败！')
        sys.exit(1)
