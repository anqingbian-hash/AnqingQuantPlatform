#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""持仓风控 - 主程序（运行所有Agent）"""

import json
import sys
from pathlib import Path
from datetime import datetime

# 添加Agent路径
sys.path.insert(0, '/root/.openclaw/workspace/持仓风控/Agents')

# 导入Agent
from Tracker.tracker_agent import TrackerAgent
from Risk.risk_agent import RiskAgent
from Adjust.adjust_agent import AdjustAgent
from Report.report_agent import ReportAgent

def run_all_agents():
    """运行所有Agent"""
    print("=== 持仓风控启动 ===\n")
    
    # 1. Tracker Agent
    print("【1/4】Tracker Agent启动...")
    tracker_agent = TrackerAgent()
    tracker_agent.load_positions()
    tracker_agent.refresh_prices()
    tracker_summary = tracker_agent.get_summary()
    print(f"✅ {tracker_summary['summary']}\n")
    
    # 2. Risk Agent
    print("【2/4】Risk Agent启动...")
    risk_agent = RiskAgent()
    tracker_data = risk_agent.load_tracker_data()
    risk_agent.check_risks(tracker_data)
    risk_summary = risk_agent.get_summary()
    print(f"✅ {risk_summary['summary']}\n")
    
    # 3. Adjust Agent
    print("【3/4】Adjust Agent启动...")
    adjust_agent = AdjustAgent()
    tracker_data = adjust_agent.load_tracker_data()
    risk_data = adjust_agent.load_risk_data()
    adjust_agent.generate_adjustments(tracker_data, risk_data)
    adjust_summary = adjust_agent.get_summary()
    print(f"✅ {adjust_summary['summary']}\n")
    
    # 4. Report Agent
    print("【4/4】Report Agent启动...")
    report_agent = ReportAgent()
    report = report_agent.generate_report()
    report_summary = report_agent.get_summary()
    print(f"✅ {report_summary['summary']}\n")
    
    # 汇总报告
    print("=== 持仓风控完成 ===\n")
    print("📊 各Agent结果：")
    print(f"  Tracker：{tracker_summary['summary']}")
    print(f"  Risk：{risk_summary['summary']}")
    print(f"  Adjust：{adjust_summary['summary']}")
    print(f"  Report：{report_summary['summary']}")
    
    print(f"\n📅 报告日期：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 风险等级：{risk_agent.risk_level.upper()}")
    
    if report and report.get('charts'):
        print(f"\n📈 图表生成：")
        if report['charts'].get('pie_chart'):
            print(f"   ✅ 持仓饼图：{report['charts']['pie_chart']}")
        if report['charts'].get('profit_curve'):
            print(f"   ✅ 收益曲线：{report['charts']['profit_curve']}")

def main():
    run_all_agents()

if __name__ == '__main__':
    main()
