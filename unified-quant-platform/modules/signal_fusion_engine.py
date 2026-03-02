#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一量化平台 - 信号融合引擎
逻辑融合 NTDF 和 Quant Trading 信号
"""

import pandas as pd
import numpy as np
from datetime import datetime

class SignalFusionEngine:
    """信号融合引擎 - 逻辑融合算法"""

    def __init__(self, mode="logical"):
        """
        初始化融合引擎

        Args:
            mode: 融合模式
                - "simple": 简单平均
                - "weighted": 加权平均
                - "logical": 逻辑融合（AND/OR）
        """
        self.mode = mode

        print(f"✅ 信号融合引擎初始化完成")
        print(f"   融合模式: {mode}")

    def fuse_signals(self, ntdf_signal, quant_signal, market_env="震荡"):
        """
        融合 NTDF 和 Quant Trading 信号

        Args:
            ntdf_signal: NTDF 信号
                - {"type": "BREAKOUT"/"REVERSAL"/"TURNOVER",
                  "score": 0.75,
                  "direction": 1/-1/0}
            quant_signal: Quant Trading 信号
                - {"score": 8.5,
                  "factors": {...}}
            market_env: 市场环境（强势/震荡/弱势）

        Returns:
            dict: 融合信号
        """
        print(f"\n📊 开始信号融合...")
        print(f"   NTDF 信号: {ntdf_signal.get('type', 'N/A')} | 评分: {ntdf_signal.get('score', 0):.2f}")
        print(f"   Quant 信号: 评分: {quant_signal.get('score', 0):.2f}")
        print(f"   市场环境: {market_env}")

        # 根据市场环境调整权重
        weights = self._get_weights(market_env)

        # 归一化评分
        ntdf_norm = self._normalize_ntdf_score(ntdf_signal.get('score', 0))
        quant_norm = self._normalize_quant_score(quant_signal.get('score', 0))

        # 根据模式融合
        if self.mode == "simple":
            fusion_score, recommendation = self._simple_fusion(ntdf_norm, quant_norm)
        elif self.mode == "weighted":
            fusion_score, recommendation = self._weighted_fusion(ntdf_norm, quant_norm, weights)
        elif self.mode == "logical":
            fusion_score, recommendation = self._logical_fusion(ntdf_signal, quant_signal, weights)
        else:
            raise ValueError(f"不支持的融合模式: {self.mode}")

        # 生成融合结果
        result = {
            "ntdf_signal": ntdf_signal,
            "quant_signal": quant_signal,
            "fusion_score": round(fusion_score, 2),
            "fusion_mode": self.mode,
            "recommendation": recommendation,
            "market_environment": market_env,
            "weights_used": weights,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self._print_fusion_result(result)
        return result

    def _get_weights(self, market_env):
        """根据市场环境获取权重"""
        if market_env == "强势":
            return {
                "ntdf": 0.4,   # NTDF 40%（技术面更重要）
                "quant": 0.6   # Quant 60%
            }
        elif market_env == "震荡":
            return {
                "ntdf": 0.5,   # 平衡
                "quant": 0.5
            }
        elif market_env == "弱势":
            return {
                "ntdf": 0.6,   # NTDF 60%（资金流更重要）
                "quant": 0.4   # Quant 40%
            }
        else:
            return {
                "ntdf": 0.5,
                "quant": 0.5
            }

    def _normalize_ntdf_score(self, score):
        """归一化 NTDF 评分 (-1 到 1 转换为 0-1）"""
        # NTDF 评分范围：-1 (完全空头) 到 1 (完全多头)
        # 转换为 0-1 范围
        return (score + 1) / 2

    def _normalize_quant_score(self, score):
        """归一化 Quant 评分 (0-10 转换为 0-1）"""
        # Quant 评分范围：0-10
        # 转换为 0-1 范围
        return score / 10

    def _simple_fusion(self, ntdf_norm, quant_norm):
        """简单平均融合"""
        fusion_score = (ntdf_norm + quant_norm) / 2

        if fusion_score >= 0.75:
            return fusion_score, {
                "action": "强力买入",
                "level": "⭐⭐⭐⭐",
                "confidence": "极高"
            }
        elif fusion_score >= 0.60:
            return fusion_score, {
                "action": "买入",
                "level": "⭐⭐⭐",
                "confidence": "高"
            }
        elif fusion_score >= 0.45:
            return fusion_score, {
                "action": "考虑买入",
                "level": "⭐⭐⭐",
                "confidence": "中等"
            }
        elif fusion_score >= 0.30:
            return fusion_score, {
                "action": "观望",
                "level": "⭐⭐",
                "confidence": "低"
            }
        else:
            return fusion_score, {
                "action": "卖出或回避",
                "level": "⭐",
                "confidence": "低"
            }

    def _weighted_fusion(self, ntdf_norm, quant_norm, weights):
        """加权平均融合"""
        fusion_score = ntdf_norm * weights['ntdf'] + quant_norm * weights['quant']

        # 加权评分映射到买卖建议
        if fusion_score >= 0.80:
            return fusion_score, {
                "action": "强力买入",
                "level": "⭐⭐⭐⭐",
                "confidence": "极高"
            }
        elif fusion_score >= 0.65:
            return fusion_score, {
                "action": "买入",
                "level": "⭐⭐⭐",
                "confidence": "高"
            }
        elif fusion_score >= 0.50:
            return fusion_score, {
                "action": "考虑买入",
                "level": "⭐⭐⭐",
                "confidence": "中等"
            }
        elif fusion_score >= 0.35:
            return fusion_score, {
                "action": "观望",
                "level": "⭐⭐",
                "confidence": "低"
            }
        else:
            return fusion_score, {
                "action": "卖出或回避",
                "level": "⭐",
                "confidence": "低"
            }

    def _logical_fusion(self, ntdf_signal, quant_signal, weights):
        """逻辑融合（复杂但精确）"""
        ntdf_type = ntdf_signal.get('type', '')
        ntdf_dir = ntdf_signal.get('direction', 0)  # 1: 多头, -1: 空头, 0: 中性
        quant_score = quant_signal.get('score', 0)

        # 规则1：NTDF 突破信号 + Quant 高分
        if ntdf_type == "BREAKOUT" and ntdf_dir > 0 and quant_score >= 8.5:
            fusion_score = 0.9  # 极高
            recommendation = {
                "action": "强力买入",
                "level": "⭐⭐⭐⭐",
                "confidence": "极高",
                "reason": "NTDF 突破 + Quant 高分，双重确认"
            }

        # 规则2：NTDF 反转信号 + Quant 高分
        elif ntdf_type == "REVERSAL" and ntdf_dir > 0 and quant_score >= 8.0:
            fusion_score = 0.85  # 很高
            recommendation = {
                "action": "强力买入",
                "level": "⭐⭐⭐⭐",
                "confidence": "极高",
                "reason": "NTDF 反转 + Quant 高分，双重确认"
            }

        # 规则3：NTDF 转量 + Quant 中高分
        elif ntdf_type == "TURNOVER" and quant_score >= 7.5:
            fusion_score = 0.75  # 高
            recommendation = {
                "action": "买入",
                "level": "⭐⭐⭐",
                "confidence": "高",
                "reason": "NTDF 转量 + Quant 中高分"
            }

        # 规则4：两者都看涨
        elif ntdf_dir > 0 and quant_score >= 7.5:
            fusion_score = 0.70  # 中高
            recommendation = {
                "action": "买入",
                "level": "⭐⭐⭐",
                "confidence": "高",
                "reason": "NTDF 看涨 + Quant 看涨"
            }

        # 规则5：两者信号冲突
        elif ntdf_dir < 0 and quant_score >= 7.5:
            fusion_score = 0.40  # 中低
            recommendation = {
                "action": "观望",
                "level": "⭐⭐",
                "confidence": "中等",
                "reason": "NTDF 看跌 + Quant 看涨，信号冲突"
            }

        # 规则6：两者都看跌
        elif ntdf_dir < 0 and quant_score < 5.0:
            fusion_score = 0.20  # 低
            recommendation = {
                "action": "卖出或回避",
                "level": "⭐",
                "confidence": "低",
                "reason": "NTDF 看跌 + Quant 看跌"
            }

        # 规则7：默认加权融合
        else:
            ntdf_norm = self._normalize_ntdf_score(ntdf_signal.get('score', 0))
            quant_norm = self._normalize_quant_score(quant_score)
            fusion_score = ntdf_norm * weights['ntdf'] + quant_norm * weights['quant']

            if fusion_score >= 0.65:
                action = "买入"
                level = "⭐⭐⭐"
                confidence = "高"
            elif fusion_score >= 0.50:
                action = "考虑买入"
                level = "⭐⭐"
                confidence = "中等"
            elif fusion_score >= 0.35:
                action = "观望"
                level = "⭐⭐"
                confidence = "低"
            else:
                action = "卖出或回避"
                level = "⭐"
                confidence = "低"

            recommendation = {
                "action": action,
                "level": level,
                "confidence": confidence,
                "reason": "默认加权融合"
            }

        return fusion_score, recommendation

    def _print_fusion_result(self, result):
        """打印融合结果"""
        print("\n" + "="*70)
        print("📊 信号融合结果")
        print("="*70)

        print(f"\n📈 NTDF 信号:")
        print(f"   类型: {result['ntdf_signal'].get('type', 'N/A')}")
        print(f"   方向: {result['ntdf_signal'].get('direction', 0)}")
        print(f"   评分: {result['ntdf_signal'].get('score', 0):.2f}")

        print(f"\n📊 Quant 信号:")
        print(f"   评分: {result['quant_signal'].get('score', 0):.2f}")

        print(f"\n🔀 融合结果:")
        print(f"   融合模式: {result['fusion_mode']}")
        print(f"   市场环境: {result['market_environment']}")
        print(f"   权重 (NTDF/Quant): {result['weights_used']['ntdf']:.2f} / {result['weights_used']['quant']:.2f}")
        print(f"   综合评分: {result['fusion_score']:.2f}")

        print(f"\n💡 买卖建议:")
        print(f"   操作: {result['recommendation']['action']}")
        print(f"   评级: {result['recommendation']['level']}")
        print(f"   信心度: {result['recommendation']['confidence']}")
        print(f"   原因: {result['recommendation'].get('reason', 'N/A')}")

        print(f"\n⏰ 时间: {result['timestamp']}")

        print("\n" + "="*70)
        print("✅ 信号融合完成！")
        print("="*70 + "\n")


if __name__ == "__main__":
    # 测试代码
    print("="*70)
    print("统一量化平台 - 信号融合引擎测试")
    print("="*70)

    # 创建融合引擎
    engine = SignalFusionEngine(mode="logical")

    # 测试场景1：双重确认
    print("\n\n测试场景1: NTDF 突破 + Quant 高分\n")
    ntdf_signal1 = {
        "type": "BREAKOUT",
        "score": 0.75,
        "direction": 1
    }
    quant_signal1 = {
        "score": 8.8,
        "factors": {}
    }
    result1 = engine.fuse_signals(ntdf_signal1, quant_signal1, market_env="强势")

    # 测试场景2：信号冲突
    print("\n\n测试场景2: NTDF 看跌 + Quant 高分\n")
    ntdf_signal2 = {
        "type": "REVERSAL",
        "score": -0.5,
        "direction": -1
    }
    quant_signal2 = {
        "score": 8.5,
        "factors": {}
    }
    result2 = engine.fuse_signals(ntdf_signal2, quant_signal2, market_env="震荡")

    # 测试场景3：中等评分
    print("\n\n测试场景3: 两者都是中等评分\n")
    ntdf_signal3 = {
        "type": "TURNOVER",
        "score": 0.2,
        "direction": 0
    }
    quant_signal3 = {
        "score": 7.2,
        "factors": {}
    }
    result3 = engine.fuse_signals(ntdf_signal3, quant_signal3, market_env="弱势")

    print("\n\n✅ 所有测试完成！\n")
