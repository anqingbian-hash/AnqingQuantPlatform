#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析y=95（错误检测位置）的特征
"""

import cv2
import numpy as np

# 5张图片
test_images = [
    ("9c5927d6-a315-4f12-9768-a9a2941aacfc.jpg", "周线", 207),
    ("437746cd-65be-4603-938c-85debf232d94.jpg", "日线", 306),
    ("19397363-b6cd-4344-93cc-870d7d872a83.jpg", "1小时", 445),
    ("7ce8ed01-8ac5-45c4-945c-e3b82dda8fe2.jpg", "15分钟", 562),
    ("6f492e6b-7b20-4356-b939-5b17422dadf2.jpg", "5分钟", 225)
]

print("=" * 80)
print("y=95（错误检测位置）vs 正确R2位置的特征对比")
print("=" * 80)

for image_name, period, correct_r2_y in test_images:
    image_path = f"/root/.openclaw/media/inbound/{image_name}"

    # Read image
    image = cv2.imread(image_path)
    height, width = image.shape[:2]
    main_chart = image[0:int(height*0.45), :]

    # 分析y=95
    margin = 5
    y_wrong = 95

    roi_wrong = main_chart[max(0, y_wrong-margin):min(main_chart.shape[0], y_wrong+margin+1), :]
    mean_wrong = np.mean(roi_wrong, axis=(0, 1))
    brightness_wrong = np.mean(mean_wrong)

    # 分析正确R2 Y
    roi_correct = main_chart[max(0, correct_r2_y-margin):min(main_chart.shape[0], correct_r2_y+margin+1), :]
    mean_correct = np.mean(roi_correct, axis=(0, 1))
    brightness_correct = np.mean(mean_correct)

    # 分类颜色
    def classify_color(brightness):
        if brightness <= 20: return 'black'
        elif brightness <= 50: return 'dark_gray'
        elif brightness <= 100: return 'gray'
        elif brightness <= 180: return 'light_gray'
        else: return 'white'

    color_wrong = classify_color(brightness_wrong)
    color_correct = classify_color(brightness_correct)

    # 计算边缘
    gray_wrong = cv2.cvtColor(roi_wrong, cv2.COLOR_BGR2GRAY)
    edges_wrong = cv2.Canny(gray_wrong, 30, 100, apertureSize=3)
    edge_count_wrong = int(np.sum(edges_wrong > 0))

    gray_correct = cv2.cvtColor(roi_correct, cv2.COLOR_BGR2GRAY)
    edges_correct = cv2.Canny(gray_correct, 30, 100, apertureSize=3)
    edge_count_correct = int(np.sum(edges_correct > 0))

    # 霍夫检测水平线
    gray_main = cv2.cvtColor(main_chart, cv2.COLOR_BGR2GRAY)
    edges_main = cv2.Canny(gray_main, 30, 100, apertureSize=3)

    lines = cv2.HoughLinesP(edges_main, rho=1, theta=np.pi/180, threshold=10,
                           minLineLength=100, maxLineGap=100)

    # y=95附近的线条
    lines_wrong = []
    # 正确R2附近的线条
    lines_correct = []

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(y1 - y2) <= 5:
                y_center = int((y1 + y2) / 2)
                if abs(y_center - y_wrong) <= 10:
                    line_length = abs(x2 - x1)
                    lines_wrong.append(line_length)
                if abs(y_center - correct_r2_y) <= 10:
                    line_length = abs(x2 - x1)
                    lines_correct.append(line_length)

    max_length_wrong = max(lines_wrong) if lines_wrong else 0
    max_length_correct = max(lines_correct) if lines_correct else 0

    print(f"\n{period}:")
    print(f"  y=95 (错误): brightness={brightness_wrong:.1f}, color={color_wrong}, edges={edge_count_wrong}")
    print(f"    附近线条数: {len(lines_wrong)}, 最大长度: {max_length_wrong}")
    if lines_wrong:
        lines_wrong_sorted = sorted(lines_wrong, reverse=True)
        print(f"    Top 3线条长度: {lines_wrong_sorted[:3]}")

    print(f"  y={correct_r2_y} (正确): brightness={brightness_correct:.1f}, color={color_correct}, edges={edge_count_correct}")
    print(f"    附近线条数: {len(lines_correct)}, 最大长度: {max_length_correct}")
    if lines_correct:
        lines_correct_sorted = sorted(lines_correct, reverse=True)
        print(f"    Top 3线条长度: {lines_correct_sorted[:3]}")

print("\n" + "=" * 80)
