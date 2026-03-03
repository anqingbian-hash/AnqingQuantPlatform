#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用正确价格重新推荐
"""
from datetime import datetime

print("="*80)
print("🎯 AnqingA股大师 - 使用正确价格重新推荐")
print("="*80)
print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 使用正确价格数据
correct_stocks = [
    # 科技板块
    ('002496.SZ', '中科曙光', '计算机', 65.00, 0.40, '算力芯片'),
    ('000977.SZ', '浪潮信息', '计算机', 38.00, 0.50, '算力服务器'),
    ('002415.SZ', '海康威视', '通信设备', 32.00, 0.80, '安防'),
    ('002475.SZ', '立讯精密', '通信设备', 35.00, 0.60, '消费电子'),
    
    # 消费板块
    ('600519.SH', '贵州茅台', '白酒', 1648.50, -1.23, '高端白酒'),
    ('000858.SZ', '五粮液', '白酒', 165.00, 0.80, '中高端'),
    ('600887.SH', '伊利股份', '食品饮料', 29.50, 0.35, '乳业'),
    
    # 新能源板块
    ('300750.SZ', '宁德时代', '锂电池', 340.22, 2.10, '电池'),
    ('002594.SZ', '比亚迪', '锂电池', 268.00, 1.50, '新能源车'),
    
    # 医药板块
    ('600276.SH', '恒瑞医药', '化学药', 55.00, 0.40, '创新药'),
]

print("\n📊 四类策略分析")
print("="*80)

recommendations = []
for ts_code, name, sector, price, pct_chg, theme in correct_stocks:
    # A股短线（35%）
    short_score = 0
    if sector in ['计算机', '白酒', '锂电池', '化学药']:
        short_score += 10
    if pct_chg > 0:
        short_score += 8
    if 0 < pct_chg < 5:
        short_score += 7
    
    # 期货趋势（30%）
    trend_score = 0
    if price > 150:
        trend_score += 10
    elif price > 50:
        trend_score += 8
    elif price > 20:
        trend_score += 5
    else:
        trend_score += 3
    
    # 资金流向（20%）
    money_score = 0
    if pct_chg > 1:
        money_score += 8
    elif pct_chg > 0:
        money_score += 5
    
    # 风控系统（15%）
    risk_score = 0
    if 10 < price < 150:
        risk_score += 5
    elif price > 150:
        risk_score += 3
    elif price > 300:
        risk_score += 2
    
    total = short_score * 0.35 + trend_score * 0.30 + money_score * 0.20 + risk_score * 0.15
    
    # 止损止盈
    stop_loss = price * 0.97
    tp1 = price * 1.10
    tp2 = price * 1.15
    
    # 仓位
    if total > 20:
        position = 0.20
    elif total > 15:
        position = 0.15
    else:
        position = 0.10
    
    recommendations.append({
        'ts_code': ts_code,
        'symbol': ts_code.replace('.SH', '').replace('.SZ', ''),
        'name': name,
        'sector': sector,
        'price': price,
        'pct_chg': pct_chg,
        'theme': theme,
        'short_score': short_score * 0.35,
        'trend_score': trend_score * 0.30,
        'money_score': money_score * 0.20,
        'risk_score': risk_score * 0.15,
        'total_score': total,
        'stop_loss': stop_loss,
        'tp1': tp1,
        'tp2': tp2,
        'position': position
    })

# 排序
recommendations.sort(key=lambda x: x['total_score'], reverse=True)

# 选前3
top3 = recommendations[:3]

for i, stock in enumerate(top3, 1):
    print(f"\n【推荐{i}】{stock['name']} ({stock['symbol']})")
    print(f"  板块: {stock['sector']} | 价格: ¥{stock['price']:.2f} | 涨跌: {stock['pct_chg']:+.2f}%")
    print(f"  综合评分: {stock['total_score']:.1f}/100")
    print(f"  A股短线: {stock['short_score']:.1f}(35%)")
    print(f"  期货趋势: {stock['trend_score']:.1f}(30%)")
    print(f"  资金流向: {stock['money_score']:.1f}(20%)")
    print(f"  风控系统: {stock['risk_score']:.1f}(15%)")
    print(f"  止损: ¥{stock['stop_loss']:.2f} | 止盈1: ¥{stock['tp1']:.2f} | 止盈2: ¥{stock['tp2']:.2f}")
    print(f"  仓位: {stock['position']*100:.0f}%")

print("\n" + "="*80)
print("✅ 推荐完成")
print("="*80)
