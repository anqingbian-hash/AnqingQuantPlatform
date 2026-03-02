#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回测系统 v1.0
用于验证量化策略的历史表现
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.quant_factors_v2 import QuantFactorsV2
from modules.ntdf_signal_v2 import NtdfSignalV2

class BacktestEngine:
    """回测引擎 v1.0"""

    def __init__(self, initial_capital=100000):
        """
        初始化回测引擎

        Args:
            initial_capital: 初始资金
        """
        print("="*70)
        print("回测系统 v1.0 - 初始化")
        print("="*70)

        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.position = 0  # 持仓数量
        self.position_value = 0  # 持仓价值
        self.cash = initial_capital  # 现金
        self.trades = []  # 交易记录
        self.equity_curve = []  # 资金曲线

        # 初始化信号计算器
        self.quant_factors = QuantFactorsV2()
        self.ntdf_signal = NtdfSignalV2()

        # 回测参数
        self.commission_rate = 0.0003  # 手续费率 0.03%
        self.slippage_rate = 0.0001  # 滑点率 0.01%

        print(f"✅ 初始资金: ¥{initial_capital:,.2f}")
        print(f"✅ 手续费率: {self.commission_rate*100:.3f}%")
        print(f"✅ 滑点率: {self.slippage_rate*100:.3f}%\n")

    def run_backtest(self, stock_data, strategy_params=None):
        """
        运行回测

        Args:
            stock_data: 股票K线数据
            strategy_params: 策略参数

        Returns:
            dict: 回测结果
        """
        if stock_data is None or len(stock_data) < 50:
            return None

        print(f"\n{'='*70}")
        print(f"📊 开始回测")
        print(f"{'='*70}")
        print(f"数据长度: {len(stock_data)} 条")
        print(f"回测周期: {stock_data['date'].iloc[0]} 至 {stock_data['date'].iloc[-1]}")

        # 默认策略参数
        if strategy_params is None:
            strategy_params = {
                "buy_threshold": 7.0,      # 买入阈值
                "sell_threshold": 4.0,     # 卖出阈值
                "stop_loss": -0.05,        # 止损（-5%）
                "take_profit": 0.15,       # 止盈（+15%）
                "position_size": 0.95       # 仓位比例
            }

        print(f"\n策略参数:")
        print(f"   买入阈值: {strategy_params['buy_threshold']}")
        print(f"   卖出阈值: {strategy_params['sell_threshold']}")
        print(f"   止损: {strategy_params['stop_loss']*100:.1f}%")
        print(f"   止盈: {strategy_params['take_profit']*100:.1f}%")

        # 重置状态
        self.current_capital = self.initial_capital
        self.position = 0
        self.position_value = 0
        self.cash = self.initial_capital
        self.trades = []
        self.equity_curve = []

        # 记录持仓成本
        entry_price = 0
        entry_date = None

        # 逐日回测
        for i in range(50, len(stock_data)):  # 前50天用于计算指标
            # 获取当前数据
            current_data = stock_data.iloc[:i+1]

            # 获取当前价格
            current_price = stock_data.iloc[i]['close']
            current_date = stock_data.iloc[i]['date']

            # 计算信号
            quant_factors = self.quant_factors.calculate_all_factors(current_data)
            quant_score = self.quant_factors.calculate_total_score(quant_factors)

            ntdf_signal = self.ntdf_signal.calculate_signal(current_data)
            ntdf_score = ntdf_signal.get('score', 0) if ntdf_signal else 0

            # 融合评分
            fusion_score = (quant_score * 0.7 + ntdf_score * 0.3)

            # 更新持仓价值
            if self.position > 0:
                self.position_value = self.position * current_price
            else:
                self.position_value = 0

            # 计算当前总资产
            self.current_capital = self.cash + self.position_value
            self.equity_curve.append({
                'date': current_date,
                'capital': self.current_capital,
                'cash': self.cash,
                'position_value': self.position_value,
                'position': self.position
            })

            # 持仓逻辑
            if self.position > 0:
                # 检查止损
                return_rate = (current_price - entry_price) / entry_price
                if return_rate <= strategy_params['stop_loss']:
                    # 触发止损
                    self._sell(current_price, current_date, "止损")
                    self.position = 0
                    entry_price = 0
                    entry_date = None
                    continue

                # 检查止盈
                if return_rate >= strategy_params['take_profit']:
                    # 触发止盈
                    self._sell(current_price, current_date, "止盈")
                    self.position = 0
                    entry_price = 0
                    entry_date = None
                    continue

                # 检查卖出信号
                if fusion_score <= strategy_params['sell_threshold']:
                    # 触发卖出
                    self._sell(current_price, current_date, f"卖出信号({fusion_score:.2f})")
                    self.position = 0
                    entry_price = 0
                    entry_date = None
                    continue

            # 空仓逻辑
            if self.position == 0:
                # 检查买入信号
                if fusion_score >= strategy_params['buy_threshold']:
                    # 计算买入数量
                    buy_amount = self.cash * strategy_params['position_size']
                    buy_price = current_price * (1 + self.slippage_rate)
                    commission = buy_amount * self.commission_rate

                    buy_shares = int((buy_amount - commission) / buy_price)

                    if buy_shares > 0:
                        self.position = buy_shares
                        self.cash -= buy_shares * buy_price + commission
                        entry_price = buy_price
                        entry_date = current_date

                        self.trades.append({
                            'date': current_date,
                            'action': '买入',
                            'price': buy_price,
                            'shares': buy_shares,
                            'commission': commission,
                            'reason': f"买入信号({fusion_score:.2f})",
                            'score': fusion_score
                        })

        # 强制平仓
        if self.position > 0:
            final_price = stock_data.iloc[-1]['close']
            final_date = stock_data.iloc[-1]['date']
            self._sell(final_price, final_date, "回测结束")

        # 生成回测报告
        return self._generate_report(stock_data, strategy_params)

    def _sell(self, price, date, reason):
        """执行卖出"""
        sell_price = price * (1 - self.slippage_rate)
        sell_value = self.position * sell_price
        commission = sell_value * self.commission_rate

        self.cash += sell_value - commission

        self.trades.append({
            'date': date,
            'action': '卖出',
            'price': sell_price,
            'shares': self.position,
            'commission': commission,
            'reason': reason,
            'pnl': sell_price - self.trades[-1]['price'] if len(self.trades) > 0 else 0
        })

    def _generate_report(self, stock_data, strategy_params):
        """生成回测报告"""
        # 计算收益率
        total_return = (self.current_capital - self.initial_capital) / self.initial_capital

        # 计算年化收益率
        days = (stock_data.iloc[-1]['date'] - stock_data.iloc[0]['date']).days
        annual_return = (1 + total_return) ** (365 / days) - 1

        # 计算最大回撤
        equity_series = pd.Series([e['capital'] for e in self.equity_curve])
        rolling_max = equity_series.expanding().max()
        drawdown = (equity_series - rolling_max) / rolling_max
        max_drawdown = drawdown.min()

        # 计算夏普比率
        equity_returns = equity_series.pct_change().dropna()
        sharpe_ratio = equity_returns.mean() / equity_returns.std() * np.sqrt(252) if equity_returns.std() > 0 else 0

        # 计算交易统计
        trades_df = pd.DataFrame(self.trades)

        if len(trades_df) == 0:
            # 没有交易
            total_trades = 0
            win_trades = 0
            win_rate = 0
            avg_pnl = 0
            max_win = 0
            max_loss = 0
        else:
            buy_trades = trades_df[trades_df['action'] == '买入']
            sell_trades = trades_df[trades_df['action'] == '卖出']

            total_trades = len(buy_trades)
            win_trades = len(sell_trades[sell_trades['pnl'] > 0]) if len(sell_trades) > 0 else 0
            win_rate = win_trades / total_trades if total_trades > 0 else 0

            avg_pnl = sell_trades['pnl'].mean() if len(sell_trades) > 0 else 0
            max_win = sell_trades['pnl'].max() if len(sell_trades) > 0 else 0
            max_loss = sell_trades['pnl'].min() if len(sell_trades) > 0 else 0

        return {
            'initial_capital': self.initial_capital,
            'final_capital': self.current_capital,
            'total_return': total_return,
            'annual_return': annual_return,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'total_trades': total_trades,
            'win_trades': win_trades,
            'win_rate': win_rate,
            'avg_pnl': avg_pnl,
            'max_win': max_win,
            'max_loss': max_loss,
            'equity_curve': self.equity_curve,
            'trades': self.trades,
            'strategy_params': strategy_params
        }

    def print_report(self, backtest_result):
        """打印回测报告"""
        if backtest_result is None:
            print("❌ 回测结果为空")
            return

        print(f"\n{'='*70}")
        print(f"📊 回测报告")
        print(f"{'='*70}")

        # 资金收益
        print(f"\n💰 资金收益:")
        print(f"   初始资金: ¥{backtest_result['initial_capital']:,.2f}")
        print(f"   最终资金: ¥{backtest_result['final_capital']:,.2f}")
        print(f"   总收益: ¥{backtest_result['final_capital'] - backtest_result['initial_capital']:,.2f}")
        print(f"   总收益率: {backtest_result['total_return']*100:+.2f}%")
        print(f"   年化收益率: {backtest_result['annual_return']*100:+.2f}%")

        # 风险指标
        print(f"\n⚠️ 风险指标:")
        print(f"   最大回撤: {backtest_result['max_drawdown']*100:.2f}%")
        print(f"   夏普比率: {backtest_result['sharpe_ratio']:.2f}")

        # 交易统计
        print(f"\n📈 交易统计:")
        print(f"   总交易次数: {backtest_result['total_trades']} 次")
        print(f"   盈利次数: {backtest_result['win_trades']} 次")
        print(f"   亏损次数: {backtest_result['total_trades'] - backtest_result['win_trades']} 次")
        print(f"   胜率: {backtest_result['win_rate']*100:.1f}%")
        print(f"   平均盈亏: ¥{backtest_result['avg_pnl']:.2f}")
        print(f"   最大盈利: ¥{backtest_result['max_win']:.2f}")
        print(f"   最大亏损: ¥{backtest_result['max_loss']:.2f}")

        # 策略参数
        params = backtest_result.get('strategy_params', {})
        if params:
            print(f"\n⚙️ 策略参数:")
            print(f"   买入阈值: {params['buy_threshold']}")
            print(f"   卖出阈值: {params['sell_threshold']}")
            print(f"   止损: {params['stop_loss']*100:.1f}%")
            print(f"   止盈: {params['take_profit']*100:.1f}%")

        print(f"\n" + "="*70)
        print("✅ 回测报告生成完成")
        print("="*70 + "\n")


if __name__ == "__main__":
    # 测试代码
    print("回测系统 v1.0 测试")

    # 创建模拟数据
    dates = pd.date_range(end=datetime.now(), periods=200, freq='D')
    base_price = 100.0
    prices = []
    for i in range(200):
        if i == 0:
            price = base_price
        else:
            # 添加趋势
            trend = 0.0003 if i < 150 else -0.0002
            price = prices[-1] * (1 + trend + np.random.normal(0, 0.02))
        prices.append(price)

    # 创建 DataFrame
    stock_data = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p * 1.02 for p in prices],
        'low': [p * 0.98 for p in prices],
        'close': prices,
        'volume': [10000000 * (1 + np.random.uniform(-0.3, 0.5)) for _ in range(200)]
    })

    # 创建回测引擎
    backtest = BacktestEngine(initial_capital=100000)

    # 运行回测
    result = backtest.run_backtest(stock_data)

    # 打印报告
    if result:
        backtest.print_report(result)

    print("\n所有测试完成")
