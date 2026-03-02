#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NTDF 信号系统 v2.0
完整的信号类型判断和计算
"""

import pandas as pd
import numpy as np
from datetime import datetime

class NtdfSignalV2:
    """NTDF 信号系统 v2.0"""

    def __init__(self):
        """初始化 NTDF 信号系统"""
        print("="*70)
        print("NTDF 信号系统 v2.0 - 初始化")
        print("="*70)
        print("✅ BREAKOUT（突破）")
        print("✅ REVERSAL（反转）")
        print("✅ TURNOVER（换手）")
        print("✅ ACCUMULATION（吸筹）")
        print("✅ DISTRIBUTION（出货）")
        print("✅ MOMENTUM（动量）")
        print("✅ CONSOLIDATION（整理）\n")

    def calculate_signal(self, data):
        """
        计算 NTDF 信号

        Args:
            data: 股票K线数据（DataFrame）

        Returns:
            dict: 信号计算结果
        """
        if data is None or len(data) < 5:
            return None

        # 计算 Delta
        delta = self._calculate_delta(data)

        # 判断信号类型
        signal_type, signal_score, signal_dir = self._determine_signal_type(data, delta)

        # 计算成交量异常
        volume_anomaly = self._calculate_volume_anomaly(data)

        # 计算价格位置
        price_position = self._calculate_price_position(data)

        # 计算动量
        momentum = self._calculate_momentum(data)

        return {
            "type": signal_type,
            "score": signal_score,
            "direction": signal_dir,
            "delta_value": delta,
            "volume_anomaly": volume_anomaly,
            "price_position": price_position,
            "momentum": momentum,
            "confidence": self._calculate_confidence(delta, volume_anomaly, momentum)
        }

    def _calculate_delta(self, data):
        """
        计算 Delta（数字净量）

        计算公式：(收盘价 - 开盘价) / (最高价 - 最低价) * 成交量
        """
        close = data['close'].values
        open_price = data['open'].values
        high = data['high'].values
        low = data['low'].values
        volume = data['volume'].values

        recent_close = close[-1]
        recent_open = open_price[-1]
        recent_high = high[-1]
        recent_low = low[-1]
        recent_volume = volume[-1]

        high_low_diff = recent_high - recent_low
        if high_low_diff > 0:
            delta = (recent_close - recent_open) / high_low_diff * recent_volume
        else:
            delta = 0

        return delta

    def _determine_signal_type(self, data, delta):
        """
        判断信号类型

        Args:
            data: 股票K线数据
            delta: Delta 值

        Returns:
            tuple: (信号类型, 信号评分, 信号方向)
        """
        volume = data['volume'].values
        close = data['close'].values

        recent_volume = volume[-1]
        avg_volume = np.mean(volume[-5:])

        # 计算成交量比率
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1

        # 计算价格趋势
        price_trend = (close[-1] - close[-5]) / close[-5] if len(close) >= 5 else 0

        # 判断信号类型
        if delta > 100000 and volume_ratio > 2:
            # 突破信号
            signal_type = "BREAKOUT"
            signal_dir = 1
            signal_score = 0.85

        elif delta < -100000 and volume_ratio > 2:
            # 反转信号（向下）
            signal_type = "REVERSAL"
            signal_dir = -1
            signal_score = 0.70

        elif delta > 50000 and volume_ratio > 1.5:
            # 吸筹信号
            signal_type = "ACCUMULATION"
            signal_dir = 1
            signal_score = 0.55

        elif delta < -50000 and volume_ratio > 1.5:
            # 出货信号
            signal_type = "DISTRIBUTION"
            signal_dir = -1
            signal_score = 0.55

        elif volume_ratio > 2.5:
            # 换手信号
            signal_type = "TURNOVER"
            signal_dir = 0
            signal_score = 0.40

        elif abs(price_trend) > 0.1 and volume_ratio > 1.2:
            # 动量信号
            signal_type = "MOMENTUM"
            signal_dir = 1 if price_trend > 0 else -1
            signal_score = 0.45

        elif abs(price_trend) < 0.02 and volume_ratio < 1.2:
            # 整理信号
            signal_type = "CONSOLIDATION"
            signal_dir = 0
            signal_score = 0.20

        elif delta > 20000:
            # 弱突破
            signal_type = "BREAKOUT_WEAK"
            signal_dir = 1
            signal_score = 0.35

        elif delta < -20000:
            # 弱反转
            signal_type = "REVERSAL_WEAK"
            signal_dir = -1
            signal_score = 0.30

        else:
            # 无信号
            signal_type = "NONE"
            signal_dir = 0
            signal_score = 0.0

        return signal_type, signal_score, signal_dir

    def _calculate_volume_anomaly(self, data):
        """
        计算成交量异常

        Args:
            data: 股票K线数据

        Returns:
            dict: 成交量异常指标
        """
        volume = data['volume'].values

        if len(volume) < 5:
            return None

        recent_volume = volume[-1]
        avg_volume_5 = np.mean(volume[-5:])
        avg_volume_10 = np.mean(volume[-10:]) if len(volume) >= 10 else avg_volume_5
        avg_volume_20 = np.mean(volume[-20:]) if len(volume) >= 20 else avg_volume_10

        # 计算成交量比率
        ratio_5 = recent_volume / avg_volume_5
        ratio_10 = recent_volume / avg_volume_10
        ratio_20 = recent_volume / avg_volume_20

        # 判断异常程度
        if ratio_5 > 3:
            anomaly_level = "极高"
            anomaly_score = 0.9
        elif ratio_5 > 2:
            anomaly_level = "高"
            anomaly_score = 0.7
        elif ratio_5 > 1.5:
            anomaly_level = "中"
            anomaly_score = 0.5
        elif ratio_5 > 1.2:
            anomaly_level = "低"
            anomaly_score = 0.3
        else:
            anomaly_level = "正常"
            anomaly_score = 0.0

        return {
            "recent_volume": recent_volume,
            "avg_volume_5": avg_volume_5,
            "avg_volume_10": avg_volume_10,
            "avg_volume_20": avg_volume_20,
            "ratio_5": ratio_5,
            "ratio_10": ratio_10,
            "ratio_20": ratio_20,
            "anomaly_level": anomaly_level,
            "anomaly_score": anomaly_score
        }

    def _calculate_price_position(self, data):
        """
        计算价格位置（在20日区间内的位置）

        Args:
            data: 股票K线数据

        Returns:
            dict: 价格位置指标
        """
        close = data['close'].values

        if len(close) < 20:
            return None

        recent_close = close[-1]
        high_20 = np.max(close[-20:])
        low_20 = np.min(close[-20:])

        # 计算价格位置
        if high_20 != low_20:
            position = (recent_close - low_20) / (high_20 - low_20)
        else:
            position = 0.5

        # 判断位置
        if position > 0.8:
            position_level = "高位"
            position_score = -0.5  # 高位风险
        elif position > 0.6:
            position_level = "偏高位"
            position_score = -0.2
        elif position > 0.4:
            position_level = "中位"
            position_score = 0.0
        elif position > 0.2:
            position_level = "偏低位"
            position_score = 0.2
        else:
            position_level = "低位"
            position_score = 0.5  # 低位机会

        return {
            "high_20": high_20,
            "low_20": low_20,
            "position": position,
            "position_level": position_level,
            "position_score": position_score
        }

    def _calculate_momentum(self, data):
        """
        计算动量

        Args:
            data: 股票K线数据

        Returns:
            dict: 动量指标
        """
        close = data['close'].values

        if len(close) < 10:
            return None

        # 计算不同周期的动量
        momentum_5 = (close[-1] - close[-5]) / close[-5]
        momentum_10 = (close[-1] - close[-10]) / close[-10] if len(close) >= 10 else momentum_5
        momentum_20 = (close[-1] - close[-20]) / close[-20] if len(close) >= 20 else momentum_10

        # 综合动量
        momentum_avg = (momentum_5 * 0.5 + momentum_10 * 0.3 + momentum_20 * 0.2)

        # 判断动量强度
        if momentum_avg > 0.1:
            momentum_level = "强势上涨"
            momentum_score = 0.8
        elif momentum_avg > 0.05:
            momentum_level = "温和上涨"
            momentum_score = 0.5
        elif momentum_avg > 0:
            momentum_level = "微涨"
            momentum_score = 0.2
        elif momentum_avg > -0.05:
            momentum_level = "微跌"
            momentum_score = -0.2
        elif momentum_avg > -0.1:
            momentum_level = "温和下跌"
            momentum_score = -0.5
        else:
            momentum_level = "强势下跌"
            momentum_score = -0.8

        return {
            "momentum_5": momentum_5,
            "momentum_10": momentum_10,
            "momentum_20": momentum_20,
            "momentum_avg": momentum_avg,
            "momentum_level": momentum_level,
            "momentum_score": momentum_score
        }

    def _calculate_confidence(self, delta, volume_anomaly, momentum):
        """
        计算信号信心度

        Args:
            delta: Delta 值
            volume_anomaly: 成交量异常
            momentum: 动量

        Returns:
            str: 信心度
        """
        # 基础信心度
        base_confidence = 0.5

        # Delta 贡献
        if abs(delta) > 100000:
            base_confidence += 0.3
        elif abs(delta) > 50000:
            base_confidence += 0.2
        elif abs(delta) > 20000:
            base_confidence += 0.1

        # 成交量异常贡献
        if volume_anomaly is not None:
            if volume_anomaly['anomaly_score'] > 0.7:
                base_confidence += 0.2
            elif volume_anomaly['anomaly_score'] > 0.5:
                base_confidence += 0.1

        # 动量贡献
        if momentum is not None:
            if abs(momentum['momentum_score']) > 0.5:
                base_confidence += 0.1

        # 归一化
        confidence_score = min(base_confidence, 1.0)

        # 转换为文字
        if confidence_score > 0.8:
            return "极高"
        elif confidence_score > 0.6:
            return "高"
        elif confidence_score > 0.4:
            return "中"
        else:
            return "低"

    def get_signal_analysis(self, signal):
        """
        获取信号分析报告

        Args:
            signal: 信号计算结果

        Returns:
            str: 信号分析
        """
        if signal is None:
            return "无有效信号"

        signal_type = signal['type']
        delta = signal['delta_value']
        volume_anomaly = signal.get('volume_anomaly')
        price_position = signal.get('price_position')
        momentum = signal.get('momentum')
        confidence = signal.get('confidence', '未知')

        # 生成分析报告
        analysis = []

        # 信号类型
        analysis.append(f"信号类型: {signal_type}")
        analysis.append(f"Delta 值: {delta:.2f}")
        analysis.append(f"信心度: {confidence}")

        # 成交量异常
        if volume_anomaly:
            analysis.append(f"成交量异常: {volume_anomaly['anomaly_level']} ({volume_anomaly['ratio_5']:.2f}倍)")

        # 价格位置
        if price_position:
            analysis.append(f"价格位置: {price_position['position_level']} ({price_position['position']*100:.1f}%)")

        # 动量
        if momentum:
            analysis.append(f"动量趋势: {momentum['momentum_level']} ({momentum['momentum_avg']*100:.2f}%)")

        return "\n".join(analysis)


if __name__ == "__main__":
    # 测试代码
    print("NTDF 信号系统 v2.0 测试")

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

    # 计算信号
    ntdf_signal = NtdfSignalV2()

    print("\n计算 NTDF 信号...")
    signal = ntdf_signal.calculate_signal(data)

    print("\nNTDF 信号结果:")
    print(f"信号类型: {signal['type']}")
    print(f"信号评分: {signal['score']:.2f}")
    print(f"信号方向: {signal['direction']}")
    print(f"Delta 值: {signal['delta_value']:.2f}")
    print(f"信心度: {signal['confidence']}")

    # 信号分析
    print("\n信号分析:")
    print(ntdf_signal.get_signal_analysis(signal))

    print("\n所有测试完成")
