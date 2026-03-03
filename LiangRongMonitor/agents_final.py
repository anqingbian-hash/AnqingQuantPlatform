#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
两融监控 - 子Agent团队（适配Tushare数据）
"""
import tushare as ts
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import logging
import yaml
from apscheduler.schedulers.blocking import BlockingScheduler
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# 配置
TUSHARE_TOKEN = '8b159caa2bbf554707c20c3f44fea1e0e6ec75b6afc82c78fa47e47b'

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========================================
# Agent 1: DataFetcher - 数据采集
# ========================================
class DataFetcher:
    """数据采集Agent"""
    
    def __init__(self):
        self.name = "DataFetcher"
        self.ts_pro = ts.pro_api(TUSHARE_TOKEN)
        self.data_source = None
        
    def fetch_margin_data(self):
        """获取两融数据 - Tushare Pro优先，AKShare备用"""
        try:
            logger.info(f"[{self.name}] 尝试从Tushare Pro获取数据...")
            
            # Tushare Pro - 两融余额
            df = self.ts_pro.margin(start_date='20250101', end_date='20260303')
            
            if df is not None and len(df) > 0:
                self.data_source = 'tushare_pro'
                logger.info(f"[{self.name}] Tushare Pro成功，获取到 {len(df)} 条数据")
                return df
            
        except Exception as e:
            logger.warning(f"[{self.name}] Tushare Pro失败: {e}，尝试AKShare备用...")
        
        # Fallback to AKShare
        try:
            logger.info(f"[{self.name}] 尝试从AKShare获取数据...")
            
            df = ak.stock_margin_detail()
            
            if df is not None and len(df) > 0:
                self.data_source = 'akshare'
                logger.info(f"[{self.name}] AKShare成功，获取到 {len(df)} 条数据")
                return df
            
        except Exception as e:
            logger.error(f"[{self.name}] AKShare也失败: {e}")
            return None
        
        return None
    
    def save_data(self, df, filename='data/margin_raw.csv'):
        """保存数据"""
        try:
            import os
            os.makedirs('data', exist_ok=True)
            
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            logger.info(f"[{self.name}] 数据已保存到 {filename}")
            
            return True
        except Exception as e:
            logger.error(f"[{self.name}] 保存数据失败: {e}")
            return False

# ========================================
# Agent 2: Analyzer - 数据分析
# ========================================
class Analyzer:
    """数据分析Agent"""
    
    def __init__(self):
        self.name = "Analyzer"
        
    def calculate_ma(self, df, window=5):
        """计算移动平均线"""
        try:
            # 使用融资余额(rzye)计算MA5
            df['MA5'] = df['rzye'].rolling(window=window).mean()
            logger.info(f"[{self.name}] MA{window} 计算完成")
            return df
        except Exception as e:
            logger.error(f"[{self.name}] MA{window} 计算失败: {e}")
            return df
    
    def calculate_change_rate(self, df):
        """计算变化率"""
        try:
            # 日变化率
            df['daily_change_pct'] = df['rzye'].pct_change() * 100
            
            # 周变化率（5日）
            df['weekly_change_pct'] = df['rzye'].pct_change(5) * 100
            
            logger.info(f"[{self.name}] 变化率计算完成")
            return df
        except Exception as e:
            logger.error(f"[{self.name}] 变化率计算失败: {e}")
            return df
    
    def predict_next_day(self, df):
        """预测下一日融资余额（线性回归）"""
        try:
            # 过滤有效数据
            df_valid = df.dropna(subset=['rzye', 'MA5'])
            
            if len(df_valid) < 5:
                logger.warning(f"[{self.name}] 数据不足，无法预测")
                return df, None
            
            # 按日期排序
            df_valid = df_valid.sort_values('trade_date')
            
            # 准备数据
            X = np.array(range(len(df_valid))).reshape(-1, 1)
            y = df_valid['rzye'].values
            
            # 标准化
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # 线性回归
            model = LinearRegression()
            model.fit(X_scaled, y)
            
            # 预测下一日
            next_day_scaled = scaler.transform([[len(df_valid)]])
            prediction = model.predict(next_day_scaled)[0]
            
            # 计算预测置信度
            score = model.score(X_scaled, y)
            
            logger.info(f"[{self.name}] 下一日预测: {prediction:.2f} (置信度: {score:.2%})")
            
            return df, {
                'prediction': prediction,
                'confidence': score,
                'date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            logger.error(f"[{self.name}] 预测失败: {e}")
            return df, None
    
    def generate_alerts(self, df, config_file='config/thresholds.yaml'):
        """生成警报"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            alerts = []
            latest = df.iloc[-1]
            
            # 检查日变化率
            daily_change = latest.get('daily_change_pct', 0)
            if pd.notna(daily_change) and abs(daily_change) > config['daily_change']['warning']:
                level = 'warning'
                if abs(daily_change) > config['daily_change']['danger']:
                    level = 'danger'
                if abs(daily_change) > config['daily_change']['critical']:
                    level = 'critical'
                
                alerts.append({
                    'type': 'daily_change',
                    'level': level,
                    'value': float(daily_change),
                    'threshold': config['daily_change']['warning'],
                    'message': "日变化率" + level + ": " + str(round(daily_change, 2)) + "%"
                })
                logger.warning(f"[{self.name}] 日变化率警报: {daily_change:.2f}%")
            
            # 检查周变化率
            weekly_change = latest.get('weekly_change_pct', 0)
            if pd.notna(weekly_change) and abs(weekly_change) > config['weekly_change']['warning']:
                level = 'warning'
                if abs(weekly_change) > config['weekly_change']['danger']:
                    level = 'danger'
                if abs(weekly_change) > config['weekly_change']['critical']:
                    level = 'critical'
                
                alerts.append({
                    'type': 'weekly_change',
                    'level': level,
                    'value': float(weekly_change),
                    'threshold': config['weekly_change']['warning'],
                    'message': "周变化率" + level + ": " + str(round(weekly_change, 2)) + "%"
                })
                logger.warning(f"[{self.name}] 周变化率警报: {weekly_change:.2f}%")
            
            return alerts
            
        except Exception as e:
            logger.error(f"[{self.name}] 警报生成失败: {e}")
            return []

