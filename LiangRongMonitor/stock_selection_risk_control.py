#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
选股策略风控 - 卞董专用版本
两融监控集成到选股策略
"""
import pandas as pd
import logging
import sys
import os

# 添加工作空间路径
sys.path.append('/root/.openclaw/workspace/LiangRongMonitor')

# 导入数据获取
from fetch_margin_fixed import fetch_margin_data

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 卞董的测试股票
TEST_STOCKS = [
    '601611.SH',  # 中国国航
    '000060.SZ',  # 中金岭南
    '600482.SH',  # 中国动力
    '000815.SZ',  # 美利云
    '600157.SH'   # 永泰能源
]

class StockSelectionRiskControl:
    """选股策略风控系统"""
    
    def __init__(self):
        self.name = "StockSelectionRiskControl"
        
        # 风险阈值
        self.risk_thresholds = {
            'stock_change_rate_high': 15.0,   # 个股融资变化率高阈值（%）
            'stock_change_rate_low': -5.0,    # 个股融资变化率低阈值（%）
            'market_change_rate_warning': -5.0,  # 市场融资变化率预警阈值（%）
            'margin_growth_positive': 0.0        # 融资余额增长阈值（%）
        }
    
    def get_stock_margin_data(self, stock_code):
        """获取个股两融数据"""
        try:
            logger.info(f"  获取 {stock_code} 两融数据...")
            
            df, source = fetch_margin_data(symbol=stock_code)
            
            if df is not None and not df.empty:
                logger.info(f"  ✓ {stock_code} 数据获取成功（来源: {source}）")
                return df, source
            else:
                logger.warning(f"  ✗ {stock_code} 数据获取失败")
                return None, None
                
        except Exception as e:
            logger.error(f"  ✗ {stock_code} 数据获取异常: {e}")
            return None, None
    
    def analyze_stock_risk(self, df):
        """分析个股风险"""
        try:
            if df is None or df.empty:
                return None, []
            
            # 计算变化率
            df['融资余额变化率'] = df['rzye'].pct_change() * 100
            
            # 获取最新数据
            latest = df.iloc[-1]
            latest_change = latest['融资余额变化率']
            
            # 风险分析
            alerts = []
            risk_level = 'low'
            
            # 检查融资变化率
            if pd.notna(latest_change):
                if latest_change > self.risk_thresholds['stock_change_rate_high']:
                    alerts.append(f"⚠️ 融资激增 {latest_change:.2f}%：建议减仓，杠杆风险放大")
                    risk_level = 'high'
                    logger.warning(f"  {df.iloc[0].get('标的证券代码', 'N/A')} 融资激增: {latest_change:.2f}%")
                elif latest_change < self.risk_thresholds['stock_change_rate_low']:
                    alerts.append(f"⚠️ 融资骤降 {latest_change:.2f}%：资金流出，注意风险")
                    risk_level = 'medium'
                    logger.warning(f"  {df.iloc[0].get('标的证券代码', 'N/A')} 融资骤降: {latest_change:.2f}%")
                else:
                    logger.info(f"  {df.iloc[0].get('标的证券代码', 'N/A')} 融资变化正常: {latest_change:.2f}%")
            
            return latest, alerts, risk_level
            
        except Exception as e:
            logger.error(f"个股风险分析失败: {e}")
            return None, [], 'low'
    
    def analyze_market_risk(self, market_df):
        """分析市场风险"""
        try:
            if market_df is None or market_df.empty:
                return [], 'low'
            
            # 计算市场融资变化率
            market_df['融资余额变化率'] = market_df['rzye'].pct_change() * 100
            
            # 获取最新数据
            latest = market_df.iloc[-1]
            latest_change = latest['融资余额变化率']
            
            # 市场风险分析
            alerts = []
            market_risk_level = 'low'
            
            # 检查市场融资变化率
            if pd.notna(latest_change):
                if latest_change < self.risk_thresholds['market_change_rate_warning']:
                    alerts.append(f"⚠️ 市场融资变化率 {latest_change:.2f}%：杠杆去化，全局警报")
                    market_risk_level = 'high'
                    logger.warning(f"市场融资变化率: {latest_change:.2f}%（全局警报）")
                else:
                    logger.info(f"市场融资变化率: {latest_change:.2f}%（正常）")
            
            return alerts, market_risk_level
            
        except Exception as e:
            logger.error(f"市场风险分析失败: {e}")
            return [], 'low'
    
    def filter_stocks_by_margin(self, stocks_data):
        """根据两融数据过滤股票"""
        try:
            logger.info("\n【步骤3】根据两融数据过滤股票")
            logger.info("="*80)
            
            filtered_stocks = []
            
            for stock_code, data in stocks_data.items():
                if data['df'] is None or data['df'].empty:
                    continue
                
                df = data['df']
                latest = df.iloc[-1]
                
                # 计算融资增长
                if len(df) >= 2:
                    growth = (latest['rzye'] - df.iloc[-2]['rzye']) / df.iloc[-2]['rzye'] * 100
                else:
                    growth = 0.0
                
                # 判断融资余额是否增长
                if growth > self.risk_thresholds['margin_growth_positive']:
                    filtered_stocks.append({
                        'stock_code': stock_code,
                        'growth': growth,
                        'margin': latest['rzye'],
                        'source': data['source'],
                        'reason': f'融资余额增长 {growth:.2f}%，优先考虑'
                    })
                    logger.info(f"  ✓ {stock_code}: 融资增长 {growth:.2f}%")
                else:
                    logger.info(f"  ✗ {stock_code}: 融资下降 {growth:.2f}%，过滤掉")
            
            return filtered_stocks
            
        except Exception as e:
            logger.error(f"股票过滤失败: {e}")
            return []
    
    def run_risk_control_analysis(self, stock_list):
        """运行风控分析"""
        try:
            logger.info("\n" + "="*80)
            logger.info("选股策略风控分析")
            logger.info("="*80)
            logger.info(f"分析时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"股票列表: {len(stock_list)} 只")
            logger.info("="*80)
            
            # 步骤1: 获取所有股票的两融数据
            logger.info("\n【步骤1】获取股票两融数据")
            logger.info("-"*80)
            
            stocks_data = {}
            for stock_code in stock_list:
                df, source = self.get_stock_margin_data(stock_code)
                stocks_data[stock_code] = {
                    'df': df,
                    'source': source
                }
            
            # 步骤2: 分析个股风险
            logger.info("\n【步骤2】分析个股风险")
            logger.info("-"*80)
            
            stock_risks = {}
            for stock_code, data in stocks_data.items():
                latest, alerts, risk_level = self.analyze_stock_risk(data['df'])
                stock_risks[stock_code] = {
                    'latest': latest,
                    'alerts': alerts,
                    'risk_level': risk_level,
                    'source': data['source']
                }
            
            # 步骤3: 获取市场数据并分析市场风险
            logger.info("\n【步骤3】获取市场两融数据并分析市场风险")
            logger.info("-"*80)
            
            market_df, market_source = fetch_margin_data()
            market_alerts, market_risk_level = self.analyze_market_risk(market_df)
            
            # 步骤4: 根据两融数据过滤股票
            logger.info("\n【步骤4】根据两融数据过滤股票")
            logger.info("-"*80)
            
            filtered_stocks = self.filter_stocks_by_margin(stocks_data)
            
            # 步骤5: 生成风控报告
            logger.info("\n【步骤5】生成风控报告")
            logger.info("-"*80)
            
            self.generate_risk_report(
                stock_risks, 
                market_alerts, 
                market_risk_level,
                filtered_stocks
            )
            
            # 总结
            logger.info("\n" + "="*80)
            logger.info("风控分析总结")
            logger.info("="*80)
            logger.info(f"股票数量: {len(stock_list)}")
            logger.info(f"高风险股票: {len([s for s in stock_risks.values() if s['risk_level'] == 'high'])}")
            logger.info(f"中风险股票: {len([s for s in stock_risks.values() if s['risk_level'] == 'medium'])}")
            logger.info(f"低风险股票: {len([s for s in stock_risks.values() if s['risk_level'] == 'low'])}")
            logger.info(f"市场风险等级: {market_risk_level}")
            logger.info(f"市场警报: {len(market_alerts)}")
            logger.info(f"融资增长股票: {len(filtered_stocks)}")
            logger.info("="*80)
            
            return True
            
        except Exception as e:
            logger.error(f"风控分析异常: {e}")
            return False
    
    def generate_risk_report(self, stock_risks, market_alerts, market_risk_level, filtered_stocks):
        """生成风控报告"""
        try:
            import os
            os.makedirs('output', exist_ok=True)
            
            # 生成报告文本
            report = f"""{'='*80}
