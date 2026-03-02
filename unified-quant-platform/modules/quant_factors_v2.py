#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quant Trading 8因子系统 v2.0
完整的8个因子计算，用于量化分析
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class QuantFactorsV2:
    """Quant Trading 8因子系统 v2.0"""

    def __init__(self):
        """初始化8因子系统"""
        print("="*70)
        print("Quant Trading 8因子系统 v2.0 - 初始化")
        print("="*70)
        print("✅ 动量因子（Momentum）")
        print("✅ 均线偏离因子（MA Deviation）")
        print("✅ 成交量趋势因子（Volume Trend）")
        print("✅ 波动率因子（Volatility）")
        print("✅ RSI 因子")
        print("✅ MACD 因子")
        print("✅ 布林带因子（Bollinger Bands）")
        print("✅ 资金流向因子（Money Flow）\n")

    def calculate_all_factors(self, data):
        """
        计算所有8个因子

        Args:
            data: 股票K线数据（DataFrame）

        Returns:
            dict: 8个因子的计算结果
        """
        if data is None or len(data) < 20:
            return None

        # 计算8个因子
        factors = {
            "momentum": self.calculate_momentum_factor(data),
            "ma_deviation": self.calculate_ma_deviation_factor(data),
            "volume_trend": self.calculate_volume_trend_factor(data),
            "volatility": self.calculate_volatility_factor(data),
            "rsi": self.calculate_rsi_factor(data),
            "macd": self.calculate_macd_factor(data),
            "bollinger": self.calculate_bollinger_factor(data),
            "money_flow": self.calculate_money_flow_factor(data)
        }

        return factors

    def calculate_momentum_factor(self, data):
        """
        计算动量因子

        计算公式：(当前价格 - N天前价格) / N天前价格
        """
        close = data['close'].values

        if len(close) < 5:
            return None

        # 5日动量
        momentum_5 = (close[-1] - close[-5]) / close[-5]

        # 10日动量
        momentum_10 = (close[-1] - close[-10]) / close[-10] if len(close) >= 10 else momentum_5

        # 20日动量
        momentum_20 = (close[-1] - close[-20]) / close[-20] if len(close) >= 20 else momentum_10

        # 综合动量（加权平均）
        momentum_avg = (momentum_5 * 0.5 + momentum_10 * 0.3 + momentum_20 * 0.2)

        # 归一化到 [-1, 1]
        momentum_score = min(max(momentum_avg * 10, -1), 1)

        return {
            "momentum_5": momentum_5,
            "momentum_10": momentum_10,
            "momentum_20": momentum_20,
            "momentum_avg": momentum_avg,
            "score": momentum_score,
            "weight": 0.25  # 权重25%
        }

    def calculate_ma_deviation_factor(self, data):
        """
        计算均线偏离因子

        计算公式：(当前价格 - 均线) / 均线
        """
        close = data['close'].values

        if len(close) < 5:
            return None

        # 计算均线
        ma_5 = np.mean(close[-5:])
        ma_10 = np.mean(close[-10:]) if len(close) >= 10 else ma_5
        ma_20 = np.mean(close[-20:]) if len(close) >= 20 else ma_10

        # 计算偏离度
        dev_5 = (close[-1] - ma_5) / ma_5
        dev_10 = (close[-1] - ma_10) / ma_10
        dev_20 = (close[-1] - ma_20) / ma_20

        # 综合偏离度
        dev_avg = (dev_5 * 0.5 + dev_10 * 0.3 + dev_20 * 0.2)

        # 归一化到 [-1, 1]
        dev_score = min(max(dev_avg * 20, -1), 1)

        return {
            "ma_5": ma_5,
            "ma_10": ma_10,
            "ma_20": ma_20,
            "deviation_5": dev_5,
            "deviation_10": dev_10,
            "deviation_20": dev_20,
            "deviation_avg": dev_avg,
            "score": dev_score,
            "weight": 0.15  # 权重15%
        }

    def calculate_volume_trend_factor(self, data):
        """
        计算成交量趋势因子

        计算公式：(当前成交量 - 平均成交量) / 平均成交量
        """
        volume = data['volume'].values

        if len(volume) < 5:
            return None

        # 计算平均成交量
        avg_volume_5 = np.mean(volume[-5:])
        avg_volume_10 = np.mean(volume[-10:]) if len(volume) >= 10 else avg_volume_5
        avg_volume_20 = np.mean(volume[-20:]) if len(volume) >= 20 else avg_volume_10

        # 计算成交量趋势
        trend_5 = (volume[-1] - avg_volume_5) / avg_volume_5
        trend_10 = (volume[-1] - avg_volume_10) / avg_volume_10
        trend_20 = (volume[-1] - avg_volume_20) / avg_volume_20

        # 综合趋势
        trend_avg = (trend_5 * 0.5 + trend_10 * 0.3 + trend_20 * 0.2)

        # 归一化到 [-1, 1]
        trend_score = min(max(trend_avg * 5, -1), 1)

        return {
            "avg_volume_5": avg_volume_5,
            "avg_volume_10": avg_volume_10,
            "avg_volume_20": avg_volume_20,
            "trend_5": trend_5,
            "trend_10": trend_10,
            "trend_20": trend_20,
            "trend_avg": trend_avg,
            "score": trend_score,
            "weight": 0.10  # 权重10%
        }

    def calculate_volatility_factor(self, data):
        """
        计算波动率因子

        计算公式：收益率的标准差
        """
        close = data['close'].values

        if len(close) < 5:
            return None

        # 计算收益率
        returns = np.diff(close) / close[:-1]

        # 计算波动率（标准差）
        volatility_5 = np.std(returns[-5:]) if len(returns) >= 5 else 0
        volatility_10 = np.std(returns[-10:]) if len(returns) >= 10 else volatility_5
        volatility_20 = np.std(returns[-20:]) if len(returns) >= 20 else volatility_10

        # 综合波动率
        volatility_avg = (volatility_5 * 0.5 + volatility_10 * 0.3 + volatility_20 * 0.2)

        # 归一化到 [-1, 1]（波动率越低越好）
        volatility_score = min(max((0.05 - volatility_avg) * 20, -1), 1)

        return {
            "volatility_5": volatility_5,
            "volatility_10": volatility_10,
            "volatility_20": volatility_20,
            "volatility_avg": volatility_avg,
            "score": volatility_score,
            "weight": 0.10  # 权重10%
        }

    def calculate_rsi_factor(self, data):
        """
        计算 RSI 因子（相对强弱指标）

        计算公式：RSI = 100 - 100 / (1 + RS)
        其中 RS = 平均上涨幅度 / 平均下跌幅度
        """
        close = data['close'].values

        if len(close) < 15:
            return None

        # 计算价格变化
        changes = np.diff(close)

        # 分离上涨和下跌
        gains = np.where(changes > 0, changes, 0)
        losses = np.where(changes < 0, -changes, 0)

        # 计算平均上涨和下跌（14日）
        avg_gain = np.mean(gains[-14:])
        avg_loss = np.mean(losses[-14:])

        # 计算 RS
        if avg_loss == 0:
            rs = 100
        else:
            rs = avg_gain / avg_loss

        # 计算 RSI
        rsi = 100 - 100 / (1 + rs)

        # 归一化到 [-1, 1]（RSI 50 为中性，>70 超买，<30 超卖）
        if rsi > 70:
            rsi_score = -min((rsi - 70) / 30, 1)  # 超买，负分
        elif rsi < 30:
            rsi_score = min((30 - rsi) / 30, 1)   # 超卖，正分
        else:
            rsi_score = (rsi - 50) / 20  # 中性区间

        return {
            "rsi": rsi,
            "rsi_score": rsi_score,
            "weight": 0.10  # 权重10%
        }

    def calculate_macd_factor(self, data):
        """
        计算 MACD 因子（指数平滑异同移动平均线）

        计算公式：
        DIF = EMA(12) - EMA(26)
        DEA = EMA(DIF, 9)
        MACD = 2 * (DIF - DEA)
        """
        close = data['close'].values

        if len(close) < 26:
            return None

        # 计算 EMA
        def calculate_ema(data, period):
            ema = np.zeros_like(data)
            ema[0] = data[0]
            multiplier = 2 / (period + 1)
            for i in range(1, len(data)):
                ema[i] = (data[i] * multiplier) + (ema[i-1] * (1 - multiplier))
            return ema

        ema_12 = calculate_ema(close, 12)
        ema_26 = calculate_ema(close, 26)

        # 计算 DIF
        dif = ema_12 - ema_26

        # 计算 DEA
        dea = calculate_ema(dif, 9)

        # 计算 MACD
        macd = 2 * (dif - dea)

        # MACD 信号
        if dif[-1] > dea[-1] and dif[-2] <= dea[-2]:
            macd_signal = "金叉"  # 买入信号
            macd_score = 0.8
        elif dif[-1] < dea[-1] and dif[-2] >= dea[-2]:
            macd_signal = "死叉"  # 卖出信号
            macd_score = -0.8
        elif dif[-1] > dea[-1]:
            macd_signal = "多头排列"
            macd_score = 0.3
        else:
            macd_signal = "空头排列"
            macd_score = -0.3

        return {
            "dif": dif[-1],
            "dea": dea[-1],
            "macd": macd[-1],
            "signal": macd_signal,
            "score": macd_score,
            "weight": 0.10  # 权重10%
        }

    def calculate_bollinger_factor(self, data):
        """
        计算布林带因子（Bollinger Bands）

        计算公式：
        中轨 = MA(20)
        上轨 = MA(20) + 2 * Std(20)
        下轨 = MA(20) - 2 * Std(20)
        """
        close = data['close'].values

        if len(close) < 20:
            return None

        # 计算中轨（20日均线）
        middle_band = np.mean(close[-20:])

        # 计算标准差
        std_dev = np.std(close[-20:])

        # 计算上下轨
        upper_band = middle_band + 2 * std_dev
        lower_band = middle_band - 2 * std_dev

        # 当前价格位置
        price = close[-1]
        position = (price - lower_band) / (upper_band - lower_band) if upper_band != lower_band else 0.5

        # 布林带信号
        if position > 0.8:
            bollinger_signal = "接近上轨"
            bollinger_score = -0.6  # 可能回调
        elif position < 0.2:
            bollinger_signal = "接近下轨"
            bollinger_score = 0.6   # 可能反弹
        elif position > 0.5:
            bollinger_signal = "中轨上方"
            bollinger_score = 0.3
        else:
            bollinger_signal = "中轨下方"
            bollinger_score = -0.3

        return {
            "upper_band": upper_band,
            "middle_band": middle_band,
            "lower_band": lower_band,
            "position": position,
            "signal": bollinger_signal,
            "score": bollinger_score,
            "weight": 0.10  # 权重10%
        }

    def calculate_money_flow_factor(self, data):
        """
        计算资金流向因子（Money Flow Index, MFI）

        计算公式：
        典型价格 = (最高 + 最低 + 收盘) / 3
        资金流量 = 典型价格 * 成交量
        正资金流量 = 上涨日的资金流量之和
        负资金流量 = 下跌日的资金流量之和
        MFI = 100 - 100 / (1 + 正资金流量 / 负资金流量)
        """
        if len(data) < 14:
            return None

        high = data['high'].values
        low = data['low'].values
        close = data['close'].values
        volume = data['volume'].values

        # 计算典型价格
        typical_price = (high + low + close) / 3

        # 计算资金流量
        money_flow = typical_price * volume

        # 分离上涨和下跌
        recent_14 = min(14, len(money_flow) - 1)
        positive_mf = np.where(money_flow[-recent_14:] > money_flow[-recent_14-1:-1], money_flow[-recent_14:], 0)
        negative_mf = np.where(money_flow[-recent_14:] < money_flow[-recent_14-1:-1], money_flow[-recent_14:], 0)

        # 计算正负资金流量之和
        total_positive_mf = np.sum(positive_mf)
        total_negative_mf = np.sum(negative_mf)

        # 计算 MFI
        if total_negative_mf == 0:
            mfi = 100
        else:
            money_ratio = total_positive_mf / total_negative_mf
            mfi = 100 - 100 / (1 + money_ratio)

        # MFI 信号
        if mfi > 80:
            mfi_signal = "资金流入过多"
            mfi_score = -0.6  # 可能回调
        elif mfi < 20:
            mfi_signal = "资金流出过多"
            mfi_score = 0.6   # 可能反弹
        elif mfi > 50:
            mfi_signal = "资金净流入"
            mfi_score = 0.3
        else:
            mfi_signal = "资金净流出"
            mfi_score = -0.3

        return {
            "mfi": mfi,
            "positive_mf": total_positive_mf,
            "negative_mf": total_negative_mf,
            "signal": mfi_signal,
            "score": mfi_score,
            "weight": 0.10  # 权重10%
        }

    def calculate_total_score(self, factors):
        """
        计算综合评分（加权平均）

        Args:
            factors: 8个因子的计算结果

        Returns:
            float: 综合评分 [0, 10]
        """
        if factors is None:
            return None

        total_score = 0
        total_weight = 0

        for factor_name, factor_data in factors.items():
            if factor_data is not None and 'score' in factor_data and 'weight' in factor_data:
                score = factor_data['score']
                weight = factor_data['weight']

                # 归一化到 [0, 1]
                normalized_score = (score + 1) / 2

                total_score += normalized_score * weight
                total_weight += weight

        # 归一化到 [0, 10]
        if total_weight > 0:
            final_score = (total_score / total_weight) * 10
            return min(max(final_score, 0), 10)
        else:
            return 0

    def get_factor_analysis(self, factors):
        """
        获取因子分析报告

        Args:
            factors: 8个因子的计算结果

        Returns:
            dict: 因子分析报告
        """
        if factors is None:
            return None

        # 找出最强的和最弱的因子
        factor_scores = []
        for factor_name, factor_data in factors.items():
            if factor_data is not None and 'score' in factor_data:
                factor_scores.append({
                    'name': factor_name,
                    'score': factor_data['score'],
                    'weight': factor_data.get('weight', 0)
                })

        # 按得分排序
        factor_scores_sorted = sorted(factor_scores, key=lambda x: x['score'], reverse=True)

        # 获取最强和最弱
        strongest = factor_scores_sorted[0] if factor_scores_sorted else None
        weakest = factor_scores_sorted[-1] if factor_scores_sorted else None

        # 计算综合评分
        total_score = self.calculate_total_score(factors)

        return {
            "total_score": total_score,
            "strongest_factor": strongest['name'] if strongest else None,
            "strongest_score": strongest['score'] if strongest else None,
            "weakest_factor": weakest['name'] if weakest else None,
            "weakest_score": weakest['score'] if weakest else None,
            "factor_count": len(factor_scores),
            "factors": factor_scores_sorted
        }


