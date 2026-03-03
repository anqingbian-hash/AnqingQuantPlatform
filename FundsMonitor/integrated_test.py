#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试脚本 - 整合FundsMonitor到主平台和LiangRongMonitor
"""
import logging
from datetime import datetime
import sys
import os

# 添加路径
sys.path.append('/root/.openclaw/workspace/FundsMonitor')
sys.path.append('/root/.openclaw/workspace/LiangRongMonitor')
sys.path.append('/root/.openclaw/workspace/unified-quot-platform')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntegratedFundsMonitor:
    """集成资金监控系统"""
    
    def __init__(self):
        self.name = "IntegratedFundsMonitor"
        
        # 潜力股阈值
        self.potential_thresholds = {
            'north_net_inflow': 30.0,       # 北向净流入>30亿
            'margin_growth': 5.0,             # 两融增长>5%
            'lhb_count': 3,                   # 龙虎榜>3只
        }
        
        # 风控减仓阈值
        self.risk_thresholds = {
            'north_outflow': -50.0,           # 北向净流出<-50亿
            'margin_decline': -5.0,           # 两融下跌<-5%
            'retail_outflow': -10000.0,       # 散户净流出<-1亿
        }
        
        # 加载模块
        self.load_modules()
    
    def load_modules(self):
        """加载必要模块"""
        try:
            # 加载FundsMonitor模块
            from modules.analyzer_v6 import Analyzer
            from modules.reporter import Reporter
            
            self.analyzer = Analyzer()
            self.reporter = Reporter(output_dir='./output')
            
            logger.info("[集成] FundsMonitor模块加载成功")
            return True
            
        except Exception as e:
            logger.error(f"[集成] 模块加载失败: {e}")
            return False
    
    def check_potential_stocks(self, analysis_results):
        """
        检查潜力股（北向净流入+两融增长>阈值）
        
        参数:
            analysis_results: 分析结果
        
        返回:
            list: 潜力股列表
        """
        try:
            potential_stocks = []
            
            # 1. 检查北向资金
            if 'north_south_funds' in analysis_results:
                df, alerts, risk_level = analysis_results['north_south_funds']
                
                if df is not None and not df.empty and '北向净流入' in df.columns:
                    latest_north = df['北向净流入'].iloc[-1]
                    
                    if pd.notna(latest_north) and latest_north > self.potential_thresholds['north_net_inflow']:
                        potential_stocks.append({
                            'type': '北向资金',
                            'code': '市场',
                            'reason': f'北向净流入{latest_north:.2f}亿，超出阈值{self.potential_thresholds["north_net_inflow"]}亿',
                            'action': '关注'
                        })
                        logger.info(f"✅ 北向资金净流入{latest_north:.2f}亿，市场潜力大")
            
            # 2. 检查两融增长
            if 'margin' in analysis_results:
                df, alerts, risk_level = analysis_results['margin']
                
                if df is not None and not df.empty and '融资余额变化率' in df.columns:
                    latest_margin_change = df['融资余额变化率'].iloc[-1]
                    
                    if pd.notna(latest_margin_change) and latest_margin_change > self.potential_thresholds['margin_growth']:
                        potential_stocks.append({
                            'type': '两融数据',
                            'code': '市场',
                            'reason': f'两融余额增长{latest_margin_change:.2f}%，超出阈值{self.potential_thresholds["margin_growth"]}%',
                            'action': '关注'
                        })
                        logger.info(f"✅ 两融余额增长{latest_margin_change:.2f}%，杠杆资金活跃")
            
            # 3. 检查龙虎榜热点
            if 'lhb' in analysis_results:
                df, alerts, risk_level = analysis_results['lhb']
                
                if df is not None and len(df) > self.potential_thresholds['lhb_count']:
                    top3 = df.head(3)
                    
                    for idx, row in top3.iterrows():
                        name = row.get('name', '未知')
                        buy_ratio = row.get('机构买入比', 0)
                        
                        if pd.notna(buy_ratio) and buy_ratio > 0.6:
                            potential_stocks.append({
                                'type': '龙虎榜',
                                'code': name,
                                'reason': f'机构买入比{buy_ratio:.1%}，>60%高控盘',
                                'action': '关注'
                            })
                            logger.info(f"✅ {name} 机构买入比{buy_ratio:.1%}，潜力股")
            
            return potential_stocks
            
        except Exception as e:
            logger.error(f"[集成] 检查潜力股失败: {e}")
            return []
    
    def check_risk_reduction(self, analysis_results):
        """
        检查风控减仓（资金流出触发）
        
        参数:
            analysis_results: 分析结果
        
        返回:
            list: 风控减仓列表
        """
        try:
            risk_actions = []
            
            # 1. 检查北向净流出
            if 'north_south_funds' in analysis_results:
                df, alerts, risk_level = analysis_results['north_south_funds']
                
                if df is not None and not df.empty and '北向净流入' in df.columns:
                    latest_north = df['北向净流入'].iloc[-1]
                    
                    if pd.notna(latest_north) and latest_north < self.risk_thresholds['north_outflow']:
                        risk_actions.append({
                            'type': '北向资金',
                            'code': '市场',
                            'reason': f'北向净流出{abs(latest_north):.2f}亿，低于阈值{abs(self.risk_thresholds["north_outflow"])}亿',
                            'action': '减仓'
                        })
                        logger.warning(f"⚠️ 北向资金净流出{abs(latest_north):.2f}亿，建议减仓")
            
            # 2. 检查两融下跌
            if 'margin' in analysis_results:
                df, alerts, risk_level = analysis_results['margin']
                
                if df is not None and not df.empty and '融资余额变化率' in df.columns:
                    latest_margin_change = df['融资余额变化率'].iloc[-1]
                    
                    if pd.notna(latest_margin_change) and latest_margin_change < self.risk_thresholds['margin_decline']:
                        risk_actions.append({
                            'type': '两融数据',
                            'code': '市场',
                            'reason': f'两融余额下跌{abs(latest_margin_change):.2f}%，低于阈值{abs(self.risk_thresholds["margin_decline"])}%',
                            'action': '减仓'
                        })
                        logger.warning(f"⚠️ 两融余额下跌{abs(latest_margin_change):.2f}%，建议减仓")
            
            # 3. 检查个股资金流出
            if 'stock_flow' in analysis_results:
                df, alerts, risk_level = analysis_results['stock_flow']
                
                if df is not None and not df.empty and '散户净流入(万)' in df.columns:
                    for idx, row in df.iterrows():
                        code = row.get('股票代码', '未知')
                        retail_inflow = row.get('散户净流入(万)', 0)
                        
                        if pd.notna(retail_inflow) and retail_inflow < self.risk_thresholds['retail_outflow']:
                            risk_actions.append({
                                'type': '个股资金流',
                                'code': code,
                                'reason': f'散户净流出{abs(retail_inflow):.2f}万，低于阈值{abs(self.risk_thresholds["retail_outflow"])}万',
                                'action': '减仓'
                            })
                            logger.warning(f"⚠️ {code} 散户净流出{abs(retail_inflow):.2f}万，建议减仓")
            
            return risk_actions
            
        except Exception as e:
            logger.error(f"[集成] 检查风控减仓失败: {e}")
            return []
    
    def run_integrated_workflow(self):
        """
        运行集成工作流（盯盘/选股）
        """
        try:
            logger.info("="*80)
            logger.info("[集成] 开始运行集成工作流")
            logger.info(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("="*80)
            
            # 1. 获取资金数据
            logger.info("\n[步骤1/5] 获取资金数据...")
            analysis_results = self.fetch_all_funds_data()
            
            if not analysis_results:
                logger.error("[集成] 获取资金数据失败")
                return False
            
            # 2. 分析资金分类
            logger.info("\n[步骤2/5] 分析资金分类...")
            analysis_results = self.analyze_all_funds(analysis_results)
            
            # 3. 检查潜力股
            logger.info("\n[步骤3/5] 检查潜力股...")
            potential_stocks = self.check_potential_stocks(analysis_results)
            
            if potential_stocks:
                logger.info(f"\n✅ 发现 {len(potential_stocks)} 只潜力股:")
                for stock in potential_stocks:
                    logger.info(f"  - [{stock['type']}] {stock['code']}: {stock['reason']} -> {stock['action']}")
            else:
                logger.info("\n✓ 未发现潜力股")
            
            # 4. 检查风控减仓
            logger.info("\n[步骤4/5] 检查风控减仓...")
            risk_actions = self.check_risk_reduction(analysis_results)
            
            if risk_actions:
                logger.warning(f"\n⚠️ 发现 {len(risk_actions)} 个风控信号:")
                for action in risk_actions:
                    logger.warning(f"  - [{action['type']}] {action['code']}: {action['reason']} -> {action['action']}")
            else:
                logger.info("\n✓ 未发现风控信号")
            
            # 5. 生成综合报告
            logger.info("\n[步骤5/5] 生成综合报告...")
            comprehensive_report = self.reporter.generate_comprehensive_report(analysis_results)
            
            logger.info(f"\n✓ 综合报告生成完成:")
            logger.info(f"  - CSV: {comprehensive_report.get('csv', '无')}")
            logger.info(f"  - Markdown: {comprehensive_report.get('markdown', '无')}")
            logger.info(f"  - 图表: {len(comprehensive_report.get('charts', {}))} 张")
            
            # 6. 总结
            logger.info("\n[集成总结]")
            logger.info(f"  潜力股: {len(potential_stocks)} 只")
            logger.info(f"  风控信号: {len(risk_actions)} 个")
            
            if potential_stocks and not risk_actions:
                logger.info("  ✅ 市场环境良好，可适当建仓")
            elif not potential_stocks and risk_actions:
                logger.warning("  ⚠️ 市场风险较高，建议减仓观望")
            else:
                logger.info("  ✓ 市场平稳，正常操作")
            
            logger.info("\n" + "="*80)
            logger.info("✅ 集成工作流执行成功!")
            logger.info("="*80)
            
            return {
                'potential_stocks': potential_stocks,
                'risk_actions': risk_actions,
                'comprehensive_report': comprehensive_report,
                'analysis_results': analysis_results
            }
            
        except Exception as e:
            logger.error(f"[集成] 运行集成工作流失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def fetch_all_funds_data(self):
        """
        获取所有资金数据（Mock）
        
        返回:
            dict: 资金数据字典
        """
        try:
            import pandas as pd
            import numpy as np
            from datetime import datetime, timedelta
            
            logger.info("  - 获取两融数据...")
            margin_df = pd.DataFrame({
                'trade_date': [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(10, 0, -1)],
                'rzye': [10000 + i*50 + np.random.randn()*50 for i in range(10)],
                'rzmre': [2000 + i*10 + np.random.randn()*10 for i in range(10)]
            })
            
            logger.info("  - 获取南北向资金...")
            funds_df = pd.DataFrame({
                'trade_date': [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(10, 0, -1)],
                'north_money': [50 + np.random.randn()*10 for i in range(10)],
                'south_money': [20 + np.random.randn()*5 for i in range(10)]
            })
            
            logger.info("  - 获取龙虎榜...")
            lhb_df = pd.DataFrame({
                'name': ['股票A', '股票B', '股票C', '股票D', '股票E'],
                'buy_amount': [100, 80, 60, 40, 20],
                'total_amount': [150, 120, 100, 80, 50]
            })
            lhb_df['机构买入比'] = lhb_df['buy_amount'] / lhb_df['total_amount']
            
            logger.info("  - 获取个股资金流...")
            flow_df = pd.DataFrame({
                'code': ['600519.SH', '300750.SZ', '000001.SZ'] * 2,
                'main_inflow': [100 + np.random.randn()*20 for _ in range(6)],
                'retail_inflow': [50 + np.random.randn()*10 for _ in range(6)],
                'turnover': [5 + np.random.randn()*2 for _ in range(6)],
                'amount': [1000 + np.random.randn()*100 for _ in range(6)]
            })
            
            return {
                'margin': margin_df,
                'north_south_funds': funds_df,
                'lhb': lhb_df,
                'stock_flow': flow_df
            }
            
        except Exception as e:
            logger.error(f"[集成] 获取资金数据失败: {e}")
            return {}
    
    def analyze_all_funds(self, raw_data):
        """
        分析所有资金数据
        
        参数:
            raw_data: 原始数据
        
        返回:
            dict: 分析结果
        """
        try:
            analysis_results = {}
            
            # 1. 分析两融
            if 'margin' in raw_data:
                df, alerts, risk_level = self.analyzer.analyze_margin(raw_data['margin'])
                analysis_results['margin'] = (df, alerts, risk_level)
                logger.info(f"  ✓ 两融分析: {len(alerts)} 条警报, 风险等级: {risk_level}")
            
            # 2. 分析南北向资金
            if 'north_south_funds' in raw_data:
                df, alerts, risk_level = self.analyzer.analyze_north_south_funds(raw_data['north_south_funds'])
                analysis_results['north_south_funds'] = (df, alerts, risk_level)
                logger.info(f"  ✓ 南北向资金: {len(alerts)} 条警报, 风险等级: {risk_level}")
            
            # 3. 分析龙虎榜
            if 'lhb' in raw_data:
                df, alerts, risk_level = self.analyzer.analyze_lhb(raw_data['lhb'])
                analysis_results['lhb'] = (df, alerts, risk_level)
                logger.info(f"  ✓ 龙虎榜: {len(alerts)} 条警报, 风险等级: {risk_level}")
            
            # 4. 分析个股资金流
            if 'stock_flow' in raw_data:
                df, alerts, risk_level = self.analyzer.analyze_stock_flow(raw_data['stock_flow'])
                analysis_results['stock_flow'] = (df, alerts, risk_level)
                logger.info(f"  ✓ 个股资金流: {len(alerts)} 条警报, 风险等级: {risk_level}")
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"[集成] 分析资金数据失败: {e}")
            return {}


def main():
    """主函数"""
    print("="*80)
    print("集成测试 - FundsMonitor + 主平台 + LiangRongMonitor")
    print("="*80)
    
    # 创建集成监控系统
    monitor = IntegratedFundsMonitor()
    
    # 运行集成工作流
    result = monitor.run_integrated_workflow()
    
    if result:
        print("\n" + "="*80)
        print("✅ 集成测试成功！")
        print("="*80)
        print(f"\n发现潜力股: {len(result['potential_stocks'])} 只")
        print(f"发现风控信号: {len(result['risk_actions'])} 个")
        
        if result['potential_stocks']:
            print("\n潜力股列表:")
            for stock in result['potential_stocks']:
                print(f"  - [{stock['type']}] {stock['code']}: {stock['reason']} -> {stock['action']}")
        
        if result['risk_actions']:
            print("\n风控信号列表:")
            for action in result['risk_actions']:
                print(f"  - [{action['type']}] {action['code']}: {action['reason']} -> {action['action']}")
        
        print("\n综合报告已生成，可推送到飞书！")
    else:
        print("\n" + "="*80)
        print("❌ 集成测试失败！")
        print("="*80)


if __name__ == '__main__':
    main()
