#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reviewer Agent - 尾盘总结"""

import json
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

class ReviewerAgent:
    def __init__(self):
        self.agent_name = "Reviewer"
        self.role = "尾盘总结"
        self.daily_summary = {}
    
    def load_morning_report(self):
        """加载早盘报告"""
        report_path = '/root/.openclaw/workspace/AnqingA股大师/reports/morning_report.json'
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            return None
    
    def load_intraday_reports(self):
        """加载盘中报告"""
        report_path = '/root/.openclaw/workspace/AnqingA股大师/reports/intraday_report.json'
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            return None
    
    def load_tracker_data(self):
        """加载持仓数据"""
        positions_path = '/root/.openclaw/workspace/AnqingA股大师/positions.json'
        try:
            with open(positions_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            return None
    
    def summarize_day(self):
        """总结一天"""
        morning_report = self.load_morning_report()
        intraday_reports = self.load_intraday_reports()
        tracker_data = self.load_tracker_data()
        
        # 汇总信息
        summary = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'summary': '今日总结完成',
            'morning_stocks': len(morning_report.get('planner', {}).get('select', {}).get('selected_stocks', [])) if morning_report else 0,
            'intraday_alerts': len(intraday_reports.get('monitor', {}).get('alerts', [])) if intraday_reports else 0,
            'final_positions': len(tracker_data) if tracker_data else 0
        }
        
        self.daily_summary = summary
        return summary
    
    def generate_daily_chart(self, tracker_data):
        """生成每日图表"""
        if not tracker_data:
            return None
        
        # 创建图片目录
        Path('/root/.openclaw/workspace/AnqingA股大师/images').mkdir(parents=True, exist_ok=True)
        
        # 创建饼图
        labels = [f"{p['name']}\n{p['profit_loss_percent']:+.1f}%" for p in tracker_data]
        sizes = [p['market_value'] for p in tracker_data]
        colors = []
        
        for p in tracker_data:
            if p['profit_loss_percent'] > 0:
                colors.append('#2ecc71')  # 绿色
            elif p['profit_loss_percent'] < -2:
                colors.append('#e74c3c')  # 红色
            else:
                colors.append('#f39c12')  # 橙色
        
        fig, ax = plt.subplots(figsize=(10, 8))
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 10}
        )
        
        ax.set_title(f"持仓分布（{datetime.now().strftime('%Y-%m-%d')}）", fontsize=16, fontweight='bold', pad=20)
        ax.axis('equal')
        
        output_path = '/root/.openclaw/workspace/AnqingA股大师/images/daily_pie_chart.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return output_path
    
    def get_summary(self):
        """获取汇总"""
        return {
            'agent': self.agent_name,
            'date': self.daily_summary.get('date', ''),
            'summary': self.daily_summary.get('summary', ''),
            'details': self.daily_summary
        }
