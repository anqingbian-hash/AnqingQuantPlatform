#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查图片的颜色分布
"""

import cv2
import numpy as np
import json


def analyze_color_distribution(image_path: str):
    """分析图片颜色分布"""

    # 读取图像
    image = cv2.imread(image_path)
    if image is None:
        print(f"无法读取图像：{image_path}")
        return

    height, width = image.shape[:2]
    print(f"图像尺寸：{width}x{height}")

    # 转换为HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 定义测试颜色范围
    test_colors = {
        '红色范围1（标准)': {
            'lower': np.array([0, 100, 100]),
            'upper': np.array([10, 255, 255])
        },
        '红色范围2（暗红)': {
            'lower': np.array([0, 50, 50]),
            'upper': np.array([10, 255, 255])
        },
        '红色范围3（淡红)': {
            'lower': np.array([0, 30, 50]),
            'upper': np.array([10, 255, 255])
        },
        '绿色范围1（标准)': {
            'lower': np.array([40, 50, 50]),
            'upper': np.array([80, 255, 255])
        },
        '绿色范围2（暗绿)': {
            'lower': np.array([30, 30, 30]),
            'upper': np.array([80, 255, 255])
        },
        '黄色范围1（标准)': {
            'lower': np.array([20, 100, 100]),
            'upper': np.array([30, 255, 255])
        },
        '黄色范围2（淡黄)': {
            'lower': np.array([15, 50, 50]),
            'upper': np.array([35, 255, 255])
        },
        '黄色范围3（宽黄)': {
            'lower': np.array([10, 30, 30]),
            'upper': np.array([40, 255, 255])
        },
        '白色范围（零轴)': {
            'lower': np.array([0, 0, 200]),
            'upper': np.array([180, 50, 255])
        },
        '黑色范围（背景)': {
            'lower': np.array([0, 0, 0]),
            'upper': np.array([180, 255, 50])
        },
        '淡紫色范围（阻力线）': {
            'lower': np.array([0, 50, 100]),
            'upper': np.array([20, 255, 200])
        },
    }

    print("\n=== 颜色范围分析 ===")

    result = {
        'image_path': image_path,
        'color_distribution': {}
    }

    for color_name, range_def in test_colors.items():
        lower = range_def['lower']
        upper = range_def['upper']

        # 创建掩码
        mask = cv2.inRange(hsv, lower, upper)

        # 统计像素
        pixel_count = cv2.countNonZero(mask)
        percentage = (pixel_count / (width * height)) * 100

        print(f"\n{color_name}:")
        print(f"  像素数: {pixel_count}")
        print(f"  百分比: {percentage:.2f}%")

        result['color_distribution'][color_name] = {
            'pixel_count': int(pixel_count),
            'percentage': round(percentage, 2)
        }

    # 保存结果
    output_file = "/root/.openclaw/workspace/color_distribution_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n分析结果已保存到：{output_file}")


def main():
    """主函数"""
    import os

    # 测试图片
    test_image = "/root/.openclaw/media/inbound/57337644-f52c-499d-825f-b3cc39322832.jpg"

    if os.path.exists(test_image):
        analyze_color_distribution(test_image)
    else:
        print(f"错误：图像不存在：{test_image}")


if __name__ == "__main__":
    main()