# ========================================
# Agent 3: Reporter - 报告生成
# ========================================
class Reporter:
    """报告生成Agent"""
    
    def __init__(self):
        self.name = "Reporter"
        
    def save_csv(self, df, filename='data/margin_processed.csv'):
        """保存CSV报告"""
        try:
            import os
            os.makedirs('data', exist_ok=True)
            
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            logger.info(f"[{self.name}] CSV报告已保存: {filename}")
            return True
        except Exception as e:
            logger.error(f"[{self.name}] CSV保存失败: {e}")
            return False
    
    def generate_chart(self, df, filename='charts/margin_trend.png'):
        """生成趋势图"""
        try:
            import os
            os.makedirs('charts', exist_ok=True)
            
            # 按日期排序
            df = df.sort_values('trade_date')
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
            
            # 图1: 融资余额趋势
            ax1.plot(range(len(df)), df['rzye'], label='融资余额', color='blue', linewidth=2)
            if 'MA5' in df.columns:
                ax1.plot(range(len(df)), df['MA5'], label='MA5', color='orange', linewidth=1.5, linestyle='--')
            ax1.set_title('两融余额趋势图', fontsize=16, fontweight='bold')
            ax1.set_ylabel('金额（元）', fontsize=12)
            ax1.legend(loc='best')
            ax1.grid(True, alpha=0.3)
            
            # 图2: 变化率
            df_valid = df.dropna(subset=['daily_change_pct'])
            ax2.bar(range(len(df_valid)), df_valid['daily_change_pct'], label='日变化率', color='green', alpha=0.6)
            ax2.set_title('两融余额变化率', fontsize=16, fontweight='bold')
            ax2.set_ylabel('变化率（%）', fontsize=12)
            ax2.set_xlabel('交易日', fontsize=12)
            ax2.legend(loc='best')
            ax2.grid(True, alpha=0.3)
            ax2.axhline(y=0, color='red', linestyle='-', linewidth=1)
            
            plt.tight_layout()
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"[{self.name}] 趋势图已保存: {filename}")
            return True
        except Exception as e:
            logger.error(f"[{self.name}] 图表生成失败: {e}")
            return False
    
    def generate_report(self, df, prediction, alerts, filename='output/daily_report.md'):
        """生成文字报告"""
        try:
            import os
            os.makedirs('output', exist_ok=True)
            
            latest = df.iloc[-1]
            
            # 预测信息
            if prediction:
                prediction_date = prediction['date']
                prediction_value = str(round(prediction['prediction'], 2)) + " 亿元"
                prediction_confidence = str(round(prediction['confidence'] * 100, 2)) + "%"
            else:
                prediction_date = 'N/A'
                prediction_value = 'N/A'
                prediction_confidence = 'N/A'
            
            report = "# 两融监控日报\n\n"
            report += "**日期**: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n"
            report += "**数据来源**: Tushare Pro / AKShare\n\n"
            report += "---\n\n"
            report += "## 📊 数据概览\n\n"
            report += "| 指标 | 值 |\n"
            report += "|------|-----|\n"
            report += "| 融资余额 | " + str(round(latest['rzye'] / 1e8, 2)) + " 亿元 |\n"
            report += "| 融券余额 | " + str(round(latest['rqye'] / 1e8, 2)) + " 亿元 |\n"
            
            if pd.notna(latest.get('daily_change_pct')):
                report += "| 日变化率 | " + str(round(latest['daily_change_pct'], 2)) + "% |\n"
            if pd.notna(latest.get('weekly_change_pct')):
                report += "| 周变化率 | " + str(round(latest['weekly_change_pct'], 2)) + "% |\n"
            if pd.notna(latest.get('MA5')):
                report += "| MA5 | " + str(round(latest['MA5'] / 1e8, 2)) + " 亿元 |\n"
            
            report += "\n---\n\n"
            report += "## 📈 预测信息\n\n"
            report += "| 项目 | 值 |\n"
            report += "|------|-----|\n"
            report += "| 预测日期 | " + prediction_date + " |\n"
            report += "| 预测融资余额 | " + prediction_value + " |\n"
            report += "| 预测置信度 | " + prediction_confidence + " |\n\n"
            report += "---\n\n"
            report += "## 🚨 警报列表\n\n"
            
            if alerts:
                for i, alert in enumerate(alerts, 1):
                    report += "### 警报 " + str(i) + "\n\n"
                    report += "- **类型**: " + alert['type'] + "\n"
                    report += "- **级别**: " + alert['level'] + "\n"
                    report += "- **数值**: " + str(round(alert['value'], 2)) + "%\n"
                    report += "- **阈值**: " + str(alert['threshold']) + "%\n"
                    report += "- **说明**: " + alert['message'] + "\n\n"
            else:
                report += "✅ 无警报\n\n"
            
            report += "---\n\n"
            report += "**生成时间**: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(f"[{self.name}] 报告已保存: {filename}")
            return True
        except Exception as e:
            logger.error(f"[{self.name}] 报告生成失败: {e}")
            return False
    
    def push_notification(self, message):
        """推送通知（预留接口）"""
        try:
            logger.info(f"[{self.name}] 推送通知: {message}")
            # TODO: 实现Telegram/微信推送
            return True
        except Exception as e:
            logger.error(f"[{self.name}] 通知推送失败: {e}")
            return False

