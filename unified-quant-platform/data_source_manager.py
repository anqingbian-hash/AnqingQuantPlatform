#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一量化平台 - 数据源管理器
支持 AKShare + Efinance + Tushare 多数据源容错
"""

import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import akshare as ak
import efinance as ef
from modules.tushare_source import TushareDataSource

class UnifiedDataManager:
    """统一数据管理器"""

    def __init__(self, primary="akshare", fallback="tushare"):
        """
        初始化数据管理器

        Args:
            primary: 主数据源（akshare/efinance/tushare）
            fallback: 备用数据源
        """
        self.primary = primary
        self.fallback = fallback
        self.failure_count = 0
        self.last_failure_time = None
        self.cooldown_minutes = 5

        print(f"✅ 数据管理器初始化完成")
        print(f"   主数据源: {self.primary}")
        print(f"   备用数据源: {self.fallback}")
        print(f"   冷却时间: {self.cooldown_minutes} 分钟\n")

    def get_stock_data(self, stock_code: str, period: str = "daily", start_date=None, end_date=None):
        """
        获取股票数据（支持多数据源容错）

        Args:
            stock_code: 股票代码（如 600519）
            period: 数据周期（daily/weekly/monthly）
            start_date: 开始日期（YYYY-MM-DD）
            end_date: 结束日期（YYYY-MM-DD）

        Returns:
            pd.DataFrame: K线数据
        """
        print(f"📊 获取股票数据: {stock_code} ({period})")

        # 检查冷却状态
        if self._is_cooldown():
            print(f"⚠️ 数据源冷却中，使用备用源: {self.fallback}")
            return self._get_from_fallback(stock_code, period, start_date, end_date)

        # 尝试主数据源
        try:
            data = self._get_from_primary(stock_code, period, start_date, end_date)
            self.failure_count = 0  # 成功后重置
            print(f"✅ 主数据源 ({self.primary}) 获取成功，共 {len(data)} 条记录")
            return data

        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            print(f"❌ 主数据源 ({self.primary}) 失败: {e}")
            print(f"   失败次数: {self.failure_count}/3")

            # 检查是否需要切换到备用源
            if self.failure_count >= 3:
                print(f"⚠️ 连续失败 {self.failure_count} 次，切换到备用源")
                self.failure_count = 0
                return self._get_from_fallback(stock_code, period, start_date, end_date)

            return self._get_from_fallback(stock_code, period, start_date, end_date)

    def _get_from_primary(self, stock_code: str, period: str, start_date, end_date):
        """从主数据源获取数据"""
        if self.primary == "akshare":
            return self._get_from_akshare(stock_code, period, start_date, end_date)
        elif self.primary == "efinance":
            return self._get_from_efinance(stock_code, period, start_date, end_date)
        elif self.primary == "tushare":
            return self._get_from_tushare(stock_code, period, start_date, end_date)
        else:
            raise ValueError(f"不支持的 primary 数据源: {self.primary}")

    def _get_from_tushare(self, stock_code: str, period: str, start_date, end_date):
        """从 Tushare 获取数据"""
        try:
            tushare_source = TushareDataSource(token=None)
            df = tushare_source.get_stock_data(stock_code, period=period, start_date=start_date, end_date=end_date)
            self.failure_count = 0
            print(f"✅ Tushare 获取成功，共 {len(df)} 条记录")
            return df
        except Exception as e:
            raise Exception(f"Tushare 获取失败: {e}")

    def _get_from_fallback(self, stock_code: str, period: str, start_date, end_date):
        """从备用数据源获取数据"""
        if self.fallback == "akshare":
            return self._get_from_akshare(stock_code, period, start_date, end_date)
        elif self.fallback == "efinance":
            return self._get_from_efinance(stock_code, period, start_date, end_date)
        elif self.fallback == "tushare":
            return self._get_from_tushare(stock_code, period, start_date, end_date)
        else:
            raise ValueError(f"不支持的 fallback 数据源: {self.fallback}")

    def _get_from_akshare(self, stock_code: str, period: str, start_date, end_date):
        """从 AKShare 获取数据"""
        try:
            # AKShare 股票历史数据
            if period == "daily":
                df = ak.stock_zh_a_hist(symbol=stock_code, period="daily",
                                          start_date="20200101", end_date=end_date,
                                          adjust="qfq")
            elif period == "weekly":
                df = ak.stock_zh_a_hist(symbol=stock_code, period="weekly",
                                          start_date="20200101", end_date=end_date,
                                          adjust="qfq")
            else:  # monthly
                df = ak.stock_zh_a_hist(symbol=stock_code, period="monthly",
                                          start_date="20200101", end_date=end_date,
                                          adjust="qfq")

            # 标准化列名
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '最高': 'high',
                '最低': 'low',
                '收盘': 'close',
                '成交量': 'volume'
            })

            # 确保日期列是 datetime 格式
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])

            return df

        except Exception as e:
            raise Exception(f"AKShare 获取失败: {e}")

    def _get_from_efinance(self, stock_code: str, period: str, start_date, end_date):
        """从 Efinance 获取数据"""
        try:
            # Efinance 股票历史数据
            if period == "daily":
                df = ef.stock.get_quote_history(stock_code, beg="20200101", end=end_date, k="d")
            elif period == "weekly":
                df = ef.stock.get_quote_history(stock_code, beg="20200101", end=end_date, k="w")
            else:  # monthly
                df = ef.stock.get_quote_history(stock_code, beg="20200101", end=end_date, k="m")

            # 标准化列名
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '最高': 'high',
                '最低': 'low',
                '收盘': 'close',
                '成交量': 'volume'
            })

            # 确保日期列是 datetime 格式
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])

            return df

        except Exception as e:
            raise Exception(f"Efinance 获取失败: {e}")

    def _is_cooldown(self):
        """检查是否在冷却状态"""
        if self.last_failure_time is None:
            return False

        cooldown_end = self.last_failure_time + timedelta(minutes=self.cooldown_minutes)
        return datetime.now() < cooldown_end

    def get_market_data(self, market: str = "A股大盘"):
        """
        获取大盘数据

        Args:
            market: 市场名称（A股大盘、上证50、沪深300）

        Returns:
            dict: 大盘数据
        """
        print(f"📊 获取大盘数据: {market}")

        try:
            # 尝试主数据源
            if market == "A股大盘":
                data = ak.stock_zh_index_daily(symbol="sh000001", start_date="20200101")
            elif market == "上证50":
                data = ak.stock_zh_index_daily(symbol="sh000016", start_date="20200101")
            elif market == "沪深300":
                data = ak.stock_zh_index_daily(symbol="sh000300", start_date="20200101")
            else:
                data = None

            self.failure_count = 0

            if data is not None:
                print(f"✅ 主数据源获取成功，共 {len(data)} 条记录")
                return {
                    "data": data,
                    "source": self.primary,
                    "status": "success"
                }

        except Exception as e:
            print(f"❌ 主数据源失败: {e}")
            # 这里简化处理，备用源逻辑类似
            return {
                "data": None,
                "source": "failed",
                "status": "error",
                "error": str(e)
            }

    def get_futures_data(self, futures_code: str, period: str = "daily"):
        """
        获取期货数据

        Args:
            futures_code: 期货代码
            period: 数据周期

        Returns:
            pd.DataFrame: 期货数据
        """
        print(f"📊 获取期货数据: {futures_code} ({period})")

        try:
            # AKShare 期货数据
            df = ak.futures_zh_hist_sina(symbol=futures_code, period=period,
                                          start_date="20200101", adjust="qfq")

            # 标准化列名
            df = df.rename(columns={
                'datetime': 'date',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'volume': 'volume'
            })

            self.failure_count = 0
            print(f"✅ 期货数据获取成功，共 {len(df)} 条记录")
            return df

        except Exception as e:
            print(f"❌ 期货数据获取失败: {e}")
            raise e

    def get_status(self):
        """获取数据源状态"""
        return {
            "primary": self.primary,
            "fallback": self.fallback,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time,
            "is_cooldown": self._is_cooldown(),
            "cooldown_end": (self.last_failure_time + timedelta(minutes=self.cooldown_minutes)) if self.last_failure_time else None
        }


if __name__ == "__main__":
    # 测试代码
    print("="*50)
    print("统一量化平台 - 数据源管理器测试")
    print("="*50)

    # 创建数据管理器
    dm = UnifiedDataManager(primary="akshare", fallback="efinance")

    # 测试1: 获取股票数据
    print("\n测试1: 获取贵州茅台 (600519) 数据\n")
    stock_data = dm.get_stock_data("600519", period="daily")
    print(f"数据列: {stock_data.columns.tolist()}")
    print(f"数据形状: {stock_data.shape}")
    print(f"最近5条:\n{stock_data.tail(5)}")

    # 测试2: 获取大盘数据
    print("\n测试2: 获取A股大盘数据\n")
    market_data = dm.get_market_data("A股大盘")
    print(f"数据状态: {market_data['status']}")

    # 测试3: 获取数据源状态
    print("\n测试3: 数据源状态\n")
    status = dm.get_status()
    print(f"主数据源: {status['primary']}")
    print(f"备用数据源: {status['fallback']}")
    print(f"失败次数: {status['failure_count']}")
    print(f"是否冷却: {status['is_cooldown']}")

    print("\n" + "="*50)
    print("✅ 所有测试完成！")
    print("="*50)
