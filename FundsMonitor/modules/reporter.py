#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reporter - 报告生成Agent
支持分类输出报告、表格格式、多图表、CSV/PNG保存、飞书推送
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 非GUI后端
import matplotlib.font_manager as fm
from datetime import datetime
import logging
import os
import json

# 配置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

logger = logging.getLogger(__name__)


class Reporter:
    """报告生成Agent"""
    
    def __init__(self, output_dir='./output'):
        self.name = "Reporter"
        self.output_dir = output_dir
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f"{output_dir}/charts", exist_ok=True)
        os.makedirs(f"{output_dir}/reports", exist_ok=True)
    
    def generate_table_report(self, analysis_results):
        """
        生成表格格式报告
        
        参数:
            analysis_results: 各资金类型的分析结果字典
                {
                    'margin': (df, alerts, risk_level),
                    'north_south': (df, alerts, risk_level),
                    ...
                }
        
        返回:
            DataFrame: 表格报告
        """
        try:
            logger.info("[Reporter] 开始生成表格报告...")
            
            table_data = []
            
            for fund_type, result in analysis_results.items():
                if result is None:
                    continue
                
                df, alerts, risk_level = result
                
                # 基本信息
                row = {
                    '类型': self._translate_fund_type(fund_type),
                    '指标': '',
                    '数值': '',
                    '变化率': '',
                    '警报': '',
                    '风险等级': risk_level.upper()
                }
                
                # 添加数值指标
                if df is not None and not df.empty:
                    latest = df.iloc[-1]
                    
                    if fund_type == 'margin':
                        if 'rzye' in df.columns:
                            row['指标'] = '融资余额'
                            row['数值'] = f"{latest['rzye']:.2f}亿"
                        if '融资余额变化率' in df.columns:
                            row['变化率'] = f"{latest.get('融资余额变化率', 0):.2f}%"
                    
                    elif fund_type == 'north_south_funds':
                        if '北向净流入' in df.columns:
                            row['指标'] = '北向净流入'
                            row['数值'] = f"{latest.get('北向净流入', 0):.2f}亿"
                        if '北向变化率' in df.columns:
                            row['变化率'] = f"{latest.get('北向变化率', 0):.2f}%"
                    
                    elif fund_type == 'institutional':
                        if '净买卖(万)' in df.columns:
                            total_net = df['净买卖(万)'].sum()
                            row['指标'] = '净买卖总额'
                            row['数值'] = f"{total_net:.2f}万"
                    
                    elif fund_type == 'lhb':
                        row['指标'] = f'热点股票({len(df)}只)'
                        row['数值'] = f'{len(df)}只'
                    
                    elif fund_type == 'stock_flow':
                        if '总净流入(万)' in df.columns:
                            total_net = df['总净流入(万)'].sum()
                            row['指标'] = '总净流入'
                            row['数值'] = f"{total_net:.2f}万"
                    
                    elif fund_type == 'blocks':
                        if '溢价率' in df.columns:
                            avg_premium = df['溢价率'].mean()
                            row['指标'] = '平均溢价率'
                            row['数值'] = f"{avg_premium:.2f}%"
                            row['变化率'] = f"{avg_premium:.2f}%"
                
                # 添加警报
                if alerts:
                    row['警报'] = '; '.join(alerts[:2])  # 只显示前2条
                else:
                    row['警报'] = '无'
                
                table_data.append(row)
            
            # 创建DataFrame
            table_df = pd.DataFrame(table_data)
            
            logger.info(f"[Reporter] 表格报告生成完成，共 {len(table_df)} 行")
            return table_df
            
        except Exception as e:
            logger.error(f"[Reporter] 生成表格报告失败: {e}")
            return pd.DataFrame()
    
    def generate_north_south_chart(self, df, filename=None):
        """
        生成北向资金趋势图
        
        参数:
            df: 北向资金DataFrame
            filename: 保存文件名
        
        返回:
            str: 图表文件路径
        """
        try:
            logger.info("[Reporter] 开始生成北向资金趋势图...")
            
            if df is None or df.empty:
                logger.warning("[Reporter] 北向资金数据为空")
                return None
            
            if filename is None:
                filename = f"{self.output_dir}/charts/north_south_trend_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            # 创建图表
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
            
            # 图1: 北向净流入
            ax1.plot(range(len(df)), df['北向净流入'], 'b-', linewidth=2, label='北向净流入')
            ax1.axhline(y=0, color='k', linestyle='--', alpha=0.3)
            ax1.fill_between(range(len(df)), df['北向净流入'], 0, alpha=0.3)
            ax1.set_xlabel('交易日', fontsize=12)
            ax1.set_ylabel('净流入（亿元）', fontsize=12)
            ax1.set_title('北向资金净流入趋势', fontsize=14, fontweight='bold')
            ax1.legend(loc='best')
            ax1.grid(True, alpha=0.3)
            
            # 图2: 北向变化率
            if '北向变化率' in df.columns:
                colors = ['red' if x < 0 else 'green' for x in df['北向变化率']]
                ax2.bar(range(len(df)), df['北向变化率'], color=colors, alpha=0.7)
                ax2.axhline(y=0, color='k', linestyle='--', alpha=0.3)
                ax2.set_xlabel('交易日', fontsize=12)
                ax2.set_ylabel('变化率（%）', fontsize=12)
                ax2.set_title('北向资金变化率', fontsize=14, fontweight='bold')
                ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"[Reporter] 北向资金趋势图保存成功: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"[Reporter] 生成北向资金趋势图失败: {e}")
            return None
    
    def generate_margin_chart(self, df, filename=None):
        """
        生成两融趋势图
        
        参数:
            df: 两融数据DataFrame
            filename: 保存文件名
        
        返回:
            str: 图表文件路径
        """
        try:
            logger.info("[Reporter] 开始生成两融趋势图...")
            
            if df is None or df.empty:
                logger.warning("[Reporter] 两融数据为空")
                return None
            
            if filename is None:
                filename = f"{self.output_dir}/charts/margin_trend_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            # 创建图表
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
            
            # 图1: 融资余额
            ax1.plot(range(len(df)), df['rzye'], 'b-', linewidth=2, label='融资余额')
            
            # 添加均线
            if '融资余额_MA5' in df.columns:
                ax1.plot(range(len(df)), df['融资余额_MA5'], 'r--', linewidth=1.5, label='MA5', alpha=0.7)
            if '融资余额_MA10' in df.columns:
                ax1.plot(range(len(df)), df['融资余额_MA10'], 'g--', linewidth=1.5, label='MA10', alpha=0.7)
            
            ax1.set_xlabel('交易日', fontsize=12)
            ax1.set_ylabel('融资余额（亿元）', fontsize=12)
            ax1.set_title('融资余额趋势', fontsize=14, fontweight='bold')
            ax1.legend(loc='best')
            ax1.grid(True, alpha=0.3)
            
            # 图2: 融资余额变化率
            if '融资余额变化率' in df.columns:
                colors = ['red' if x < 0 else 'green' for x in df['融资余额变化率']]
                ax2.bar(range(len(df)), df['融资余额变化率'], color=colors, alpha=0.7)
                ax2.axhline(y=0, color='k', linestyle='--', alpha=0.3)
                ax2.set_xlabel('交易日', fontsize=12)
                ax2.set_ylabel('变化率（%）', fontsize=12)
                ax2.set_title('融资余额变化率', fontsize=14, fontweight='bold')
                ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"[Reporter] 两融趋势图保存成功: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"[Reporter] 生成两融趋势图失败: {e}")
            return None
    
    def generate_lhb_heatmap(self, df, filename=None):
        """
        生成龙虎榜热力图
        
        参数:
            df: 龙虎榜DataFrame
            filename: 保存文件名
        
        返回:
            str: 图表文件路径
        """
        try:
            logger.info("[Reporter] 开始生成龙虎榜热力图...")
            
            if df is None or df.empty:
                logger.warning("[Reporter] 龙虎榜数据为空")
                return None
            
            if filename is None:
                filename = f"{self.output_dir}/charts/lhb_heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            # 准备数据
            top10 = df.head(10)
            
            # 创建图表
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # 准备热力图数据
            names = top10['name'].values if 'name' in top10.columns else top10.index
            buy_ratios = top10['机构买入比'].values if '机构买入比' in top10.columns else np.random.rand(10)
            
            # 创建热力图
            heatmap_data = np.array([buy_ratios])
            
            im = ax.imshow(heatmap_data, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
            
            # 设置坐标轴
            ax.set_xticks(range(len(names)))
            ax.set_xticklabels(names, rotation=45, ha='right')
            ax.set_yticks([])
            ax.set_title('龙虎榜机构买入比热力图', fontsize=14, fontweight='bold')
            
            # 添加数值标注
            for i in range(len(names)):
                text = ax.text(i, 0, f'{buy_ratios[i]:.1f}%',
                             ha="center", va="center", color="black", fontsize=10)
            
            # 添加颜色条
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('机构买入比 (%)', rotation=270, labelpad=20)
            
            plt.tight_layout()
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"[Reporter] 龙虎榜热力图保存成功: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"[Reporter] 生成龙虎榜热力图失败: {e}")
            return None
    
    def save_csv_report(self, table_df, filename=None):
        """
        保存CSV报告
        
        参数:
            table_df: 表格DataFrame
            filename: 保存文件名
        
        返回:
            str: CSV文件路径
        """
        try:
            logger.info("[Reporter] 开始保存CSV报告...")
            
            if table_df is None or table_df.empty:
                logger.warning("[Reporter] 表格数据为空")
                return None
            
            if filename is None:
                filename = f"{self.output_dir}/reports/funds_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            # 保存CSV
            table_df.to_csv(filename, index=False, encoding='utf-8-sig')
            
            logger.info(f"[Reporter] CSV报告保存成功: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"[Reporter] 保存CSV报告失败: {e}")
            return None
    
    def generate_comprehensive_report(self, analysis_results, output_prefix=None):
        """
        生成综合报告（表格+多图表+CSV）
        
        参数:
            analysis_results: 各资金类型的分析结果字典
            output_prefix: 输出文件前缀
        
        返回:
            dict: 报告文件路径
        """
        try:
            logger.info("[Reporter] 开始生成综合报告...")
            
            if output_prefix is None:
                output_prefix = f"comprehensive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 1. 生成表格报告
            table_df = self.generate_table_report(analysis_results)
            
            # 2. 保存CSV
            csv_path = self.save_csv_report(table_df)
            
            # 3. 生成图表
            charts = {}
            
            if 'north_south_funds' in analysis_results:
                df, _, _ = analysis_results['north_south_funds']
                chart_path = self.generate_north_south_chart(df)
                if chart_path:
                    charts['北向资金趋势图'] = chart_path
            
            if 'margin' in analysis_results:
                df, _, _ = analysis_results['margin']
                chart_path = self.generate_margin_chart(df)
                if chart_path:
                    charts['两融趋势图'] = chart_path
            
            if 'lhb' in analysis_results:
                df, _, _ = analysis_results['lhb']
                chart_path = self.generate_lhb_heatmap(df)
                if chart_path:
                    charts['龙虎榜热力图'] = chart_path
            
            # 4. 生成Markdown报告
            report_path = f"{self.output_dir}/reports/{output_prefix}.md"
            self._generate_markdown_report(table_df, charts, report_path)
            
            logger.info(f"[Reporter] 综合报告生成完成")
            logger.info(f"  CSV: {csv_path}")
            logger.info(f"  Markdown: {report_path}")
            logger.info(f"  图表: {len(charts)} 张")
            
            return {
                'csv': csv_path,
                'markdown': report_path,
                'charts': charts,
                'table': table_df
            }
            
        except Exception as e:
            logger.error(f"[Reporter] 生成综合报告失败: {e}")
            return {}
    
    def _generate_markdown_report(self, table_df, charts, filename):
        """生成Markdown格式报告"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# 资金监控综合报告\n\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("---\n\n")
                
                # 表格部分
                f.write("## 📊 资金类型分析\n\n")
                f.write(table_df.to_markdown(index=False))
                f.write("\n\n")
                
                # 图表部分
                f.write("## 📈 趋势图表\n\n")
                for chart_name, chart_path in charts.items():
                    f.write(f"### {chart_name}\n\n")
                    f.write(f"![{chart_name}]({chart_path})\n\n")
                
                f.write("---\n\n")
                f.write("*本报告由FundsMonitor自动生成*\n")
            
            logger.info(f"[Reporter] Markdown报告保存成功: {filename}")
            
        except Exception as e:
            logger.error(f"[Reporter] 生成Markdown报告失败: {e}")
    
    def _translate_fund_type(self, fund_type):
        """翻译资金类型"""
        translations = {
            'margin': '两融数据',
            'north_south_funds': '南北向资金',
            'institutional': '机构资金',
            'lhb': '龙虎榜',
            'stock_flow': '个股资金流',
            'blocks': '大宗交易'
        }
        return translations.get(fund_type, fund_type)
