#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Review Agent - 审核并推荐"""

import json
import sys
from pathlib import Path

# 添加akshare路径
sys.path.insert(0, '/root/.openclaw/skills')

# Review Agent
class ReviewAgent:
    def __init__(self):
        self.agent_name = "Review"
        self.role = "审核并推荐"
        self.recommended_stocks = []
    
    def load_backtest_data(self):
        """加载Backtest数据"""
        input_path = '/root/.openclaw/workspace/选股工厂/backtest_output.json'
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            print(f"⚠️ Backtest数据不存在，使用模拟数据")
            return self._get_mock_backtest_data()
    
    def _get_mock_backtest_data(self):
        """获取模拟Backtest数据"""
        return {
            'backtest_results': [
                {
                    'symbol': '600519',
                    'name': '贵州茅台',
                    'annual_return': 15.5,
                    'max_drawdown': -8.5,
                    'sharpe_ratio': 1.35,
                    'win_rate': 0.65,
                    'notes': 'MACD金叉策略表现良好'
                },
                {
                    'symbol': '000858',
                    'name': '五粮液',
                    'annual_return': 12.8,
                    'max_drawdown': -7.5,
                    'sharpe_ratio': 1.45,
                    'win_rate': 0.70,
                    'notes': '稳健增长，适合长线持有'
                }
            ],
            'summary': {
                'backtest_count': 10,
                'avg_annual_return': 12.5,
                'avg_sharpe_ratio': 1.35,
                'recommended_count': 8
            }
        }
    
    def review_stocks(self, backtest_data):
        """审核股票并推荐"""
        recommended = []
        for result in backtest_data.get('backtest_results', []):
            # 推荐条件：夏普比率>1.2
            if result['sharpe_ratio'] > 1.2:
                stock = {
                    'symbol': result['symbol'],
                    'name': result['name'],
                    'annual_return': result['annual_return'],
                    'max_drawdown': result['max_drawdown'],
                    'sharpe_ratio': result['sharpe_ratio'],
                    'win_rate': result['win_rate'],
                    'recommendation': '推荐买入',
                    'risk_level': '中低风险',
                    'hold_period': '中长线持有',
                    'notes': result['notes']
                }
                recommended.append(stock)
        
        # 按夏普比率排序
        recommended.sort(key=lambda x: x['sharpe_ratio'], reverse=True)
        self.recommended_stocks = recommended
        return recommended
    
    def get_summary(self):
        """获取审核总结"""
        if not self.recommended_stocks:
            return {
                'agent': self.agent_name,
                'recommended_count': 0,
                'summary': '没有推荐股票'
            }
        
        avg_return = sum(s['annual_return'] for s in self.recommended_stocks) / len(self.recommended_stocks)
        avg_sharpe = sum(s['sharpe_ratio'] for s in self.recommended_stocks) / len(self.recommended_stocks)
        
        return {
            'agent': self.agent_name,
            'recommended_count': len(self.recommended_stocks),
            'avg_annual_return': avg_return,
            'avg_sharpe_ratio': avg_sharpe,
            'top_stock': self.recommended_stocks[0],
            'summary': f"推荐{len(self.recommended_stocks)}只股票，平均年化收益{avg_return:.1f}%，平均夏普比率{avg_sharpe:.2f}"
        }

def main():
    print("=== Review Agent启动 ===")
    
    agent = ReviewAgent()
    
    print("\n1. 加载Backtest数据...")
    backtest_data = agent.load_backtest_data()
    backtest_count = len(backtest_data.get('backtest_results', []))
    print(f"回测股票：{backtest_count} 只")
    
    print("\n2. 审核股票...")
    print("推荐条件：夏普比率 > 1.2")
    
    recommended = agent.review_stocks(backtest_data)
    print(f"\n推荐股票（{len(recommended)}只）：\n")
    
    for i, stock in enumerate(recommended, 1):
        print(f"{i}. {stock['name']} ({stock['symbol']})")
        print(f"   推荐：{stock['recommendation']}")
        print(f"   年化收益：{stock['annual_return']:.1f}%")
        print(f"   最大回撤：{stock['max_drawdown']:.1f}%")
        print(f"   夏普比率：{stock['sharpe_ratio']:.2f}")
        print(f"   胜率：{stock['win_rate']*100:.0f}%")
        print(f"   风险等级：{stock['risk_level']}")
        print(f"   持有周期：{stock['hold_period']}")
        print(f"   备注：{stock['notes']}\n")
    
    print("=== Review Agent完成 ===")
    summary = agent.get_summary()
    print(f"总结：{summary['summary']}")
    
    if summary.get('top_stock'):
        print(f"\n最佳股票：{summary['top_stock']['name']} ({summary['top_stock']['symbol']})")
        print(f"夏普比率：{summary['top_stock']['sharpe_ratio']:.2f}")
        print(f"年化收益：{summary['top_stock']['annual_return']:.1f}%")
    
    # 输出到文件
    output = {
        'recommended_stocks': recommended,
        'summary': summary
    }
    output_path = '/root/.openclaw/workspace/选股工厂/review_output.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 结果已保存到：{output_path}")
    
    # 生成Markdown报告
    self._generate_markdown_report(recommended, summary, output_path)
    
def _generate_markdown_report(self, recommended, summary, output_path):
    """生成Markdown报告"""
    md_path = '/root/.openclaw/workspace/选股工厂/review_report.md'
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("# 选股工厂 - 审核报告\n\n")
        f.write(f"**生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## 📊 推荐股票清单\n\n")
        
        for i, stock in enumerate(recommended, 1):
            f.write(f"### {i}. {stock['name']} ({stock['symbol']})\n\n")
            f.write(f"- **推荐**：{stock['recommendation']}\n")
            f.write(f"- **年化收益**：{stock['annual_return']:.1f}%\n")
            f.write(f"- **最大回撤**：{stock['max_drawdown']:.1f}%\n")
            f.write(f"- **夏普比率**：{stock['sharpe_ratio']:.2f}\n")
            f.write(f"- **胜率**：{stock['win_rate']*100:.0f}%\n")
            f.write(f"- **风险等级**：{stock['risk_level']}\n")
            f.write(f"- **持有周期**：{stock['hold_period']}\n")
            f.write(f"- **备注**：{stock['notes']}\n\n")
        
        f.write("## 📈 总结\n\n")
        f.write(f"- 推荐股票：{summary['recommended_count']} 只\n")
        f.write(f"- 平均年化收益：{summary['avg_annual_return']:.1f}%\n")
        f.write(f"- 平均夏普比率：{summary['avg_sharpe_ratio']:.2f}\n")
        
        if summary.get('top_stock'):
            f.write(f"\n## 🏆 最佳股票\n\n")
            f.write(f"- **名称**：{summary['top_stock']['name']} ({summary['top_stock']['symbol']})\n")
            f.write(f"- **夏普比率**：{summary['top_stock']['sharpe_ratio']:.2f}\n")
            f.write(f"- **年化收益**：{summary['top_stock']['annual_return']:.1f}%\n")
    
    print(f"✅ Markdown报告已生成：{md_path}")

if __name__ == '__main__':
    main()
