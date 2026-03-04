#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WKF R2 Line Detector V4 - Intelligent Clustering
智能聚类版R2（阻力线）识别器
"""

import cv2
import numpy as np
import json
import os
from typing import Dict, List, Tuple
from collections import defaultdict

class WKFR2DetectorV4:
    """R2 (Resistance Line) Detector V4 - Intelligent Clustering"""
    
    def __init__(self):
        """Initialize detector with intelligent clustering"""
        self.regions = {
            'main_chart': (0, int(1377 * 0.45))
        }
        
        # Intelligent Hough parameters
        self.hough_params = {
            'rho': 1,
            'theta': np.pi/180,
            'threshold': 15,
            'minLineLength': 100,
            'maxLineGap': 100
        }
    
    def detect_r2_line(self, image_path: str) -> Dict:
        """Detect R2 (resistance line) using intelligent clustering"""
        print(f"\n[R2 Detection V4] Analyzing: {os.path.basename(image_path)}")
        
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
        
        # [1] Edge detection (on full grayscale)
        print("  [1] Edge detection...")
        gray = cv2.cvtColor(main_chart, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 30, 100, apertureSize=3)
        
        edge_count = int(np.sum(edges > 0))
        print(f"    Edge pixels: {edge_count}")
        
        # [2] Hough line detection
        print(f"  [2] Hough line detection...")
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
                'edge_count': edge_count,
                'lines_detected': 0
            }
        
        print(f"    Lines detected: {len(lines)}")
        
        # [3] Analyze all lines and group by color
        print("  [3] Analyzing all lines and clustering by color...")
        
        line_analysis = []
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # Must be horizontal (y1 ≈ y2)
            if abs(y1 - y2) > 10:
                continue
            
            # Must be long enough
            line_length = abs(x2 - x1)
            if line_length < self.hough_params['minLineLength']:
                continue
            
            # Extract line pixels for color analysis
            line_pixels = main_chart[max(0, y1-3):min(main_chart.shape[0], y1+4), x1:x2]
            
            if line_pixels.size == 0:
                continue
            
            # Analyze color
            mean_color = np.mean(line_pixels, axis=(0, 1))
            b, g, r = mean_color
            std_color = np.std(line_pixels, axis=(0, 1))
            
            # Color category
            color_category = self._classify_color(b, g, r, std_color)
            
            line_analysis.append({
                'y': int(y1 + self.regions['main_chart'][0]),
                'length': line_length,
                'x1': int(x1),
                'x2': int(x2),
                'mean_color': [float(b), float(g), float(r)],
                'std_color': [float(std_color[0]), float(std_color[1]), float(std_color[2])],
                'color_category': color_category
            })
        
        print(f"    Valid horizontal lines: {len(line_analysis)}")
        
        # [4] Cluster lines by color category
        print("  [4] Clustering lines by color...")
        
        color_clusters = defaultdict(list)
        for line in line_analysis:
            color_clusters[line['color_category']].append(line)
        
        print(f"    Color clusters found:")
        for color, lines in color_clusters.items():
            avg_length = sum(l['length'] for l in lines) / len(lines)
            print(f"      {color}: {len(lines)} lines, avg_length={avg_length:.0f}")
        
        # [5] Select best R2 candidate
        print("  [5] Selecting best R2 candidate...")
        
        # Prioritize: longest line in brightest color category
        r2_candidates = []
        
        # Bright color categories (more likely to be R2)
        bright_categories = ['white', 'light_gray', 'light_red', 'yellow']
        
        for category in bright_categories:
            if category in color_clusters:
                # Find longest line in this category
                category_lines = color_clusters[category]
                longest_line = max(category_lines, key=lambda x: x['length'])
                r2_candidates.append(longest_line)
        
        # Sort candidates by length (longest first)
        r2_candidates.sort(key=lambda x: x['length'], reverse=True)
        
        # [6] Return result
        if r2_candidates:
            r2_line = r2_candidates[0]
            detected = True
            print(f"    Result: R2 detected at y={r2_line['y']}, length={r2_line['length']}, color={r2_line['color_category']}")
        else:
            r2_line = None
            detected = False
            print(f"    Result: No R2 detected (no suitable color clusters)")
        
        return {
            'success': True,
            'detected': detected,
            'edge_count': edge_count,
            'lines_detected': len(lines) if lines is not None else 0,
            'valid_horizontal_lines': len(line_analysis),
            'color_clusters': {k: len(v) for k, v in color_clusters.items()},
            'r2_candidates': len(r2_candidates),
            'r2_line': r2_line
        }
    
    def _classify_color(self, b: float, g: float, r: float, std: np.ndarray) -> str:
        """Classify color based on BGR values and standard deviation"""
        b_std, g_std, r_std = std
        
        # Calculate brightness
        brightness = (b + g + r) / 3
        brightness_std = (b_std + g_std + r_std) / 3
        
        # White (all channels high, low std)
        if brightness >= 200 and brightness_std < 30:
            return 'white'
        
        # Light gray (all channels medium-high, low std)
        elif brightness >= 150 and brightness_std < 30:
            return 'light_gray'
        
        # Gray (all channels medium, low std)
        elif brightness >= 100 and brightness < 150 and brightness_std < 30:
            return 'gray'
        
        # Dark gray (all channels low-medium, low std)
        elif brightness >= 50 and brightness < 100 and brightness_std < 30:
            return 'dark_gray'
        
        # Black (all channels low, low std)
        elif brightness < 50 and brightness_std < 30:
            return 'black'
        
        # Red (red channel high, others low)
        elif r >= 150 and g <= 100 and b <= 100:
            return 'red'
        
        # Light red (red channel high, green medium, blue medium-high)
        elif r >= 150 and g >= 100 and b >= 150:
            return 'light_red'
        
        # Green (green channel high, others low)
        elif g >= 150 and r <= 100 and b <= 100:
            return 'green'
        
        # Yellow (red and green high, blue low)
        elif r >= 150 and g >= 150 and b <= 100:
            return 'yellow'
        
        # Blue (blue channel high, others low)
        elif b >= 150 and r <= 100 and g <= 100:
            return 'blue'
        
        else:
            return 'colorful'


def test_r2_detector_v4():
    """Test R2 detector V4 on 5 images"""
    
    test_images = [
        "9c5927d6-a315-4f12-9768-a9a2941aacfc.jpg",  # Weekly
        "437746cd-65be-4603-938c-85debf232d94.jpg",  # Daily
        "19397363-b6cd-4344-93cc-870d7d872a83.jpg",  # Hourly
        "7ce8ed01-8ac5-45c4-945c-e3b82dda8fe2.jpg",  # 15min
        "6f492e6b-7b20-4356-b939-5b17422dadf2.jpg"  # 5min
    ]
    
    periods = ['周线', '日线', '1小时', '15分钟', '5分钟']
    
    detector = WKFR2DetectorV4()
    
    print("=" * 80)
    print("WKF R2 Detector V4 - Intelligent Clustering Test")
    print("=" * 80)
    print("Intelligent Clustering Parameters:")
    print(f"  Hough Threshold: 15")
    print(f"  MinLineLength: 100")
    print(f"  MaxLineGap: 100")
    print(f"  Horizontal tolerance: 10px")
    print(f"  Color clustering: By mean color and std dev")
    print(f"  Bright color categories: white, light_gray, light_red, yellow")
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
            print(f"  Edge Pixels: {result['edge_count']}")
            print(f"  Lines Detected: {result['lines_detected']}")
            print(f"  Valid Horizontal Lines: {result['valid_horizontal_lines']}")
            print(f"  Color Clusters: {result['color_clusters']}")
            print(f"  R2 Candidates: {result['r2_candidates']}")
            
            if result['detected']:
                r2_line = result['r2_line']
                print(f"  R2 Y-coordinate: {r2_line['y']}")
                print(f"  R2 Length: {r2_line['length']}")
                print(f"  R2 Color: {r2_line['color_category']}")
                print(f"  R2 Mean Color: BGR={r2_line['mean_color']}")
                print(f"  R2 Std Dev: BGR={r2_line['std_color']}")
            else:
                print(f"  R2: Not detected")
            
        except Exception as e:
            print(f"\nError analyzing {image_name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Print summary
    print("\n" + "=" * 80)
    print("R2 Detection V4 Summary")
    print("=" * 80)
    
    detected_count = sum(1 for r in all_results if r['detected'])
    print(f"\nTotal images analyzed: {len(all_results)}")
    print(f"R2 detected: {detected_count}/{len(all_results)} ({detected_count/len(all_results)*100:.0f}%)")
    
    if all_results:
        avg_edge_count = sum(r['edge_count'] for r in all_results) / len(all_results)
        avg_lines_detected = sum(r['lines_detected'] for r in all_results) / len(all_results)
        avg_valid_lines = sum(r['valid_horizontal_lines'] for r in all_results) / len(all_results)
        avg_candidates = sum(r['r2_candidates'] for r in all_results) / len(all_results)
        print(f"Average edge count: {avg_edge_count:.0f}")
        print(f"Average lines detected: {avg_lines_detected:.0f}")
        print(f"Average valid horizontal lines: {avg_valid_lines:.0f}")
        print(f"Average R2 candidates: {avg_candidates:.0f}")
    
    # Detailed results
    print(f"\nDetailed Results:")
    for result in all_results:
        period = result['period']
        detected = result['detected']
        edge_count = result['edge_count']
        lines_detected = result['lines_detected']
        candidates = result['r2_candidates']
        
        if detected:
            r2_y = result['r2_line']['y']
            r2_color = result['r2_line']['color_category']
            r2_length = result['r2_line']['length']
            print(f"  {period}: ✅ y={r2_y}, {r2_color}, length={r2_length} (edges={edge_count}, lines={lines_detected}, candidates={candidates})")
        else:
            print(f"  {period}: ❌ (edges={edge_count}, lines={lines_detected}, candidates={candidates})")
    
    # Save results
    output_file = "/root/.openclaw/workspace/r2_detection_v4_results.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {output_file}")
    except Exception as e:
        print(f"\nError saving results: {e}")
    
    print("=" * 80)


if __name__ == "__main__":
    test_r2_detector_v4()
