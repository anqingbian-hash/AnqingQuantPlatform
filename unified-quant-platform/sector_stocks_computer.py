#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 计算机板块股票池（从板块分析结果提取）
sectors = {
    '计算机': [
        ('002496.SZ', '中科曙光', 65, 0.4),
        ('000977.SZ', '浪潮信息', 38, 0.5),
        ('300782.SZ', '卓易信息', 12, 0.6),
    ]
}

print("=" * 60)
print("🎯 计算机板块选股池")
print("=" * 60)

for sector, stocks in sectors.items():
    print(f"\n📊 {sector} 板块股票:")
    for i, (ts_code, name, price, pct_chg) in enumerate(stocks, 1):
        print(f"{i}. {name} ({ts_code})")
        print(f"   价格: ¥{price:.2f}")
        print(f"   涨跌: {pct_chg:+.2f}%")

print("\n✅ 计算机板块股票池构建完成")
print("=" * 60)
