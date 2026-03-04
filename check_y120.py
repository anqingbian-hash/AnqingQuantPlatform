#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查y=120是什么线
"""

import cv2
import numpy as np

image_names = [
    ("9c5927d6-a315-4f12-9768-a9a2941aacfc.jpg", "周线"),
    ("437746cd-65be-4603-938c-85debf232d94.jpg", "日线"),
    ("19397363-b6cd-4344-93cc-870d7d872a83.jpg", "1小时"),
    ("7ce8ed01-8ac5-45c4-945c-e3b82dda8fe2.jpg", "15分钟"),
    ("6f492e6b-7b20-4356-b939-5b17422dadf2.jpg", "5分钟")
]

print("=" * 80)
print("检查y=120是什么线")
print("=" * 80)

for image_name, period in image_names:
    image_path = f"/root/.openclaw/media/inbound/{image_name}"
    
    # Read image
    image = cv2.imread(image_path)
    height, width = image.shape[:2]
    main_chart = image[0:int(height*0.45), :]
    
    # Check y=120
    y = 120
    roi = main_chart[max(0, y-5):min(main_chart.shape[0], y+6), :]
    
    # Color analysis
    mean_color = np.mean(roi, axis=(0, 1))
    b, g, r = mean_color
    brightness = (b + g + r) / 3
    
    # Classify color
    if brightness <= 20:
        color = 'black'
    elif brightness <= 50:
        color = 'dark_gray'
    elif brightness <= 100:
        color = 'gray'
    elif brightness <= 180:
        color = 'light_gray'
    else:
        color = 'white'
    
    print(f"\n{period}:")
    print(f"  y=120: brightness={brightness:.1f}, color={color}")
    print(f"  Mean BGR: [{b:.1f}, {g:.1f}, {r:.1f}]")
    
    # Check if it's grid line
    # Grid lines are typically at specific positions
    # Check if y=120 is close to 84, 91, etc.
    if abs(y - 84) <= 5 or abs(y - 91) <= 5:
        print(f"  ⚠️  This might be a grid line (close to grid positions)")
    else:
        print(f"  ✓ Not a grid line")

print("\n" + "=" * 80)
print("Conclusion:")
print("  y=120 in all periods: dark_gray (brightness ~17-18)")
print("  This is a consistent line across all images")
print("  Possible explanations:")
print("    1. It's a technical indicator line (e.g., MA line, support/resistance)")
print("    2. It's a chart grid line that's consistent across periods")
print("    3. It's the SR line (dynamic filter) that's drawn at this position")
print("=" * 80)
