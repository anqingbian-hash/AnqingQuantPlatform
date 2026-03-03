#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
其他板块选股（白酒、医药、新能源、半导体）
"""
import random
from datetime import datetime

# 白酒板块
baijiu_stocks = [
    ('600519.SH', '贵州茅台', '消费', 1850, 0.8, '消费'),
    ('000858.SZ', '五粮液', '消费', 165, 0.5, '消费'),
    ('000568.SZ', '泸州老窖', '消费', 16, 0.3, '消费'),
]

# 医药板块
zhongyao_stocks = [
    ('600276.SH', '恒瑞医药', '医药', 55, 0.4, '医药'),
    ('002007.SZ', '全新好', '医药', 28, 0.5, '医药'),
    ('600566.SH', '济川药业', '医药', 32, 0.3, '医药'),
    ('600566.SH', '济川药业', '医药', 32, 0.3, '医药'),
]

# 新能源板块
xinnengyuan_stocks = [
    ('300750.SZ', '宁德时代', '新能源', 185, 1.5, '新能源'),
    ('002594.SZ', '比亚迪', '汽车', 268, 2.1, '新能源'),
    ('601012.SH', '隆基绿能', '新能源', 25, 0.8, '新能源'),
    ('601012.SH', '隆基绿能', '新能源', 25, 0.8, '新能源'),
]

# 半导体板块
bandaoti_stocks = [
    ('688981.SH', '中芯国际', '半导体', 45, 0.6, '科技'),
    ('600460.SH', '士兰微', '半导体', 38, 0.7, '科技'),
    ('002376.SZ', '汇顶科技', '半导体', 85, 0.4, '科技'),
    ('300474.SZ', '兆易创新', '半导体', 85, 0.8, '科技'),
]

def analyze_stock(stock):
    """四类策略评分"""
    short_score = 0
    trend_score = 0
    money_score = 0
    risk_score = 0
    signals = []
    
    ts_code, name, industry, price, pct_chg, vol_ratio, theme = stock
    
    # A股短线实战策略（35%）
    if theme in ['消费', '医药', '新能源', '科技']:
        short_score += 12
        if pct_chg > 0:
            short_score += 8
        if 0 < pct_chg < 8:
            short_score += 6
    if industry == '消费':
        short_score += 5
    
    # 期货趋势跟踪策略（30%）
    if 10 < price < 100:
        trend_score += 8
    if pct_chg > 1:
        trend_score += 6
    if 5 < pct_chg < 10:
        trend_score += 5
    
    # 资金流向策略（20%）
    if pct_chg > 2:
        money_score += 8
    if vol_ratio > 1.0:
        money_score += 6
    if theme in ['新能源']:
        money_score += 4
    
    # 风控系统（15%）
    if 10 < price < 80:
        risk_score += 5
    elif price > 150:
        risk_score += 3
    if industry in ['消费', '医药']:
        risk_score += 3
    
    total_score = short_score * 0.35 + trend_score * 0.30 + money_score * 0.20 + risk_score * 0.15
    
    # 信号
    if short_score > 8:
        signals.append("A股短线：情绪周期+量价")
    if trend_score > 8:
        signals.append("期货趋势：多周期共振")
    if money_score > 8:
        signals.append("资金流向：主力关注")
    if risk_score > 8:
        signals.append("风控系统：低位安全")
    
    return total_score, signals

def generate_recommendations():
    """生成推荐"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 合并所有板块
    all_stocks = []
    all_stocks.extend([(s[0], s[1], s[2], s[3], s[4]) for s in baijiu_stocks])
    all_stocks.extend([(s[0], s[1], s[2], s[3], s[4]) for s in zhongyao_stocks])
    all_stocks.extend([(s[0], s[1], s[2], s[3], s[4]) for s in xinnengyuan_stocks])
    all_stocks.extend([(s[0], s[1], s[2], s[3], s[4]) for s in bandaoti_stocks])
    
    print("="*80)
    print("🎯 AnqingA股大师 - 其他板块选股")
    print("="*80)
    print(f"⏰ 生成时间: {now}")
    print("📋 分析板块: 白酒、医药、新能源、半导体")
    print("="*80)
    
    recommendations = []
    
    for stock in all_stocks:
        total_score, signals = analyze_stock(stock)
        
        # 止损止盈计算
        ts_code, name, industry, price, pct_chg, vol_ratio, theme = stock
        stop_loss = price * 0.97
        tp1 = price * 1.10  # 10%
        tp2 = price * 1.15  # 15%
        
        # 仓位计算
        if total_score > 60:
            position = 0.20
        elif total_score > 40:
            position = 0.15
        elif total_score > 25:
            position = 0.12
        else:
            position = 0.10
        
        # 盈亏比
        risk = (price - stop_loss) / price * 100
        reward1 = risk * 1.5  # 1:1.5
        reward2 = risk * 3.0  # 1:3
        
        if total_score > 30:
            recommendations.append({
                'ts_code': ts_code,
                'symbol': ts_code.replace('.SH', '').replace('.SZ', ''),
                'name': name,
                'industry': industry,
                'price': price,
                'pct_chg': pct_chg,
                'theme': theme,
                'short_score': round(total_score * 0.35, 1),
                'trend_score': round(total_score * 0.30, 1),
                'money_score': round(total_score * 0.20, 1),
                'risk_score': round(total_score * 0.15, 1),
                'total_score': round(total_score, 1),
                'stop_loss': round(stop_loss, 2),
                'tp1': round(tp1, 2),
                'tp2': round(tp2, 2),
                'position': round(position * 100, 1),
                'signals': signals,
                'is_star': total_score > 40
            })
    
    # 按评分排序
    recommendations.sort(key=lambda x: x['total_score'], reverse=True)
    
    # 选前10名
    top10 = recommendations[:10]
    
    # 生成报告
    report = f"""
================================================================================
📊 AnqingA股大师 - 其他板块选股报告
================================================================================
⏰ 生成时间: {now}
📋 分析板块: 白酒、医药、新能源、半导体

💡 推荐股票（按四类策略综合评分）
================================================================================
"""

    for i, stock in enumerate(top10, 1):
        star = "⭐" * (5 if stock['is_star'] else (4 if stock['total_score'] > 30 else 3))
        report += f"""
【{star}推荐{i}】{stock['name']} ({stock['symbol']})
{'─'*80}
📋 基本信息:
   • 板块: {stock['industry']}
   • 主题: {stock['theme']}
   • 当前价格: ¥{stock['price']:.2f}
   • 今日涨跌: {stock['pct_chg']:+.2f}%

📊 四类策略评分:
   • A股短线: {stock['short_score']:.1f}分 (35%)
   • 期货趋势: {stock['trend_score']:.1f}分 (30%)
   • 资金流向: {stock['money_score']:.1f}分 (20%)
   • 风控系统: {stock['risk_score']:.1f}分 (15%)
   • 综合评分: {stock['total_score']:.1f}分

📋 信号分析:
"""
        for signal in stock['signals']:
            report += f"   • {signal}\n"
        if not stock['signals']:
            report += "   • 无明显信号\n"

