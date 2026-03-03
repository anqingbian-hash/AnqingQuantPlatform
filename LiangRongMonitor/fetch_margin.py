#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
两融数据采集 - 卞董专用版本
使用真实Tushare Token
"""
import akshare as ak
import tushare as ts
import pandas as pd
from datetime import datetime

# 卞董的Tushare Token
TS_TOKEN = '8b159caa2bbf554707c20c3f44fea1e0e6ec75b6afc82c78fa47e47b'

# 设置Token
ts.set_token(TS_TOKEN)
pro = ts.pro_api()

def fetch_margin_data(date=None, symbol=None):
    """获取两融数据
    
    参数:
        date: 日期（YYYYMMDD格式），默认为今天
        symbol: 股票代码，如'000001.SZ'
        
    返回:
        (data, source) - 数据DataFrame和数据源名称
    """
    if date is None:
        date = datetime.now().strftime('%Y%m%d')
    
    data = None
    source = None
    
    print(f"获取两融数据 - 日期: {date}, 股票: {symbol}")
    print("="*60)
    
    # 尝试Tushare Pro
    try:
        print("[1/2] 尝试Tushare Pro...")
        
        if symbol:
            df = pro.margin_detail(trade_date=date, ts_code=symbol)
        else:
            df = pro.margin(trade_date=date)
        
        if not df.empty:
            data = df
            source = 'Tushare'
            print(f"✓ Tushare Pro成功 - 获取到 {len(df)} 条记录")
            return data, source
        else:
            print("✗ Tushare Pro返回空数据")
            
    except Exception as e:
        print(f"✗ Tushare Pro失败: {e}")
    
    # Fallback到AKShare
    try:
        print("\n[2/2] 尝试AKShare备用...")
        
        if symbol:
            # AKShare 个股数据
            if 'SZ' in symbol:
                df = ak.stock_margin_detail_szse(date=date)
            else:
                df = ak.stock_margin_detail_sse(date=date)
            data = df[df['标的证券代码'] == symbol.split('.')[0]]
        else:
            # AKShare 市场汇总
            df_sse = ak.stock_margin_sse(date=date)
            df_szse = ak.stock_margin_szse(date=date)
            data = pd.concat([df_sse, df_szse])
        
        if data is not None and not data.empty:
            source = 'AKShare'
            print(f"✓ AKShare成功 - 获取到 {len(data)} 条记录")
            return data, source
        else:
            print("✗ AKShare返回空数据")
            
    except Exception as e:
        print(f"✗ AKShare失败: {e}")
    
    print("\n" + "="*60)
    print("数据获取失败")
    return data, source

# ========================================
# 测试代码
# ========================================
if __name__ == '__main__':
    print("="*60)
    print("两融数据采集 - 卞董专用版本")
    print("="*60)
    print(f"Tushare Token: {TS_TOKEN}")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    print()
    
    # 测试1: 获取今天市场汇总数据
    print("【测试1】获取今天市场汇总数据")
    print()
    df_market, source_market = fetch_margin_data()
    
    if df_market is not None and not df_market.empty:
        print(f"\n✓ 市场数据获取成功 (来源: {source_market})")
        print(f"数据维度: {df_market.shape}")
        print("\n最新融资余额信息:")
        
        # 查看最新记录
        latest = df_market.iloc[0]
        print(f"  日期: {latest.get('trade_date', 'N/A')}")
        print(f"  融资余额(rzye): {latest.get('rzye', 'N/A')}")
        print(f"  融券余额(rqye): {latest.get('rqye', 'N/A')}")
        print(f"  融资买入额(rzmre): {latest.get('rzmre', 'N/A')}")
        print(f"  融券卖出额(rqyl): {latest.get('rqyl', 'N/A')}")
        
        # 计算总额（如果有多个交易所）
        if 'exchange_id' in df_market.columns:
            print(f"\n各交易所汇总:")
            for exchange, group in df_market.groupby('exchange_id'):
                total_rzye = group['rzye'].sum()
                print(f"  {exchange}: {total_rzye/1e8:.2f} 亿元")
    else:
        print("\n✗ 市场数据获取失败")
    
    print()
    print("-"*60)
    print()
    
    # 测试2: 获取特定股票数据（可选）
    print("【测试2】获取宁德时代(300750.SZ)数据")
    print()
    df_stock, source_stock = fetch_margin_data(symbol='300750.SZ')
    
    if df_stock is not None and not df_stock.empty:
        print(f"\n✓ 个股数据获取成功 (来源: {source_stock})")
        print(f"数据维度: {df_stock.shape}")
        
        latest_stock = df_stock.iloc[0]
        print(f"\n宁德时代两融数据:")
        print(f"  日期: {latest_stock.get('trade_date', latest_stock.get('日期', 'N/A'))}")
        print(f"  融资余额: {latest_stock.get('rzye', latest_stock.get('融资余额', 'N/A'))}")
        print(f"  融券余额: {latest_stock.get('rqye', latest_stock.get('融券余额', 'N/A'))}")
    else:
        print("\n✗ 个股数据获取失败")
    
    print()
    print("="*60)
    print("测试完成")
    print("="*60)
