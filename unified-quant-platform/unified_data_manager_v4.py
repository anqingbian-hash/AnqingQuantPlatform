#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一数据管理器 v3
支持 AKShare + Efinance + Tushare + Baostock
"""

import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# 导入各数据源
from modules.akshare_source import AkShareDataSource
from modules.efinance_source import EfinanceDataSource
from modules.tushare_source import TushareDataSource
from modules.baostock_source import BaostockDataSource

class UnifiedDataManagerV4:
    """统一数据管理器 v4"""

    def __init__(self, primary="akshare", fallback="tushare", tertiary="baostock"):
        """
        初始化数据管理器 v4

        Args:
            primary: 主数据源
            fallback: 备用数据源
            tertiary: 第三数据源
        """
        self.primary = primary
        self.fallback = fallback
        self.tertiary = tertiary
        self.failure_count = 0
        self.last_failure_time = None
        self.cooldown_minutes = 5
        self.current_source = primary

        print(f"初始化统一数据管理器 v4")
        print(f"  主数据源: {self.primary}")
        print(f"  备用数据源: {self.fallback}")
        print(f"  第三数据源: {self.tertiary}")
        print(f"  冷却时间: {self.cooldown_minutes} 分钟")

    def get_stock_data(self, stock_code, period="daily", start_date=None, end_date=None, prefer_real_data=True):
        """
        获取股票数据（4 个数据源容错）

        Args:
            stock_code: 股票代码
            period: 周期
            prefer_real_data: 是否优先使用真实数据
        """
        # 如果优先使用真实数据且当前不在冷却状态
        if prefer_real_data and not self._is_cooldown():
            return self._get_from_current(stock_code, period, start_date, end_date)

        # 否则使用本地数据源
        print("使用本地模拟数据")
        return self._get_local_data(stock_code, period, start_date, end_date)

    def get_market_data(self, market="A股大盘"):
        """
        获取大盘数据
        """
        print(f"获取大盘数据: {market}")

        # 优先使用真实数据源
        if not self._is_cooldown():
            return self._get_market_from_current(market)
        else:
            return self._get_local_market_data(market)

    def _is_cooldown(self):
        """检查冷却状态"""
        if self.last_failure_time is None:
            return False

        cooldown_end = self.last_failure_time + timedelta(minutes=self.cooldown_minutes)
        return datetime.now() < cooldown_end

    def _get_from_current(self, stock_code, period, start_date, end_date):
        """从当前数据源获取"""
        try:
            if self.current_source == "akshare":
                return self._get_from_akshare(stock_code, period, start_date, end_date)
            elif self.current_source == "tushare":
                return self._get_from_tushare(stock_code, period, start_date, end_date)
            elif self.current_source == "efinance":
                return self._get_from_efinance(stock_code, period, start_date, end_date)
            elif self.current_source == "baostock":
                return self._get_from_baostock(stock_code, period, start_date, end_date)
            else:
                raise ValueError(f"不支持的数据源: {self.current_source}")

        except Exception as e:
            self._on_failure(self.current_source, str(e))

    def _get_from_fallback(self, stock_code, period, start_date, end_date):
        """从备用数据源获取"""
        try:
            if self.fallback == "tushare":
                return self._get_from_tushare(stock_code, period, start_date, end_date)
            elif self.fallback == "efinance":
                return self._get_from_efinance(stock_code, period, start_date, end_date)
            elif self.fallback == "baostock":
                return self._get_from_baostock(stock_code, period, start_date, end_date)
            else:
                raise ValueError(f"不支持的备用数据源: {self.fallback}")

        except Exception as e:
            self._on_failure(self.fallback, str(e))

    def _get_from_akshare(self, stock_code, period, start_date, end_date):
        """从 AKShare 获取"""
        try:
            import akshare as ak
            df = ak.stock_zh_a_hist(symbol=stock_code, period=period,
                                          adjust="qfq",
                                          start_date=start_date or "20200101",
                                          end_date=end_date)
            return {
                "source": "akshare",
                "data": df,
                "quality": "high"
            }
        except Exception as e:
            raise Exception(f"AKShare 失败: {e}")

    def _get_from_efinance(self, stock_code, period, start_date, end_date):
        """从 Efinance 获取"""
        try:
            import efinance as ef
            if period == "daily":
                df = ef.stock.get_quote_history(stock_code, beg="20200101", end_date=end_date, k="d")
            return {
                "source": "efinance",
                "data": df,
                "quality": "high"
            }
        except Exception as e:
            raise Exception(f"Efinance 失败: {e}")

    def _get_from_tushare(self, stock_code, period, start_date, end_date):
        """从 Tushare 获取"""
        try:
            import tushare as ts
            df = ts.pro_bar(
                ts_code=stock_code,
                adj='qfq',
                start_date=start_date or "20200101",
                end_date=end_date,
                freq='D'
            )
            return {
                "source": "tushare",
                "data": df,
                "quality": "high"
            }
        except Exception as e:
            raise Exception(f"Tushare 失败: {e}")

    def _get_from_baostock(self, stock_code, period, start_date, end_date):
        """从 Baostock 获取"""
        try:
            import baostock as bs
            bs.query_history_k_data_plus(
                stock_code,
                klt=101,
                start_date=start_date or "20200101",
                end_date=end_date,
                adjustflag="2"
            )
            return {
                "source": "baostock",
                "data": df,
                "quality": "very_high"
            }
        except Exception as e:
            raise Exception(f"Baostock 失败: {e}")

    def _on_failure(self, failed_source, error_msg):
        """处理失败"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        print(f"❌ 数据源 失败: {failed_source}")
        print(f"   错误: {error_msg}")
        print(f"   失败次数: {self.failure_count}/3")

        # 失败3次后切换
        if self.failure_count >= 3:
            self._switch_source()

    def _switch_source(self):
        """切换数据源"""
        sources_order = [self.primary, self.fallback, self. self.tertiary]

        for i, source in enumerate(sources_order):
            if source != self.current_source:
                self.current_source = source
                self.failure_count = 0
                print(f"✅ 切换到数据源: {source}")
                return

        print("没有可用的数据源了")
        raise Exception("所有数据源都失败了")

    def get_status(self):
        """获取状态"""
        return {
            "primary": self.primary,
            "fallback": self.fallback,
            "tertiary": self.tertiary,
            "current_source": self.current_source,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time,
            "is_cooldown": self._is_cooldown(),
            "cooldown_end": (self.last_failure_time + timedelta(minutes=self.cooldown_minutes)) if self.last_failure_time else None,
            "sources_available": ["akshare", "efinance", "tushare", "baostock"]
        }


if __name__ == "__main__":
    print("测试统一数据管理器 v4")

    dm = UnifiedDataManagerV4(
        primary="akshare",
        fallback="tushare",
        tertiary="baostock"
    )

    # 测试本地数据源
    print("\n测试本地数据源\n")
    local_data = dm.get_stock_data("600519", period="daily", prefer_real_data=False)
    if local_data:
        print("本地数据源测试通过")
        print(f"数据形状: {local_data.shape}")
        print(f"最近5条:\n{local_data.tail()}")
    else:
        print("本地数据源测试失败")
