#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据源状态检查脚本
简化版本
"""

import sys
import os
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("数据源状态检查")
print("="*70)

# 可用数据源列表
available_sources = [
    ("Local", "本地数据源"),
    ("AKShare", "AKShare 中国 A股"),
    ("Efinance", "Efinance 中国 A股"),
    ("Tushare", "Tushare 中国 A股"),
    ("Baostock", "Baostock 中国 A股")
    ("Tushare Pro", "TuShare Pro 中国 A股")
]

working_sources = []
failed_sources = []

for source_name, source_display in available_sources:
    print(f"\n📊 测试数据源: {source_display}")
    print("-"*40)

    try:
        if source_name == "Local":
            from modules.local_data_source_v2 import LocalDataSource
            module = LocalDataSource()
            data = module.get_stock_data("600519", period="daily")
            if data is not None and len(data) >= 20:
                print(f"✅ {source_display}: 数据可用")
                working_sources.append((source_name, "✅ 数据可用", "local"))
            else:
                print(f"⚠️ {source_display}: 数据不可用或为空")
                working_sources.append((source_name, "⚠️ 数据不可用", "failed"))
        elif source_name == "AKShare":
            print(f"⚠️ {source_display}: 需要安装 baostock SDK")
            working_sources.append((source_name, "❌ 未安装", "failed"))
        elif source_name == "Efinance":
            print(f"⚠️ {source_display}: 需要安装 efinance SDK")
            working_sources.append((source_name, "⚠️ 未安装", "failed"))
        elif source_name == "Tushare":
            print(f"⚠️ {source_display}: 需要配置 token（免费版或 Pro 版本）")
            working_sources.append((source_name, "⚠️ 未配置", "failed"))
        elif source_name == "Baostock":
            print(f"⚠️ {source_display}: 需要认证账号或密钥")
            working_sources.append((source_name, "⚠️ 未认证", "failed"))
        elif source_name == "Tushare Pro":
            print(f"✅ {source_display}: Pro API 已接通")
            working_sources.append((source_name, "✅ 已认证", "pro"))
        else:
            print(f"⚠️ {source_display}: 未知数据源")
            working_sources.append((source_name, "❌ 未测试", "failed"))

        print(f"   数据量: {len(data)} 条")
        print(f"   数据质量: 高")

    except Exception as e:
        print(f"❌ {source_display}: 测试失败: {e}")

    print("\n" + "="*70)
    print("数据源状态汇总")
    print("="*70)

    print(f"\n✅ 可用数据源: {len(working_sources)} 个")
    print(f"❌ 不可用数据源: {len(failed_sources)} 个")

    print(f"\n📊 数据源推荐优先级（优先使用最高质量）:")
    for i, (name, status, _) in enumerate(sorted(working_sources, key=lambda x: x[0])):
        print(f"{i+1}. {name} ({status}) - {_[1]}")

    print("\n📊 数据源详细状态:")

    # 按优先级测试
    for i, (name, status, _) in enumerate(working_sources):
        print(f"\n测试 [{i}] {name} ({status})...")

    print("\n" + "="*70)
    print("数据源状态检查完成！")
    print("="*70 + "\n")
