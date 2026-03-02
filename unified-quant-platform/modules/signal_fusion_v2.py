#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信号融合引擎 v2.0
融合 NTDF 和 Quant Trading 信号，添加市场环境和资金流向分析
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.quant_factors_v2 import QuantFactorsV2
from modules.ntdf_signal_v2 import NtdfSignalV2

class SignalFusionEngineV2:
    """信号融合引擎 v2.0"""

    def __init__(self):
        """初始化信号融合引擎"""
        print("="*70)
        print("信号融合引擎 v2.0 - 初始化")
        print("="*70)
        print("✅ NTDF 信号融合")
        print("✅ Quant Trading 8因子融合")
        print("✅ 市场环境分析")
        print("✅ 资金流向分析")
        print("✅ 技术形态识别\n")

        # 初始化信号计算器
        self.quant_factors = QuantFactorsV2()
        self.ntdf_signal = NtdfSignalV2()

    def fuse_signals(self, stock_data, market_data):
        """
        融合所有信号

        Args:
            stock_data: 股票K线数据
            market_data: 大盘数据

        Returns:
            dict: 融合信号结果
        """
        if stock_data is None or len(stock_data) < 20:
            return None

        # 计算 NTDF 信号
        ntdf_result = self.ntdf_signal.calculate_signal(stock_data)

        # 计算 Quant Trading 8因子
        quant_result = self.quant_factors.calculate_all_factors(stock_data)

        # 获取市场环境
        market_env = self._get_market_environment(market_data)

        # 获取资金流向
        money_flow = self._analyze_money_flow(stock_data, quant_result)

        # 获取技术形态
        technical_pattern = self._analyze_technical_pattern(stock_data)

        # 融合信号
        fusion_result = self._perform_fusion(
            ntdf_result,
            quant_result,
            market_env,
            money_flow,
            technical_pattern
        )

        return fusion_result

    def _get_market_environment(self, market_data):
        """
        获取市场环境

        Args:
            market_data: 大盘数据

        Returns:
            dict: 市场环境
        """
        if market_data is None:
            return {
                "environment": "未知",
                "factor": 1.0,
                "trend": "未知"
            }

        environment = market_data.get('environment', '震荡')
        up_ratio = market_data.get('up_ratio', 0.5)

        # 判断趋势
        if up_ratio > 0.6:
            trend = "上涨"
            factor = 1.2  # 强势市场，买入信号更强
        elif up_ratio > 0.4:
            trend = "震荡"
            factor = 1.0  # 震荡市场，不调整
        else:
            trend = "下跌"
            factor = 0.8  # 弱势市场，买入信号更弱

        return {
            "environment": environment,
            "trend": trend,
            "up_ratio": up_ratio,
            "factor": factor
        }

    def _analyze_money_flow(self, stock_data, quant_result):
        """
        分析资金流向

        Args:
            stock_data: 股票K线数据
            quant_result: Quant Trading 因子结果

        Returns:
            dict: 资金流向分析
        """
        if stock_data is None or quant_result is None:
            return None

        # 获取资金流向因子
        money_flow_factor = quant_result.get('money_flow')

        if money_flow_factor is None:
            return None

        mfi = money_flow_factor.get('mfi', 50)
        positive_mf = money_flow_factor.get('positive_mf', 0)
        negative_mf = money_flow_factor.get('negative_mf', 0)

        # 判断资金流向
        if mfi > 80:
            flow_direction = "过度流入"
            flow_signal = "风险"
            flow_score = -0.5  # 过度流入，风险增加
        elif mfi > 60:
            flow_direction = "净流入"
            flow_signal = "买入"
            flow_score = 0.5
        elif mfi > 40:
            flow_direction = "平衡"
            flow_signal = "观望"
            flow_score = 0.0
        elif mfi > 20:
            flow_direction = "净流出"
            flow_signal = "卖出"
            flow_score = -0.5
        else:
            flow_direction = "过度流出"
            flow_signal = "机会"
            flow_score = 0.5  # 过度流出，可能反弹

        return {
            "mfi": mfi,
            "positive_mf": positive_mf,
            "negative_mf": negative_mf,
            "flow_direction": flow_direction,
            "flow_signal": flow_signal,
            "flow_score": flow_score
        }

    def _analyze_technical_pattern(self, stock_data):
        """
        分析技术形态

        Args:
            stock_data: 股票K线数据

        Returns:
            dict: 技术形态分析
        """
        if stock_data is None or len(stock_data) < 20:
            return None

        close = stock_data['close'].values

        # 计算20日均线
        ma_20 = np.mean(close[-20:])

        # 计算价格趋势
        price_trend = (close[-1] - close[-20]) / close[-20]

        # 判断形态
        if close[-1] > ma_20 and price_trend > 0.1:
            pattern = "上升通道"
            pattern_score = 0.5
        elif close[-1] > ma_20 and price_trend < -0.1:
            pattern = "高位震荡"
            pattern_score = -0.2
        elif close[-1] < ma_20 and price_trend > 0.1:
            pattern = "低位反弹"
            pattern_score = 0.3
        elif close[-1] < ma_20 and price_trend < -0.1:
            pattern = "下降通道"
            pattern_score = -0.5
        else:
            pattern = "震荡整理"
            pattern_score = 0.0

        return {
            "pattern": pattern,
            "ma_20": ma_20,
            "price_trend": price_trend,
            "pattern_score": pattern_score
        }

    def _perform_fusion(self, ntdf_result, quant_result, market_env, money_flow, technical_pattern):
        """
        执行信号融合

        Args:
            ntdf_result: NTDF 信号结果
            quant_result: Quant Trading 因子结果
            market_env: 市场环境
            money_flow: 资金流向
            technical_pattern: 技术形态

        Returns:
            dict: 融合信号结果
        """
        # 计算各部分得分
        ntdf_score = ntdf_result.get('score', 0) if ntdf_result else 0
        quant_score = self.quant_factors.calculate_total_score(quant_result) if quant_result else 0

        # 资金流向得分
        money_flow_score = money_flow.get('flow_score', 0) if money_flow else 0

        # 技术形态得分
        technical_pattern_score = technical_pattern.get('pattern_score', 0) if technical_pattern else 0

        # 市场环境因子
        market_factor = market_env.get('factor', 1.0)

        # 加权融合
        # NTDF: 30%
        # Quant: 50%
        # Money Flow: 10%
        # Technical Pattern: 10%
        fusion_score = (
            ntdf_score * 0.3 +
            quant_score * 0.5 +
            (money_flow_score + 1) * 0.1 * 10 +
            (technical_pattern_score + 1) * 0.1 * 10
        ) * market_factor

        # 归一化到 [0, 10]
        fusion_score = min(max(fusion_score, 0), 10)

        # 生成买卖建议
        if fusion_score >= 8.0:
            action = "STRONG_BUY"
            confidence = "极高"
            reason = "多个指标均显示强势，强烈建议买入"
        elif fusion_score >= 6.5:
            action = "BUY"
            confidence = "高"
            reason = "指标偏向多头，建议买入"
        elif fusion_score >= 5.0:
            action = "WEAK_BUY"
            confidence = "中高"
            reason = "指标偏向多头，可适量买入"
        elif fusion_score >= 3.5:
            action = "HOLD"
            confidence = "中"
            reason = "信号中性，建议观望"
        elif fusion_score >= 2.0:
            action = "WEAK_SELL"
            confidence = "中高"
            reason = "指标偏向空头，可适量卖出"
        elif fusion_score >= 0.5:
            action = "SELL"
            confidence = "高"
            reason = "指标偏向空头，建议卖出"
        else:
            action = "STRONG_SELL"
            confidence = "极高"
            reason = "多个指标均显示弱势，强烈建议卖出"

        return {
            "fusion_score": fusion_score,
            "fusion_mode": "weighted",
            "recommendation": {
                "action": action,
                "confidence": confidence,
                "reason": reason
            },
            "components": {
                "ntdf_score": ntdf_score,
                "ntdf_weight": 0.3,
                "quant_score": quant_score,
                "quant_weight": 0.5,
                "money_flow_score": money_flow_score,
                "money_flow_weight": 0.1,
                "technical_pattern_score": technical_pattern_score,
                "technical_pattern_weight": 0.1
            },
            "market_environment": market_env,
            "money_flow": money_flow,
            "technical_pattern": technical_pattern,
            "ntdf_signal": ntdf_result,
            "quant_factors": quant_result,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def get_fusion_analysis(self, fusion_result):
        """
        获取融合分析报告

        Args:
            fusion_result: 融合信号结果

        Returns:
            str: 融合分析报告
        """
        if fusion_result is None:
            return "无有效融合信号"

        # 基本信息
        fusion_score = fusion_result.get('fusion_score', 0)
        recommendation = fusion_result.get('recommendation', {})
        components = fusion_result.get('components', {})
        market_env = fusion_result.get('market_environment', {})
        money_flow = fusion_result.get('money_flow')
        technical_pattern = fusion_result.get('technical_pattern')

        # 生成报告
        analysis = []

        # 融合评分
        analysis.append("="*70)
        analysis.append("📊 信号融合分析报告")
        analysis.append("="*70)

        # 综合评分
        analysis.append(f"\n🔀 融合评分: {fusion_score:.2f}/10")
        analysis.append(f"💡 买卖建议: {recommendation.get('action', 'N/A')}")
        analysis.append(f"🎯 信心度: {recommendation.get('confidence', 'N/A')}")
        analysis.append(f"📝 原因: {recommendation.get('reason', 'N/A')}")

        # 各组成部分
        analysis.append(f"\n📈 各组成部分:")
        analysis.append(f"   NTDF 信号: {components.get('ntdf_score', 0):.2f} (权重: {components.get('ntdf_weight', 0):.0%})")
        analysis.append(f"   Quant 8因子: {components.get('quant_score', 0):.2f} (权重: {components.get('quant_weight', 0):.0%})")

        if money_flow:
            analysis.append(f"   资金流向: {money_flow.get('flow_direction', 'N/A')} (权重: {components.get('money_flow_weight', 0):.0%})")

        if technical_pattern:
            analysis.append(f"   技术形态: {technical_pattern.get('pattern', 'N/A')} (权重: {components.get('technical_pattern_weight', 0):.0%})")

        # 市场环境
        analysis.append(f"\n📊 市场环境:")
        analysis.append(f"   环境: {market_env.get('environment', 'N/A')}")
        analysis.append(f"   趋势: {market_env.get('trend', 'N/A')}")
        analysis.append(f"   因子: {market_env.get('factor', 1.0):.2f}")

        # NTDF 信号详情
        ntdf_signal = fusion_result.get('ntdf_signal')
        if ntdf_signal:
            analysis.append(f"\n📊 NTDF 信号详情:")
            analysis.append(f"   信号类型: {ntdf_signal.get('type', 'N/A')}")
            analysis.append(f"   Delta 值: {ntdf_signal.get('delta_value', 0):.2f}")
            analysis.append(f"   信心度: {ntdf_signal.get('confidence', 'N/A')}")

            volume_anomaly = ntdf_signal.get('volume_anomaly')
            if volume_anomaly:
                analysis.append(f"   成交量异常: {volume_anomaly.get('anomaly_level', 'N/A')}")

            price_position = ntdf_signal.get('price_position')
            if price_position:
                analysis.append(f"   价格位置: {price_position.get('position_level', 'N/A')}")

        # Quant 因子详情
        quant_factors = fusion_result.get('quant_factors')
        if quant_factors:
            analysis.append(f"\n📊 Quant 8因子详情:")
            factor_analysis = self.quant_factors.get_factor_analysis(quant_factors)
            if factor_analysis:
                analysis.append(f"   综合评分: {factor_analysis.get('total_score', 0):.2f}/10")
                analysis.append(f"   最强因子: {factor_analysis.get('strongest_factor', 'N/A')} (评分: {factor_analysis.get('strongest_score', 0):.2f})")
                analysis.append(f"   最弱因子: {factor_analysis.get('weakest_factor', 'N/A')} (评分: {factor_analysis.get('weakest_score', 0):.2f})")

        analysis.append(f"\n⏰ 分析时间: {fusion_result.get('timestamp', 'N/A')}")
        analysis.append("="*70)

        return "\n".join(analysis)


if __name__ == "__main__":
    # 测试代码
    print("信号融合引擎 v2.0 测试")

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

    # 创建股票数据
    stock_data = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p * 1.02 for p in prices],
        'low': [p * 0.98 for p in prices],
        'close': prices,
        'volume': [10000000 * (1 + np.random.uniform(-0.3, 0.5)) for _ in range(100)]
    })

    # 创建大盘数据
    market_data = {
        "data": stock_data,
        "environment": "震荡",
        "threshold": 9.0,
        "up_count": 15,
        "down_count": 15,
        "up_ratio": 0.5
    }

    # 融合信号
    fusion_engine = SignalFusionEngineV2()

    print("\n融合信号...")
    fusion_result = fusion_engine.fuse_signals(stock_data, market_data)

    print("\n融合结果:")
    print(f"融合评分: {fusion_result['fusion_score']:.2f}/10")
    print(f"买卖建议: {fusion_result['recommendation']['action']}")
    print(f"信心度: {fusion_result['recommendation']['confidence']}")
    print(f"原因: {fusion_result['recommendation']['reason']}")

    # 融合分析
    print("\n融合分析:")
    analysis = fusion_engine.get_fusion_analysis(fusion_result)
    print(analysis)

    print("\n所有测试完成")
