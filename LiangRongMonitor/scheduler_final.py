#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
两融监控调度器 - 卞董专用版本
每天15:30自动执行完整监控流程
"""
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
import sys
import os

# 添加工作空间路径
sys.path.append('/root/.openclaw/workspace/LiangRongMonitor')

# 导入子Agent
from fetch_margin_fixed import fetch_margin_data
from analyze_margin import analyze_margin_changes
from reporter import Reporter

# 卞董的自选股
WATCHLIST = [
    '600519.SH',  # 贵州茅台
    '300750.SZ',  # 宁德时代
    '000001.SZ'   # 平安银行
]

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MarginScheduler:
    """两融监控调度器"""
    
    def __init__(self):
        self.name = "Scheduler"
        self.scheduler = BlockingScheduler(timezone='Asia/Shanghai')
        self.reporter = Reporter()
        
        # 自选股监控数据
        self.watchlist_data = {}
    
    def fetch_market_data(self):
        """获取市场两融数据"""
        logger.info("\n" + "="*80)
        logger.info("步骤1: 获取市场两融数据")
        logger.info("="*80)
        
        try:
            df, source = fetch_margin_data()
            
            if df is not None and not df.empty:
                logger.info(f"✓ 市场数据获取成功（来源: {source}）")
                logger.info(f"数据维度: {df.shape}")
                return df, source
            else:
                logger.error("✗ 市场数据获取失败")
                return None, None
        except Exception as e:
            logger.error(f"✗ 市场数据获取异常: {e}")
            return None, None
    
    def fetch_watchlist_data(self):
        """获取自选股两融数据"""
        logger.info("\n" + "="*80)
        logger.info("步骤2: 获取自选股两融数据")
        logger.info("="*80)
        
        for stock in WATCHLIST:
            try:
                logger.info(f"  获取 {stock} 两融数据...")
                
                df, source = fetch_margin_data(symbol=stock)
                
                if df is not None and not df.empty:
                    self.watchlist_data[stock] = {
                        'df': df,
                        'source': source
                    }
                    logger.info(f"  ✓ {stock} 数据获取成功（来源: {source}）")
                else:
                    logger.warning(f"  ✗ {stock} 数据获取失败")
            except Exception as e:
                logger.error(f"  ✗ {stock} 数据获取异常: {e}")
        
        return len(self.watchlist_data) > 0
    
    def analyze_market(self, df):
        """分析市场数据"""
        logger.info("\n" + "="*80)
        logger.info("步骤3: 分析市场两融数据")
        logger.info("="*80)
        
        try:
            df_analyzed, alerts = analyze_margin_changes(df, history_days=30)
            
            if df_analyzed is not None:
                logger.info("✓ 市场数据分析完成")
                return df_analyzed, alerts
            else:
                logger.error("✗ 市场数据分析失败")
                return None, []
        except Exception as e:
            logger.error(f"✗ 市场数据分析异常: {e}")
            return None, []
    
    def analyze_watchlist(self):
        """分析自选股数据"""
        logger.info("\n" + "="*80)
        logger.info("步骤4: 分析自选股两融数据")
        logger.info("="*80)
        
        watchlist_alerts = []
        
        for stock, data in self.watchlist_data.items():
            try:
                logger.info(f"  分析 {stock}...")
                
                df = data['df']
                df_analyzed, alerts = analyze_margin_changes(df, history_days=10)
                
                if alerts:
                    for alert in alerts:
                        watchlist_alerts.append({
                            'stock': stock,
                            'alert': alert
                        })
                        logger.warning(f"  ⚠️ {stock}: {alert}")
                else:
                    logger.info(f"  ✓ {stock}: 无警报")
                    
            except Exception as e:
                logger.error(f"  ✗ {stock} 分析异常: {e}")
        
        return watchlist_alerts
    
    def generate_report(self, df, source, market_alerts, watchlist_alerts):
        """生成完整报告"""
        logger.info("\n" + "="*80)
        logger.info("步骤5: 生成监控报告")
        logger.info("="*80)
        
        try:
            # 合并警报
            all_alerts = []
            
            # 添加市场警报
            if market_alerts:
                all_alerts.append("【市场警报】")
                all_alerts.extend(market_alerts)
            
            # 添加自选股警报
            if watchlist_alerts:
                all_alerts.append("\n【自选股警报】")
                for item in watchlist_alerts:
                    all_alerts.append(f"  {item['stock']}: {item['alert']}")
            
            # 生成报告
            success = self.reporter.generate_full_report(df, source, all_alerts)
            
            if success:
                logger.info("✓ 报告生成完成")
                return True
            else:
                logger.error("✗ 报告生成失败")
                return False
        except Exception as e:
            logger.error(f"✗ 报告生成异常: {e}")
            return False
    
    def run_workflow(self):
        """运行完整监控工作流"""
        try:
            logger.info("\n" + "="*80)
            logger.info("开始执行两融监控工作流")
            logger.info(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("="*80)
            
            # 步骤1: 获取市场数据
            df_market, source = self.fetch_market_data()
            
            if df_market is None:
                logger.error("市场数据获取失败，工作流终止")
                return False
            
            # 步骤2: 获取自选股数据
            has_watchlist = self.fetch_watchlist_data()
            
            # 步骤3: 分析市场数据
            df_analyzed, market_alerts = self.analyze_market(df_market)
            
            if df_analyzed is None:
                logger.error("市场数据分析失败，工作流终止")
                return False
            
            # 步骤4: 分析自选股数据（如果有的话）
            watchlist_alerts = []
            if has_watchlist:
                watchlist_alerts = self.analyze_watchlist()
            
            # 步骤5: 生成报告
            success = self.generate_report(
                df_analyzed, 
                source, 
                market_alerts, 
                watchlist_alerts
            )
            
            # 工作流总结
            logger.info("\n" + "="*80)
            logger.info("工作流执行总结")
            logger.info("="*80)
            logger.info(f"市场数据: {'成功' if df_market is not None else '失败'}")
            logger.info(f"自选股数据: {'成功' if has_watchlist else '无'}")
            logger.info(f"市场警报: {len(market_alerts)} 条")
            logger.info(f"自选股警报: {len(watchlist_alerts)} 条")
            logger.info(f"报告生成: {'成功' if success else '失败'}")
            logger.info("="*80)
            logger.info("工作流执行完成")
            logger.info("="*80)
            
            return success
            
        except Exception as e:
            logger.error(f"工作流执行异常: {e}")
            return False
    
    def setup_schedule(self):
        """设置定时任务"""
        logger.info("\n" + "="*80)
        logger.info("设置定时任务")
        logger.info("="*80)
        
        try:
            # 每天15:30执行（交易后）
            self.scheduler.add_job(
                self.run_workflow,
                'cron',
                hour=15,
                minute=30,
                id='daily_margin_monitor',
                name='两融监控每日任务'
            )
            
            logger.info("✓ 定时任务已设置: 每天15:30（北京时间）")
            logger.info("  任务ID: daily_margin_monitor")
            logger.info("  任务名称: 两融监控每日任务")
            
            return True
        except Exception as e:
            logger.error(f"✗ 定时任务设置失败: {e}")
            return False
    
    def start(self, autonomous=False):
        """启动调度器
        
        参数:
            autonomous: 是否自动模式（不阻塞）
        """
        logger.info("\n" + "="*80)
        logger.info("两融监控调度器启动")
        logger.info("="*80)
        logger.info(f"自选股: {', '.join(WATCHLIST)}")
        logger.info(f"执行时间: 每天15:30（北京时间）")
        logger.info(f"自动模式: {autonomous}")
        logger.info("="*80)
        
        # 设置定时任务
        self.setup_schedule()
        
        if autonomous:
            logger.info("\n进入自动运行模式...")
            logger.info("定时任务将自动执行...")
            logger.info("按Ctrl+C停止\n")
            
            # 启动调度器（阻塞）
            try:
                self.scheduler.start()
            except (KeyboardInterrupt, SystemExit):
                logger.info("\n调度器已停止")
                self.scheduler.shutdown()
        else:
            logger.info("\n手动模式: 执行一次后退出")

# ========================================
# 主程序
# ========================================
if __name__ == '__main__':
    print("="*80)
    print("两融监控调度器 - 卞董专用版本")
    print("="*80)
    print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print("自选股监控:")
    for i, stock in enumerate(WATCHLIST, 1):
        print(f"  {i}. {stock}")
    print("="*80)
    
    # 创建调度器
    scheduler = MarginScheduler()
    
    # 立即执行一次（测试）
    logger.info("\n立即执行一次（测试全流程）")
    success = scheduler.run_workflow()
    
    if success:
        logger.info("\n✓ 测试执行成功!")
    else:
        logger.info("\n✗ 测试执行失败!")
    
    # 询问是否启动自动模式
    print("\n" + "="*80)
    print("是否启动自动运行模式？")
    print("  - 每天15:30自动执行")
    print("  - 按Ctrl+C停止")
    print("="*80)
    
    # 启动自动模式（注释掉以避免阻塞）
    # user_input = input("\n按Enter启动自动模式，或输入q退出: ")
    # 
    # if user_input.lower() != 'q':
    #     scheduler.start(autonomous=True)
    # else:
    #     logger.info("程序退出")
