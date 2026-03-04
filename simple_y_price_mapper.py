#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WKF系统Y坐标到价格的精确映射模型（简化版）
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


class SimpleYPriceMapper:
    """简化的Y坐标到价格映射器"""

    def __init__(self):
        """初始化"""
        # 颜色阈值
        self.color_thresholds = {
            'resistance_white': {'b': (220, 255), 'g': (230, 255), 'r': (220, 255)},
            'support_yellow': {'b': (20, 60), 'g': (150, 200), 'r': (150, 200)},
            'current_price_yellow': {'b': (20, 60), 'g': (150, 200), 'r': (150, 200)}
        }

        # 区域分割
        self.regions = {
            'main_chart': (0, int(1377 * 0.45))
        }

    def build_mapping_model(self, image_path: str, manual_data: Dict) -> Dict:
        """构建映射模型"""
        print(f"\n正在分析：{os.path.basename(image_path)}")

        # 读取图像
        image = cv2.imread(image_path)
        if image is None:
            return {'success': False, 'error': '无法读取图像'}

        # 提取主图区域
        main_chart = image[self.regions['main_chart'][0]:self.regions['main_chart'][1], :]

        # 检测R2（白色阻力线）
        r2_y = self._detect_white_resistance(main_chart)

        # 检测S2（黄色支撑线）
        s2_y = self._detect_yellow_support(main_chart)

        # 检测现价（黄色）
        current_y = self._detect_yellow_current_price(main_chart)

        # 收集校准点
        calibration_points = []
        if r2_y is not None and manual_data.get('r2') is not None:
            calibration_points.append({'y': r2_y, 'price': manual_data['r2'], 'type': 'r2'})
        if s2_y is not None and manual_data.get('s2') is not None:
            calibration_points.append({'y': s2_y, 'price': manual_data['s2'], 'type': 's2'})
        if current_y is not None and manual_data.get('current_price') is not None:
            calibration_points.append({'y': current_y, 'price': manual_data['current_price'], 'type': 'current_price'})

        # 构建映射模型（简单的线性插值）
        mapping_model = self._build_simple_mapping(calibration_points)

        result = {
            'success': True,
            'image_path': image_path,
            'image_name': os.path.basename(image_path),
            'detected_y_coords': {
                'r2_y': r2_y,
                's2_y': s2_y,
                'current_y': current_y
            },
            'manual_data': manual_data,
            'calibration_points': calibration_points,
            'mapping_model': mapping_model
        }

        # 打印结果
        self._print_result(result)

        return result

    def _detect_white_resistance(self, image: np.ndarray) -> int:
        """检测白色阻力线（R2）"""
        lower = np.array([
            self.color_thresholds['resistance_white']['b'][0],
            self.color_thresholds['resistance_white']['g'][0],
            self.color_thresholds['resistance_white']['r'][0]
        ])
        upper = np.array([
            self.color_thresholds['resistance_white']['b'][1],
            self.color_thresholds['resistance_white']['g'][1],
            self.color_thresholds['resistance_white']['r'][1]
        ])

        mask = cv2.inRange(image, lower, upper)
        row_counts = np.sum(mask, axis=1)

        if np.max(row_counts) < image.shape[1] * 0.2:
            return None

        top_rows = np.argsort(row_counts)[-3:]
        y_local = top_rows[-1]

        return int(y_local + self.regions['main_chart'][0])

    def _detect_yellow_support(self, image: np.ndarray) -> int:
        """检测黄色支撑线（S2）"""
        lower = np.array([
            self.color_thresholds['support_yellow']['b'][0],
            self.color_thresholds['support_yellow']['g'][0],
            self.color_thresholds['support_yellow']['r'][0]
        ])
        upper = np.array([
            self.color_thresholds['support_yellow']['b'][1],
            self.color_thresholds['support_yellow']['g'][1],
            self.color_thresholds['support_yellow']['r'][1]
        ])

        mask = cv2.inRange(image, lower, upper)
        row_counts = np.sum(mask, axis=1)

        if np.max(row_counts) < image.shape[1] * 0.1:
            return None

        top_rows = np.argsort(row_counts)[-3:]
        y_local = top_rows[-1]

        return int(y_local + self.regions['main_chart'][0])

    def _detect_yellow_current_price(self, image: np.ndarray) -> int:
        """检测黄色现价线"""
        lower = np.array([
            self.color_thresholds['current_price_yellow']['b'][0],
            self.color_thresholds['current_price_yellow']['g'][0],
            self.color_thresholds['current_price_yellow']['r'][0]
        ])
        upper = np.array([
            self.color_thresholds['current_price_yellow']['b'][1],
            self.color_thresholds['current_price_yellow']['g'][1],
            self.color_thresholds['current_price_yellow']['r'][1]
        ])

        mask = cv2.inRange(image, lower, upper)
        row_counts = np.sum(mask, axis=1)

        if np.max(row_counts) < image.shape[1] * 0.1:
            return None

        y_local = np.argmax(row_counts)

        return int(y_local + self.regions['main_chart'][0])

    def _build_simple_mapping(self, calibration_points: List[Dict]) -> Dict:
        """构建简单的线性映射模型"""
        if len(calibration_points) < 2:
            return {'model_type': 'none', 'error': '校准点不足（需要≥2个）'}

        # 计算线性回归系数
        y_values = np.array([cp['y'] for cp in calibration_points])
        prices = np.array([cp['price'] for cp in calibration_points])

        # 最小二乘法
        n = len(y_values)
        sum_y = np.sum(y_values)
        sum_price = np.sum(prices)
        sum_y_price = np.sum(y_values * prices)
        sum_y2 = np.sum(y_values ** 2)

        denominator = n * sum_y2 - sum_y ** 2
        if denominator == 0:
            return {'model_type': 'none', 'error': '无法计算线性回归'}

        coefficient = (n * sum_y_price - sum_y * sum_price) / denominator
        intercept = (sum_price - coefficient * sum_y) / n

        # 验证映射准确性
        validation = {}
        for cp in calibration_points:
            y = cp['y']
            actual_price = cp['price']
            predicted_price = coefficient * y + intercept
            error = abs(predicted_price - actual_price)

            validation[cp['type']] = {
                'y': y,
                'actual_price': actual_price,
                'predicted_price': float(predicted_price),
                'error': float(error),
                'error_percentage': float(error / actual_price * 100) if actual_price != 0 else 0
            }

        return {
            'model_type': 'linear_regression',
            'coefficient': float(coefficient),
            'intercept': float(intercept),
            'r_squared': float(self._calculate_r_squared(y_values, prices, coefficient, intercept)),
            'validation': validation
        }

    def _calculate_r_squared(self, y_values, prices, coefficient, intercept):
        """计算R²"""
        predicted = coefficient * y_values + intercept
        ss_total = np.sum((prices - np.mean(prices)) ** 2)
        ss_residual = np.sum((prices - predicted) ** 2)

        if ss_total == 0:
            return 1.0

        return 1 - (ss_residual / ss_total)

    def _print_result(self, result: Dict):
        """打印结果"""
        print(f"\n检测结果：")
        y_coords = result['detected_y_coords']
        print(f"  R2 Y坐标：{y_coords['r2_y']}")
        print(f"  S2 Y坐标：{y_coords['s2_y']}")
        print(f"  现价 Y坐标：{y_coords['current_y']}")

        print(f"\n人工标注：")
        manual = result['manual_data']
        print(f"  R2价格：{manual.get('r2', '未标注')}")
        print(f"  S2价格：{manual.get('s2', '未标注')}")
        print(f"  现价：{manual.get('current_price', '未标注')}")

        mapping = result['mapping_model']
        if mapping['model_type'] == 'linear_regression':
            print(f"\n映射模型：")
            print(f"  模型类型：{mapping['model_type']}")
            print(f"  系数：{mapping['coefficient']:.6f}")
            print(f"  截距：{mapping['intercept']:.6f}")
            print(f"  R²：{mapping['r_squared']:.4f}")

            print(f"\n验证结果：")
            for type_name, val in mapping['validation'].items():
                print(f"  {type_name.upper()}：")
                print(f"    实际：{val['actual_price']}")
                print(f"    预测：{val['predicted_price']:.2f}")
                print(f"    误差：{val['error']:.2f} ({val['error_percentage']:.2f}%)")
        else:
            print(f"\n⚠️  {mapping['error']}")


def analyze_all_periods():
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

    # 创建映射器
    mapper = SimpleYPriceMapper()

    print("=" * 80)
    print("WKF系统Y坐标到价格的精确映射")
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
            result = mapper.build_mapping_model(image_path, manual_data)
            result['period'] = periods[i]
            all_results.append(result)

        except Exception as e:
            print(f"\n错误：{e}")
            import traceback
            traceback.print_exc()

    # 保存结果
    output_file = "/root/.openclaw/workspace/y_price_mapping_final.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)

    print("\n" + "=" * 80)
    print("映射模型建立完成")
    print("=" * 80)
    print(f"结果已保存到：{output_file}")

    # 打印汇总
    print("\n=== 汇总统计 ===")
    for result in all_results:
        period = result['period']
        mapping = result['mapping_model']

        if mapping['model_type'] == 'linear_regression':
            print(f"{period}：")
            print(f"  映射模型：价格 = {mapping['coefficient']:.6f} × Y + {mapping['intercept']:.6f}")
            print(f"  R²：{mapping['r_squared']:.4f}")
        else:
            print(f"{period}：{mapping['error']}")


if __name__ == "__main__":
    analyze_all_periods()
