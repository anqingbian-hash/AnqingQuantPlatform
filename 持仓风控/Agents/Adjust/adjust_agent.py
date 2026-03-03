#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Adjust Agent - 建议调仓"""

import json
import sys
from pathlib import Path
from datetime import datetime

# 添加akshare路径
sys.path.insert(0, '/root/.openclaw/skills')

# Adjust Agent
class AdjustAgent:
    def __init__(self):
        self.agent_name = "Adjust"
        self.role = "建议调仓"
        self.adjustments = []
    
    def load_tracker_data(self):
        """加载Tracker数据"""
        input_path = '/root/.openclaw/workspace/持仓风控/tracker_output.json'
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            print(f"⚠️ Tracker数据不存在")
            return None
    
    def load_risk_data(self):
        """加载Risk数据"""
        input_path = '/root/.openclaw/workspace/持仓风控/risk_output.json'
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            print(f"⚠️ Risk数据不存在")
            return None
    
    def generate_adjustments(self, tracker_data, risk_data):
        """生成调仓建议"""
        if not tracker_data:
            return []
        
        adjustments = []
        positions = tracker_data.get('positions', [])
        alerts = risk_data.get('alerts', []) if risk_data else []
        
        # 1. 根据风险告警生成调仓建议
        for alert in alerts:
            if alert['level'] == 'critical':
                if alert['type'] in ['single_stock_critical', 'total_loss']:
                    adjustment = {
                        'type': 'sell',
                        'symbol': alert.get('symbol', ''),
                        'name': alert.get('name', ''),
                        'reason': f"严重风险：{alert['reason']}",
                        'action': '止损',
                        'shares': '部分或全部',
                        'priority': 'critical',
                        'time': datetime.now().isoformat()
                    }
                    adjustments.append(adjustment)
            
            elif alert['level'] == 'high':
                if alert['type'] == 'single_stock_loss':
                    adjustment = {
                        'type': 'sell',
                        'symbol': alert.get('symbol', ''),
                        'name': alert.get('name', ''),
                        'reason': f"高位风险：{alert['reason']}",
                        'action': '减仓',
                        'shares': '30-50%',
                        'priority': 'high',
                        'time': datetime.now().isoformat()
                    }
                    adjustments.append(adjustment)
            
            elif alert['level'] == 'medium':
                if alert['type'] == 'single_stock_gain':
                    adjustment = {
                        'type': 'sell',
                        'symbol': alert.get('symbol', ''),
                        'name': alert.get('name', ''),
                        'reason': f"锁定收益：{alert['reason']}",
                        'action': '减仓',
                        'shares': '20-30%',
                        'priority': 'medium',
                        'time': datetime.now().isoformat()
                    }
                    adjustments.append(adjustment)
                
                elif alert['type'] == 'high_position':
                    adjustment = {
                        'type': 'rebalance',
                        'reason': f"降低仓位：{alert['reason']}",
                        'action': '调仓',
                        'target_ratio': 0.7,
                        'priority': 'medium',
                        'time': datetime.now().isoformat()
                    }
                    adjustments.append(adjustment)
        
        # 2. 根据持仓盈利情况生成调仓建议
        for pos in positions:
            if pos['profit_loss_percent'] > 15.0:
                adjustment = {
                    'type': 'sell',
                    'symbol': pos['symbol'],
                    'name': pos['name'],
                    'reason': f"涨幅超过15%（{pos['profit_loss_percent']:.2f}%），建议减仓锁定收益",
                    'action': '减仓',
                    'shares': '20-30%',
                    'priority': 'medium',
                    'time': datetime.now().isoformat()
                }
                adjustments.append(adjustment)
        
        # 3. 根据持仓亏损情况生成调仓建议
        for pos in positions:
            if pos['profit_loss_percent'] < -5.0 and pos['profit_loss_percent'] > -10.0:
                adjustment = {
                    'type': 'hold',
                    'symbol': pos['symbol'],
                    'name': pos['name'],
                    'reason': f"亏损{abs(pos['profit_loss_percent']):.2f}%，建议持有观察",
                    'action': '持有',
                    'notes': '等待反弹或止损信号',
                    'priority': 'low',
                    'time': datetime.now().isoformat()
                }
                adjustments.append(adjustment)
        
        self.adjustments = adjustments
        return adjustments
    
    def get_summary(self):
        """获取调仓汇总"""
        critical_count = sum(1 for a in self.adjustments if a['priority'] == 'critical')
        high_count = sum(1 for a in self.adjustments if a['priority'] == 'high')
        medium_count = sum(1 for a in self.adjustments if a['priority'] == 'medium')
        
        return {
            'agent': self.agent_name,
            'adjustments_count': len(self.adjustments),
            'critical_count': critical_count,
            'high_count': high_count,
            'medium_count': medium_count,
            'summary': f"建议{len(self.adjustments)}次调仓（紧急{critical_count}，重要{high_count}，一般{medium_count}）"
        }

def main():
    print("=== Adjust Agent启动 ===")
    
    agent = AdjustAgent()
    
    print("\n1. 加载Tracker数据...")
    tracker_data = agent.load_tracker_data()
    
    print("\n2. 加载Risk数据...")
    risk_data = agent.load_risk_data()
    
    if tracker_data:
        print("持仓数量：", len(tracker_data.get('positions', [])))
        
        if risk_data:
            print("风险告警：", len(risk_data.get('alerts', [])), "个")
        
        print("\n3. 生成调仓建议...")
        adjustments = agent.generate_adjustments(tracker_data, risk_data)
        
        if adjustments:
            print(f"\n建议{len(adjustments)}次调仓：\n")
            
            # 按优先级排序
            adjustments.sort(key=lambda x: {
                'critical': 0,
                'high': 1,
                'medium': 2,
                'low': 3
            }.get(x['priority'], 99))
            
            for i, adj in enumerate(adjustments, 1):
                priority_icon = "🔴" if adj['priority'] == 'critical' else "🟠" if adj['priority'] == 'high' else "🟡"
                print(f"{i}. {priority_icon} {adj['reason']}")
                
                if 'symbol' in adj:
                    print(f"   股票：{adj['name']} ({adj['symbol']})")
                
                print(f"   操作：{adj['action']}")
                
                if 'shares' in adj:
                    print(f"   比例：{adj['shares']}")
                
                if 'target_ratio' in adj:
                    print(f"   目标仓位：{adj['target_ratio']*100:.0f}%")
                
                if 'notes' in adj:
                    print(f"   备注：{adj['notes']}")
                
                print(f"   时间：{adj['time'][-8:]}")
                print()
        else:
            print("\n✅ 无需调仓")
    else:
        print("⚠️ 没有数据")
    
    print("=== Adjust Agent完成 ===")
    summary = agent.get_summary()
    print(f"汇总：{summary['summary']}")
    
    # 输出到文件
    output_path = '/root/.openclaw/workspace/持仓风控/adjust_output.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'adjustments': agent.adjustments,
            'summary': summary
        }, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 结果已保存到：{output_path}")

if __name__ == '__main__':
    main()
