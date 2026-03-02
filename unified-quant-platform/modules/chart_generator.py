#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图表生成器 v1.0
用于生成 K线图、指标图、收益曲线等可视化图表
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ChartGenerator:
    """图表生成器 v1.0"""

    def __init__(self):
        """初始化图表生成器"""
        print("="*70)
        print("图表生成器 v1.0 - 初始化")
        print("="*70)

        # 检查是否安装了 matplotlib
        try:
            import matplotlib
            matplotlib.use('Agg')  # 非交互式后端
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
            from matplotlib.font_manager import FontProperties

            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
            plt.rcParams['axes.unicode_minus'] = False

            self.plt = plt
            self.mdates = mdates
            self.font_props = None

            print("✅ matplotlib 已安装")
            print("✅ 支持 K线图、指标图、收益曲线等图表")
            print("✅ 支持 PNG、JPG、PDF 格式导出\n")

        except ImportError:
            print("⚠️ matplotlib 未安装，图表生成功能不可用")
            print("   安装命令: pip install matplotlib\n")
            self.plt = None

    def generate_kline_chart(self, stock_data, stock_name, stock_code, save_path=None):
        """
        生成 K线图

        Args:
            stock_data: 股票K线数据
            stock_name: 股票名称
            stock_code: 股票代码
            save_path: 保存路径

        Returns:
            str: 图片路径
        """
        if self.plt is None:
            print("❌ matplotlib 未安装，无法生成图表")
            return None

        print(f"\n{'='*70}")
        print(f"📊 生成 K线图: {stock_name} ({stock_code})")
        print(f"{'='*70}")

        try:
            # 准备数据
            data = stock_data.copy()
            data = data.set_index('date')

            # 添加移动平均线
            data['MA5'] = data['close'].rolling(window=5).mean()
            data['MA10'] = data['close'].rolling(window=10).mean()
            data['MA20'] = data['close'].rolling(window=20).mean()

            # 添加成交量均线
            data['VOL_MA5'] = data['volume'].rolling(window=5).mean()

            # 尝试使用 mplfinance
            try:
                from mplfinance import mpf

                # 创建图表
                fig, axes = mpf.plot(
                    data,
                    type='candle',
                    style='yahoo',
                    title=f'{stock_name} ({stock_code}) K线图',
                    ylabel='价格',
                    volume=True,
                    mav=(5, 10, 20),
                    volume_panel=1,
                    returnfig=True,
                    figsize=(16, 10)
                )

                # 保存图表
                if save_path is None:
                    save_path = f"charts/{stock_code}_kline.png"
                    os.makedirs('charts', exist_ok=True)

                fig.savefig(save_path, dpi=150, bbox_inches='tight')
                self.plt.close(fig)

                print(f"✅ K线图已保存到: {save_path}")
                return save_path

            except ImportError:
                print("⚠️ mplfinance 未安装，使用简化版 K线图")

            # 简化版 K线图
            fig, (ax1, ax2) = self.plt.subplots(2, 1, figsize=(16, 10), gridspec_kw={'height_ratios': [3, 1]})

            # 绘制价格
            ax1.plot(data.index, data['close'], label='收盘价', color='blue', linewidth=1)
            ax1.plot(data.index, data['MA5'], label='MA5', color='orange', linewidth=1, alpha=0.7)
            ax1.plot(data.index, data['MA10'], label='MA10', color='green', linewidth=1, alpha=0.7)
            ax1.plot(data.index, data['MA20'], label='MA20', color='red', linewidth=1, alpha=0.7)

            ax1.set_title(f'{stock_name} ({stock_code}) K线图', fontsize=16)
            ax1.set_ylabel('价格', fontsize=12)
            ax1.legend(loc='best')
            ax1.grid(True, alpha=0.3)

            # 绘制成交量
            ax2.bar(data.index, data['volume'], color='lightblue', alpha=0.6)
            ax2.plot(data.index, data['VOL_MA5'], label='成交量均线', color='orange', linewidth=1)
            ax2.set_ylabel('成交量', fontsize=12)
            ax2.legend(loc='best')
            ax2.grid(True, alpha=0.3)

            # 格式化 x 轴
            for ax in [ax1, ax2]:
                ax.xaxis.set_major_formatter(self.mdates.DateFormatter('%Y-%m-%d'))
                ax.xaxis.set_major_locator(self.mdates.DayLocator(interval=10))
                self.plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

            self.plt.tight_layout()

            # 保存图表
            if save_path is None:
                save_path = f"charts/{stock_code}_kline_simple.png"
                os.makedirs('charts', exist_ok=True)

            fig.savefig(save_path, dpi=150, bbox_inches='tight')
            self.plt.close(fig)

            print(f"✅ 简化版 K线图已保存到: {save_path}")
            return save_path

        except Exception as e:
            print(f"❌ 生成 K线图失败: {e}")
            return None

    def generate_indicator_chart(self, stock_data, stock_name, stock_code, indicators=['RSI', 'MACD', 'KDJ'], save_path=None):
        """
        生成技术指标图

        Args:
            stock_data: 股票K线数据
            stock_name: 股票名称
            stock_code: 股票代码
            indicators: 指标列表
            save_path: 保存路径

        Returns:
            str: 图片路径
        """
        if self.plt is None:
            print("❌ matplotlib 未安装，无法生成图表")
            return None

        print(f"\n{'='*70}")
        print(f"📊 生成技术指标图: {stock_name} ({stock_code})")
        print(f"{'='*70}")

        try:
            # 计算指标
            data = stock_data.copy()
            data = data.set_index('date')

            # RSI
            if 'RSI' in indicators:
                data['RSI'] = self._calculate_rsi(data['close'])

            # MACD
            if 'MACD' in indicators:
                data['MACD_DIF'], data['MACD_DEA'], data['MACD_BAR'] = self._calculate_macd(data['close'])

            # KDJ
            if 'KDJ' in indicators:
                data['KDJ_K'], data['KDJ_D'], data['KDJ_J'] = self._calculate_kdj(data)

            # 创建图表
            n_indicators = len(indicators)
            fig, axes = self.plt.subplots(n_indicators, 1, figsize=(16, 4 * n_indicators))
            if n_indicators == 1:
                axes = [axes]

            # 绘制每个指标
            for i, indicator in enumerate(indicators):
                ax = axes[i]

                if indicator == 'RSI':
                    ax.plot(data.index, data['RSI'], label='RSI', color='purple', linewidth=1)
                    ax.axhline(y=70, color='r', linestyle='--', linewidth=1, alpha=0.5)
                    ax.axhline(y=30, color='g', linestyle='--', linewidth=1, alpha=0.5)
                    ax.set_ylabel('RSI')
                    ax.set_ylim(0, 100)
                    ax.legend(loc='best')

                elif indicator == 'MACD':
                    ax.plot(data.index, data['MACD_DIF'], label='DIF', color='blue', linewidth=1)
                    ax.plot(data.index, data['MACD_DEA'], label='DEA', color='orange', linewidth=1)
                    ax.bar(data.index, data['MACD_BAR'], label='BAR', color='lightblue', alpha=0.6)
                    ax.set_ylabel('MACD')
                    ax.legend(loc='best')

                elif indicator == 'KDJ':
                    ax.plot(data.index, data['KDJ_K'], label='K', color='blue', linewidth=1)
                    ax.plot(data.index, data['KDJ_D'], label='D', color='orange', linewidth=1)
                    ax.plot(data.index, data['KDJ_J'], label='J', color='purple', linewidth=1)
                    ax.set_ylabel('KDJ')
                    ax.legend(loc='best')

                ax.grid(True, alpha=0.3)
                ax.xaxis.set_major_formatter(self.mdates.DateFormatter('%Y-%m-%d'))
                ax.xaxis.set_major_locator(self.mdates.DayLocator(interval=10))
                self.plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

            self.plt.suptitle(f'{stock_name} ({stock_code}) 技术指标', fontsize=16)
            self.plt.tight_layout()

            # 保存图表
            if save_path is None:
                save_path = f"charts/{stock_code}_indicators.png"
                os.makedirs('charts', exist_ok=True)

            fig.savefig(save_path, dpi=150, bbox_inches='tight')
            self.plt.close(fig)

            print(f"✅ 技术指标图已保存到: {save_path}")
            return save_path

        except Exception as e:
            print(f"❌ 生成技术指标图失败: {e}")
            return None

    def generate_equity_curve(self, equity_curve, save_path=None):
        """
        生成资金曲线

        Args:
            equity_curve: 资金曲线数据
            save_path: 保存路径

        Returns:
            str: 图片路径
        """
        if self.plt is None:
            print("❌ matplotlib 未安装，无法生成图表")
            return None

        print(f"\n{'='*70}")
        print(f"📊 生成资金曲线")
        print(f"{'='*70}")

        try:
            # 准备数据
            df = pd.DataFrame(equity_curve)
            df['date'] = pd.to_datetime(df['date'])

            # 创建图表
            fig, ax = self.plt.subplots(figsize=(16, 8))

            # 绘制资金曲线
            ax.plot(df['date'], df['capital'], label='总资产', color='blue', linewidth=2)

            # 绘制持仓价值
            ax.plot(df['date'], df['position_value'], label='持仓价值', color='orange', linewidth=1, alpha=0.7)

            # 绘制现金
            ax.plot(df['date'], df['cash'], label='现金', color='green', linewidth=1, alpha=0.7)

            ax.set_title('资金曲线', fontsize=16)
            ax.set_ylabel('资金 (¥)', fontsize=12)
            ax.legend(loc='best')
            ax.grid(True, alpha=0.3)

            # 格式化 y 轴
            ax.yaxis.set_major_formatter(self.plt.FuncFormatter(lambda x, p: f'¥{x:,.0f}'))

            # 格式化 x 轴
            ax.xaxis.set_major_formatter(self.mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(self.mdates.DayLocator(interval=10))
            self.plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

            self.plt.tight_layout()

            # 保存图表
            if save_path is None:
                save_path = "charts/equity_curve.png"
                os.makedirs('charts', exist_ok=True)

            fig.savefig(save_path, dpi=150, bbox_inches='tight')
            self.plt.close(fig)

            print(f"✅ 资金曲线已保存到: {save_path}")
            return save_path

        except Exception as e:
            print(f"❌ 生成资金曲线失败: {e}")
            return None

    def _calculate_rsi(self, close_prices, period=14):
        """计算 RSI"""
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_macd(self, close_prices, fast=12, slow=26, signal=9):
        """计算 MACD"""
        ema_fast = close_prices.ewm(span=fast).mean()
        ema_slow = close_prices.ewm(span=slow).mean()
        dif = ema_fast - ema_slow
        dea = dif.ewm(span=signal).mean()
        bar = (dif - dea) * 2
        return dif, dea, bar

    def _calculate_kdj(self, data, n=9, m1=3, m2=3):
        """计算 KDJ"""
        low = data['low'].rolling(window=n).min()
        high = data['high'].rolling(window=n).max()
        close = data['close']

        rsv = (close - low) / (high - low) * 100
        k = rsv.ewm(com=m1).mean()
        d = k.ewm(com=m2).mean()
        j = 3 * k - 2 * d

        return k, d, j


if __name__ == "__main__":
    # 测试代码
    print("图表生成器 v1.0 测试")

    # 创建模拟数据
    dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
    base_price = 100.0
    prices = []
    for i in range(100):
        if i == 0:
            price = base_price
        else:
            price = prices[-1] * (1 + np.random.normal(0, 0.02))
        prices.append(price)

    # 创建 DataFrame
    stock_data = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p * 1.02 for p in prices],
        'low': [p * 0.98 for p in prices],
        'close': prices,
        'volume': [10000000 * (1 + np.random.uniform(-0.3, 0.5)) for _ in range(100)]
    })

    # 创建图表生成器
    chart_gen = ChartGenerator()

    # 测试 K线图
    print("\n测试1: 生成 K线图")
    kline_path = chart_gen.generate_kline_chart(
        stock_data,
        "测试股票",
        "TEST",
        "charts/test_kline.png"
    )

    # 测试技术指标图
    print("\n测试2: 生成技术指标图")
    indicator_path = chart_gen.generate_indicator_chart(
        stock_data,
        "测试股票",
        "TEST",
        ['RSI', 'MACD'],
        "charts/test_indicators.png"
    )

    # 测试资金曲线
    print("\n测试3: 生成资金曲线")
    equity_curve = [
        {
            'date': dates[i],
            'capital': 100000 * (1 + 0.0005 * i),
            'position_value': 100000 * (1 + 0.0005 * i) * 0.7,
            'cash': 100000 * (1 + 0.0005 * i) * 0.3
        }
        for i in range(100)
    ]
    equity_path = chart_gen.generate_equity_curve(equity_curve, "charts/test_equity.png")

    print("\n所有测试完成")
