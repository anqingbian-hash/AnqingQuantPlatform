#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于人工标注数据验证OCR识别
"""

import sys
import os
sys.path.append('/root/.openclaw/workspace')

import cv2
import numpy as np
import json
import re
from modules.wenhua_parser_v2 import WenHuaParserV2


def manual_annotation_test():
    """使用人工标注数据测试"""

    # 创建解析器
    parser = WenHuaParserV2()

    # 测试图片路径
    test_image = "/root/.openclaw/media/inbound/92ea67d8-5897-401a-825a-63df2f39ee75.jpg"

    # 人工标注数据（卞董提供）
    manual_annotation = {
        'S2': 8.48,
        'current_price': 15.69,
        'R2': 17.58,
        'high_price': 20.10
    }

    print(f"\n=== 人工标注数据 ===")
    print(f"S2（支撑位）：{manual_annotation['S2']}")
    print(f"现价：{manual_annotation['current_price']}")
    print(f"R2（阻力位）：{manual_annotation['R2']}")
    print(f"图中高点：{manual_annotation['high_price']}")

    # 解析图片
    print(f"\n正在解析图片：{test_image}")
    result = parser.parse_screenshot(test_image)

    print(f"\n=== OCR识别结果 ===")

    # 打印SR线
    support_lines = result['main_chart'].get('support_lines', [])
    resistance_lines = result['main_chart'].get('resistance_lines', [])

    print(f"\n支撑线（绿色）：")
    for line in support_lines:
        print(f"  y={line['y']}, price={line.get('price', 'N/A')}")

    print(f"\n阻力线（红色）：")
    for line in resistance_lines:
        print(f"  y={line['y']}, price={line.get('price', 'N/A')}")

    # 打印现价
    current_price = result['main_chart'].get('current_price')
    if current_price:
        print(f"\n现价：{current_price.get('price', 'N/A')}")
        print(f"  位置：x={current_price.get('x')}, y={current_price.get('y')}")

    # 打印净量
    net_volume = result['sub_chart_1']
    if net_volume.get('value') is not None:
        print(f"\n净量：{net_volume['value']} ({'正' if net_volume['is_positive'] else '负'})")
    else:
        print(f"\n净量：未识别到")

    # 打印DELTA
    delta = result['sub_chart_2']
    if delta.get('slope'):
        print(f"\nDELTA斜率：{delta['slope']}")

    # 对比分析
    print(f"\n=== 对比分析 ===")

    # 对比S2
    if support_lines:
        print(f"✗ OCR识别到{len(support_lines)}条支撑线，但未能识别到价格")
        print(f"  人工标注：S2 = {manual_annotation['S2']}")
    else:
        print(f"✗ OCR未识别到支撑线")
        print(f"  人工标注：S2 = {manual_annotation['S2']}")

    # 对比R2
    if resistance_lines:
        print(f"✗ OCR识别到{len(resistance_lines)}条阻力线，但未能识别到价格")
        print(f"  人工标注：R2 = {manual_annotation['R2']}")
    else:
        print(f"✗ OCR未识别到阻力线")
        print(f"  人工标注：R2 = {manual_annotation['R2']}")

    # 对比现价
    if current_price and current_price.get('price'):
        ocr_price = current_price['price']
        manual_price = manual_annotation['current_price']

        diff = abs(ocr_price - manual_price)

        if diff < 0.1:
            print(f"✓ 现价识别准确")
            print(f"  OCR：{ocr_price}, 人工：{manual_price}")
        elif diff < 1.0:
            print(f"△ 现价识别基本准确（误差{diff:.2f}）")
            print(f"  OCR：{ocr_price}, 人工：{manual_price}")
        else:
            print(f"✗ 现价识别不准确（误差{diff:.2f}）")
            print(f"  OCR：{ocr_price}, 人工：{manual_price}")
    else:
        print(f"✗ OCR未识别到现价")
        print(f"  人工标注：现价 = {manual_annotation['current_price']}")

    # 保存结果
    output_file = "/root/.openclaw/workspace/manual_annotation_test_result.json"

    test_result = {
        'manual_annotation': manual_annotation,
        'ocr_result': result,
        'comparison': {
            'S2_found': len(support_lines) > 0,
            'R2_found': len(resistance_lines) > 0,
            'current_price_found': current_price is not None and current_price.get('price') is not None
        }
    }

    # 转换numpy类型
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.integer, np.int32, np.int64)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float32, np.float64)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(test_result, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)

    print(f"\n测试结果已保存到：{output_file}")


if __name__ == "__main__":
    manual_annotation_test()
