#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地数据源生成器 - 修复版本
生成模拟的 A股/期货数据用于系统测试和演示
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class LocalDataSource:
    """本地数据源生成器"""

    def __init__(self):
        """初始化本地数据源"""
        print("="*50)
        print("本地数据源生成器 - 初始化")
        print("="*50)
        print("✅ 无需网络连接")
        print("✅ 数据稳定可靠")
        print("✅ 完全控制数据\n")

        # 股票基础数据
        self.stock_base_prices = {
            "600519": 1500.0,   # 茅台
            "000858": 180.0,    # 五粮液
            "002475": 25.0,      # 立讯精密
            "600036": 30.0,      # 招商银行
            "000001": 10.0,       # 平安银行
            "000002": 25.0,       # 万科A
            "600031": 35.0,      # 三一重工
        }

        self.stock_names = {
            "600519": "贵州茅台",
            "000858": "五粮液",
            "002475": "立讯精密",
            "600036": "招商银行",
            "000001": "平安银行",
            "000002": "万科A",
            "600031": "三一重工",
        }

    def get_stock_data(self, stock_code: str, period: str = "daily", start_date=None, end_date=None):
        """
        获取股票数据（生成模拟数据）

        Args:
            stock_code: 股票代码（如 600519）
            period: 数据周期
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            pd.DataFrame: K线数据
        """
        print(f"本地数据源生成: {stock_code} ({period})")

        # 确定数据范围
        n_days = 365
        dates = pd.date_range(end=datetime.now(), periods=n_days, freq='D')

        # 生成模拟价格数据（随机漫步）
        base_price = self.stock_base_prices.get(stock_code, 100.0)
        seed = hash(stock_code) % 10000
        np.random.seed(seed)

        # 波动率
        volatility = 0.015 + np.random.random() * 0.01

        prices = []
        for i in range(n_days):
            if i == 0:
                price = base_price
            else:
                # 随机漫步 + 漂变趋势
                trend = np.random.normal(0, volatility * 0.3)
                price = prices[-1] * (1 + trend + np.random.normal(0, volatility))
                # 确保价格为正数
                price = max(price, 1.0)

            prices.append(price)

        # 生成K线数据
        data = []
        for i, date in enumerate(dates):
            price = prices[i]
            
            # 简单的高低开生成
            high = price * (1 + abs(np.random.normal(0, 0.01)))
            low = price * (1 - abs(np.random.normal(0, 0.01)))
            
            if i == 0:
                open_price = price
            else:
                open_price = prices[i-1]
            
            # 成交量（随机）
            base_volume = 10000000
            volume = int(base_volume * (1 + np.random.uniform(-0.3, 0.5)))

            data.append({
                'date': date,
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(price, 2),
                'volume': volume
            })

        df = pd.DataFrame(data)
        print(f"本地数据生成成功，共 {len(df)} 条记录")
        return df

    def get_market_data(self, market: str = "A股大盘"):
        """
        获取大盘数据

        Args:
            market: 市场名称

        Returns:
            dict: 大盘数据
        """
        print(f"本地数据源生成: {market}")

        # 生成大盘数据
        dates = pd.date_range(end=datetime.now(), periods=365, freq='D')

        # 生成指数数据（随机漫步）
        base_index = 3000.0
        seed = 10000
        np.random.seed(seed)

        indices = []
        up_count = 0
        down_count = 0

        for i, date in enumerate(dates):
            # 市场趋势
            if i % 30 < 15:
                market_trend = 0.02  # 上涨期
            else:
                market_trend = -0.01  # 下跌期

            index = indices[-1] * (1 + market_trend + np.random.normal(0, 0.01))

            if i % 2 == 0:
                up_count += 1
            else:
                down_count += 1

            indices.append(index)

        # 判断市场环境
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

        df = pd.DataFrame({
            'date': list(dates),
            'index': indices
        })

        print(f"大盘数据生成成功")
        print(f"市场环境: {market_env}")
        print(f"上涨占比: {up_ratio*100:.1f}%")

        return {
            "data": df,
            "environment": market_env,
            "threshold": threshold,
            "up_count": up_count,
            "down_count": down_count,
            "up_ratio": up_ratio
        }

    def get_status(self):
        """获取数据源状态"""
        return {
            "source_type": "local",
            "description": "本地数据源生成器",
            "status": "stable",
            "network_required": False,
            "stocks_supported": list(self.stock_base_prices.keys()),
            "data_quality": "simulation",
            "advantages": [
                "无需网络连接",
                "数据稳定可靠",
                "可完全控制",
                "生成速度快"
            ],
            "disadvantages": [
                "非真实数据",
                "仅用于演示和测试"
            ]
        }


if __name__ == "__main__":
    # 测试代码
    print("本地数据源测试")

    source = LocalDataSource()

    # 测试1: 获取股票数据
    print("\n测试1: 获取贵州茅台数据")
    stock_data = source.get_stock_data("600519")
    print(f"数据形状: {stock_data.shape}")
    print(f"最近5条:\n{stock_data.tail(5)}")

    print("\n测试2: 获取大盘数据")
    market_data = source.get_market_data("A股大盘")
    print(f"市场环境: {market_data['environment']}")
    print(f"上涨占比: {market_data['up_ratio']*100:.1f}%")

    print("\n测试3: 数据源状态")
    status = source.get_status()
    print(f"数据源类型: {status['source_type']}")
    print(f"数据质量: {status['data_quality']}")
    print(f"支持的股票: {status['stocks_supported']}")

    print("\n所有测试完成")
