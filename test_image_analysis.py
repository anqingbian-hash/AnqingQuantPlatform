#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试图像颜色和区域定位
"""

import cv2
import numpy as np
import json
from typing import Dict, List, Tuple


def analyze_image_colors(image_path: str):
    """分析图像中的颜色分布"""

    # 读取图像
    image = cv2.imread(image_path)
    if image is None:
        print(f"无法读取图像：{image_path}")
        return

    height, width = image.shape[:2]
    print(f"\n图像尺寸：{width}x{height}")

    # 转换为HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 定义颜色范围（基于OpenCV标准）
    color_ranges = {
        '红色': {
            'hsv_ranges': [(0, 120, 70), (10, 255, 255), (170, 120, 70), (180, 255, 255)],
            'display_color': (0, 0, 255)
        },
        '绿色': {
            'hsv_ranges': [(40, 50, 50), (80, 255, 255)],
            'display_color': (0, 255, 0)
        },
        '黄色': {
            'hsv_ranges': [(20, 100, 100), (30, 255, 255)],
            'display_color': (0, 255, 255)
        },
        '蓝色': {
            'hsv_ranges': [(100, 100, 100), (130, 255, 255)],
            'display_color': (255, 0, 0)
        },
        '青色': {
            'hsv_ranges': [(80, 100, 100), (100, 255, 255)],
            'display_color': (255, 255, 0)
        },
        '白色': {
            'hsv_ranges': [(0, 0, 200), (180, 30, 255)],
            'display_color': (255, 255, 255)
        },
        '黑色': {
            'hsv_ranges': [(0, 0, 0), (180, 255, 50)],
            'display_color': (0, 0, 0)
        }
    }

    print("\n=== 颜色分析 ===")

    results = {}

    for color_name, color_info in color_ranges.items():
        ranges = color_info['hsv_ranges']

        # 创建掩码
        if len(ranges) == 4:  # 红色有两个范围
            lower1, upper1, lower2, upper2 = [np.array(r) for r in ranges]
            mask1 = cv2.inRange(hsv, lower1, upper1)
            mask2 = cv2.inRange(hsv, lower2, upper2)
            mask = cv2.bitwise_or(mask1, mask2)
        else:
            lower, upper = [np.array(r) for r in ranges]
            mask = cv2.inRange(hsv, lower, upper)

        # 统计像素数量
        pixel_count = cv2.countNonZero(mask)
        percentage = (pixel_count / (width * height)) * 100

        results[color_name] = {
            'pixel_count': int(pixel_count),
            'percentage': round(percentage, 2)
        }

        print(f"{color_name}：{pixel_count} 像素（{percentage:.2f}%）")

    # 保存结果
    output_file = "/root/.openclaw/workspace/image_color_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n结果已保存到：{output_file}")

    # 可视化特定区域
    print("\n=== 区域分析 ===")

    # 主图区域（上半部分）
    main_chart_y = int(height * 0.45)
    main_chart = image[:main_chart_y, :]
    print(f"主图区域：0 - {main_chart_y}行")

    # 净量副图区域（中间部分）
    net_volume_start_y = int(height * 0.45)
    net_volume_end_y = int(height * 0.72)
    net_volume_chart = image[net_volume_start_y:net_volume_end_y, :]
    print(f"净量副图区域：{net_volume_start_y} - {net_volume_end_y}行")

    # DELTA副图区域（下半部分）
    delta_chart = image[net_volume_end_y:, :]
    print(f"DELTA副图区域：{net_volume_end_y} - {height}行")

    # 保存分割后的图像用于分析
    cv2.imwrite("/root/.openclaw/workspace/debug_main_chart.jpg", main_chart)
    cv2.imwrite("/root/.openclaw/workspace/debug_net_volume.jpg", net_volume_chart)
    cv2.imwrite("/root/.openclaw/workspace/debug_delta_chart.jpg", delta_chart)

    print("\n分割图像已保存")


def analyze_horizontal_lines(image_path: str):
    """分析水平线"""

    # 读取图像
    image = cv2.imread(image_path)
    if image is None:
        print(f"无法读取图像：{image_path}")
        return

    height, width = image.shape[:2]

    # 转换为灰度
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 边缘检测
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # 霍夫变换检测直线
    lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=100,
                           minLineLength=100, maxLineGap=10)

    if lines is not None:
        horizontal_lines = []

        for line in lines:
            x1, y1, x2, y2 = line[0]

            # 检查是否是水平线（y1和y2接近）
            if abs(y1 - y2) < 5:
                horizontal_lines.append((x1, y1, x2, y2))

        print(f"\n找到 {len(horizontal_lines)} 条水平线")

        # 按y坐标排序
        horizontal_lines.sort(key=lambda l: l[1])

        # 打印前20条
        for i, line in enumerate(horizontal_lines[:20]):
            x1, y1, x2, y2 = line
            print(f"  线{i+1}: y={y1}, x={x1}-{x2}")

        # 保存结果
        results = [list(line) for line in horizontal_lines]
        output_file = "/root/.openclaw/workspace/horizontal_lines.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n结果已保存到：{output_file}")


def main():
    """主函数"""
    import os

    test_image = "/root/.openclaw/media/inbound/0c4062f0-7feb-4f68-a145-5a36a5d54e1c.jpg"

    if os.path.exists(test_image):
        # 1. 分析颜色
        analyze_image_colors(test_image)

        # 2. 分析水平线
        analyze_horizontal_lines(test_image)
    else:
        print(f"错误：图像不存在：{test_image}")


if __name__ == "__main__":
    main()
