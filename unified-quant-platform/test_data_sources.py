#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据源测试脚本
测试所有可用的数据源
"""

import sys
import os
import warnings
warnings.filterwarnings('ignore')

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.local_data_source_v2 import LocalDataSource
from modules.akshare_source import AkShareDataSource
from modules.tushare_source import TushareDataSource

class DataSourceTester:
    """数据源测试器"""

    def __init__(self):
        print("="*70)
        print("数据源测试器初始化")
        print("="*70)

        self.sources = {
            "local": {
                "name": "本地数据源",
                "obj": LocalDataSource(),
                "priority": "低",
                "quality": "simulation",
                "network": False
            },
            "akshare": {
                "name": "AKShare",
                "obj": AkShareDataSource(),
                "priority": "高",
                "quality": "high",
                "network": True
            },
            "tushare": {
                "name": "Tushare",
                "obj": TushareDataSource(),
                "priority": "高",
                "quality": "high",
                "network": True
            }
        }

    def test_stock_data(self, stock_code):
        """测试股票数据获取"""
        print(f"\n测试股票数据: {stock_code}")
        print("="*70)

        results = {}

        # 测试本地数据源
        try:
            print("\n1️⃣ 测试本地数据源...")
            data = self.sources["local"]["obj"].get_stock_data(stock_code)
            if data is not None and len(data) > 0:
                results["local"] = {"status": "success", "count": len(data)}
                print(f"✅ 本地数据源: {results['local']['count']} 条记录")
            else:
                results["local"] = {"status": "failed", "count": 0}
                print(f"❌ 本地数据源: 无数据")
        except Exception as e:
            results["local"] = {"status": "error", "error": str(e)}
            print(f"❌ 本地数据源: {results['local']['error']}")

        # 测试 AKShare
        try:
            print("\n2️⃣ 测试 AKShare 数据源...")
            data = self.sources["akshare"]["obj"].get_stock_data(stock_code)
            if data is not None and len(data) > 0:
                results["akshare"] = {"status": "success", "count": len(data)}
                print(f"✅ AKShare 数据源: {results['akshare']['count']} 条记录")
            else:
                results["akshare"] = {"status": "failed", "count": 0}
                print(f"❌ AKShare 数据源: 无数据")
        except Exception as e:
            results["akshare"] = {"status": "error", "error": str(e)}
            print(f"❌ AKShare 数据源: {results['akshare']['error']}")

        # 测试 Tushare
        try:
            print("\n3️⃣ 测试 Tushare 数据源...")
            data = self.sources["tushare"]["obj"].get_stock_data(stock_code)
            if data is not None and len(data) > 0:
                results["tushare"] = {"status": "success", "count": len(data)}
                print(f"✅ Tushare 数据源: {results['tushare']['count']} 条记录")
            else:
                results["tushare"] = {"status": "failed", "count": 0}
                print(f"❌ Tushare 数据源: 无数据")
        except Exception as e:
            results["tushare"] = {"status": "error", "error": str(e)}
            print(f"❌ Tushare 数据源: {results['tushare']['error']}")

        return results

    def test_market_data(self):
        """测试大盘数据"""
        print(f"\n测试大盘数据...")
        print("="*70)

        results = {}

        # 测试本地数据源
        try:
            print("1️⃣ 测试本地数据源...")
            data = self.sources["local"]["obj"].get_market_data("A股大盘")
            if data and data.get("data") is not None:
                results["local"] = {"status": "success", "count": len(data.get("data"))}
                print(f"✅ 本地数据源: {results['local']['count']} 条记录")
            else:
                results["local"] = {"status": "failed", "count": 0}
                print(f"❌ 本地数据源: 无数据")
        except Exception as e:
            results["local"] = {"status": "error", "error": str(e)}
            print(f"❌ 本地数据源: {results['local']['error']}")

        # 测试 AKShare
        try:
            print("\n2️⃣ 测试 AKShare 数据源...")
            data = self.sources["akshare"]["obj"].get_market_data("A股大盘")
            if data and data.get("data") is not None:
                results["akshare"] = {"status": "success", "count": len(data.get("data"))}
                print(f"✅ AKShare 数据源: {results['akshare']['count']} 条记录")
            else:
                results["akshare"] = {"status": "failed", "count": 0}
                print(f"❌ AKShare 数据源: 无数据")
        except Exception as e:
            results["akshare"] = results.get("akshare", {})

        return results

    def generate_report(self, stock_results, market_results):
        """生成测试报告"""
        print("="*70)
        print("数据源测试报告")
        print("="*70)

        print(f"\n📊 股票数据测试结果:")
        print("-"*40)

        total_count = 0
        for source_name, result in stock_results.items():
            count = result["count"]
            total_count += count
            status = result["status"]
            icon = "✅" if status == "success" else ("❌" if status == "failed" else "⚠️")
            print(f"  {icon} {source_name:12s}: {count:3d} 条记录")

        print(f"\n📊 大盘数据测试结果:")
        print("-"*40)

        for source_name, result in market_results.items():
            count = result["count"]
            status = result["status"]
            icon = "✅" if status == "success" else ("❌" if status == "failed" else "�️️")
            print(f"  {icon} {source_name:12s}: {count:3d} 条记录")

        print(f"\n" + "="*70)
        print(f"总计: {total_count} 条记录")
        print("="*70)


if __name__ == "__main__":
    # 创建测试器
    tester = DataSourceTester()

    # 测试贵州茅台
    print("\n测试1: 股票数据获取")
    stock_results = tester.test_stock_data("600519")

    # 测试大盘数据
    print("\n测试2: 大盘数据获取")
    market_results = tester.test_market_data()

    # 生成报告
    tester.generate_report(stock_results, market_results)

    print("\n测试完成！")
