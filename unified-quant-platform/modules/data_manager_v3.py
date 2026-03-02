#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据源管理器 v3
支持 AKShare + Efinance + Tushare + Baostock 多数据源容错
"""

import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# 导入各数据源模块
from modules.akshare_source import AkShareDataSource
from modules.efinance_source import EfinanceDataSource
from modules.tushare_source import TushareDataSource
from modules.baostock_source import BaostockDataSource

class UnifiedDataManagerV3:
    """统一数据管理器 v3
    支持4 个数据源：AKShare / Efinance / Tushare / Baostock
    """

    def __init__(self, primary="akshare", fallback="tushare", tertiary="efinance"):
        """
        初始化数据管理器 v3

        Args:
            primary: 主数据源（akshare/efinance/tushare/baostock）
            fallback: 备用数据源
            tertiary: 第三数据源
        """
        self.primary = primary
        self.fallback = fallback
        self.tertiary = tertiary
        self.current_source = primary
        self.failure_count = 0
        self.last_failure_time = None
        self.cooldown_minutes = 5

        # 初始化数据源
        print(f"初始化统一数据管理器 v3")
        print(f"主数据源: {self.primary}")
        print(f"备用数据源: {self.fallback}")
        print(f"第三数据源: {self.tertiary}")
        print(f"冷却时间: {self.cooldown_minutes} 分钟")

    def get_stock_data(self, stock_code, period="daily", start_date=None, end_date=None, prefer_real_data=False):
        """
        获取股票数据（多数据源容错）

        Args:
            stock_code: 股票代码
            period: 数据周期
            start_date: 开始日期
            end_date: 结束日期
            prefer_real_data: 优先使用真实数据

        Returns:
            dict: {source, data, quality}
        """
        # 如果优先使用真实数据且当前不在冷却状态
        if prefer_real_data and not self._is_cooldown():
            return self._try_all_sources(stock_code, period, start_date, end_date)

        # 否则使用当前数据源
        return self._get_from_current_source(stock_code, period, start_date, end_date)

    def _try_all_sources(self, stock_code, period, start_date, end_date):
        """尝试所有数据源"""
        sources = [self.primary, self.fallback, self.tertiary]

        for source in sources:
            print(f"\n尝试数据源: {source}")

            try:
                if source == "akshare":
                    data = self._get_from_akshare(stock_code, period, start_date, end_date)
                    return {"source": "akshare", "data": data, "quality": "high", "status": "success"}

                elif source == "efinance":
                    data = self._get_from_efinance(stock_code, period, start_date, end_date)
                    return {"source": "efinance", "data": data, "quality": "high", "status": "success"}

                elif source == "tushare":
                    data = self._get_from_tushare(stock_code, period, start_date, end_date)
                    return {"source": "tushare", "data": data, "quality": "high", "status": "success"}

                elif source == "baostock":
                    data = self._get_from_baostock(stock_code, period, start_date, end_date)
                    return {"source": "baostock", "data": data, "quality": "very_high", "status": "success"}

            except Exception as e:
                print(f"   失败: {e}")
                self._on_failure(source, str(e))

        # 所有数据源都失败
        print("所有数据源均失败，返回 None")
        return None

    def _get_from_current_source(self, stock_code, period, start_date, end_date):
        """从当前数据源获取"""
        try:
            data = self._get_from_primary(stock_code, period, start_date, end_date)
            self.failure_count = 0
            print(f"数据源 ({self.current_source}) 获取成功，共 {len(data)} 条记录")
            return {"source": self.current_source, "data": data, "quality": "high", "status": "success"}

        except Exception as e:
            return self._on_failure(self.current_source, str(e))

    def _on_failure(self, failed_source, error_msg):
        """处理失败"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        print(f"数据源 ({failed_source}) 失败: {error_msg}")
        print(f"失败次数: {self.failure_count}/3")

        # 3 次失败后切换到下一个数据源
        if self.failure_count >= 3:
            sources = [self.primary, self.fallback, self.tertiary]
            current_idx = sources.index(failed_source) if failed_source in sources else -1

            # 切换到下一个可用的数据源
            next_sources = [s for s in sources[current_idx+1:] if s != failed_source]

            if next_sources:
                self.current_source = next_sources[0]
                self.failure_count = 0
                print(f"自动切换到: {self.current_source}")
            else:
                print("没有可用的数据源了")

    def _get_from_akshare(self, stock_code, period, start_date, end_date):
        """从 AKShare 获取"""
        import akshare as ak

        try:
            if period == "daily":
                df = ak.stock_zh_a_hist(symbol=stock_code,
                                          period=period,
                                          adjust="qfq")
            else:
                print(f"AKShare 仅支持日线数据")
                return None

            # 标准化
            df = df.rename(columns={
                'date': '日期',
                'open': '开盘',
                'high': '最高',
                'low': '最低',
                'close': '收盘',
                'volume': '成交量'
            })

            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])

            return df

        except Exception as e:
            raise Exception(f"AKShare 获取失败: {e}")

    def _get_from_efinance(self, stock_code, period, start_date, end_date):
        """从 Efinance 获取"""
        import efinance as ef

        try:
            df = ef.stock.get_quote_history(stock_code, beg="20200101",
                                          k="d" if period=="daily" else "w",
                                          end_date=end_date)

            # 标准化
            df = df.rename(columns={
                'date': '日期',
                'open': '开盘',
                'high': '最高',
                'low': '最低',
                'close': '收盘',
                'volume': '成交量'
            })

            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])

            return df

        except Exception as e:
            raise Exception(f"Efinance 获取失败: {e}")

    def _get_from_tushare(self, stock_code, period, start_date, end_date):
        """从 Tushare 获取"""
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
            else:
                print(f"Tushare 仅支持日线数据")
                return None

            df = df.reset_index()
            df = df.rename(columns={
                'date': 'trade_date',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'vol': 'volume',
                'code': 'code'
            })

            return df

        except Exception as e:
            raise Exception(f"Tushare 获取失败: {e}")

    def _get_from_baostock(self, stock_code, period, start_date, end_date):
        """从 Baostock 获取"""
        import baostock as bs

        try:
            # Baostock 仅支持日线
            if period != "daily":
                return None

            df = bs.query_history_k_data_plus(
                stock_code,
                klt=101,
                start_date=start_date or "2020-01-01",
                end_date=end_date,
                adjustflag="2"
            )

            # 标准化
            df = df.rename(columns={
                'date': 'date',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'volume': 'vol'
            })

            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])

            return df

        except Exception as e:
            raise Exception(f"Baostock 获取失败: {e}")

    def get_market_data(self, market="A股大盘"):
        """获取大盘数据"""
        import akshare as ak

        try:
            if market == "A股大盘":
                data = ak.stock_zh_index_daily(symbol="sh000001",
                                                start_date="20200101")
            elif market == "上证50":
                data = ak.stock_zh_index_daily(symbol="sh000016",
                                                start_date="20200101")
            elif market == "沪深300":
                data = ak.stock_zh_index_daily(symbol="sh000300",
                                                start_date="20200101")
            else:
                data = None

            if data is not None:
                data = data.rename(columns={
                    'date': '日期',
                    'open': 'open',
                    'high': 'high',
                    'low': 'low',
                    'close': 'close',
                    'volume': 'volume'
                })

            return {"data": data, "source": "akshare", "quality": "high", "status": "success"}

        except Exception as e:
            return {"data": None, "source": "akshare", "quality": "low", "status": "failed", "error": str(e)}

    def get_status(self):
        """获取数据源状态"""
        return {
            "primary": self.primary,
            "fallback": self.fallback,
            "tertiary": self.tertiary,
            "current_source": self.current_source,
            "failure_count": self.failure_count,
            "is_cooldown": self._is_cooldown(),
            "sources_available": ["akshare", "efinance", "tushare", "baostock"]
        }


if __name__ == "__main__":
    # 测试
    print("="*70)
    print("统一数据管理器 v3 测试")
    print("="*70)

    dm = UnifiedDataManagerV3(
        primary="akshare",
        fallback="tushare",
        tertiary="baostock"
    )

    # 测试1: 状态检查
    print("\n1️⃣ 测试数据源状态\n")
    status = dm.get_status()
    print(f"当前数据源: {status['current_source']}")
    print(f"可用数据源: {', '.join(status['sources_available'])}")

    # 测试2: 获取股票数据（优先真实数据）
    print("\n2️⃣ 测试股票数据获取\n")
    result = dm.get_stock_data("600519", period="daily", prefer_real_data=True)

    if result and result.get('status') == "success":
        print(f"成功获取数据")
        print(f"数据源: {result['source']}")
        print(f"数据质量: {result['quality']}")
    else:
        print("获取失败")

    print("\n✅ 所有测试完成！\n")
