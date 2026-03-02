#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Baostock 数据源模块
集成 Baostock 作为 A股数据源
"""

import pandas as pd
from datetime import datetime

class BaostockDataSource:
    """Baostock 数据源"""

    def __init__(self, lg=None, pwd=None):
        """初始化 Baostock"""
        self.lg = lg
        self.pwd = pwd

        if self.lg and self.pwd:
            print(f"使用提供的账号密码")
        else:
            print("使用匿名模式")

    def get_stock_data(self, stock_code, period="daily", start_date=None, end_date=None):
        """
        获取股票数据

        Args:
            stock_code: 股票代码
            period: 周期
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            pd.DataFrame: K线数据
        """
        print(f"Baostock 获取数据: {stock_code}")

        # 尝试获取数据（匿名模式）
        try:
            import baostock as bs
            import pandas as pd

            if period == "daily":
                df = bs.query_history_k_data_plus(
                    stock_code,
                    klt=101,
                    start_date=start_date or "2020-01-01",
                    end_date=end_date,
                    adjustflag="2"
                )
            else:
                print(f"仅支持日线数据")
                return None

            if df is not None and len(df) > 0:
                # 标准化列名
                df = df.rename(columns={
                    'date': 'date',
                    'open': 'open',
                    'high': 'high',
                    'low': 'low',
                    'close': 'close',
                    'volume': 'vol',
                    'amount': 'amount'
                })

                print(f"获取成功，共 {len(df)} 条记录")
                return df

        except Exception as e:
            print(f"Baostock 获取失败: {e}")
            return None

    def authorize(self, lg=None, pwd=None):
        """认证"""
        try:
            import baostock as bs

            bs.login(lg=lg, pwd=pwd)
            print(f"Baostock 登录成功")
            return True

        except Exception as e:
            print(f"Baostock 认证失败: {e}")
            return False

    def logout(self):
        """登出"""
        try:
            import baostock as bs
            bs.logout()
            print("Baostock 已登出")
            return True

        except Exception as e:
            print(f"Baostock 登出失败: {e}")
            return False

    def get_status(self):
        """获取状态"""
        return {
            "source": "baostock",
            "authorized": self.lg is not None,
            "mode": "anonymous" if not self.lg else "authenticated"
        }


if __name__ == "__main__":
    # 测试
    source = BaostockDataSource()
    print("测试 Baostock 数据源")
    stock_data = source.get_stock_data("sh.600519", period="daily", start_date="2025-01-01", end_date="2026-02-28")

    if stock_data is not None:
        print(f"\n数据示例:\n{stock_data.tail(10)}")
