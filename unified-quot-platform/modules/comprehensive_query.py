#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合股票查询 - 实时行情 + Tushare Pro基本面
"""
import os
import sys
sys.path.insert(0, '.')

# 配置环境
os.environ['TUSHARE_TOKEN'] = '8b159caa2bbf554707c20c3f44fea1e0e6ec75b6afc82c78fa47e47b'

from modules.tushare_pro_enhanced import TushareProEnhanced
from modules.realtime_quote import RealtimeQuote
from datetime import datetime


def get_comprehensive_realtime(code: str) -> dict:
    """
    获取综合实时数据

    参数:
        code: 股票代码

    返回:
        dict: 综合数据
    """
    print(f"\n{'='*70}")
    print(f"查询 {code} - 综合实时数据")
    print(f"{'='*70}")

    result = {'code': code, 'query_time': datetime.now().isoformat()}

    # 1. 实时行情
    print("\n【1. 实时行情】")
    realtime = RealtimeQuote()
    quote_data = realtime.query(code)

    if quote_data:
        print(f"✓ 数据源: {quote_data['source']}")
        print(f"✓ 股票: {quote_data['name']}")
        print(f"✓ 当前价格: {quote_data['price']:.2f}")
        print(f"✓ 开盘价: {quote_data['open']:.2f}")
        print(f"✓ 最高价: {quote_data['high']:.2f}")
        print(f"✓ 最低价: {quote_data['low']:.2f}")
        print(f"✓ 成交量: {quote_data['volume']:,.0f} 手")
        print(f"✓ 成交额: {quote_data['amount']:,.0f} 万元")

        if 'change_pct' in quote_data:
            print(f"✓ 涨跌幅: {quote_data['change_pct']:+.2f}%")
            change_pct = quote_data['change_pct']
        else:
            # 如果没有涨跌幅，计算
            if quote_data.get('close_prev', 0) > 0:
                change_pct = ((quote_data['price'] - quote_data['close_prev']) / quote_data['close_prev']) * 100
                print(f"✓ 涨跌幅: {change_pct:+.2f}%")
            else:
                change_pct = 0

        result['realtime'] = {
            'name': quote_data['name'],
            'price': quote_data['price'],
            'open': quote_data['open'],
            'high': quote_data['high'],
            'low': quote_data['low'],
            'volume': quote_data['volume'],
            'amount': quote_data['amount'],
            'change_pct': change_pct,
            'source': quote_data['source'],
            'update_time': quote_data['query_time']
        }
    else:
        print("✗ 实时行情查询失败")
        result['realtime'] = None

    # 2. 基本信息
    print("\n【2. 基本信息】")
    tushare = TushareProEnhanced()
    basic = tushare.get_stock_basic(code)

    if basic:
        print(f"✓ 股票名称: {basic['name']}")
        print(f"✓ 所属行业: {basic['industry']}")
        print(f"✓ 所在市场: {basic['market']}")
        print(f"✓ 上市日期: {basic['list_date']}")
        print(f"✓ 所在地区: {basic['area']}")

        result['basic'] = basic
    else:
        print("✗ 基本信息查询失败")
        result['basic'] = None

    # 3. 估值指标
    print("\n【3. 估值指标】")
    df_basic = tushare.get_daily_basic(code, limit=1)

    if df_basic is not None and not df_basic.empty:
        latest = df_basic.iloc[0]
        print(f"✓ 市盈率(PE): {latest.get('pe', 'N/A')}")
        print(f"✓ 市盈率(TTM): {latest.get('pe_ttm', 'N/A')}")
        print(f"✓ 市净率(PB): {latest.get('pb', 'N/A')}")
        print(f"✓ 市销率(PS): {latest.get('ps', 'N/A')}")
        print(f"✓ 换手率: {latest.get('turnover_rate', 'N/A')}%")
        print(f"✓ 总股本: {latest.get('total_share', 'N/A'):,.0f} 万股")
        print(f"✓ 流通股本: {latest.get('float_share', 'N/A'):,.0f} 万股")

        result['valuation'] = {
            'pe': float(latest.get('pe', 0)) if latest.get('pe') else None,
            'pe_ttm': float(latest.get('pe_ttm', 0)) if latest.get('pe_ttm') else None,
            'pb': float(latest.get('pb', 0)) if latest.get('pb') else None,
            'ps': float(latest.get('ps', 0)) if latest.get('ps') else None,
            'turnover_rate': float(latest.get('turnover_rate', 0)) if latest.get('turnover_rate') else None,
            'total_share': float(latest.get('total_share', 0)) if latest.get('total_share') else None,
            'float_share': float(latest.get('float_share', 0)) if latest.get('float_share') else None,
        }
    else:
        print("✗ 估值指标查询失败")
        result['valuation'] = None

    # 4. 财务指标
    print("\n【4. 财务指标】")
    financial = tushare.get_financial_indicators(code)

    if financial:
        print(f"✓ ROE: {financial['roe']:.2f}%")
        print(f"✓ ROA: {financial['roa']:.2f}%")
        print(f"✓ 毛利率: {financial['gross_profit_margin']:.2f}%")
        print(f"✓ 资产负债率: {financial['debt_to_assets']:.2f}%")
        print(f"✓ 流动比率: {financial['current_ratio']:.2f}")
        print(f"✓ 速动比率: {financial['quick_ratio']:.2f}")
        print(f"✓ 每股收益(EPS): {financial['eps']:.2f}")
        print(f"✓ 每股净资产(BPS): {financial['bps']:.2f}")
        print(f"✓ 报告期: {financial['end_date']}")

        result['financial'] = financial
    else:
        print("✗ 财务指标查询失败")
        result['financial'] = None

    # 5. 综合摘要
    print(f"\n{'='*70}")
    print("【综合摘要】")

    if result['realtime'] and result['basic']:
        rt = result['realtime']
        bs = result['basic']

        print(f"\n股票: {rt['name']} ({bs['industry']})")
        print(f"当前价格: {rt['price']:.2f} 元 ({rt['change_pct']:+.2f}%)")
        print(f"成交量: {rt['volume']:,.0f} 手")

        if result['valuation']:
            val = result['valuation']
            if val.get('pe'):
                print(f"市盈率: {val['pe']:.2f}")
            if val.get('pb'):
                print(f"市净率: {val['pb']:.2f}")

        if result['financial']:
            fin = result['financial']
            print(f"ROE: {fin['roe']:.2f}%")
            print(f"资产负债率: {fin['debt_to_assets']:.2f}%")

        print(f"\n实时行情更新时间: {rt['update_time']}")
        print(f"综合查询完成时间: {result['query_time']}")

    print(f"\n{'='*70}")

    return result


if __name__ == '__main__':
    # 查询中国核建
    code = '601611'
    result = get_comprehensive_realtime(code)
