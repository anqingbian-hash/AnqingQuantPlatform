#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WKF BC (Buying Climax) Pattern Detector
BC（购买高潮）- 短期高点，别追多
"""

import cv2
import numpy as np
import json
import os
from typing import Dict, List, Tuple

class WKFBCPatternDetector:
    """BC (Buying Climax) Pattern Detector"""
    
    def __init__(self):
        """Initialize detector"""
        self.regions = {
            'main_chart': (0, int(1377 * 0.45)),
            'net_volume': (int(1377 * 0.45), int(1377 * 0.72)),
            'delta': (int(1377 * 0.72), 1377)
        }
        
        # Color thresholds
        self.color_thresholds = {
            'current_price': {
                'lower': np.array([20, 60, 150]),
                'upper': np.array([60, 200, 200])
            },
            'candlestick_bullish': {
                'lower': np.array([0, 100, 100]),
                'upper': np.array([50, 255, 255])
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
    
    def detect_bc_pattern(self, image_path: str) -> Dict:
        """Detect BC (Buying Climax) pattern"""
        print(f"\n[BC Pattern Detection] Analyzing: {os.path.basename(image_path)}")
        
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            return {
                'success': False,
                'error': 'Cannot read image',
                'detected': False,
                'pattern': 'bc',
                'confidence': 0,
                'description': 'BC（购买高潮），短期高点，别追多 - 无法读取图片'
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
        
        # Detect BC pattern
        print("  [4] Detecting BC pattern...")
        bc_result = self._detect_bc(price_analysis, net_volume_analysis, delta_analysis)
        
        return {
            'success': True,
            'image_path': image_path,
            'image_name': os.path.basename(image_path),
            'pattern': 'bc',
            'price_analysis': price_analysis,
            'net_volume_analysis': net_volume_analysis,
            'delta_analysis': delta_analysis,
            **bc_result
        }
    
    def _analyze_price_structure(self, main_chart: np.ndarray, width: int, height: int) -> Dict:
        """Analyze price structure for BC pattern"""
        # Detect current price line
        current_price_mask = cv2.inRange(main_chart, 
                                       self.color_thresholds['current_price']['lower'],
                                       self.color_thresholds['current_price']['upper'])
        
        row_counts = np.sum(current_price_mask, axis=1)
        
        if np.max(row_counts) < 50:
            current_price_y = None
        else:
            current_price_y = int(np.argmax(row_counts))
        
        # Detect recent high points
        gray = cv2.cvtColor(main_chart, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Find high points (local maxima)
        # Simple approach: detect edges in upper region
        upper_region = main_chart[0:int(main_chart.shape[0] * 0.3), :]
        upper_edges = cv2.Canny(cv2.cvtColor(upper_region, cv2.COLOR_BGR2GRAY), 50, 150)
        high_edge_count = np.sum(upper_edges > 0)
        
        return {
            'current_price_y': current_price_y,
            'high_edge_count': int(high_edge_count),
            'upper_region_ratio': 0.3
        }
    
    def _analyze_net_volume(self, net_volume: np.ndarray, width: int, height: int) -> Dict:
        """Analyze net volume for BC pattern"""
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
        
        # Check for volume surge (abnormal increase)
        # If red_count is significantly higher than green_count
        volume_surge = red_count > green_count * 2
        
        return {
            'red_count': red_count,
            'green_count': green_count,
            'total_count': total_count,
            'net_long_ratio': net_long_ratio,
            'net_short_ratio': net_short_ratio,
            'net_long': red_count > green_count,
            'volume_surge': volume_surge,
            'surge_ratio': red_count / (green_count + 1) if green_count > 0 else red_count
        }
    
    def _analyze_delta(self, delta: np.ndarray, width: int, height: int) -> Dict:
        """Analyze DELTA for BC pattern"""
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
                accelerating = red_count > green_count * 1.5
            elif green_count > red_count:
                slope = 'down'
                accelerating = green_count > red_count * 1.5
            else:
                slope = 'flat'
                accelerating = False
        else:
            slope = 'unknown'
            accelerating = False
        
        return {
            'has_curve': has_curve,
            'slope': slope,
            'accelerating': accelerating,
            'red_count': red_count,
            'green_count': green_count,
            'curve_count': len(lines) if lines is not None else 0
        }
    
    def _detect_bc(self, price_analysis: Dict, net_volume_analysis: Dict, delta_analysis: Dict) -> Dict:
        """Detect BC (Buying Climax) pattern based on all analyses"""
        
        # BC Pattern Characteristics:
        # 1. Price breaks above recent high (high edge count in upper region)
        # 2. Volume surge abnormally (net_long_ratio > 0.67 and surge_ratio > 2)
        # 3. Delta slope up and accelerating
        
        # Calculate confidence score
        confidence_score = 0
        signals = []
        
        # Check 1: Price structure - high points in upper region
        if price_analysis['high_edge_count'] > 1000:
            confidence_score += 30
            signals.append('价格突破近期高点（上部区域高点密集）')
        elif price_analysis['high_edge_count'] > 500:
            confidence_score += 15
            signals.append('价格接近近期高点')
        
        # Check 2: Net volume - volume surge
        if net_volume_analysis['volume_surge']:
            confidence_score += 40
            signals.append(f'净量异常增大（做多/做空比={net_volume_analysis["surge_ratio"]:.2f}）')
        elif net_volume_analysis['net_long']:
            confidence_score += 20
            signals.append('净量净多（但未达爆发水平）')
        
        # Check 3: Delta - accelerating upward
        if delta_analysis['slope'] == 'up' and delta_analysis['accelerating']:
            confidence_score += 30
            signals.append('DELTA斜率向上并加速（动能增强）')
        elif delta_analysis['slope'] == 'up':
            confidence_score += 15
            signals.append('DELTA斜率向上（动能增强）')
        
        # Determine if BC pattern detected
        detected = confidence_score >= 70
        
        # Description
        if detected:
            description = 'BC（购买高潮），短期高点，别追多'
            risk_warning = 'BC形态：短期高点，注意回调，不建议追多'
            action_plan = [
                '观望，等待价格回调',
                '若回调确认后再考虑入场',
                '严格止损，不扛单'
            ]
        else:
            description = 'BC（购买高潮）-未检测到'
            risk_warning = None
            action_plan = None
        
        print(f"  Result: {'BC Pattern Detected' if detected else 'No BC Pattern'} (Confidence: {confidence_score}%)")
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


def test_bc_detector():
    """Test BC pattern detector on 5 images"""
    
    test_images = [
        "9c5927d6-a315-4f12-9768-a9a2941aacfc.jpg",  # Weekly
        "437746cd-65be-4603-938c-85debf232d94.jpg",  # Daily
        "19397363-b6cd-4344-93cc-870d7d872a83.jpg",  # Hourly
        "7ce8ed01-8ac5-45c4-945c-e3b82dda8fe2.jpg",  # 15min
        "6f492e6b-7b20-4356-b939-5b17422dadf2.jpg"  # 5min
    ]
    
    detector = WKFBCPatternDetector()
    
    print("=" * 80)
    print("WKF BC Pattern Detector - Test")
    print("=" * 80)
    print("Testing BC (Buying Climax) Pattern Detection on 5 images")
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
            result = detector.detect_bc_pattern(image_path)
            all_results.append(result)
            
            # Print summary
            print(f"\nBC Pattern Summary for {image_name}:")
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
    print("BC Pattern Detection Summary")
    print("=" * 80)
    
    detected_count = sum(1 for r in all_results if r['detected'])
    print(f"\nTotal images analyzed: {len(all_results)}")
    print(f"BC patterns detected: {detected_count}/{len(all_results)}")
    
    if all_results:
        avg_confidence = sum(r['confidence'] for r in all_results) / len(all_results)
        print(f"Average confidence: {avg_confidence:.1f}%")
    
    # Save results
    output_file = "/root/.openclaw/workspace/bc_pattern_detection_results.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {output_file}")
    except Exception as e:
        print(f"\nError saving results: {e}")


if __name__ == "__main__":
    test_bc_detector()
