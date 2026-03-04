#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析黄色框 - 宽松模式
"""

import cv2
import numpy as np
import pytesseract
from typing import List, Dict
import re
import json


def find_all_yellow_boxes(image: np.ndarray) -> List[Dict]:
    """
    查找所有黄色框（非常宽松的阈值）
    """
    # 转换为HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 黄色范围（非常宽松，包括黄色、橙色、淡绿色等）
    # 尝试多个范围
    ranges = [
        (np.array([0, 80, 100]), np.array([30, 255, 255])),  # 红色到黄色
        (np.array([15, 50, 100]), np.array([35, 255, 255])),  # 黄色
        (np.array([10, 50, 100]), np.array([40, 255, 255])),  # 黄橙色
        (np.array([20, 30, 100]), np.array([50, 255, 255])),  # 金黄色
    ]

    combined_mask = np.zeros(image.shape[:2], dtype=np.uint8)

    for lower, upper in ranges:
        mask = cv2.inRange(hsv, lower, upper)
        combined_mask = cv2.bitwise_or(combined_mask, mask)

    # 形态学操作
    kernel = np.ones((5, 5), np.uint8)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)

    # 查找轮廓
    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    yellow_boxes = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        # 过滤：不要太小
        if w < 20 or h < 10:
            continue

        # 提取ROI
        roi = image[y:y+h, x:x+w]

        # 预处理
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        # OCR识别
        text = pytesseract.image_to_string(binary, config='--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789.').strip()

        # 提取数字
        numbers = re.findall(r'\d+\.?\d*', text)

        if numbers:
            yellow_boxes.append({
                'x': x,
                'y': y,
                'width': w,
                'height': h,
                'center_y': y + h // 2,
                'text': text,
                'value': float(numbers[0])
            })

    # 按Y坐标排序
    yellow_boxes.sort(key=lambda b: b['center_y'])

    return yellow_boxes


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

    # 查找所有黄色框
    print("\n=== 查找黄色框（宽松模式）===")
    yellow_boxes = find_all_yellow_boxes(image)

    print(f"找到 {len(yellow_boxes)} 个黄色框")

    for i, box in enumerate(yellow_boxes, 1):
        print(f"\n黄色框{i}:")
        print(f"  位置：x={box['x']}, y={box['y']}")
        print(f"  尺寸：{box['width']}x{box['height']}")
        print(f"  中心Y：{box['center_y']}")
        print(f"  OCR文本：{box['text']}")
        print(f"  识别价格：{box['value']}")

    # 分类（假设找到3个框）
    print(f"\n=== 分类分析 ===")

    manual_annotation = {
        'S2': 8.48,
        'current_price': 15.69,
        'R2': 17.58
    }

    if len(yellow_boxes) >= 3:
        # 按Y坐标排序
        sorted_boxes = sorted(yellow_boxes, key=lambda b: b['center_y'])

        # 最低的Y是S2
        # 中间的Y是现价
        # 最高的Y是R2

        classified = {
            'S2': sorted_boxes[0] if len(sorted_boxes) >= 1 else None,
            'current_price': sorted_boxes[1] if len(sorted_boxes) >= 2 else None,
            'R2': sorted_boxes[2] if len(sorted_boxes) >= 3 else None
        }

        for name, box in [('S2', classified['S2']), 
                         ('current_price', classified['current_price']),
                         ('R2', classified['R2'])]:
            if box:
                ocr_value = box['value']
                manual_value = manual_annotation[name]
                diff = abs(ocr_value - manual_value)

                print(f"\n{name}:")
                print(f"  OCR：{ocr_value}")
                print(f"  人工：{manual_value}")
                print(f"  误差：{diff:.2f}")

                if diff < 0.1:
                    print(f"  准确度：✓ 完全准确")
                elif diff < 0.5:
                    print(f"  准确度：✓ 非常准确")
                elif diff < 1.0:
                    print(f"  准确度：✓ 基本准确")
                else:
                    print(f"  准确度：✗ 不准确")
            else:
                print(f"\n{name}: 未识别到")
    else:
        print(f"\n黄色框数量不足3个，无法分类")

    # 保存结果
    result = {
        'image_path': test_image,
        'yellow_box_count': len(yellow_boxes),
        'yellow_boxes': yellow_boxes
    }

    output_file = "/root/.openclaw/workspace/yellow_box_wide_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n结果已保存到：{output_file}")


if __name__ == "__main__":
    main()
