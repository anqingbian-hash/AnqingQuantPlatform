#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据源状态检查脚本
检查所有数据源的可用性
"""

import sys
import os
import warnings
warnings.filterwarnings('ignore')

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*70)
print("数据源状态检查")
print("="*70)

# 检查数据源列表
sources_to_check = [
    ("Local", "本地数据源", "modules.local_data_source.LocalDataSource"),
    ("AKShare", "AKShare", "modules.akshare_source.AkShareDataSource"),
    ("Efinance", "Efinance", "modules.efinance_source.EfinanceDataSource"),
    ("Tushare", "Tushare", "modules.tushare_source.TushareDataSource"),
    ("Baostock", "Baostock", "modules.baostock_source.BaostockDataSource"),
]

available_sources = []

print(f"\n开始检查 {len(sources_to_check)} 个数据源\n")

for source_name, source_display, module_path in sources_to_check:
    print(f"\n{'='*70}")
    print(f"检查数据源: {source_display} ({source_name})")
    print(f"模块: {module_path}")
    print(f"{'='*70}")

    # 尝试获取状态
    try:
        # 分割模块路径
        module_name = '.'.join(module_path.split('.')[:-1])
        class_name = module_path.split('.')[-1]

        # 导入模块
        module = __import__(module_name, fromlist=[class_name])
        data_source_class = getattr(module, class_name)
        source_obj = data_source_class()
        data = source_obj.get_status()

        if data.get("status") == "stable":
            available_sources.append({
                "name": source_display,
                "module": module_path,
                "source": data.get("source_type", "unknown"),
                "status": data.get("status", "unknown"),
                "network_required": data.get("network_required", False),
                "data_quality": data.get("data_quality", "low"),
                "stocks_supported": data.get("stocks_supported", [])
            })
            print(f"✅ {source_display}: ✅ 可用 - {data.get('status', 'unknown')}")
            print(f"   数据质量: {data.get('data_quality', 'unknown')}")
            print(f"   支持股票: {len(data.get('stocks_supported', []))}")
        else:
            available_sources.append({
                "name": source_display,
                "module": module_path,
                "source": data.get("source_type", "unknown"),
                "status": data.get("status", "unknown"),
                "network_required": data.get("network_required", False),
                "data_quality": data.get("data_quality", "low"),
                "stocks_supported": data.get("stocks_supported", [])
            })
            print(f"❌ {source_display}: ❌ 不可用 - {data.get('status', 'unknown')}")
            print(f"   数据质量: {data.get('data_quality', 'unknown')}")
            print(f"   支持股票: {data.get('stocks_supported', [])}")

    except ImportError as e:
        print(f"❌ {source_display}: ❌ 模块未找到 - {e}")
        available_sources.append({
            "name": source_display,
            "module": module_path,
            "source": "unknown",
            "status": "uninstalled",
            "error": "ModuleNotFoundError"
        })
    except Exception as e:
        print(f"❌ {source_display}: ❌ 检查失败: {e}")
        available_sources.append({
            "name": source_display,
            "module": module_path,
            "source": "unknown",
            "status": "failed",
            "error": str(e)
        })

print(f"\n" + "="*70)
print("检查完成")
print("="*70)

# 汇总
print(f"\n✅ 可用数据源: {len([s for s in available_sources if s['status'] == 'stable'])} 个")
print(f"❌ 不可用数据源: {len([s for s in available_sources if s['status'] != 'stable'])} 个")

print("\n可用数据源（按优先级）:")
for i, s in enumerate([s for s in available_sources if s['status'] == 'stable'], 1):
    print(f"  {i}. {s['name']} ({s['status']}) - {s.get('data_quality', 'N/A')}")

print("\n" + "="*70)
print("不可用数据源:")
for i, s in enumerate([s for s in available_sources if s['status'] != 'stable'], 1):
    print(f"  {i}. {s['name']} ({s['status']}) - {s.get('error', 'N/A')}")

print("\n" + "="*70)
