#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WKF R2 Line Detector V2 - Optimized
优化版R2（阻力线）识别器
"""

import cv2
import numpy as np
import json
import os
from typing import Dict, List, Tuple

class WKFR2DetectorV2:
    """R2 (Resistance Line) Detector V2 - Optimized"""
    
    def __init__(self):
        """Initialize detector with optimized parameters"""
        self.regions = {
            'main_chart': (0, int(1377 * 0.45))
        }
        
        # Optimized color thresholds
        self.color_thresholds = {
            'white_r2': {
                'lower': np.array([200, 200, 200]),  # 放宽到[200-255]
                'upper': np.array([255, 255, 255])
            }
        }
        
        # Optimized Hough parameters
        self.hough_params = {
            'rho': 1,
            'theta': np.pi/180,
            'threshold': 20,  # 降低到20
            'minLineLength': None,  # 动态计算
            'maxLineGap': 50
        }
    
    def detect_r2_line(self, image_path: str) -> Dict:
        """Detect R2 (resistance line) with optimized parameters"""
        print(f"\n[R2 Detection V2] Analyzing: {os.path.basename(image_path)}")
        
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            return {
                'success': False,
                'error': 'Cannot read image',
                'detected': False
            }
        
        height, width = image.shape[:2]
        main_chart = image[self.regions['main_chart'][0]:self.regions['main_chart'][1], :]
        
        # Calculate dynamic minLineLength (width * 0.1)
        min_line_length = int(width * 0.1)
        
        # [1] Detect white pixels
        print("  [1] Detecting white pixels...")
        white_mask = cv2.inRange(main_chart,
                                 self.color_thresholds['white_r2']['lower'],
                                 self.color_thresholds['white_r2']['upper'])
        
        white_count = int(np.count_nonzero(white_mask))
        white_ratio = white_count / (main_chart.shape[0] * main_chart.shape[1])
        
        print(f"    White pixels: {white_count} ({white_ratio:.2%})")
        
        if white_count < 100:
            print("    Warning: Too few white pixels, may not detect R2")
        
        # [2] Edge detection
        print("  [2] Edge detection...")
        gray = cv2.cvtColor(main_chart, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(white_mask, 50, 150, apertureSize=3)
        
        edge_count = int(np.sum(edges > 0))
        print(f"    Edge pixels: {edge_count}")
        
        # [3] Hough line detection with optimized parameters
        print(f"  [3] Hough line detection (threshold={self.hough_params['threshold']}, minLineLength={min_line_length})...")
        lines = cv2.HoughLinesP(edges,
                               rho=self.hough_params['rho'],
                               theta=self.hough_params['theta'],
                               threshold=self.hough_params['threshold'],
                               minLineLength=min_line_length,
                               maxLineGap=self.hough_params['maxLineGap'])
        
        if lines is None:
            print("    No lines detected")
            return {
                'success': True,
                'detected': False,
                'white_count': white_count,
                'white_ratio': white_ratio,
                'edge_count': edge_count,
                'lines_detected': 0
            }
        
        print(f"    Lines detected: {len(lines)}")
        
        # [4] Filter and classify lines
        print("  [4] Filtering and classifying lines...")
        
        resistance_lines = []
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # Must be horizontal (y1 ≈ y2)
            if abs(y1 - y2) > 5:
                continue
            
            # Must be long enough
            line_length = abs(x2 - x1)
            if line_length < min_line_length:
                continue
            
            # Extract line pixels for color analysis
            line_pixels = main_chart[y1-2:y1+3, x1:x2]
            
            # Classify color
            line_color = self._classify_line_color(line_pixels)
            
            if line_color == 'white':
                # Check if it's a K-line connector (thin vertical line)
                if line_length > width * 0.3:  # Wide enough, likely R2
                    resistance_lines.append({
                        'y': int(y1 + self.regions['main_chart'][0]),
                        'length': line_length,
                        'x1': int(x1),
                        'x2': int(x2),
                        'type': 'resistance',
                        'color': 'white',
                        'line_pixels': line_pixels
                    })
                    print(f"    R2 line found: y={y1}, length={line_length}")
        
        # Sort by length (longest first)
        resistance_lines.sort(key=lambda x: x['length'], reverse=True)
        
        # [5] Return result
        detected = len(resistance_lines) > 0
        
        if detected:
            r2_line = resistance_lines[0]
            print(f"  [5] Result: R2 detected at y={r2_line['y']}, length={r2_line['length']}")
        else:
            print(f"  [5] Result: No R2 detected")
        
        return {
            'success': True,
            'detected': detected,
            'white_count': white_count,
            'white_ratio': white_ratio,
            'edge_count': edge_count,
            'lines_detected': len(lines) if lines is not None else 0,
            'resistance_lines': resistance_lines,
            'r2_line': resistance_lines[0] if detected else None
        }
    
    def _classify_line_color(self, line_pixels: np.ndarray) -> str:
        """Classify line color"""
        if line_pixels.size == 0:
            return 'unknown'
        
        mean_color = np.mean(line_pixels, axis=(0, 1))
        b, g, r = mean_color
        
        # White detection (all channels high)
        if b >= 200 and g >= 200 and r >= 200:
            return 'white'
        
        # Red detection (red channel high)
        elif r >= 150 and g <= 100 and b <= 100:
            return 'red'
        
        # Green detection (green channel high)
        elif g >= 150 and r <= 100 and b <= 100:
            return 'green'
        
        # Yellow detection (red and green high)
        elif r >= 150 and g >= 150 and b <= 100:
            return 'yellow'
        
        else:
            return 'unknown'


def test_r2_detector_v2():
    """Test R2 detector V2 on 5 images"""
    
    test_images = [
        "9c5927d6-a315-4f12-9768-a9a2941aacfc.jpg",  # Weekly
        "437746cd-65be-4603-938c-85debf232d94.jpg",  # Daily
        "19397363-b6cd-4344-93cc-870d7d872a83.jpg",  # Hourly
        "7ce8ed01-8ac5-45c4-945c-e3b82dda8fe2.jpg",  # 15min
        "6f492e6b-7b20-4356-b939-5b17422dadf2.jpg"  # 5min
    ]
    
    periods = ['周线', '日线', '1小时', '15分钟', '5分钟']
    
    detector = WKFR2DetectorV2()
    
    print("=" * 80)
    print("WKF R2 Detector V2 - Optimized Test")
    print("=" * 80)
    print("Optimized Parameters:")
    print(f"  White Threshold: [200-255, 200-255, 200-255]")
    print(f"  Hough Threshold: 20 (reduced from 100)")
    print(f"  MinLineLength: width * 0.1 (dynamic)")
    print("=" * 80)
    
    all_results = []
    
    for i, (image_name, period) in enumerate(zip(test_images, periods), 1):
        image_path = f"/root/.openclaw/media/inbound/{image_name}"
        
        if not os.path.exists(image_path):
            print(f"\n[{i}/{len(test_images)}] Image not found: {image_name}")
            continue
        
        print(f"\n{'='*80}")
        print(f"[{i}/{len(test_images)}] {period} - {image_name}")
        print(f"{'='*80}")
        
        try:
            result = detector.detect_r2_line(image_path)
            all_results.append({
                'period': period,
                'image_name': image_name,
                **result
            })
            
            # Print summary
            print(f"\nR2 Detection Summary for {period}:")
            print(f"  Detected: {'Yes' if result['detected'] else 'No'}")
            print(f"  White Pixels: {result['white_count']} ({result['white_ratio']:.2%})")
            print(f"  Edge Pixels: {result['edge_count']}")
            print(f"  Lines Detected: {result['lines_detected']}")
            
            if result['detected']:
                r2_line = result['r2_line']
                print(f"  R2 Y-coordinate: {r2_line['y']}")
                print(f"  R2 Length: {r2_line['length']}")
            else:
                print(f"  R2: Not detected")
            
        except Exception as e:
            print(f"\nError analyzing {image_name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Print summary
    print("\n" + "=" * 80)
    print("R2 Detection V2 Summary")
    print("=" * 80)
    
    detected_count = sum(1 for r in all_results if r['detected'])
    print(f"\nTotal images analyzed: {len(all_results)}")
    print(f"R2 detected: {detected_count}/{len(all_results)}")
    
    if all_results:
        avg_white_ratio = sum(r['white_ratio'] for r in all_results) / len(all_results)
        avg_edge_count = sum(r['edge_count'] for r in all_results) / len(all_results)
        print(f"Average white ratio: {avg_white_ratio:.2%}")
        print(f"Average edge count: {avg_edge_count:.0f}")
    
    # Detailed results
    print(f"\nDetailed Results:")
    for result in all_results:
        period = result['period']
        detected = result['detected']
        white_ratio = result['white_ratio']
        edge_count = result['edge_count']
        lines_detected = result['lines_detected']
        
        print(f"  {period}: {'✅' if detected else '❌'} (white={white_ratio:.2%}, edges={edge_count}, lines={lines_detected})")
    
    # Save results
    output_file = "/root/.openclaw/workspace/r2_detection_v2_results.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {output_file}")
    except Exception as e:
        print(f"\nError saving results: {e}")
    
    print("=" * 80)


if __name__ == "__main__":
    test_r2_detector_v2()
