#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tushare Pro增强数据源 - 扩展数据接口
支持日线行情、财务数据、历史数据、技术指标等
"""
import os
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List

# 配置Tushare Token
os.environ['TUSHARE_TOKEN'] = '8b159caa2bbf554707c20c3f44fea1e0e6ec75b6afc82c78fa47e47b'

import tushare as ts

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TushareProEnhanced:
    """Tushare Pro增强数据源"""

    def __init__(self):
        """初始化"""
        self.token = os.getenv('TUSHARE_TOKEN')
        self.pro = ts.pro_api(self.token)
        logger.info(f"[TushareProEnhanced] 已初始化，Token: {self.token[:10]}...")

    def convert_code(self, code: str) -> str:
        """
        转换代码格式为Tushare格式

        参数:
            code: 6位股票代码（如 '000001'）

        返回:
            str: Tushare格式代码（如 '000001.SZ'）
        """
        if code.startswith('6'):
            return f"{code}.SH"
        else:
            return f"{code}.SZ"

    def revert_code(self, ts_code: str) -> str:
        """
        从Tushare格式转换为6位代码

        参数:
            ts_code: Tushare格式代码（如 '000001.SZ'）

        返回:
            str: 6位股票代码（如 '000001'）
        """
        return ts_code.split('.')[0]

    def get_stock_basic(self, code: str) -> Optional[Dict]:
        """
        获取股票基本信息

        参数:
            code: 股票代码

        返回:
            dict: 股票基本信息
        """
        try:
            ts_code = self.convert_code(code)
            df = self.pro.stock_basic(ts_code=ts_code)

            if df.empty:
                return None

            basic = df.iloc[0]
            return {
                'code': code,
                'ts_code': basic['ts_code'],
                'name': basic['name'],
                'area': basic['area'],
                'industry': basic['industry'],
                'market': basic['market'],
                'list_date': basic['list_date']
            }

        except Exception as e:
            logger.error(f"[TushareProEnhanced] 获取基本信息失败 {code}: {e}")
            return None

    def get_daily_quotes(self, code: str, start_date: str = None, end_date: str = None, limit: int = 100) -> Optional[pd.DataFrame]:
        """
        获取日线行情

        参数:
            code: 股票代码
            start_date: 开始日期（YYYYMMDD）
            end_date: 结束日期（YYYYMMDD）
            limit: 返回条数

        返回:
            DataFrame: 日线行情数据
        """
        try:
            ts_code = self.convert_code(code)

            # 默认查询最近100天
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')

            df = self.pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)

            if not df.empty:
                # 按日期排序，取最近的limit条
                df = df.sort_values('trade_date', ascending=False).head(limit)

            return df

        except Exception as e:
            logger.error(f"[TushareProEnhanced] 获取日线行情失败 {code}: {e}")
            return None

    def get_latest_quote(self, code: str) -> Optional[Dict]:
        """
        获取最新行情

        参数:
            code: 股票代码

        返回:
            dict: 最新行情
        """
        try:
            df = self.get_daily_quotes(code, limit=1)

            if df is None or df.empty:
                return None

            latest = df.iloc[0]
            return {
                'code': code,
                'trade_date': latest['trade_date'],
                'open': float(latest['open']),
                'high': float(latest['high']),
                'low': float(latest['low']),
                'close': float(latest['close']),
                'volume': float(latest['vol']),
                'amount': float(latest['amount']),
                'pct_chg': float(latest['pct_chg']),
                'change': float(latest['change'])
            }

        except Exception as e:
            logger.error(f"[TushareProEnhanced] 获取最新行情失败 {code}: {e}")
            return None

    def get_daily_basic(self, code: str, start_date: str = None, end_date: str = None, limit: int = 100) -> Optional[pd.DataFrame]:
        """
        获取每日基本面指标（市盈率、市净率等）

        参数:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            limit: 返回条数

        返回:
            DataFrame: 每日基本面指标
        """
        try:
            ts_code = self.convert_code(code)

            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')

            df = self.pro.daily_basic(ts_code=ts_code, start_date=start_date, end_date=end_date)

            if not df.empty:
                df = df.sort_values('trade_date', ascending=False).head(limit)

            return df

        except Exception as e:
            logger.error(f"[TushareProEnhanced] 获取每日指标失败 {code}: {e}")
            return None

    def get_financial_indicators(self, code: str) -> Optional[Dict]:
        """
        获取最新财务指标

        参数:
            code: 股票代码

        返回:
            dict: 财务指标
        """
        try:
            ts_code = self.convert_code(code)

            # 获取财务指标
            df = self.pro.fina_indicator(ts_code=ts_code)

            if df.empty:
                return None

            # 获取最新的指标
            latest = df.iloc[0]

            return {
                'code': code,
                'end_date': latest['end_date'],
                'roe': float(latest.get('roe', 0)) if pd.notna(latest.get('roe')) else 0,
                'roa': float(latest.get('roa', 0)) if pd.notna(latest.get('roa')) else 0,
                'gross_profit_margin': float(latest.get('gross_profit_margin', 0)) if pd.notna(latest.get('gross_profit_margin')) else 0,
                'debt_to_assets': float(latest.get('debt_to_assets', 0)) if pd.notna(latest.get('debt_to_assets')) else 0,
                'current_ratio': float(latest.get('current_ratio', 0)) if pd.notna(latest.get('current_ratio')) else 0,
                'quick_ratio': float(latest.get('quick_ratio', 0)) if pd.notna(latest.get('quick_ratio')) else 0,
                'eps': float(latest.get('eps', 0)) if pd.notna(latest.get('eps')) else 0,
                'bps': float(latest.get('bps', 0)) if pd.notna(latest.get('bps')) else 0,
            }

        except Exception as e:
            logger.error(f"[TushareProEnhanced] 获取财务指标失败 {code}: {e}")
            return None

    def get_income_statement(self, code: str, period: str = 'latest') -> Optional[pd.DataFrame]:
        """
        获取利润表

        参数:
            code: 股票代码
            period: 期间（latest/2023/2022）

        返回:
            DataFrame: 利润表
        """
        try:
            ts_code = self.convert_code(code)

            df = self.pro.income(ts_code=ts_code, period=period)

            if not df.empty:
                df = df.sort_values('end_date', ascending=False)

            return df

        except Exception as e:
            logger.error(f"[TushareProEnhanced] 获取利润表失败 {code}: {e}")
            return None

    def get_balance_sheet(self, code: str, period: str = 'latest') -> Optional[pd.DataFrame]:
        """
        获取资产负债表

        参数:
            code: 股票代码
            period: 期间

        返回:
            DataFrame: 资产负债表
        """
        try:
            ts_code = self.convert_code(code)

            df = self.pro.balancesheet(ts_code=ts_code, period=period)

            if not df.empty:
                df = df.sort_values('end_date', ascending=False)

            return df

        except Exception as e:
            logger.error(f"[TushareProEnhanced] 获取资产负债表失败 {code}: {e}")
            return None

    def get_cashflow(self, code: str, period: str = 'latest') -> Optional[pd.DataFrame]:
        """
        获取现金流量表

        参数:
            code: 股票代码
            period: 期间

        返回:
            DataFrame: 现金流量表
        """
        try:
            ts_code = self.convert_code(code)

            df = self.pro.cashflow(ts_code=ts_code, period=period)

            if not df.empty:
                df = df.sort_values('end_date', ascending=False)

            return df

        except Exception as e:
            logger.error(f"[TushareProEnhanced] 获取现金流量表失败 {code}: {e}")
            return None

    def get_comprehensive_data(self, code: str) -> Optional[Dict]:
        """
        获取综合数据（基本信息 + 最新行情 + 财务指标）

        参数:
            code: 股票代码

        返回:
            dict: 综合数据
        """
        try:
            # 基本信息
            basic = self.get_stock_basic(code)
            if not basic:
                return None

            # 最新行情
            quote = self.get_latest_quote(code)

            # 财务指标
            financial = self.get_financial_indicators(code)

            # 每日指标
            df_basic = self.get_daily_basic(code, limit=1)
            daily_basic = None
            if df_basic is not None and not df_basic.empty:
                latest = df_basic.iloc[0]
                daily_basic = {
                    'pe': float(latest.get('pe', 0)) if pd.notna(latest.get('pe')) else 0,
                    'pe_ttm': float(latest.get('pe_ttm', 0)) if pd.notna(latest.get('pe_ttm')) else 0,
                    'pb': float(latest.get('pb', 0)) if pd.notna(latest.get('pb')) else 0,
                    'ps': float(latest.get('ps', 0)) if pd.notna(latest.get('ps')) else 0,
                    'ps_ttm': float(latest.get('ps_ttm', 0)) if pd.notna(latest.get('ps_ttm')) else 0,
                    'dv_ratio': float(latest.get('dv_ratio', 0)) if pd.notna(latest.get('dv_ratio')) else 0,
                    'dv_ttm': float(latest.get('dv_ttm', 0)) if pd.notna(latest.get('dv_ttm')) else 0,
                    'total_share': float(latest.get('total_share', 0)) if pd.notna(latest.get('total_share')) else 0,
                    'float_share': float(latest.get('float_share', 0)) if pd.notna(latest.get('float_share')) else 0,
                    'free_share': float(latest.get('free_share', 0)) if pd.notna(latest.get('free_share')) else 0,
                    'turnover_rate': float(latest.get('turnover_rate', 0)) if pd.notna(latest.get('turnover_rate')) else 0,
                }

            result = {
                'code': code,
                'name': basic['name'],
                'industry': basic['industry'],
                'market': basic['market'],
                'list_date': basic['list_date'],
                'quote': quote,
                'financial': financial,
                'daily_basic': daily_basic,
                'data_time': datetime.now().isoformat()
            }

            return result

        except Exception as e:
            logger.error(f"[TushareProEnhanced] 获取综合数据失败 {code}: {e}")
            return None


def test_tushare_pro_enhanced():
    """测试Tushare Pro增强数据源"""
    print("=" * 70)
    print("Tushare Pro增强数据源测试")
    print("=" * 70)

    tushare = TushareProEnhanced()

    # 测试股票
    test_code = '000001'

    print(f"\n=== 测试股票: {test_code} ===")

    # 测试1: 基本信息
    print("\n1. 基本信息")
    basic = tushare.get_stock_basic(test_code)
    if basic:
        print(f"✓ 名称: {basic['name']}")
        print(f"✓ 行业: {basic['industry']}")
        print(f"✓ 市场: {basic['market']}")
        print(f"✓ 上市日期: {basic['list_date']}")

    # 测试2: 最新行情
    print("\n2. 最新行情")
    quote = tushare.get_latest_quote(test_code)
    if quote:
        print(f"✓ 日期: {quote['trade_date']}")
        print(f"✓ 收盘: {quote['close']:.2f}")
        print(f"✓ 涨跌幅: {quote['pct_chg']:.2f}%")
        print(f"✓ 成交量: {quote['volume']:.0f}")
        print(f"✓ 成交额: {quote['amount']:.0f}")

    # 测试3: 每日指标
    print("\n3. 每日指标")
    df_basic = tushare.get_daily_basic(test_code, limit=1)
    if df_basic is not None and not df_basic.empty:
        latest = df_basic.iloc[0]
        print(f"✓ 市盈率: {latest.get('pe', 'N/A')}")
        print(f"✓ 市净率: {latest.get('pb', 'N/A')}")
        print(f"✓ 换手率: {latest.get('turnover_rate', 'N/A')}%")

    # 测试4: 财务指标
    print("\n4. 财务指标")
    financial = tushare.get_financial_indicators(test_code)
    if financial:
        print(f"✓ ROE: {financial['roe']:.2f}%")
        print(f"✓ ROA: {financial['roa']:.2f}%")
        print(f"✓ 毛利率: {financial['gross_profit_margin']:.2f}%")
        print(f"✓ 资产负债率: {financial['debt_to_assets']:.2f}%")

    # 测试5: 综合数据
    print("\n5. 综合数据")
    comprehensive = tushare.get_comprehensive_data(test_code)
    if comprehensive:
        print(f"✓ 股票: {comprehensive['name']} ({comprehensive['industry']})")
        if comprehensive['quote']:
            print(f"✓ 价格: {comprehensive['quote']['close']:.2f}")
        if comprehensive['daily_basic']:
            print(f"✓ 市盈率: {comprehensive['daily_basic']['pe']:.2f}")
        if comprehensive['financial']:
            print(f"✓ ROE: {comprehensive['financial']['roe']:.2f}%")

    print("\n" + "=" * 70)


if __name__ == '__main__':
    test_tushare_pro_enhanced()
