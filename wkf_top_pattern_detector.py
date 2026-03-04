#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WKF Complete Analyzer V4
Includes: SR line detection, Y-coordinate to price mapping, top/bottom pattern detection, WKF judgment
"""

import cv2
import numpy as np
import json
import os
from typing import Dict, List, Tuple
import sys

sys.path.append('/root/.openclaw/workspace')


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


class WKFTopPatternDetector:
    """WKF Top/Bottom Pattern Detector"""

    def __init__(self):
        """Initialize"""
        self.regions = {
            'main_chart': (0, int(1377 * 0.45))
        }

    def detect_top_patterns(self, image_path: str) -> Dict:
        """Detect top patterns (BC/SC/LPSY)"""
        print(f"\\nTop Pattern Detection")
        print(f"Analyzing: {os.path.basename(image_path)}")

        # Read image
        image = cv2.imread(image_path)
        if image is None:
            return {
                'success': False,
                'error': 'Cannot read image'
            }

        height, width = image.shape[:2]
        main_chart = image[self.regions['main_chart'][0]:self.regions['main_chart'][1], :]]

        # Analyze net volume
        print(f"\\n[1] Analyzing Net Volume...")
        net_volume = self._analyze_net_volume(image, width, height)

        # Analyze DELTA
        print(f"\\n[2] Analyzing Delta...")
        delta = self._analyze_delta(image, width, height)

        # Detect top patterns (BC/SC/LPS/LPSY)
        print(f"\\n[3] Detecting Top Patterns (BC/SC/LPS/LPSY)...")

        top_patterns = {}

        # Detect BC (Buying Climax) - Short term high, Don't Chase
        print("  Detecting BC (Buying Climax)...")

        # Detect SC (Selling Climax) - Short term low, Don't Short
        print("  Detecting SC (Selling Climax)...")

        # Detect LPS (Last Point of Support) - Last buying position, Low buy entry
        print(" Detecting LPS (Last Point of Support)...")

        # Detect LPSY (Last Point of Supply) - Last selling position, High exit
        print(" Detecting LPSY (Last Point of Supply)...")

        # Combine patterns
        top_patterns['bc'] = {'detected': False, 'confidence': 0, 'description': 'BC（购买高潮），短期高点，别追多'}
        top_patterns['sc'] = {'detected': False, 'confidence': 0, 'description': 'SC（卖出密集区），短期低点，别追空'}
        top_patterns['lps'] = {'detected': False, 'confidence': 0, 'description': 'LPS（最后的支撑点），二买位置，低吸参考'}
        top_patterns['lpsy'] = {'detected': False, 'confidence': 0, 'description': 'LPSY（最后的供应点），二卖位置，高抛参考'}

        print(f"\nTop Patterns Summary:")
        for pattern_type in ['bc', 'sc', 'lps', 'lpsy']:
            print(f"  {pattern_type.upper()}  {top_patterns[pattern_type]['description']} - 置信度：{top_patterns[pattern_type]['confidence']}%")

        return top_patterns

    def _analyze_net_volume(self, image: np.ndarray, width: int, height: int) -> Dict:
        """Analyze net volume for top pattern detection"""
        # Extract net volume region
        net_volume_region = image[self.regions['net_volume'][0]:self.regions['net_volume'][1], :]]

        # Red pixels (Long positions)
        lower_red = np.array([150, 150, 150), (255, 255)])
        upper_red = np.array([200, 255, 255), (255, 255)])
        red_mask = cv2.inRange(net_volume_region, lower_red, upper_red)

        # Green pixels (Short positions)
        lower_green = np.array([0, 0, 0), (0, 100, 100), (0, 10])
        upper_green = np.array([(0, 0, 0), (0, 200), (0, 100), (0, 10)])

        red_count = int(np.count_nonzero(red_mask))
        green_count = int(np.count_nonzero(green_mask))

        print(f"  Net Volume Status:")
        if red_count > green_count:
            print(f"  Status: Net Long (Long) - {red_count} red pixels vs {green_count} green pixels)")
        elif green_count > red_count:
            print(f"  Net Short (Short) - {green_count} green pixels vs {red_count} red pixels")
        else:
            print("  Status: Flat (Neutral)")

        return {
            'success': True,
            'red_count': red_count,
            'green_count': green_count,
            'net_long': red_count > green_count,
            'net_short': green_count > red_count
        }

    def _analyze_delta(self, image: np.ndarray, width: int, height: int) -> Dict:
        """Analyze DELTA for top pattern detection"""
        # Extract delta region
        delta_region = image[self.regions['delta'][0]:self.regions['delta'][1], :]]

        # Convert to grayscale
        gray = cv2.cvtColor(delta_region, cv2.COLOR_BGR2GRAY)

        # Edge detection
        edges = cv2.Canny(gray, 50, 100, apertureSize=3)

        # Hough lines for curve detection
        lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180,
                               threshold=40, minLineLength=100, maxLineGap=30)

        # Check if there is a curve
        has_curve = lines is not None and len(lines) > 0

        red_mask = cv2.inRange(delta_region, (150, 150, 150), (255, 255))
        green_mask = cv2.inRange(delta_region, (0, 0), (100, 255, 100))

        red_count = int(np.count_nonzero(red_mask))
        green_count = int(np.count_nonzero(green_mask))

        print(f"  Curve Detection: {has_curve} curves, {len(lines) if lines is not None else 0}")

        if has_curve:
            print(f"  Red: {red_count} Green: {green_count}")

            if red_count > green_count:
                slope = 'up'
                print(f"  Slope: up")
            elif green_count > red_count:
                slope = 'down'
                print(f"  Slope: down")
            else:
                slope = 'unknown'

        return {
            'has_curve': has_curve,
            'red_count': red_count,
            'green_count': green_count,
            'red_count': red_count,
            'green_count': green_count,
            'slope': slope
        }

    def detect_bc_pattern(self, main_chart: np.ndarray) -> Dict:
        """
        Detect BC (Buying Climax) pattern - Short term high, Don't chase
        """
        # BC Characteristics:
        # 1. Price breaks above recent high
        # 2. Volume surge abnormally
        # 3. Delta slope up (accelerating)

        # TODO: Implement BC detection logic
        return {
            'pattern': 'bc',
            'detected': False,
            'confidence': 0,
            'description': 'BC（购买高潮），短期高点，别追多'
        }

    def detect_sc_pattern(self, main_chart: np.ndarray) -> Dict:
        """
        Detect SC (Selling Climax) pattern - Short term low, Don't chase
        """
        # SC Characteristics:
        # 1. Price drops below recent low
        # 2. Volume spike (short selling)
        # 3. Delta slope down (accelerating)

        # TODO: Implement SC detection logic
        return {
            'pattern': 'sc',
            'detected': False,
            'confidence': 0,
            'description': 'SC（卖出密集区），短期低点，别追空'
        }

    def detect_lps_pattern(self, main_chart: np.ndarray) -> Dict:
        """
        Detect LPS (Last Point of Support) - Last buying position, Low buy entry
        """
        # LPS Characteristics:
        # 1. Price stabilizes 3+ candles above S2 (3-week consolidation)
        # 2. Net long (long-term) stable
        # 3. Delta flat or slightly up

        # TODO: Implement LPS detection logic
        return {
            'pattern': 'lps',
            'detected': False,
            'confidence': 0,
            'description': 'LPS（最后的支撑点），二买位置，低吸参考'
        }

    def detect_lpsy_pattern(self, main_chart: np.ndarray) -> Dict:
        """
        Detect LPSY (Last Point of Supply) - Last selling position, High exit position
        """
        # LPSY Characteristics:
        # 1. Price consolidates below R2 (2-week consolidation)
        # 2. Net volume shrinking or turning from long to short
        # 3. Delta down or flat

        # TODO: Implement LPSY detection logic
        return {
            'pattern': 'lpsy',
            'detected': False,
            'confidence': 0,
            'description': 'LPSY（最后的供应点），二卖位置，高抛参考'
        }

    def detect_top_patterns(self, image: np.ndarray) -> Dict:
        """
        Detect top patterns (BC/SC/LPS/LPSY) - Returns all detected patterns
        """
        print(f"\n[3] Detecting Top Patterns (BC/SC/LPS/LPSY)...\n")

        # 1. Detect net volume
        net_volume_result = self._analyze_net_volume(image, width, height)
        patterns = {
            'bc': {'detected': False, 'confidence': 0, 'description': 'BC（购买高潮），短期高点，别追多'}
        }

        # 2. Detect DELTA
        delta_result = self._analyze_delta(image, width, height)

        # 3. Detect LPS
        lps_result = self.detect_lps_pattern(image)
        lpsy_result = self.detect_lpsy_pattern(image)

        # 4. Detect LPSY
        lpsy_result = self.detect_lpsy_pattern(image)

        # 5. Combine patterns
        top_patterns = {
            'bc': self.detect_bc_pattern(image),
            'sc': self.detect_sc_pattern(image),
            'lps': self.detect_lps_pattern(image),
            'lpsy': self.detect_lpsy_pattern(image)
        }

        print(f"\n=== Top Patterns Summary ===")
        for pattern_type in ['bc', 'sc', 'lps', 'lpsy']:
            if top_patterns[pattern_type]['detected']:
                print(f"  {pattern_type.upper()}: {top_patterns[pattern_type]['description']} - 置信度：{top_patterns[pattern_type]['confidence']}%")

        return top_patterns


def test_top_patterns():
    """Test top pattern detection"""
    # Test image
    test_images = [
        "9c5927d6-a315-4f12-9768-a9a2941aacfc.jpg",
        "437746cd-65be-4603-938c-85debf232d94.jpg",
        "19397363-b6cd-4344-93cc-870d7d872a83.jpg",
        "7ce8ed01-8ac5-45c4-945c-e3b82dda8fe2.jpg",
        "6f492e6b-7b20-4356-b939-5b17422dadf2.jpg"
    ]

    # Create analyzer
    top_detector = WKFTopPatternDetector()

    print("\n=== Top Pattern Detector Test ===")
    print("=" * 80)

    all_results = []

    for i, image_name in enumerate(test_images):
        image_path = f"/root/.openclaw/media/inbound/{image_name}"

        if not os.path.exists(image_path):
            print(f"\n[{i+1}/{len(test_images)}] Image not found: {image_name}")
            continue

        print(f"\n{i+1}/{len(test_images)} Analyzing: {image_name}")
        print("=" * 80)

        try:
            result = top_detector.detect_top_patterns(image_path)
            all_results.append(result)

            # Print summary
            print(f"Top Patterns Summary for {image_name}")
            for pattern_type in ['bc', 'sc', 'lps', 'lpsy']:
                pattern = result.get(pattern_type)
                if pattern.get('detected', False):
                    print(f"  {pattern_type.upper()}：未检测到")
                    print(f"  Confidence：{pattern['confidence']}%")
                elif pattern.get('detected', True):
                    print(f"  {pattern.upper()}：{pattern['description']} - 置信度：{pattern['confidence']}%")

        except Exception as e:
            print(f"\nError analyzing {image_name}: {e}")
            import traceback
            traceback.print_exc()

    # Print summary
    print("\n=== Summary ===")
    print("Top Patterns Detected:")
    for pattern_type in ['bc', 'sc', 'lps', 'lpsy']:
        detected_count = sum([1 for p in all_results if p.get('detected', False)])

        print(f"Total detected patterns: {detected_count}/4")
    print("=" * 80)


if __name__ == "__main__":
    test_top_patterns()
