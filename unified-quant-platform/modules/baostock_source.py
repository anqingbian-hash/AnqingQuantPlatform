#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Baostock 数据源模块
集成 Baostock 作为 A股数据源
"""

import pandas as pd
import baostock as bs
from datetime import datetime

class BaostockDataSource:
    """Baostock 数据源"""

    def __init__(self, lg=None, pwd=None):
        """
        初始化 Baostock

        Args:
            lg: 账号
            pwd: 密码
        """
        self.lg = lg
        self.pwd = pwd
        self.authorized = False

        print(f"✅ Baostock 数据源初始化完成")

        if not self.lg:
            print("⚠️ 未提供账号，使用匿名模式")
            print("   匿名模式下数据受限")

    def authorize(self):
        """认证"""
        try:
            print("🔐 尝试 Baostock 登录...")

            # 匿名登录
            lg = bs.login()
            if lg:
                print(f"✅ Baostock 匿名登录成功")
                self.authorized = True
                return True
            else:
                print("❌ 登录失败")
                return False

        except Exception as e:
            print(f"❌ Baostock 认证异常: {e}")
            return False

    def get_status(self):
        """获取数据源状态"""
        return {
            "source_type": "baostock",
            "description": "Baostock 数据源",
            "status": "stable",
            "network_required": True,
            "stocks_supported": ["A股"],
            "data_quality": "very_high",
            "advantages": [
                "免费匿名模式",
                "数据质量高",
                "无频率限制"
            ],
            "disadvantages": [
                "仅支持A股",
                "功能相对简单"
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
        print(f"📊 Baostock 获取股票数据: {stock_code} ({period})")

        # 如果未认证，先登录
        if not self.authorized and not self.lg:
            print("⚠️ 未认证，尝试匿名获取数据...")
            # 匿名模式下可能无法获取数据
            return None

        try:
            # 获取数据
            if period == "daily":
                df = bs.query_history_k_data_plus(
                    stock_code,
                    fields=[
                        "date",
                        "open",
                        "high",
                        "low",
                        "close",
                        "preclose",
                        "vol",
                        "amount",
                        "adjustflag",
                        "pctChg"
                    ],
                    klt=101,  # 获取101条
                    start_date=start_date,
                    end_date=end_date,
                    adjustflag="2",  # 前复权
                    fq_ref_date="1990-12-19"
                )
            else:
                print(f"⚠️ 仅支持日线数据，period={period}")
                return None

            # 标准化列名
            if df is not None and len(df) > 0:
                # 重命名列名以匹配统一格式
                df = df.rename(columns={
                    'date': 'date',
                    'open': 'open',
                    'high': 'high',
                    'low': 'low',
                    'close': 'close',
                    'vol': 'volume',
                    'amount': 'amount',
                    'adjust': 'adjust',
                    'pctChg': 'change_percent'
                })

                # 确保日期是 datetime 格式
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])

                print(f"✅ Baostock 获取成功，共 {len(df)} 条记录")
                return df
            else:
                print("❌ 未获取到数据")
                return None

        except Exception as e:
            print(f"❌ Baostock 获取失败: {e}")
            raise e

    def logout(self):
        """登出"""
        try:
            bs.logout()
            self.authorized = False
            print("✅ Baostock 已登出")
        except Exception as e:
            print(f"❌ 登出失败: {e}")


if __name__ == "__main__":
    # 测试代码
    print("="*60)
    print("Baostock 数据源测试")
    print("="*60)

    # 创建数据源（匿名模式）
    source = BaostockDataSource()

    # 测试：获取贵州茅台数据
    print("\n测试：获取贵州茅台 (600519) 数据")
    try:
        data = source.get_stock_data("sh.600519", period="daily")

        if data is not None:
            print(f"数据形状: {data.shape}")
            print(f"最近5条:\n{data.tail(5)}")
        else:
            print("未获取到数据")

    except Exception as e:
        print(f"错误: {e}")

    print("\n" + "="*60)
    print("测试完成")
