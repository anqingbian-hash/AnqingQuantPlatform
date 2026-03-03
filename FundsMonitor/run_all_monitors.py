#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资金监控系统主运行脚本
"""
import logging
from datetime import datetime
import sys
import os

# 添加工作空间路径
sys.path.append('/root/.openclaw/workspace/FundsMonitor')

# 导入Scheduler
from modules.scheduler import FundsMonitorScheduler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 主程序
if __name__ == '__main__':
    print("="*80)
    print("FundsMonitor - 全方位资金监控系统")
    print("="*80)
    print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print("功能模块:")
    print("  1. 两融监控")
    print("  2. 南北向资金")
    print("  3. 机构资金")
    print("  4. 龙虎榜")
    print("  5. 个股资金流")
    print("="*80)
    print()
    
    # 创建调度器
    scheduler = FundsMonitorScheduler()
    
    # 运行一次（测试）
    logger.info("立即执行一次（测试全流程）")
    success = scheduler.run_workflow()
    
    if success:
        logger.info("\n✓ 测试执行成功!")
        print("\n输出文件:")
        print("  1. 综合报告: output/comprehensive_report.txt")
        print("  2. 两融图表: charts/margin_trend.png")
        print("="*80)
    else:
        logger.info("\n✗ 测试执行失败!")
        print("="*80)
    
    # 询问是否启动自动模式
    print("\n是否启动自动运行模式？")
    print("  - 每天15:30自动执行")
    print("  - 按Ctrl+C停止")
    print("="*80)
    
    # 启动自动模式
    # user_input = input("\n按Enter启动自动模式，或输入q退出: ")
    # 
    # if user_input.lower() != 'q':
    #     scheduler.start(autonomous=True)
    # else:
    #     logger.info("程序退出")

