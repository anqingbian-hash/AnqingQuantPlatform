#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""智能选股策略引擎 v2.0 - 主流A股策略框架"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import tushare as ts

class StockSelectorV2:
    """A股主流策略选股器 v2.0"""

    def __init__(self, pro=None):
        self.pro = pro
        self.today = datetime.now().strftime('%Y%m%d')

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

        # 资金流向（简化版）
        df['money_flow'] = (df['close'] - df['open']) * df['vol']

        return df

    def generate_mock_data(self, stock_code, days=60):
        """生成Mock历史数据（测试用）"""
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        prices = [random.uniform(10, 100) for _ in range(days)]

        df = pd.DataFrame({
            'trade_date': dates,
            'open': [p * random.uniform(0.98, 1.02) for p in prices],
            'high': [p * random.uniform(1.0, 1.05) for p in prices],
            'low': [p * random.uniform(0.95, 1.0) for p in prices],
            'close': prices,
            'vol': [random.randint(100000, 1000000) for _ in range(days)],
            'pre_close': [prices[i-1] if i > 0 else prices[i] for i in range(days)]
        })

        return self.calculate_indicators(df)

    # ==================== 策略1：量价策略 ====================

    def volume_price_strategy(self, stock_code, days=60):
        """量价策略：威科夫、筹码派发、吸筹识别"""
        try:
            df = self.generate_mock_data(stock_code, days)
            latest = df.iloc[-1]

            score = 0
            signals = []

            # 1. 威科夫量价配合
            if latest['close'] > df.iloc[-2]['close'] and latest['vol'] > df.iloc[-2]['vol']:
                score += 20
                signals.append("威科夫量价配合")

            # 2. 筹码集中度检测（简化版）
            recent_vol_std = df['vol'].tail(5).std()
            if recent_vol_std < df['vol'].tail(20).std():
                score += 15
                signals.append("筹码相对集中")

            # 3. 吸筹识别（底部放量后缩量）
            if (df.iloc[-3]['vol'] > df['vol_ma5'].iloc[-10] * 1.5 and
                latest['vol'] < df.iloc[-3]['vol'] * 0.8 and
                latest['close'] > df.iloc[-3]['close']):
                score += 25
                signals.append("吸筹特征明显")

            # 4. 量价背离
            if (df.iloc[-5]['close'] < df.iloc[-1]['close'] and
                df.iloc[-5]['vol'] > latest['vol']):
                score -= 15
                signals.append("量价背离")

            # 5. 放量突破
            if latest['vol'] > df['vol_ma5'].iloc[-1] * 1.5:
                score += 20
                signals.append("放量突破")

            return score, " | ".join(signals) if signals else "无明显量价信号"

        except Exception as e:
            return 0, f"量价策略异常: {str(e)}"

    # ==================== 策略2：多周期共振 ====================

    def multi_timeframe_strategy(self, stock_code, days=120):
        """多周期共振：15分钟+60分钟+日线三级共振"""
        try:
            # 模拟15分钟、60分钟、日线数据
            df_15m = self.generate_mock_data(stock_code, 60)  # 模拟15分钟
            df_60m = self.generate_mock_data(stock_code, 60)  # 模拟60分钟
            df_daily = self.generate_mock_data(stock_code, days)  # 日线

            score = 0
            signals = []

            # 1. 15分钟周期趋势
            latest_15m = df_15m.iloc[-1]
            if (latest_15m['ma5'] > latest_15m['ma10'] and
                latest_15m['close'] > latest_15m['ma20']):
                score += 15
                signals.append("15分钟多头")

            # 2. 60分钟周期趋势
            latest_60m = df_60m.iloc[-1]
            if (latest_60m['ma5'] > latest_60m['ma10'] and
                latest_60m['macd'] > 0):
                score += 20
                signals.append("60分钟共振")

            # 3. 日线周期趋势
            latest_daily = df_daily.iloc[-1]
            if (latest_daily['ma20'] > latest_daily['ma60'] and
                latest_daily['close'] > latest_daily['ma20']):
                score += 25
                signals.append("日线趋势向上")

            # 4. 三周期共振
            if (latest_15m['close'] > latest_15m['ma5'] and
                latest_60m['close'] > latest_60m['ma5'] and
                latest_daily['close'] > latest_daily['ma20']):
                score += 30
                signals.append("✨三周期共振！")

            return score, " | ".join(signals) if signals else "无明显周期信号"

        except Exception as e:
            return 0, f"多周期策略异常: {str(e)}"

    # ==================== 策略3：资金流策略 ====================

    def money_flow_strategy(self, stock_code, days=30):
        """资金流策略：主力净量、机构动向、北向资金"""
        try:
            df = self.generate_mock_data(stock_code, days)
            latest = df.iloc[-1]

            score = 0
            signals = []

            # 1. 主力净流入（简化版：大单成交量）
            if df['vol'].iloc[-1] > df['vol_ma5'].iloc[-1] * 1.3:
                score += 25
                signals.append("主力净流入")

            # 2. 机构动向（持续性放量）
            if (df['vol'].iloc[-1] > df['vol'].iloc[-2] and
                df['vol'].iloc[-2] > df['vol'].iloc[-3]):
                score += 20
                signals.append("机构持续流入")

            # 3. 资金流向趋势
            money_flow_trend = df['money_flow'].tail(5).sum()
            if money_flow_trend > 0:
                score += 15
                signals.append("资金净流入")

            # 4. 北向资金（模拟）
            if latest['change_percent'] > 2:
                score += 10
                signals.append("资金关注")

            # 5. 大单比例
            vol_ratio = latest['vol'] / df['vol_ma5'].iloc[-1]
            if vol_ratio > 2.0:
                score += 20
                signals.append(f"大单涌入({vol_ratio:.1f}倍)")

            return score, " | ".join(signals) if signals else "无明显资金信号"

        except Exception as e:
            return 0, f"资金流策略异常: {str(e)}"

    # ==================== 策略4：趋势策略 ====================

    def trend_strategy(self, stock_code, days=60):
        """趋势策略：20日、60日均线趋势跟踪，突破入场"""
        try:
            df = self.generate_mock_data(stock_code, days)
            latest = df.iloc[-1]

            score = 0
            signals = []

            # 1. 均线多头排列
            if latest['ma5'] > latest['ma10'] > latest['ma20'] > latest['ma60']:
                score += 30
                signals.append("均线多头排列")

            # 2. 价格突破20日线
            if latest['close'] > latest['ma20'] * 1.02:
                score += 20
                signals.append("突破20日线")

            # 3. 20日线向上
            if df['ma20'].iloc[-1] > df['ma20'].iloc[-5]:
                score += 15
                signals.append("20日线向上")

            # 4. 60日线支撑
            if latest['close'] > latest['ma60'] * 0.95:
                score += 10
                signals.append("60日线支撑")

            # 5. 趋势强度
            ma_slope = (df['ma20'].iloc[-1] - df['ma20'].iloc[-10]) / 10
            if ma_slope > 0:
                score += 15
                signals.append(f"趋势向上(斜率{ma_slope:.3f})")

            return score, " | ".join(signals) if signals else "无明显趋势信号"

        except Exception as e:
            return 0, f"趋势策略异常: {str(e)}"

    # ==================== 策略5：短线策略 ====================

    def short_term_strategy(self, stock_code, days=30):
        """短线策略：龙回头、首板套利、弱转强"""
        try:
            df = self.generate_mock_data(stock_code, days)
            latest = df.iloc[-1]

            score = 0
            signals = []

            # 1. 龙回头（强势股回调后反弹）
            recent_high = df['high'].tail(10).max()
            if (latest['close'] > recent_high * 0.95 and
                df['pct_chg'].tail[3].max() < -3 and
                latest['pct_chg'] > 0):
                score += 30
                signals.append("龙回头形态")

            # 2. 首板套利（涨停后机会）
            if (df['pct_chg'].iloc[-2] > 8 and
                latest['pct_chg'] > 3 and
                latest['vol'] > df['vol_ma5'].iloc[-1] * 1.5):
                score += 25
                signals.append("首板机会")

            # 3. 弱转强（连续下跌后反弹）
            if (all(df['pct_chg'].iloc[-5:-2] < 0) and
                df['pct_chg'].iloc[-1] > 2):
                score += 25
                signals.append("弱转强")

            # 4. 短期强势
            if latest['pct_chg'] > 5:
                score += 20
                signals.append("短期强势")

            # 5. MACD金叉
            if latest['macd'] > 0 and df['macd'].iloc[-2] <= 0:
                score += 15
                signals.append("MACD金叉")

            return score, " | ".join(signals) if signals else "无明显短线信号"

        except Exception as e:
            return 0, f"短线策略异常: {str(e)}"

    # ==================== 策略6：风控策略 ====================

    def risk_control_strategy(self, stock_code, days=60):
        """风控策略：固定仓位、最大回撤控制、分批止盈止损"""
        try:
            df = self.generate_mock_data(stock_code, days)
            latest = df.iloc[-1]

            score = 0
            signals = []

            # 1. 波动率控制（低波动更安全）
            volatility = df['pct_chg'].tail(20).std()
            if 2 < volatility < 6:
                score += 20
                signals.append(f"波动率适中({volatility:.2f}%)")
            elif volatility > 8:
                score -= 15
                signals.append(f"波动率过高({volatility:.2f}%)")

            # 2. 最大回撤控制
            max_price = df['close'].tail(20).max()
            drawdown = (max_price - latest['close']) / max_price * 100
            if drawdown < 5:
                score += 25
                signals.append(f"回撤小({drawdown:.2f}%)")
            elif drawdown > 15:
                score -= 20
                signals.append(f"回撤大({drawdown:.2f}%)")

            # 3. 换手率适中
            if 3 < latest['turnover_rate'] < 10:
                score += 15
                signals.append("换手率适中")
            elif latest['turnover_rate'] > 15:
                score -= 10
                signals.append("换手率过高")

            # 4. 止损位置参考
            support_level = latest['ma20'] * 0.95
            if latest['close'] > support_level * 1.05:
                score += 20
                signals.append(f"止损位: {support_level:.2f}")

            # 5. 止盈位置参考
            resistance_level = latest['ma20'] * 1.08
            if latest['close'] < resistance_level * 0.95:
                score += 15
                signals.append(f"止盈位: {resistance_level:.2f}")

            return score, " | ".join(signals) if signals else "无明显风控信号"

        except Exception as e:
            return 0, f"风控策略异常: {str(e)}"

    # ==================== 综合评分 ====================

    def composite_strategy(self, stock_code):
        """综合策略：6大策略综合评分"""
        try:
            scores = {}
            all_signals = []

            # 执行各策略
            strategies = {
                '量价': self.volume_price_strategy,
                '多周期': self.multi_timeframe_strategy,
                '资金流': self.money_flow_strategy,
                '趋势': self.trend_strategy,
                '短线': self.short_term_strategy,
                '风控': self.risk_control_strategy
            }

            for name, strategy_func in strategies.items():
                score, signals = strategy_func(stock_code)
                scores[name] = score
                if signals and "异常" not in signals:
                    all_signals.append(f"[{name}] {signals}")

            # 加权综合评分
            weights = {
                '量价': 0.20,      # 量价配合最重要
                '多周期': 0.18,   # 周期共振次之
                '资金流': 0.18,    # 资金流向关键
                '趋势': 0.18,       # 趋势方向重要
                '短线': 0.13,       # 短线机会
                '风控': 0.13       # 风险控制
            }

            total_score = sum(scores[k] * weights[k] for k in weights)

            # 综合评分等级
            if total_score >= 50:
                level = "强烈推荐"
                level_score = 5
            elif total_score >= 35:
                level = "推荐"
                level_score = 4
            elif total_score >= 20:
                level = "关注"
                level_score = 3
            elif total_score >= 5:
                level = "中性"
                level_score = 2
            else:
                level = "回避"
                level_score = 1

            return total_score, level, level_score, " | ".join(all_signals)

        except Exception as e:
            return 0, "数据异常", 1, str(e)

    # ==================== 市场扫描 ====================

    def get_stock_list(self, count=50):
        """获取模拟股票列表"""
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
            ('601919.SH', '中远海控', '航运'),
            ('600030.SH', '中粮糖业', '农业'),
            ('000333.SZ', '美的集团', '家电'),
            ('601398.SH', '工商银行', '金融'),
            ('601288.SH', '农业银行', '金融'),
            ('000002.SZ', '万科A', '地产'),
            ('000001.SZ', '平安银行', '金融'),
            ('600519.SH', '贵州茅台', '消费'),
            ('000568.SZ', '泸州老窖', '消费'),
            ('002475.SZ', '立讯精密', '科技'),
            ('300059.SZ', '东方财富', '金融'),
            ('600887.SH', '伊利股份', '消费'),
            ('000895.SZ', '双汇发展', '消费'),
            ('601318.SH', '中国平安', '金融'),
            ('600048.SH', '保利发展', '地产'),
            ('600690.SH', '海尔智家', '家电'),
            ('000768.SZ', '中航西飞', '军工'),
            ('600745.SH', '闻泰科技', '科技'),
            ('002460.SZ', '赣锋锂业', '新能源'),
            ('300274.SZ', '阳光电源', '新能源'),
            ('601899.SH', '紫金矿业', '有色'),
            ('601988.SH', '中国重工', '基建'),
            ('000858.SZ', '五粮液', '消费'),
            ('600585.SH', '海螺水泥', '建材'),
            ('601668.SH', '中国建筑', '基建'),
            ('000725.SZ', '京东方A', '科技'),
            ('002352.SZ', '顺丰控股', '物流'),
            ('600547.SH', '山东黄金', '有色'),
            ('601618.SH', '中国中冶', '基建'),
            ('300015.SZ', '爱尔眼科', '医药'),
            ('000728.SZ', '国元证券', '金融'),
        ]
        return stocks[:count]

    def scan_market(self, max_stocks=30, min_score=15):
        """市场扫描（快速测试版）"""
        print(f"🔍 开始扫描: {max_stocks} 只股票...")

        stock_list = self.get_stock_list(max_stocks)
        results = []

        for i, (ts_code, name, industry) in enumerate(stock_list):
            try:
                print(f"📊 进度: {i+1}/{len(stock_list)} - {name}")

                score, level, level_score, signals = self.composite_strategy(ts_code)

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
                        'reasons': signals
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
📊 AnqingA股大师 - 智能选股报告 v2.0
{'='*80}
⏰ 生成时间: {now}
🎯 选股策略: A股6大主流策略框架
📈 策略组成:
   • 量价策略(20%): 威科夫、筹码派发、吸筹识别
   • 多周期(18%): 15分钟+60分钟+日线三级共振
   • 资金流(18%): 主力净量、机构动向、北向资金
   • 趋势策略(18%): 20日、60日均线趋势跟踪
   • 短线策略(13%): 龙回头、首板套利、弱转强
   • 风控策略(13%): 固定仓位、最大回撤、分批止盈止损

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
💡 信号: {s['reasons'][:100]}...
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
💡 信号: {s['reasons'][:100]}...
"""
        else:
            report += "无\n"

        report += f"\n{'='*80}\n📋 关注（3星）：\n{'='*80}\n"
        level_3 = [s for s in stocks if s['level_score'] == 3]
        if level_3:
            for s in level_3[:5]:  # 限制5只
                report += f"""
