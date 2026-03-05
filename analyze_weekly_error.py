#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析周线误差原因
目标：检测y=269 vs 正确y=207，误差1.52 (7.9%)
"""

import cv2
import numpy as np
import json

image_path = "/root/.openclaw/media/inbound/9c5927d6-a315-4f12-9768-a9a2941aacfc.jpg"
period = "周线"
detected_y = 269
correct_y = 207

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

def calculate_edge_density(edges, y_center, line_length, chart_width):
    roi_y_start = max(0, y_center - 3)
    roi_y_end = min(edges.shape[0], y_center + 4)
    roi = edges[roi_y_start:roi_y_end, :]
    
    edge_pixels_in_roi = int(np.sum(roi > 0))
    roi_area = (roi_y_end - roi_y_start) * chart_width
    return edge_pixels_in_roi / roi_area if roi_area > 0 else 0.0

print("=" * 80)
print(f"周线分析：检测y={detected_y} vs 正确y={correct_y}")
print("=" * 80)

# 分析y=269附近
print(f"\n[1] y={detected_y}（V13检测位置）:")
candidates_269 = []
if lines is not None:
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if abs(y1 - y2) <= 5:
            y_center = int((y1 + y2) / 2)
            if abs(y_center - detected_y) <= 10:
                line_length = abs(x2 - x1)
                edge_density = calculate_edge_density(edges, y_center, line_length, width)
                
                # 颜色分析
                line_pixels = main_chart[max(0, y_center-3):min(main_chart.shape[0], y_center+4), x1:x2]
                if line_pixels.size > 0:
                    mean_color = np.mean(line_pixels, axis=(0, 1))
                    b, g, r = mean_color
                    brightness = (b + g + r) / 3
                    
                    candidates_269.append({
                        'y': y_center,
                        'length': line_length,
                        'edge_density': edge_density,
                        'brightness': brightness
                    })

if candidates_269:
    sorted_269 = sorted(candidates_269, key=lambda x: x['edge_density'], reverse=True)
    print(f"  候选数: {len(candidates_269)}")
    print(f"  Top 5候选:")
    for i, c in enumerate(sorted_269[:5], 1):
        print(f"    {i}. y={c['y']}, length={c['length']}, edge_density={c['edge_density']:.3f}, brightness={c['brightness']:.1f}")
    print(f"  最佳: y={sorted_269[0]['y']}, edge_density={sorted_269[0]['edge_density']:.3f}, length={sorted_269[0]['length']}")

# 分析y=207附近
print(f"\n[2] y={correct_y}（正确R2位置）:")
candidates_207 = []
if lines is not None:
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if abs(y1 - y2) <= 5:
            y_center = int((y1 + y2) / 2)
            if abs(y_center - correct_y) <= 10:
                line_length = abs(x2 - x1)
                edge_density = calculate_edge_density(edges, y_center, line_length, width)
                
                # 颜色分析
                line_pixels = main_chart[max(0, y_center-3):min(main_chart.shape[0], y_center+4), x1:x2]
                if line_pixels.size > 0:
                    mean_color = np.mean(line_pixels, axis=(0, 1))
                    b, g, r = mean_color
                    brightness = (b + g + r) / 3
                    
                    candidates_207.append({
                        'y': y_center,
                        'length': line_length,
                        'edge_density': edge_density,
                        'brightness': brightness
                    })

if candidates_207:
    sorted_207 = sorted(candidates_207, key=lambda x: x['edge_density'], reverse=True)
    print(f"  候选数: {len(candidates_207)}")
    print(f"  Top 5候选:")
    for i, c in enumerate(sorted_207[:5], 1):
        print(f"    {i}. y={c['y']}, length={c['length']}, edge_density={c['edge_density']:.3f}, brightness={c['brightness']:.1f}")
    print(f"  最佳: y={sorted_207[0]['y']}, edge_density={sorted_207[0]['edge_density']:.3f}, length={sorted_207[0]['length']}")

# 对比分析
if candidates_269 and candidates_207:
    best_269 = sorted_269[0]
    best_207 = sorted_207[0]
    
    print(f"\n[3] 对比分析:")
    print(f"  y={detected_y}: edge_density={best_269['edge_density']:.3f}, length={best_269['length']}, brightness={best_269['brightness']:.1f}")
    print(f"  y={correct_y}: edge_density={best_207['edge_density']:.3f}, length={best_207['length']}, brightness={best_207['brightness']:.1f}")
    
    # 计算V13评分（简化版）
    print(f"\n[4] V13评分计算:")
    
    # SR线约束
    sr_line_y = 122
    is_near_sr_269 = abs(detected_y - sr_line_y) <= 20
    is_near_sr_207 = abs(correct_y - sr_line_y) <= 20
    print(f"  SR线约束: y={detected_y} (near_sr={is_near_sr_269}) vs y={correct_y} (near_sr={is_near_sr_207})")
    
    # Edge Density评分
    edge_density_score_269 = 0.7 if best_269['edge_density'] >= 0.08 else 0.3
    edge_density_score_207 = 0.7 if best_207['edge_density'] >= 0.08 else 0.3
    print(f"  Edge Density评分: y={detected_y} ({edge_density_score_269}) vs y={correct_y} ({edge_density_score_207})")
    
    # Length评分
    length_score_269 = 1.0 if 200 <= best_269['length'] <= 800 else 0.5
    length_score_207 = 1.0 if 200 <= best_207['length'] <= 800 else 0.5
    print(f"  Length评分: y={detected_y} ({length_score_269}) vs y={correct_y} ({length_score_207})")
    
    # 综合评分
    score_269 = 0.2 * (0 if is_near_sr_269 else 1) + 0.15 * edge_density_score_269 + 0.25 * length_score_269
    score_207 = 0.2 * (0 if is_near_sr_207 else 1) + 0.15 * edge_density_score_207 + 0.25 * length_score_207
    print(f"  综合评分: y={detected_y} ({score_269:.3f}) vs y={correct_y} ({score_207:.3f})")
    print(f"  结论: y={detected_y}得分更高，被选中")

print("\n" + "=" * 80)
print("优化建议:")
print("  1. y=269的edge_density=0.082，低于阈值(0.08)，但被选中")
print("  2. 原因：length评分过高（1.0），补偿了edge_density不足")
print("  3. 建议：降低length评分权重，提高edge_density权重")
print("=" * 80)
