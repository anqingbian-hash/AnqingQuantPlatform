#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Risk Agent - 风控预警"""

import json
import sys
from pathlib import Path
from datetime import datetime

# 添加akshare路径
sys.path.insert(0, '/root/.openclaw/skills')

# Risk Agent
class RiskAgent:
    def __init__(self):
        self.agent_name = "Risk"
        self.role = "风控预警"
        self.alerts = []
        self.risk_level = "low"
    
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
    
    def check_risks(self, tracker_data):
        """检查风险"""
        if not tracker_data:
            return []
        
        alerts = []
        positions = tracker_data.get('positions', [])
        summary = tracker_data.get('summary', {})
        
        # 1. 单股跌幅>4%预警
        for pos in positions:
            if pos['profit_loss_percent'] < -4.0:
                alert = {
                    'type': 'single_stock_loss',
                    'level': 'high',
                    'symbol': pos['symbol'],
                    'name': pos['name'],
                    'reason': f"单股跌幅{pos['profit_loss_percent']:.2f}%超过阈值4%",
                    'value': pos['profit_loss_percent'],
                    'threshold': -4.0,
                    'time': datetime.now().isoformat()
                }
                alerts.append(alert)
        
        # 2. 单股跌幅>8%严重预警
        for pos in positions:
            if pos['profit_loss_percent'] < -8.0:
                alert = {
                    'type': 'single_stock_critical',
                    'level': 'critical',
                    'symbol': pos['symbol'],
                    'name': pos['name'],
                    'reason': f"单股跌幅{pos['profit_loss_percent']:.2f}%严重预警！",
                    'value': pos['profit_loss_percent'],
                    'threshold': -8.0,
                    'time': datetime.now().isoformat()
                }
                alerts.append(alert)
        
        # 3. 单股涨幅>10%建议减仓
        for pos in positions:
            if pos['profit_loss_percent'] > 10.0:
                alert = {
                    'type': 'single_stock_gain',
                    'level': 'medium',
                    'symbol': pos['symbol'],
                    'name': pos['name'],
                    'reason': f"单股涨幅{pos['profit_loss_percent']:.2f}%，建议减仓锁定收益",
                    'value': pos['profit_loss_percent'],
                    'threshold': 10.0,
                    'time': datetime.now().isoformat()
                }
                alerts.append(alert)
        
        # 4. 总仓位>80%提醒
        total_market_value = summary.get('total_market_value', 0)
        total_capital = 2000000.0  # 初始资金200万
        position_ratio = total_market_value / total_capital if total_capital > 0 else 0
        
        if position_ratio > 0.8:
            alert = {
                'type': 'high_position',
                'level': 'medium',
                'reason': f"总仓位{position_ratio*100:.1f}%超过80%，建议降低仓位",
                'value': position_ratio,
                'threshold': 0.8,
                'time': datetime.now().isoformat()
            }
            alerts.append(alert)
        
        # 5. 总仓位>90%严重提醒
        if position_ratio > 0.9:
            alert = {
                'type': 'critical_position',
                'level': 'critical',
                'reason': f"总仓位{position_ratio*100:.1f}%严重预警！",
                'value': position_ratio,
                'threshold': 0.9,
                'time': datetime.now().isoformat()
            }
            alerts.append(alert)
        
        # 6. 总亏损>10%严重预警
        total_profit_loss = summary.get('total_profit_loss', 0)
        total_capital = 2000000.0
        total_loss_ratio = total_profit_loss / total_capital if total_capital > 0 else 0
        
        if total_loss_ratio < -0.1:
            alert = {
                'type': 'total_loss',
                'level': 'critical',
                'reason': f"总亏损{abs(total_loss_ratio)*100:.1f}%严重预警！",
                'value': total_loss_ratio,
                'threshold': -0.1,
                'time': datetime.now().isoformat()
            }
            alerts.append(alert)
        
        self.alerts = alerts
        
        # 确定风险等级
        if any(a['level'] == 'critical' for a in alerts):
            self.risk_level = "critical"
        elif any(a['level'] == 'high' for a in alerts):
            self.risk_level = "high"
        elif any(a['level'] == 'medium' for a in alerts):
            self.risk_level = "medium"
        else:
            self.risk_level = "low"
        
        return alerts
    
    def get_summary(self):
        """获取风控汇总"""
        return {
            'agent': self.agent_name,
            'alerts_count': len(self.alerts),
            'risk_level': self.risk_level,
            'summary': f"发现{len(self.alerts)}个风险，风险等级：{self.risk_level.upper()}"
        }

def main():
    print("=== Risk Agent启动 ===")
    
    agent = RiskAgent()
    
    print("\n1. 加载Tracker数据...")
    tracker_data = agent.load_tracker_data()
    
    if tracker_data:
        print("持仓数量：", len(tracker_data.get('positions', [])))
        print("总市值：", tracker_data.get('summary', {}).get('total_market_value', 0)/10000, "万")
        
        print("\n2. 检查风险...")
        alerts = agent.check_risks(tracker_data)
        
        if alerts:
            print(f"\n发现{len(alerts)}个风险：\n")
            for i, alert in enumerate(alerts, 1):
                level_icon = "🔴" if alert['level'] == 'critical' else "🟠" if alert['level'] == 'high' else "🟡"
                print(f"{i}. {level_icon} {alert['reason']}")
                if 'symbol' in alert:
                    print(f"   股票：{alert['name']} ({alert['symbol']})")
                print(f"   数值：{alert['value']:.2f}")
                print(f"   阈值：{alert['threshold']:.2f}")
                print(f"   时间：{alert['time'][-8:]}")
                print()
        else:
            print("\n✅ 未发现风险")
    else:
        print("⚠️ 没有数据")
    
    print("=== Risk Agent完成 ===")
    summary = agent.get_summary()
    print(f"汇总：{summary['summary']}")
    
    # 输出到文件
    output_path = '/root/.openclaw/workspace/持仓风控/risk_output.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'alerts': agent.alerts,
            'risk_level': agent.risk_level,
            'summary': summary
        }, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 结果已保存到：{output_path}")

if __name__ == '__main__':
    main()
