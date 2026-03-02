#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 选股系统 v2.0
整合 Quant Trading 8因子和 NTDF 信号，提供智能股票筛选
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

class AIStockPickerV2:
    """AI 选股系统 v2.0"""

    def __init__(self):
        """初始化 AI 选股系统"""
        print("="*70)
        print("AI 选股系统 v2.0 - 初始化")
        print("="*70)

        # 初始化信号计算器
        self.quant_factors = QuantFactorsV2()
        self.ntdf_signal = NtdfSignalV2()

        # 筛选条件
        self.criteria = {
            "min_fusion_score": 6.5,      # 最小融合评分
            "min_quant_score": 5.0,        # 最小 Quant 评分
            "min_ntdf_score": 0.3,         # 最小 NTDF 评分
            "min_volume_anomaly": 0.0,     # 最小成交量异常
            "max_price_position": 0.9,     # 最大价格位置（避免高位接盘）
            "min_money_flow_mfi": 20,      # 最小资金流向 MFI
            "max_money_flow_mfi": 80,      # 最大资金流向 MFI
            "preferred_patterns": ["上升通道", "低位反弹", "震荡整理"]  # 偏好形态
        }

        print(f"✅ 筛选条件:")
        print(f"   最小融合评分: {self.criteria['min_fusion_score']}")
        print(f"   最小 Quant 评分: {self.criteria['min_quant_score']}")
        print(f"   最小 NTDF 评分: {self.criteria['min_ntdf_score']}")
        print(f"   最大价格位置: {self.criteria['max_price_position']*100:.0f}%")
        print(f"   偏好形态: {', '.join(self.criteria['preferred_patterns'])}\n")

    def screen_stocks(self, stock_list, market_data=None):
        """
        筛选股票

        Args:
            stock_list: 股票代码列表
            market_data: 大盘数据（用于市场环境分析）

        Returns:
            list: 推荐股票列表
        """
        print(f"\n{'='*70}")
        print(f"🔍 AI 智能选股 - 开始筛选")
        print(f"{'='*70}")

        # 获取市场环境
        market_env = self._get_market_environment(market_data)

        print(f"\n市场环境: {market_env.get('environment', '未知')}")
        print(f"市场趋势: {market_env.get('trend', '未知')}")
        print(f"股票池: {len(stock_list)} 只")

        # 分析每只股票
        recommendations = []
        for i, stock_code in enumerate(stock_list, 1):
            print(f"\n分析 {i}/{len(stock_list)}: {stock_code}")

            # 获取股票数据
            stock_data = self._get_stock_data(stock_code)
            if stock_data is None or len(stock_data) < 20:
                print(f"   ⚠️ 数据不足，跳过")
                continue

            # 分析股票
            analysis = self._analyze_stock(stock_code, stock_data, market_env)

            # 检查是否符合条件
            if self._check_criteria(analysis):
                recommendations.append(analysis)
                print(f"   ✅ 符合条件，评分: {analysis['fusion_score']:.2f}")
            else:
                print(f"   ❌ 不符合条件，评分: {analysis['fusion_score']:.2f}")

        # 排序
        recommendations_sorted = sorted(
            recommendations,
            key=lambda x: x['fusion_score'],
            reverse=True
        )

        print(f"\n{'='*70}")
        print(f"✅ 筛选完成，找到 {len(recommendations_sorted)} 只符合条件")
        print(f"{'='*70}")

        return recommendations_sorted

    def _get_stock_data(self, stock_code):
        """
        获取股票数据（简化版，使用本地数据源）

        Args:
            stock_code: 股票代码

        Returns:
            pd.DataFrame: 股票K线数据
        """
        # 这里简化处理，使用本地数据源
        # 在实际应用中，应该使用统一数据管理器 v5
        from modules.local_data_source_v2 import LocalDataSource
        data_source = LocalDataSource()
        return data_source.get_stock_data(stock_code, period="daily")

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
                "trend": "未知",
                "factor": 1.0
            }

        environment = market_data.get('environment', '震荡')
        up_ratio = market_data.get('up_ratio', 0.5)

        # 判断趋势
        if up_ratio > 0.6:
            trend = "上涨"
            factor = 1.2
        elif up_ratio > 0.4:
            trend = "震荡"
            factor = 1.0
        else:
            trend = "下跌"
            factor = 0.8

        return {
            "environment": environment,
            "trend": trend,
            "up_ratio": up_ratio,
            "factor": factor
        }

    def _analyze_stock(self, stock_code, stock_data, market_env):
        """
        分析股票

        Args:
            stock_code: 股票代码
            stock_data: 股票K线数据
            market_env: 市场环境

        Returns:
            dict: 分析结果
        """
        # 计算 Quant 8因子
        quant_factors = self.quant_factors.calculate_all_factors(stock_data)
        quant_score = self.quant_factors.calculate_total_score(quant_factors)

        # 计算 NTDF 信号
        ntdf_signal = self.ntdf_signal.calculate_signal(stock_data)
        ntdf_score = ntdf_signal.get('score', 0) if ntdf_signal else 0

        # 计算融合评分
        market_factor = market_env.get('factor', 1.0)
        fusion_score = (quant_score * 0.7 + ntdf_score * 0.3) * market_factor
        fusion_score = min(max(fusion_score, 0), 10)

        # 生成推荐等级
        if fusion_score >= 8.5:
            recommendation = "STRONG_BUY"
            level = "3星"
            reason = "多个指标均显示强势，强烈建议买入"
        elif fusion_score >= 7.5:
            recommendation = "BUY"
            level = "2星"
            reason = "指标偏向多头，建议买入"
        elif fusion_score >= 6.5:
            recommendation = "WEAK_BUY"
            level = "1星"
            reason = "指标偏向多头，可适量买入"
        elif fusion_score >= 5.0:
            recommendation = "HOLD"
            level = "0星"
            reason = "信号中性，建议观望"
        elif fusion_score >= 3.5:
            recommendation = "WEAK_SELL"
            level = "风险1"
            reason = "指标偏向空头，可适量卖出"
        else:
            recommendation = "SELL"
            level = "风险2"
            reason = "指标偏向空头，建议卖出"

        return {
            "stock_code": stock_code,
            "stock_name": self._get_stock_name(stock_code),
            "fusion_score": fusion_score,
            "quant_score": quant_score,
            "ntdf_score": ntdf_score,
            "recommendation": recommendation,
            "level": level,
            "reason": reason,
            "quant_factors": quant_factors,
            "ntdf_signal": ntdf_signal,
            "market_env": market_env
        }

    def _check_criteria(self, analysis):
        """
        检查是否符合筛选条件

        Args:
            analysis: 分析结果

        Returns:
            bool: 是否符合条件
        """
        # 融合评分
        fusion_score = analysis.get('fusion_score', 0)
        if fusion_score < self.criteria['min_fusion_score']:
            return False

        # Quant 评分
        quant_score = analysis.get('quant_score', 0)
        if quant_score < self.criteria['min_quant_score']:
            return False

        # NTDF 评分
        ntdf_score = analysis.get('ntdf_score', 0)
        if ntdf_score < self.criteria['min_ntdf_score']:
            return False

        # 价格位置
        ntdf_signal = analysis.get('ntdf_signal')
        if ntdf_signal:
            price_position = ntdf_signal.get('price_position', {})
            if price_position:
                position = price_position.get('position', 0.5)
                if position > self.criteria['max_price_position']:
                    return False

        # 资金流向 MFI
        quant_factors = analysis.get('quant_factors')
        if quant_factors:
            money_flow = quant_factors.get('money_flow', {})
            if money_flow:
                mfi = money_flow.get('mfi', 50)
                if mfi < self.criteria['min_money_flow_mfi'] or mfi > self.criteria['max_money_flow_mfi']:
                    return False

        return True

    def _get_stock_name(self, stock_code):
        """获取股票名称"""
        name_map = {
            "600519": "贵州茅台",
            "000858": "五粮液",
            "002475": "立讯精密",
            "600036": "招商银行",
            "000001": "平安银行",
            "000002": "万科A",
            "601318": "中国平安"
        }
        return name_map.get(str(stock_code), f"股票{stock_code}")

    def generate_report(self, recommendations):
        """
        生成选股报告

        Args:
            recommendations: 推荐股票列表

        Returns:
            str: 选股报告
        """
        report = []

        report.append("="*70)
        report.append("📊 AI 智能选股报告")
        report.append("="*70)

        report.append(f"\n推荐股票: {len(recommendations)} 只")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        if len(recommendations) == 0:
            report.append("\n⚠️ 没有找到符合条件的股票")
            report.append("建议：")
            report.append("   1. 降低筛选条件")
            report.append("   2. 扩大股票池")
            report.append("   3. 等待市场环境改善")
            return "\n".join(report)

        # 推荐股票列表
        report.append("\n" + "="*70)
        report.append("📈 推荐股票列表")
        report.append("="*70)

        for i, stock in enumerate(recommendations[:10], 1):
            report.append(f"\n[{i}] {stock['stock_name']} ({stock['stock_code']})")
            report.append(f"    综合评分: {stock['fusion_score']:.2f}/10")
            report.append(f"    评分等级: {stock['level']}")
            report.append(f"    推荐操作: {stock['recommendation']}")
            report.append(f"    推荐理由: {stock['reason']}")

            # Quant 因子详情
            quant_factors = stock.get('quant_factors')
            if quant_factors:
                factor_analysis = self.quant_factors.get_factor_analysis(quant_factors)
                if factor_analysis:
                    report.append(f"    最强因子: {factor_analysis.get('strongest_factor', 'N/A')}")

            # NTDF 信号详情
            ntdf_signal = stock.get('ntdf_signal')
            if ntdf_signal:
                volume_anomaly = ntdf_signal.get('volume_anomaly')
                if volume_anomaly:
                    report.append(f"    成交量异常: {volume_anomaly.get('anomaly_level', 'N/A')}")

        # 统计信息
        report.append("\n" + "="*70)
        report.append("📊 统计信息")
        report.append("="*70)

        if len(recommendations) > 0:
            scores = [stock['fusion_score'] for stock in recommendations]
            report.append(f"\n最高评分: {max(scores):.2f}")
            report.append(f"最低评分: {min(scores):.2f}")
            report.append(f"平均评分: {np.mean(scores):.2f}")

        # 等级分布
        level_count = {}
        for stock in recommendations:
            level = stock.get('level', 'N/A')
            level_count[level] = level_count.get(level, 0) + 1

        report.append(f"\n等级分布:")
        for level, count in sorted(level_count.items(), key=lambda x: x[0], reverse=True):
            report.append(f"   {level}: {count} 只")

        report.append("\n" + "="*70)

        return "\n".join(report)


if __name__ == "__main__":
    # 测试代码
    print("AI 选股系统 v2.0 测试")

    # 创建 AI 选股系统
    ai_picker = AIStockPickerV2()

    # 股票池
    stock_list = ["600519", "000858", "002475", "600036", "000001", "000002", "601318"]

    # 筛选股票
    recommendations = ai_picker.screen_stocks(stock_list)

    # 生成报告
    report = ai_picker.generate_report(recommendations)
    print("\n" + report)

    print("\n所有测试完成")
