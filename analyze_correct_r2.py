#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析正确R2 Y坐标的颜色特征
"""

import cv2
import numpy as np
import os

# 正确的R2 Y坐标（来自y_price_mapping_final.json）
correct_r2_y = {
    '周线': 207,
    '日线': 306,
    '1小时': 445,
    '15分钟': 562,
    '5分钟': 225
}

# 5张图片
test_images = [
    ("9c5927d6-a315-4f12-9768-a9a2941aacfc.jpg", "周线"),
    ("437746cd-65be-4603-938c-85debf232d94.jpg", "日线"),
    ("19397363-b6cd-4344-93cc-870d7d872a83.jpg", "1小时"),
    ("7ce8ed01-8ac5-45c4-945c-e3b82dda8fe2.jpg", "15分钟"),
    ("6f492e6b-7b20-4356-b939-5b17422dadf2.jpg", "5分钟")
]

print("=" * 80)
print("正确R2 Y坐标的颜色特征分析")
print("=" * 80)

results = []

for image_name, period in test_images:
    image_path = f"/root/.openclaw/media/inbound/{image_name}"

    print(f"\n{period} - {image_name}")
    print(f"  正确R2 Y: {correct_r2_y[period]}")

    # Read image
    image = cv2.imread(image_path)
    if image is None:
        print(f"  ERROR: Cannot read image")
        continue

    height, width = image.shape[:2]
    main_chart_height = int(height * 0.45)

    # 检查Y是否在主图区域
    if correct_r2_y[period] >= main_chart_height:
        print(f"  ⚠️  WARNING: R2 Y is OUTSIDE main chart region")
        print(f"     Main chart height: {main_chart_height}")
        continue

    # 提取R2线附近像素
    margin = 5
    r2_y = correct_r2_y[period]
    roi = image[max(0, r2_y-margin):min(main_chart_height, r2_y+margin+1), :]

    # 计算颜色统计
    mean_color = np.mean(roi, axis=(0, 1))
    std_color = np.std(roi, axis=(0, 1))
    median_color = np.median(roi, axis=(0, 1))

    b, g, r = mean_color
    brightness = (b + g + r) / 3
    max_diff = max(abs(b - g), abs(g - r), abs(b - r))

    # 分类颜色
    if brightness <= 20:
        color_category = 'black'
    elif brightness <= 50:
        color_category = 'dark_gray'
    elif brightness <= 100:
        color_category = 'gray'
    elif brightness <= 180:
        color_category = 'light_gray'
    else:
        color_category = 'white'

    # 计算边缘数量
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    edges_roi = cv2.Canny(gray_roi, 30, 100, apertureSize=3)
    edge_count_roi = int(np.sum(edges_roi > 0))

    # 使用Hough检测R2线附近的水平线
    gray_main = cv2.cvtColor(image[0:main_chart_height, :], cv2.COLOR_BGR2GRAY)
    edges_main = cv2.Canny(gray_main, 30, 100, apertureSize=3)

    lines = cv2.HoughLinesP(edges_main, rho=1, theta=np.pi/180, threshold=10,
                           minLineLength=100, maxLineGap=100)

    nearby_lines = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(y1 - y2) <= 5:  # 水平线
                y_center = int((y1 + y2) / 2)
                if abs(y_center - r2_y) <= 10:
                    line_length = abs(x2 - x1)
                    nearby_lines.append({
                        'y': y_center,
                        'length': line_length,
                        'x1': x1,
                        'x2': x2
                    })

    print(f"  ROI: y={r2_y-margin} to {r2_y+margin} (height={roi.shape[0]})")
    print(f"  Mean BGR: [{b:.1f}, {g:.1f}, {r:.1f}]")
    print(f"  Std BGR: [{std_color[0]:.1f}, {std_color[1]:.1f}, {std_color[2]:.1f}]")
    print(f"  Median BGR: [{median_color[0]:.1f}, {median_color[1]:.1f}, {median_color[2]:.1f}]")
    print(f"  Brightness: {brightness:.1f}")
    print(f"  Color: {color_category}")
    print(f"  Edge pixels in ROI: {edge_count_roi}")
    print(f"  Hough检测到{len(nearby_lines)}条附近的水平线:")

    if nearby_lines:
        for i, line_info in enumerate(nearby_lines[:3], 1):
            print(f"    {i}. y={line_info['y']}, length={line_info['length']}")
    else:
        print(f"    无")

    results.append({
        'period': period,
        'r2_y': r2_y,
        'brightness': brightness,
        'color_category': color_category,
        'edge_count': edge_count_roi,
        'nearby_lines': len(nearby_lines)
    })

# 总结
print("\n" + "=" * 80)
print("总结")
print("=" * 80)

color_counts = {}
for r in results:
    cat = r['color_category']
    color_counts[cat] = color_counts.get(cat, 0) + 1

print(f"\n颜色分布:")
for cat, count in sorted(color_counts.items()):
    print(f"  {cat}: {count}")

print(f"\n详细结果:")
for r in results:
    print(f"  {r['period']}: y={r['r2_y']}, {r['color_category']}, brightness={r['brightness']:.1f}, edges={r['edge_count']}, nearby_lines={r['nearby_lines']}")
