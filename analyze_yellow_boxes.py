#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析卞董标记的黄色框
"""

import cv2
import numpy as np
import pytesseract
from typing import List, Dict
import re
import json


def find_yellow_boxes(image: np.ndarray) -> List[Dict]:
    """
    查找所有黄色框
    """
    # 转换为HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 黄色范围（宽松）
    lower = np.array([15, 100, 100])
    upper = np.array([45, 255, 255])

    # 创建掩码
    mask = cv2.inRange(hsv, lower, upper)

    # 查找轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    yellow_boxes = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        # 过滤小区域
        if w < 30 or h < 15:
            continue

        # 提取ROI
        roi = image[y:y+h, x:x+w]

        # OCR识别
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray, config='--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789.').strip()

        # 提取数字
        numbers = re.findall(r'\d+\.?\d*', text)

        if numbers:
            yellow_boxes.append({
                'x': x,
                'y': y,
                'width': w,
                'height': h,
                'text': text,
                'value': float(numbers[0]),
                'center_y': y + h // 2
            })

    # 按y坐标排序
    yellow_boxes.sort(key=lambda b: b['center_y'])

    return yellow_boxes


def classify_yellow_boxes(yellow_boxes: List[Dict]) -> Dict[str, Dict]:
    """
    根据Y坐标分类黄色框（S2、现价、R2）
    """
    if len(yellow_boxes) < 3:
        return {
            'count': len(yellow_boxes),
            's2': None,
            'current_price': None,
            'r2': None
        }

    # 按Y坐标排序后
    # 最低的y是S2（支撑位，价格最低）
    # 中间的y是现价
    # 最高的y是R2（阻力位，价格最高）
    
    sorted_boxes = sorted(yellow_boxes, key=lambda b: b['center_y'])
    
    result = {
        'count': len(yellow_boxes),
        's2': sorted_boxes[0] if len(sorted_boxes) >= 1 else None,
        'current_price': sorted_boxes[1] if len(sorted_boxes) >= 2 else None,
        'r2': sorted_boxes[2] if len(sorted_boxes) >= 3 else None
    }

    return result


def main():
    """主函数"""
    import os

    # 测试图片
    test_image = "/root/.openclaw/media/inbound/57337644-f52c-499d-825f-b3cc39322832.jpg"

    if not os.path.exists(test_image):
        print(f"错误：图像不存在：{test_image}")
        return

    print(f"正在分析图片：{test_image}")

    # 读取图像
    image = cv2.imread(test_image)
    if image is None:
        print(f"错误：无法读取图像：{test_image}")
        return

    height, width = image.shape[:2]
    print(f"图像尺寸：{width}x{height}")

    # 查找黄色框
    print("\n=== 查找黄色框 ===")
    yellow_boxes = find_yellow_boxes(image)

    print(f"找到 {len(yellow_boxes)} 个黄色框")

    for i, box in enumerate(yellow_boxes, 1):
        print(f"\n黄色框{i}:")
        print(f"  位置：x={box['x']}, y={box['y']}")
        print(f"  尺寸：{box['width']}x{box['height']}")
        print(f"  中心Y：{box['center_y']}")
        print(f"  OCR文本：{box['text']}")
        print(f"  识别价格：{box['value']}")

    # 分类黄色框
    print(f"\n=== 分类黄色框 ===")
    classified = classify_yellow_boxes(yellow_boxes)

    print(f"总计：{classified['count']} 个黄色框")

    if classified['s2']:
        print(f"\nS2（支撑位，最低）：")
        print(f"  价格：{classified['s2']['value']}")
        print(f"  Y坐标：{classified['s2']['center_y']}")

    if classified['current_price']:
        print(f"\n现价（中间）：")
        print(f"  价格：{classified['current_price']['value']}")
        print(f"  Y坐标：{classified['current_price']['center_y']}")

    if classified['r2']:
        print(f"\nR2（阻力位，最高）：")
        print(f"  价格：{classified['r2']['value']}")
        print(f"  Y坐标：{classified['r2']['center_y']}")

    # 对比分析
    print(f"\n=== 对比分析 ===")

    manual_annotation = {
        'S2': 8.48,
        'current_price': 15.69,
        'R2': 17.58
    }

    for name, box in [('S2', classified['s2']), 
                     ('current_price', classified['current_price']),
                     ('R2', classified['r2'])]:
        if box:
            ocr_value = box['value']
            manual_value = manual_annotation[name]
            diff = abs(ocr_value - manual_value)

            if diff < 0.1:
                print(f"✓ {name}：OCR={ocr_value}, 人工={manual_value}, 误差={diff:.2f}（完全准确）")
            elif diff < 0.5:
                print(f"✓ {name}：OCR={ocr_value}, 人工={manual_value}, 误差={diff:.2f}（基本准确）")
            elif diff < 1.0:
                print(f"△ {name}：OCR={ocr_value}, 人工={manual_value}, 误差={diff:.2f}（可接受）")
            else:
                print(f"✗ {name}：OCR={ocr_value}, 人工={manual_value}, 误差={diff:.2f}（不准确）")
        else:
            print(f"✗ {name}：未识别到")

    # 保存结果
    result = {
        'image_path': test_image,
        'yellow_boxes': yellow_boxes,
        'classified': classified,
        'comparison': {}
    }

    # 添加对比数据
    for name, box in [('S2', classified['s2']), 
                     ('current_price', classified['current_price']),
                     ('R2', classified['r2'])]:
        if box:
            ocr_value = box['value']
            manual_value = manual_annotation[name]
            diff = abs(ocr_value - manual_value)

            result['comparison'][name] = {
                'ocr_value': ocr_value,
                'manual_value': manual_value,
                'diff': diff,
                'accuracy': 'perfect' if diff < 0.1 else 
                            'good' if diff < 0.5 else 
                            'acceptable' if diff < 1.0 else 'poor'
            }

    output_file = "/root/.openclaw/workspace/yellow_box_analysis_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n✓ 结果已保存到：{output_file}")


if __name__ == "__main__":
    main()
