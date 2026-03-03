#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
两融额度监控系统
"""
import akshare as ak
import pandas as pd
import logging
from datetime import datetime
import yaml
import json
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MarginMonitor:
    def __init__(self):
        self.load_config()
        
    def load_config(self):
        """加载配置文件"""
        config_path = 'config/monitor.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        logger.info("配置加载完成")
        
    def get_margin_data(self):
        """获取两融数据"""
        try:
            logger.info("开始获取两融数据...")
            
            # 获取两融余额数据
            margin_debt = ak.stock_margin_detail()
            
            # 保存原始数据
            os.makedirs('data', exist_ok=True)
            margin_debt.to_csv('data/margin_raw.csv', index=False, encoding='utf-8-sig')
            
            logger.info(f"获取到 {len(margin_debt)} 条两融数据")
            return margin_debt
            
        except Exception as e:
            logger.error(f"获取两融数据失败: {e}")
            return None
    
    def process_data(self, df):
        """处理数据"""
        if df is None:
            return None
            
        try:
            logger.info("开始处理数据...")
            
            # 数据清洗
            df = df.dropna()
            
            # 计算变化率
            df['daily_change_pct'] = df['融资买入额'].pct_change() * 100
            df['weekly_change_pct'] = df['融资买入额'].pct_change(5) * 100
            
            # 保存处理后的数据
            df.to_csv('data/margin_processed.csv', index=False, encoding='utf-8-sig')
            
            logger.info("数据处理完成")
            return df
            
        except Exception as e:
            logger.error(f"数据处理失败: {e}")
            return None
    
    def check_alerts(self, df):
        """检查预警"""
        try:
            alerts = []
            
            if df is None or len(df) == 0:
                return alerts
                
            # 获取最新数据
            latest = df.iloc[-1]
            
            # 检查日变化率
            if abs(latest.get('daily_change_pct', 0)) > self.config['monitor']['thresholds']['daily_change_percent']:
                alert = {
                    'type': 'daily_change',
                    'level': 'warning',
                    'value': latest['daily_change_pct'],
                    'threshold': self.config['monitor']['thresholds']['daily_change_percent'],
                    'timestamp': datetime.now().isoformat()
                }
                alerts.append(alert)
                logger.warning(f"日变化率预警: {latest['daily_change_pct']:.2f}%")
            
            # 保存预警记录
            if alerts:
                os.makedirs('logs', exist_ok=True)
                with open('logs/alerts.log', 'a', encoding='utf-8') as f:
                    f.write(json.dumps(alert, ensure_ascii=False) + '\n')
            
            return alerts
            
        except Exception as e:
            logger.error(f"预警检查失败: {e}")
            return []
    
    def run(self):
        """运行监控"""
        logger.info("="*60)
        logger.info("两融监控系统启动")
        logger.info(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*60)
        
        # 获取数据
        df = self.get_margin_data()
        
        # 处理数据
        df = self.process_data(df)
        
        # 检查预警
        alerts = self.check_alerts(df)
        
        if alerts:
            logger.warning(f"发现 {len(alerts)} 个预警")
        else:
            logger.info("未发现预警")
        
        logger.info("="*60)
        logger.info("监控完成")
        logger.info("="*60)

if __name__ == '__main__':
    monitor = MarginMonitor()
    monitor.run()
