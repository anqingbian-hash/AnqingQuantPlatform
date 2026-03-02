#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一量化平台 - 本地数据版本
解决网络问题，使用本地数据源
"""

import sys
import os
import warnings
warnings.filterwarnings('ignore')

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.local_data_source import LocalDataSource
from modules.signal_fusion_engine import SignalFusionEngine

class UnifiedQuantPlatformLocal:
    """统一量化平台 - 本地数据版本"""

    def __init__(self):
        """初始化本地版本"""
        print("="*70)
        print("统一量化平台 v1.1 - 本地数据版本")
        print("解决网络问题，使用本地数据源")
        print("="*70)

        # 初始化本地数据源
        self.data_source = LocalDataSource()

        # 初始化信号融合引擎
        self.fusion_engine = SignalFusionEngine(mode="logical")

    def analyze_stock(self, stock_code: str):
        """
        统一分析股票（使用本地数据）

        Args:
            stock_code: 股票代码（如 600519）

        Returns:
            dict: 完整分析报告
        """
        print(f"\n{'='*70}")
        print(f"📊 统一量化分析: {stock_code}")
        print(f"{'='*70}")

        # 1. 获取本地股票数据
        print("\n[1/5] 获取本地股票数据...")
        stock_data = self.data_source.get_stock_data(stock_code, period="daily")

        if stock_data is None or len(stock_data) == 0:
            print("❌ 无法获取股票数据")
            return None

        # 2. 计算 NTDF 信号
        print("\n[2/5] 计算 NTDF 数字净量信号...")
        ntdf_signal = self._calculate_ntdf_signal(stock_data)

        # 3. 计算 Quant Trading 信号
        print("\n[3/5] 计算 Quant Trading 8因子信号...")
        quant_signal = self._calculate_quant_signal(stock_data)

        # 4. 判断市场环境
        print("\n[4/5] 判断大盘环境...")
        market_data = self.data_source.get_market_data("A股大盘")
        market_env = market_data['environment'] if market_data else "震荡"
        market_threshold = market_data.get('threshold', 9.0)

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

        # 获取最近数据
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
        if delta > 50000:
            signal_type = "BREAKOUT"
            signal_dir = 1
            signal_score = 0.75
        elif delta < -50000:
            signal_type = "REVERSAL"
            signal_dir = -1
            signal_score = 0.60
        elif recent_volume > 2000000:
            signal_type = "TURNOVER"
            signal_dir = 0
            signal_score = 0.45
        else:
            signal_type = "NONE"
            signal_dir = 0
            signal_score = 0.30

        return {
            "type": signal_type,
            "score": signal_score,
            "direction": signal_dir,
            "delta_value": delta
        }

    def _calculate_quant_signal(self, data):
        """计算 Quant Trading 8因子信号（简化版本）"""
        close = data['close'].values
        volume = data['volume'].values

        if len(close) < 10:
            return None

        # 简化的因子计算
        # 动量指标
        momentum = 0
        if len(close) >= 5:
            momentum = (close[-1] - close[-5]) / close[-5]

        # 均线偏离
        ma_deviation = 0
        if len(close) >= 20:
            ma = close[-20:].mean()
            ma_deviation = (close[-1] - ma) / ma

        # 成交量趋势
        volume_trend = 0
        if len(volume) >= 5:
            recent_avg = volume[-5:].mean()
            past_avg = volume[-20:-5].mean()
            volume_trend = (recent_avg - past_avg) / past_avg

        # 波动率
        volatility = 0
        if len(close) >= 20:
            returns = np.diff(np.log(close[-20:]))
            volatility = np.std(returns)

        # MACD
        macd_signal = 0
        if len(close) >= 26:
            ema12 = pd.Series(close).ewm(span=12).mean().values[-1]
            ema26 = pd.Series(close).ewm(span=26).mean().values[-1]
            dif = ema12 - ema26
            macd_signal = 1.0 if dif > 0 else -1.0

        # 综合评分（简化）
        momentum_score = min(max(momentum * 10, -1), 1) * 0.25
        ma_score = min(max(ma_deviation * 10, -1), 1) * 0.20
        volume_score = min(max(volume_trend * 5, -1), 1) * 0.15
        volatility_score = min(max(volatility * 10, -1), 1) * 0.10
        macd_score = macd_signal * 0.10

        total_score = momentum_score + ma_score + volume_score + volatility_score + macd_score

        return {
            "score": min(total_score * 10, 10),
            "factors": {
                "momentum": momentum,
                "ma_deviation": ma_deviation,
                "volume_trend": volume_trend,
                "volatility": volatility,
                "macd": macd_signal
            }
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
            "data_source": "local",
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
        print(f"   数据源: {report['data_source']}")
        print(f"   大盘环境: {report['market_environment']}")

        # NTDF 信号
        if report['ntdf_signal']:
            print(f"\n📊 NTDF 数字净量信号:")
            print(f"   信号类型: {report['ntdf_signal']['type']}")
            print(f"   方向: {report['ntdf_signal']['direction']}")
            print(f"   评分: {report['ntdf_signal']['score']:.2f}")

        # Quant Trading 信号
        if report['quant_signal']:
            print(f"\n📊 Quant Trading 8因子信号:")
            print(f"   综合评分: {report['quant_signal']['score']:.2f}/10")
            factors = report['quant_signal']['factors']
            print(f"   动量: {factors['momentum']:.2f}")
            print(f"   均线偏离: {factors['ma_deviation']:.2f}")
            print(f"   成交量: {factors['volume_trend']:.2f}")
            print(f"   波动率: {factors['volatility']:.2f}")
            print(f"   MACD: {factors['macd']:.2f}")

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
    print("\n🧪 统一量化平台 - 本地数据版本测试\n")

    platform = UnifiedQuantPlatformLocal()

    # 测试分析
    print("1️⃣ 分析贵州茅台 (600519)...\n")
    report1 = platform.analyze_stock("600519")

    print("\n2️⃣ 分析五粮液 (000858)...\n")
    report2 = platform.analyze_stock("000858")

    print("\n✅ 所有测试完成！\n")
