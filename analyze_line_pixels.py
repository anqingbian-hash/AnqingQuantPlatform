#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析图像中SR线和现价的实际像素值
"""

import cv2
import numpy as np
import json


def analyze_line_pixels(image_path: str):
    """分析SR线和现价的像素值"""

    # 读取图像
    image = cv2.imread(image_path)
    if image is None:
        print(f"无法读取图像：{image_path}")
        return

    height, width = image.shape[:2]
    print(f"图像尺寸：{width}x{height}")

    # 转换为HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 分割主图（上半部分）
    main_chart = image[:int(height * 0.45), :]

    main_hsv = hsv[:int(height * 0.45), :]
    main_height, main_width = main_chart.shape[:2]

    print(f"\n主图尺寸：{main_width}x{main_height}")

    # 根据人工标注，手动取样几个点
    # 假设S2在图像的某个y坐标附近（需要通过人工标注数据推断）

    # 创建一个简单的取样器，让用户点击查看像素值
    result = {
        'image_path': image_path,
        'image_size': {'width': width, 'height': height},
        'main_chart_size': {'width': main_width, 'height': main_height},
        'analysis_method': 'manual_sampling_needed'
    }

    # 方法1：查找所有水平线并统计颜色
    print("\n=== 方法1：查找所有水平线并统计颜色 ===")

    # 转换为灰度
    gray = cv2.cvtColor(main_chart, cv2.COLOR_BGR2GRAY)

    # 边缘检测
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # 霍夫变换
    lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=50,
                           minLineLength=200, maxLineGap=20)

    if lines is not None:
        # 筛选水平线
        horizontal_lines = []

        for line in lines:
            x1, y1, x2, y2 = line[0]

            # 检查角度
            angle = abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)

            if angle < 10 or angle > 170:
                horizontal_lines.append({
                    'x1': int(x1),
                    'y1': int(y1),
                    'x2': int(x2),
                    'y2': int(y2),
                    'y': int((y1 + y2) / 2),
                    'length': int(abs(x2 - x1))
                })

        # 按y坐标排序
        horizontal_lines.sort(key=lambda l: l['y'])

        print(f"找到 {len(horizontal_lines)} 条水平线")

        # 分析每条线的颜色
        line_colors = []

        for i, line in enumerate(horizontal_lines[:30]):  # 只分析前30条
            y = line['y']
            x = line['x1'] + line['length'] // 2

            if 0 <= x < main_width and 0 <= y < main_height:
                # 获取中心像素的BGR值
                bgr = main_chart[y, x]

                # 获取HSV值
                hsv_pixel = main_hsv[y, x]

                line_colors.append({
                    'line_index': i + 1,
                    'y': y,
                    'center_x': x,
                    'bgr': [int(bgr[0]), int(bgr[1]), int(bgr[2])],
                    'hsv': [int(hsv_pixel[0]), int(hsv_pixel[1]), int(hsv_pixel[2])]
                })

                print(f"线{i+1}: y={y}, 中心=({x},{y})")
                print(f"  BGR: {bgr}")
                print(f"  HSV: {hsv_pixel}")

        result['horizontal_lines'] = horizontal_lines[:30]
        result['line_colors'] = line_colors

    # 方法2：直接采样整个主图的像素值分布
    print("\n=== 方法2：采样主图像素值分布 ===")

    # 将主图reshape为像素列表
    pixels = main_chart.reshape(-1, 3)

    # 转换为HSV
    main_hsv_pixels = main_hsv.reshape(-1, 3)

    # 统计颜色分布
    bgr_ranges = {
        'red': {'count': 0, 'samples': []},
        'green': {'count': 0, 'samples': []},
        'yellow': {'count': 0, 'samples': []},
        'blue': {'count': 0, 'samples': []},
        'white': {'count': 0, 'samples': []}
    }

    for i, pixel in enumerate(pixels):
        b, g, r = pixel

        # 简单分类
        if r > 150 and g < 100 and b < 100:  # 红色
            bgr_ranges['red']['count'] += 1
            if len(bgr_ranges['red']['samples']) < 10:
                bgr_ranges['red']['samples'].append([int(b), int(g), int(r)])

        elif g > 150 and r < 100 and b < 100:  # 绿色
            bgr_ranges['green']['count'] += 1
            if len(bgr_ranges['green']['samples']) < 10:
                bgr_ranges['green']['samples'].append([int(b), int(g), int(r)])

        elif r > 200 and g > 200 and b < 100:  # 黄色
            bgr_ranges['yellow']['count'] += 1
            if len(bgr_ranges['yellow']['samples']) < 10:
                bgr_ranges['yellow']['samples'].append([int(b), int(g), int(r)])

        elif b > 150 and g < 100 and r < 100:  # 蓝色
            bgr_ranges['blue']['count'] += 1
            if len(bgr_ranges['blue']['samples']) < 10:
                bgr_ranges['blue']['samples'].append([int(b), int(g), int(r)])

        elif b > 200 and g > 200 and r > 200:  # 白色
            bgr_ranges['white']['count'] += 1
            if len(bgr_ranges['white']['samples']) < 10:
                bgr_ranges['white']['samples'].append([int(b), int(g), int(r)])

    total_pixels = len(pixels)

    print("\n颜色分布统计：")
    for color_name, data in bgr_ranges.items():
        count = data['count']
        percentage = (count / total_pixels) * 100
        samples = data['samples']

        print(f"\n{color_name}:")
        print(f"  像素数: {count}")
        print(f"  百分比: {percentage:.2f}%")

        if samples:
            print(f"  样本BGR值: {samples}")

    result['color_distribution'] = {
        color_name: {
            'count': data['count'],
            'percentage': round((data['count'] / total_pixels) * 100, 2),
            'samples': data['samples']
        }
        for color_name, data in bgr_ranges.items()
    }

    # 保存结果
    output_file = "/root/.openclaw/workspace/line_pixel_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n分析结果已保存到：{output_file}")

    # 提示下一步
    print("\n=== 下一步建议 ===")
    print("1. 查看line_colors中的水平线颜色，找出支撑线（绿色）和阻力线（红色）的BGR值")
    print("2. 调整color_thresholds参数，使用实际测量的BGR值")
    print("3. 根据颜色分布统计，优化颜色范围")


def main():
    """主函数"""
    import os

    test_image = "/root/.openclaw/media/inbound/92ea67d8-5897-401a-825a-63df2f39ee75.jpg"

    if os.path.exists(test_image):
        analyze_line_pixels(test_image)
    else:
        print(f"错误：图像不存在：{test_image}")


if __name__ == "__main__":
    main()
