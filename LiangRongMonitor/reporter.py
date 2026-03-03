#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
两融报告生成与推送 - 卞董专用版本
收到Analyzer输出后，生成报告、图表、推送通知
"""
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import pandas as pd
from datetime import datetime
import os

class Reporter:
    """报告生成Agent"""
    
    def __init__(self):
        self.name = "Reporter"
        self.charts_dir = 'charts'
        self.output_dir = 'output'
        self.data_dir = 'data'
        
        # 确保目录存在
        os.makedirs(self.charts_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
    
    def save_dataframe(self, df, filename='margin_market.csv'):
        """保存分析后的DataFrame"""
        try:
            filepath = os.path.join(self.data_dir, filename)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"✓ 数据已保存: {filepath}")
            return True
        except Exception as e:
            print(f"✗ 数据保存失败: {e}")
            return False
    
    def generate_trend_chart(self, df, filename='margin_trend.png'):
        """生成融资余额趋势图 + MA5"""
        try:
            print(f"\n【生成趋势图】...")
            
            # 按日期排序
            df = df.sort_values('trade_date')
            
            # 创建图表
            fig, ax = plt.subplots(figsize=(14, 8))
            
            # 绘制融资余额
            ax.plot(range(len(df)), df['rzye'], 
                   label='融资余额', color='#2E86AB', linewidth=2.5, marker='o', markersize=4)
            
            # 绘制MA5（如果存在）
            if '融资余额_MA5' in df.columns:
                ax.plot(range(len(df)), df['融资余额_MA5'],
                       label='MA5', color='#F25F5C', linewidth=1.8, linestyle='--')
            
            # 标题和标签
            ax.set_title('两融余额趋势图', fontsize=20, fontweight='bold', pad=20)
            ax.set_ylabel('融资余额（亿元）', fontsize=14, fontweight='bold')
            ax.set_xlabel('交易日', fontsize=12)
            
            # 网格和图例
            ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
            ax.legend(loc='best', fontsize=12, framealpha=0.9)
            
            # 标记最新点
            latest_idx = len(df) - 1
            ax.scatter([latest_idx], [df['rzye'].iloc[latest_idx]], 
                      color='#FF0000', s=200, marker='*', zorder=5)
            ax.annotate(f'最新: {df["rzye"].iloc[latest_idx]/1e8:.2f}亿元',
                       xy=(latest_idx, df['rzye'].iloc[latest_idx]),
                       xytext=(latest_idx-0.5, df['rzye'].iloc[latest_idx]*1.05),
                       fontsize=11, fontweight='bold',
                       arrowprops=dict(arrowstyle='->', color='red', lw=1.5))
            
            # 紧凑布局
            plt.tight_layout()
            
            # 保存图表
            filepath = os.path.join(self.charts_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✓ 趋势图已保存: {filepath}")
            return True
            
        except Exception as e:
            print(f"✗ 趋势图生成失败: {e}")
            return False
    
    def generate_report_text(self, df, source, alerts, filename='margin_report.txt'):
        """生成报告文本"""
        try:
            print(f"\n【生成报告文本】...")
            
            # 获取最新数据
            latest = df.iloc[-1]
            
            # 提取变化率
            change_rate = latest.get('融资余额变化率', 0)
            if pd.notna(change_rate):
                change_str = f"{change_rate:.2f}%"
                trend = "上涨" if change_rate > 0 else "下跌"
            else:
                change_str = "N/A"
                trend = "N/A"
            
            # 格式化警报
            if alerts:
                alerts_str = "\n".join([f"  - {alert}" for alert in alerts])
            else:
                alerts_str = "  无警报，市场状态正常"
            
            # 生成报告
            report = f"""{'='*80}
两融监控日报
{'='*80}

【基本信息】
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
数据来源: {source}
数据日期: {latest.get('trade_date', 'N/A')}

{'='*80}

【核心指标】
融资余额: {latest['rzye']/1e8:.2f} 亿元
变化率: {change_str}
趋势: {trend}

{'='*80}

