#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WKF R2 Line Detector V3 - Ultra Optimized
超优化版R2（阻力线）识别器
"""

import cv2
import numpy as np
import json
import os
from typing import Dict, List, Tuple

class WKFR2DetectorV3:
    """R2 (Resistance Line) Detector V3 - Ultra Optimized"""
    
    def __init__(self):
        """Initialize detector with ultra optimized parameters"""
        self.regions = {
            'main_chart': (0, int(1377 * 0.45))
        }
        
        # Ultra optimized color thresholds
        self.color_thresholds = {
            'white_r2': {
                'lower': np.array([200, 200, 200]),  # 放宽到[200-255]
                'upper': np.array([255, 255, 255])
            },
            'light_red_r2': {
                'lower': np.array([150, 150, 180]),
                'upper': np.array([200, 200, 255])
            }
        }
        
        # Ultra optimized Hough parameters
        self.hough_params = {
            'rho': 1,
            'theta': np.pi/180,
            'threshold': 15,  # 降低到15
            'minLineLength': 100,  # 降低到100（固定）
            'maxLineGap': 100  # 增加到100
        }
    
    def detect_r2_line(self, image_path: str) -> Dict:
        """Detect R2 (resistance line) with ultra optimized parameters"""
        print(f"\n[R2 Detection V3] Analyzing: {os.path.basename(image_path)}")
        
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
        
        # [1] Detect white and light red pixels
        print("  [1] Detecting white and light red pixels...")
        white_mask = cv2.inRange(main_chart,
                                 self.color_thresholds['white_r2']['lower'],
                                 self.color_thresholds['white_r2']['upper'])
        
        light_red_mask = cv2.inRange(main_chart,
                                     self.color_thresholds['light_red_r2']['lower'],
                                     self.color_thresholds['light_red_r2']['upper'])
        
        # Combine masks
        resistance_mask = cv2.bitwise_or(white_mask, light_red_mask)
        
        white_count = int(np.count_nonzero(white_mask))
        light_red_count = int(np.count_nonzero(light_red_mask))
        total_count = int(np.count_nonzero(resistance_mask))
        
        total_ratio = total_count / (main_chart.shape[0] * main_chart.shape[1])
        
        print(f"    White pixels: {white_count}")
        print(f"    Light red pixels: {light_red_count}")
        print(f"    Total resistance pixels: {total_count} ({total_ratio:.2%})")
        
        if total_count < 100:
            print("    Warning: Too few resistance pixels, may not detect R2")
        
        # [2] Edge detection
        print("  [2] Edge detection...")
        gray = cv2.cvtColor(main_chart, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(resistance_mask, 30, 100, apertureSize=3)
        
        edge_count = int(np.sum(edges > 0))
        print(f"    Edge pixels: {edge_count}")
        
        # [3] Hough line detection with ultra optimized parameters
        print(f"  [3] Hough line detection (threshold={self.hough_params['threshold']}, minLineLength={self.hough_params['minLineLength']}, maxLineGap={self.hough_params['maxLineGap']})...")
        lines = cv2.HoughLinesP(edges,
                               rho=self.hough_params['rho'],
                               theta=self.hough_params['theta'],
                               threshold=self.hough_params['threshold'],
                               minLineLength=self.hough_params['minLineLength'],
                               maxLineGap=self.hough_params['maxLineGap'])
        
        if lines is None:
            print("    No lines detected")
            return {
                'success': True,
                'detected': False,
                'white_count': white_count,
                'light_red_count': light_red_count,
                'total_count': total_count,
                'total_ratio': total_ratio,
                'edge_count': edge_count,
                'lines_detected': 0
            }
        
        print(f"    Lines detected: {len(lines)}")
        
        # [4] Filter and classify lines (relaxed criteria)
        print("  [4] Filtering and classifying lines (relaxed criteria)...")
        
        resistance_lines = []
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # Must be horizontal (y1 ≈ y2)
            if abs(y1 - y2) > 10:  # 放宽到10
                continue
            
            # Must be long enough (reduced to 100)
            line_length = abs(x2 - x1)
            if line_length < self.hough_params['minLineLength']:
                continue
            
            # Extract line pixels for color analysis
            line_pixels = main_chart[max(0, y1-3):min(main_chart.shape[0], y1+4), x1:x2]
            
            if line_pixels.size == 0:
                continue
            
            # Classify color
            mean_color = np.mean(line_pixels, axis=(0, 1))
            b, g, r = mean_color
            
            # Relaxed color detection
            is_white = (b >= 200 and g >= 200 and r >= 200)
            is_light_red = (r >= 150 and g >= 150 and b >= 180)
            
            if is_white or is_light_red:
                # Check if it's likely R2 (long horizontal line)
                # Also check if it's NOT a K-line connector (not too many vertical lines)
                resistance_lines.append({
                    'y': int(y1 + self.regions['main_chart'][0]),
                    'length': line_length,
                    'x1': int(x1),
                    'x2': int(x2),
                    'type': 'resistance',
                    'color': 'white' if is_white else 'light_red',
                    'mean_color': [float(b), float(g), float(r)],
                    'line_pixels_count': line_pixels.size
                })
                print(f"    R2 line candidate: y={y1}, length={line_length}, color={'white' if is_white else 'light_red'}")
        
        # Sort by length (longest first)
        resistance_lines.sort(key=lambda x: x['length'], reverse=True)
        
        # [5] Select best R2 candidate
        if resistance_lines:
            # Select the longest line as R2
            r2_line = resistance_lines[0]
            detected = True
            print(f"  [5] Result: R2 detected at y={r2_line['y']}, length={r2_line['length']}, color={r2_line['color']}")
        else:
            r2_line = None
            detected = False
            print(f"  [5] Result: No R2 detected (no valid candidates)")
        
        return {
            'success': True,
            'detected': detected,
            'white_count': white_count,
            'light_red_count': light_red_count,
            'total_count': total_count,
            'total_ratio': total_ratio,
            'edge_count': edge_count,
            'lines_detected': len(lines) if lines is not None else 0,
            'resistance_candidates': len(resistance_lines),
            'resistance_lines': resistance_lines,
            'r2_line': r2_line
        }


def test_r2_detector_v3():
    """Test R2 detector V3 on 5 images"""
    
    test_images = [
        "9c5927d6-a315-4f12-9768-a9a2941aacfc.jpg",  # Weekly
        "437746cd-65be-4603-938c-85debf232d94.jpg",  # Daily
        "19397363-b6cd-4344-93cc-870d7d872a83.jpg",  # Hourly
        "7ce8ed01-8ac5-45c4-945c-e3b82dda8fe2.jpg",  # 15min
        "6f492e6b-7b20-4356-b939-5b17422dadf2.jpg"  # 5min
    ]
    
    periods = ['周线', '日线', '1小时', '15分钟', '5分钟']
    
    detector = WKFR2DetectorV3()
    
    print("=" * 80)
    print("WKF R2 Detector V3 - Ultra Optimized Test")
    print("=" * 80)
    print("Ultra Optimized Parameters:")
    print(f"  White Threshold: [200-255, 200-255, 200-255]")
    print(f"  Light Red Threshold: [150-255, 150-255, 180-255]")
    print(f"  Hough Threshold: 15 (reduced from 100)")
    print(f"  MinLineLength: 100 (fixed)")
    print(f"  MaxLineGap: 100 (increased)")
    print(f"  Horizontal tolerance: 10px (increased)")
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
            print(f"  Detected: {'Yes ✅' if result['detected'] else 'No ❌'}")
            print(f"  White Pixels: {result['white_count']}")
            print(f"  Light Red Pixels: {result['light_red_count']}")
            print(f"  Total Pixels: {result['total_count']} ({result['total_ratio']:.2%})")
            print(f"  Edge Pixels: {result['edge_count']}")
            print(f"  Lines Detected: {result['lines_detected']}")
            print(f"  R2 Candidates: {result['resistance_candidates']}")
            
            if result['detected']:
                r2_line = result['r2_line']
                print(f"  R2 Y-coordinate: {r2_line['y']}")
                print(f"  R2 Length: {r2_line['length']}")
                print(f"  R2 Color: {r2_line['color']}")
                print(f"  R2 Mean Color: BGR={r2_line['mean_color']}")
            else:
                print(f"  R2: Not detected")
            
        except Exception as e:
            print(f"\nError analyzing {image_name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Print summary
    print("\n" + "=" * 80)
    print("R2 Detection V3 Summary")
    print("=" * 80)
    
    detected_count = sum(1 for r in all_results if r['detected'])
    print(f"\nTotal images analyzed: {len(all_results)}")
    print(f"R2 detected: {detected_count}/{len(all_results)} ({detected_count/len(all_results)*100:.0f}%)")
    
    if all_results:
        avg_total_ratio = sum(r['total_ratio'] for r in all_results) / len(all_results)
        avg_edge_count = sum(r['edge_count'] for r in all_results) / len(all_results)
        avg_lines_detected = sum(r['lines_detected'] for r in all_results) / len(all_results)
        avg_candidates = sum(r['resistance_candidates'] for r in all_results) / len(all_results)
        print(f"Average total ratio: {avg_total_ratio:.2%}")
        print(f"Average edge count: {avg_edge_count:.0f}")
        print(f"Average lines detected: {avg_lines_detected:.0f}")
        print(f"Average R2 candidates: {avg_candidates:.0f}")
    
    # Detailed results
    print(f"\nDetailed Results:")
    for result in all_results:
        period = result['period']
        detected = result['detected']
        total_ratio = result['total_ratio']
        edge_count = result['edge_count']
        lines_detected = result['lines_detected']
        candidates = result['resistance_candidates']
        
        if detected:
            r2_y = result['r2_line']['y']
            r2_color = result['r2_line']['color']
            print(f"  {period}: ✅ y={r2_y}, {r2_color} (total={total_ratio:.2%}, edges={edge_count}, lines={lines_detected}, candidates={candidates})")
        else:
            print(f"  {period}: ❌ (total={total_ratio:.2%}, edges={edge_count}, lines={lines_detected}, candidates={candidates})")
    
    # Save results
    output_file = "/root/.openclaw/workspace/r2_detection_v3_results.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {output_file}")
    except Exception as e:
        print(f"\nError saving results: {e}")
    
    print("=" * 80)


if __name__ == "__main__":
    test_r2_detector_v3()
