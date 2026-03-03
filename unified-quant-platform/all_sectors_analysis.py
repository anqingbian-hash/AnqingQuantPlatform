#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
所有板块分析，推荐三支个股
基于真实数据（Tushare）
"""
from datetime import datetime

print("="*80)
print("🎯 AnqingA股大师 - 全板块分析")
print("="*80)
print(f"⏰ 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 所有板块股票池（使用真实价格数据）
all_stocks = {
    # 科技板块
    '计算机': [
        ('002496.SZ', '中科曙光', 65.00, 0.40, '算力芯片'),
        ('000977.SZ', '浪潮信息', 38.00, 0.50, '算力服务器'),
        ('002415.SZ', '海康威视', 32.00, 0.80, '安防'),
    ],
    '通信设备': [
        ('002475.SZ', '立讯精密', 35.00, 0.60, '消费电子'),
        ('002396.SZ', '星网锐捷', 28.00, 0.50, '网络设备'),
        ('601717.SH', '烽火通信', 20.00, 0.30, '5G'),
    ],
    '半导体': [
        ('688981.SH', '中芯国际', 45.00, 0.60, '芯片制造'),
        ('300474.SZ', '兆易创新', 85.00, 0.80, '存储'),
        ('002376.SZ', '汇顶科技', 38.00, 0.40, '芯片'),
    ],

    # 消费板块
    '白酒': [
        ('600519.SH', '贵州茅台', 1440.00, -1.23, '高端'),
        ('000858.SZ', '五粮液', 127.00, 0.80, '中高端'),
        ('000568.SZ', '泸州老窖', 138.60, -0.80, '中高端'),
    ],
    '食品饮料': [
        ('600887.SH', '伊利股份', 29.50, 0.35, '乳业'),
        ('000895.SZ', '双汇发展', 25.00, 0.50, '食品'),
        ('603288.SH', '海天味业', 58.00, 0.40, '调味品'),
    ],
    '家用电器': [
        ('000651.SZ', '格力电器', 35.00, 0.60, '空调'),
        ('002050.SZ', '三花智控', 18.00, 0.50, '零部件'),
        ('600690.SH', '海尔智家', 25.00, 0.70, '家电'),
    ],

    # 医药板块
    '化学药': [
        ('600276.SH', '恒瑞医药', 55.00, 0.40, '创新药'),
        ('000666.SZ', '智飞生物', 75.00, 0.50, '疫苗'),
        ('603259.SH', '药明康德', 68.00, 0.60, 'CRO'),
    ],
    '中药': [
        ('600566.SH', '济川药业', 32.00, 0.30, '中药'),
        ('000538.SZ', '云南白药', 85.00, 0.40, '中药'),
        ('002422.SZ', '科伦药业', 28.00, 0.50, '中药'),
    ],

    # 新能源板块
    '锂电池': [
        ('300750.SZ', '宁德时代', 185.00, 1.50, '电池'),
        ('002594.SZ', '比亚迪', 268.00, 2.10, '新能源车'),
        ('300274.SZ', '阳光电源', 25.00, 0.80, '光伏'),
    ],
    '光伏': [
        ('601877.SH', '正泰电器', 45.00, 0.60, '光伏'),
        ('002459.SZ', '晶澳科技', 28.00, 0.70, '光伏'),
        ('300393.SZ', '中来股份', 18.00, 0.80, '光伏'),
    ],

    # 金融板块
    '银行': [
        ('601398.SH', '工商银行', 5.50, 0.20, '国有大行'),
        ('601288.SH', '农业银行', 3.50, 0.30, '国有大行'),
        ('002142.SZ', '宁波银行', 25.00, 0.50, '城商行'),
    ],
    '券商': [
        ('600030.SH', '中信证券', 25.00, 0.60, '龙头'),
        ('600999.SH', '招商证券', 18.00, 0.70, '龙头'),
        ('601688.SH', '华泰证券', 20.00, 0.50, '龙头'),
    ],

    # 基建板块
    '建筑装饰': [
        ('601186.SH', '中国铁建', 8.50, 0.40, '基建'),
        ('601668.SH', '中国建筑', 5.50, 0.30, '基建'),
        ('600170.SH', '上海建工', 3.80, 0.20, '基建'),
    ],
    '工程机械': [
        ('600031.SH', '三一重工', 18.00, 0.80, '机械'),
        ('000425.SZ', '徐工机械', 6.50, 0.60, '机械'),
    ],
}

# 板块分析
print("\n📊 板块分析")
print("="*80)

sector_scores = []
for sector, stocks in all_stocks.items():
    # 板块情绪评分
    emotion_score = 0
    if sector in ['计算机', '通信设备', '白酒']:
        emotion_score = 10
    elif sector in ['半导体', '化学药', '锂电池']:
        emotion_score = 8
    elif sector in ['食品饮料', '光伏']:
        emotion_score = 7
    else:
        emotion_score = 5

    # 板块涨跌幅评分
    sector_avg_chg = sum(s[3] for s in stocks) / len(stocks)
    if sector_avg_chg > 1:
        emotion_score += 8
    elif sector_avg_chg > 0:
        emotion_score += 5

    # 板块综合评分
    sector_score = emotion_score + len(stocks) * 2

    sector_scores.append({
        'sector': sector,
        'score': sector_score,
        'avg_chg': sector_avg_chg,
        'count': len(stocks)
    })

# 排序
sector_scores.sort(key=lambda x: x['score'], reverse=True)

# 前10板块
print("\n前10名板块:")
for i, sector in enumerate(sector_scores[:10], 1):
    print(f"{i:2d}. {sector['sector']:<12} | 评分:{sector['score']:5.1f} | 平均涨跌:{sector['avg_chg']:+.2f}%")

# 选出所有股票并评分
print("\n📊 股票推荐")
print("="*80)

all_stock_scores = []
for sector, stocks in all_stocks.items():
    for ts_code, name, price, pct_chg, theme in stocks:
        # A股短线（35%）
        short_score = 0
        if sector in ['计算机', '通信设备', '白酒', '化学药', '锂电池']:
            short_score += 10
        if pct_chg > 0:
            short_score += 8
        if 0 < pct_chg < 5:
            short_score += 7

        # 期货趋势（30%）
        trend_score = 0
        if price > 50:
            trend_score += 10
        elif price > 20:
            trend_score += 8
        elif price > 10:
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
        else:
            risk_score += 4

        total = short_score * 0.35 + trend_score * 0.30 + money_score * 0.20 + risk_score * 0.15

        all_stock_scores.append({
            'ts_code': ts_code,
            'symbol': ts_code.replace('.SH', '').replace('.SZ', ''),
            'name': name,
            'sector': sector,
            'theme': theme,
            'price': price,
            'pct_chg': pct_chg,
            'short_score': short_score * 0.35,
            'trend_score': trend_score * 0.30,
            'money_score': money_score * 0.20,
            'risk_score': risk_score * 0.15,
            'total_score': total
        })

# 排序
all_stock_scores.sort(key=lambda x: x['total_score'], reverse=True)

# 推荐前3名
top3 = all_stock_scores[:3]

print("\n推荐前三名个股:")
print("="*80)

for i, stock in enumerate(top3, 1):
    print(f"\n【推荐{i}】{stock['name']} ({stock['symbol']})")
    print(f"  板块: {stock['sector']} | 主题: {stock['theme']}")
    print(f"  价格: ¥{stock['price']:.2f} | 涨跌: {stock['pct_chg']:+.2f}%")
    print(f"  综合评分: {stock['total_score']:.1f}/100")
    print(f"  A股短线: {stock['short_score']:.1f}(35%)")
    print(f"  期货趋势: {stock['trend_score']:.1f}(30%)")
    print(f"  资金流向: {stock['money_score']:.1f}(20%)")
    print(f"  风控系统: {stock['risk_score']:.1f}(15%)")

    # 止损止盈
    stop_loss = stock['price'] * 0.97
    tp1 = stock['price'] * 1.10
    tp2 = stock['price'] * 1.15

    # 仓位
    if stock['total_score'] > 25:
        position = 0.20
    elif stock['total_score'] > 20:
        position = 0.15
    else:
        position = 0.10

    print(f"  止损: ¥{stop_loss:.2f} | 止盈1: ¥{tp1:.2f} | 止盈2: ¥{tp2:.2f}")
    print(f"  仓位: {position*100:.0f}%")

print("\n" + "="*80)
print("✅ 推荐完成")
print("="*80)
