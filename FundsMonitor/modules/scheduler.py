#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scheduler - 任务调度Agent
支持定时运行全流程、监控自选股、早盘资金异动检查
"""
import logging
from datetime import datetime, timedelta, time
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import json
import os

logger = logging.getLogger(__name__)


class FundsMonitorScheduler:
    """资金监控系统任务调度器"""
    
    def __init__(self, output_dir='./output'):
        self.name = "Scheduler"
        self.output_dir = output_dir
        
        # 自选股配置
        self.watchlist = [
            '600519.SH',  # 贵州茅台
            '300750.SZ',  # 宁德时代
            '000001.SZ'   # 平安银行
        ]
        
        # 创建调度器
        self.scheduler = BlockingScheduler(timezone='Asia/Shanghai')
        
        # 输出目录
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f"{output_dir}/charts", exist_ok=True)
        os.makedirs(f"{output_dir}/reports", exist_ok=True)
    
    def load_modules(self):
        """
        加载必要模块
        
        返回:
            tuple: (analyzer, reporter)
        """
        try:
            from modules.analyzer_v6 import Analyzer
            from modules.reporter import Reporter
            
            analyzer = Analyzer()
            reporter = Reporter(output_dir=self.output_dir)
            
            logger.info("[Scheduler] 模块加载成功")
            return analyzer, reporter
            
        except Exception as e:
            logger.error(f"[Scheduler] 模块加载失败: {e}")
            return None, None
    
    def fetch_mock_data(self, fund_type):
        """
        获取Mock数据（测试用）
        
        参数:
            fund_type: 资金类型
        
        返回:
            DataFrame: 模拟数据
        """
        try:
            import pandas as pd
            import numpy as np
            from datetime import datetime, timedelta
            
            # 生成日期序列（最近10个交易日）
            dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(10, 0, -1)]
            
            if fund_type == 'margin':
                df = pd.DataFrame({
                    'trade_date': dates,
                    'rzye': [10000 + i*50 + np.random.randn()*50 for i in range(10)],
                    'rzmre': [2000 + i*10 + np.random.randn()*10 for i in range(10)]
                })
            
            elif fund_type == 'north_south_funds':
                df = pd.DataFrame({
                    'trade_date': dates,
                    'north_money': [50 + np.random.randn()*10 for i in range(10)],
                    'south_money': [20 + np.random.randn()*5 for i in range(10)]
                })
            
            elif fund_type == 'lhb':
                stocks = ['股票A', '股票B', '股票C', '股票D', '股票E']
                df = pd.DataFrame({
                    'name': stocks,
                    'buy_amount': [100 - i*20 for i in range(5)],
                    'total_amount': [150 - i*30 for i in range(5)]
                })
                df['机构买入比'] = df['buy_amount'] / df['total_amount']
            
            elif fund_type == 'stock_flow':
                df = pd.DataFrame({
                    'code': self.watchlist * 2,
                    'main_inflow': [100 + np.random.randn()*20 for _ in range(6)],
                    'retail_inflow': [50 + np.random.randn()*10 for _ in range(6)],
                    'turnover': [5 + np.random.randn()*2 for _ in range(6)],
                    'amount': [1000 + np.random.randn()*100 for _ in range(6)]
                })
            
            else:
                df = pd.DataFrame()
            
            logger.info(f"[Scheduler] 获取{fund_type}Mock数据成功: {len(df)} 条")
            return df
            
        except Exception as e:
            logger.error(f"[Scheduler] 获取Mock数据失败: {e}")
            return pd.DataFrame()
    
    def run_full_workflow(self):
        """
        运行完整工作流（15:30执行）
        """
        try:
            logger.info("="*80)
            logger.info("[Scheduler] 开始执行完整工作流")
            logger.info(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("="*80)
            
            # 1. 加载模块
            analyzer, reporter = self.load_modules()
            if analyzer is None or reporter is None:
                logger.error("[Scheduler] 模块加载失败，终止工作流")
                return False
            
            # 2. 获取数据
            logger.info("\n[步骤1/5] 获取资金数据...")
            analysis_results = {}
            
            # 两融数据
            margin_df = self.fetch_mock_data('margin')
            margin_df, margin_alerts, margin_risk = analyzer.analyze_margin(margin_df)
            analysis_results['margin'] = (margin_df, margin_alerts, margin_risk)
            logger.info(f"  ✓ 两融数据: {len(margin_alerts)} 条警报, 风险等级: {margin_risk}")
            
            # 南北向资金
            funds_df = self.fetch_mock_data('north_south_funds')
            funds_df, funds_alerts, funds_risk = analyzer.analyze_north_south_funds(funds_df)
            analysis_results['north_south_funds'] = (funds_df, funds_alerts, funds_risk)
            logger.info(f"  ✓ 南北向资金: {len(funds_alerts)} 条警报, 风险等级: {funds_risk}")
            
            # 龙虎榜
            lhb_df = self.fetch_mock_data('lhb')
            lhb_df, lhb_alerts, lhb_risk = analyzer.analyze_lhb(lhb_df)
            analysis_results['lhb'] = (lhb_df, lhb_alerts, lhb_risk)
            logger.info(f"  ✓ 龙虎榜: {len(lhb_alerts)} 条警报, 风险等级: {lhb_risk}")
            
            # 个股资金流
            flow_df = self.fetch_mock_data('stock_flow')
            flow_df, flow_alerts, flow_risk = analyzer.analyze_stock_flow(flow_df)
            analysis_results['stock_flow'] = (flow_df, flow_alerts, flow_risk)
            logger.info(f"  ✓ 个股资金流: {len(flow_alerts)} 条警报, 风险等级: {flow_risk}")
            
            # 3. 生成报告
            logger.info("\n[步骤2/5] 生成报告...")
            comprehensive_report = reporter.generate_comprehensive_report(analysis_results)
            logger.info(f"  ✓ CSV: {comprehensive_report.get('csv', '无')}")
            logger.info(f"  ✓ Markdown: {comprehensive_report.get('markdown', '无')}")
            logger.info(f"  ✓ 图表: {len(comprehensive_report.get('charts', {}))} 张")
            
            # 4. 监控自选股
            logger.info("\n[步骤3/5] 监控自选股...")
            self.monitor_watchlist(flow_df)
            
            # 5. 保存运行日志
            logger.info("\n[步骤4/5] 保存运行日志...")
            self.save_run_log(analysis_results, comprehensive_report)
            
            # 6. 总结
            logger.info("\n[步骤5/5] 工作流完成...")
            self.summarize_results(analysis_results)
            
            logger.info("\n" + "="*80)
            logger.info("✅ 完整工作流执行成功!")
            logger.info("="*80)
            
            return True
            
        except Exception as e:
            logger.error(f"[Scheduler] 执行完整工作流失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def monitor_watchlist(self, flow_df):
        """
        监控自选股资金变化
        
        参数:
            flow_df: 个股资金流DataFrame
        """
        try:
            logger.info(f"\n[自选股监控] 监控 {len(self.watchlist)} 只股票...")
            
            if flow_df is None or flow_df.empty:
                logger.warning("[自选股监控] 资金流数据为空")
                return
            
            # 按股票分组
            for stock_code in self.watchlist:
                stock_data = flow_df[flow_df['code'] == stock_code]
                
                if stock_data.empty:
                    logger.warning(f"  ⚠️ {stock_code}: 无数据")
                    continue
                
                # 提取最新数据
                latest = stock_data.iloc[-1]
                
                main_inflow = latest.get('主力净流入(万)', 0)
                retail_inflow = latest.get('散户净流入(万)', 0)
                turnover = latest.get('换手率', 0)
                
                # 判断资金状态
                if main_inflow > 10000:  # >1亿
                    logger.info(f"  ✅ {stock_code}: 主力净流入 {main_inflow:.2f}万 → 强势")
                elif main_inflow > 0:
                    logger.info(f"  ✓ {stock_code}: 主力净流入 {main_inflow:.2f}万 → 上涨")
                else:
                    logger.warning(f"  ⚠️ {stock_code}: 主力净流出 {abs(main_inflow):.2f}万 → 下跌")
                
                # 换手率预警
                if pd.notna(turnover) and turnover > 10:
                    logger.warning(f"  ⚠️ {stock_code}: 换手率 {turnover:.2f}% → 高速换手")
            
            logger.info("[自选股监控] 完成")
            
        except Exception as e:
            logger.error(f"[自选股监控] 失败: {e}")
    
    def early_morning_check(self):
        """
        早盘资金异动检查（9:00执行）
        """
        try:
            logger.info("="*80)
            logger.info("[Scheduler] 开始早盘资金异动检查")
            logger.info(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("="*80)
            
            # 1. 加载模块
            analyzer, reporter = self.load_modules()
            if analyzer is None or reporter is None:
                logger.error("[Scheduler] 模块加载失败，终止检查")
                return False
            
            # 2. 获取昨日数据
            logger.info("\n[步骤1/3] 获取昨日资金数据...")
            
            # 获取自选股资金流
            flow_df = self.fetch_mock_data('stock_flow')
            flow_df, flow_alerts, flow_risk = analyzer.analyze_stock_flow(flow_df)
            
            # 3. 检测异动
            logger.info("\n[步骤2/3] 检测资金异动...")
            abnormal_stocks = self.detect_abnormal_flow(flow_df)
            
            # 4. 生成异动报告
            logger.info("\n[步骤3/3] 生成异动报告...")
            if abnormal_stocks:
                logger.info(f"⚠️ 发现 {len(abnormal_stocks)} 只股票资金异动:")
                for stock in abnormal_stocks:
                    logger.info(f"  - {stock['code']}: {stock['reason']}")
                
                # 保存异动报告
                self.save_abnormal_report(abnormal_stocks)
            else:
                logger.info("✓ 未发现资金异动")
            
            logger.info("\n" + "="*80)
            logger.info("✅ 早盘资金异动检查完成!")
            logger.info("="*80)
            
            return True
            
        except Exception as e:
            logger.error(f"[Scheduler] 早盘资金异动检查失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def detect_abnormal_flow(self, flow_df):
        """
        检测资金异动
        
        参数:
            flow_df: 个股资金流DataFrame
        
        返回:
            list: 异动股票列表
        """
        try:
            abnormal = []
            
            if flow_df is None or flow_df.empty:
                return abnormal
            
            # 按股票分组
            for stock_code in self.watchlist:
                stock_data = flow_df[flow_df['code'] == stock_code]
                
                if stock_data.empty:
                    continue
                
                latest = stock_data.iloc[-1]
                
                main_inflow = latest.get('主力净流入(万)', 0)
                turnover = latest.get('换手率', 0)
                
                # 异动条件1: 主力大幅净流入（>5亿）
                if main_inflow > 50000:
                    abnormal.append({
                        'code': stock_code,
                        'type': '主力大幅净流入',
                        'value': main_inflow,
                        'reason': f'主力净流入 {main_inflow:.2f}万，建议关注'
                    })
                
                # 异动条件2: 换手率异常高（>20%）
                if pd.notna(turnover) and turnover > 20:
                    abnormal.append({
                        'code': stock_code,
                        'type': '换手率异常高',
                        'value': turnover,
                        'reason': f'换手率 {turnover:.2f}%，异常活跃'
                    })
            
            return abnormal
            
        except Exception as e:
            logger.error(f"[Scheduler] 检测资金异动失败: {e}")
            return []
    
    def save_run_log(self, analysis_results, comprehensive_report):
        """
        保存运行日志
        
        参数:
            analysis_results: 分析结果
            comprehensive_report: 综合报告
        """
        try:
            log_file = f"{self.output_dir}/run_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            log_data = {
                'timestamp': datetime.now().isoformat(),
                'analysis_results': {},
                'comprehensive_report': {
                    'csv': comprehensive_report.get('csv', ''),
                    'markdown': comprehensive_report.get('markdown', ''),
                    'charts': comprehensive_report.get('charts', {})
                }
            }
            
            for fund_type, result in analysis_results.items():
                df, alerts, risk_level = result
                log_data['analysis_results'][fund_type] = {
                    'alerts_count': len(alerts),
                    'risk_level': risk_level,
                    'alerts': alerts[:5]  # 只保存前5条
                }
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✓ 运行日志保存成功: {log_file}")
            
        except Exception as e:
            logger.error(f"[Scheduler] 保存运行日志失败: {e}")
    
    def save_abnormal_report(self, abnormal_stocks):
        """
        保存异动报告
        
        参数:
            abnormal_stocks: 异动股票列表
        """
        try:
            report_file = f"{self.output_dir}/abnormal_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'abnormal_count': len(abnormal_stocks),
                'abnormal_stocks': abnormal_stocks
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✓ 异动报告保存成功: {report_file}")
            
        except Exception as e:
            logger.error(f"[Scheduler] 保存异动报告失败: {e}")
    
    def summarize_results(self, analysis_results):
        """
        总结分析结果
        
        参数:
            analysis_results: 分析结果
        """
        try:
            total_alerts = 0
            risk_summary = {'low': 0, 'medium': 0, 'high': 0}
            
            for fund_type, result in analysis_results.items():
                df, alerts, risk_level = result
                total_alerts += len(alerts)
                risk_summary[risk_level.lower()] += 1
            
            logger.info(f"\n【总结】")
            logger.info(f"  总警报数: {total_alerts}")
            logger.info(f"  风险分布: LOW={risk_summary['low']}, MEDIUM={risk_summary['medium']}, HIGH={risk_summary['high']}")
            
            if risk_summary['high'] > 0:
                logger.warning(f"  ⚠️ 有 {risk_summary['high']} 个高风险资金类型，需要关注！")
            elif risk_summary['medium'] > 0:
                logger.warning(f"  ⚠️ 有 {risk_summary['medium']} 个中风险资金类型，需要留意！")
            else:
                logger.info(f"  ✅ 所有资金类型均为低风险，市场稳定！")
            
        except Exception as e:
            logger.error(f"[Scheduler] 总结结果失败: {e}")
    
    def start(self, autonomous=False):
        """
        启动调度器
        
        参数:
            autonomous: 是否自动运行（默认False）
        """
        try:
            logger.info("="*80)
            logger.info("[Scheduler] 启动资金监控系统")
            logger.info(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("="*80)
            
            # 添加定时任务
            # 1. 每天15:30执行完整工作流
            self.scheduler.add_job(
                self.run_full_workflow,
                trigger=CronTrigger(hour=15, minute=30),
                id='full_workflow',
                name='完整工作流',
                replace_existing=True
            )
            logger.info("✓ 已添加定时任务: 每天15:30执行完整工作流")
            
            # 2. 每天9:00执行早盘资金异动检查
            self.scheduler.add_job(
                self.early_morning_check,
                trigger=CronTrigger(hour=9, minute=0),
                id='early_check',
                name='早盘资金异动检查',
                replace_existing=True
            )
            logger.info("✓ 已添加定时任务: 每天9:00执行早盘资金异动检查")
            
            # 3. 显示下次执行时间
            jobs = self.scheduler.get_jobs()
            logger.info(f"\n已配置的定时任务:")
            for job in jobs:
                logger.info(f"  - {job.name} (ID: {job.id})")
            logger.info("\n提示: 调度器启动后将自动在指定时间执行任务")
            
            logger.info("\n" + "="*80)
            logger.info("✅ 调度器已启动，等待定时任务执行...")
            logger.info("按 Ctrl+C 停止")
            logger.info("="*80 + "\n")
            
            # 启动调度器
            if autonomous:
                self.scheduler.start()
            else:
                # 测试模式：不启动，只打印信息
                logger.info("[Scheduler] 测试模式：未启动调度器")
                logger.info("提示: 自主运行请使用 start(autonomous=True)")
            
            return True
            
        except Exception as e:
            logger.error(f"[Scheduler] 启动失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_workflow(self):
        """
        手动运行一次工作流（测试用）
        """
        return self.run_full_workflow()
