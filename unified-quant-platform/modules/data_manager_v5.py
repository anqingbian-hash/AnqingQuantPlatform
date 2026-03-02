#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一数据管理器 v5.0
整合所有数据源：Local + AKShare + Efinance + Tushare + Baostock
自动容错，自动切换
"""

import sys
import os
import warnings
warnings.filterwarnings('ignore')

from datetime import datetime, timedelta

from modules.local_data_source_v2 import LocalDataSource
from modules.akshare_source import AkShareDataSource
from modules.efinance_source import EfinanceDataSource
from modules.tushare_source import TushareDataSource
from modules.baostock_source import BaostockDataSource

class UnifiedDataManagerV5:
    """统一数据管理器 v5.0 - 整合所有数据源"""

    def __init__(self, primary="akshare", fallback="efinance", tertiary="tushare"):
        """
        初始化统一数据管理器

        Args:
            primary: 主数据源（akshare/efinance/tushare/baostock/local）
            fallback: 备用数据源
            tertiary: 第三数据源
        """
        print("="*70)
        print("统一数据管理器 v5.0 - 初始化")
        print("="*70)

        # 数据源优先级
        self.primary = primary
        self.fallback = fallback
        self.tertiary = tertiary

        # 失败计数和冷却时间
        self.failure_count = {}
        self.last_failure_time = {}
        self.cooldown_period = timedelta(minutes=5)

        # 当前数据源
        self.current_source = primary

        # 初始化所有数据源
        self.sources = {
            "local": LocalDataSource(),
            "akshare": AkShareDataSource(),
            "efinance": EfinanceDataSource(),
            "tushare": TushareDataSource(),
            "baostock": BaostockDataSource()
        }

        print(f"✅ 数据源优先级:")
        print(f"   主数据源: {primary}")
        print(f"   备用数据源: {fallback}")
        print(f"   第三数据源: {tertiary}")

    def get_stock_data(self, stock_code: str, period: str = "daily", prefer_real_data=True):
        """
        获取股票数据（自动切换数据源）

        Args:
            stock_code: 股票代码
            period: 数据周期
            prefer_real_data: 是否优先使用真实数据

        Returns:
            pd.DataFrame: K线数据
        """
        print(f"\n{'='*70}")
        print(f"📊 获取股票数据: {stock_code} ({period})")
        print(f"{'='*70}")

        # 数据源优先级
        if prefer_real_data:
            sources = [self.primary, self.fallback, self.tertiary, "local"]
        else:
            sources = ["local"]

        for source in sources:
            print(f"\n尝试数据源: {source}")

            try:
                # 检查冷却时间
                if self._is_in_cooldown(source):
                    print(f"⚠️ {source} 在冷却期，跳过")
                    continue

                # 获取数据
                data_source = self.sources[source]
                data = data_source.get_stock_data(stock_code, period)

                if data is not None and len(data) > 0:
                    self.current_source = source
                    self._reset_failure(source)
                    print(f"✅ 数据源 ({source}) 获取成功，共 {len(data)} 条记录")
                    return data
                else:
                    self._on_failure(source, "数据为空")

            except Exception as e:
                self._on_failure(source, str(e))

        # 所有数据源都失败
        print("❌ 所有数据源均失败")
        return None

    def get_market_data(self, market: str = "A股大盘"):
        """
        获取大盘数据

        Args:
            market: 市场名称

        Returns:
            dict: 大盘数据
        """
        print(f"\n{'='*70}")
        print(f"📊 获取大盘数据: {market}")
        print(f"{'='*70}")

        # 数据源优先级
        sources = [self.primary, self.fallback, self.tertiary, "local"]

        for source in sources:
            print(f"\n尝试数据源: {source}")

            try:
                # 检查冷却时间
                if self._is_in_cooldown(source):
                    print(f"⚠️ {source} 在冷却期，跳过")
                    continue

                # 获取数据
                data_source = self.sources[source]

                # 尝试获取大盘数据
                if hasattr(data_source, 'get_market_data'):
                    market_data = data_source.get_market_data(market)
                elif hasattr(data_source, 'get_index_data'):
                    df = data_source.get_index_data("sh000001")
                    if df is not None and len(df) > 0:
                        recent = df.tail(30)
                        up_count = len(recent[recent['close'] > recent['open']])
                        down_count = len(recent[recent['close'] < recent['open']])
                        up_ratio = up_count / (up_count + down_count)

                        if up_ratio > 0.6:
                            market_env = "强势"
                            threshold = 8.5
                        elif up_ratio > 0.4:
                            market_env = "震荡"
                            threshold = 9.0
                        else:
                            market_env = "弱势"
                            threshold = 9.5

                        market_data = {
                            "data": df,
                            "environment": market_env,
                            "threshold": threshold,
                            "up_count": up_count,
                            "down_count": down_count,
                            "up_ratio": up_ratio
                        }
                    else:
                        market_data = None
                else:
                    print(f"⚠️ {source} 不支持大盘数据")
                    continue

                if market_data is not None and market_data.get('data') is not None:
                    self.current_source = source
                    self._reset_failure(source)
                    print(f"✅ 数据源 ({source}) 获取成功，市场环境: {market_data.get('environment', 'N/A')}")
                    return market_data
                else:
                    self._on_failure(source, "数据为空")

            except Exception as e:
                self._on_failure(source, str(e))

        # 所有数据源都失败
        print("❌ 所有数据源均失败")
        return None

    def _is_in_cooldown(self, source: str) -> bool:
        """检查数据源是否在冷却期"""
        if source not in self.last_failure_time:
            return False

        time_since_failure = datetime.now() - self.last_failure_time[source]
        return time_since_failure < self.cooldown_period

    def _on_failure(self, source: str, error_msg: str):
        """处理失败"""
        self.failure_count[source] = self.failure_count.get(source, 0) + 1
        self.last_failure_time[source] = datetime.now()
        print(f"❌ 数据源 ({source}) 获取失败: {error_msg}")
        print(f"   失败次数: {self.failure_count[source]}")

    def _reset_failure(self, source: str):
        """重置失败计数"""
        self.failure_count[source] = 0
        if source in self.last_failure_time:
            del self.last_failure_time[source]

    def get_status(self):
        """获取数据管理器状态"""
        return {
            "current_source": self.current_source,
            "primary": self.primary,
            "fallback": self.fallback,
            "tertiary": self.tertiary,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time,
            "cooldown_period": str(self.cooldown_period)
        }


if __name__ == "__main__":
    # 测试代码
    print("\n测试统一数据管理器 v5.0\n")

    dm = UnifiedDataManagerV5(
        primary="akshare",
        fallback="efinance",
        tertiary="tushare"
    )

    # 测试1: 获取股票数据
    print("\n测试1: 获取贵州茅台数据\n")
    stock_data = dm.get_stock_data("600519", period="daily")
    if stock_data is not None:
        print(f"数据形状: {stock_data.shape}")
        print(f"当前数据源: {dm.current_source}")
        print(f"最近5条:\n{stock_data.tail(5)}")

    # 测试2: 获取大盘数据
    print("\n\n测试2: 获取大盘数据\n")
    market_data = dm.get_market_data("A股大盘")
    if market_data:
        print(f"当前数据源: {dm.current_source}")
        print(f"市场环境: {market_data.get('environment', 'N/A')}")
        print(f"上涨占比: {market_data.get('up_ratio', 0)*100:.1f}%")

    # 测试3: 数据管理器状态
    print("\n\n测试3: 数据管理器状态\n")
    status = dm.get_status()
    print(f"当前数据源: {status['current_source']}")
    print(f"主数据源: {status['primary']}")
    print(f"备用数据源: {status['fallback']}")
    print(f"第三数据源: {status['tertiary']}")
    print(f"失败次数: {status['failure_count']}")

    print("\n✅ 所有测试完成！\n")
