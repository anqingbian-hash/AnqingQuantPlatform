#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一量化平台 - Tushare 数据源模块
集成 Tushare 作为备选数据源
"""

import pandas as pd
import numpy as np
import tushare as ts
from datetime import datetime

class TushareDataSource:
    """Tushare 数据源"""

    def __init__(self, token=None):
        """
        初始化 Tushare 数据源

        Args:
            token: Tushare API Token（如果有的话）
        """
        self.token = token
        self.pro = ts.pro_api(token) if token else None

        print(f"✅ Tushare 数据源初始化完成")
        if self.token:
            print(f"   API Token: {self.token[:10]}...")
        else:
            print(f"   使用免费 API（受限）")

    def get_status(self):
        """获取数据源状态"""
        return {
            "source_type": "tushare",
            "description": "Tushare 数据源",
            "status": "stable",
            "network_required": True,
            "stocks_supported": ["A股", "指数", "期货"],
            "data_quality": "high" if self.token else "medium",
            "advantages": [
                "数据质量高",
                "覆盖面广",
                "免费可用"
            ],
            "disadvantages": [
                "免费版限制较多",
                "需要注册获取Token"
            ]
        }

    def get_stock_data(self, stock_code: str, period: str = "daily", start_date=None, end_date=None):
        """
        获取股票数据

        Args:
            stock_code: 股票代码（如 600519）
            period: 数据周期（daily/weekly/monthly）
            start_date: 开始日期（YYYY-MM-DD）
            end_date: 结束日期（YYYY-MM-DD）

        Returns:
            pd.DataFrame: K线数据
        """
        print(f"📊 Tushare 获取股票数据: {stock_code} ({period})")

        try:
            # Tushare 股票历史数据
            if period == "daily":
                df = ts.pro_bar(
                    ts_code=stock_code,
                    adj='qfq',  # 前复权
                    start_date=start_date or "20200101",
                    end_date=end_date,
                    freq='D'
                )
            elif period == "weekly":
                df = ts.pro_bar(
                    ts_code=stock_code,
                    adj='qfq',
                    start_date=start_date or "20200101",
                    end_date=end_date,
                    freq='W'
                )
            else:  # monthly
                df = ts.pro_bar(
                    ts_code=stock_code,
                    adj='qfq',
                    start_date=start_date or "20200101",
                    end_date=end_date,
                    freq='M'
                )

            # 标准化列名
            df = df.reset_index()
            df = df.rename(columns={
                'ts_code': 'code',
                'trade_date': 'date',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'vol': 'volume',
                'amount': 'amount',
                'pct_chg': 'change_percent'
            })

            print(f"✅ Tushare 获取成功，共 {len(df)} 条记录")
            return df

        except Exception as e:
            print(f"❌ Tushare 获取失败: {e}")
            raise e

    def get_index_data(self, index_code: str):
        """
        获取指数数据

        Args:
            index_code: 指数代码（如 sh000001）

        Returns:
            pd.DataFrame: 指数数据
        """
        print(f"📊 Tushare 获取指数数据: {index_code}")

        try:
            df = ts.pro_bar(
                ts_code=index_code,
                adj='qfq',
                start_date="20200101",
                freq='D'
            )

            df = df.reset_index()
            df = df.rename(columns={
                'ts_code': 'code',
                'trade_date': 'date',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'vol': 'volume'
            })

            print(f"✅ Tushare 指数获取成功，共 {len(df)} 条记录")
            return df

        except Exception as e:
            print(f"❌ Tushare 指数获取失败: {e}")
            raise e

    def get_futures_data(self, futures_code: str):
        """
        获取期货数据

        Args:
            futures_code: 期货代码

        Returns:
            pd.DataFrame: 期货数据
        """
        print(f"📊 Tushare 获取期货数据: {futures_code}")

        try:
            df = ts.pro_fut_bar(
                ts_code=futures_code,
                start_date="20200101",
                freq='D'
            )

            df = df.reset_index()
            df = df.rename(columns={
                'ts_code': 'code',
                'trade_date': 'date',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'vol': 'volume'
            })

            print(f"✅ Tushare 期货获取成功，共 {len(df)} 条记录")
            return df

        except Exception as e:
            print(f"❌ Tushare 期货获取失败: {e}")
            raise e


if __name__ == "__main__":
    # 测试代码
    print("="*50)
    print("Tushare 数据源测试")
    print("="*50)

    # 创建 Tushare 数据源（不使用 Token，免费 API）
    tushare = TushareDataSource()

    # 测试1: 获取股票数据
    print("\n\n测试1: 获取上证指数数据\n")
    try:
        index_data = tushare.get_index_data("sh000001")
        print(f"数据形状: {index_data.shape}")
        print(f"最近5条:\n{index_data.tail(5)}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

    print("\n" + "="*50)
    print("✅ 所有测试完成！")
    print("="*50)
