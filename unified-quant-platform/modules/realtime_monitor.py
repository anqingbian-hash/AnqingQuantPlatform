#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时监控系统 v1.0
用于实时监控市场变化和信号推送
"""

import pandas as pd
import numpy as np
from datetime import datetime
import time
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_manager_v5 import UnifiedDataManagerV5
from modules.signal_fusion_v2 import SignalFusionEngineV2

class RealTimeMonitor:
    """实时监控系统 v1.0"""

    def __init__(self, primary="akshare", fallback="efinance", tertiary="tushare"):
        """
        初始化实时监控系统

        Args:
            primary: 主数据源
            fallback: 备用数据源
            tertiary: 第三数据源
        """
        print("="*70)
        print("实时监控系统 v1.0 - 初始化")
        print("="*70)

        # 初始化数据管理器
        self.dm = UnifiedDataManagerV5(
            primary=primary,
            fallback=fallback,
            tertiary=tertiary
        )

        # 初始化信号融合引擎
        self.fusion_engine = SignalFusionEngineV2()

        # 监控股票列表
        self.watchlist = []

        # 信号阈值
        self.signal_thresholds = {
            "strong_buy": 8.0,      # 强烈买入阈值
            "buy": 6.5,             # 买入阈值
            "sell": 4.0,            # 卖出阈值
            "strong_sell": 2.0      # 强烈卖出阈值
        }

        # 价格变动阈值
        self.price_change_threshold = 3.0  # 3%

        # 成交量异常阈值
        self.volume_anomaly_threshold = 2.0  # 2倍

        print(f"✅ 数据源: {self.dm.primary} → {self.dm.fallback} → {self.dm.tertiary}")
        print(f"✅ 信号阈值: 强烈买入≥{self.signal_thresholds['strong_buy']}, 买入≥{self.signal_thresholds['buy']}")
        print(f"✅ 价格变动阈值: ±{self.price_change_threshold}%")
        print(f"✅ 成交量异常阈值: {self.volume_anomaly_threshold}倍\n")

    def add_to_watchlist(self, stock_codes):
        """
        添加股票到监控列表

        Args:
            stock_codes: 股票代码列表
        """
        if isinstance(stock_codes, str):
            stock_codes = [stock_codes]

        for code in stock_codes:
            if code not in self.watchlist:
                self.watchlist.append(code)

        print(f"✅ 已添加 {len(stock_codes)} 只股票到监控列表")
        print(f"   监控列表: {', '.join(self.watchlist)}\n")

    def remove_from_watchlist(self, stock_codes):
        """
        从监控列表移除股票

        Args:
            stock_codes: 股票代码列表
        """
        if isinstance(stock_codes, str):
            stock_codes = [stock_codes]

        for code in stock_codes:
            if code in self.watchlist:
                self.watchlist.remove(code)

        print(f"✅ 已从监控列表移除 {len(stock_codes)} 只股票\n")

    def scan_once(self):
        """
        执行一次扫描

        Returns:
            list: 信号列表
        """
        print(f"\n{'='*70}")
        print(f"🔍 执行一次扫描 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")

        signals = []

        # 获取大盘环境
        market_data = self.dm.get_market_data("A股大盘")
        if market_data:
            print(f"\n📊 大盘环境: {market_data.get('environment', 'N/A')}")
            print(f"   上涨占比: {market_data.get('up_ratio', 0)*100:.1f}%")

        # 扫描每只股票
        for stock_code in self.watchlist:
            print(f"\n📈 扫描: {stock_code}")

            # 获取股票数据
            stock_data = self.dm.get_stock_data(stock_code, period="daily", prefer_real_data=True)

            if stock_data is None or len(stock_data) == 0:
                print(f"   ❌ 无法获取数据")
                continue

            # 计算信号
            fusion_result = self.fusion_engine.fuse_signals(stock_data, market_data)

            if fusion_result is None:
                print(f"   ❌ 无法计算信号")
                continue

            # 获取最新数据
            latest = stock_data.iloc[-1]
            price_change = (latest['close'] - latest['open']) / latest['open'] * 100

            # 检查价格变动
            if abs(price_change) >= self.price_change_threshold:
                signal_type = "价格异常"
                signal_level = "重要" if abs(price_change) >= 5.0 else "一般"
                signals.append({
                    'stock_code': stock_code,
                    'stock_name': self._get_stock_name(stock_code),
                    'signal_type': signal_type,
                    'signal_level': signal_level,
                    'price': latest['close'],
                    'price_change': price_change,
                    'volume': latest['volume'],
                    'fusion_score': fusion_result.get('fusion_score', 0),
                    'recommendation': fusion_result.get('recommendation', {}).get('action', 'N/A'),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                print(f"   ⚠️ {signal_type}: {price_change:+.2f}%")

            # 检查融合信号
            fusion_score = fusion_result.get('fusion_score', 0)
            recommendation = fusion_result.get('recommendation', {})
            action = recommendation.get('action', 'N/A')

            if fusion_score >= self.signal_thresholds['strong_buy']:
                signal_type = "强烈买入信号"
                signal_level = "重要"
                signals.append({
                    'stock_code': stock_code,
                    'stock_name': self._get_stock_name(stock_code),
                    'signal_type': signal_type,
                    'signal_level': signal_level,
                    'price': latest['close'],
                    'price_change': price_change,
                    'volume': latest['volume'],
                    'fusion_score': fusion_score,
                    'recommendation': action,
                    'reason': recommendation.get('reason', ''),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                print(f"   ✅ {signal_type}: {fusion_score:.2f}")

            elif fusion_score >= self.signal_thresholds['buy']:
                signal_type = "买入信号"
                signal_level = "一般"
                signals.append({
                    'stock_code': stock_code,
                    'stock_name': self._get_stock_name(stock_code),
                    'signal_type': signal_type,
                    'signal_level': signal_level,
                    'price': latest['close'],
                    'price_change': price_change,
                    'volume': latest['volume'],
                    'fusion_score': fusion_score,
                    'recommendation': action,
                    'reason': recommendation.get('reason', ''),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                print(f"   ✅ {signal_type}: {fusion_score:.2f}")

            elif fusion_score <= self.signal_thresholds['strong_sell']:
                signal_type = "强烈卖出信号"
                signal_level = "重要"
                signals.append({
                    'stock_code': stock_code,
                    'stock_name': self._get_stock_name(stock_code),
                    'signal_type': signal_type,
                    'signal_level': signal_level,
                    'price': latest['close'],
                    'price_change': price_change,
                    'volume': latest['volume'],
                    'fusion_score': fusion_score,
                    'recommendation': action,
                    'reason': recommendation.get('reason', ''),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                print(f"   ⚠️ {signal_type}: {fusion_score:.2f}")

            # 检查成交量异常
            ntdf_signal = fusion_result.get('ntdf_signal')
            if ntdf_signal:
                volume_anomaly = ntdf_signal.get('volume_anomaly')
                if volume_anomaly:
                    ratio_5 = volume_anomaly.get('ratio_5', 0)
                    if ratio_5 >= self.volume_anomaly_threshold:
                        signal_type = "成交量异常"
                        signal_level = "重要" if ratio_5 >= 3.0 else "一般"
                        signals.append({
                            'stock_code': stock_code,
                            'stock_name': self._get_stock_name(stock_code),
                            'signal_type': signal_type,
                            'signal_level': signal_level,
                            'price': latest['close'],
                            'price_change': price_change,
                            'volume': latest['volume'],
                            'volume_ratio': ratio_5,
                            'fusion_score': fusion_score,
                            'recommendation': action,
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                        print(f"   ⚠️ {signal_type}: {ratio_5:.2f}倍")

        # 汇总
        print(f"\n{'='*70}")
        print(f"✅ 扫描完成，发现 {len(signals)} 个信号")

        # 按重要性排序
        important_signals = [s for s in signals if s['signal_level'] == '重要']
        normal_signals = [s for s in signals if s['signal_level'] == '一般']

        if important_signals:
            print(f"\n🔴 重要信号 ({len(important_signals)}):")
            for i, signal in enumerate(important_signals, 1):
                print(f"   [{i}] {signal['stock_name']} ({signal['stock_code']})")
                print(f"       类型: {signal['signal_type']}")
                if 'fusion_score' in signal:
                    print(f"       评分: {signal['fusion_score']:.2f}")
                if 'price_change' in signal:
                    print(f"       涨跌: {signal['price_change']:+.2f}%")

        if normal_signals:
            print(f"\n🟡 一般信号 ({len(normal_signals)}):")
            for i, signal in enumerate(normal_signals, 1):
                print(f"   [{i}] {signal['stock_name']} ({signal['stock_code']})")
                print(f"       类型: {signal['signal_type']}")

        return signals

    def start_monitoring(self, interval_minutes=5, max_scans=None):
        """
        开始持续监控

        Args:
            interval_minutes: 扫描间隔（分钟）
            max_scans: 最大扫描次数（None 表示无限）
        """
        print(f"\n{'='*70}")
        print(f"🔄 开始持续监控")
        print(f"{'='*70}")
        print(f"   监控股票: {len(self.watchlist)} 只")
        print(f"   扫描间隔: {interval_minutes} 分钟")
        if max_scans:
            print(f"   最大扫描: {max_scans} 次")
        else:
            print(f"   最大扫描: 无限")

        scan_count = 0
        try:
            while True:
                scan_count += 1

                # 执行扫描
                signals = self.scan_once()

                # 检查是否达到最大扫描次数
                if max_scans and scan_count >= max_scans:
                    print(f"\n✅ 已完成 {max_scans} 次扫描，停止监控")
                    break

                # 等待下一次扫描
                print(f"\n⏰ 等待 {interval_minutes} 分钟后进行下一次扫描...")
                time.sleep(interval_minutes * 60)

        except KeyboardInterrupt:
            print(f"\n\n⚠️ 监控已手动停止")
            print(f"   共完成 {scan_count} 次扫描")

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


if __name__ == "__main__":
    # 测试代码
    print("实时监控系统 v1.0 测试")

    # 创建监控系统
    monitor = RealTimeMonitor()

    # 添加监控股票
    monitor.add_to_watchlist(["600519", "000858", "002475"])

    # 执行一次扫描
    signals = monitor.scan_once()

    print("\n所有测试完成")
