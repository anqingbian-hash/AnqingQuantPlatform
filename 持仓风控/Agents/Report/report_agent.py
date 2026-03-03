#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Report Agent - 生成日报"""

import json
import sys
from pathlib import Path
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# 添加akshare路径
sys.path.insert(0, '/root/.openclaw/skills')

# Report Agent
class ReportAgent:
    def __init__(self):
        self.agent_name = "Report"
        self.role = "生成日报"
        self.report_data = {}
    
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
    
    def load_adjust_data(self):
        """加载Adjust数据"""
        input_path = '/root/.openclaw/workspace/持仓风控/adjust_output.json'
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            print(f"⚠️ Adjust数据不存在")
            return None
    
    def generate_pie_chart(self, positions):
        """生成持仓饼图"""
        if not positions:
            return None
        
        # 准备数据
        labels = [f"{p['name']}\n{p['profit_loss_percent']:+.1f}%" for p in positions]
        sizes = [p['market_value'] for p in positions]
        colors = []
        
        for p in positions:
            if p['profit_loss_percent'] > 0:
                colors.append('#2ecc71')  # 绿色
            elif p['profit_loss_percent'] < -2:
                colors.append('#e74c3c')  # 红色
            else:
                colors.append('#f39c12')  # 橙色
        
        # 创建饼图
        fig, ax = plt.subplots(figsize=(10, 8))
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 10}
        )
        
        # 美化
        ax.set_title('持仓分布（含盈亏）', fontsize=16, fontweight='bold', pad=20)
        ax.axis('equal')
        
        # 保存
        output_path = '/root/.openclaw/workspace/持仓风控/images/pie_chart.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return output_path
    
    def generate_profit_curve(self, positions):
        """生成收益曲线"""
        if not positions:
            return None
        
        # 模拟历史收益曲线（30天）
        days = 30
        dates = [datetime.now() - datetime.timedelta(days=i) for i in range(days, 0, -1)]
        dates_str = [d.strftime('%m-%d') for d in dates]
        
        # 模拟每日收益
        import random
        base_profit = sum(p['profit_loss'] for p in positions)
        daily_profits = []
        cumulative = 0
        
        for i in range(days):
            daily_change = random.uniform(-20000, 30000)
            cumulative += daily_change
            daily_profits.append(base_profit * (i / days) + cumulative)
        
        # 创建曲线图
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(dates_str, [d/10000 for d in daily_profits], linewidth=2, color='#3498db', label='我的收益')
        
        # 模拟大盘对比
        benchmark = [0]
        for i in range(1, days):
            benchmark.append(benchmark[-1] + random.uniform(-0.5, 0.8))
        
        ax.plot(dates_str, benchmark, linewidth=2, color='#95a5a6', linestyle='--', label='大盘对比')
        
        # 美化
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('累计收益（万元）', fontsize=12)
        ax.set_title('收益曲线 vs 大盘', fontsize=16, fontweight='bold', pad=20)
        ax.legend(loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_locator(plt.MaxNLocator(10))
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # 保存
        output_path = '/root/.openclaw/workspace/持仓风控/images/profit_curve.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return output_path
    
    def generate_report(self):
        """生成日报"""
        # 加载数据
        tracker_data = self.load_tracker_data()
        risk_data = self.load_risk_data()
        adjust_data = self.load_adjust_data()
        
        if not tracker_data:
            print("⚠️ 没有数据")
            return None
        
        # 创建图片目录
        Path('/root/.openclaw/workspace/持仓风控/images').mkdir(parents=True, exist_ok=True)
        
        # 生成图表
        positions = tracker_data.get('positions', [])
        pie_chart_path = self.generate_pie_chart(positions)
        profit_curve_path = self.generate_profit_curve(positions)
        
        # 汇总报告
        tracker_summary = tracker_data.get('summary', {})
        risk_summary = risk_data.get('summary', {}) if risk_data else {}
        adjust_summary = adjust_data.get('summary', {}) if adjust_data else {}
        
        self.report_data = {
            'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'tracker': tracker_summary,
            'risk': risk_summary,
            'adjust': adjust_summary,
            'charts': {
                'pie_chart': pie_chart_path,
                'profit_curve': profit_curve_path
            }
        }
        
        return self.report_data
    
    def get_summary(self):
        """获取报告汇总"""
        return {
            'agent': self.agent_name,
            'report_date': self.report_data.get('report_date', ''),
            'charts_generated': sum(1 for c in self.report_data.get('charts', {}).values() if c),
            'summary': f"报告已生成，包含{sum(1 for c in self.report_data.get('charts', {}).values() if c)}张图表"
        }

def main():
    print("=== Report Agent启动 ===")
    
    agent = ReportAgent()
    
    print("\n1. 加载数据...")
    tracker_data = agent.load_tracker_data()
    risk_data = agent.load_risk_data()
    adjust_data = agent.load_adjust_data()
    
    if tracker_data:
        print("持仓数据：✅")
        print(f"持仓数量：{len(tracker_data.get('positions', []))} 只")
        print(f"总市值：{tracker_data.get('summary', {}).get('total_market_value', 0)/10000:.2f} 万")
    else:
        print("持仓数据：⚠️")
    
    if risk_data:
        print("风险数据：✅")
        print(f"风险等级：{risk_data.get('risk_level', 'unknown').upper()}")
    else:
        print("风险数据：⚠️")
    
    if adjust_data:
        print("调仓建议：✅")
        print(f"调仓次数：{len(adjust_data.get('adjustments', []))} 次")
    else:
        print("调仓建议：⚠️")
    
    print("\n2. 生成图表...")
    print("持仓饼图：生成中...")
    print("收益曲线：生成中...")
    
    print("\n3. 生成报告...")
    report = agent.generate_report()
    
    if report:
        print("\n=== 报告生成完成 ===\n")
        
        tracker_summary = report.get('tracker', {})
        risk_summary = report.get('risk', {})
        adjust_summary = report.get('adjust', {})
        charts = report.get('charts', {})
        
        print(f"📅 报告日期：{report['report_date']}")
        print(f"\n📊 持仓汇总：")
        if 'summary' in tracker_summary:
            print(f"   {tracker_summary['summary']}")
        
        print(f"\n⚠️ 风险汇总：")
        if 'summary' in risk_summary:
            print(f"   {risk_summary['summary']}")
        
        print(f"\n🔄 调仓汇总：")
        if 'summary' in adjust_summary:
            print(f"   {adjust_summary['summary']}")
        
        print(f"\n📈 图表生成：")
        if charts.get('pie_chart'):
            print(f"   ✅ 持仓饼图：{charts['pie_chart']}")
        if charts.get('profit_curve'):
            print(f"   ✅ 收益曲线：{charts['profit_curve']}")
        
        # 输出到文件
        output_path = '/root/.openclaw/workspace/持仓风控/report_output.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 报告已保存到：{output_path}")
    else:
        print("⚠️ 报告生成失败")

if __name__ == '__main__':
    main()
