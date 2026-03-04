#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析正确R2位置的edge_density
"""

import cv2
import numpy as np
import json

# 正确的R2 Y坐标
correct_r2_y = {
    '周线': 207,
    '日线': 306,
    '1小时': 445,
    '15分钟': 562,
    '5分钟': 225
}

# 5张图片
image_names = [
    ("9c5927d6-a315-4f12-9768-a9a2941aacfc.jpg", "周线"),
    ("437746cd-65be-4603-938c-85debf232d94.jpg", "日线"),
    ("19397363-b6cd-4344-93cc-870d7d872a83.jpg", "1小时"),
    ("7ce8ed01-8ac5-45c4-945c-e3b82dda8fe2.jpg", "15分钟"),
    ("6f492e6b-7b20-4356-b939-5b17422dadf2.jpg", "5分钟")
]

def calculate_edge_density(edges, y_center, line_length, chart_width):
    """Calculate edge density for a line"""
    roi_y_start = max(0, y_center - 3)
    roi_y_end = min(edges.shape[0], y_center + 4)
    roi = edges[roi_y_start:roi_y_end, :]
    
    edge_pixels_in_roi = int(np.sum(roi > 0))
    roi_area = (roi_y_end - roi_y_start) * chart_width
    edge_density = edge_pixels_in_roi / roi_area if roi_area > 0 else 0.0
    
    return edge_density

print("=" * 80)
print("正确R2位置的edge_density分析")
print("=" * 80)

results = []

for image_name, period in image_names:
    image_path = f"/root/.openclaw/media/inbound/{image_name}"
    
    # Read image
    image = cv2.imread(image_path)
    height, width = image.shape[:2]
    main_chart = image[0:int(height*0.45), :]
    main_chart_height = main_chart.shape[0]
    
    # Edge detection
    gray = cv2.cvtColor(main_chart, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 30, 100, apertureSize=3)
    
    # Hough detection
    lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=10,
                           minLineLength=100, maxLineGap=100)
    
    # Correct R2 Y
    r2_y = correct_r2_y[period]
    
    # Calculate edge density at correct R2 position
    # First, find the actual line length at this position
    nearby_lines = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(y1 - y2) <= 5:
                y_center = int((y1 + y2) / 2)
                if abs(y_center - r2_y) <= 5:
                    line_length = abs(x2 - x1)
                    nearby_lines.append(line_length)
    
    avg_line_length = sum(nearby_lines) / len(nearby_lines) if nearby_lines else 500
    edge_density = calculate_edge_density(edges, r2_y, avg_line_length, width)
    
    print(f"\n{period}:")
    print(f"  Correct R2 Y: {r2_y}")
    print(f"  Nearby lines: {len(nearby_lines)}")
    if nearby_lines:
        print(f"  Line lengths: {sorted(nearby_lines, reverse=True)[:3]}")
        print(f"  Avg line length: {avg_line_length:.0f}")
    print(f"  Edge density: {edge_density:.3f}")
    
    results.append({
        'period': period,
        'correct_y': r2_y,
        'nearby_lines_count': len(nearby_lines),
        'avg_line_length': avg_line_length,
        'edge_density': edge_density
    })

# Summary
print("\n" + "=" * 80)
print("Summary")
print("=" * 80)

print(f"\nPeriod\tCorrect Y\tEdge Density\tAvg Length")
for r in results:
    print(f"{r['period']}\t{r['correct_y']}\t\t{r['edge_density']:.3f}\t\t{r['avg_line_length']:.0f}")

# Compare with V10 results
print("\n" + "=" * 80)
print("V10 Detected vs Correct R2")
print("=" * 80)

v10_results = {
    '周线': {'detected_y': 128, 'edge_density': 0.093},
    '日线': {'detected_y': 128, 'edge_density': 0.091},
    '1小时': {'detected_y': 382, 'edge_density': 0.048},
    '15分钟': {'detected_y': 128, 'edge_density': 0.091},
    '5分钟': {'detected_y': 289, 'edge_density': 0.033}
}

print(f"\nPeriod\tDetected Y\tEdge Density\tCorrect Y\tEdge Density\tDiff")
for r in results:
    period = r['period']
    v10 = v10_results[period]
    diff_y = abs(v10['detected_y'] - r['correct_y'])
    diff_density = abs(v10['edge_density'] - r['edge_density'])
    print(f"{period}\t{v10['detected_y']}\t\t{v10['edge_density']:.3f}\t\t{r['correct_y']}\t{r['edge_density']:.3f}\t\t{diff_y}")

print("=" * 80)
