#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
两融数据采集 - 卞董专用版本（修复版）
使用真实Tushare Token
"""
import akshare as ak
import tushare as ts
import pandas as pd
from datetime import datetime, timedelta

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
        
        if df is not None and not df.empty:
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
            stock_code = symbol.split('.')[0]
            df = ak.stock_margin_detail_sse(date=date)  # 统一接口
            data = df[df['标的证券代码'] == stock_code]
        else:
            # AKShare 市场汇总
            df = ak.stock_margin_sse(date=date)
            data = df
        
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
    
    # 尝试获取最近的数据（前5天）
    print("尝试获取最近5天的数据...")
    print()
    
    for i in range(5):
        test_date = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
        print(f"\n【尝试 {i+1}/5】日期: {test_date}")
        print()
        
        df_market, source_market = fetch_margin_data(date=test_date)
        
        if df_market is not None and not df_market.empty:
            print(f"\n✓ 数据获取成功! (来源: {source_market})")
            print(f"数据维度: {df_market.shape}")
            print(f"数据列: {list(df_market.columns)}")
            print("\n最新融资余额信息:")
            
            # 查看前几条记录
            for idx, row in df_market.head(3).iterrows():
                print(f"\n记录 {idx}:")
                for col in df_market.columns:
                    val = row[col]
                    if pd.notna(val):
                        # 如果是数字，格式化显示
                        if isinstance(val, (int, float)) and val > 1e6:
                            print(f"  {col}: {val/1e8:.2f} 亿元")
                        else:
                            print(f"  {col}: {val}")
            
            # 计算总额（如果有多个交易所）
            if 'exchange_id' in df_market.columns:
                print(f"\n各交易所汇总:")
                for exchange, group in df_market.groupby('exchange_id'):
                    if 'rzye' in group.columns:
                        total_rzye = group['rzye'].sum()
                        print(f"  {exchange}: {total_rzye/1e8:.2f} 亿元")
            elif 'rzye' in df_market.columns:
                total_rzye = df_market['rzye'].sum()
                print(f"\n市场总额: {total_rzye/1e8:.2f} 亿元")
            
            print("\n" + "="*60)
            print("测试成功!")
            print("="*60)
            
            # 保存数据
            import os
            os.makedirs('data', exist_ok=True)
            df_market.to_csv(f'data/margin_{test_date}.csv', index=False, encoding='utf-8-sig')
            print(f"\n数据已保存到: data/margin_{test_date}.csv")
            
            break
        else:
            print(f"\n✗ {test_date} 数据获取失败，尝试下一天...")
    
    print()
    print("="*60)
    print("测试完成")
    print("="*60)
