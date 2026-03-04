#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析人工标注R2线的实际位置和特征
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

print("=" * 80)
print("人工标注R2线的实际位置和特征")
print("=" * 80)

for image_name, period in test_images:
    image_path = f"/root/.openclaw/media/inbound/{image_name}"

    print(f"\n{period} - {image_name}")
    print(f"  人工标注R2 Y: {manual_r2_y[period]}")

    # Read image
    image = cv2.imread(image_path)
    if image is None:
        print(f"  ERROR: Cannot read image")
        continue

    height, width = image.shape[:2]
    main_chart_height = int(height * 0.45)
    print(f"  Image size: {width}x{height}")
    print(f"  Main chart height: {main_chart_height}")

    # 检查标注Y是否在主图区域
    if manual_r2_y[period] >= main_chart_height:
        print(f"  ⚠️  WARNING: Manual R2 Y ({manual_r2_y[period]}) is OUTSIDE main chart region (max: {main_chart_height-1})")
        # 可能标注的是全局坐标，而不是主图区域内的坐标
        relative_y = manual_r2_y[period] - main_chart_height
        print(f"  Relative Y in main chart: {relative_y}")
        if relative_y < 0:
            print(f"  ⚠️  This is negative! The annotation might be for a different region.")
    else:
        print(f"  ✓ Manual R2 Y is INSIDE main chart region")

    # 提取标注线附近像素
    margin = 5
    roi_y_start = max(0, manual_r2_y[period] - margin)
    roi_y_end = min(height, manual_r2_y[period] + margin + 1)
    roi = image[roi_y_start:roi_y_end, :]

    # 计算颜色统计
    mean_color = np.mean(roi, axis=(0, 1))
    std_color = np.std(roi, axis=(0, 1))
    median_color = np.median(roi, axis=(0, 1))

    b, g, r = mean_color
    brightness = (b + g + r) / 3

    # 计算ROI的边缘数量
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    edges_roi = cv2.Canny(gray_roi, 30, 100, apertureSize=3)
    edge_count_roi = int(np.sum(edges_roi > 0))

    print(f"  ROI: y={roi_y_start} to {roi_y_end} (height={roi.shape[0]})")
    print(f"  Mean BGR: [{b:.1f}, {g:.1f}, {r:.1f}]")
    print(f"  Std BGR: [{std_color[0]:.1f}, {std_color[1]:.1f}, {std_color[2]:.1f}]")
    print(f"  Median BGR: [{median_color[0]:.1f}, {median_color[1]:.1f}, {median_color[2]:.1f}]")
    print(f"  Brightness: {brightness:.1f}")
    print(f"  Edge pixels in ROI: {edge_count_roi}")

    # 尝试用霍夫变换检测标注线附近
    gray = cv2.cvtColor(image[0:main_chart_height, :], cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 30, 100, apertureSize=3)

    # 检测标注Y附近的水平线
    # 使用HoughLinesP，但限制ROI
    lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=10,
                           minLineLength=100, maxLineGap=100)

    if lines is not None:
        # 统计标注Y附近（±10px）的线条
        nearby_lines = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(y1 - y2) <= 5:  # 水平线
                y_center = int((y1 + y2) / 2)
                if abs(y_center - manual_r2_y[period]) <= 10:
                    line_length = abs(x2 - x1)
                    nearby_lines.append({
                        'y': y_center,
                        'length': line_length,
                        'x1': x1,
                        'x2': x2
                    })

        if nearby_lines:
            print(f"  Hough检测到{len(nearby_lines)}条附近的水平线:")
            for i, line_info in enumerate(nearby_lines[:3], 1):
                print(f"    {i}. y={line_info['y']}, length={line_info['length']}")
        else:
            print(f"  Hough未检测到附近的水平线")

print("\n" + "=" * 80)
