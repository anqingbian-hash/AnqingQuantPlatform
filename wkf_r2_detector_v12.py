#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WKF R2 Line Detector V12 - Period Specific & Short Line Tolerant
周期特异性与短线条容忍版 - 针对不同周期使用不同参数，降低短线条惩罚
"""

import cv2
import numpy as np
import json
import os
from typing import Dict, List, Tuple

class WKFR2DetectorV12:
    """R2 (Resistance Line) Detector V12 - Period Specific & Short Line Tolerant"""
    
    def __init__(self):
        """Initialize detector with period specific parameters"""
        self.regions = {
            'main_chart': (0, int(1377 * 0.45))
        }
        
        # Hough parameters
        self.hough_params = {
            'rho': 1,
            'theta': np.pi/180,
            'threshold': 10,
            'minLineLength': 100,
            'maxLineGap': 100
        }
        
        # Period specific parameters
        self.period_params = {
            '周线': {
                'length_range': (150, 800),      # 短线条容忍（周线R2可能很短）
                'optimal_length': (200, 500),   # 最优长度
                'edge_density_threshold': 0.08,  # 降低阈值
                'weights': {
                    'edge_density': 0.25,
                    'line_length': 0.25,
                    'grid_penalty': 0.20,
                    'brightness': 0.15,
                    'position': 0.10,
                    'color': 0.05
                }
            },
            '日线': {
                'length_range': (200, 1000),
                'optimal_length': (300, 700),
                'edge_density_threshold': 0.10,
                'weights': {
                    'edge_density': 0.25,
                    'line_length': 0.25,
                    'grid_penalty': 0.20,
                    'brightness': 0.15,
                    'position': 0.10,
                    'color': 0.05
                }
            },
            '1小时': {
                'length_range': (300, 1200),
                'optimal_length': (400, 800),
                'edge_density_threshold': 0.08,
                'weights': {
                    'edge_density': 0.25,
                    'line_length': 0.25,
                    'grid_penalty': 0.20,
                    'brightness': 0.15,
                    'position': 0.10,
                    'color': 0.05
                }
            },
            '15分钟': {
                'length_range': (200, 1000),
                'optimal_length': (300, 600),
                'edge_density_threshold': 0.08,
                'weights': {
                    'edge_density': 0.25,
                    'line_length': 0.25,
                    'grid_penalty': 0.20,
                    'brightness': 0.15,
                    'position': 0.10,
                    'color': 0.05
                }
            },
            '5分钟': {
                'length_range': (300, 1200),
                'optimal_length': (400, 700),
                'edge_density_threshold': 0.08,
                'weights': {
                    'edge_density': 0.25,
                    'line_length': 0.25,
                    'grid_penalty': 0.20,
                    'brightness': 0.15,
                    'position': 0.10,
                    'color': 0.05
                }
            }
        }
        
        self.grid_line_threshold = 2000
    
    def detect_r2_line(self, image_path: str, period: str) -> Dict:
        """Detect R2 (resistance line) using period specific parameters"""
        print(f"\n[R2 Detection V12] Analyzing: {os.path.basename(image_path)}")
        print(f"  Period: {period}")
        
        # Get period specific parameters
        period_params = self.period_params.get(period, self.period_params['日线'])
        
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            return {
                'success': False,
                'error': 'Cannot read image',
                'detected': False,
                'period': period
            }
        
        height, width = image.shape[:2]
        main_chart = image[self.regions['main_chart'][0]:self.regions['main_chart'][1], :]
        main_chart_height = main_chart.shape[0]
        
        # [1] Edge detection
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
                'lines_detected': 0,
                'period': period
            }
        
        print(f"    Lines detected: {len(lines)}")
        
        # [3] Analyze all horizontal lines with period specific parameters
        print("  [3] Analyzing horizontal lines with period specific parameters...")
        
        horizontal_lines = []
        
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
            y_center = int((y1 + y2) / 2)
            line_pixels = main_chart[max(0, y_center-3):min(main_chart.shape[0], y_center+4), x1:x2]
            
            if line_pixels.size == 0:
                continue
            
            # Analyze color
            mean_color = np.mean(line_pixels, axis=(0, 1))
            b, g, r = mean_color
            brightness = (b + g + r) / 3
            
            # Classify color
            color_category = self._classify_color(b, g, r)
            
            # Calculate edge density
            edge_density = self._calculate_edge_density(edges, y_center, line_length, main_chart_width=width)
            
            # Detect nearby grid lines
            nearby_max_length = self._detect_nearby_max_length(lines, y_center)
            has_grid_line = nearby_max_length > self.grid_line_threshold
            
            # Calculate period specific score
            score = self._calculate_period_specific_score(
                line_length, brightness, y_center, main_chart_height, color_category,
                has_grid_line, nearby_max_length, edge_density, period_params
            )
            
            horizontal_lines.append({
                'y': int(y_center + self.regions['main_chart'][0]),
                'length': line_length,
                'x1': int(x1),
                'x2': int(x2),
                'mean_color': [float(b), float(g), float(r)],
                'brightness': brightness,
                'color_category': color_category,
                'has_grid_line': has_grid_line,
                'nearby_max_length': nearby_max_length,
                'edge_density': edge_density,
                'score': score
            })
        
        print(f"    Valid horizontal lines: {len(horizontal_lines)}")
        
        # [4] Select R2 candidate (highest period specific score)
        print("  [4] Selecting R2 candidate (highest period specific score)...")
        
        if horizontal_lines:
            # Sort by period specific score (highest first)
            horizontal_lines.sort(key=lambda x: x['score'], reverse=True)
            
            # Select top 5 candidates
            top_candidates = horizontal_lines[:5]
            
            r2_line = top_candidates[0]
            detected = True
            
            print(f"    Result: R2 detected (highest period specific score)")
            print(f"      Top 5 candidates:")
            for i, candidate in enumerate(top_candidates, 1):
                grid_status = "⚠️ GRID" if candidate['has_grid_line'] else "✓ NO GRID"
                print(f"        {i}. y={candidate['y']}, length={candidate['length']}, score={candidate['score']:.2f}, {grid_status}, edge_density={candidate['edge_density']:.3f}")
        else:
            r2_line = None
            detected = False
            print(f"    Result: No R2 detected (no valid horizontal lines)")
        
        return {
            'success': True,
            'detected': detected,
            'edge_count': edge_count,
            'lines_detected': len(lines) if lines is not None else 0,
            'valid_horizontal_lines': len(horizontal_lines),
            'top_candidates': top_candidates if detected else [],
            'r2_line': r2_line,
            'period': period,
            'period_params': period_params
        }
    
    def _calculate_edge_density(self, edges: np.ndarray, y_center: int, line_length: int, main_chart_width: int) -> float:
        """Calculate edge density for the line"""
        roi_y_start = max(0, y_center - 3)
        roi_y_end = min(edges.shape[0], y_center + 4)
        roi = edges[roi_y_start:roi_y_end, :]
        
        edge_pixels_in_roi = int(np.sum(roi > 0))
        roi_area = (roi_y_end - roi_y_start) * main_chart_width
        edge_density = edge_pixels_in_roi / roi_area if roi_area > 0 else 0.0
        
        return edge_density
    
    def _detect_nearby_max_length(self, lines: np.ndarray, y_center: int) -> int:
        """Detect maximum line length near y_center (within 10px)"""
        max_length = 0
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(y1 - y2) <= 5:
                y_line = int((y1 + y2) / 2)
                if abs(y_line - y_center) <= 10:
                    line_length = abs(x2 - x1)
                    if line_length > max_length:
                        max_length = line_length
        
        return max_length
    
    def _calculate_period_specific_score(self, length: float, brightness: float, y: int, 
                                           chart_height: int, color_category: str,
                                           has_grid_line: bool, nearby_max_length: int,
                                           edge_density: float, period_params: Dict) -> float:
        """Calculate period specific score for R2 candidate"""
        
        weights = period_params['weights']
        length_range = period_params['length_range']
        optimal_length = period_params['optimal_length']
        edge_density_threshold = period_params['edge_density_threshold']
        
        score = 0.0
        
        # [1] Edge density (using period specific threshold)
        if edge_density >= edge_density_threshold + 0.04:
            edge_density_score = 1.0
        elif edge_density >= edge_density_threshold + 0.02:
            edge_density_score = 0.9
        elif edge_density >= edge_density_threshold:
            edge_density_score = 0.8
        elif edge_density >= edge_density_threshold - 0.02:
            edge_density_score = 0.6
        else:
            edge_density_score = 0.4
        score += edge_density_score * weights['edge_density']
        
        # [2] Line length (period specific, short line tolerant)
        min_len, max_len = length_range
        opt_min, opt_max = optimal_length
        
        if length < min_len:
            # 低于最小长度，但给予一定分数（V12改进）
            length_score = 0.5
        elif length < opt_min:
            length_score = 0.8
        elif opt_min <= length <= opt_max:
            length_score = 1.0  # 最优范围
        elif length <= max_len:
            length_score = 0.8
        elif length <= max_len + 500:
            length_score = 0.6
        else:  # > max_len + 500
            length_score = 0.4  # 网格线，但仍给分
        score += length_score * weights['line_length']
        
        # [3] Grid line penalty (unchanged)
        if has_grid_line:
            grid_penalty_score = 0.6
        else:
            grid_penalty_score = 1.0
        score += grid_penalty_score * weights['grid_penalty']
        
        # [4] Brightness score (unchanged)
        if brightness <= 20:
            brightness_score = 1.0
        elif brightness <= 50:
            brightness_score = 0.8
        elif brightness <= 100:
            brightness_score = 0.5
        elif brightness <= 180:
            brightness_score = 0.2
        else:
            brightness_score = 0.0
        score += brightness_score * weights['brightness']
        
        # [5] Position score (restored to 0.1)
        normalized_y = y / chart_height
        position_score = 1.0 - normalized_y
        score += position_score * weights['position']
        
        # [6] Color score (unchanged)
        if color_category == 'black':
            color_score = 1.0
        elif color_category == 'dark_gray':
            color_score = 0.8
        elif color_category == 'gray':
            color_score = 0.5
        elif color_category == 'light_gray':
            color_score = 0.2
        else:
            color_score = 0.0
        score += color_score * weights['color']
        
        return score
    
    def _classify_color(self, b: float, g: float, r: float) -> str:
        """Classify color based on BGR values"""
        brightness = (b + g + r) / 3
        
        if brightness <= 20:
            return 'black'
        elif brightness <= 50:
            return 'dark_gray'
        elif brightness <= 100:
            return 'gray'
        elif brightness <= 180:
            return 'light_gray'
        else:
            return 'white'


def test_r2_detector_v12():
    """Test R2 detector V12 on 5 images"""
    
    test_images = [
        ("9c5927d6-a315-4f12-9768-a9a2941aacfc.jpg", "周线"),
        ("437746cd-65be-4603-938c-85debf232d94.jpg", "日线"),
        ("19397363-b6cd-4344-93cc-870d7d872a83.jpg", "1小时"),
        ("7ce8ed01-8ac5-45c4-945c-e3b82dda8fe2.jpg", "15分钟"),
        ("6f492e6b-7b20-4356-b939-5b17422dadf2.jpg", "5分钟")
    ]
    
    detector = WKFR2DetectorV12()
    
    print("=" * 80)
    print("WKF R2 Detector V12 - Period Specific & Short Line Tolerant")
    print("=" * 80)
    print("V12 Improvements:")
    print("  1. Period specific parameters (different for each period)")
    print("  2. Short line tolerance (150-800px for 周线)")
    print("  3. Lowered edge density threshold (0.08 for most periods)")
    print("  4. Restored position weight to 0.1 (V11: 0.05 -> V12: 0.1)")
    print("\nPeriod Specific Parameters:")
    for period, params in detector.period_params.items():
        print(f"  {period}: length={params['length_range']}, optimal={params['optimal_length']}, edge_threshold={params['edge_density_threshold']}")
    print("=" * 80)
    
    all_results = []
    
    for i, (image_name, period) in enumerate(test_images, 1):
        image_path = f"/root/.openclaw/media/inbound/{image_name}"
        
        if not os.path.exists(image_path):
            print(f"\n[{i}/{len(test_images)}] Image not found: {image_name}")
            continue
        
        print(f"\n{'='*80}")
        print(f"[{i}/{len(test_images)}] {period} - {image_name}")
        print(f"{'='*80}")
        
        try:
            result = detector.detect_r2_line(image_path, period)
            all_results.append({
                'period': period,
                'image_name': image_name,
                'detected': result['detected'],
                'edge_count': result['edge_count'],
                'lines_detected': result['lines_detected'],
                'valid_horizontal_lines': result['valid_horizontal_lines'],
                'top_candidates': [
                    {
                        'y': c['y'],
                        'length': c['length'],
                        'score': c['score'],
                        'color_category': c['color_category'],
                        'brightness': c['brightness'],
                        'has_grid_line': c['has_grid_line'],
                        'nearby_max_length': c['nearby_max_length'],
                        'edge_density': c['edge_density']
                    }
                    for c in result['top_candidates']
                ],
                'r2_line': {
                    'y': result['r2_line']['y'],
                    'length': result['r2_line']['length'],
                    'score': result['r2_line']['score'],
                    'color_category': result['r2_line']['color_category'],
                    'brightness': result['r2_line']['brightness'],
                    'has_grid_line': result['r2_line']['has_grid_line'],
                    'nearby_max_length': result['r2_line']['nearby_max_length'],
                    'edge_density': result['r2_line']['edge_density']
                } if result['detected'] else None
            })
            
            # Print summary
            print(f"\nR2 Detection Summary for {period}:")
            print(f"  Detected: {'Yes ✅' if result['detected'] else 'No ❌'}")
            print(f"  Top Candidates: {len(result['top_candidates'])}")
            
            if result['detected']:
                r2_line = result['r2_line']
                print(f"  R2 Y-coordinate: {r2_line['y']}")
                print(f"  R2 Length: {r2_line['length']}")
                print(f"  R2 Score: {r2_line['score']:.2f}")
                print(f"  R2 Color: {r2_line['color_category']}")
                print(f"  R2 Brightness: {r2_line['brightness']:.0f}")
                print(f"  Has Grid Line: {r2_line['has_grid_line']}")
                print(f"  Max Nearby Length: {r2_line['nearby_max_length']}")
                print(f"  Edge Density: {r2_line['edge_density']:.3f}")
                
                # Compare with manual annotation
                print(f"\n  Comparison with Manual Annotation:")
                manual_r2 = {
                    '周线': 19.20,
                    '日线': 18.13,
                    '1小时': 19.36,
                    '15分钟': 18.13,
                    '5分钟': 17.99
                }.get(period, None)
                
                if manual_r2:
                    print(f"    Manual R2: {manual_r2}")
                    price_mapping = {
                        '周线': {'eff': 0.024471, 'int': 14.134588},
                        '日线': {'eff': 0.007228, 'int': 15.918152},
                        '1小时': {'eff': 0.006935, 'int': 16.273932},
                        '15分钟': {'eff': 0.001068, 'int': 17.529682},
                        '5分钟': {'eff': 0.000485, 'int': 17.880777}
                    }.get(period, None)
                    
                    if price_mapping:
                        estimated_price = price_mapping['eff'] * r2_line['y'] + price_mapping['int']
                        print(f"    Estimated Price: {estimated_price:.2f}")
                        print(f"    Error: {abs(estimated_price - manual_r2):.2f} ({abs(estimated_price - manual_r2)/manual_r2*100:.1f}%)")
            else:
                print(f"  R2: Not detected")
            
        except Exception as e:
            print(f"\nError analyzing {image_name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Print summary
    print("\n" + "=" * 80)
    print("R2 Detection V12 Summary")
    print("=" * 80)
    
    detected_count = sum(1 for r in all_results if r['detected'])
    print(f"\nTotal images analyzed: {len(all_results)}")
    print(f"R2 detected: {detected_count}/{len(all_results)} ({detected_count/len(all_results)*100:.0f}%)")
    
    # Accuracy calculation
    if all_results:
        print(f"\nAccuracy Analysis (vs Manual Annotations):")
        total_error = 0
        total_manual = 0
        accurate_count = 0
        grid_line_count = 0
        
        for result in all_results:
            if result['detected']:
                period = result['period']
                r2_y = result['r2_line']['y']
                has_grid = result['r2_line']['has_grid_line']
                edge_density = result['r2_line']['edge_density']
                
                if has_grid:
                    grid_line_count += 1
                
                manual_r2_price = {
                    '周线': 19.20,
                    '日线': 18.13,
                    '1小时': 19.36,
                    '15分钟': 18.13,
                    '5分钟': 17.99
                }.get(period, None)
                
                price_mapping = {
                    '周线': {'eff': 0.024471, 'int': 14.134588},
                    '日线': {'eff': 0.007228, 'int': 15.918152},
                    '1小时': {'eff': 0.006935, 'int': 16.273932},
                    '15分钟': {'eff': 0.001068, 'int': 17.529682},
                    '5分钟': {'eff': 0.000485, 'int': 17.880777}
                }.get(period, None)
                
                if manual_r2_price and price_mapping:
                    estimated_price = price_mapping['eff'] * r2_y + price_mapping['int']
                    error = abs(estimated_price - manual_r2_price)
                    error_pct = error / manual_r2_price * 100
                    
                    total_error += error
                    total_manual += manual_r2_price
                    
                    if error_pct < 5.0:
                        accurate_count += 1
                    
                    grid_status = "GRID" if has_grid else "NO GRID"
                    print(f"  {period}: error={error:.2f} ({error_pct:.1f}%), {grid_status}, edge_density={edge_density:.3f}")
        
        if total_manual > 0:
            avg_error_pct = (total_error / total_manual) * 100
            accuracy_pct = (accurate_count / len(all_results)) * 100
            grid_line_pct = (grid_line_count / len(all_results)) * 100
            print(f"\nAverage Error: {avg_error_pct:.1f}%")
            print(f"Accuracy (<5% error): {accurate_count}/{len(all_results)} ({accuracy_pct:.0f}%)")
            print(f"Grid Line Count: {grid_line_count}/{len(all_results)} ({grid_line_pct:.0f}%)")
    
    # Detailed results
    print(f"\nDetailed Results:")
    for result in all_results:
        period = result['period']
        detected = result['detected']
        valid_lines = result['valid_horizontal_lines']
        
        if detected:
            r2_y = result['r2_line']['y']
            r2_color = result['r2_line']['color_category']
            r2_score = result['r2_line']['score']
            r2_edge_density = result['r2_line']['edge_density']
            print(f"  {period}: ✅ y={r2_y}, {r2_color}, score={r2_score:.2f}, edge_density={r2_edge_density:.3f} (valid_lines={valid_lines})")
        else:
            print(f"  {period}: ❌ (valid_lines={valid_lines})")
    
    # Save results
    output_file = "/root/.openclaw/workspace/r2_detection_v12_results.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {output_file}")
    except Exception as e:
        print(f"\nError saving results: {e}")
    
    print("=" * 80)


if __name__ == "__main__":
    test_r2_detector_v12()
