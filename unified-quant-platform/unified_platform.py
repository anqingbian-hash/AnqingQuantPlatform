#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一量化平台 - 主程序
整合 NTDF + Quant Trading 系统
"""

import sys
import os
import warnings
warnings.filterwarnings('ignore')

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.data_source_manager import UnifiedDataManager
from modules.signal_fusion_engine import SignalFusionEngine

class UnifiedQuantPlatform:
    """统一量化平台"""

    def __init__(self):
        """初始化统一平台"""
        print("="*70)
        print("统一量化平台 v1.0 - 初始化")
        print("整合 NTDF 数字净量系统 + Quant Trading 8因子系统")
        print("="*70)

        # 初始化数据管理器
        self.data_manager = UnifiedDataManager(
            primary="akshare",
            fallback="efinance"
        )

        # 初始化信号融合引擎
        self.fusion_engine = SignalFusionEngine(mode="logical")

    def analyze_stock(self, stock_code: str):
        """
        统一分析股票（使用 NTDF + Quant Trading 双系统）

        Args:
            stock_code: 股票代码（如 600519）

        Returns:
            dict: 完整分析报告
        """
        print(f"\n{'='*70}")
        print(f"📊 统一量化分析: {stock_code}")
        print(f"{'='*70}")

        # 1. 获取股票数据
        print("\n[1/4] 获取股票数据...")
        stock_data = self.data_manager.get_stock_data(
            stock_code,
            period="daily"
        )

        if stock_data is None or len(stock_data) == 0:
            print("❌ 无法获取股票数据")
            return None

        # 2. 计算 NTDF 信号
        print("\n[2/4] 计算 NTDF 数字净量信号...")
        ntdf_signal = self._calculate_ntdf_signal(stock_data)

        # 3. 计算 Quant Trading 信号
        print("\n[3/4] 计算 Quant Trading 8因子信号...")
        quant_signal = self._calculate_quant_signal(stock_data)

        # 4. 判断市场环境
        print("\n[4/4] 判断大盘环境...")
        market_env = self._judge_market_environment()

        # 5. 融合信号
        print("\n[5/5] 信号融合分析...")
        fusion_result = self.fusion_engine.fuse_signals(
            ntdf_signal,
            quant_signal,
            market_env
        )

        # 6. 生成完整报告
        report = self._generate_report(
            stock_code,
            stock_data,
            ntdf_signal,
            quant_signal,
            fusion_result,
            market_env
        )

        # 7. 打印报告
        self._print_full_report(report)

        return report

    def _calculate_ntdf_signal(self, data):
        """计算 NTDF 信号（简化版本）"""
        close = data['close'].values
        volume = data['volume'].values

        # 简化 Delta 计算
        if len(close) < 5:
            return None

        # Delta = (收盘价 - 开盘价) / (最高价 - 最低价) × 成交量
        if len(data) >= 5:
            recent_close = close[-1]
            recent_open = data['open'].iloc[-1]
            recent_high = data['high'].iloc[-1]
            recent_low = data['low'].iloc[-1]
            recent_volume = volume[-1]

            # 简化 Delta
            high_low_diff = recent_high - recent_low
            if high_low_diff > 0:
                delta = (recent_close - recent_open) / high_low_diff * recent_volume
            else:
                delta = 0

            # 信号类型判断
            if delta > 100000:  # 简化阈值
                signal_type = "BREAKOUT"
                signal_dir = 1  # 多头
                signal_score = 0.75  # 简化评分
            elif delta < -50000:
                signal_type = "REVERSAL"
                signal_dir = -1  # 空头
                signal_score = 0.60  # 简化评分
            else:
                signal_type = "TURNOVER"
                signal_dir = 0  # 中性
                signal_score = 0.30  # 简化评分

            return {
                "type": signal_type,
                "score": signal_score,
                "direction": signal_dir,
                "delta_value": delta
            }

        return None

    def _calculate_quant_signal(self, data):
        """计算 Quant Trading 8因子信号（简化版本）"""
        close = data['close'].values
        volume = data['volume'].values

        if len(close) < 10:
            return None

        # 简化的因子计算
        # 动量指标
        if len(close) >= 5:
            momentum = (close[-1] - close[-5]) / close[-5]
        else:
            momentum = 0

        # 成交量趋势
        if len(volume) >= 5:
            recent_vol = volume[-5:].mean()
            past_vol = volume[-20:-5].mean() if len(volume) >= 20 else volume[:-5].mean()
            volume_trend = (recent_vol - past_vol) / past_vol if past_vol > 0 else 0
        else:
            volume_trend = 0

        # 综合评分（简化）
        momentum_score = min(max(momentum * 10, -1), 1) * 0.4
        volume_score = min(max(volume_trend * 5, -1), 1) * 0.3
        total_score = 0.5 + momentum_score + volume_score

        return {
            "score": min(total_score * 10, 10),
            "factors": {
                "momentum": momentum,
                "volume_trend": volume_trend
            }
        }

    def _judge_market_environment(self):
        """判断大盘环境（简化版本）"""
        # 随机模拟（实际应该获取真实大盘数据）
        import random
        up_ratio = random.uniform(0.3, 0.7)

        if up_ratio > 0.6:
            return "强势"
        elif up_ratio > 0.4:
            return "震荡"
        else:
            return "弱势"

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
            "analysis_time": fusion_result['timestamp']
        }

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
        print(f"   大盘环境: {report['market_environment']}")

        # NTDF 信号
        if report['ntdf_signal']:
            print(f"\n📊 NTDF 数字净量信号:")
            print(f"   信号类型: {report['ntdf_signal']['type']}")
            print(f"   方向: {report['ntdf_signal']['direction']}")
            print(f"   Delta 值: {report['ntdf_signal']['delta_value']:.2f}")
            print(f"   评分: {report['ntdf_signal']['score']:.2f}")

        # Quant Trading 信号
        if report['quant_signal']:
            print(f"\n📊 Quant Trading 8因子信号:")
            print(f"   综合评分: {report['quant_signal']['score']:.2f}/10")

        # 融合结果
        if report['fusion_result']:
            print(f"\n🔀 信号融合结果:")
            print(f"   融合模式: {report['fusion_result']['fusion_mode']}")
            print(f"   融合评分: {report['fusion_result']['fusion_score']:.2f}")
            print(f"   买卖建议: {report['fusion_result']['recommendation']['action']}")
            print(f"   评级: {report['fusion_result']['recommendation']['level']}")
            print(f"   信心度: {report['fusion_result']['recommendation']['confidence']}")
            if 'reason' in report['fusion_result']['recommendation']:
                print(f"   原因: {report['fusion_result']['recommendation']['reason']}")

        print(f"\n⏰ 分析时间: {report['analysis_time']}")
        print(f"{'='*70}\n")


if __name__ == "__main__":
    # 测试代码
    print("\n🧪 统一量化平台 - 测试模式\n")

    platform = UnifiedQuantPlatform()

    # 测试分析
    print("1️⃣  分析贵州茅台 (600519)...\n")
    report1 = platform.analyze_stock("600519")

    print("\n2️⃣  分析五粮液 (000858)...\n")
    report2 = platform.analyze_stock("000858")

    print("\n✅ 所有测试完成！\n")
