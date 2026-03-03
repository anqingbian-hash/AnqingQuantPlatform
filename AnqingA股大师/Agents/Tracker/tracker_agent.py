#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tracker Agent - 持仓跟踪"""

import json
from datetime import datetime
from pathlib import Path

class TrackerAgent:
    def __init__(self):
        self.agent_name = "Tracker"
        self.role = "持仓跟踪"
        self.positions = []
    
    def load_positions(self):
        """加载持仓数据"""
        positions_path = '/root/.openclaw/workspace/AnqingA股大师/positions.json'
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
        positions_path = '/root/.openclaw/workspace/AnqingA股大师/positions.json'
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
        stock_names = {
            '600519.SH': '贵州茅台',
            '000858.SZ': '五粮液',
            '600036.SH': '招商银行',
            '601318.SH': '中国平安',
            '000001.SZ': '平安银行'
        }
        return stock_names.get(symbol, symbol)
    
    def refresh_prices(self):
        """刷新持仓价格（待集成akshare）"""
        # 模拟数据
        import random
        for pos in self.positions:
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
