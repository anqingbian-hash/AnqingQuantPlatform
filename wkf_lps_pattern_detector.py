#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WKF LPS (Last Point of Support) Pattern Detector
LPS（最后的支撑点）- 二买位置，低吸参考
"""

import cv2
import numpy as np
import json
import os
from typing import Dict, List, Tuple

class WKFLPSPatternDetector:
    """LPS (Last Point of Support) Pattern Detector"""
    
    def __init__(self):
        """Initialize detector"""
        self.regions = {
            'main_chart': (0, int(1377 * 0.45)),
            'net_volume': (int(1377 * 0.45), int(1377 * 0.72)),
            'delta': (int(1377 * 0.72), 1377)
        }
        
        # Color thresholds
        self.color_thresholds = {
            'support_line_yellow': {
                'lower': np.array([20, 60, 150]),
                'upper': np.array([60, 200, 200])
            },
            'current_price': {
                'lower': np.array([50, 80, 210]),
                'upper': np.array([80, 215, 215])
            },
            'net_volume_long': {
                'lower': np.array([150, 150, 150]),
                'upper': np.array([255, 255, 255])
            },
            'net_volume_short': {
                'lower': np.array([0, 100, 0]),
                'upper': np.array([100, 255, 100])
            }
        }
    
    def detect_lps_pattern(self, image_path: str) -> Dict:
        """Detect LPS (Last Point of Support) pattern"""
        print(f"\n[LPS Pattern Detection] Analyzing: {os.path.basename(image_path)}")
        
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            return {
                'success': False,
                'error': 'Cannot read image',
                'detected': False,
                'pattern': 'lps',
                'confidence': 0,
                'description': 'LPS（最后的支撑点），二买位置，低吸参考 - 无法读取图片'
            }
        
        height, width = image.shape[:2]
        main_chart = image[self.regions['main_chart'][0]:self.regions['main_chart'][1], :]
        net_volume = image[self.regions['net_volume'][0]:self.regions['net_volume'][1], :]
        delta = image[self.regions['delta'][0]:self.regions['delta'][1], :]
        
        # Analyze components
        print("  [1] Analyzing price structure...")
        price_analysis = self._analyze_price_structure(main_chart, width, height)
        
        print("  [2] Analyzing net volume...")
        net_volume_analysis = self._analyze_net_volume(net_volume, width, height)
        
        print("  [3] Analyzing DELTA...")
        delta_analysis = self._analyze_delta(delta, width, height)
        
        # Detect LPS pattern
        print("  [4] Detecting LPS pattern...")
        lps_result = self._detect_lps(price_analysis, net_volume_analysis, delta_analysis)
        
        return {
            'success': True,
            'image_path': image_path,
            'image_name': os.path.basename(image_path),
            'pattern': 'lps',
            'price_analysis': price_analysis,
            'net_volume_analysis': net_volume_analysis,
            'delta_analysis': delta_analysis,
            **lps_result
        }
    
    def _analyze_price_structure(self, main_chart: np.ndarray, width: int, height: int) -> Dict:
        """Analyze price structure for LPS pattern"""
        # Detect support line (yellow)
        support_mask = cv2.inRange(main_chart, 
                                   self.color_thresholds['support_line_yellow']['lower'],
                                   self.color_thresholds['support_line_yellow']['upper'])
        
        # Find the strongest horizontal yellow line
        row_counts = np.sum(support_mask, axis=1)
        
        if np.max(row_counts) > 100:
            support_y = int(np.argmax(row_counts))
            support_strength = int(row_counts[support_y])
        else:
            support_y = None
            support_strength = 0
        
        # Detect current price line
        current_price_mask = cv2.inRange(main_chart, 
                                       self.color_thresholds['current_price']['lower'],
                                       self.color_thresholds['current_price']['upper'])
        
        row_counts = np.sum(current_price_mask, axis=1)
        
        if np.max(row_counts) > 50:
            current_price_y = int(np.argmax(row_counts))
        else:
            current_price_y = None
        
        # Calculate stabilization (price above support line)
        if support_y is not None and current_price_y is not None:
            above_support = current_price_y < support_y
            distance_to_support = abs(current_price_y - support_y)
        else:
            above_support = False
            distance_to_support = None
        
        # Detect candlestick stability (multiple candles at similar price)
        # Analyze recent candlesticks (last 50 pixels in horizontal direction)
        recent_region = main_chart[:, -50:]
        gray_recent = cv2.cvtColor(recent_region, cv2.COLOR_BGR2GRAY)
        
        # Count candles in stable range (within 10 pixels)
        if current_price_y is not None:
            stable_range_start = max(0, current_price_y - 10)
            stable_range_end = min(main_chart.shape[0], current_price_y + 10)
            stable_pixels = np.sum(gray_recent[stable_range_start:stable_range_end, :])
            
            # Approximate candle count (assuming each candle has at least 100 pixels)
            stable_candle_count = int(stable_pixels / 100)
        else:
            stable_candle_count = 0
        
        return {
            'support_y': support_y,
            'support_strength': support_strength,
            'current_price_y': current_price_y,
            'above_support': above_support,
            'distance_to_support': distance_to_support,
            'stable_candle_count': stable_candle_count,
            'stabilized': stable_candle_count >= 3
        }
    
    def _analyze_net_volume(self, net_volume: np.ndarray, width: int, height: int) -> Dict:
        """Analyze net volume for LPS pattern"""
        # Red pixels (long positions)
        red_mask = cv2.inRange(net_volume,
                              self.color_thresholds['net_volume_long']['lower'],
                              self.color_thresholds['net_volume_long']['upper'])
        
        # Green pixels (short positions)
        green_mask = cv2.inRange(net_volume,
                                self.color_thresholds['net_volume_short']['lower'],
                                self.color_thresholds['net_volume_short']['upper'])
        
        red_count = int(np.count_nonzero(red_mask))
        green_count = int(np.count_nonzero(green_mask))
        total_count = red_count + green_count
        
        # Calculate net volume metrics
        if total_count > 0:
            net_long_ratio = red_count / total_count
            net_short_ratio = green_count / total_count
        else:
            net_long_ratio = 0
            net_short_ratio = 0
        
        # Check for net long stability (net_long_ratio > 0.5)
        net_long_stable = red_count > green_count
        
        return {
            'red_count': red_count,
            'green_count': green_count,
            'total_count': total_count,
            'net_long_ratio': net_long_ratio,
            'net_short_ratio': net_short_ratio,
            'net_long': red_count > green_count,
            'net_short': green_count > red_count,
            'net_long_stable': net_long_stable
        }
    
    def _analyze_delta(self, delta: np.ndarray, width: int, height: int) -> Dict:
        """Analyze DELTA for LPS pattern"""
        # Convert to grayscale
        gray = cv2.cvtColor(delta, cv2.COLOR_BGR2GRAY)
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Hough lines for curve detection
        lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180,
                               threshold=30, minLineLength=80, maxLineGap=30)
        
        # Analyze curve direction
        has_curve = lines is not None and len(lines) > 0
        
        # Count red and green pixels in DELTA
        red_mask = cv2.inRange(delta,
                              self.color_thresholds['net_volume_long']['lower'],
                              self.color_thresholds['net_volume_long']['upper'])
        
        green_mask = cv2.inRange(delta,
                                self.color_thresholds['net_volume_short']['lower'],
                                self.color_thresholds['net_volume_short']['upper'])
        
        red_count = int(np.count_nonzero(red_mask))
        green_count = int(np.count_nonzero(green_mask))
        
        # Determine slope
        if has_curve:
            if red_count > green_count:
                slope = 'up'
            elif green_count > red_count:
                slope = 'down'
            else:
                slope = 'flat'
        else:
            slope = 'unknown'
        
        # Check if flat or slightly up (LPS condition)
        flat_or_slightly_up = slope in ['up', 'flat']
        
        return {
            'has_curve': has_curve,
            'slope': slope,
            'red_count': red_count,
            'green_count': green_count,
            'curve_count': len(lines) if lines is not None else 0,
            'flat_or_slightly_up': flat_or_slightly_up
        }
    
    def _detect_lps(self, price_analysis: Dict, net_volume_analysis: Dict, delta_analysis: Dict) -> Dict:
        """Detect LPS (Last Point of Support) pattern based on all analyses"""
        
        # LPS Pattern Characteristics:
        # 1. Price stabilizes 3+ candles above S2 (stabilized = True and above_support = True)
        # 2. Net volume net long and stable (net_long_stable = True)
        # 3. Delta flat or slightly up (flat_or_slightly_up = True)
        
        # Calculate confidence score
        confidence_score = 0
        signals = []
        
        # Check 1: Price structure - stabilization above S2
        if price_analysis['stabilized'] and price_analysis['above_support']:
            confidence_score += 40
            signals.append(f'价格站稳S2上方{price_analysis["stable_candle_count"]}根K线（企稳）')
        elif price_analysis['above_support']:
            confidence_score += 20
            signals.append('价格位于S2上方（但未企稳）')
        elif price_analysis['stabilized']:
            confidence_score += 15
            signals.append('价格企稳（但位于S2下方）')
        
        # Check 2: Net volume - net long and stable
        if net_volume_analysis['net_long_stable']:
            confidence_score += 35
            signals.append('净量净多稳定')
        elif net_volume_analysis['net_long']:
            confidence_score += 20
            signals.append('净量净多（但不够稳定）')
        
        # Check 3: Delta - flat or slightly up
        if delta_analysis['flat_or_slightly_up']:
            confidence_score += 25
            if delta_analysis['slope'] == 'up':
                signals.append('DELTA斜率向上（动能增强）')
            else:
                signals.append('DELTA平坦（动能稳定）')
        elif delta_analysis['slope'] == 'down':
            confidence_score += 0
            signals.append('DELTA斜率向下（动能减弱）')
        
        # Determine if LPS pattern detected
        detected = confidence_score >= 70
        
        # Description
        if detected:
            description = 'LPS（最后的支撑点），二买位置，低吸参考'
            risk_warning = 'LPS形态：二买位置，低吸参考'
            action_plan = [
                '回踩S2后做多单',
                '严格止损，不扛单',
                '若突破失败，立即止损'
            ]
        else:
            description = 'LPS（最后的支撑点）-未检测到'
            risk_warning = None
            action_plan = None
        
        print(f"  Result: {'LPS Pattern Detected' if detected else 'No LPS Pattern'} (Confidence: {confidence_score}%)")
        if signals:
            print(f"  Signals: {', '.join(signals)}")
        
        return {
            'detected': detected,
            'confidence': confidence_score,
            'description': description,
            'risk_warning': risk_warning,
            'signals': signals,
            'action_plan': action_plan
        }


def test_lps_detector():
    """Test LPS pattern detector on 5 images"""
    
    test_images = [
        "9c5927d6-a315-4f12-9768-a9a2941aacfc.jpg",  # Weekly
        "437746cd-65be-4603-938c-85debf232d94.jpg",  # Daily
        "19397363-b6cd-4344-93cc-870d7d872a83.jpg",  # Hourly
        "7ce8ed01-8ac5-45c4-945c-e3b82dda8fe2.jpg",  # 15min
        "6f492e6b-7b20-4356-b939-5b17422dadf2.jpg"  # 5min
    ]
    
    detector = WKFLPSPatternDetector()
    
    print("=" * 80)
    print("WKF LPS Pattern Detector - Test")
    print("=" * 80)
    print("Testing LPS (Last Point of Support) Pattern Detection on 5 images")
    print("=" * 80)
    
    all_results = []
    
    for i, image_name in enumerate(test_images, 1):
        image_path = f"/root/.openclaw/media/inbound/{image_name}"
        
        if not os.path.exists(image_path):
            print(f"\n[{i}/{len(test_images)}] Image not found: {image_name}")
            continue
        
        print(f"\n{'='*80}")
        print(f"[{i}/{len(test_images)}] Testing: {image_name}")
        print(f"{'='*80}")
        
        try:
            result = detector.detect_lps_pattern(image_path)
            all_results.append(result)
            
            # Print summary
            print(f"\nLPS Pattern Summary for {image_name}:")
            print(f"  Detected: {'Yes' if result['detected'] else 'No'}")
            print(f"  Confidence: {result['confidence']}%")
            print(f"  Description: {result['description']}")
            
            if result['detected']:
                print(f"\n  Risk Warning: {result['risk_warning']}")
                if result['action_plan']:
                    print(f"  Action Plan:")
                    for j, action in enumerate(result['action_plan'], 1):
                        print(f"    {j}. {action}")
            
        except Exception as e:
            print(f"\nError analyzing {image_name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Print summary
    print("\n" + "=" * 80)
    print("LPS Pattern Detection Summary")
    print("=" * 80)
    
    detected_count = sum(1 for r in all_results if r['detected'])
    print(f"\nTotal images analyzed: {len(all_results)}")
    print(f"LPS patterns detected: {detected_count}/{len(all_results)}")
    
    if all_results:
        avg_confidence = sum(r['confidence'] for r in all_results) / len(all_results)
        print(f"Average confidence: {avg_confidence:.1f}%")
    
    # Save results
    output_file = "/root/.openclaw/workspace/lps_pattern_detection_results.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {output_file}")
    except Exception as e:
        print(f"\nError saving results: {e}")


if __name__ == "__main__":
    test_lps_detector()
