#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""智能选股策略引擎 - 整合多维度指标"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tushare as ts

class StockSelector:
    """智能选股器 - 基于8因子信号系统"""

    def __init__(self, pro):
        self.pro = pro
        self.today = datetime.now().strftime('%Y%m%d')
        self.strategies = {
            'trend': self.trend_strategy,
            'momentum': self.momentum_strategy,
            'volume': self.volume_strategy,
            'technical': self.technical_strategy,
            'composite': self.composite_strategy  # 综合策略
        }

    def get_stock_list(self):
        """获取A股列表"""
        try:
            df = self.pro.stock_basic(exchange='', list_status='L',
                                     fields='ts_code,symbol,name,area,industry,list_date')
            return df
        except Exception as e:
            print(f"获取股票列表失败: {e}")
            return pd.DataFrame()

    def calculate_indicators(self, df):
        """计算技术指标"""
        df = df.sort_values('trade_date').reset_index(drop=True)

        # MA均线
        df['ma5'] = df['close'].rolling(window=5).mean()
        df['ma10'] = df['close'].rolling(window=10).mean()
        df['ma20'] = df['close'].rolling(window=20).mean()
        df['ma60'] = df['close'].rolling(window=60).mean()

        # 成交量均线
        df['vol_ma5'] = df['vol'].rolling(window=5).mean()
        df['vol_ma10'] = df['vol'].rolling(window=10).mean()

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

        # 量比
        df['vol_ratio'] = df['vol'] / df['vol_ma5']

        # 换手率
        df['turnover_rate'] = df['vol'] / df['vol_ma10'] * 100

        # 涨跌幅
        df['pct_chg'] = df['close'].pct_change() * 100

        return df

    def trend_strategy(self, stock_code, days=60):
        """趋势策略：均线多头排列 + 价格突破"""
        try:
            df = self.pro.daily(ts_code=stock_code, start_date=
                              (datetime.now() - timedelta(days=days+10)).strftime('%Y%m%d'),
                              end_date=self.today)
            if df.empty or len(df) < 20:
                return 0, "数据不足"

            df = self.calculate_indicators(df)
            latest = df.iloc[-1]

            score = 0
            reasons = []

            # 均线多头排列
            if latest['ma5'] > latest['ma10'] > latest['ma20']:
                score += 30
                reasons.append("均线多头排列")
            else:
                score -= 10

            # 价格突破MA20
            if latest['close'] > latest['ma20'] * 1.02:
                score += 20
                reasons.append("突破20日线")
            elif latest['close'] < latest['ma20'] * 0.98:
                score -= 20

            # MA20向上
            if df.iloc[-1]['ma20'] > df.iloc[-5]['ma20']:
                score += 15
                reasons.append("20日线向上")

            # 最近5日涨幅
            recent_gain = (df.iloc[-1]['close'] / df.iloc[-5]['close'] - 1) * 100
            if 0 < recent_gain < 5:
                score += 15
            elif recent_gain > 10:
                score -= 10  # 避免追高

            # 振幅控制
            amplitude = (latest['high'] - latest['low']) / latest['close'] * 100
            if amplitude < 8:
                score += 10
            else:
                score -= 5

            return score, "；".join(reasons) if reasons else "无明显信号"

        except Exception as e:
            return 0, f"趋势策略异常: {str(e)}"

    def momentum_strategy(self, stock_code, days=30):
        """动量策略：量价齐升 + RSI强势"""
        try:
            df = self.pro.daily(ts_code=stock_code, start_date=
                              (datetime.now() - timedelta(days=days+10)).strftime('%Y%m%d'),
                              end_date=self.today)
            if df.empty or len(df) < 15:
                return 0, "数据不足"

            df = self.calculate_indicators(df)
            latest = df.iloc[-1]

            score = 0
            reasons = []

            # RSI强势区间
            if 50 < latest['rsi'] < 70:
                score += 25
                reasons.append(f"RSI强势({latest['rsi']:.1f})")
            elif latest['rsi'] >= 70:
                score -= 15  # 超买风险
            elif latest['rsi'] < 40:
                score -= 20

            # 量价齐升
            if latest['close'] > df.iloc[-3]['close'] and latest['vol'] > df.iloc[-3]['vol']:
                score += 25
                reasons.append("量价齐升")

            # 连续上涨
            if (df.iloc[-1]['close'] > df.iloc[-2]['close'] and
                df.iloc[-2]['close'] > df.iloc[-3]['close']):
                score += 15
                reasons.append("连续上涨")

            # KDJ金叉
            if latest['k'] > latest['d'] and df.iloc[-2]['k'] <= df.iloc[-2]['d']:
                score += 20
                reasons.append("KDJ金叉")

            return score, "；".join(reasons) if reasons else "无明显信号"

        except Exception as e:
            return 0, f"动量策略异常: {str(e)}"

    def volume_strategy(self, stock_code, days=30):
        """量能策略：放量突破 + 筹码集中"""
        try:
            df = self.pro.daily(ts_code=stock_code, start_date=
                              (datetime.now() - timedelta(days=days+10)).strftime('%Y%m%d'),
                              end_date=self.today)
            if df.empty or len(df) < 10:
                return 0, "数据不足"

            df = self.calculate_indicators(df)
            latest = df.iloc[-1]

            score = 0
            reasons = []

            # 放量
            if latest['vol'] > latest['vol_ma5'] * 1.5:
                score += 30
                reasons.append(f"放量({latest['vol'] / latest['vol_ma5']:.1f}倍)")
            elif latest['vol'] < latest['vol_ma5'] * 0.5:
                score -= 15

            # 换手率适中
            if 3 < latest['turnover_rate'] < 10:
                score += 20
                reasons.append(f"换手率适中({latest['turnover_rate']:.1f}%)")
            elif latest['turnover_rate'] > 15:
                score -= 10

            # 成交额活跃
            avg_amount_10 = df['amount'].tail(10).mean()
            if latest['amount'] > avg_amount_10 * 1.2:
                score += 20
                reasons.append("成交额活跃")

            # 量能持续
            if (df.iloc[-1]['vol'] > df.iloc[-2]['vol'] and
                df.iloc[-2]['vol'] > df.iloc[-3]['vol']):
                score += 15
                reasons.append("量能持续放大")

            return score, "；".join(reasons) if reasons else "无明显信号"

        except Exception as e:
            return 0, f"量能策略异常: {str(e)}"

    def technical_strategy(self, stock_code, days=30):
        """技术指标策略：MACD + KDJ组合"""
        try:
            df = self.pro.daily(ts_code=stock_code, start_date=
                              (datetime.now() - timedelta(days=days+10)).strftime('%Y%m%d'),
                              end_date=self.today)
            if df.empty or len(df) < 30:
                return 0, "数据不足"

            df = self.calculate_indicators(df)
            latest = df.iloc[-1]

            score = 0
            reasons = []

            # MACD金叉
            if latest['macd'] > 0 and df.iloc[-2]['macd'] <= 0:
                score += 35
                reasons.append("MACD金叉")
            elif latest['macd'] > 0:
                score += 10
                reasons.append("MACD红柱")

            # KDJ超卖反弹
            if df.iloc[-3]['k'] < 20 and latest['k'] > 20:
                score += 30
                reasons.append("KDJ超卖反弹")

            # 布林突破（简化版）
            std = df['close'].tail(20).std()
            ma20 = df['close'].tail(20).mean()
            upper = ma20 + 2 * std
            lower = ma20 - 2 * std

            if latest['close'] > upper * 0.98:
                score += 20
                reasons.append("突破上轨")
            elif latest['close'] < lower * 1.02:
                score -= 15

            # MACD背离检测
            if (df.iloc[-1]['close'] < df.iloc[-5]['close'] and
                df.iloc[-1]['macd'] > df.iloc[-5]['macd']):
                score += 25
                reasons.append("MACD底背离")

            return score, "；".join(reasons) if reasons else "无明显信号"

        except Exception as e:
            return 0, f"技术策略异常: {str(e)}"

    def composite_strategy(self, stock_code):
        """综合策略：整合所有策略评分"""
        try:
            scores = {}
            all_reasons = []

            # 执行各策略
            for name, strategy_func in self.strategies.items():
                if name == 'composite':
                    continue
                score, reasons = strategy_func(stock_code)
                scores[name] = score
                if reasons and "异常" not in reasons:
                    all_reasons.append(f"[{name}] {reasons}")

            # 加权综合评分
            weights = {
                'trend': 0.30,      # 趋势最重要
                'momentum': 0.25,   # 动量次之
                'volume': 0.20,    # 量能支撑
                'technical': 0.25   # 技术确认
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

    def scan_market(self, max_stocks=100, min_score=20):
        """全市场扫描"""
        print("🔄 开始全市场扫描...")
        stock_list = self.get_stock_list()

        if stock_list.empty:
            print("❌ 无法获取股票列表")
            return []

        results = []
        scanned = 0

        for _, stock in stock_list.head(max_stocks).iterrows():
            try:
                scanned += 1
                if scanned % 10 == 0:
                    print(f"📊 已扫描 {scanned}/{max_stocks} 只股票...")

                score, level, level_score, reasons = self.composite_strategy(stock['ts_code'])

                if score >= min_score:
                    # 获取实时数据
                    try:
                        df_today = self.pro.daily(ts_code=stock['ts_code'],
                                                 start_date=self.today,
                                                 end_date=self.today)
                        if not df_today.empty:
                            latest = df_today.iloc[0]
                            results.append({
                                'ts_code': stock['ts_code'],
                                'symbol': stock['symbol'],
                                'name': stock['name'],
                                'industry': stock['industry'],
                                'price': latest['close'],
                                'pct_chg': latest['pct_chg'],
                                'vol': latest['vol'],
                                'amount': latest['amount'],
                                'score': round(score, 2),
                                'level': level,
                                'level_score': level_score,
                                'reasons': reasons
                            })
                    except:
                        pass

            except Exception as e:
                continue

        # 按评分排序
        results.sort(key=lambda x: x['score'], reverse=True)

        print(f"✅ 扫描完成: 找到 {len(results)} 只符合条件的股票")
        return results

    def generate_report(self, stocks):
        """生成选股报告"""
        if not stocks:
            return "未找到符合条件的股票"

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        report = f"""
{'='*80}
📊 AnqingA股大师 - 智能选股报告
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


if __name__ == '__main__':
    import sys
    sys.path.insert(0, '/root/.openclaw/workspace/unified-quant-platform')

    from real_data_app import TUSHARE_TOKEN

    ts.set_token(TUSHARE_TOKEN)
    pro = ts.pro_api()

    selector = StockSelector(pro)

    # 测试单只股票
    print("\n🔍 测试趋势策略:")
    score, reasons = selector.trend_strategy('600519.SH')
    print(f"贵州茅台: {score}分 - {reasons}")

    print("\n🔍 测试动量策略:")
    score, reasons = selector.momentum_strategy('600519.SH')
    print(f"贵州茅台: {score}分 - {reasons}")

    print("\n🔍 测试量能策略:")
    score, reasons = selector.volume_strategy('600519.SH')
    print(f"贵州茅台: {score}分 - {reasons}")

    print("\n🔍 测试技术策略:")
    score, reasons = selector.technical_strategy('600519.SH')
    print(f"贵州茅台: {score}分 - {reasons}")

    print("\n🔍 测试综合策略:")
    score, level, level_score, reasons = selector.composite_strategy('600519.SH')
    print(f"贵州茅台: {score}分 | 等级: {level}({level_score}星)")
    print(f"信号: {reasons}")
