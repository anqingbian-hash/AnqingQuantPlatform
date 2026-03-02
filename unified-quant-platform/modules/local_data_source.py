#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地数据源生成器
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
            "600519": 1500.0,   # 贵州茅台
            "000858": 180.0,    # 五粮液
            "002475": 25.0,     # 立讯精密
            "600036": 30.0,      # 招商银行
            "000001": 10.0,      # 平安银行
            "000002": 25.0,      # 万科A
            "600031": 35.0,      # 三一重工
            "000858": 180.0,    # 五粮液
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
            stock_code: 股票代码
            period: 数据周期
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            pd.DataFrame: K线数据
        """
        print(f"📊 本地数据源生成: {stock_code} ({period})")

        # 确定数据范围
        n_days = 365
        dates = pd.date_range(end=datetime.now(), periods=n_days, freq='D')

        # 生成模拟价格数据（随机漫步）
        base_price = self.stock_base_prices.get(stock_code, 100.0)
        seed = hash(stock_code) % 10000
        random.seed(seed)

        prices = []
        volatilities = random.uniform(0.015, 0.03)  # 日波动率 1.5%-3%

        for i in range(n_days):
            if i == 0:
                price = base_price
            else:
                change = random.normal(0, volatilities)
                price = prices[-1] * (1 + change)

            prices.append(price)

        # 生成 K线数据
        data = []
        for i, date in enumerate(dates):
            price = prices[i]
            volatility_daily = volatilities * price

            # 生成开高低收
            high = price * (1 + random.uniform(0, 0.02))
            low = price * (1 - random.uniform(0, 0.02))

            if i == 0:
                open_price = price
            else:
                open_price = prices[i-1]

            # 生成成交量
            base_volume = 1000000
            volume_change = random.uniform(0.5, 2.0)
            volume = int(base_volume * volume_change)

            data.append({
                'date': date,
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(price, 2),
                'volume': volume
            })

        df = pd.DataFrame(data)
        print(f"✅ 本地数据生成成功，共 {len(df)} 条记录")
        return df

    def get_market_data(self, market: str = "A股大盘"):
        """
        获取大盘数据

        Args:
            market: 市场名称

        Returns:
            dict: 大盘数据
        """
        print(f"📊 本地数据源生成: {market}")

        # 生成大盘数据
        dates = pd.date_range(end=datetime.now(), periods=365, freq='D')

        # 生成指数数据
        base_index = 3000.0

        # 模拟市场环境（随机漫步）
        random.seed(10000)
        market_trend = random.choice([0.02, 0, -0.02])  # 上涨/震荡/下跌趋势

        indices = []
        up_count = 0
        down_count = 0

        for i, date in enumerate(dates):
            if i == 0:
                index = base_index
            else:
                change = random.normal(market_trend, 0.01)
                index = indices[-1] * (1 + change)

            if i % 2 == 0:  # 隔日判断涨跌
                change_pct = (index - indices[-2]) / indices[-2] if i >= 2 else 0
                if change_pct > 0:
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

        print(f"✅ 大盘数据生成成功")
        print(f"   市场环境: {market_env}")
        print(f"   动态阈值: {threshold}")
        print(f"   上涨占比: {up_ratio*100:.1f}%")

        return {
            "data": df,
            "environment": market_env,
            "threshold": threshold,
            "up_count": up_count,
            "down_count": down_count,
            "up_ratio": up_ratio
        }

    def get_futures_data(self, futures_code: str, period: str = "daily"):
        """
        获取期货数据（生成模拟数据）

        Args:
            futures_code: 期货代码
            period: 数据周期

        Returns:
            pd.DataFrame: 期货数据
        """
        print(f"📊 本地数据源生成: {futures_code} ({period})")

        # 期货基础数据
        futures_base = {
            "IF2403": 3500.0,  # 沪深300期货
            "IC2403": 5500.0,  # 中证500期货
            "IH2403": 2800.0,  # 上证50期货
        }

        base_price = futures_base.get(futures_code, 3000.0)

        # 生成数据
        n_days = 365
        dates = pd.date_range(end=datetime.now(), periods=n_days, freq='D')

        seed = hash(futures_code) % 10000
        random.seed(seed)

        prices = []
        volatilities = random.uniform(0.02, 0.04)  # 期货波动率更大

        for i in range(n_days):
            if i == 0:
                price = base_price
            else:
                change = random.normal(0, volatilities)
                price = prices[-1] * (1 + change)

            prices.append(price)

        # 生成 K线数据
        data = []
        for i, date in enumerate(dates):
            price = prices[i]
            volatility_daily = volatilities * price

            high = price * (1 + random.uniform(0, 0.03))
            low = price * (1 - random.uniform(0, 0.03))

            if i == 0:
                open_price = price
            else:
                open_price = prices[i-1]

            # 期货成交量更大
            base_volume = 50000000
            volume_change = random.uniform(0.5, 3.0)
            volume = int(base_volume * volume_change)

            data.append({
                'date': date,
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(price, 2),
                'volume': volume
            })

        df = pd.DataFrame(data)
        print(f"✅ 期货数据生成成功，共 {len(df)} 条记录")
        return df

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
                "无网络依赖",
                "数据稳定可靠",
                "可完全控制",
                "速度快"
            ],
            "disadvantages": [
                "非真实数据",
                "仅用于演示和测试"
            ]
        }


if __name__ == "__main__":
    # 测试代码
    print("\n🧪 本地数据源测试\n")

    source = LocalDataSource()

    # 测试1: 获取股票数据
    print("\n\n1️⃣ 测试股票数据获取\n")
    stock_data = source.get_stock_data("600519")
    print(f"数据形状: {stock_data.shape}")
    print(f"最近5条:\n{stock_data.tail(5)}")

    # 测试2: 获取大盘数据
    print("\n\n2️⃣ 测试大盘数据获取\n")
    market_data = source.get_market_data("A股大盘")
    print(f"市场环境: {market_data['environment']}")

    # 测试3: 获取期货数据
    print("\n\n3️⃣ 测试期货数据获取\n")
    futures_data = source.get_futures_data("IF2403")
    print(f"数据形状: {futures_data.shape}")

    # 测试4: 获取状态
    print("\n\n4️⃣ 数据源状态\n")
    status = source.get_status()
    print(f"数据源类型: {status['source_type']}")
    print(f"数据质量: {status['data_quality']}")

    print("\n✅ 所有测试完成！\n")
