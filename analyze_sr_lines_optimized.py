#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SR线优化识别 - 排除K线链接线，准确识别R2（白色）和S2（绿色）
"""

import cv2
import numpy as np
import json
import os
from typing import Dict, List
import sys

sys.path.append('/root/.openclaw/workspace')


class NumpyEncoder(json.JSONEncoder):
    """Numpy类型JSON编码器"""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int32, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


class SROptimizedDetector:
    """SR线优化检测器"""

    def __init__(self):
        """初始化"""
        # 区域分割
        self.regions = {
            'main_chart': (0, int(1377 * 0.45))
        }

    def analyze_sr_lines(self, image_path: str, manual_data: Dict = None) -> Dict:
        """分析SR线"""
        print(f"\n正在分析：{os.path.basename(image_path)}")

        # 读取图像
        image = cv2.imread(image_path)
        if image is None:
            return {'success': False, 'error': '无法读取图像'}

        height, width = image.shape[:2]
        print(f"  尺寸：{width}x{height}")

        # 1. 颜色采样（学习真实的R2和S2颜色）
        print(f"\n[1] 颜色采样...")
        color_samples = self._sample_colors(image, width, height)

        # 2. 检测SR线（排除K线链接线）
        print(f"\n[2] 检测SR线...")
        sr_lines = self._detect_sr_lines_optimized(
            image, width, height, color_samples)

        # 3. 转换为价格
        print(f"\n[3] 转换为价格...")
        sr_prices = self._convert_to_prices(
            sr_lines, manual_data)

        result = {
            'success': True,
            'image_path': image_path,
            'image_name': os.path.basename(image_path),
            'color_samples': color_samples,
            'sr_lines': sr_lines,
            'sr_prices': sr_prices,
            'manual_data': manual_data
        }

        # 打印摘要
        self._print_summary(result)

        return result

    def _sample_colors(self, image: np.ndarray, width: int, height: int) -> Dict:
        """采样R2（白色）和S2（绿色）的颜色"""
        main_chart = image[self.regions['main_chart'][0]:self.regions['main_chart'][1], :]

        # 白色像素采样（R2阻力线）
        lower_white = np.array([220, 220, 220])
        upper_white = np.array([255, 255, 255])
        white_mask = cv2.inRange(main_chart, lower_white, upper_white)
        white_pixels = main_chart[white_mask > 0]

        # 绿色像素采样（S2支撑线）
        lower_green = np.array([0, 100, 0])
        upper_green = np.array([100, 255, 100])
        green_mask = cv2.inRange(main_chart, lower_green, upper_green)
        green_pixels = main_chart[green_mask > 0]

        samples = {}

        if len(white_pixels) > 0:
            white_mean = np.mean(white_pixels, axis=0)
            white_std = np.std(white_pixels, axis=0)
            samples['white_r2'] = {
                'mean': [int(white_mean[0]), int(white_mean[1]), int(white_mean[2])],
                'std': [int(white_std[0]), int(white_std[1]), int(white_std[2])],
                'count': len(white_pixels)
            }
            print(f"  R2（白色）采样：")
            print(f"    BGR均值：{samples['white_r2']['mean']}")
            print(f"    BGR标准差：{samples['white_r2']['std']}")
            print(f"    像素数量：{samples['white_r2']['count']}")

        if len(green_pixels) > 0:
            green_mean = np.mean(green_pixels, axis=0)
            green_std = np.std(green_pixels, axis=0)
            samples['green_s2'] = {
                'mean': [int(green_mean[0]), int(green_mean[1]), int(green_mean[2])],
                'std': [int(green_std[0]), int(green_std[1]), int(green_std[2])],
                'count': len(green_pixels)
            }
            print(f"  S2（绿色）采样：")
            print(f"    BGR均值：{samples['green_s2']['mean']}")
            print(f"    BGR标准差：{samples['green_s2']['std']}")
            print(f"    像素数量：{samples['green_s2']['count']}")

        return samples

    def _detect_sr_lines_optimized(self, image: np.ndarray, width: int,
                                    height: int, color_samples: Dict) -> Dict:
        """优化检测SR线（排除K线链接线）"""
        main_chart = image[self.regions['main_chart'][0]:self.regions['main_chart'][1], :]

        # 提取R2（白色）
        white_lines = []
        if 'white_r2' in color_samples:
            white_mean = color_samples['white_r2']['mean']
            white_std = color_samples['white_r2']['std']

            # 使用实际测量的颜色范围
            lower_white = np.array([
                max(white_mean[0] - white_std[0], 220),
                max(white_mean[1] - white_std[1], 220),
                max(white_mean[2] - white_std[2], 220)
            ])
            upper_white = np.array([
                min(white_mean[0] + white_std[0], 255),
                min(white_mean[1] + white_std[1], 255),
                min(white_mean[2] + white_std[2], 255)
            ])

            white_mask = cv2.inRange(main_chart, lower_white, upper_white)

            # 边缘检测
            gray = cv2.cvtColor(main_chart, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)

            # 霍夫变换检测水平线
            lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180,
                                   threshold=80, minLineLength=width * 0.4,
                                   maxLineGap=50)

            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]

                    if abs(y1 - y2) > 5 or abs(x2 - x1) < width * 0.2:
                        continue

                    # 排除K线链接线（垂直方向的斜线）
                    if abs(x2 - x1) < width * 0.3:
                        continue

                    line_pixels = main_chart[y1:y1+2, x1:x2]

                    # 计算白色像素占比
                    white_pixels = np.sum(
                        (line_pixels[:, :, 0] >= lower_white[0]) &
                        (line_pixels[:, :, 1] >= lower_white[1]) &
                        (line_pixels[:, :, 2] >= lower_white[2])
                    )

                    white_ratio = white_pixels / (line_pixels.shape[0] * line_pixels.shape[1])

                    # 白色像素占比>80%才认为是R2线
                    if white_ratio > 0.8:
                        white_lines.append({
                            'y': int(y1 + self.regions['main_chart'][0]),
                            'length': abs(x2 - x1),
                            'pixel_count': int(white_pixels),
                            'white_ratio': float(white_ratio)
                        })

        # 提取S2（绿色）
        green_lines = []
        if 'green_s2' in color_samples:
            green_mean = color_samples['green_s2']['mean']
            green_std = color_samples['green_s2']['std']

            # 使用实际测量的颜色范围
            lower_green = np.array([
                max(green_mean[0] - green_std[0], 0),
                max(green_mean[1] - green_std[1], 100),
                max(green_mean[2] - green_std[2], 0)
            ])
            upper_green = np.array([
                min(green_mean[0] + green_std[0], 100),
                min(green_mean[1] + green_std[1], 255),
                min(green_mean[2] + green_std[2], 100)
            ])

            green_mask = cv2.inRange(main_chart, lower_green, upper_green)

            # 统计每行的绿色像素
            rows, cols = main_chart.shape[:2]
            row_green_counts = np.sum(green_mask, axis=1)

            # 找到绿色像素最多的行
            if np.max(row_green_counts) > cols * 0.1:
                top_green_rows = np.argsort(row_green_counts)[-10:]

                for y_local in top_green_rows:
                    if row_green_counts[y_local] > cols * 0.15:
                        y = int(y_local + self.regions['main_chart'][0])
                        green_lines.append({
                            'y': y,
                            'pixel_count': int(row_green_counts[y_local]),
                            'green_ratio': float(row_green_counts[y_local] / cols)
                        })

        # 排序（按Y坐标）
        white_lines.sort(key=lambda x: x['y'], reverse=True)  # 从上到下
        green_lines.sort(key=lambda x: x['y'])  # 从下到上

        print(f"  R2（白色）线：{len(white_lines)}条")
        for i, line in enumerate(white_lines[:2], 1):
            print(f"    R2{i}: y={line['y']}, 长度={line['length']}, 白色占比={line['white_ratio']:.2f}")

        print(f"  S2（绿色）线：{len(green_lines)}条")
        for i, line in enumerate(green_lines[:2], 1):
            print(f"    S2{i}: y={line['y']}, 像素数={line['pixel_count']}, 绿色占比={line['green_ratio']:.2f}")

        return {
            'r2_lines': white_lines,
            's2_lines': green_lines,
            'r2_count': len(white_lines),
            's2_count': len(green_lines)
        }

    def _convert_to_prices(self, sr_lines: Dict, manual_data: Dict) -> Dict:
        """转换为价格（使用人工标注数据）"""
        prices = {}

        if manual_data and sr_lines['r2_lines']:
            r2_y = sr_lines['r2_lines'][0]['y'] if sr_lines['r2_lines'] else None
            r2_price = manual_data.get('r2', None)

            if r2_y is not None and r2_price is not None:
                prices['r2_y'] = r2_y
                prices['r2_price'] = r2_price

        if manual_data and sr_lines['s2_lines']:
            s2_y = sr_lines['s2_lines'][0]['y'] if sr_lines['s2_lines'] else None
            s2_price = manual_data.get('s2', None)

            if s2_y is not None and s2_price is not None:
                prices['s2_y'] = s2_y
                prices['s2_price'] = s2_price

        if manual_data:
            current_price = manual_data.get('current_price', None)
            if current_price is not None:
                prices['current_price'] = current_price

        print(f"\n价格映射：")
        if prices.get('r2_price'):
            print(f"  R2：Y={prices['r2_y']}, 价格={prices['r2_price']}")
        if prices.get('s2_price'):
            print(f"  S2：Y={prices['s2_y']}, 价格={prices['s2_price']}")
        if prices.get('current_price'):
            print(f"  现价：{prices['current_price']}")

        return prices

    def _print_summary(self, result: Dict):
        """打印摘要"""
        sr_prices = result.get('sr_prices', {})

        print(f"\n=== SR线识别结果 ===")

        if sr_prices.get('r2_price'):
            print(f"R2（阻力线）：{sr_prices['r2_price']}")
            print(f"  Y坐标：{sr_prices['r2_y']}")
        if sr_prices.get('s2_price'):
            print(f"S2（支撑线）：{sr_prices['s2_price']}")
            print(f"  Y坐标：{sr_prices['s2_y']}")
        if sr_prices.get('current_price'):
            print(f"现价：{sr_prices['current_price']}")


def analyze_all_5_periods():
    """分析所有5个周期"""

    # 5张图片 + 人工标注数据
    stock_data = [
        ("9c5927d6-a315-4f12-9768-a9a2941aacfc.jpg",
         {'r2': 19.20, 's2': 16.25, 'current_price': 17.99}),
        ("437746cd-65be-4603-938c-85debf232d94.jpg",
         {'r2': 18.13, 's2': 15.61, 'current_price': 17.99}),
        ("19397363-b6cd-4344-93cc-870d7d872a83.jpg",
         {'r2': 19.36, 's2': 16.25, 'current_price': 17.99}),
        ("7ce8ed01-8ac5-45c4-945c-e3b82dda8fe2.jpg",
         {'r2': 18.13, 's2': 17.33, 'current_price': 17.99}),
        ("6f492e6b-7b20-4356-b939-5b17422dadf2.jpg",
         {'r2': 17.99, 's2': 17.89, 'current_price': 17.99})
    ]

    periods = ['周线', '日线', '1小时', '15分钟', '5分钟']

    # 创建检测器
    detector = SROptimizedDetector()

    print("=" * 80)
    print("SR线优化识别 - 排除K线链接线")
    print("=" * 80)

    all_results = []

    for i, (image_name, manual_data) in enumerate(stock_data):
        image_path = f"/root/.openclaw/media/inbound/{image_name}"

        if not os.path.exists(image_path):
            print(f"\n{i+1}/{len(stock_data)} 图片不存在：{image_name}")
            continue

        print(f"\n{'='*80}")
        print(f"[{i+1}/{len(stock_data)}] {periods[i]}分析")
        print(f"{'='*80}")

        try:
            result = detector.analyze_sr_lines(image_path, manual_data)
            result['period'] = periods[i]
            all_results.append(result)

        except Exception as e:
            print(f"\n错误：{e}")
            import traceback
            traceback.print_exc()

    # 保存结果
    output_file = "/root/.openclaw/workspace/sr_lines_optimized_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)

    print("\n" + "=" * 80)
    print("SR线优化识别完成")
    print("=" * 80)
    print(f"结果已保存到：{output_file}")


if __name__ == "__main__":
    analyze_all_5_periods()
