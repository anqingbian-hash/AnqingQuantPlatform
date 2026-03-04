#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WKF系统Y坐标映射学习器
从人工标注数据学习Y坐标到价格的映射关系
"""

import cv2
import numpy as np
import json
import os
from typing import Dict, List
import sys

sys.path.append('/root/.openclaw/workspace')


class YCoordinateMapper:
    """Y坐标到价格的映射器"""

    def __init__(self):
        """初始化"""
        # 颜色阈值
        self.color_thresholds = {
            'resistance': {
                'white': {'b': (220, 255), 'g': (230, 255), 'r': (220, 255)},
                'red': {'b': (90, 100), 'g': (90, 100), 'r': (160, 170)}
            },
            'support': {
                'yellow': {'b': (20, 60), 'g': (150, 200), 'r': (150, 200)},
                'green': {'b': (40, 50), 'g': (170, 220), 'r': (40, 50)}
            },
            'current_price': {
                'yellow': {'b': (20, 60), 'g': (150, 200), 'r': (150, 200)}
            }
        }

        # 区域分割
        self.regions = {
            'main_chart': (0, int(1377 * 0.45))
        }

    def analyze_image_and_build_mapping(self, image_path: str,
                                     manual_annotation: Dict = None) -> Dict:
        """
        分析图片并建立Y坐标映射
        """
        print(f"\n正在分析：{os.path.basename(image_path)}")

        # 读取图像
        image = cv2.imread(image_path)
        if image is None:
            return {
                'success': False,
                'error': '无法读取图像'
            }

        height, width = image.shape[:2]
        print(f"  尺寸：{width}x{height}")

        # 提取主图区域
        main_chart = image[self.regions['main_chart'][0]:self.regions['main_chart'][1], :]

        # 检测R2（阻力线）- 白色
        print(f"\n[1] 检测R2（阻力线）...")
        r2_lines = self._detect_resistance_lines(main_chart, 'white')

        # 检测S2（支撑线）- 黄色
        print(f"\n[2] 检测S2（支撑线）...")
        s2_lines = self._detect_support_lines(main_chart, 'yellow')

        # 检测现价 - 黄色
        print(f"\n[3] 检测现价...")
        current_price_lines = self._detect_current_price(main_chart)

        # 建立Y坐标映射
        print(f"\n[4] 建立Y坐标映射...")
        mapping = self._build_mapping(r2_lines, s2_lines,
                                   current_price_lines, manual_annotation)

        result = {
            'success': True,
            'image_path': image_path,
            'image_name': os.path.basename(image_path),
            'r2_lines': r2_lines,
            's2_lines': s2_lines,
            'current_price_lines': current_price_lines,
            'mapping': mapping
        }

        # 打印摘要
        self._print_summary(result)

        return result

    def _detect_resistance_lines(self, image: np.ndarray, color_type: str) -> List[Dict]:
        """检测阻力线（白色或红色）"""
        if color_type == 'white':
            lower = np.array([
                self.color_thresholds['resistance']['white']['b'][0],
                self.color_thresholds['resistance']['white']['g'][0],
                self.color_thresholds['resistance']['white']['r'][0]
            ])
            upper = np.array([
                self.color_thresholds['resistance']['white']['b'][1],
                self.color_thresholds['resistance']['white']['g'][1],
                self.color_thresholds['resistance']['white']['r'][1]
            ])
        else:
            lower = np.array([
                self.color_thresholds['resistance']['red']['b'][0],
                self.color_thresholds['resistance']['red']['g'][0],
                self.color_thresholds['resistance']['red']['r'][0]
            ])
            upper = np.array([
                self.color_thresholds['resistance']['red']['b'][1],
                self.color_thresholds['resistance']['red']['g'][1],
                self.color_thresholds['resistance']['red']['r'][1]
            ])

        mask = cv2.inRange(image, lower, upper)

        # 统计每行的像素数
        rows, cols = image.shape[:2]
        row_counts = np.sum(mask, axis=1)

        # 找到像素数最多的行（水平线）
        if np.max(row_counts) < cols * 0.3:  # 如果没有足够的像素
            print(f"  未检测到阻力线（{color_type}）")
            return []

        top_rows = np.argsort(row_counts)[-5:]  # 前5个最多的行

        lines = []
        for y in top_rows:
            if row_counts[y] > cols * 0.2:  # 至少20%的宽度
                lines.append({
                    'y': int(y + self.regions['main_chart'][0]),
                    'pixel_count': int(row_counts[y]),
                    'color_type': color_type
                })

        print(f"  检测到{len(lines)}条{color_type}阻力线")
        for i, line in enumerate(lines[:2], 1):
            print(f"    阻力{i}: y={line['y']}, 像素数={line['pixel_count']}")

        return lines

    def _detect_support_lines(self, image: np.ndarray, color_type: str) -> List[Dict]:
        """检测支撑线（黄色或绿色）"""
        if color_type == 'yellow':
            lower = np.array([
                self.color_thresholds['support']['yellow']['b'][0],
                self.color_thresholds['support']['yellow']['g'][0],
                self.color_thresholds['support']['yellow']['r'][0]
            ])
            upper = np.array([
                self.color_thresholds['support']['yellow']['b'][1],
                self.color_thresholds['support']['yellow']['g'][1],
                self.color_thresholds['support']['yellow']['r'][1]
            ])
        else:
            lower = np.array([
                self.color_thresholds['support']['green']['b'][0],
                self.color_thresholds['support']['green']['g'][0],
                self.color_thresholds['support']['green']['r'][0]
            ])
            upper = np.array([
                self.color_thresholds['support']['green']['b'][1],
                self.color_thresholds['support']['green']['g'][1],
                self.color_thresholds['support']['green']['r'][1]
            ])

        mask = cv2.inRange(image, lower, upper)

        # 统计每行的像素数
        rows, cols = image.shape[:2]
        row_counts = np.sum(mask, axis=1)

        # 找到像素数最多的行（水平线）
        if np.max(row_counts) < cols * 0.3:
            print(f"  未检测到支撑线（{color_type}）")
            return []

        top_rows = np.argsort(row_counts)[-5:]

        lines = []
        for y in top_rows:
            if row_counts[y] > cols * 0.2:
                lines.append({
                    'y': int(y + self.regions['main_chart'][0]),
                    'pixel_count': int(row_counts[y]),
                    'color_type': color_type
                })

        print(f"  检测到{len(lines)}条{color_type}支撑线")
        for i, line in enumerate(lines[:2], 1):
            print(f"    支撑{i}: y={line['y']}, 像素数={line['pixel_count']}")

        return lines

    def _detect_current_price(self, image: np.ndarray) -> List[Dict]:
        """检测现价线（黄色）"""
        lower = np.array([
            self.color_thresholds['current_price']['yellow']['b'][0],
            self.color_thresholds['current_price']['yellow']['g'][0],
            self.color_thresholds['current_price']['yellow']['r'][0]
        ])
        upper = np.array([
            self.color_thresholds['current_price']['yellow']['b'][1],
            self.color_thresholds['current_price']['yellow']['g'][1],
            self.color_thresholds['current_price']['yellow']['r'][1]
        ])

        mask = cv2.inRange(image, lower, upper)

        # 统计每行的像素数
        rows, cols = image.shape[:2]
        row_counts = np.sum(mask, axis=1)

        if np.max(row_counts) < cols * 0.1:
            print(f"  未检测到现价线")
            return []

        top_row = np.argmax(row_counts)

        lines = [{
            'y': int(top_row + self.regions['main_chart'][0]),
            'pixel_count': int(row_counts[top_row]),
            'color_type': 'yellow'
        }]

        print(f"  检测到现价线：y={lines[0]['y']}, 像素数={lines[0]['pixel_count']}")

        return lines

    def _build_mapping(self, r2_lines: List[Dict], s2_lines: List[Dict],
                     current_price_lines: List[Dict],
                     manual_annotation: Dict = None) -> Dict:
        """建立Y坐标映射"""
        mapping = {
            'r2': {'y': None, 'price': None, 'detected': False},
            's2': {'y': None, 'price': None, 'detected': False},
            'current_price': {'y': None, 'price': None, 'detected': False},
            'manual_annotation': manual_annotation,
            'calibration_points': []
        }

        # 使用人工标注数据（如果有）
        if manual_annotation:
            # 找到对应的Y坐标
            if r2_lines:
                r2_y = r2_lines[0]['y']
                mapping['r2']['y'] = r2_y
                mapping['r2']['detected'] = True
                mapping['calibration_points'].append({
                    'y': r2_y,
                    'price': manual_annotation.get('r2', None),
                    'type': 'r2'
                })

            if s2_lines:
                s2_y = s2_lines[0]['y']
                mapping['s2']['y'] = s2_y
                mapping['s2']['detected'] = True
                mapping['calibration_points'].append({
                    'y': s2_y,
                    'price': manual_annotation.get('s2', None),
                    'type': 's2'
                })

            if current_price_lines:
                current_y = current_price_lines[0]['y']
                mapping['current_price']['y'] = current_y
                mapping['current_price']['detected'] = True
                mapping['calibration_points'].append({
                    'y': current_y,
                    'price': manual_annotation.get('current_price', None),
                    'type': 'current_price'
                })

        return mapping

    def _print_summary(self, result: Dict):
        """打印摘要"""
        mapping = result['mapping']

        print(f"\nY坐标映射结果：")

        if mapping['manual_annotation']:
            print(f"  人工标注：")
            print(f"    R2（阻力线）：{mapping['manual_annotation'].get('r2', '未标注')}")
            print(f"    S2（支撑线）：{mapping['manual_annotation'].get('s2', '未标注')}")
            print(f"    现价：{mapping['manual_annotation'].get('current_price', '未标注')}")

        print(f"\n  检测结果：")
        if mapping['r2']['detected']:
            print(f"    R2：y={mapping['r2']['y']}")
        else:
            print(f"    R2：未检测到")

        if mapping['s2']['detected']:
            print(f"    S2：y={mapping['s2']['y']}")
        else:
            print(f"    S2：未检测到")

        if mapping['current_price']['detected']:
            print(f"    现价：y={mapping['current_price']['y']}")
        else:
            print(f"    现价：未检测到")


def analyze_stock_5_periods():
    """分析1只股票的5个周期"""

    # 5张图片（1只股票的5个周期）
    stock_images = [
        "9c5927d6-a315-4f12-9768-a9a2941aacfc.jpg",
        "437746cd-65be-4603-938c-85debf232d94.jpg",
        "19397363-b6cd-4344-93cc-870d7d872a83.jpg",
        "7ce8ed01-8ac5-45c4-945c-e3b82dda8fe2.jpg",
        "6f492e6b-7b20-4356-b939-5b17422dadf2.jpg"
    ]

    # 周期名称
    periods = ['周线', '日线', '1小时', '15分钟', '5分钟']

    # 创建映射器
    mapper = YCoordinateMapper()

    print("=" * 80)
    print("WKF系统Y坐标映射学习")
    print("=" * 80)

    all_results = []

    for i, image_name in enumerate(stock_images):
        image_path = f"/root/.openclaw/media/inbound/{image_name}"

        if not os.path.exists(image_path):
            print(f"\n{i+1}/{len(stock_images)} 图片不存在：{image_name}")
            continue

        print(f"\n{'='*80}")
        print(f"[{i+1}/{len(stock_images)}] {periods[i]}分析")
        print(f"{'='*80}")

        # 分析（暂时不使用人工标注，先检测）
        result = mapper.analyze_image_and_build_mapping(image_path)

        if result['success']:
            all_results.append(result)

    # 保存结果
    output_file = "/root/.openclaw/workspace/y_coordinate_mapping_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("Y坐标映射学习完成")
    print("=" * 80)
    print(f"结果已保存到：{output_file}")
    print("\n请卞董为每个周期提供人工标注数据：")
    print("  格式：{周期名: R2=39.5, S2=36.53, 现价=36.39}")


if __name__ == "__main__":
    analyze_stock_5_periods()
