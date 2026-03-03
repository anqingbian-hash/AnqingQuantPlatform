#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A股盯盘Agent - 模拟版"""

import json
from datetime import datetime, timedelta

class StockWatcher:
    def __init__(self, user_id="default"):
        self.user_id = user_id
        self.watched_stocks = []
        self.alerts = []

    def add_alert(self, symbol, name, reason, price, change_percent, volume):
        self.alerts.append({
            'symbol': symbol,
            'name': name,
            'reason': reason,
            'price': price,
            'change_percent': change_percent,
            'volume': volume,
            'time': datetime.now().isoformat()
        })

    def get_summary(self):
        return {
            'user_id': self.user_id,
            'watched_count': len(self.watched_stocks),
            'alerts_count': len(self.alerts),
            'summary': f"发现{len(self.alerts)}个异动，监控{len(self.watched_stocks)}只股票"
        }

# 模拟数据
class MockStockAPI:
    def get_stock_realtime(self, symbol):
        # 模拟真实数据
        base_price = 100.0
        import random
        change = random.uniform(-5, 8)
        price = base_price * (1 + change / 100)
        volume = random.randint(1000000, 5000000)
        return {
            'symbol': symbol,
            'name': f'{symbol}模拟股票',
            'price': price,
            'change': price - base_price,
            'change_percent': change,
            'volume': volume
        }

def monitor_stocks(watched_stocks, thresholds):
    """监控股票异动"""
    api = MockStockAPI()
    alerts = []
    
    for symbol in watched_stocks:
        data = api.get_stock_realtime(symbol)
        
        # 检查涨幅阈值
        if data['change_percent'] > thresholds['rise']:
            alerts.append({
                'symbol': symbol,
                'name': data['name'],
                'reason': f"涨幅{data['change_percent']:.2f}%超过阈值{thresholds['rise']}%",
                'price': data['price'],
                'change_percent': data['change_percent'],
                'volume': data['volume'],
                'time': datetime.now().isoformat()
            })
        
        # 检查成交额阈值
        amount = data['price'] * data['volume'] / 10000
        if amount > thresholds['amount']:
            alerts.append({
                'symbol': symbol,
                'name': data['name'],
                'reason': f"成交额{amount:.0f}万超过阈值{thresholds['amount']}万",
                'price': data['price',
                'change_percent': data['change_percent'],
                'volume': data['volume'],
                'time': datetime.now().isoformat()
            })
    
    return alerts

def main():
    print("=== A股盯盘Agent启动 ===")
    print("⏰ 监控：每5分钟刷新")
    
    # 模拟监控的股票列表
    watched_stocks = ['600519', '000858', '002594', '600036', '601318']
    thresholds = {
        'rise': 5.0,      # 涨幅>5%
        'amount': 5000      # 成交额>5000万
    }
    
    print(f"监控股票: {len(watched_stocks)} 只")
    print(f"涨停阈值: {thresholds['rise']}%")
    print(f"成交额阈值: {thresholds['amount']}万")
    
    # 模拟监控
    for i in range(10):
        print(f"\n--- 第{i+1}轮监控 ({9*5+9}:00) ---")
        alerts = monitor_stocks(watched_stocks, thresholds)
        
        if alerts:
            print(f"发现{len(alerts)}个异动：")
            for alert in alerts:
                print(f"  {alert['name']} - {alert['reason']}")
                print(f"  价格: {alert['price']:.2f} ({alert['change_percent']:+.2f}%)")
                print(f"  成交额: {alert['volume']/10000:.2f}万")
                print(f"  时间: {alert['time'][-8:]}")
    
    print("\n=== 盯控完成 ===")

if __name__ == "__main__":
    main()
