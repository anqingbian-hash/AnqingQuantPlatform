#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Anqing A股大师 - 主程序（终极AI交易助理）"""

import json
import sys
from pathlib import Path
from datetime import datetime

# 添加Agent路径
sys.path.insert(0, '/root/.openclaw/workspace/AnqingA股大师/Agents')

# 导入Agent
from Planner.planner_agent import PlannerAgent
from Monitor.monitor_agent import MonitorAgent
from Tracker.tracker_agent import TrackerAgent
from Reviewer.reviewer_agent import ReviewerAgent

class AnqingMaster:
    def __init__(self):
        self.name = "Anqing A股大师"
        self.version = "1.0.0"
        self.user_id = "ou_4ea9ab25e2205ba44aadece04ba60ddd"
        self.planner = PlannerAgent()
        self.monitor = MonitorAgent()
        self.tracker = TrackerAgent()
        self.reviewer = ReviewerAgent()
    
    def run_morning_workflow(self):
        """早盘流程：选股 + 回测"""
        print("\n" + "="*60)
        print("【早盘流程】选股 + 回测")
        print("="*60 + "\n")
        
        # 1. Planner：选股 + 回测
        print("【1/3】Planner启动...")
        research_summary = self.planner.scan_hot_sectors()
        select_summary = self.planner.select_stocks()
        backtest_summary = self.planner.run_backtest()
        
        print(f"\n✅ {research_summary['summary']}")
        print(f"✅ {select_summary['summary']}")
        print(f"✅ {backtest_summary['summary']}\n")
        
        # 2. 初始化Tracker
        print("【2/3】Tracker初始化...")
        self.tracker.load_positions()
        tracker_summary = self.tracker.get_summary()
        print(f"✅ {tracker_summary['summary']}\n")
        
        # 3. 生成早盘报告
        print("【3/3】生成早盘报告...")
        morning_report = {
            'report_type': 'morning',
            'report_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'planner': {
                'research': research_summary,
                'select': select_summary,
                'backtest': backtest_summary
            },
            'tracker': tracker_summary
        }
        
        # 保存报告
        report_path = '/root/.openclaw/workspace/AnqingA股大师/reports/morning_report.json'
        Path('/root/.openclaw/workspace/AnqingA股大师/reports').mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(morning_report, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 早盘报告已生成：{report_path}")
        
        return morning_report
    
    def run_intraday_workflow(self):
        """盘中流程：盯盘 + 持仓"""
        print("\n" + "="*60)
        print("【盘中流程】盯盘 + 持仓")
        print("="*60 + "\n")
        
        # 1. Monitor：盯盘
        print("【1/2】Monitor启动...")
        monitor_alerts = self.monitor.check_alerts()
        
        if monitor_alerts:
            print(f"\n发现{len(monitor_alerts)}个异动：")
            for alert in monitor_alerts:
                print(f"  {alert['name']} ({alert['symbol']}) - {alert['reason']}")
        else:
            print("\n✅ 无异动")
        
        # 2. Tracker：持仓
        print("\n【2/2】Tracker刷新...")
        self.tracker.refresh_prices()
        tracker_summary = self.tracker.get_summary()
        print(f"✅ {tracker_summary['summary']}\n")
        
        # 生成盘中报告
        intraday_report = {
            'report_type': 'intraday',
            'report_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'monitor': {
                'alerts_count': len(monitor_alerts),
                'alerts': monitor_alerts
            },
            'tracker': tracker_summary
        }
        
        # 保存报告
        report_path = '/root/.openclaw/workspace/AnqingA股大师/reports/intraday_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(intraday_report, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 盘中报告已保存：{report_path}")
        
        return intraday_report
    
    def run_close_workflow(self):
        """尾盘流程：总结 + 日报"""
        print("\n" + "="*60)
        print("【尾盘流程】总结 + 日报")
        print("="*60 + "\n")
        
        # 1. Reviewer：总结
        print("【1/3】Reviewer启动...")
        review_summary = self.reviewer.summarize_day()
        print(f"✅ {review_summary['summary']}\n")
        
        # 2. 最终持仓
        print("【2/3】最终持仓...")
        self.tracker.refresh_prices()
        final_positions = self.tracker.positions
        tracker_summary = self.tracker.get_summary()
        print(f"✅ {tracker_summary['summary']}\n")
        
        # 3. 生成日报
        print("【3/3】生成日报...")
        daily_report = {
            'report_type': 'daily',
            'report_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'reviewer': review_summary,
            'final_positions': final_positions,
            'tracker': tracker_summary
        }
        
        # 保存报告
        report_path = '/root/.openclaw/workspace/AnqingA股大师/reports/daily_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(daily_report, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 日报已生成：{report_path}")
        
        return daily_report
    
    def get_summary(self):
        """获取大师汇总"""
        return {
            'name': self.name,
            'version': self.version,
            'user_id': self.user_id,
            'agents': ['Planner', 'Monitor', 'Tracker', 'Reviewer'],
            'workflow': [
                '早盘：选股 + 回测（9:00）',
                '盘中：盯盘 + 持仓（每5分钟）',
                '尾盘：总结 + 日报（15:30）'
            ]
        }

def main():
    print("="*60)
    print(f"{ 'Anqing A股大师'.center(40) }")
    print(f"终极AI交易助理 v1.0.0")
    print("="*60)
    
    master = AnqingMaster()
    summary = master.get_summary()
    
    print(f"\n{summary['name']} v{summary['version']}")
    print(f"用户ID：{summary['user_id']}")
    print(f"Agent团队：{', '.join(summary['agents'])}")
    
    print("\n工作流程：")
    for workflow in summary['workflow']:
        print(f"  • {workflow}")
    
    print("\n选择模式：")
    print("  1. 早盘流程（选股 + 回测）")
    print("  2. 盘中流程（盯盘 + 持仓）")
    print("  3. 尾盘流程（总结 + 日报）")
    print("  4. 完整流程（早盘 → 盘中 → 尾盘）")
    
    # 默认运行早盘流程
    print("\n正在运行早盘流程...")
    morning_report = master.run_morning_workflow()
    
    print("\n" + "="*60)
    print("Anqing A股大师 - 早盘流程完成")
    print("="*60)
    
    print("\n📊 早盘报告摘要：")
    planner = morning_report['planner']
    tracker = morning_report['tracker']
    
    print(f"  Research：{planner['research']['summary']}")
    print(f"  Select：{planner['select']['summary']}")
    print(f"  Backtest：{planner['backtest']['summary']}")
    print(f"  Tracker：{tracker['summary']}")

if __name__ == '__main__':
    main()
