#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一量化平台 v3.0 - 完整版
整合 NTDF + Quant Trading + 多数据源（Local + AKShare + Efinance + Tushare + Baostock）
"""

import sys
import os
import warnings
warnings.filterwarnings('ignore')

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.data_manager_v5 import UnifiedDataManagerV5

class UnifiedQuantPlatformV3:
    """统一量化平台 v3.0 - 完整版"""

    def __init__(self, primary="akshare", fallback="efinance", tertiary="tushare"):
        """初始化"""
        print("="*70)
        print("统一量化平台 v3.0 - 初始化")
        print("="*70)

        # 初始化统一数据管理器 v5
        self.dm = UnifiedDataManagerV5(
            primary=primary,
            fallback=fallback,
            tertiary=tertiary
        )

        print(f"\n✅ 数据管理器 v5 初始化完成")
        print(f"   主数据源: {self.dm.primary}")
        print(f"   备用数据源: {self.dm.fallback}")
        print(f"   第三数据源: {self.dm.tertiary}")

    def analyze_stock(self, stock_code):
        """
        分析单只股票

        Args:
            stock_code: 股票代码
        """
        print(f"\n{'='*70}")
        print(f"📊 统一量化分析: {stock_code}")
        print(f"{'='*70}")

        # 获取数据
        stock_data = self.dm.get_stock_data(stock_code, period="daily", prefer_real_data=True)

        if stock_data is None or len(stock_data) == 0:
            print("❌ 无法获取股票数据")
            return None

        # 计算信号
        ntdf_signal = self._calculate_ntdf_signal(stock_data)
        quant_signal = self._calculate_quant_signal(stock_data)

        # 获取大盘环境
        market_env_obj = self.dm.get_market_data("A股大盘")
        market_env = market_env_obj.get('environment', '震荡') if market_env_obj else '震荡'

        # 融合信号
        fusion_result = self._fuse_signals(ntdf_signal, quant_signal, market_env)

        # 生成报告
        report = self._generate_report(
            stock_code,
            stock_data,
            ntdf_signal,
            quant_signal,
            fusion_result,
            market_env
        )

        self._print_full_report(report)

        return report

    def scan_market(self, threshold=8.0, limit=10):
        """
        扫描市场股票

        Args:
            threshold: 评分阈值（默认8.0）
            limit: 返回数量
        """
        print(f"\n{'='*70}")
        print(f"🔍 市场扫描...")

        # 获取大盘环境
        market_env_obj = self.dm.get_market_data("A股大盘")
        if not market_env_obj or market_env_obj.get('data') is None:
            print("❌ 无法获取大盘环境")
            return []

        # 扫描股票池
        stock_codes = ["600519", "000858", "002475", "600036", "000001", "000002", "601318"][:limit]

        # 分析每只股票
        recommendations = []
        for stock_code in stock_codes:
            analysis = self.analyze_stock(stock_code)
            if analysis:
                score = analysis.get('fusion_result', {}).get('score', 0)
                if score >= threshold:
                    recommendations.append(analysis)

        # 排序
        recommendations_sorted = sorted(
            recommendations,
            key=lambda x: x.get('fusion_result', {}).get('score', 0),
            reverse=True
        )

        print(f"\n✅ 扫描完成，找到 {len(recommendations_sorted)} 只符合条件")

        for i, stock in enumerate(recommendations_sorted[:10], 1):
            print(f"\n[{i}] {stock['stock_name']} ({stock['stock_code']})")
            print(f"    综合评分: {stock.get('fusion_result', {}).get('score', 0):.2f}/10")
            print(f"    买卖建议: {stock.get('fusion_result', {}).get('recommendation', {}).get('action', '❌')}")
            print(f"    信心度: {stock.get('fusion_result', {}).get('recommendation', {}).get('confidence', '❌')}")

        return recommendations_sorted

    def _calculate_ntdf_signal(self, data):
        """计算 NTDF 信号"""
        close = data['close'].values
        volume = data['volume'].values

        if len(close) < 5:
            return None

        # Delta 计算（简化版）
        recent_close = close[-1]
        recent_open = data['open'].iloc[-1]
        recent_high = data['high'].iloc[-1]
        recent_low = data['low'].iloc[-1]
        recent_volume = volume[-1]

        high_low_diff = recent_high - recent_low
        if high_low_diff > 0:
            delta = (recent_close - recent_open) / high_low_diff * recent_volume
        else:
            delta = 0

        # 信号类型判断
        if delta > 50000:
            signal_type = "BREAKOUT"
            signal_dir = 1
            signal_score = 0.75
        elif delta < -50000:
            signal_type = "REVERSAL"
            signal_dir = -1
            signal_score = 0.60
        elif recent_volume > 500000:
            signal_type = "TURNOVER"
            signal_dir = 0
            signal_score = 0.30
        else:
            signal_type = "NONE"
            signal_dir = 0
            signal_score = 0.0

        return {
            "type": signal_type,
            "score": signal_score,
            "direction": signal_dir,
            "delta_value": delta
        }

    def _calculate_quant_signal(self, data):
        """计算 Quant Trading 8因子信号"""
        close = data['close'].values
        volume = data['volume'].values

        if len(close) < 10:
            return None

        # 简化计算
        momentum = (close[-1] - close[-5]) / close[-5]
        ma_dev = 0
        volume_trend = 0

        momentum_score = min(max(momentum * 10, -1), 1) * 0.3
        ma_score = 0
        volume_score = min(max(volume_trend * 5, -1), 1) * 0.2

        total_score = (momentum_score + ma_score + volume_score) * 10

        return {
            "score": min(total_score, 10),
            "factors": {
                "momentum": momentum,
                "ma_dev": ma_dev,
                "volume_trend": volume_trend
            }
        }

    def _fuse_signals(self, ntdf_signal, quant_signal, market_env):
        """融合 NTDF 和 Quant Trading 信号"""
        if ntdf_signal is None or quant_signal is None:
            return {
                "score": (ntdf_signal or quant_signal or {}).get('score', 0),
                "recommendation": {
                    "action": "HOLD",
                    "confidence": "低",
                    "reason": "信号不完整"
                },
                "timestamp": self._get_timestamp()
            }

        # 融合评分
        ntdf_score = ntdf_signal.get('score', 0) * 10
        quant_score = quant_signal.get('score', 0)

        # 市场环境调整
        market_factor = 1.0
        if market_env == "强势":
            market_factor = 1.2  # 强势市场，买入信号更强
        elif market_env == "弱势":
            market_factor = 0.8  # 弱势市场，买入信号更弱
        # 震荡市场，不调整

        # 加权融合（NTDF 40%, Quant 60%）
        fusion_score = (ntdf_score * 0.4 + quant_score * 0.6) * market_factor

        # 生成买卖建议
        if fusion_score >= 8.0:
            action = "STRONG_BUY"
            confidence = "高"
            reason = "多个指标均显示强势"
        elif fusion_score >= 6.0:
            action = "BUY"
            confidence = "中高"
            reason = "指标偏向多头"
        elif fusion_score >= 4.0:
            action = "HOLD"
            confidence = "中"
            reason = "信号中性，观望"
        elif fusion_score >= 2.0:
            action = "SELL"
            confidence = "中高"
            reason = "指标偏向空头"
        else:
            action = "STRONG_SELL"
            confidence = "高"
            reason = "多个指标均显示弱势"

        return {
            "score": min(fusion_score, 10),
            "ntdf_weight": 0.4,
            "quant_weight": 0.6,
            "market_factor": market_factor,
            "market_environment": market_env,
            "recommendation": {
                "action": action,
                "confidence": confidence,
                "reason": reason
            },
            "timestamp": self._get_timestamp()
        }

    def _generate_report(self, stock_code, stock_data, ntdf_signal, quant_signal, fusion_result, market_env):
        """生成完整报告"""
        latest = stock_data.iloc[-1]

        return {
            "stock_code": stock_code,
            "stock_name": self._get_stock_name(stock_code),
            "latest_price": float(latest['close']),
            "price_change": float((latest['close'] - latest['open']) / latest['open'] * 100),
            "volume": int(latest['volume']),
            "ntdf_signal": ntdf_signal,
            "quant_signal": quant_signal,
            "fusion_result": fusion_result,
            "market_environment": market_env,
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

        # NTDF 信号
        if report['ntdf_signal']:
            print(f"\n📊 NTDF 信号:")
            print(f"   信号类型: {report['ntdf_signal'].get('type', 'N/A')}")
            print(f"   信号方向: {report['ntdf_signal'].get('direction', 0)}")
            print(f"   Delta: {report['ntdf_signal'].get('delta_value', 0):.2f}")

        # Quant Trading 信号
        if report['quant_signal']:
            print(f"\n📊 Quant Trading 信号:")
            print(f"   综合评分: {report['quant_signal'].get('score', 0):.2f}/10")

        # 融合结果
        if report['fusion_result']:
            print(f"\n🔀 信号融合结果:")
            print(f"   融合评分: {report['fusion_result'].get('score', 0):.2f}/10")
            print(f"   市场环境: {report['fusion_result'].get('market_environment', 'N/A')}")
            print(f"   市场因子: {report['fusion_result'].get('market_factor', 1.0):.2f}")

            print(f"\n💡 买卖建议: {report['fusion_result'].get('recommendation', {}).get('action', '❌')}")
            print(f"   信心度: {report['fusion_result'].get('recommendation', {}).get('confidence', '❌')}")
            if 'reason' in report['fusion_result'].get('recommendation', {}):
                print(f"   原因: {report['fusion_result'].get('recommendation', {}).get('reason', 'N/A')}")

        # 市场环境
        print(f"\n📊 市场环境: {report.get('market_environment', 'N/A')}")

        # 数据源
        print(f"\n🔧 数据源: {report.get('data_source', 'N/A')}")

        print(f"\n⏰ 分析时间: {report.get('analysis_time', 'N/A')}")

        print(f"\n" + "="*70)
        print("✅ 报告生成完成")
        print("="*70 + "\n")

    def _get_timestamp(self):
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    # 测试代码
    print("\n测试统一量化平台 v3.0\n")

    platform = UnifiedQuantPlatformV3(
        primary="akshare",
        fallback="efinance",
        tertiary="tushare"
    )

    # 测试贵州茅台
    print("1️⃣ 分析贵州茅台 (600519)...\n")
    result1 = platform.analyze_stock("600519")

    print("\n2️⃣ 测试五粮液 (000858)...\n")
    result2 = platform.analyze_stock("000858")

    print("\n✅ 所有测试完成！\n")
