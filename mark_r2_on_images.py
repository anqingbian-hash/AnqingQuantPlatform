#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查图片内容，标记人工标注的R2位置
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

print("检查图片内容，标记人工标注的R2位置...")

for image_name, period in test_images:
    image_path = f"/root/.openclaw/media/inbound/{image_name}"
    output_path = f"/tmp/{image_name}"

    # Read image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Cannot read {image_name}")
        continue

    height, width = image.shape[:2]

    # 在人工标注位置画红线
    r2_y = manual_r2_y[period]
    cv2.line(image, (0, r2_y), (width, r2_y), (0, 0, 255), 3)  # 红色，3px宽

    # 添加文字
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image, f"Manual R2: {r2_y}", (10, r2_y - 10),
                font, 1, (0, 0, 255), 2)

    # 主图区域边界（黄色）
    main_chart_height = int(height * 0.45)
    cv2.line(image, (0, main_chart_height), (width, main_chart_height), (0, 255, 255), 1)
    cv2.putText(image, f"Main Chart: 0-{main_chart_height}", (10, main_chart_height - 5),
                font, 0.5, (0, 255, 255), 1)

    # 保存标记后的图片
    cv2.imwrite(output_path, image)
    print(f"✓ {period}: 保存到 {output_path}")

print("\n所有图片已标记并保存到 /tmp/")