🛑️ 止损止盈:
   • 止损位: ¥{stock['stop_loss']:.2f} (-3%)
   • 第一目标: ¥{stock['tp1']:.2f} (+10%)
   • 第二目标: ¥{stock['tp2']:.2f} (+15%)
   • 盈亏比: 1:1.5 到 1:3

📦 建议仓位: {stock['position']:.0f}% (总资金的{stock['position']/100:.0f}%)
   • 风险: {abs(stock['pct_chg']) + 3}%

💡 交易建议:
   • 严格执行止损止盈纪律
   • 单只股票仓位不超过20%
   • 分散投资，控制风险
"""

    report += f"""
================================================================================
📊 统计信息
================================================================================
• 推荐总数: {len(top10)} 只
• 强烈推荐: {len([s for s in top10 if s['is_star']])} 只
• ⭐⭐⭐⭐ 强烈: {len([s for s in top10 if s['total_score'] > 40])} 只
• 平均评分: {sum(s['total_score'] for s in top10) / len(top10):.1f}分
• 平均建议仓位: {sum(s['position'] for s in top10) / len(top10):.1f}%

================================================================================
⚠️ 重要提示:
================================================================================
• 本推荐基于四类实战策略综合评分
• 白酒：低位布局，长期持有
• 医药：低位关注，左侧交易
• 新能源：波段操作，高抛低吸
• 半导体：景气轮动，技术领先
• 严格执行止损，控制风险
• 单只股票仓位控制在总资金20%以内
• 分散投资，降低集中度

================================================================================
"""

    print(report)

    # 保存结果
    import json
    with open('other_stocks_recommend.json', 'w', encoding='utf-8') as f:
        json.dump({
            'scan_time': now,
            'sectors': ['白酒', '医药', '新能源', '半导体'],
            'recommendations': top10,
            'statistics': {
                'total': len(top10),
                'avg_score': sum(s['total_score'] for s in top10) / len(top10),
                'strong_count': len([s for s in top10 if s['is_star']]),
                'avg_position': sum(s['position'] for s in top10) / len(top10) / 100
            }
        }, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 扫描完成: {len(top10)} 只推荐")
    print(f"✅ 结果已保存: other_stocks_recommend.json")
    print("="*80)
EOF
