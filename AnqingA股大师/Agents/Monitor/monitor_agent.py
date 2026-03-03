#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monitor Agent - 盘中盯盘"""

import json
from datetime import datetime

class MonitorAgent:
    def __init__(self):
        self.agent_name = "Monitor"
        self.role = "盘中盯盘"
        self.alerts = []
        self.watched_stocks = []
    
    def load_selected_stocks(self):
        """加载选中的股票"""
        # 模拟数据
        self.watched_stocks = [
            {'symbol': '600519', 'name': '贵州茅台'},
            {'symbol': '000858', 'name': '五粮液'},
            {'symbol': '600036', 'name': '招商银行'}
        ]
        return self.watched_stocks
    
    def check_alerts(self, thresholds=None):
        """检查异动（待集成akshare）"""
        if thresholds is None:
            thresholds = {
                'rise_threshold': 5.0,      # 涨幅>5%
                'volume_ratio': 2.0,        # 量比>2.0
                'amount_threshold': 10000000  # 成交额>1000万
            }
        
        # 模拟数据
        mock_alerts = [
            {
                'symbol': '600519',
                'name': '贵州茅台',
                'reason': '涨幅6.5%超过阈值5%',
                'price': 1800.50,
                'change_percent': 6.5,
                'volume': 50000,
                'time': datetime.now().strftime('%H:%M:%S')
            },
            {
                'symbol': '000858',
                'name': '五粮液',
                'reason': '量比2.5超过阈值2.0',
                'price': 180.50,
                'change_percent': 3.2,
                'volume': 30000,
                'time': datetime.now().strftime('%H:%M:%S')
            }
        ]
        
        self.alerts = mock_alerts
        return self.alerts
    
    def get_summary(self):
        """获取汇总"""
        return {
            'agent': self.agent_name,
            'watched_count': len(self.watched_stocks),
            'alerts_count': len(self.alerts),
            'summary': f"监控{len(self.watched_stocks)}只股票，发现{len(self.alerts)}个异动"
        }
