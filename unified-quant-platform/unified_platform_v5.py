#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一量化平台 v5.0 - 最终版
整合 NTDF v2 + Quant Trading v2 + 多数据源 + 资金流向分析 + AI 选股
"""

import sys
import os
import warnings
warnings.filterwarnings('ignore')

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.data_manager_v5 import UnifiedDataManagerV5
from modules.signal_fusion_v2 import SignalFusionEngineV2
from modules.ai_stock_picker_v2 import AIStockPickerV2

class UnifiedQuantPlatformV5:
    """统一量化平台 v5.0 - 最终版"""

    def __init__(self, primary="akshare", fallback="efinance", tertiary="tushare"):
        """初始化"""
        print("="*70)
        print("统一量化平台 v5.0 - 初始化")
        print("="*70)

        # 初始化统一数据管理器 v5
        self.dm = UnifiedDataManagerV5(
            primary=primary,
            fallback=fallback,
            tertiary=tertiary
        )

        # 初始化信号融合引擎 v2
        self.fusion_engine = SignalFusionEngineV2()

        # 初始化 AI 选股系统 v2
        self.ai_picker = AIStockPickerV2()

        print(f"\n✅ 数据管理器 v5 初始化完成")
        print(f"   主数据源: {self.dm.primary}")
        print(f"   备用数据源: {self.dm.fallback}")
        print(f"   第三数据源: {self.dm.tertiary}")
        print(f"\n✅ 信号融合引擎 v2 初始化完成")
        print(f"   NTDF v2: 7 种信号类型")
        print(f"   Quant Trading v2: 8 个因子")
        print(f"   资金流向分析: ✅")
        print(f"   技术形态识别: ✅")
        print(f"\n✅ AI 选股系统 v2 初始化完成")
        print(f"   智能筛选: ✅")
        print(f"   多维度评分: ✅")
        print(f"   推荐等级: ✅")

    def analyze_stock(self, stock_code):
        """
        分析单只股票

        Args:
            stock_code: 股票代码
        """
        print(f"\n{'='*70}")
        print(f"📊 统一量化分析: {stock_code}")
        print(f"{'='*70}")

        # 获取股票数据
        stock_data = self.dm.get_stock_data(stock_code, period="daily", prefer_real_data=True)

        if stock_data is None or len(stock_data) == 0:
            print("❌ 无法获取股票数据")
            return None

        # 获取大盘数据
        market_data = self.dm.get_market_data("A股大盘")

        # 融合信号
        fusion_result = self.fusion_engine.fuse_signals(stock_data, market_data)

        # 生成报告
        report = self._generate_report(stock_code, stock_data, fusion_result, market_data)

        self._print_full_report(report)

        return report

    def scan_market(self, threshold=6.5, limit=10):
        """
        扫描市场股票

        Args:
            threshold: 评分阈值（默认6.5）
            limit: 返回数量
        """
        print(f"\n{'='*70}")
        print(f"🔍 市场扫描...")

        # 获取大盘环境
        market_data = self.dm.get_market_data("A股大盘")
        if not market_data or market_data.get('data') is None:
            print("❌ 无法获取大盘环境")
            return []

        # 扫描股票池
        stock_codes = ["600519", "000858", "002475", "600036", "000001", "000002", "601318"][:limit]

        # 分析每只股票
        recommendations = []
        for stock_code in stock_codes:
            print(f"\n分析股票: {stock_code}")
            analysis = self.analyze_stock(stock_code)
            if analysis:
                score = analysis.get('fusion_result', {}).get('fusion_score', 0)
                if score >= threshold:
                    recommendations.append(analysis)

        # 排序
        recommendations_sorted = sorted(
            recommendations,
            key=lambda x: x.get('fusion_result', {}).get('fusion_score', 0),
            reverse=True
        )

        print(f"\n{'='*70}")
        print(f"✅ 扫描完成，找到 {len(recommendations_sorted)} 只符合条件（阈值: {threshold}）")
        print(f"{'='*70}")

        for i, stock in enumerate(recommendations_sorted[:10], 1):
            print(f"\n[{i}] {stock['stock_name']} ({stock['stock_code']})")
            print(f"    综合评分: {stock.get('fusion_result', {}).get('fusion_score', 0):.2f}/10")
            print(f"    买卖建议: {stock.get('fusion_result', {}).get('recommendation', {}).get('action', '❌')}")
            print(f"    信心度: {stock.get('fusion_result', {}).get('recommendation', {}).get('confidence', '❌')}")
            print(f"    资金流向: {stock.get('fusion_result', {}).get('money_flow', {}).get('flow_direction', 'N/A')}")
            print(f"    技术形态: {stock.get('fusion_result', {}).get('technical_pattern', {}).get('pattern', 'N/A')}")

        return recommendations_sorted

    def ai_pick_stocks(self, stock_list=None, min_score=6.5):
        """
        AI 智能选股

        Args:
            stock_list: 股票代码列表（默认使用预设股票池）
            min_score: 最小评分阈值
        """
        print(f"\n{'='*70}")
        print(f"🤖 AI 智能选股")

        # 使用预设股票池
        if stock_list is None:
            stock_list = ["600519", "000858", "002475", "600036", "000001", "000002", "601318"]

        # 获取大盘数据
        market_data = self.dm.get_market_data("A股大盘")

        # 筛选股票
        recommendations = self.ai_picker.screen_stocks(stock_list, market_data)

        # 生成报告
        report = self.ai_picker.generate_report(recommendations)
        print("\n" + report)

        return recommendations

    def _generate_report(self, stock_code, stock_data, fusion_result, market_data):
        """生成完整报告"""
        latest = stock_data.iloc[-1]

        return {
            "stock_code": stock_code,
            "stock_name": self._get_stock_name(stock_code),
            "latest_price": float(latest['close']),
            "price_change": float((latest['close'] - latest['open']) / latest['open'] * 100),
            "volume": int(latest['volume']),
            "fusion_result": fusion_result,
            "market_environment": market_data.get('environment') if market_data else '未知',
            "data_source": self.dm.current_source,
            "analysis_time": fusion_result.get('timestamp', '')
        }

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
        return name_map.get(stock_code, f"股票{stock_code}")

    def _print_full_report(self, report):
        """打印完整报告"""
        print(f"\n{'='*70}")
        print(f"📊 统一量化分析报告 - {report['stock_name']} ({report['stock_code']})")
        print(f"{'='*70}")

        # 基本信息
        print(f"\n📈 基本信息:")
        print(f"   当前价格: {report['latest_price']:.2f}")
        print(f"   涨跌幅: {report['price_change']:+.2f}%")
        print(f"   成交量: {report['volume']:,}")

        # 融合结果
        fusion_result = report.get('fusion_result')
        if fusion_result:
            recommendation = fusion_result.get('recommendation', {})
            components = fusion_result.get('components', {})
            market_env = fusion_result.get('market_environment', {})

            print(f"\n🔀 融合评分: {fusion_result.get('fusion_score', 0):.2f}/10")
            print(f"\n💡 买卖建议: {recommendation.get('action', '❌')}")
            print(f"   信心度: {recommendation.get('confidence', '❌')}")
            print(f"   原因: {recommendation.get('reason', 'N/A')}")

            print(f"\n📈 各组成部分:")
            print(f"   NTDF 信号: {components.get('ntdf_score', 0):.2f}/10 (权重: {components.get('ntdf_weight', 0):.0%})")
            print(f"   Quant 8因子: {components.get('quant_score', 0):.2f}/10 (权重: {components.get('quant_weight', 0):.0%})")

            money_flow = fusion_result.get('money_flow')
            if money_flow:
                print(f"   资金流向: {money_flow.get('flow_direction', 'N/A')} (权重: {components.get('money_flow_weight', 0):.0%})")

            technical_pattern = fusion_result.get('technical_pattern')
            if technical_pattern:
                print(f"   技术形态: {technical_pattern.get('pattern', 'N/A')} (权重: {components.get('technical_pattern_weight', 0):.0%})")

            print(f"\n📊 市场环境:")
            print(f"   环境: {market_env.get('environment', 'N/A')}")
            print(f"   趋势: {market_env.get('trend', 'N/A')}")
            print(f"   因子: {market_env.get('factor', 1.0):.2f}")

        # NTDF 信号详情
        ntdf_signal = fusion_result.get('ntdf_signal') if fusion_result else None
        if ntdf_signal:
            print(f"\n📊 NTDF 信号详情:")
            print(f"   信号类型: {ntdf_signal.get('type', 'N/A')}")
            print(f"   Delta 值: {ntdf_signal.get('delta_value', 0):.2f}")
            print(f"   信心度: {ntdf_signal.get('confidence', 'N/A')}")

            volume_anomaly = ntdf_signal.get('volume_anomaly')
            if volume_anomaly:
                print(f"   成交量异常: {volume_anomaly.get('anomaly_level', 'N/A')} ({volume_anomaly.get('ratio_5', 0):.2f}倍)")

            price_position = ntdf_signal.get('price_position')
            if price_position:
                print(f"   价格位置: {price_position.get('position_level', 'N/A')} ({price_position.get('position', 0)*100:.1f}%)")

        # Quant 因子详情
        quant_factors = fusion_result.get('quant_factors') if fusion_result else None
        if quant_factors:
            print(f"\n📊 Quant 8因子详情:")

            factor_analysis = self.fusion_engine.quant_factors.get_factor_analysis(quant_factors)
            if factor_analysis:
                print(f"   综合评分: {factor_analysis.get('total_score', 0):.2f}/10")
                print(f"   最强因子: {factor_analysis.get('strongest_factor', 'N/A')} (评分: {factor_analysis.get('strongest_score', 0):.2f})")
                print(f"   最弱因子: {factor_analysis.get('weakest_factor', 'N/A')} (评分: {factor_analysis.get('weakest_score', 0):.2f})")

        # 市场环境
        print(f"\n📊 市场环境: {report.get('market_environment', 'N/A')}")

        # 数据源
        print(f"\n🔧 数据源: {report.get('data_source', 'N/A')}")

        # 分析时间
        print(f"\n⏰ 分析时间: {report.get('analysis_time', 'N/A')}")

        print(f"\n" + "="*70)
        print("✅ 报告生成完成")
        print("="*70 + "\n")


if __name__ == "__main__":
    # 测试代码
    print("\n测试统一量化平台 v5.0\n")

    platform = UnifiedQuantPlatformV5(
        primary="akshare",
        fallback="efinance",
        tertiary="tushare"
    )

    # 测试贵州茅台
    print("1️⃣ 分析贵州茅台 (600519)...\n")
    result1 = platform.analyze_stock("600519")

    print("\n✅ 所有测试完成！\n")
