#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyzer v6 - 数据分析Agent - 分类分析版
支持6种资金分类分析：两融、南北向、机构、龙虎榜、个股、大宗
"""
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class Analyzer:
    """数据分析Agent - 分类分析版"""
    
    def __init__(self):
        self.name = "Analyzer"
        
        # 风险阈值配置
        self.thresholds = {
            'margin': {
                'stock_change_rate_high': 15.0,      # 个股融资变化率高阈值
                'stock_change_rate_low': -5.0,       # 个股融资变化率低阈值
                'market_change_rate_warning': -5.0,  # 市场融资变化率预警
                'margin_growth_positive': 0.0,       # 融资余额增长阈值
            },
            'north_south_funds': {
                'north_outflow_warning': 50.0,       # 北向净流出预警（亿元）
                'south_inflow_warning': 30.0,        # 南向流入预警（亿元）
                'north_inflow_warning': 50.0,        # 北向流入预警（亿元）
            },
            'institutional': {
                'inst_outflow_warning': 100.0,       # 机构流出预警（亿元）
                'large_buy_warning': 50000.0,        # 大额买入预警（万元）
                'buy_ratio_warning': 0.6,            # 买入比>60%预警
            },
            'lhb': {
                'hot_count_warning': 3,              # 热点数量预警（>3只）
                'buy_ratio_warning': 0.6,            # 买入比>60%预警
            },
            'stock_flow': {
                'main_inflow_warning': 10000.0,      # 主力净流入预警（万元）
                'retail_outflow_warning': -5000.0,   # 散户净流出预警（万元）
                'turnover_high_warning': 10.0,       # 换手率高预警（%）
            },
            'blocks': {
                'premium_warning': 20.0,              # 溢价率预警（%）
                'volume_warning': 10000,             # 成交量预警（万手）
                'discount_warning': -10.0,            # 折价率预警（%）
            }
        }
    
    def analyze_margin(self, df):
        """
        分析两融数据
        
        参数:
            df: 两融数据DataFrame
        
        返回:
            tuple: (分析后的DataFrame, 警报列表, 风险等级)
        """
        try:
            if df is None or df.empty:
                logger.warning("[Analyzer] 两融数据为空")
                return None, [], 'low'
            
            logger.info(f"[Analyzer] 开始分析两融数据，记录数: {len(df)}")
            
            # 1. 按日期排序
            df = df.sort_values('trade_date')
            
            # 2. 计算变化率
            if 'rzye' in df.columns:
                df['融资余额变化率'] = df['rzye'].pct_change() * 100
            
            # 3. 计算均线
            if 'rzye' in df.columns:
                df['融资余额_MA5'] = df['rzye'].rolling(5).mean()
                df['融资余额_MA10'] = df['rzye'].rolling(10).mean()
            
            # 4. 生成警报
            alerts = []
            latest = df.iloc[-1]
            
            # 检查融资余额变化率
            if '融资余额变化率' in df.columns:
                change_rate = latest.get('融资余额变化率', 0)
                
                if pd.notna(change_rate):
                    if change_rate > self.thresholds['margin']['stock_change_rate_high']:
                        alerts.append(f"⚠️ 融资余额激增 {change_rate:.2f}%：建议减仓，杠杆风险放大")
                        risk_level = 'high'
                        logger.warning(f"融资余额变化率过高: {change_rate:.2f}%")
                    elif change_rate < self.thresholds['margin']['stock_change_rate_low']:
                        alerts.append(f"⚠️ 融资余额骤降 {change_rate:.2f}%：资金流出，注意风险")
                        risk_level = 'medium'
                        logger.warning(f"融资余额变化率过低: {change_rate:.2f}%")
                    else:
                        logger.info(f"✓ 融资余额变化率正常: {change_rate:.2f}%")
                        risk_level = 'low'
            
            # 检查均线关系
            if '融资余额_MA5' in df.columns and '融资余额_MA10' in df.columns:
                ma5 = latest.get('融资余额_MA5', 0)
                ma10 = latest.get('融资余额_MA10', 0)
                
                if pd.notna(ma5) and pd.notna(ma10):
                    if ma5 > ma10:
                        logger.info(f"✓ MA5({ma5:.0f}) > MA10({ma10:.0f})：金叉，趋势向上")
                    elif ma5 < ma10:
                        logger.info(f"✓ MA5({ma5:.0f}) < MA10({ma10:.0f})：死叉，趋势向下")
                    else:
                        logger.info(f"✓ MA5 = MA10：横盘")
            
            logger.info(f"[Analyzer] 两融分析完成，发现 {len(alerts)} 条警报")
            return df, alerts, risk_level if 'risk_level' in locals() else 'low'
            
        except Exception as e:
            logger.error(f"[Analyzer] 两融分析失败: {e}")
            return None, [], 'low'
    
    def analyze_north_south_funds(self, df):
        """
        分析南北向资金
        
        参数:
            df: 南北向资金DataFrame
        
        返回:
            tuple: (分析后的DataFrame, 警报列表, 风险等级)
        """
        try:
            if df is None or df.empty:
                logger.warning("[Analyzer] 南北向资金为空")
                return None, [], 'low'
            
            logger.info(f"[Analyzer] 开始分析南北向资金，记录数: {len(df)}")
            
            # 1. 按日期排序
            df = df.sort_values('trade_date')
            
            # 2. 计算净流入
            if 'north_money' in df.columns and 'south_money' in df.columns:
                df['北向净流入'] = df['north_money']
                df['南向净流入'] = df['south_money']
                df['净流入'] = df['北向净流入'] - df['南向净流入']
            elif 'ggt_ss' in df.columns and 'ggt_sz' in df.columns:
                df['北向净流入'] = df['ggt_ss'] + df['ggt_sz']
                df['南向净流入'] = df.get('sgt_ss', 0) + df.get('sgt_sz', 0)
                df['净流入'] = df['北向净流入'] - df['南向净流入']
            
            # 3. 计算变化率
            if '北向净流入' in df.columns:
                df['北向变化率'] = df['北向净流入'].pct_change() * 100
            
            # 4. 计算均线
            if '北向净流入' in df.columns:
                df['北向MA5'] = df['北向净流入'].rolling(5).mean()
                df['北向MA10'] = df['北向净流入'].rolling(10).mean()
            
            # 5. 生成警报
            alerts = []
            latest = df.iloc[-1]
            
            # 检查北向净流入
            if '北向净流入' in df.columns:
                north_inflow = latest.get('北向净流入', 0)
                
                if pd.notna(north_inflow):
                    if north_inflow < -self.thresholds['north_south_funds']['north_outflow_warning']:
                        alerts.append(f"⚠️ 北向资金净流出 {abs(north_inflow):.2f}亿元：市场风险")
                        risk_level = 'high'
                        logger.warning(f"北向资金大幅净流出: {abs(north_inflow):.2f}亿元")
                    elif north_inflow > self.thresholds['north_south_funds']['north_inflow_warning']:
                        alerts.append(f"✅ 北向资金大幅净流入 {north_inflow:.2f}亿元：市场机会")
                        risk_level = 'low'
                        logger.info(f"北向资金大幅净流入: {north_inflow:.2f}亿元")
                    else:
                        logger.info(f"✓ 北向资金净流入: {north_inflow:.2f}亿元")
                        risk_level = 'low'
            
            # 检查趋势
            if '北向MA5' in df.columns and '北向MA10' in df.columns:
                ma5 = latest.get('北向MA5', 0)
                ma10 = latest.get('北向MA10', 0)
                
                if pd.notna(ma5) and pd.notna(ma10):
                    if ma5 > ma10:
                        logger.info(f"✓ 北向MA5({ma5:.2f}) > MA10({ma10:.2f})：金叉，趋势向上")
                    elif ma5 < ma10:
                        logger.info(f"✓ 北向MA5({ma5:.2f}) < MA10({ma10:.2f})：死叉，趋势向下")
            
            logger.info(f"[Analyzer] 南北向资金分析完成，发现 {len(alerts)} 条警报")
            return df, alerts, risk_level if 'risk_level' in locals() else 'low'
            
        except Exception as e:
            logger.error(f"[Analyzer] 南北向资金分析失败: {e}")
            return None, [], 'low'
    
    def analyze_institutional(self, df):
        """
        分析机构资金
        
        参数:
            df: 机构资金DataFrame
        
        返回:
            tuple: (分析后的DataFrame, 警报列表, 风险等级)
        """
        try:
            if df is None or df.empty:
                logger.warning("[Analyzer] 机构资金为空")
                return None, [], 'low'
            
            logger.info(f"[Analyzer] 开始分析机构资金，记录数: {len(df)}")
            
            # 1. 按券商分组统计
            if 'exalter' in df.columns or 'net_amount' in df.columns:
                # 按券商分组
                grouped = df.groupby('exalter').agg({
                    'buy_amt': 'sum',
                    'sell_amt': 'sum',
                    'net_amount': 'sum'
                }).reset_index()
                
                # 重命名列
                grouped.columns = ['券商', '买入额', '卖出额', '净买卖']
                
                # 计算买卖比
                grouped['买卖比'] = grouped['买入额'] / (grouped['卖出额'] + 1e-6)
                
                # 转换为万元
                grouped['买入额(万)'] = grouped['买入额'] / 10000
                grouped['卖出额(万)'] = grouped['卖出额'] / 10000
                grouped['净买卖(万)'] = grouped['净买卖'] / 10000
                
            else:
                logger.warning("[Analyzer] 机构资金缺少必要字段")
                grouped = df.copy()
            
            # 2. 生成警报
            alerts = []
            
            for idx, row in grouped.iterrows():
                broker = row.get('券商', '未知')
                buy_amount = row.get('买入额(万)', 0)
                sell_amount = row.get('卖出额(万)', 0)
                net_buy = row.get('净买卖(万)', 0)
                buy_ratio = row.get('买卖比', 0)
                
                # 大额买入预警
                if buy_amount > 50000:  # 5亿元
                    alerts.append(f"⚠️ {broker} 大额买入 {buy_amount:.2f}万元")
                    risk_level = 'high'
                    logger.warning(f"{broker} 大额买入: {buy_amount:.2f}万元")
                
                # 大额卖出预警
                if sell_amount > 30000:  # 3亿元
                    alerts.append(f"⚠️ {broker} 大额卖出 {sell_amount:.2f}万元")
                    risk_level = 'medium'
                    logger.warning(f"{broker} 大额卖出: {sell_amount:.2f}万元")
                
                # 买卖比预警
                if buy_ratio > self.thresholds['institutional']['buy_ratio_warning']:
                    alerts.append(f"⚠️ {broker} 买入比 {buy_ratio:.1%}：高控盘程度")
                    risk_level = 'high'
                    logger.warning(f"{broker} 买入比过高: {buy_ratio:.1%}")
            
            logger.info(f"[Analyzer] 机构资金分析完成，发现 {len(alerts)} 条警报")
            return grouped, alerts, risk_level if 'risk_level' in locals() else 'low'
            
        except Exception as e:
            logger.error(f"[Analyzer] 机构资金分析失败: {e}")
            return None, [], 'low'
    
    def analyze_lhb(self, df):
        """
        分析龙虎榜
        
        参数:
            df: 龙虎榜DataFrame
        
        返回:
            tuple: (分析后的DataFrame, 警报列表, 风险等级)
        """
        try:
            if df is None or df.empty:
                logger.warning("[Analyzer] 龙虎榜为空")
                return None, [], 'low'
            
            logger.info(f"[Analyzer] 开始分析龙虎榜，记录数: {len(df)}")
            
            # 1. 提取前5名
            top5 = df.head(5)
            
            # 2. 计算机构买入比例
            if 'buy_amount' in df.columns and 'total_amount' in df.columns:
                top5['机构买入比'] = top5['buy_amount'] / (top5['total_amount'] + 1e-6)
            elif 'lbuy' in df.columns and 'exalter' in df.columns:
                # 机构买入比例 = 机构买入额 / 总买入额
                top5['机构买入额'] = top5[top5['exalter'].str.contains('机构', na=False)]['lbuy'].sum()
                top5['总买入额'] = top5['lbuy'].sum()
                top5['机构买入比'] = top5['机构买入额'] / (top5['总买入额'] + 1e-6)
            
            # 3. 生成警报
            alerts = []
            
            # 热点数量预警
            if len(top5) > self.thresholds['lhb']['hot_count_warning']:
                alerts.append(f"⚠️ 龙虎榜热点股票 {len(top5)}只：市场过热")
                risk_level = 'medium'
                logger.warning(f"龙虎榜热点过多: {len(top5)}只")
            
            # 检查机构买入比例
            for idx, row in top5.iterrows():
                name = row.get('name', row.get('sec_name', '未知'))
                buy_ratio = row.get('机构买入比', 0)
                
                if pd.notna(buy_ratio) and buy_ratio > self.thresholds['lhb']['buy_ratio_warning']:
                    alerts.append(f"⚠️ {name} 机构买入比 {buy_ratio:.1%}：高控盘程度")
                    risk_level = 'high'
                    logger.warning(f"{name} 机构买入比过高: {buy_ratio:.1%}")
            
            logger.info(f"[Analyzer] 龙虎榜分析完成，发现 {len(alerts)} 条警报")
            return top5, alerts, risk_level if 'risk_level' in locals() else 'low'
            
        except Exception as e:
            logger.error(f"[Analyzer] 龙虎榜分析失败: {e}")
            return None, [], 'low'
    
    def analyze_stock_flow(self, df):
        """
        分析个股资金流
        
        参数:
            df: 个股资金流DataFrame
        
        返回:
            tuple: (分析后的DataFrame, 警报列表, 风险等级)
        """
        try:
            if df is None or df.empty:
                logger.warning("[Analyzer] 个股资金流为空")
                return None, [], 'low'
            
            logger.info(f"[Analyzer] 开始分析个股资金流，记录数: {len(df)}")
            
            # 1. 按股票代码分组
            if 'code' in df.columns:
                grouped = df.groupby('code').agg({
                    'main_inflow': 'sum',
                    'retail_inflow': 'sum',
                    'net_inflow': 'sum',
                    'turnover': 'mean',
                    'amount': 'sum'
                }).reset_index()
                
                # 重命名列
                grouped.columns = ['股票代码', '主力净流入', '散户净流入', '总净流入', '换手率', '成交额']
                
                # 转换单位
                grouped['主力净流入(万)'] = grouped['主力净流入'] / 10000
                grouped['散户净流入(万)'] = grouped['散户净流入'] / 10000
                grouped['总净流入(万)'] = grouped['总净流入'] / 10000
                grouped['成交额(万)'] = grouped['成交额'] / 10000
            else:
                logger.warning("[Analyzer] 个股资金流缺少code字段")
                grouped = df.copy()
            
            # 2. 生成警报
            alerts = []
            
            for idx, row in grouped.iterrows():
                code = row.get('股票代码', '未知')
                main_inflow = row.get('主力净流入(万)', 0)
                retail_inflow = row.get('散户净流入(万)', 0)
                turnover = row.get('换手率', 0)
                
                # 主力净流入预警
                if main_inflow > self.thresholds['stock_flow']['main_inflow_warning']:
                    alerts.append(f"⚠️ {code} 主力净流入 {main_inflow:.2f}万元")
                    risk_level = 'high'
                    logger.warning(f"{code} 主力大幅净流入: {main_inflow:.2f}万元")
                
                # 散户净流出预警
                if retail_inflow < self.thresholds['stock_flow']['retail_outflow_warning']:
                    alerts.append(f"⚠️ {code} 散户净流出 {abs(retail_inflow):.2f}万元")
                    risk_level = 'medium'
                    logger.warning(f"{code} 散户大幅净流出: {abs(retail_inflow):.2f}万元")
                
                # 换手率预警
                if pd.notna(turnover) and turnover > self.thresholds['stock_flow']['turnover_high_warning']:
                    alerts.append(f"⚠️ {code} 换手率 {turnover:.2f}%：高速换手")
                    risk_level = 'high'
                    logger.warning(f"{code} 换手率过高: {turnover:.2f}%")
                
                # 主力vs散户对比
                if main_inflow > 0 and retail_inflow < 0:
                    alerts.append(f"✅ {code} 主力流入({main_inflow:.2f}万) vs 散户流出({abs(retail_inflow):.2f}万)：主力主导")
                    logger.info(f"{code} 主力主导资金流向")
            
            logger.info(f"[Analyzer] 个股资金流分析完成，发现 {len(alerts)} 条警报")
            return grouped, alerts, risk_level if 'risk_level' in locals() else 'low'
            
        except Exception as e:
            logger.error(f"[Analyzer] 个股资金流分析失败: {e}")
            return None, [], 'low'
    
    def analyze_blocks(self, df):
        """
        分析大宗交易
        
        参数:
            df: 大宗交易DataFrame
        
        返回:
            tuple: (分析后的DataFrame, 警报列表, 风险等级)
        """
        try:
            if df is None or df.empty:
                logger.warning("[Analyzer] 大宗交易为空")
                return None, [], 'low'
            
            logger.info(f"[Analyzer] 开始分析大宗交易，记录数: {len(df)}")
            
            # 1. 计算溢价率
            if 'price' in df.columns and 'close' in df.columns:
                df['溢价率'] = ((df['price'] - df['close']) / df['close']) * 100
            
            # 2. 生成警报
            alerts = []
            
            for idx, row in df.iterrows():
                code = row.get('code', '未知')
                premium_rate = row.get('溢价率', 0)
                volume = row.get('volume', 0)
                
                # 溢价率预警
                if pd.notna(premium_rate) and premium_rate > self.thresholds['blocks']['premium_warning']:
                    alerts.append(f"⚠️ {code} 溢价率 {premium_rate:.2f}%：高溢价")
                    risk_level = 'medium'
                    logger.warning(f"{code} 溢价率过高: {premium_rate:.2f}%")
                
                # 折价预警
                if pd.notna(premium_rate) and premium_rate < self.thresholds['blocks']['discount_warning']:
                    alerts.append(f"⚠️ {code} 折价率 {abs(premium_rate):.2f}%：大幅折价")
                    risk_level = 'medium'
                    logger.warning(f"{code} 折价率过高: {abs(premium_rate):.2f}%")
                
                # 大宗成交量预警
                if pd.notna(volume) and volume > self.thresholds['blocks']['volume_warning']:
                    alerts.append(f"⚠️ {code} 大宗成交量 {volume:.2f}万手")
                    risk_level = 'high'
                    logger.warning(f"{code} 大宗成交量过大: {volume:.2f}万手")
            
            logger.info(f"[Analyzer] 大宗交易分析完成，发现 {len(alerts)} 条警报")
            return df, alerts, risk_level if 'risk_level' in locals() else 'low'
            
        except Exception as e:
            logger.error(f"[Analyzer] 大宗交易分析失败: {e}")
            return None, [], 'low'
    
    def predict_next_day(self, df, column='main_inflow'):
        """
        预测下一日数据（线性回归）
        
        参数:
            df: DataFrame
            column: 预测的列名
        
        返回:
            tuple: (预测值, 置信度)
        """
        try:
            if df is None or df.empty:
                return None, None
            
            if column not in df.columns:
                logger.warning(f"[Analyzer] 列不存在: {column}")
                return None, None
            
            # 过滤空值
            df_clean = df.dropna(subset=[column])
            
            if len(df_clean) < 5:
                logger.warning(f"[Analyzer] 数据量不足，无法预测: {len(df_clean)}")
                return None, None
            
            # 准备数据
            X = np.array(range(len(df_clean))).reshape(-1, 1)
            y = df_clean[column].values
            
            # 标准化
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # 线性回归
            model = LinearRegression()
            model.fit(X_scaled, y)
            
            # 预测下一日
            next_day_scaled = scaler.transform([[len(df_clean)]])
            prediction = model.predict(next_day_scaled)[0]
            
            # 计算置信度
            score = model.score(X_scaled, y)
            
            logger.info(f"[Analyzer] 预测完成: {prediction:.2f}, 置信度: {score:.2%}")
            
            return float(prediction), float(score)
            
        except Exception as e:
            logger.error(f"[Analyzer] 预测失败: {e}")
            return None, None
    
    def generate_comprehensive_report(self, analysis_results):
        """
        生成综合分析报告
        
        参数:
            analysis_results: 各资金类型的分析结果字典
        
        返回:
            str: 综合报告文本
        """
        try:
            report_lines = []
            report_lines.append("=" * 80)
            report_lines.append("资金监控综合分析报告")
            report_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append("=" * 80)
            report_lines.append("")
            
            # 各资金类型分析结果
            for fund_type, result in analysis_results.items():
                if result is None:
                    continue
                
                df, alerts, risk_level = result
                
                report_lines.append(f"\n【{fund_type.upper()}】风险等级: {risk_level.upper()}")
                report_lines.append("-" * 80)
                
                if alerts:
                    report_lines.append(f"\n警报 ({len(alerts)}条):")
                    for alert in alerts:
                        report_lines.append(f"  {alert}")
                else:
                    report_lines.append(f"\n✓ 无警报")
                
                if df is not None and not df.empty:
                    report_lines.append(f"\n数据统计:")
                    report_lines.append(f"  记录数: {len(df)}")
                    report_lines.append(f"  字段数: {len(df.columns)}")
            
            report_lines.append("\n" + "=" * 80)
            
            return "\n".join(report_lines)
            
        except Exception as e:
            logger.error(f"[Analyzer] 生成综合报告失败: {e}")
            return "报告生成失败"