选股策略风控报告
{'='*80}

【基本信息】
生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
分析股票数量: {len(stock_risks)}

{'='*80}

【市场风险分析】"""
            
            # 市场风险等级
            risk_level_map = {
                'low': '低风险',
                'medium': '中风险',
                'high': '高风险'
            }
            
            report += f"\n市场风险等级: {risk_level_map.get(market_risk_level, '未知')}\n"
            
            if market_alerts:
                report += "\n市场警报:\n"
                for alert in market_alerts:
                    report += f"  - {alert}\n"
            else:
                report += "\n市场警报: 无\n"
            
            report += f"\n{'='*80}\n"
            
            # 个股风险分析
            report += "【个股风险分析】\n"
            
            high_risk_stocks = []
            medium_risk_stocks = []
            low_risk_stocks = []
            
            for stock_code, risk_data in stock_risks.items():
                risk_level = risk_data['risk_level']
                alerts = risk_data['alerts']
                latest = risk_data['latest']
                
                if risk_level == 'high':
                    high_risk_stocks.append((stock_code, risk_data))
                elif risk_level == 'medium':
                    medium_risk_stocks.append((stock_code, risk_data))
                else:
                    low_risk_stocks.append((stock_code, risk_data))
            
            if high_risk_stocks:
                report += "\n高风险股票（建议减仓）:\n"
                for stock_code, risk_data in high_risk_stocks:
                    report += f"\n  {stock_code}:\n"
                    for alert in risk_data['alerts']:
                        report += f"    - {alert}\n"
            
            if medium_risk_stocks:
                report += "\n中风险股票:\n"
                for stock_code, risk_data in medium_risk_stocks:
                    report += f"\n  {stock_code}:\n"
                    for alert in risk_data['alerts']:
                        report += f"    - {alert}\n"
            
            if low_risk_stocks:
                report += "\n低风险股票:\n"
                for stock_code in low_risk_stocks:
                    report += f"  - {stock_code}\n"
            
            report += f"\n{'='*80}\n"
            
            # 过滤后的股票
            report += "【推荐股票（融资余额增长）】\n"
            
            if filtered_stocks:
                for stock_info in filtered_stocks:
                    report += f"\n  {stock_info['stock_code']}\n"
                    report += f"    融资余额增长: {stock_info['growth']:.2f}%\n"
                    report += f"    融资余额: {stock_info['margin']/1e8:.2f} 亿元\n"
                    report += f"    数据源: {stock_info['source']}\n"
                    report += f"    推荐理由: {stock_info['reason']}\n"
            else:
                report += "  无融资增长的股票\n"
            
            report += f"\n{'='*80}\n"
            
            # 投资建议
            report += "【投资建议】\n\n"
            
            if market_risk_level == 'high':
                report += "⚠️ 市场处于高杠杆去化状态\n"
                report += "  建议全局观望，减少仓位\n"
                report += "  注意控制风险，保护本金\n"
            elif len(high_risk_stocks) > len(stock_risks) * 0.5:
                report += "⚠️ 多数股票处于高风险状态\n"
                report += "  建议减仓，降低杠杆\n"
                report += "  优先考虑低风险股票\n"
            elif filtered_stocks:
                report += "✓ 有融资余额增长的股票\n"
                report += f"  建议优先考虑: {', '.join([s['stock_code'] for s in filtered_stocks])}\n"
                report += "  融资增长代表资金关注\n"
            else:
                report += "  当前市场无明显机会\n"
                report += "  建议观望为主\n"
            
            report += f"\n{'='*80}\n"
            report += "【报告结束】\n"
            report += f"生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            report += f"{'='*80}\n"
            
            # 保存报告
            filepath = 'output/stock_selection_risk_control.txt'
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(f"✓ 风控报告已保存: {filepath}")
            
            # 打印报告摘要
            print(f"\n{report[:500]}...")
            
            return True
            
        except Exception as e:
            logger.error(f"报告生成失败: {e}")
            return False

# ========================================
# 主程序
# ========================================
if __name__ == '__main__':
    print("="*80)
    print("选股策略风控 - 卞董专用版本")
    print("="*80)
    print(f"测试时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print("测试股票:")
    for i, stock in enumerate(TEST_STOCKS, 1):
        print(f"  {i}. {stock}")
    print("="*80)
    
    # 创建风控系统
    risk_control = StockSelectionRiskControl()
    
    # 运行风控分析
    success = risk_control.run_risk_control_analysis(TEST_STOCKS)
    
    if success:
        print("\n" + "="*80)
        print("✓ 风控分析成功!")
        print("="*80)
        print("\n输出文件:")
        print("  1. 风控报告: output/stock_selection_risk_control.txt")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("✗ 风控分析失败!")
        print("="*80)
