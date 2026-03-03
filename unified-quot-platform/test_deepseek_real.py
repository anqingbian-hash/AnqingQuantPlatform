#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试DeepSeek API - 真实LLM决策
"""
import os
import sys
from datetime import datetime

# 配置API密钥
os.environ['DEEPSEEK_API_KEY'] = 'sk-446299a62b7c414ba2af12873290a071'

# 添加路径
sys.path.append('/root/.openclaw/workspace/unified-quot-platform')

# 导入模块
from decision_maker import DecisionMaker

# 配置日志
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_deepseek_real():
    """测试DeepSeek真实API"""
    print('='*80)
    print('测试DeepSeek API - 真实LLM决策')
    print('='*80)
    
    # 检查API密钥
    api_key = os.getenv('DEEPSEEK_API_KEY')
    
    print(f'\n【API配置】')
    print(f'DeepSeek API密钥: {api_key[:10]}...{api_key[-4:]}')
    print(f'API密钥长度: {len(api_key)}')
    
    if not api_key:
        print('✗ API密钥未配置')
        return False
    
    print('✓ API密钥已配置')
    
    # 创建DecisionMaker实例
    print(f'\n【初始化】')
    print(f'创建DecisionMaker实例...')
    maker = DecisionMaker(model='deepseek/deepseek-chat', api_key=api_key)
    print('✓ DecisionMaker初始化完成')
    
    # 测试贵州茅台
    print(f'\n【测试1】贵州茅台（600519.SH）')
    print('-'*80)
    
    moutai_market_data = {
        'stock_quote': {
            'code': '600519.SH',
            'name': '贵州茅台',
            'price': 1440.00,
            'change_pct': 0.5
        },
        'fund_flow': {
            'north_inflow': 30.0,
            'margin_growth': 5.0
        },
        'news': [
            {
                'title': '贵州茅台2025年业绩超预期，机构上调评级',
                'score': 0.9,
                'url': 'https://example.com'
            },
            {
                'title': '贵州茅台新产品上市，销量突破预期',
                'score': 0.8,
                'url': 'https://example.com'
            },
            {
                'title': '贵州茅台股价创新高，短期回调风险增加',
                'score': 0.6,
                'url': 'https://example.com'
            }
        ]
    }
    
    # 生成决策
    print('生成交易决策...')
    moutai_decision = maker.generate_decision(moutai_market_data)
    
    if moutai_decision:
        print('✓ 贵州茅台决策生成成功')
        print(f'  交易决策: {moutai_decision.get("decision", "N/A")}')
        print(f'  操作建议: {moutai_decision.get("action", "N/A")}')
        print(f'  入场点位: {moutai_decision.get("entry_point", "N/A")}')
        print(f'  止损位: {moutai_decision.get("stop_loss", "N/A")}')
        print(f'  止盈位: {moutai_decision.get("take_profit", "N/A")}')
        print(f'  市场环境: {moutai_decision.get("market_env", "N/A")}')
        print(f'  风险等级: {moutai_decision.get("risk_level", "N/A")}')
    else:
        print('✗ 贵州茅台决策生成失败')
        return False
    
    # 生成仪表盘
    print('\n生成决策仪表盘...')
    moutai_dashboard = maker.generate_dashboard(moutai_decision)
    
    if moutai_dashboard:
        print('✓ 贵州茅台仪表盘生成成功')
    else:
        print('✗ 贵州茅台仪表盘生成失败')
        return False
    
    # 测试AAPL
    print(f'\n【测试2】AAPL美股（Apple Inc.）')
    print('-'*80)
    
    aapl_market_data = {
        'stock_quote': {
            'code': 'AAPL',
            'name': '苹果（Apple Inc.）',
            'price': 175.00,
            'change_pct': 1.16
        },
        'fund_flow': {
            'north_inflow': 0,
            'margin_growth': 0
        },
        'news': [
            {
                'title': 'Apple发布新款产品，市场反应积极',
                'score': 0.85,
                'url': 'https://example.com'
            },
            {
                'title': 'iPhone销量超预期，股价创新高',
                'score': 0.8,
                'url': 'https://example.com'
            },
            {
                'title': 'Apple财报亮眼，机构上调目标价',
                'score': 0.75,
                'url': 'https://example.com'
            }
        ]
    }
    
    # 生成决策
    print('生成交易决策...')
    aapl_decision = maker.generate_decision(aapl_market_data)
    
    if aapl_decision:
        print('✓ AAPL决策生成成功')
        print(f'  交易决策: {aapl_decision.get("decision", "N/A")}')
        print(f'  操作建议: {aapl_decision.get("action", "N/A")}')
        print(f'  入场点位: {aapl_decision.get("entry_point", "N/A")}')
        print(f'  止损位: {aapl_decision.get("stop_loss", "N/A")}')
        print(f'  止盈位: {aapl_decision.get("take_profit", "N/A")}')
        print(f'  市场环境: {aapl_decision.get("market_env", "N/A")}')
        print(f'  风险等级: {aapl_decision.get("risk_level", "N/A")}')
    else:
        print('✗ AAPL决策生成失败')
        return False
    
    # 生成仪表盘
    print('\n生成决策仪表盘...')
    aapl_dashboard = maker.generate_dashboard(aapl_decision)
    
    if aapl_dashboard:
        print('✓ AAPL仪表盘生成成功')
    else:
        print('✗ AAPL仪表盘生成失败')
        return False
    
    # 保存报告
    print(f'\n【保存报告】')
    print('-'*80)
    
    output_dir = './output'
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存贵州茅台报告
    moutai_file = f'{output_dir}/moutai_decision_report_real.md'
    with open(moutai_file, 'w', encoding='utf-8') as f:
        f.write(moutai_dashboard)
    print(f'✓ 贵州茅台报告保存: {moutai_file}')
    
    # 保存AAPL报告
    aapl_file = f'{output_dir}/aapl_decision_report_real.md'
    with open(aapl_file, 'w', encoding='utf-8') as f:
        f.write(aapl_dashboard)
    print(f'✓ AAPL报告保存: {aapl_file}')
    
    # 打印贵州茅台仪表盘
    print(f'\n【贵州茅台决策仪表盘】')
    print('='*80)
    print(moutai_dashboard)
    
    # 打印AAPL仪表盘
    print(f'\n【AAPL决策仪表盘】')
    print('='*80)
    print(aapl_dashboard)
    
    print('\n' + '='*80)
    print('✅ DeepSeek API测试完成！真实LLM决策成功！')
    print('='*80)
    
    return True


if __name__ == '__main__':
    success = test_deepseek_real()
    
    if success:
        print('\n✅ DeepSeek API测试成功！')
        sys.exit(0)
    else:
        print('\n✗ DeepSeek API测试失败！')
        sys.exit(1)
