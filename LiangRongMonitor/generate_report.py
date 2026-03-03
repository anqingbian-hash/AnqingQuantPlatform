#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
两融监控报告生成
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 非GUI后端
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_report():
    """生成监控报告"""
    logger.info("开始生成报告...")
    
    try:
        # 读取数据
        df = pd.read_csv('data/margin_processed.csv')
        
        if df is None or len(df) == 0:
            logger.error("没有可用数据")
            return
        
        # 创建图表目录
        os.makedirs('charts', exist_ok=True)
        
        # 绘制两融趋势图
        plt.figure(figsize=(12, 6))
        plt.plot(df.index, df['融资买入额'], label='融资买入额', color='blue')
        plt.title('两融余额趋势图')
        plt.xlabel('日期')
        plt.ylabel('金额（亿元）')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('charts/margin_trend.png', dpi=300)
        plt.close()
        
        logger.info("报告生成完成")
        logger.info(f"图表保存路径: charts/margin_trend.png")
        
    except Exception as e:
        logger.error(f"报告生成失败: {e}")

if __name__ == '__main__':
    generate_report()
