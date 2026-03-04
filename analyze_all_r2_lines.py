#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze all 5 R2 lines
"""

import cv2
import numpy as np
import os

# 人工标注的R2 Y坐标（根据memory）
manual_r2_y = {
    '周线': 490,
    '日线': 296,
    '1小时': 514,
    '15分钟': 542,
    '5分钟': 279
}

# 5张图片
test_images = [
    ("9c5927d6-a315-4f12-9768-a9a2941aacfc.jpg", "周线"),
    ("437746cd-65be-4603-938c-85debf232d94.jpg", "日线"),
    ("19397363-b6cd-4344-93cc-870d7d872a83.jpg", "1小时"),
    ("7ce8ed01-8ac5-45c4-945c-e3b82dda8fe2.jpg", "15分钟"),
    ("6f492e6b-7b20-4356-b939-5b17422dadf2.jpg", "5分钟")
]

margin = 5  # 上下各5像素

print("=" * 80)
print("All 5 R2 Lines Color Analysis")
print("=" * 80)

results = []

for image_name, period in test_images:
    image_path = f"/root/.openclaw/media/inbound/{image_name}"

    print(f"\n{period} - {image_name}")
    print(f"  Manual R2 Y: {manual_r2_y[period]}")

    # Read image
    image = cv2.imread(image_path)
    if image is None:
        print(f"  ERROR: Cannot read image")
        continue

    height, width = image.shape[:2]
    main_chart_height = int(height * 0.45)
    main_chart = image[0:main_chart_height, :]

    # 提取R2线附近像素
    r2_y = manual_r2_y[period] - 0  # 转换为主图坐标
    roi = main_chart[max(0, r2_y-margin):min(main_chart_height, r2_y+margin+1), :]

    # 计算颜色统计
    mean_color = np.mean(roi, axis=(0, 1))
    median_color = np.median(roi, axis=(0, 1))

    b, g, r = mean_color
    brightness = (b + g + r) / 3
    max_diff = max(abs(b - g), abs(g - r), abs(b - r))

    # 分类颜色
    if brightness >= 220 and max_diff < 30:
        color_category = 'white'
    elif brightness >= 180:
        color_category = 'light_gray'
    elif brightness >= 100:
        color_category = 'gray'
    elif brightness >= 50:
        color_category = 'dark_gray'
    else:
        color_category = 'black'

    print(f"  Mean BGR: [{b:.1f}, {g:.1f}, {r:.1f}]")
    print(f"  Median BGR: [{median_color[0]:.1f}, {median_color[1]:.1f}, {median_color[2]:.1f}]")
    print(f"  Brightness: {brightness:.1f}")
    print(f"  Category: {color_category}")

    results.append({
        'period': period,
        'r2_y': r2_y,
        'mean_color': [float(b), float(g), float(r)],
        'brightness': float(brightness),
        'color_category': color_category
    })

# 总结
print("\n" + "=" * 80)
print("Summary")
print("=" * 80)

color_counts = {}
for r in results:
    cat = r['color_category']
    color_counts[cat] = color_counts.get(cat, 0) + 1

print(f"\nColor Distribution:")
for cat, count in sorted(color_counts.items()):
    print(f"  {cat}: {count}")

print(f"\nDetailed Results:")
for r in results:
    print(f"  {r['period']}: {r['color_category']} (brightness={r['brightness']:.1f})")
