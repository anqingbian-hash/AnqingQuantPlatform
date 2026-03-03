#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Select Agent - 选10只潜力股"""

import json
import sys
from pathlib import Path

# 添加akshare路径
sys.path.insert(0, '/root/.openclaw/skills')

# Select Agent
class SelectAgent:
    def __init__(self):
        self.agent_name = "Select"
        self.role = "选10只潜力股"
        self.selected_stocks = []
    
    def load_research_data(self):
        """加载Research数据"""
        input_path = '/root/.openclaw/workspace/选股工厂/research_output.json'
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            print(f"⚠️ Research数据不存在，使用模拟数据")
            return self._get_mock_research_data()
    
    def _get_mock_research_data(self):
        """获取模拟Research数据"""
        return {
            'hot_sectors': [
                {'sector': '人工智能', 'rank': 1, 'change': 8.5},
                {'sector': '半导体', 'rank': 2, 'change': 7.2}
            ],
            'limit_up': [
                {'symbol': '600519', 'name': '贵州茅台', 'price': 1800.5, 'limit_up': 10.0, 'volume': 50000}
            ],
            'low_volume_rise': [
                {'symbol': '600036', 'name': '招商银行', 'price': 45.5, 'week_change': 6.5, 'volume_ratio': 2.8}
            ]
        }
    
    def select_stocks(self, research_data):
        """选10只潜力股"""
        # 模拟选股逻辑
        mock_stocks = [
            {'symbol': '600519', 'name': '贵州茅台', 'sector': '消费', 'score': 95, 'reason': '核心资产，龙头股'},
            {'symbol': '000858', 'name': '五粮液', 'sector': '消费', 'score': 92, 'reason': '白酒龙头，稳健增长'},
            {'symbol': '600036', 'name': '招商银行', 'sector': '金融', 'score': 90, 'reason': '银行龙头，低估值'},
            {'symbol': '601318', 'name': '中国平安', 'sector': '金融', 'score': 88, 'reason': '保险龙头，稳健'},
            {'symbol': '000001', 'name': '平安银行', 'sector': '金融', 'score': 85, 'reason': '股份制银行，成长性好'},
            {'symbol': '002594', 'name': '比亚迪', 'sector': '新能源', 'score': 93, 'reason': '新能源汽车龙头'},
            {'symbol': '300059', 'name': '东方财富', 'sector': '金融科技', 'score': 87, 'reason': '券商龙头'},
            {'symbol': '600276', 'name': '恒瑞医药', 'sector': '医药', 'score': 89, 'reason': '医药龙头，研发能力强'},
            {'symbol': '000858', 'name': '五粮液', 'sector': '消费', 'score': 91, 'reason': '白酒龙头，品牌价值高'},
            {'symbol': '601888', 'name': '中国中免', 'sector': '消费', 'score': 86, 'reason': '免税龙头，政策利好'}
        ]
        self.selected_stocks = mock_stocks
        return mock_stocks
    
    def get_summary(self):
        """获取选股总结"""
        return {
            'agent': self.agent_name,
            'selected_count': len(self.selected_stocks),
            'avg_score': sum(s['score'] for s in self.selected_stocks) / len(self.selected_stocks),
            'sectors': list(set(s['sector'] for s in self.selected_stocks)),
            'summary': f"选择{len(self.selected_stocks)}只潜力股，平均得分{sum(s['score'] for s in self.selected_stocks) / len(self.selected_stocks):.1f}"
        }

def main():
    print("=== Select Agent启动 ===")
    
    agent = SelectAgent()
    
    print("\n1. 加载Research数据...")
    research_data = agent.load_research_data()
    print(f"热点板块：{len(research_data.get('hot_sectors', []))} 个")
    print(f"涨停板：{len(research_data.get('limit_up', []))} 只")
    print(f"低位放量股：{len(research_data.get('low_volume_rise', []))} 只")
    
    print("\n2. 选择潜力股...")
    stocks = agent.select_stocks(research_data)
    print(f"选择{len(stocks)}只潜力股：\n")
    for i, stock in enumerate(stocks, 1):
        print(f"{i:2d}. {stock['name']} ({stock['symbol']})")
        print(f"    板块: {stock['sector']}")
        print(f"    评分: {stock['score']}")
        print(f"    理由: {stock['reason']}")
        print()
    
    print("=== Select Agent完成 ===")
    summary = agent.get_summary()
    print(f"总结：{summary['summary']}")
    print(f"板块分布：{', '.join(summary['sectors'])}")
    
    # 输出到文件
    output = {
        'selected_stocks': stocks,
        'summary': summary
    }
    output_path = '/root/.openclaw/workspace/选股工厂/select_output.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 结果已保存到：{output_path}")

if __name__ == '__main__':
    main()
