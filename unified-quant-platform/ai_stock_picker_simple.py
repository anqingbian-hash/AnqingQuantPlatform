#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 殗力选股测试脚本
简化版本，修复 indent 问题
"""

import sys
import os
import warnings
warnings.filterwarnings('ignore')

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.local_data_source import LocalDataSource

class AIStockPicker:
    """AI 算力选股"""

    def __init__(self):
        """初始化"""
        print("="*50)
        print("AI 算力选股系统")
        print("="*50)

        self.data_source = LocalDataSource()

        # 选股标准
        self.criteria = {
            "min_score": 7.0,
            "min_momentum": 0.3,
            "min_volume_trend": 0.2,
            "min_change": -3.0,
            "max_change": 10.0
        }

    def screen_stocks(self, stock_list=None):
        """
        筛选股票

        Args:
            stock_list: 股票代码列表

        Returns:
            list: 推荐股票列表
        """
        print("\n开始筛选股票...")

        # 默认股票池
        if stock_list is None:
            stock_list = [
                "600519",
                "000858",
                "002475",
                "600036",
                "000001"
            ]

        print(f"   股票池: {len(stock_list)} 只")

        # 分析每只股票
        recommendations = []
        for stock_code in stock_list:
            stock_data = self.data_source.get_stock_data(stock_code, period="daily")
            if stock_data is None or len(stock_data) < 20:
                continue

            # 计算指标
            analysis = self._analyze_stock(stock_code, stock_data)

            if analysis['score'] >= self.criteria['min_score']:
                recommendations.append(analysis)

        print(f"\n筛选完成，找到 {len(recommendations)} 只符合条件")

        # 排序推荐
        recommendations_sorted = sorted(
            recommendations,
            key=lambda x: x['score'],
            reverse=True
        )

        return recommendations_sorted

    def _analyze_stock(self, stock_code, data):
        """分析单只股票"""
        close = data['close'].values
        volume = data['volume'].values

        # 计算动量（5日/10日）
        if len(close) >= 10:
            momentum_5 = (close[-1] - close[-5]) / close[-5]
            momentum_10 = (close[-1] - close[-10]) / close[-10]
            momentum_avg = (momentum_5 + momentum_10) / 2
        else:
            momentum_avg = 0

        # 计算成交量趋势
        if len(volume) >= 20:
            volume_recent = volume[-5:].mean()
            volume_past = volume[-20:-5].mean()
            volume_trend = (volume_recent - volume_past) / volume_past
        else:
            volume_trend = 0

        # 计算价格变化
        if len(data) >= 1:
            price_change = (data['close'].iloc[-1] - data['open'].iloc[-1]) / data['open'].iloc[-1] * 100
        else:
            price_change = 0

        # 计算波动率（20日）
        if len(close) >= 20:
            returns = np.diff(np.log(close[-20:]))
            volatility = np.std(returns)
        else:
            volatility = 0

        # 综合评分
        momentum_score = max(min(momentum_avg * 10, -1), 1) * 0.4
        volume_score = min(max(volume_trend * 10, -1), 1) * 0.2
        change_score = 1.0 - min(abs(price_change) / 10.0, 1.0)

        total_score = (momentum_score + volume_score + change_score) * 10

        # 生成建议
        reasons = []
        if momentum_avg > 0.05:
            reasons.append(f"动量强劲({momentum_avg*100:.1f}%)")
        if volume_trend > 0.2:
            reasons.append(f"放量上涨({volume_trend*100:.1f}%)")
        if abs(price_change) < 2.0:
            reasons.append(f"价格稳定({price_change:+.2f}%)")

        if total_score >= 8.5:
            recommendation = "强力买入"
            level = "3星"
        elif total_score >= 7.5:
            recommendation = "买入"
            level = "2星"
        elif total_score >= 6.5:
            recommendation = "考虑买入"
            level = "1星"
        elif total_score >= 5.0:
            recommendation = "观望"
            level = "0星"
        else:
            recommendation = "避免"
            level = "推荐"

        # 获取股票名称
        stock_name = self._get_stock_name(stock_code)

        analysis = {
            "stock_code": stock_code,
            "stock_name": stock_name,
            "score": total_score,
            "recommendation": recommendation,
            "level": level,
            "momentum_5": momentum_5 if len(close) >= 5 else 0,
            "momentum_10": momentum_10 if len(close) >= 10 else 0,
            "volume_trend": volume_trend,
            "price_change": price_change,
            "volatility": volatility,
            "reasons": reasons
        }

        return analysis

    def _get_stock_name(self, stock_code):
        """获取股票名称"""
        name_map = {
            "600519": "贵州茅台",
            "000858": "五粮液",
            "002475": "立讯精密",
            "600036": "招商银行",
            "000001": "平安银行"
        }
        return name_map.get(stock_code, f"股票{stock_code}")

    def generate_report(self, recommendations):
        """生成选股报告"""
        print("\n" + "="*70)
        print("AI 算力选股报告")
        print("="*70)

        print(f"\n推荐股票: {len(recommendations)} 只")

        for i, stock in enumerate(recommendations[:10], 1):
            print(f"\n[{i}] {stock['stock_name']} ({stock['stock_code']})")
            print(f"    综合评分: {stock['score']:.1f}/10")
            print(f"    买卖建议: {stock['recommendation']} [{stock['level']}]")

            if stock['reasons']:
                print(f"    推荐理由:")
                for reason in stock['reasons']:
                    print(f"      - {reason}")

            print(f"    动量5日: {stock['momentum_5']:.3f}")
            print(f"    动量10日: {stock['momentum_10']:.3f}")
            print(f"    成交趋势: {stock['volume_trend']:.3f}")
            print(f"    价格变化: {stock['price_change']:+.2f}%")
            print(f"    波动率: {stock['volatility']:.3f}")

        print("\n" + "="*70)
        print("选股报告生成完成")
        print("="*70)

    def run(self, stock_list=None):
        """运行选股系统"""
        print("\n运行 AI 算力选股系统")

        # 筛选股票
        recommendations = self.screen_stocks(stock_list)

        if not recommendations:
            print("未找到符合条件的股票")
            return None

        # 生成报告
        self.generate_report(recommendations)

        return recommendations


if __name__ == "__main__":
    # 创建选股系统
    picker = AIStockPicker()

    # 运行选股
    print("开始运行 AI 算力选股")

    recommendations = picker.run()

    if recommendations:
        print(f"\n成功推荐 {len(recommendations)} 只股票")
    else:
        print("\n未找到符合条件的股票")
