#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
R2 Detection Summary - Progression
"""

v5_avg_error = 8.2
v6_avg_error = 8.0
v7_avg_error = 8.0
v8_avg_error = 7.8
v9_avg_error = 5.2

v5_accuracy = 0  # 0/5
v6_accuracy = 40  # 2/5
v7_accuracy = 40  # 2/5
v8_accuracy = 40  # 2/5
v9_accuracy = 60  # 3/5

print("=" * 80)
print("R2 Detection Progression Summary")
print("=" * 80)

print("\nAverage Error:")
print(f"  V5 (Color Agnostic): {v5_avg_error}%")
print(f"  V6 (Smart Selection): {v6_avg_error}%")
print(f"  V7 (Black Line Optimized): {v7_avg_error}%")
print(f"  V8 (Grid Line Avoidance): {v8_avg_error}%")
print(f"  V9 (Grid Line Detection): {v9_avg_error}%")

print("\nAccuracy (<5% error):")
print(f"  V5: {v5_accuracy}%")
print(f"  V6: {v6_accuracy}%")
print(f"  V7: {v7_accuracy}%")
print(f"  V8: {v8_accuracy}%")
print(f"  V9: {v9_accuracy}%")

print("\nKey Improvements:")
print("  - V5-V8: All selected grid lines (y=84-95)")
print("  - V9: Successfully avoided grid lines, but selected too-short lines")
print("\nV9 Problem:")
print("  - All candidates are short (100-200px)")
print("  - True R2 lines are medium length (300-900px)")
print("  - V9 penalized grid lines too heavily")

print("\nNext Step (V10):")
print("  - Reduce grid line penalty (0.4 -> 0.2)")
print("  - Increase line length weight (0.25 -> 0.35)")
print("  - Add edge density weight (new)")
print("  - Target: medium length lines (300-900px)")

print("=" * 80)