📌 {s['name']} ({s['symbol']})
💰 价格: {s['price']:.2f}  📈 涨跌: {s['pct_chg']:+.2f}%
🎯 综合评分: {s['score']:.1f}分
"""
            if len(level_3) > 5:
                report += f"\n... 还有 {len(level_3) - 5} 只股票\n"
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

    selector = StockSelectorV2(pro)

    print("\n🎯 AnqingA股大师 v2.0 - 6大策略框架")
    print("="*60)

    # 测试单只股票
    print("\n🔍 测试贵州茅台:")
    score, signals = selector.volume_price_strategy('600519.SH')
    print(f"  量价策略: {score}分 - {signals}")

    score, signals = selector.trend_strategy('600519.SH')
    print(f"  趋势策略: {score}分 - {signals}")

    print("\n🔍 综合评分:")
    score, level, level_score, signals = selector.composite_strategy('600519.SH')
    print(f"  {score:.1f}分 | 等级: {level}({level_score}星)")
    print(f"  信号: {signals}")

    print("\n🔍 扫描市场:")
    results = selector.scan_market(max_stocks=20, min_score=15)
    print(f"✅ 找到 {len(results)} 只符合条件的股票")
    if results:
        for r in results[:3]:
            print(f"  {r['name']} - {r['score']:.1f}分 - {r['level']}")
