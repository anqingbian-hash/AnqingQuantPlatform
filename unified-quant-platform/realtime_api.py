#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时数据API - 使用真实数据源
"""

import pandas as pd
import numpy as np
import akshare as ak
import efinance as ef
from datetime import datetime
import time

def get_realtime_data(stock_code):
    """
    获取实时股票数据（使用AKShare + Efinance双数据源）

    Args:
        stock_code: 股票代码（如 600519 或 000001）

    Returns:
        dict: 实时数据
    """
    # 格式化股票代码
    code = format_stock_code(stock_code)

    try:
        # 尝试使用 AKShare 获取实时数据
        data = get_akshare_realtime(code)
        if data:
            return {
                'success': True,
                'message': '实时数据获取成功（AKShare）',
                'source': 'akshare',
                'data': data,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

        # 如果 AKShare 失败，尝试 Efinance
        data = get_efinance_realtime(code)
        if data:
            return {
                'success': True,
                'message': '实时数据获取成功（Efinance）',
                'source': 'efinance',
                'data': data,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

        return {
            'success': False,
            'message': '无法获取实时数据',
            'data': None
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'获取数据失败: {str(e)}',
            'data': None
        }

def format_stock_code(code):
    """
    格式化股票代码（确保符合数据源要求）

    Args:
        code: 股票代码

    Returns:
        str: 格式化后的代码
    """
    code = str(code).strip()

    # 去除前缀
    code = code.replace('sh', '').replace('sz', '').replace('.SH', '').replace('.SZ', '')

    # 添加前缀
    if len(code) == 6:
        if code.startswith('6'):
            return f'sh{code}'
        else:
            return f'sz{code}'

    return code

def get_akshare_realtime(code):
    """
    使用 AKShare 获取实时数据

    Args:
        code: 股票代码（格式：sh600519）

    Returns:
        dict: 实时数据
    """
    try:
        # 获取实时数据
        df = ak.stock_zh_a_spot_em()

        # 查找对应股票
        code_clean = code.replace('sh', '').replace('sz', '')
        stock = df[df['代码'] == code_clean]

        if stock.empty:
            return None

        stock = stock.iloc[0]

        return {
            'symbol': stock['代码'],
            'name': stock['名称'],
            'price': float(stock['最新价']),
            'change': float(stock['涨跌额']),
            'change_percent': f"{float(stock['涨跌幅']):.2f}%",
            'volume': int(stock['成交量']),
            'amount': float(stock['成交额']),
            'high': float(stock['最高']),
            'low': float(stock['最低']),
            'open': float(stock['今开']),
            'pre_close': float(stock['昨收'])
        }

    except Exception as e:
        print(f"⚠️ AKShare 获取失败: {e}")
        return None

def get_efinance_realtime(code):
    """
    使用 Efinance 获取实时数据

    Args:
        code: 股票代码（格式：600519）

    Returns:
        dict: 实时数据
    """
    try:
        # 获取实时数据
        code_clean = code.replace('sh', '').replace('sz', '')
        df = ef.stock.get_realtime_quotes(code_clean)

        if df is None or df.empty:
            return None

        stock = df.iloc[0]

        return {
            'symbol': stock['股票代码'],
            'name': stock['股票名称'],
            'price': float(stock['最新价']),
            'change': float(stock['涨跌额']),
            'change_percent': f"{float(stock['涨跌幅']):.2f}%",
            'volume': int(stock['成交量']),
            'amount': float(stock['成交额']),
            'high': float(stock['最高']),
            'low': float(stock['最低']),
            'open': float(stock['今开']),
            'pre_close': float(stock['昨收'])
        }

    except Exception as e:
        print(f"⚠️ Efinance 获取失败: {e}")
        return None

def get_stock_history(stock_code, period='daily', days=30):
    """
    获取历史K线数据

    Args:
        stock_code: 股票代码
        period: 周期（daily/weekly/monthly）
        days: 天数

    Returns:
        pd.DataFrame: K线数据
    """
    try:
        code = format_stock_code(stock_code)
        code_clean = code.replace('sh', '').replace('sz', '')

        # 使用 AKShare 获取历史数据
        if period == 'daily':
            df = ak.stock_zh_a_hist(symbol=code_clean, period="daily", adjust="qfq")
        elif period == 'weekly':
            df = ak.stock_zh_a_hist(symbol=code_clean, period="weekly", adjust="qfq")
        else:
            df = ak.stock_zh_a_hist(symbol=code_clean, period="monthly", adjust="qfq")

        if df.empty:
            return None

        # 重命名列
        df = df.rename(columns={
            '日期': 'date',
            '开盘': 'open',
            '收盘': 'close',
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume',
            '成交额': 'amount'
        })

        # 按日期排序，取最近N天
        df = df.sort_values('date').tail(days)

        return df

    except Exception as e:
        print(f"⚠️ 获取历史数据失败: {e}")
        return None

def calculate_technical_indicators(df):
    """
    计算技术指标

    Args:
        df: K线数据

    Returns:
        dict: 技术指标
    """
    if df is None or len(df) < 20:
        return None

    try:
        close = df['close'].values

        # MA5, MA10, MA20
        ma5 = np.mean(close[-5:])
        ma10 = np.mean(close[-10:])
        ma20 = np.mean(close[-20:])

        # RSI (14)
        rsi = calculate_rsi(close, 14)

        # MACD
        macd_data = calculate_macd(close)
        macd = macd_data['macd'][-1] if macd_data else 0

        return {
            'ma5': float(ma5),
            'ma10': float(ma10),
            'ma20': float(ma20),
            'rsi': float(rsi),
            'macd': float(macd)
        }

    except Exception as e:
        print(f"⚠️ 计算技术指标失败: {e}")
        return None

def calculate_rsi(close, period=14):
    """计算RSI指标"""
    if len(close) < period + 1:
        return 50.0

    delta = np.diff(close)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = np.mean(gain[-period:])
    avg_loss = np.mean(loss[-period:])

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

def calculate_macd(close, fast=12, slow=26, signal=9):
    """计算MACD指标"""
    if len(close) < slow + signal:
        return None

    ema_fast = pd.Series(close).ewm(span=fast).mean()
    ema_slow = pd.Series(close).ewm(span=slow).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal).mean()
    histogram = macd_line - signal_line

    return {
        'macd': float(macd_line.iloc[-1]),
        'signal': float(signal_line.iloc[-1]),
        'histogram': float(histogram.iloc[-1])
    }

# 测试
if __name__ == '__main__':
    print("🧪 测试实时数据API")

    # 测试贵州茅台
    data = get_realtime_data('600519')
    print(f"\n贵州茅台: {data}")

    # 测试浦发银行
    data = get_realtime_data('600000')
    print(f"\n浦发银行: {data}")