【详细指标】"""
            
            # 添加其他指标
            if '融资余额_MA5' in df.columns and pd.notna(latest['融资余额_MA5']):
                report += f"\n融资余额MA5: {latest['融资余额_MA5']/1e8:.2f} 亿元"
            
            if '融券余额变化率' in df.columns and pd.notna(latest['融券余额变化率']):
                report += f"\n融券余额变化率: {latest['融券余额变化率']:.2f}%"
            
            if 'rzmre' in df.columns:
                report += f"\n融资买入额: {latest['rzmre']/1e8:.2f} 亿元"
            
            if 'rqyl' in df.columns:
                report += f"\n融券卖出额: {latest['rqyl']:.2f} 万元"
            
            report += f"\n{'='*80}\n"
            
            # 添加警报
            report += "【风险警报】\n"
            report += alerts_str
            report += f"\n{'='*80}\n"
            
            # 添加总结
            report += "【投资建议】\n"
            if change_rate > 5:
                report += "  - 融资激增，市场情绪高涨，但杠杆风险放大\n"
                report += "  - 建议谨慎追高，注意控制仓位\n"
            elif change_rate < -5:
                report += "  - 融资骤降，市场情绪降温，可能回调\n"
                report += "  - 建议观望为主，等待企稳信号\n"
            else:
                report += "  - 融资余额平稳，市场情绪正常\n"
                report += "  - 建议维持当前策略\n"
            
            report += f"\n{'='*80}\n"
            report += "【报告结束】\n"
            report += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            report += f"{'='*80}\n"
            
            # 保存报告
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"✓ 报告已保存: {filepath}")
            return report, True
            
        except Exception as e:
            print(f"✗ 报告生成失败: {e}")
            return None, False
    
    def send_notification(self, report, chart_path):
        """推送报告 + 图表到飞书/Telegram/微信"""
        try:
            print(f"\n【推送通知】...")
            
            # TODO: 实现具体的推送功能
            # 目前只打印信息
            
            print(f"通知内容（飞书推送）:")
            print(f"  {report[:200]}...")  # 只打印前200字符
            
            print(f"\n图表路径: {chart_path}")
            print(f"  图表大小: {os.path.getsize(chart_path)/1024:.1f} KB")
            
            # 模拟推送成功
            print(f"✓ 推送已发送（模拟）")
            return True
            
        except Exception as e:
            print(f"✗ 推送失败: {e}")
            return False
    
    def generate_full_report(self, df, source, alerts):
        """生成完整报告（数据+图表+文本）"""
        print("\n" + "="*80)
        print("Reporter - 开始生成完整报告")
        print("="*80)
        
        success = True
        
        # 1. 保存数据
        print("\n【步骤1】保存分析数据")
        if not self.save_dataframe(df):
            success = False
        
        # 2. 生成图表
        print("\n【步骤2】生成趋势图表")
        chart_path = os.path.join(self.charts_dir, 'margin_trend.png')
        if not self.generate_trend_chart(df, 'margin_trend.png'):
            success = False
        
        # 3. 生成报告文本
        print("\n【步骤3】生成报告文本")
        report, _ = self.generate_report_text(df, source, alerts, 'margin_report.txt')
        
        # 4. 推送通知
        print("\n【步骤4】推送通知")
        if report and os.path.exists(chart_path):
            self.send_notification(report, chart_path)
        
        print("\n" + "="*80)
        if success:
            print("✓ 报告生成完成")
        else:
            print("✗ 报告生成失败")
        print("="*80)
        
        return success

# ========================================
# 测试代码
# ========================================
if __name__ == '__main__':
    print("="*80)
    print("两融报告生成与推送 - 卞董专用版本")
    print("="*80)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 导入数据和警报
    import sys
    sys.path.append('/root/.openclaw/workspace/LiangRongMonitor')
    
    # 模拟数据（实际应该从Analyzer获取）
    from fetch_margin_fixed import fetch_margin_data
    
    print("\n【步骤0】获取数据")
    df, source = fetch_margin_data(date='20260302')
    
    if df is None or df.empty:
        print("✗ 数据获取失败，测试终止")
        sys.exit(1)
    
    # 模拟警报（实际应该从Analyzer获取）
    alerts = [
        "⚠️ 融券骤降 -52.67%：做空平仓，可能反弹"
    ]
    
    # 创建Reporter
    reporter = Reporter()
    
    # 生成完整报告
    success = reporter.generate_full_report(df, source, alerts)
    
    if success:
        print("\n✓ 测试成功!")
        print(f"\n输出文件:")
        print(f"  1. 数据文件: data/margin_market.csv")
        print(f"  2. 趋势图表: charts/margin_trend.png")
        print(f"  3. 报告文本: output/margin_report.txt")
        
        # 显示报告摘要
        with open('output/margin_report.txt', 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"\n{content[:500]}...")
    else:
        print("\n✗ 测试失败!")
    
    print("\n" + "="*80)
    print("测试完成")
    print("="*80)
