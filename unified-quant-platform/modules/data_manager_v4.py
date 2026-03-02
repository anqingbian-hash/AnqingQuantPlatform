#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据源管理器 v4
最终版本：AKShare + Efinance + Tushare + Baostock 四数据源
"""

import pandas as pd
import warnings
warnings.filterwarnings('ignore')

class UnifiedDataManagerV4:
    """统一数据管理器 v4"""

    def __init__(self, primary="akshare", fallback="tushare"):
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

        print(f"初始化数据管理器 v4")
        print(f"主数据源: {self.primary}")
        print(f"备用数据源: {self.fallback}")
        print(f"第三数据源: {self.tertiary}")
        print(f"冷却时间: {self.cooldown_minutes} 分钟")

    def get_stock_data(self, stock_code, period="daily", start_date=None, end_date=None, prefer_real_data=True):
        """
        获取股票数据（4个数据源容错）
        """
        print(f"获取股票数据: {stock_code}")

        # 检查冷却
        if self._is_cooldown():
            print(f"数据源冷却中，使用备用源")
            return self._get_from_current()

        # 尝试主数据源
        try:
            data = self._get_from_primary(stock_code, period, start_date, end_date)
            self.failure_count = 0
            print(f"主数据源 ({self.primary}) 获取成功，{len(data)}条记录")
            return data

        except Exception as e:
            self._on_failure(self.primary, str(e))
            return self._get_from_current()

    def get_market_data(self, market="A股大盘"):
        """获取大盘数据"""
        print(f"获取大盘数据: {market}")

        try:
            if market == "A股大盘":
                return self._get_from_akshare_index(market)
            else:
                return {"data": None, "status": "not_supported", "error": "not_supported"}

        except Exception as e:
            print(f"大盘数据获取失败: {e}")
            return {"data": None, "status": "failed", "error": str(e)}

    def get_status(self):
        """获取状态"""
        return {
            "primary": self.primary,
            "fallback": self.fallback,
            "tertiary": self.tertiary,
            "current_source": self._get_current_name(),
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time,
            "is_cooldown": self._is_cooldown()
        }

    def _is_cooldown(self):
        """检查冷却状态"""
        if self.last_failure_time is None:
            return False

        cooldown_end = self.last_failure_time + timedelta(minutes=self.cooldown_minutes)
        return datetime.now() < cooldown_end

    def _on_failure(self, failed_source, error_msg):
        """处理失败"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        print(f"数据源 {failed_source} 失败: {error_msg}")
        print(f"失败次数: {self.failure_count}/3")

        # 失败3次后切换
        if self.failure_count >= 3:
            print(f"连续失败，切换到下一个数据源")
            self._switch_source()

    def _switch_source(self):
        """切换数据源"""
        sources = [self.primary, self.fallback, self.tertiary]

        current_idx = sources.index(self.current_source)
        next_sources = sources[current_idx+1:] if current_idx < len(sources)-1 else []

        if next_sources:
            self.current_source = next_sources[0]
            self.failure_count = 0
            print(f"切换到: {self.current_source}")
            return True
        else:
            print("没有可用的数据源")
            return False

    def _get_current_name(self):
        """获取当前数据源名称"""
        source_map = {
            "akshare": "AKShare",
            "tushare": "TuShare",
            "baostock": "Baostock"
            "efinance": "Efinance"
        }
        return source_map.get(self.current_source, "unknown")

    def _get_from_primary(self, stock_code, period, start_date, end_date):
        """从主数据源获取"""
        try:
            if self.primary == "akshare":
                return self._get_from_akshare(stock_code, period, start_date, end_date)
            elif self.primary == "tushare":
                return self._get_from_tushare(stock_code, period, start_date, end_date)
            elif self.primary == "baostock":
                return self._get_from_baostock(stock_code, period, start_date, end_date)
            elif self.primary == "efinance":
                return self._get_from_efinance(stock_code, period, start_date, end_date)
            else:
                raise ValueError(f"不支持的主数据源: {self.primary}")

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

    def _get_from_tertiary(self, stock_code, period, start_date, end_date):
        """从第三数据源获取"""
        return self._get_from_baostock(stock_code, period, start_date, end_date)

    def _get_from_akshare(self, stock_code, period, start_date, end_date):
        """从 AKShare 获取"""
        import akshare as ak

        try:
            if period == "daily":
                df = ak.stock_zh_a_hist(
                    symbol=stock_code,
                    start_date=start_date or "20200101",
                    end_date=end_date,
                    adjust="qfq"
                )
            else:
                print("AKShare 仅支持日线数据")
                return None

            if df is not None and len(df) > 0:
                return {
                    "source": "akshare",
                    "data": df,
                    "quality": "high",
                    "status": "success"
                }
            else:
                raise Exception("AKShare 获取失败")

    def _get_from_tushare(self, stock_code, period, start_date, end_date):
        """从 TuShare 获取"""
        import tushare as ts

        try:
            if period == "daily":
                df = ts.pro_bar(
                    ts_code=stock_code,
                    adj='qfq',
                    start_date=start_date or "20200101",
                    end_date=end_date,
                    freq='D'
                )

            if df is not None and len(df) > 0:
                return {
                    "source": "tushare",
                    "data": df,
                    "quality": "high",
                    "status": "success"
                }
            else:
                raise Exception("TuShare 获取失败")

    def _get_from_baostock(self, stock_code, period, start_date, end_date):
        """从 Baostock 获取"""
        import baostock as bs

        try:
            if period == "daily":
                df = bs.query_history_k_data_plus(
                    stock_code,
                    klt=101,
                    start_date=start_date or "20200101",
                    end_date=end_date,
                    adjustflag="2"
                )

            if df is not None and len(df) > 0:
                return {
                    "source": "baostock",
                    "data": df,
                    "quality": "very_high",
                    "status": "success"
                }
            else:
                raise Exception("Baostock 获取失败")

    def _get_from_efinance(self, stock_code, period, start_date, end_date):
        """从 Efinance 获取"""
        import efinance as ef

        try:
            df = ef.stock.get_quote_history(
                stock_code,
                beg="20200101",
                k="d" if period=="daily" else "w" if period=="weekly" else "m",
                end_date=end_date
            )

            if df is not None and len(df) > 0:
                return {
                    "source": "efinance",
                    "data": df,
                    "quality": "high",
                    "status": "success"
                }
            else:
                raise Exception("Efinance 获取失败")
