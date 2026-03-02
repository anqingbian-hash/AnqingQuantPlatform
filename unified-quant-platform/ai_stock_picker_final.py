#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 殗力选股测试脚本 - 最终版本
"""

import sys
import os
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.local_data_source_v2 import LocalDataSource

class AIStockPickerFinal:
    """AI 殗力选股"""

    def __init__(self):
        print("="*50)
        print("AI 殗力选股系统")
        print("="*50)

        self.data_source = LocalDataSource()
        self.criteria = {
            "min_score": 7.0,
            "min_momentum": 0.3,
            "min_volume_trend": 0.2,
            "min_change": -3.0,
            "max_change": 10.0
        }

    def screen_stocks(self, stock_list=None):
        print("\n开始筛选股票...")

        if stock_list is None:
            stock_list = [
                "600519",
                "000858",
                "002475",
                "600036",
                "000001",
                "000002",
                "601318"
            ]

        print(f"   股票池: {len(stock_list)} 只")

        recommendations = []
        for stock_code in stock_list:
            stock_data = self.data_source.get_stock_data(stock_code, period="daily")
            if stock_data is None or len(stock_data) < 20:
                continue

            analysis = self._analyze_stock(stock_code, stock_data)

            if analysis['score'] >= self.criteria['min_score']:
                recommendations.append(analysis)

        print(f"\n筛选完成，找到 {len(recommendations)} 只符合条件")

        recommendations_sorted = sorted(
            recommendations,
            key=lambda x: x['score'],
            reverse=True
        )

        return recommendations_sorted

    def _analyze_stock(self, stock_code, data):
        close = data['close'].values
        volume = data['volume'].values

        if len(close) >= 10:
            momentum_5 = (close[-1] - close[-5]) / close[-5]
        else:
            momentum_5 = 0

        if len(close) >= 20:
            momentum_10 = (close[-1] - close[-10]) / close[-10]
        else:
            momentum_10 = 0

        momentum_avg = (momentum_5 + momentum_10) / 2 if len(close) >= 20 else momentum_5

        if len(volume) >= 20:
            volume_recent = volume[-5:].mean()
            volume_past = volume[-20:-5].mean()
            volume_trend = (volume_recent - volume_past) / volume_past
        else:
            volume_trend = 0

        if len(data) >= 1:
            price_change = (data['close'].iloc[-1] - data['open'].iloc[-1]) / data['open'].iloc[-1] * 100
        else:
            price_change = 0

        momentum_score = min(max(momentum_avg * 10, -1), 1) * 0.4
        volume_score = min(max(volume_trend * 10, -1), 1) * 0.3
        change_score = 1.0 - min(abs(price_change) / 10.0, 1.0)  # 下跌越少得分越高

        total_score = (momentum_score + volume_score + change_score) * 10

        if total_score >= 8.5:
            recommendation = "买入"
            level = "3星"
        elif total_score >= 7.5:
            recommendation = "考虑买入"
            level = "2星"
        elif total_score >= 6.5:
            recommendation = "观望"
            level = "1星"
        else:
            recommendation = "回避"
            level = "0星"

        stock_name = self._get_stock_name(stock_code)

        return {
            "stock_code": stock_code,
            "stock_name": stock_name,
            "score": total_score,
            "recommendation": recommendation,
            "level": level,
            "momentum_5": momentum_5,
            "momentum_10": momentum_10,
            "volume_trend": volume_trend,
            "price_change": price_change
        }

    def _get_stock_name(self, stock_code):
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
        print("="*70)
        print("AI 殗力选股报告")
        print("="*70)

        print(f"\n推荐股票: {len(recommendations)} 只\n")

        for i, stock in enumerate(recommendations[:10], 1):
            print(f"\n[{i}] {stock['stock_name']} ({stock['stock_code']})")
            print(f"    综合评分: {stock['score']:.2f}/10")
            print(f"    买卖建议: {stock['recommendation']} [{stock['level']}]")
            print(f"    详情:")
            print(f"      动量5日: {stock['momentum_5']:.3f}")
            print(f"      动量10日: {stock['momentum_10']:.3f}")
            print(f"      成交趋势: {stock['volume_trend']:+.3f}")
            print(f"      价格变化: {stock['price_change']:+.2f}%")

        print("\n" + "="*70)
        print("选股报告生成完成")
        print("="*70)

        return recommendations

    def run(self, stock_list=None):
        print("运行 AI 殗力选股系统")

        recommendations = self.screen_stocks(stock_list)

        if not recommendations:
            print("未找到符合条件的股票")
            return None

        self.generate_report(recommendations)

        return recommendations


if __name__ == "__main__":
    picker = AIStockPickerFinal()

    print("\n开始运行 AI 殗力选股...")

    recommendations = picker.run()

    print("\n选股完成！")
