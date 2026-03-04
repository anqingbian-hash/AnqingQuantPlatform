#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WKF LPSY (Last Point of Supply) Pattern Detector
LPSY（最后的供应点）- 二卖位置，高抛参考
"""

import cv2
import numpy as np
import json
import os
from typing import Dict, List, Tuple

class WKFLPSYPatternDetector:
    """LPSY (Last Point of Supply) Pattern Detector"""
    
    def __init__(self):
        """Initialize detector"""
        self.regions = {
            'main_chart': (0, int(1377 * 0.45)),
            'net_volume': (int(1377 * 0.45), int(1377 * 0.72)),
            'delta': (int(1377 * 0.72), 1377)
        }
        
        # Color thresholds
        self.color_thresholds = {
            'resistance_line_red': {
                'lower': np.array([90, 90, 160]),
                'upper': np.array([100, 100, 170])
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
    
    def detect_lpsy_pattern(self, image_path: str) -> Dict:
        """Detect LPSY (Last Point of Supply) pattern"""
        print(f"\n[LPSY Pattern Detection] Analyzing: {os.path.basename(image_path)}")
        
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            return {
                'success': False,
                'error': 'Cannot read image',
                'detected': False,
                'pattern': 'lpsy',
                'confidence': 0,
                'description': 'LPSY（最后的供应点），二卖位置，高抛参考 - 无法读取图片'
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
        
        # Detect LPSY pattern
        print("  [4] Detecting LPSY pattern...")
        lpsy_result = self._detect_lpsy(price_analysis, net_volume_analysis, delta_analysis)
        
        return {
            'success': True,
            'image_path': image_path,
            'image_name': os.path.basename(image_path),
            'pattern': 'lpsy',
            'price_analysis': price_analysis,
            'net_volume_analysis': net_volume_analysis,
            'delta_analysis': delta_analysis,
            **lpsy_result
        }
    
    def _analyze_price_structure(self, main_chart: np.ndarray, width: int, height: int) -> Dict:
        """Analyze price structure for LPSY pattern"""
        # Detect resistance line (red/pink)
        resistance_mask = cv2.inRange(main_chart, 
                                     self.color_thresholds['resistance_line_red']['lower'],
                                     self.color_thresholds['resistance_line_red']['upper'])
        
        # Find the strongest horizontal red line
        row_counts = np.sum(resistance_mask, axis=1)
        
        if np.max(row_counts) > 100:
            resistance_y = int(np.argmax(row_counts))
            resistance_strength = int(row_counts[resistance_y])
        else:
            resistance_y = None
            resistance_strength = 0
        
        # Detect current price line
        current_price_mask = cv2.inRange(main_chart, 
                                       self.color_thresholds['current_price']['lower'],
                                       self.color_thresholds['current_price']['upper'])
        
        row_counts = np.sum(current_price_mask, axis=1)
        
        if np.max(row_counts) > 50:
            current_price_y = int(np.argmax(row_counts))
        else:
            current_price_y = None
        
        # Calculate consolidation (price below resistance line)
        if resistance_y is not None and current_price_y is not None:
            below_resistance = current_price_y > resistance_y
            distance_to_resistance = abs(current_price_y - resistance_y)
        else:
            below_resistance = False
            distance_to_resistance = None
        
        # Detect candlestick consolidation (multiple candles at similar price)
        # Analyze recent candlesticks (last 50 pixels in horizontal direction)
        recent_region = main_chart[:, -50:]
        gray_recent = cv2.cvtColor(recent_region, cv2.COLOR_BGR2GRAY)
        
        # Count candles in consolidation range (within 10 pixels)
        if current_price_y is not None:
            consolidation_range_start = max(0, current_price_y - 10)
            consolidation_range_end = min(main_chart.shape[0], current_price_y + 10)
            consolidation_pixels = np.sum(gray_recent[consolidation_range_start:consolidation_range_end, :])
            
            # Approximate candle count (assuming each candle has at least 100 pixels)
            consolidation_candle_count = int(consolidation_pixels / 100)
        else:
            consolidation_candle_count = 0
        
        return {
            'resistance_y': resistance_y,
            'resistance_strength': resistance_strength,
            'current_price_y': current_price_y,
            'below_resistance': below_resistance,
            'distance_to_resistance': distance_to_resistance,
            'consolidation_candle_count': consolidation_candle_count,
            'consolidated': consolidation_candle_count >= 3
        }
    
    def _analyze_net_volume(self, net_volume: np.ndarray, width: int, height: int) -> Dict:
        """Analyze net volume for LPSY pattern"""
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
        
        # Check for net short dominance or turning from long to short
        net_short_dominant = green_count > red_count * 1.2
        turning_from_long_to_short = red_count > green_count * 0.8 and green_count > red_count * 0.8
        
        return {
            'red_count': red_count,
            'green_count': green_count,
            'total_count': total_count,
            'net_long_ratio': net_long_ratio,
            'net_short_ratio': net_short_ratio,
            'net_long': red_count > green_count,
            'net_short': green_count > red_count,
            'net_short_dominant': net_short_dominant,
            'turning_from_long_to_short': turning_from_long_to_short
        }
    
    def _analyze_delta(self, delta: np.ndarray, width: int, height: int) -> Dict:
        """Analyze DELTA for LPSY pattern"""
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
        
        # Check if flat or down (LPSY condition)
        flat_or_down = slope in ['down', 'flat']
        
        return {
            'has_curve': has_curve,
            'slope': slope,
            'red_count': red_count,
            'green_count': green_count,
            'curve_count': len(lines) if lines is not None else 0,
            'flat_or_down': flat_or_down
        }
    
    def _detect_lpsy(self, price_analysis: Dict, net_volume_analysis: Dict, delta_analysis: Dict) -> Dict:
        """Detect LPSY (Last Point of Supply) pattern based on all analyses"""
        
        # LPSY Pattern Characteristics:
        # 1. Price consolidates 3+ candles below R2 (consolidated = True and below_resistance = True)
        # 2. Net volume net short or turning from long to short (net_short_dominant or turning_from_long_to_short)
        # 3. Delta flat or down (flat_or_down = True)
        
        # Calculate confidence score
        confidence_score = 0
        signals = []
        
        # Check 1: Price structure - consolidation below R2
        if price_analysis['consolidated'] and price_analysis['below_resistance']:
            confidence_score += 40
            signals.append(f'价格在R2下方企稳{price_analysis["consolidation_candle_count"]}根K线（震荡）')
        elif price_analysis['below_resistance']:
            confidence_score += 20
            signals.append('价格位于R2下方（但未企稳）')
        elif price_analysis['consolidated']:
            confidence_score += 15
            signals.append('价格企稳（但位于R2上方）')
        
        # Check 2: Net volume - net short dominant or turning
        if net_volume_analysis['net_short_dominant']:
            confidence_score += 35
            signals.append('净量净空主导')
        elif net_volume_analysis['turning_from_long_to_short']:
            confidence_score += 30
            signals.append('净量由多转空（转折）')
        elif net_volume_analysis['net_short']:
            confidence_score += 20
            signals.append('净量净空（但不够主导）')
        
        # Check 3: Delta - flat or down
        if delta_analysis['flat_or_down']:
            confidence_score += 25
            if delta_analysis['slope'] == 'down':
                signals.append('DELTA斜率向下（动能减弱）')
            else:
                signals.append('DELTA平坦（动能稳定）')
        elif delta_analysis['slope'] == 'up':
            confidence_score += 0
            signals.append('DELTA斜率向上（动能增强）')
        
        # Determine if LPSY pattern detected
        detected = confidence_score >= 70
        
        # Description
        if detected:
            description = 'LPSY（最后的供应点），二卖位置，高抛参考'
            risk_warning = 'LPSY形态：二卖位置，高抛参考'
            action_plan = [
                '回踩R2后做空单',
                '严格止损，不扛单',
                '若突破失败，立即止损'
            ]
        else:
            description = 'LPSY（最后的供应点）-未检测到'
            risk_warning = None
            action_plan = None
        
        print(f"  Result: {'LPSY Pattern Detected' if detected else 'No LPSY Pattern'} (Confidence: {confidence_score}%)")
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


def test_lpsy_detector():
    """Test LPSY pattern detector on 5 images"""
    
    test_images = [
        "9c5927d6-a315-4f12-9768-a9a2941aacfc.jpg",  # Weekly
        "437746cd-65be-4603-938c-85debf232d94.jpg",  # Daily
        "19397363-b6cd-4344-93cc-870d7d872a83.jpg",  # Hourly
        "7ce8ed01-8ac5-45c4-945c-e3b82dda8fe2.jpg",  # 15min
        "6f492e6b-7b20-4356-b939-5b17422dadf2.jpg"  # 5min
    ]
    
    detector = WKFLPSYPatternDetector()
    
    print("=" * 80)
    print("WKF LPSY Pattern Detector - Test")
    print("=" * 80)
    print("Testing LPSY (Last Point of Supply) Pattern Detection on 5 images")
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
            result = detector.detect_lpsy_pattern(image_path)
            all_results.append(result)
            
            # Print summary
            print(f"\nLPSY Pattern Summary for {image_name}:")
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
    print("LPSY Pattern Detection Summary")
    print("=" * 80)
    
    detected_count = sum(1 for r in all_results if r['detected'])
    print(f"\nTotal images analyzed: {len(all_results)}")
    print(f"LPSY patterns detected: {detected_count}/{len(all_results)}")
    
    if all_results:
        avg_confidence = sum(r['confidence'] for r in all_results) / len(all_results)
        print(f"Average confidence: {avg_confidence:.1f}%")
    
    # Save results
    output_file = "/root/.openclaw/workspace/lpsy_pattern_detection_results.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {output_file}")
    except Exception as e:
        print(f"\nError saving results: {e}")


if __name__ == "__main__":
    test_lpsy_detector()
