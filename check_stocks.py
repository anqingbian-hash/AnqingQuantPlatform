#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 检查股票池是否正确

stocks = [
    ('002475.SZ', '立讯精密', '通信设备', 35, 0.6, '算力'),
    ('300760.SZ', '中际旭创', '通信设备', 28, 0.8, '算力'),
    ('002316.SZ', '亚联发展', '通信设备', 42, 0.4, '算力'),
    ('002496.SZ', '中科曙光', '计算机', 65, 0.4, '算力'),
    ('300722.SZ', '贝斯特', '通信设备', 22, 0.5, '算力'),
]

print("=" * 60)
print("🔍 检查股票池...")
print("=" * 60)

for i, (ts_code, name, industry, price, pct_chg, vol_ratio, theme) in enumerate(stocks, 1):
    print(f"\n[{i}] {name} ({ts_code})")
    print(f"   板块: {industry}")
    print(f"   主题: {theme}")
    print(f"   价格: ¥{price:.2f}")
    print(f"   涨跌: {pct_chg:+.2f}%")
    print(f"   量比: {vol_ratio:.1f}倍")

print("\n" + "=" * 60)
print("✅ 检查完成")
print("=" * 60)
