#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WKF系统Y坐标到价格的精确映射模型
基于人工标注数据，建立每个周期的独立映射关系
"""

import cv2
import numpy as np
import json
import os
from typing import Dict, List
from sklearn.linear_model import LinearRegression
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


class YPriceMappingModel:
    """Y坐标到价格的映射模型"""

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

        # 周期名称
        self.periods = ['周线', '日线', '1小时', '15分钟', '5分钟']

    def build_mapping_model(self, image_path: str, manual_data: Dict) -> Dict:
        """构建单个周期的映射模型"""
        print(f"\n正在分析：{os.path.basename(image_path)}")

        # 读取图像
        image = cv2.imread(image_path)
        if image is None:
            return {
                'success': False,
                'error': '无法读取图像'
            }

        height, width = image.shape[:2]

        # 提取主图区域
        main_chart = image[self.regions['main_chart'][0]:self.regions['main_chart'][1], :]

        # 检测R2（白色阻力线）
        r2_y = self._detect_resistance_white(main_chart)

        # 检测S2（黄色支撑线）
        s2_y = self._detect_support_yellow(main_chart)

        # 检测现价线（黄色）
        current_price_y = self._detect_current_price_yellow(main_chart)

        # 建立校准点（Y坐标 -> 价格）
        calibration_points = []

        if r2_y is not None and manual_data.get('r2') is not None:
            calibration_points.append({
                'y': r2_y,
                'price': manual_data['r2'],
                'type': 'r2'
            })

        if s2_y is not None and manual_data.get('s2') is not None:
            calibration_points.append({
                'y': s2_y,
                'price': manual_data['s2'],
                'type': 's2'
            })

        if current_price_y is not None and manual_data.get('current_price') is not None:
            calibration_points.append({
                'y': current_price_y,
                'price': manual_data['current_price'],
                'type': 'current_price'
            })

        # 线性回归建立映射模型
        model = None
        r_squared = 0
        if len(calibration_points) >= 2:
            model, r_squared = self._build_linear_model(calibration_points)

        # 验证映射准确性
        validation_results = {}
        if model is not None:
            validation_results = self._validate_mapping(
                model, calibration_points)

        result = {
            'success': True,
            'image_path': image_path,
            'image_name': os.path.basename(image_path),
            'detected_y_coords': {
                'r2_y': r2_y,
                's2_y': s2_y,
                'current_price_y': current_price_y
            },
            'manual_data': manual_data,
            'calibration_points': calibration_points,
            'mapping_model': {
                'model': 'linear_regression' if model is not None else 'none',
                'r_squared': r_squared,
                'coefficients': None if model is None else {
                    'coefficient': float(model.coef_[0][0]) if model.coef_.ndim > 1 else float(model.coef_[0]),
                    'intercept': float(model.intercept_)
                }
            },
            'validation': validation_results
        }

        # 打印结果
        self._print_result(result)

        return result

    def _detect_resistance_white(self, image: np.ndarray) -> int:
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

        # 统计每行的像素数
        row_counts = np.sum(mask, axis=1)

        if np.max(row_counts) < image.shape[1] * 0.3:
            return None

        # 找到像素数最多的行
        top_rows = np.argsort(row_counts)[-5:]
        y_local = top_rows[0]

        return int(y_local + self.regions['main_chart'][0])

    def _detect_support_yellow(self, image: np.ndarray) -> int:
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

        # 统计每行的像素数
        row_counts = np.sum(mask, axis=1)

        if np.max(row_counts) < image.shape[1] * 0.1:
            return None

        # 找到像素数最多的行
        top_rows = np.argsort(row_counts)[-5:]

        # 选择最靠下的一行（较大的Y值）
        y_local = top_rows[-1]

        return int(y_local + self.regions['main_chart'][0])

    def _detect_current_price_yellow(self, image: np.ndarray) -> int:
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

        # 统计每行的像素数
        row_counts = np.sum(mask, axis=1)

        if np.max(row_counts) < image.shape[1] * 0.1:
            return None

        # 找到像素数最多的行
        y_local = np.argmax(row_counts)

        return int(y_local + self.regions['main_chart'][0])

    def _build_linear_model(self, calibration_points: List[Dict]):
        """构建线性回归模型"""
        X = np.array([[cp['y']] for cp in calibration_points])
        y = np.array([[cp['price']] for cp in calibration_points])

        model = LinearRegression()
        model.fit(X, y)
        r_squared = model.score(X, y)

        return model, r_squared

    def _validate_mapping(self, model, calibration_points: List[Dict]) -> Dict:
        """验证映射准确性"""
        results = {}

        for cp in calibration_points:
            y = cp['y']
            actual_price = cp['price']
            type_name = cp['type']

            # 预测价格
            predicted_price = model.predict([[y]])[0][0]
            error = abs(predicted_price - actual_price)

            results[type_name] = {
                'y': y,
                'actual_price': actual_price,
                'predicted_price': float(predicted_price),
                'error': float(error),
                'error_percentage': float(error / actual_price * 100) if actual_price != 0 else 0
            }

        return results

    def _print_result(self, result: Dict):
        """打印结果"""
        print(f"\n检测结果：")
        print(f"  R2 Y坐标：{result['detected_y_coords']['r2_y']}")
        print(f"  S2 Y坐标：{result['detected_y_coords']['s2_y']}")
        print(f"  现价 Y坐标：{result['detected_y_coords']['current_price_y']}")

        print(f"\n人工标注：")
        print(f"  R2价格：{result['manual_data'].get('r2', '未标注')}")
        print(f"  S2价格：{result['manual_data'].get('s2', '未标注')}")
        print(f"  现价：{result['manual_data'].get('current_price', '未标注')}")

        if result['mapping_model']['model'] != 'none':
            print(f"\n映射模型：")
            print(f"  模型类型：{result['mapping_model']['model']}")
            print(f"  R²：{result['mapping_model']['r_squared']:.4f}")
            print(f"  系数：{result['mapping_model']['coefficients']['coefficient']:.6f}")
            print(f"  截距：{result['mapping_model']['coefficients']['intercept']:.6f}")

            print(f"\n验证结果：")
            for type_name, val in result['validation'].items():
                print(f"  {type_name.upper()}：")
                print(f"    实际：{val['actual_price']}")
                print(f"    预测：{val['predicted_price']:.2f}")
                print(f"    误差：{val['error']:.2f} ({val['error_percentage']:.2f}%)")
        else:
            print(f"\n⚠️  校准点不足（需要≥2个），无法建立映射模型")


def analyze_all_periods():
    """分析所有5个周期"""

    # 5张图片
    stock_images = [
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
    mapper = YPriceMappingModel()

    print("=" * 80)
    print("WKF系统Y坐标到价格的精确映射")
    print("=" * 80)

    all_results = []

    for i, (image_name, manual_data) in enumerate(stock_images):
        image_path = f"/root/.openclaw/media/inbound/{image_name}"

        if not os.path.exists(image_path):
            print(f"\n{i+1}/{len(stock_images)} 图片不存在：{image_name}")
            continue

        print(f"\n{'='*80}")
        print(f"[{i+1}/{len(stock_images)}] {periods[i]}分析")
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
    output_file = "/root/.openclaw/workspace/y_price_mapping_final_results.json"
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
        r2_y = result['detected_y_coords']['r2_y']
        s2_y = result['detected_y_coords']['s2_y']
        cp_y = result['detected_y_coords']['current_price_y']
        r_squared = result['mapping_model']['r_squared']

        print(f"{period}：")
        print(f"  R2 Y={r2_y}, S2 Y={s2_y}, 现价 Y={cp_y}")
        print(f"  映射模型 R² = {r_squared:.4f}")


if __name__ == "__main__":
    analyze_all_periods()
