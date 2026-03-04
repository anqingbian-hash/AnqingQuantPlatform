#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据验证脚本 - 确保所有股票代码和名称准确无误
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.stock_codes_db import VALIDATED_STOCK_CODES, get_stock_name, get_stock_info


def validate_file(filename: str):
    """
    验证文件中的股票代码

    参数:
        filename: 文件名
    """
    print(f"\n=== 验证 {filename} ===")

    # 读取文件
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查所有6位数字的股票代码
    import re
    codes = re.findall(r'["\'](\d{6})["\']', content)

    if not codes:
        print("  未找到股票代码")
        return

    # 去重
    unique_codes = sorted(set(codes))

    print(f"  找到 {len(unique_codes)} 个股票代码: {unique_codes}")

    # 验证每个代码
    errors = []
    for code in unique_codes:
        stock_info = get_stock_info(code)
        if stock_info:
            print(f"  ✓ {code}: {stock_info['name']} ({stock_info['sector']})")
        else:
            print(f"  ✗ {code}: 未在数据库中找到")
            errors.append(code)

    # 检查常见的错误映射
    wrong_mappings = [
        ('002496', '平安银行'),  # 实际上是*ST辉丰
        ('002496', '中科曙光'),  # 实际上中科曙光是603019
        ('000001', '中科曙光'),  # 实际上是平安银行
        ('603019', '中科曙光'),  # 这是正确的
    ]

    print("\n  检查常见的错误映射:")
    for code, wrong_name in wrong_mappings:
        if f"{code}.*{wrong_name}" in content or f'"{code}".*{wrong_name}' in content:
            print(f"  ⚠ 警告: 发现错误映射 {code} = {wrong_name}")
            errors.append(f"{code}={wrong_name}")

    if errors:
        print(f"\n  ❌ 发现 {len(errors)} 个错误")
        for error in errors:
            print(f"     - {error}")
        return False
    else:
        print(f"\n  ✅ 所有股票代码验证通过")
        return True


def main():
    """主函数"""
    print("=" * 60)
    print("数据验证 - 确保股票代码准确性")
    print("=" * 60)

    # 验证的关键股票代码
    print("\n=== 关键股票代码对照表 ===")
    key_stocks = {
        '002496': '*ST辉丰',
        '000001': '平安银行',
        '600519': '贵州茅台',
        '603019': '中科曙光',
        '601318': '中国平安',
    }

    all_correct = True
    for code, expected_name in key_stocks.items():
        actual_name = get_stock_name(code)
        if actual_name == expected_name:
            print(f"  ✓ {code}: {actual_name}")
        else:
            print(f"  ✗ {code}: 期望 {expected_name}, 实际 {actual_name}")
            all_correct = False

    # 验证主要文件
    files_to_validate = [
        'app_v10_full.py',
        'app_v10_dual_source.py',
    ]

    for filename in files_to_validate:
        filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'unified-quot-platform', filename)
        if os.path.exists(filepath):
            if not validate_file(filepath):
                all_correct = False

    # 总结
    print("\n" + "=" * 60)
    if all_correct:
        print("✅ 所有验证通过！数据准确无误")
    else:
        print("❌ 验证失败，请检查上述错误")
    print("=" * 60)

    return 0 if all_correct else 1


if __name__ == '__main__':
    sys.exit(main())