# ========================================
# Agent 4: Scheduler - 任务调度
# ========================================
class Scheduler:
    """任务调度Agent"""
    
    def __init__(self):
        self.name = "Scheduler"
        self.scheduler = BlockingScheduler()
        
    def setup_schedule(self):
        """设置定时任务"""
        try:
            # 每天15:30执行（T+1数据更新后）
            self.scheduler.add_job(
                self.run_workflow,
                'cron',
                hour=15,
                minute=30,
                id='daily_margin_monitor',
                name='两融监控每日任务'
            )
            
            logger.info(f"[{self.name}] 定时任务已设置: 每天15:30")
            return True
        except Exception as e:
            logger.error(f"[{self.name}] 定时任务设置失败: {e}")
            return False
    
    def run_workflow(self):
        """运行完整工作流"""
        try:
            logger.info("="*60)
            logger.info("开始执行两融监控工作流")
            logger.info(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("="*60)
            
            # Agent 1: 数据采集
            logger.info("\n[步骤1] 数据采集...")
            fetcher = DataFetcher()
            df = fetcher.fetch_margin_data()
            
            if df is None or len(df) == 0:
                logger.error("数据获取失败，工作流终止")
                return False
            
            fetcher.save_data(df)
            
            # Agent 2: 数据分析
            logger.info("\n[步骤2] 数据分析...")
            analyzer = Analyzer()
            
            # 计算MA5
            df = analyzer.calculate_ma(df, window=5)
            
            # 计算变化率
            df = analyzer.calculate_change_rate(df)
            
            # 预测下一日
            df, prediction = analyzer.predict_next_day(df)
            
            # 生成警报
            alerts = analyzer.generate_alerts(df)
            
            # Agent 3: 报告生成
            logger.info("\n[步骤3] 报告生成...")
            reporter = Reporter()
            
            # 保存CSV
            reporter.save_csv(df)
            
            # 生成图表
            reporter.generate_chart(df)
            
            # 生成报告
            reporter.generate_report(df, prediction, alerts)
            
            # 推送通知
            if alerts:
                reporter.push_notification("发现 " + str(len(alerts)) + " 个警报")
            
            logger.info("\n[步骤4] 工作流完成")
            logger.info("="*60)
            logger.info("两融监控工作流执行成功")
            logger.info("="*60)
            
            return True
            
        except Exception as e:
            logger.error(f"工作流执行失败: {e}")
            return False
    
    def start(self):
        """启动调度器"""
        try:
            logger.info(f"[{self.name}] 调度器启动中...")
            self.setup_schedule()
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info(f"[{self.name}] 调度器停止")
            self.scheduler.shutdown()

# ========================================
# 主程序
# ========================================
if __name__ == '__main__':
    logger.info("="*60)
    logger.info("两融监控 - 子Agent团队")
    logger.info("="*60)
    logger.info("团队成员:")
    logger.info("  1. DataFetcher - 数据采集（Tushare Pro + AKShare）")
    logger.info("  2. Analyzer - 数据分析（MA5 + 变化率 + 预测）")
    logger.info("  3. Reporter - 报告生成（CSV + 图表 + 通知）")
    logger.info("  4. Scheduler - 任务调度（每日15:30）")
    logger.info("="*60)
    
    # 测试运行
    scheduler = Scheduler()
    scheduler.run_workflow()
    
    # 启动调度器（注释掉以避免阻塞）
    # scheduler.start()
