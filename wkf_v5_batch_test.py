#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WKF Complete Analyzer V5 Batch Test
批量测试所有形态检测器
"""

import cv2
import numpy as np
import json
import os
from typing import Dict, List, Tuple
import sys

sys.path.append('/root/.openclaw/workspace')

# Import pattern detectors
from wkf_bc_pattern_detector import WKFBCPatternDetector
from wkf_sc_pattern_detector import WKFSCPatternDetector
from wkf_lps_pattern_detector import WKFLPSPatternDetector
from wkf_lpsy_pattern_detector import WKFLPSYPatternDetector


class NumpyEncoder(json.JSONEncoder):
    """Numpy type JSON encoder"""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int32, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def batch_analyze_all_periods():
    """Batch analyze all 5 periods with pattern detection"""
    
    # 5 images
    stock_images = [
        ("9c5927d6-a315-4f12-9768-a9a2941aacfc.jpg", "周线"),
        ("437746cd-65be-4603-938c-85debf232d94.jpg", "日线"),
        ("19397363-b6cd-4344-93cc-870d7d872a83.jpg", "1小时"),
        ("7ce8ed01-8ac5-45c4-945c-e3b82dda8fe2.jpg", "15分钟"),
        ("6f492e6b-7b20-4356-b939-5b17422dadf2.jpg", "5分钟")
    ]
    
    # Initialize pattern detectors
    print("[WKF V5] Initializing pattern detectors...")
    bc_detector = WKFBCPatternDetector()
    sc_detector = WKFSCPatternDetector()
    lps_detector = WKFLPSPatternDetector()
    lpsy_detector = WKFLPSYPatternDetector()
    print("[WKF V5] Pattern detectors initialized")
    
    print("=" * 80)
    print("WKF Complete Analyzer V5 - Batch Test")
    print("=" * 80)
    print("包含：BC/SC/LPS/LPSY形态检测")
    print("=" * 80)
    
    all_results = []
    
    for i, (image_name, period) in enumerate(stock_images, 1):
        image_path = f"/root/.openclaw/media/inbound/{image_name}"
        
        if not os.path.exists(image_path):
            print(f"\n[{i}/{len(stock_images)}] Image not found: {image_name}")
            continue
        
        print(f"\n{'='*80}")
        print(f"[{i}/{len(stock_images)}] {period} - {image_name}")
        print(f"{'='*80}")
        
        try:
            # Detect all patterns
            print("\n[1/4] Detecting BC Pattern...")
            bc_result = bc_detector.detect_bc_pattern(image_path)
            
            print("\n[2/4] Detecting SC Pattern...")
            sc_result = sc_detector.detect_sc_pattern(image_path)
            
            print("\n[3/4] Detecting LPS Pattern...")
            lps_result = lps_detector.detect_lps_pattern(image_path)
            
            print("\n[4/4] Detecting LPSY Pattern...")
            lpsy_result = lpsy_detector.detect_lpsy_pattern(image_path)
            
            # Enhanced judgment
            patterns_detected = {
                'bc': bc_result.get('detected', False),
                'sc': sc_result.get('detected', False),
                'lps': lps_result.get('detected', False),
                'lpsy': lpsy_result.get('detected', False)
            }
            
            top_patterns_count = sum([patterns_detected['bc'], patterns_detected['lpsy']])
            bottom_patterns_count = sum([patterns_detected['sc'], patterns_detected['lps']])
            
            # Generate signal
            if patterns_detected['bc']:
                enhanced_signal = 'wait'
                position_size = 4
                enhancement = 'BC形态：短期高点，注意回调，降低仓位到4%'
            elif patterns_detected['lpsy']:
                enhanced_signal = 'short'
                position_size = 0
                enhancement = 'LPSY形态：二卖位置，高抛参考'
            elif patterns_detected['lps']:
                enhanced_signal = 'long'
                position_size = 12
                enhancement = 'LPS形态：二买位置，低吸参考，仓位12%'
            elif patterns_detected['sc']:
                enhanced_signal = 'wait'
                position_size = 6
                enhancement = 'SC形态：短期低点，考虑反弹，仓位6%'
            else:
                enhanced_signal = 'wait'
                position_size = 8
                enhancement = '无形态增强，观望，仓位8%'
            
            result = {
                'success': True,
                'image_path': image_path,
                'image_name': image_name,
                'period': period,
                'bc_pattern': bc_result,
                'sc_pattern': sc_result,
                'lps_pattern': lps_result,
                'lpsy_pattern': lpsy_result,
                'patterns_detected': patterns_detected,
                'top_patterns_count': top_patterns_count,
                'bottom_patterns_count': bottom_patterns_count,
                'enhanced_signal': enhanced_signal,
                'position_size': position_size,
                'enhancement': enhancement
            }
            
            all_results.append(result)
            
            # Print summary
            print(f"\n{'='*80}")
            print(f"[{period}] Pattern Detection Summary")
            print(f"{'='*80}")
            print(f"BC: {'Detected' if bc_result.get('detected') else 'Not Detected'} ({bc_result.get('confidence', 0)}%)")
            print(f"SC: {'Detected' if sc_result.get('detected') else 'Not Detected'} ({sc_result.get('confidence', 0)}%)")
            print(f"LPS: {'Detected' if lps_result.get('detected') else 'Not Detected'} ({lps_result.get('confidence', 0)}%)")
            print(f"LPSY: {'Detected' if lpsy_result.get('detected') else 'Not Detected'} ({lpsy_result.get('confidence', 0)}%)")
            print(f"\nTop Patterns: {top_patterns_count}")
            print(f"Bottom Patterns: {bottom_patterns_count}")
            print(f"\nEnhanced Signal: {enhanced_signal}")
            print(f"Position Size: {position_size}%")
            print(f"Enhancement: {enhancement}")
            print(f"{'='*80}")
            
        except Exception as e:
            print(f"\n[ERROR] Analysis failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Save results
    output_file = "/root/.openclaw/workspace/wkf_v5_batch_test_results.json"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)
        print(f"\n{'='*80}")
        print(f"Results saved to: {output_file}")
        print(f"{'='*80}")
    except Exception as e:
        print(f"\nError saving results: {e}")
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"Batch Analysis Summary")
    print(f"{'='*80}")
    
    print(f"\nTotal images analyzed: {len(all_results)}")
    
    # Count phases
    signal_count = {}
    pattern_count = {}
    
    for result in all_results:
        signal = result.get('enhanced_signal', 'wait')
        signal_count[signal] = signal_count.get(signal, 0) + 1
        
        # Count patterns
        patterns_detected = result.get('patterns_detected', {})
        if patterns_detected.get('bc', False):
            pattern_count['bc'] = pattern_count.get('bc', 0) + 1
        if patterns_detected.get('sc', False):
            pattern_count['sc'] = pattern_count.get('sc', 0) + 1
        if patterns_detected.get('lps', False):
            pattern_count['lps'] = pattern_count.get('lps', 0) + 1
        if patterns_detected.get('lpsy', False):
            pattern_count['lpsy'] = pattern_count.get('lpsy', 0) + 1
    
    print(f"\nSignal Statistics:")
    for signal, count in sorted(signal_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {signal}: {count}张")
    
    print(f"\nPattern Statistics:")
    for pattern, count in sorted(pattern_count.items(), key=lambda x: x[1], reverse=True):
        pattern_cn = {
            'bc': 'BC（购买高潮）',
            'sc': 'SC（卖出密集区）',
            'lps': 'LPS（最后的支撑点）',
            'lpsy': 'LPSY（最后的供应点）'
        }.get(pattern, pattern)
        print(f"  {pattern_cn}: {count}张")
    
    print(f"\n{'='*80}")
    print(f"Batch Test Complete")
    print(f"{'='*80}")


if __name__ == "__main__":
    batch_analyze_all_periods()
