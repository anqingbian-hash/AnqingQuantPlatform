#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze R2 line pixel distribution
"""

import cv2
import numpy as np
import os
import matplotlib.pyplot as plt

# 人工标注的R2 Y坐标（根据memory）
manual_r2_y = {
    '周线': 490,
    '日线': 296,
    '1小时': 514,
    '15分钟': 542,
    '5分钟': 279
}

# 分析一张图片（周线）
image_path = "/root/.openclaw/media/inbound/9c5927d6-a315-4f12-9768-a9a2941aacfc.jpg"
period = '周线'

print(f"Analyzing {period} R2 line...")
print(f"Manual R2 Y: {manual_r2_y[period]}")

# Read image
image = cv2.imread(image_path)
if image is None:
    print("Cannot read image")
    exit(1)

height, width = image.shape[:2]
main_chart_height = int(height * 0.45)
main_chart = image[0:main_chart_height, :]

print(f"Image size: {width}x{height}")
print(f"Main chart height: {main_chart_height}")

# 提取R2线附近像素
r2_y = manual_r2_y[period] - 0  # 转换为主图坐标（已在主图区域）
margin = 5  # 上下各5像素

roi = main_chart[max(0, r2_y-margin):min(main_chart_height, r2_y+margin+1), :]
print(f"ROI shape: {roi.shape}")

# 计算颜色统计
mean_color = np.mean(roi, axis=(0, 1))
std_color = np.std(roi, axis=(0, 1))
median_color = np.median(roi, axis=(0, 1))

print(f"\nR2 Line Color Statistics:")
print(f"  Mean: BGR={mean_color}")
print(f"  Std: BGR={std_color}")
print(f"  Median: BGR={median_color}")
print(f"  Brightness: {np.mean(mean_color):.1f}")

# 分类颜色
b, g, r = mean_color
brightness = (b + g + r) / 3
max_diff = max(abs(b - g), abs(g - r), abs(b - r))

if brightness >= 220:
    color_category = 'white'
elif brightness >= 180:
    color_category = 'light_gray'
elif brightness >= 100:
    color_category = 'gray'
elif brightness >= 50:
    color_category = 'dark_gray'
else:
    color_category = 'black'

print(f"  Category: {color_category}")

# 保存ROI图片
cv2.imwrite("/tmp/r2_roi.jpg", roi)
print(f"\nROI saved to: /tmp/r2_roi.jpg")

# 保存完整图片，标记R2线
marked_image = image.copy()
cv2.line(marked_image, (0, r2_y), (width, r2_y), (0, 0, 255), 2)
cv2.imwrite("/tmp/r2_marked.jpg", marked_image)
print(f"Marked image saved to: /tmp/r2_marked.jpg")

# 统计全图颜色分布
print(f"\nFull Image Color Distribution:")
unique_colors = np.unique(image.reshape(-1, 3), axis=0)
print(f"  Total unique colors: {len(unique_colors)}")

# 统计主图区域颜色分布
print(f"\nMain Chart Color Distribution (sample):")
# 随机采样10000个像素
sample_indices = np.random.choice(main_chart.shape[0] * main_chart.shape[1], 10000, replace=False)
sample_pixels = main_chart.reshape(-1, 3)[sample_indices]

for i, pixel in enumerate(sample_pixels[:10]):
    b, g, r = pixel
    brightness = (b + g + r) / 3
    if brightness >= 220:
        cat = 'white'
    elif brightness >= 180:
        cat = 'light_gray'
    elif brightness >= 100:
        cat = 'gray'
    elif brightness >= 50:
        cat = 'dark_gray'
    else:
        cat = 'black'
    print(f"  {i+1}. BGR=({int(b)},{int(g)},{int(r)}), brightness={brightness:.0f}, {cat}")
