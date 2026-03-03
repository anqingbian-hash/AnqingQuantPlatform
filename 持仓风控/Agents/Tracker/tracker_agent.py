#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tracker Agent - 实时跟踪持仓"""

import json
import sys
from pathlib import Path
from datetime import datetime

# 添加akshare路径
sys.path.insert(0, '/root/.openclaw/skills')

# Tracker Agent
class TrackerAgent:
    def __init__(self):
        self.agent_name = "Tracker"
        self.role = "实时跟踪持仓"
        self.positions = []
        self.current_prices = {}
    
    def load_positions(self):
        """加载持仓数据"""
        positions_path = '/root/.openclaw/workspace/持仓风控/positions.json'
        try:
            with open(positions_path, 'r', encoding='utf-8') as f:
                self.positions = json.load(f)
            return self.positions
        except FileNotFoundError:
            # 初始化示例持仓
            self.positions = self._init_sample_positions()
            self._save_positions()
            return self.positions
    
    def _init_sample_positions(self):
        """初始化示例持仓"""
        return [
            {
                'symbol': '600519.SH',
                'name': '贵州茅台',
                'shares': 1000,
                'avg_cost': 1700.00,
                'current_price': 1800.00,
                'market_value': 1800000.00,
                'profit_loss': 100000.00,
                'profit_loss_percent': 5.88,
                'buy_date': '2024-01-15',
                'notes': '核心资产，龙头股'
            }
        ]
    
    def _save_positions(self):
        """保存持仓数据"""
        positions_path = '/root/.openclaw/workspace/持仓风控/positions.json'
        with open(positions_path, 'w', encoding='utf-8') as f:
            json.dump(self.positions, f, ensure_ascii=False, indent=2)
    
    def add_position(self, symbol, shares, current_price, notes=""):
        """添加持仓"""
        # 检查是否已存在
        existing = next((p for p in self.positions if p['symbol'] == symbol), None)
        
        if existing:
            # 更新持仓
            total_shares = existing['shares'] + shares
            total_cost = existing['avg_cost'] * existing['shares'] + current_price * shares
            existing['shares'] = total_shares
            existing['avg_cost'] = total_cost / total_shares
            existing['current_price'] = current_price
            existing['market_value'] = total_shares * current_price
            existing['profit_loss'] = (current_price - existing['avg_cost']) * total_shares
            existing['profit_loss_percent'] = (current_price - existing['avg_cost']) / existing['avg_cost'] * 100
            existing['notes'] = notes if notes else existing['notes']
        else:
            # 新增持仓
            position = {
                'symbol': symbol,
                'name': self._get_stock_name(symbol),
                'shares': shares,
                'avg_cost': current_price,
                'current_price': current_price,
                'market_value': shares * current_price,
                'profit_loss': 0.0,
                'profit_loss_percent': 0.0,
                'buy_date': datetime.now().strftime('%Y-%m-%d'),
                'notes': notes
            }
            self.positions.append(position)
        
        self._save_positions()
        return True
    
    def sell_position(self, symbol, shares):
        """卖出持仓"""
        existing = next((p for p in self.positions if p['symbol'] == symbol), None)
        
        if existing:
            if shares >= existing['shares']:
                # 全部卖出
                self.positions.remove(existing)
            else:
                # 部分卖出
                existing['shares'] -= shares
                existing['market_value'] = existing['shares'] * existing['current_price']
                existing['profit_loss'] = (existing['current_price'] - existing['avg_cost']) * existing['shares']
                existing['profit_loss_percent'] = (existing['current_price'] - existing['avg_cost']) / existing['avg_cost'] * 100
            
            self._save_positions()
            return True
        return False
    
    def _get_stock_name(self, symbol):
        """获取股票名称（模拟）"""
        # 模拟数据 - 待集成akshare
        stock_names = {
            '600519.SH': '贵州茅台',
            '000001.SZ': '平安银行',
            '600036.SH': '招商银行',
            '601318.SH': '中国平安'
        }
        return stock_names.get(symbol, symbol)
    
    def refresh_prices(self):
        """刷新持仓价格（模拟）"""
        # 模拟数据 - 待集成akshare
        for pos in self.positions:
            # 模拟价格波动（±2%）
            import random
            change = random.uniform(-0.02, 0.02)
            pos['current_price'] = pos['current_price'] * (1 + change)
            pos['market_value'] = pos['shares'] * pos['current_price']
            pos['profit_loss'] = (pos['current_price'] - pos['avg_cost']) * pos['shares']
            pos['profit_loss_percent'] = (pos['current_price'] - pos['avg_cost']) / pos['avg_cost'] * 100
        
        self._save_positions()
        return self.positions
    
    def get_summary(self):
        """获取持仓汇总"""
        total_market_value = sum(p['market_value'] for p in self.positions)
        total_profit_loss = sum(p['profit_loss'] for p in self.positions)
        avg_profit_loss_percent = total_profit_loss / sum(p['avg_cost'] * p['shares'] for p in self.positions) * 100 if self.positions else 0
        
        return {
            'agent': self.agent_name,
            'positions_count': len(self.positions),
            'total_market_value': total_market_value,
            'total_profit_loss': total_profit_loss,
            'avg_profit_loss_percent': avg_profit_loss_percent,
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'summary': f"持仓{len(self.positions)}只，市值{total_market_value/10000:.2f}万，盈亏{total_profit_loss/10000:.2f}万（{avg_profit_loss_percent:+.2f}%）"
        }

def main():
    print("=== Tracker Agent启动 ===")
    
    agent = TrackerAgent()
    
    print("\n1. 加载持仓数据...")
    positions = agent.load_positions()
    print(f"持仓数量：{len(positions)} 只")
    
    print("\n2. 刷新持仓价格...")
    positions = agent.refresh_prices()
    
    print("\n持仓明细：\n")
    for i, pos in enumerate(positions, 1):
        print(f"{i}. {pos['name']} ({pos['symbol']})")
        print(f"   持仓：{pos['shares']} 股")
        print(f"   成本价：{pos['avg_cost']:.2f}")
        print(f"   现价：{pos['current_price']:.2f}")
        print(f"   市值：{pos['market_value']/10000:.2f} 万")
        print(f"   盈亏：{pos['profit_loss']/10000:+.2f} 万（{pos['profit_loss_percent']:+.2f}%）")
        print(f"   备注：{pos['notes']}")
        print()
    
    print("=== Tracker Agent完成 ===")
    summary = agent.get_summary()
    print(f"汇总：{summary['summary']}")
    
    # 输出到文件
    output_path = '/root/.openclaw/workspace/持仓风控/tracker_output.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'positions': positions,
            'summary': summary
        }, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 结果已保存到：{output_path}")

if __name__ == '__main__':
    main()
