#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单WKF分析器 - 临时测试
"""

import cv2
import json
import os

from wkf_full_analyzer_fixed import WKFFullAnalyzerFixed

# 简单张图片测试
image_path = '/root/.openclaw/media/inbound/9c5927d6-a315-4f12-9768-a9a2941aacfc.jpg'

print("=" * 80)
print("WKF系统分析测试")
print("=" * 80)

analyzer = WKFFullAnalyzerFixed()

try:
    result = analyzer.analyze_image(image_path, 'weekly')
    print("\n" + "=" * 80)
    print("分析结果")
    print(f"  Phase: {result['wkf_judgment']['phase']}")
    print(f"  Signal: {result['recommendations']['trading_signal']}")
    print(f"  Position Size: {result['recommendations']['position_size']}%")
    print(f"  Risk Level: {result['recommendations']['risk_level']}")
    print(f"  Top Pattern: {result['recommendations'].get('risk_warning', [])}")

    if result['recommendations'].get('risk_warning'):
        print("\n  Risk Warning:")
        for warning in result['recommendations'].get('risk_warning', []):
            print(f"  {warning}")

    print()

except Exception as e:
    print(f"\n错误: {e}")
    import traceback
    traceback.print_exc()


if __name__ == "__main__":
    test_wkf_analyzer()
