#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
两融数据分析 - 卞董专用版本
处理DataFetcher拉取的数据，生成警报
"""
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def analyze_margin_changes(df, history_days=30):
    """分析两融变化，生成警报
    
    参数:
        df: 两融数据DataFrame（来自DataFetcher）
        history_days: 历史数据天数，用于回归分析
        
    返回:
        (df_with_analysis, alerts) - 包含分析的数据框和警报列表
    """
    
    # 按日期排序
    df = df.sort_values('trade_date')
    
    # 计算变化率
    df['融资余额变化率'] = df['rzye'].pct_change() * 100
    df['融券余额变化率'] = df['rqye'].pct_change() * 100
    
    # 计算MA5
    df['融资余额_MA5'] = df['rzye'].rolling(5).mean()
    df['融券余额_MA5'] = df['rqye'].rolling(5).mean()
    
    # 计算MA10
    df['融资余额_MA10'] = df['rzye'].rolling(10).mean()
    df['融券余额_MA10'] = df['rqye'].rolling(10).mean()
    
    # 生成警报
    alerts = []
    
    # 获取最新数据
    latest = df.iloc[-1]
    
    print("="*80)
    print("两融数据分析报告")
    print("="*80)
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"数据天数: {len(df)} 天")
    print(f"使用历史: {history_days} 天")
    print("="*80)
    
    # 1. 融资余额变化率检查
    latest_rzye_change = latest['融资余额变化率']
    if pd.notna(latest_rzye_change):
        print(f"\n【1】融资余额变化率: {latest_rzye_change:.2f}%")
        
        if latest_rzye_change > 5:
            alert = f"⚠️ 融资激增 {latest_rzye_change:.2f}%：可能短期拉升，但杠杆风险放大"
            alerts.append(alert)
            print(f"   → {alert}")
        elif latest_rzye_change < -5:
            alert = f"⚠️ 融资骤降 {latest_rzye_change:.2f}%：市场情绪降温，可能回调"
            alerts.append(alert)
            print(f"   → {alert}")
        else:
            print(f"   ✓ 变化率正常")
    
    # 2. 融券余额变化率检查
    latest_rqye_change = latest['融券余额变化率']
    if pd.notna(latest_rqye_change):
        print(f"\n【2】融券余额变化率: {latest_rqye_change:.2f}%")
        
        if latest_rqye_change > 10:
            alert = f"⚠️ 融券上升 {latest_rqye_change:.2f}%：潜在高估/做空信号"
            alerts.append(alert)
            print(f"   → {alert}")
        elif latest_rqye_change < -10:
            alert = f"⚠️ 融券骤降 {latest_rqye_change:.2f}%：做空平仓，可能反弹"
            alerts.append(alert)
            print(f"   → {alert}")
        else:
            print(f"   ✓ 变化率正常")
    
    # 3. MA金叉/死叉检查
    if pd.notna(latest['融资余额_MA5']) and pd.notna(latest['融资余额_MA10']):
        print(f"\n【3】均线系统")
        print(f"   MA5: {latest['融资余额_MA5']/1e8:.2f} 亿元")
        print(f"   MA10: {latest['融资余额_MA10']/1e8:.2f} 亿元")
        
        if latest['融资余额_MA5'] > latest['融资余额_MA10']:
            print(f"   ✓ MA5 > MA10（金叉），趋势向上")
            # 检查前一日是否死叉
            if len(df) > 1:
                prev = df.iloc[-2]
                if pd.notna(prev['融资余额_MA5']) and pd.notna(prev['融资余额_MA10']):
                    if prev['融资余额_MA5'] <= prev['融资余额_MA10']:
                        alert = "📈 MA金叉出现，趋势向上确认"
                        alerts.append(alert)
                        print(f"   → {alert}")
        else:
            print(f"   ✓ MA5 < MA10（死叉），趋势向下")
            # 检查前一日是否金叉
            if len(df) > 1:
                prev = df.iloc[-2]
                if pd.notna(prev['融资余额_MA5']) and pd.notna(prev['融资余额_MA10']):
                    if prev['融资余额_MA5'] >= prev['融资余额_MA10']:
                        alert = "📉 MA死叉出现，趋势向下确认"
                        alerts.append(alert)
                        print(f"   → {alert}")
    
    # 4. 线性回归预测下一日
    print(f"\n【4】趋势预测（线性回归）")
    
    # 准备数据（使用最近history_days天）
    if len(df) >= history_days:
        X = np.array(range(history_days)).reshape(-1, 1)
        y = df['rzye'].values[-history_days:]
        
        # 标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # 线性回归
        model = LinearRegression()
        model.fit(X_scaled, y)
        
        # 预测下一日
        next_day_scaled = scaler.transform([[history_days]])
        pred = model.predict(next_day_scaled)[0]
        
        # 计算预测变化率
        pred_change = (pred - y[-1]) / y[-1] * 100
        
        # 计算预测置信度（R²）
        score = model.score(X_scaled, y)
        
        print(f"   当前融资余额: {y[-1]/1e8:.2f} 亿元")
        print(f"   预测融资余额: {pred/1e8:.2f} 亿元")
        print(f"   预测变化率: {pred_change:.2f}%")
        print(f"   预测置信度: {score:.2%}")
        
        if abs(pred_change) > 2:
            direction = "上涨" if pred_change > 0 else "下跌"
            alert = f"📊 预判下一交易日融资余额{direction}约 {abs(pred_change):.2f}%（置信度: {score:.1%}）"
            alerts.append(alert)
            print(f"   → {alert}")
        else:
            print(f"   ✓ 预测变化率平稳（<2%）")
    else:
        print(f"   ⚠️ 数据不足（需要至少{history_days}天），无法预测")
    
    # 5. 融资融券比检查
    if pd.notna(latest['rqye']) and latest['rqye'] > 0:
        margin_ratio = latest['rzye'] / latest['rqye']
        print(f"\n【5】融资融券比: {margin_ratio:.2f}")
        
        if margin_ratio < 5:
            alert = f"⚠️ 融资融券比过低（{margin_ratio:.2f}），做空压力大"
            alerts.append(alert)
            print(f"   → {alert}")
        else:
            print(f"   ✓ 融资融券比正常")
    
    # 6. 极值检查
    print(f"\n【6】极值检查")
    
    # 检查是否创历史新高
    if latest['rzye'] == df['rzye'].max():
        alert = "📈 融资余额创历史新高，市场情绪高涨"
        alerts.append(alert)
        print(f"   → {alert}")
    elif latest['rzye'] == df['rzye'].min():
        alert = "📉 融资余额创历史新低，市场情绪低迷"
        alerts.append(alert)
        print(f"   → {alert}")
    else:
        print(f"   ✓ 未出现极值")
    
    print("\n" + "="*80)
    print(f"分析完成，共生成 {len(alerts)} 条警报")
    if alerts:
        print("\n警报列表:")
        for i, alert in enumerate(alerts, 1):
            print(f"{i}. {alert}")
    else:
        print("\n✓ 无警报，市场状态正常")
    print("="*80)
    
    return df, alerts

# ========================================
# 测试代码
# ========================================
if __name__ == '__main__':
    # 导入数据获取函数
    import sys
    sys.path.append('/root/.openclaw/workspace/LiangRongMonitor')
    from fetch_margin_fixed import fetch_margin_data
    
    print("="*80)
    print("两融数据分析 - 卞董专用版本")
    print("="*80)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print()
    
    # 获取数据
    print("步骤1: 获取两融数据")
    print("-"*80)
    
    df, source = fetch_margin_data(date='20260302')
    
    if df is None or df.empty:
        print("✗ 数据获取失败，分析终止")
        sys.exit(1)
    
    print(f"\n✓ 数据获取成功（来源: {source}）")
    print(f"数据维度: {df.shape}")
    print(f"数据列: {list(df.columns)}")
    
    # 分析数据
    print("\n步骤2: 分析两融变化")
    print("-"*80)
    
    df_analyzed, alerts = analyze_margin_changes(df, history_days=30)
    
    # 保存结果
    import os
    os.makedirs('output', exist_ok=True)
    
    # 保存分析后的数据
    output_file = 'output/margin_analysis.csv'
    df_analyzed.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✓ 分析结果已保存到: {output_file}")
    
    # 保存警报
    alert_file = 'output/margin_alerts.txt'
    with open(alert_file, 'w', encoding='utf-8') as f:
        f.write(f"两融警报报告\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"="*80 + "\n\n")
        
        if alerts:
            for i, alert in enumerate(alerts, 1):
                f.write(f"{i}. {alert}\n")
        else:
            f.write("✓ 无警报，市场状态正常\n")
    
    print(f"✓ 警报列表已保存到: {alert_file}")
    
    print("\n" + "="*80)
    print("测试完成")
    print("="*80)