if __name__ == "__main__":
    # 测试代码
    print("Quant Trading 8因子系统 v2.0 测试")

    # 创建模拟数据
    dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
    base_price = 100.0
    prices = []
    for i in range(100):
        if i == 0:
            price = base_price
        else:
            price = prices[-1] * (1 + np.random.normal(0, 0.02))
        prices.append(price)

    # 创建 DataFrame
    data = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p * 1.02 for p in prices],
        'low': [p * 0.98 for p in prices],
        'close': prices,
        'volume': [10000000 * (1 + np.random.uniform(-0.3, 0.5)) for _ in range(100)]
    })

    # 计算因子
    quant_factors = QuantFactorsV2()

    print("\n计算所有因子...")
    factors = quant_factors.calculate_all_factors(data)

    print("\n因子计算结果:")
    for factor_name, factor_data in factors.items():
        if factor_data is not None:
            print(f"\n{factor_name}:")
            print(f"   评分: {factor_data.get('score', 0):.2f}")
            print(f"   权重: {factor_data.get('weight', 0):.2%}")

    # 计算综合评分
    total_score = quant_factors.calculate_total_score(factors)
    print(f"\n综合评分: {total_score:.2f}/10")

    # 因子分析
    analysis = quant_factors.get_factor_analysis(factors)
    print(f"\n最强因子: {analysis.get('strongest_factor', 'N/A')} (评分: {analysis.get('strongest_score', 0):.2f})")
    print(f"最弱因子: {analysis.get('weakest_factor', 'N/A')} (评分: {analysis.get('weakest_score', 0):.2f})")

    print("\n所有测试完成")
