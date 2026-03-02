#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一量化平台 - Efinance 数据源模块
集成 Efinance 作为备选数据源
"""

import pandas as pd
import numpy as np
import efinance as ef
from datetime import datetime, timedelta

class EfinanceDataSource:
    """Efinance 数据源"""

    def __init__(self):
        """初始化 Efinance 数据源"""
        print("="*50)
        print("Efinance 数据源 - 初始化")
        print("="*50)
        print("✅ 无需 API Token")
        print("✅ 支持实时行情")
        print("✅ 数据质量高\n")

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
        print(f"📊 Efinance 获取股票数据: {stock_code} ({period})")

        try:
            # 格式化股票代码
            if '.' not in stock_code:
                # 判断是沪市还是深市
                if stock_code.startswith('6'):
                    formatted_code = f"SH{stock_code}"
                else:
                    formatted_code = f"SZ{stock_code}"
            else:
                formatted_code = stock_code.upper()

            # 获取数据
            df = ef.stock.get_quote_history(
                stock_codes=formatted_code,
                beg=start_date,
                end=end_date,
                klt=101 if period == "daily" else 102 if period == "weekly" else 103
            )

            # 标准化列名
            df = df.rename(columns={
                '股票代码': 'code',
                '股票名称': 'name',
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount',
                '振幅': 'amplitude',
                '涨跌幅': 'change_percent',
                '涨跌额': 'change_amount',
                '换手率': 'turnover'
            })

            # 确保日期是 datetime 格式
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])

            print(f"✅ Efinance 获取成功，共 {len(df)} 条记录")
            return df

        except Exception as e:
            print(f"❌ Efinance 获取失败: {e}")
            raise e

    def get_realtime_quote(self, stock_code: str):
        """
        获取实时行情

        Args:
            stock_code: 股票代码（如 600519）

        Returns:
            pd.DataFrame: 实时行情数据
        """
        print(f"📊 Efinance 获取实时行情: {stock_code}")

        try:
            # 格式化股票代码
            if '.' not in stock_code:
                # 判断是沪市还是深市
                if stock_code.startswith('6'):
                    formatted_code = f"SH{stock_code}"
                else:
                    formatted_code = f"SZ{stock_code}"
            else:
                formatted_code = stock_code.upper()

            # 获取实时数据
            df = ef.stock.get_realtime_quotes(symbols=formatted_code)

            # 标准化列名
            df = df.rename(columns={
                '股票代码': 'code',
                '股票名称': 'name',
                '最新价': 'price',
                '涨跌幅': 'change_percent',
                '涨跌额': 'change_amount',
                '成交量': 'volume',
                '成交额': 'amount',
                '今开': 'open',
                '昨收': 'pre_close',
                '最高': 'high',
                '最低': 'low'
            })

            print(f"✅ Efinance 实时行情获取成功")
            return df

        except Exception as e:
            print(f"❌ Efinance 实时行情获取失败: {e}")
            raise e

    def get_index_data(self, index_code: str):
        """
        获取指数数据

        Args:
            index_code: 指数代码（如 sh000001）

        Returns:
            pd.DataFrame: 指数数据
        """
        print(f"📊 Efinance 获取指数数据: {index_code}")

        try:
            # 计算日期范围
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")

            # 格式化指数代码
            formatted_code = index_code.upper()

            # 获取数据
            df = ef.stock.get_quote_history(
                stock_codes=formatted_code,
                beg=start_date,
                end=end_date,
                klt=101
            )

            # 标准化列名
            df = df.rename(columns={
                '股票代码': 'code',
                '股票名称': 'name',
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount',
                '振幅': 'amplitude',
                '涨跌幅': 'change_percent'
            })

            # 确保日期是 datetime 格式
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])

            print(f"✅ Efinance 指数获取成功，共 {len(df)} 条记录")
            return df

        except Exception as e:
            print(f"❌ Efinance 指数获取失败: {e}")
            raise e

    def get_market_data(self, market: str = "A股大盘"):
        """
        获取大盘数据

        Args:
            market: 市场名称

        Returns:
            dict: 大盘数据
        """
        print(f"📊 Efinance 获取大盘数据: {market}")

        try:
            # 获取上证指数
            df = self.get_index_data("sh000001")

            # 计算市场环境
            if df is not None and len(df) > 0:
                recent = df.tail(30)
                up_count = len(recent[recent['close'] > recent['open']])
                down_count = len(recent[recent['close'] < recent['open']])
                up_ratio = up_count / (up_count + down_count)

                # 判断市场环境
                if up_ratio > 0.6:
                    market_env = "强势"
                    threshold = 8.5
                elif up_ratio > 0.4:
                    market_env = "震荡"
                    threshold = 9.0
                else:
                    market_env = "弱势"
                    threshold = 9.5

                return {
                    "data": df,
                    "environment": market_env,
                    "threshold": threshold,
                    "up_count": up_count,
                    "down_count": down_count,
                    "up_ratio": up_ratio
                }
            else:
                return None

        except Exception as e:
            print(f"❌ Efinance 大盘获取失败: {e}")
            raise e

    def get_status(self):
        """获取数据源状态"""
        return {
            "source_type": "efinance",
            "description": "Efinance 数据源",
            "status": "stable",
            "network_required": True,
            "stocks_supported": ["A股", "指数", "港股", "美股", "期货", "基金"],
            "data_quality": "high",
            "advantages": [
                "完全免费",
                "无需 API Token",
                "支持实时行情",
                "数据质量高"
            ],
            "disadvantages": [
                "部分功能需要网络",
                "文档相对简单"
            ]
        }


if __name__ == "__main__":
    # 测试代码
    print("Efinance 数据源测试")

    source = EfinanceDataSource()

    # 测试1: 获取股票数据
    print("\n测试1: 获取贵州茅台数据")
    try:
        stock_data = source.get_stock_data("600519")
        print(f"数据形状: {stock_data.shape}")
        print(f"最近5条:\n{stock_data.tail(5)}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

    # 测试2: 获取大盘数据
    print("\n测试2: 获取大盘数据")
    try:
        market_data = source.get_market_data("A股大盘")
        if market_data:
            print(f"市场环境: {market_data['environment']}")
            print(f"上涨占比: {market_data['up_ratio']*100:.1f}%")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

    # 测试3: 数据源状态
    print("\n测试3: 数据源状态")
    status = source.get_status()
    print(f"数据源类型: {status['source_type']}")
    print(f"数据质量: {status['data_quality']}")
    print(f"支持的股票: {status['stocks_supported']}")

    print("\n所有测试完成")
