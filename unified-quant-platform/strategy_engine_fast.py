#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""智能选股策略引擎 - 快速测试版（使用Mock数据）"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class StockSelector:
    """快速选股器 - 使用Mock数据测试"""

    def __init__(self, pro=None):
        self.today = datetime.now().strftime('%Y%m%d')

    def generate_mock_data(self, stock_code, days=60):
        """生成Mock历史数据"""
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        prices = []
        for i in range(days):
            base_price = random.uniform(10, 100)
            prices.append(base_price)

        df = pd.DataFrame({
            'trade_date': dates,
            'open': [p * random.uniform(0.98, 1.02) for p in prices],
            'high': [p * random.uniform(1.0, 1.05) for p in prices],
            'low': [p * random.uniform(0.95, 1.0) for p in prices],
            'close': prices,
            'vol': [random.randint(100000, 1000000) for _ in range(days)],
            'pre_close': [prices[i-1] if i > 0 else prices[i] for i in range(days)]
        })
        return df

    def calculate_indicators(self, df):
        """计算技术指标"""
        df = df.sort_values('trade_date').reset_index(drop=True)

        # MA均线
        df['ma5'] = df['close'].rolling(window=5).mean()
        df['ma10'] = df['close'].rolling(window=10).mean()
        df['ma20'] = df['close'].rolling(window=20).mean()

        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        # MACD
        df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema26'] = df['close'].ewm(span=26, adjust=False).mean()
        df['dif'] = df['ema12'] - df['ema26']
        df['dea'] = df['dif'].ewm(span=9, adjust=False).mean()
        df['macd'] = (df['dif'] - df['dea']) * 2

        # KDJ
        low_list = df['low'].rolling(window=9, min_periods=1).min()
        high_list = df['high'].rolling(window=9, min_periods=1).max()
        rsv = (df['close'] - low_list) / (high_list - low_list) * 100
        df['k'] = rsv.ewm(com=2, adjust=False).mean()
        df['d'] = df['k'].ewm(com=2, adjust=False).mean()
        df['j'] = 3 * df['k'] - 2 * df['d']

        return df

    def trend_strategy(self, stock_code, days=60):
        """趋势策略"""
        try:
            df = self.generate_mock_data(stock_code, days)
            df = self.calculate_indicators(df)
            latest = df.iloc[-1]

            score = 0
            reasons = []

            if latest['ma5'] > latest['ma10'] > latest['ma20']:
                score += 30
                reasons.append("均线多头排列")

            if latest['close'] > latest['ma20'] * 1.02:
                score += 20
                reasons.append("突破20日线")

            if df.iloc[-1]['ma20'] > df.iloc[-5]['ma20']:
                score += 15
                reasons.append("20日线向上")

            return score, "；".join(reasons) if reasons else "无明显信号"

        except Exception as e:
            return 0, f"趋势策略异常: {str(e)}"

    def momentum_strategy(self, stock_code, days=30):
        """动量策略"""
        try:
            df = self.generate_mock_data(stock_code, days)
            df = self.calculate_indicators(df)
            latest = df.iloc[-1]

            score = 0
            reasons = []

            if 50 < latest['rsi'] < 70:
                score += 25
                reasons.append(f"RSI强势({latest['rsi']:.1f})")

            if latest['k'] > latest['d'] and df.iloc[-2]['k'] <= df.iloc[-2]['d']:
                score += 20
                reasons.append("KDJ金叉")

            return score, "；".join(reasons) if reasons else "无明显信号"

        except Exception as e:
            return 0, f"动量策略异常: {str(e)}"

    def volume_strategy(self, stock_code, days=30):
        """量能策略"""
        try:
            df = self.generate_mock_data(stock_code, days)
            df = self.calculate_indicators(df)
            latest = df.iloc[-1]

            score = 0
            reasons = []

            # Mock量能指标
            vol_ratio = random.uniform(1.0, 2.5)
            if vol_ratio > 1.5:
                score += 30
                reasons.append(f"放量({vol_ratio:.1f}倍)")

            turnover = random.uniform(3, 12)
            if 3 < turnover < 10:
                score += 20
                reasons.append(f"换手率适中({turnover:.1f}%)")

            return score, "；".join(reasons) if reasons else "无明显信号"

        except Exception as e:
            return 0, f"量能策略异常: {str(e)}"

    def technical_strategy(self, stock_code, days=30):
        """技术指标策略"""
        try:
            df = self.generate_mock_data(stock_code, days)
            df = self.calculate_indicators(df)
            latest = df.iloc[-1]

            score = 0
            reasons = []

            # MACD金叉
            if latest['macd'] > 0:
                score += 35
                reasons.append("MACD金叉")

            if df.iloc[-3]['k'] < 20 and latest['k'] > 20:
                score += 30
                reasons.append("KDJ超卖反弹")

            return score, "；".join(reasons) if reasons else "无明显信号"

        except Exception as e:
            return 0, f"技术策略异常: {str(e)}"

    def composite_strategy(self, stock_code):
        """综合策略"""
        try:
            scores = {}
            all_reasons = []

            # 执行各策略
            for name, strategy_func in [
                ('trend', self.trend_strategy),
                ('momentum', self.momentum_strategy),
                ('volume', self.volume_strategy),
                ('technical', self.technical_strategy)
            ]:
                score, reasons = strategy_func(stock_code)
                scores[name] = score
                if reasons and "异常" not in reasons:
                    all_reasons.append(f"[{name}] {reasons}")

            # 加权综合评分
            weights = {
                'trend': 0.30,
                'momentum': 0.25,
                'volume': 0.20,
                'technical': 0.25
            }

            total_score = sum(scores[k] * weights[k] for k in weights)

            # 综合评分等级
            if total_score >= 50:
                level = "强烈推荐"
                level_score = 5
            elif total_score >= 30:
                level = "推荐"
                level_score = 4
            elif total_score >= 10:
                level = "关注"
                level_score = 3
            elif total_score >= -10:
                level = "中性"
                level_score = 2
            else:
                level = "回避"
                level_score = 1

            return total_score, level, level_score, " | ".join(all_reasons)

        except Exception as e:
            return 0, "数据异常", 1, str(e)

    def get_mock_stock_list(self, count=50):
        """生成Mock股票列表"""
        stocks = [
            ('600519.SH', '贵州茅台', '消费'),
            ('000858.SZ', '五粮液', '消费'),
            ('601318.SH', '中国平安', '金融'),
            ('600036.SH', '招商银行', '金融'),
            ('000651.SZ', '格力电器', '家电'),
            ('002594.SZ', '比亚迪', '汽车'),
            ('601888.SH', '中国中免', '消费'),
            ('600276.SH', '恒瑞医药', '医药'),
            ('300750.SZ', '宁德时代', '新能源'),
            ('601012.SH', '隆基绿能', '新能源'),
            ('600900.SH', '长江电力', '电力'),
            ('601390.SH', '中国中铁', '基建'),
            ('002415.SZ', '海康威视', '科技'),
            ('600031.SH', '三一重工', '机械'),
            ('000725.SZ', '京东方A', '科技'),
            ('601628.SH', '人寿保险', '金融'),
            ('000063.SZ', '中兴通讯', '科技'),
            ('600519.SH', '贵州茅台', '消费'),
            ('601919.SH', '中远海控', '航运'),
        ]
        return stocks[:count]

    def scan_market(self, max_stocks=20, min_score=20):
        """快速扫描（使用Mock数据）"""
        print(f"🔍 快速扫描: {max_stocks} 只股票...")

        stock_list = self.get_mock_stock_list(max_stocks)
        results = []

        for i, (ts_code, name, industry) in enumerate(stock_list):
            print(f"📊 进度: {i+1}/{len(stock_list)} - {name}")

            try:
                score, level, level_score, reasons = self.composite_strategy(ts_code)

                if score >= min_score:
                    results.append({
                        'ts_code': ts_code,
                        'symbol': ts_code.replace('.SH', '').replace('.SZ', ''),
                        'name': name,
                        'industry': industry,
                        'price': round(random.uniform(10, 100), 2),
                        'pct_chg': round(random.uniform(-5, 10), 2),
                        'vol': random.randint(100000, 1000000),
                        'amount': round(random.uniform(10000000, 100000000), 2),
                        'score': score,
                        'level': level,
                        'level_score': level_score,
                        'reasons': reasons
                    })
            except Exception as e:
                continue

        results.sort(key=lambda x: x['score'], reverse=True)
        print(f"✅ 扫描完成: 找到 {len(results)} 只股票")

        return results

    def generate_report(self, stocks):
        """生成选股报告"""
        if not stocks:
            return "未找到符合条件的股票"

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        report = f"""
{'='*80}
📊 AnqingA股大师 - 智能选股报告（快速测试版）
{'='*80}
⏰ 生成时间: {now}
🎯 选股策略: 8因子综合评分系统
📈 筛选标准: 综合评分 >= 20分

{'='*80}
📋 强烈推荐（5星）：
{'='*80}
"""
        level_5 = [s for s in stocks if s['level_score'] == 5]
        if level_5:
            for s in level_5:
                report += f"""
📌 {s['name']} ({s['symbol']})
💰 价格: {s['price']:.2f}  📈 涨跌: {s['pct_chg']:+.2f}%
🎯 综合评分: {s['score']:.1f}分
💡 信号: {s['reasons']}
"""
        else:
            report += "无\n"

        report += f"\n{'='*80}\n📋 推荐（4星）：\n{'='*80}\n"
        level_4 = [s for s in stocks if s['level_score'] == 4]
        if level_4:
            for s in level_4:
                report += f"""
📌 {s['name']} ({s['symbol']})
💰 价格: {s['price']:.2f}  📈 涨跌: {s['pct_chg']:+.2f}%
🎯 综合评分: {s['score']:.1f}分
💡 信号: {s['reasons']}
"""
        else:
            report += "无\n"

        report += f"\n{'='*80}\n📋 关注（3星）：\n{'='*80}\n"
        level_3 = [s for s in stocks if s['level_score'] == 3]
        if level_3:
            for s in level_3:
                report += f"""
📌 {s['name']} ({s['symbol']})
💰 价格: {s['price']:.2f}  📈 涨跌: {s['pct_chg']:+.2f}%
🎯 综合评分: {s['score']:.1f}分
"""
        else:
            report += "无\n"

        report += f"\n{'='*80}\n📊 统计信息\n{'='*80}\n"
        report += f"✅ 总计扫描: {len(stocks)} 只股票\n"
        report += f"⭐ 强烈推荐: {len(level_5)} 只\n"
        report += f"⭐ 推荐: {len(level_4)} 只\n"
        report += f"⭐ 关注: {len(level_3)} 只\n"
        report += f"{'='*80}\n"

        return report
