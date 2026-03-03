#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""选股工厂 - 主程序（运行所有Agent）"""

import json
import sys
from pathlib import Path
from datetime import datetime

# 添加Agent路径
sys.path.insert(0, '/root/.openclaw/workspace/选股工厂/Agents')

# 导入Agent
from Research.research_agent import ResearchAgent
from Select.select_agent import SelectAgent
from Backtest.backtest_agent import BacktestAgent
from Review.review_agent import ReviewAgent

def run_all_agents():
    """运行所有Agent"""
    print("=== 选股工厂启动 ===\n")
    
    # 1. Research Agent
    print("【1/4】Research Agent启动...")
    research_agent = ResearchAgent()
    research_agent.scan_hot_sectors()
    research_agent.scan_limit_up()
    research_agent.scan_low_volume_rise()
    research_summary = research_agent.get_summary()
    print(f"✅ {research_summary['summary']}\n")
    
    # 2. Select Agent
    print("【2/4】Select Agent启动...")
    select_agent = SelectAgent()
    research_data = select_agent.load_research_data()
    select_agent.select_stocks(research_data)
    select_summary = select_agent.get_summary()
    print(f"✅ {select_summary['summary']}\n")
    
    # 3. Backtest Agent
    print("【3/4】Backtest Agent启动...")
    backtest_agent = BacktestAgent()
    select_data = backtest_agent.load_select_data()
    backtest_agent.run_backtest(select_data)
    backtest_summary = backtest_agent.get_summary()
    print(f"✅ {backtest_summary['summary']}\n")
    
    # 4. Review Agent
    print("【4/4】Review Agent启动...")
    review_agent = ReviewAgent()
    backtest_data = review_agent.load_backtest_data()
    review_agent.review_stocks(backtest_data)
    review_summary = review_agent.get_summary()
    print(f"✅ {review_summary['summary']}\n")
    
    # 汇总报告
    print("=== 选股工厂完成 ===\n")
    print("📊 各Agent结果：")
    print(f"  Research：{research_summary['summary']}")
    print(f"  Select：{select_summary['summary']}")
    print(f"  Backtest：{backtest_summary['summary']}")
    print(f"  Review：{review_summary['summary']}")
    
    print(f"\n🎯 最终推荐：{review_summary['recommended_count']} 只股票")
    if review_summary.get('top_stock'):
        print(f"   最佳股票：{review_summary['top_stock']['name']} ({review_summary['top_stock']['symbol']})")
        print(f"   夏普比率：{review_summary['top_stock']['sharpe_ratio']:.2f}")
        print(f"   年化收益：{review_summary['top_stock']['annual_return']:.1f}%")

def main():
    run_all_agents()

if __name__ == '__main__':
    main()
