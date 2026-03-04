#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查周线y=207的候选情况
"""

import cv2
import numpy as np

image_path = "/root/.openclaw/media/inbound/9c5927d6-a315-4f12-9768-a9a2941aacfc.jpg"

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

# Check y=207
correct_y = 207
v10_detected_y = 129
v11_detected_y = 129

def calculate_edge_density(edges, y_center, line_length, chart_width):
    roi_y_start = max(0, y_center - 3)
    roi_y_end = min(edges.shape[0], y_center + 4)
    roi = edges[roi_y_start:roi_y_end, :]
    edge_pixels_in_roi = int(np.sum(roi > 0))
    roi_area = (roi_y_end - roi_y_start) * chart_width
    return edge_pixels_in_roi / roi_area if roi_area > 0 else 0.0

print("=" * 80)
print("周线：检查y=207 vs y=129的候选情况")
print("=" * 80)

# Find candidates near y=207 and y=129
candidates_207 = []
candidates_129 = []

if lines is not None:
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if abs(y1 - y2) <= 5:
            y_center = int((y1 + y2) / 2)
            
            if abs(y_center - correct_y) <= 10:
                line_length = abs(x2 - x1)
                edge_density = calculate_edge_density(edges, y_center, line_length, width)
                candidates_207.append({
                    'y': y_center,
                    'length': line_length,
                    'edge_density': edge_density
                })
            
            if abs(y_center - v11_detected_y) <= 10:
                line_length = abs(x2 - x1)
                edge_density = calculate_edge_density(edges, y_center, line_length, width)
                candidates_129.append({
                    'y': y_center,
                    'length': line_length,
                    'edge_density': edge_density
                })

print(f"\ny=207（正确R2位置）:")
print(f"  候选数: {len(candidates_207)}")
if candidates_207:
    sorted_207 = sorted(candidates_207, key=lambda x: x['edge_density'], reverse=True)
    print(f"  Top 5候选:")
    for i, c in enumerate(sorted_207[:5], 1):
        print(f"    {i}. y={c['y']}, length={c['length']}, edge_density={c['edge_density']:.3f}")
    print(f"  最佳: y={sorted_207[0]['y']}, edge_density={sorted_207[0]['edge_density']:.3f}")

print(f"\ny=129（V11检测位置）:")
print(f"  候选数: {len(candidates_129)}")
if candidates_129:
    sorted_129 = sorted(candidates_129, key=lambda x: x['edge_density'], reverse=True)
    print(f"  Top 5候选:")
    for i, c in enumerate(sorted_129[:5], 1):
        print(f"    {i}. y={c['y']}, length={c['length']}, edge_density={c['edge_density']:.3f}")
    print(f"  最佳: y={sorted_129[0]['y']}, edge_density={sorted_129[0]['edge_density']:.3f}")

# Compare
if candidates_207 and candidates_129:
    best_207 = sorted(candidates_207, key=lambda x: x['edge_density'], reverse=True)[0]
    best_129 = sorted(candidates_129, key=lambda x: x['edge_density'], reverse=True)[0]
    
    print(f"\n对比:")
    print(f"  y=207: edge_density={best_207['edge_density']:.3f}, length={best_207['length']}")
    print(f"  y=129: edge_density={best_129['edge_density']:.3f}, length={best_129['length']}")
    
    # Why V11 chose y=129 over y=207?
    # Check the length score
    if best_207['length'] < 300 or best_207['length'] > 1500:
        length_score_207 = 0.5
    elif 500 <= best_207['length'] <= 800:
        length_score_207 = 1.0
    else:
        length_score_207 = 0.8
    
    if best_129['length'] < 300 or best_129['length'] > 1500:
        length_score_129 = 0.5
    elif 500 <= best_129['length'] <= 800:
        length_score_129 = 1.0
    else:
        length_score_129 = 0.8
    
    print(f"\n长度评分:")
    print(f"  y=207: {length_score_207}")
    print(f"  y=129: {length_score_129}")
    
    print(f"\nV11综合评分 (edge_density*0.25 + length*0.30):")
    score_207 = best_207['edge_density'] * 0.25 + length_score_207 * 0.30
    score_129 = best_129['edge_density'] * 0.25 + length_score_129 * 0.30
    print(f"  y=207: {score_207:.3f}")
    print(f"  y=129: {score_129:.3f}")
    
    print(f"\n结论: y=129的长度评分更高，导致被选择")

print("=" * 80)
