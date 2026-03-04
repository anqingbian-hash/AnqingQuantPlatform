#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文华财经截图精准解析器V3
基于人工标注数据优化算法
"""

import cv2
import numpy as np
import pytesseract
from typing import Dict, List, Optional, Tuple
import re
import json


class WenHuaParserV3:
    """文华财经截图解析器V3 - 精准版"""

    def __init__(self):
        """初始化"""
        # Tesseract配置 - 针对数字和文本优化
        self.tess_config_digit = '--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789.-'
        self.tess_config_text = '--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZlpsybcSCTEST'

        # 颜色阈值（更精确）
        self.color_thresholds = {
            'red': {'lower': (0, 100, 100), 'upper': (10, 255, 255)},
            'green': {'lower': (40, 50, 50), 'upper': (80, 255, 255)},
            'yellow': {'lower': (20, 100, 100), 'upper': (30, 255, 255)},
            'white': {'lower': (0, 0, 200), 'upper': (180, 30, 255)},
            'black': {'lower': (0, 0, 0), 'upper': (180, 255, 50)}
        }

    def create_color_mask(self, image: np.ndarray, color_name: str) -> np.ndarray:
        """创建颜色掩码"""
        if color_name not in self.color_thresholds:
            return np.zeros(image.shape[:2], dtype=np.uint8)

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        threshold = self.color_thresholds[color_name]

        if color_name == 'red':
            # 红色需要两个范围
            lower1 = np.array([0, 100, 100])
            upper1 = np.array([10, 255, 255])
            lower2 = np.array([170, 100, 100])
            upper2 = np.array([180, 255, 255])

            mask1 = cv2.inRange(hsv, lower1, upper1)
            mask2 = cv2.inRange(hsv, lower2, upper2)
            mask = cv2.bitwise_or(mask1, mask2)
        else:
            lower = np.array(threshold['lower'])
            upper = np.array(threshold['upper'])
            mask = cv2.inRange(hsv, lower, upper)

        return mask

    def extract_number_from_roi(self, image: np.ndarray, x: int, y: int,
                              w: int, h: int) -> Optional[float]:
        """从ROI区域提取数字"""
        height, width = image.shape[:2]

        # 确保ROI在图像范围内
        x = max(0, min(x, width - w))
        y = max(0, min(y, height - h))

        roi = image[y:y+h, x:x+w]

        # 预处理
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # 增强对比度
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # 二值化
        binary = cv2.threshold(enhanced, 0, 255,
                             cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        # OCR识别
        text = pytesseract.image_to_string(binary, config=self.tess_config_digit).strip()

        # 提取数字
        numbers = re.findall(r'\d+\.?\d*', text)

        if numbers:
            try:
                return float(numbers[0])
            except ValueError:
                pass

        return None

    def find_horizontal_lines_by_color(self, image: np.ndarray, color_name: str,
                                      min_length: int = 500) -> List[Dict]:
        """通过颜色查找水平线"""
        height, width = image.shape[:2]

        # 创建颜色掩码
        mask = self.create_color_mask(image, color_name)

        # 查找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)

        horizontal_lines = []

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # 检查是否是水平线（长而细）
            if w >= min_length and h < 15:
                horizontal_lines.append({
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h,
                    'line': (x, y, x+w, y+h)
                })

        # 按y坐标排序
        horizontal_lines.sort(key=lambda l: l['y'])

        return horizontal_lines

    def extract_price_label_near_line(self, image: np.ndarray, line: Dict,
                                     direction: str = 'right',
                                     offset: int = 10) -> Optional[float]:
        """提取线条附近的价格标签"""
        x, y, w, h = line['x'], line['y'], line['width'], line['height']

        # 定义ROI区域
        if direction == 'right':
            # 线条右侧
            roi_x = x + w + offset
            roi_y = max(0, y - 15)
            roi_w = 120
            roi_h = 30
        else:
            # 线条左侧
            roi_x = max(0, x - 120 - offset)
            roi_y = max(0, y - 15)
            roi_w = 120
            roi_h = 30

        # 提取数字
        return self.extract_number_from_roi(image, roi_x, roi_y, roi_w, roi_h)

    def find_current_price_by_color(self, image: np.ndarray) -> Optional[Dict]:
        """通过颜色查找现价"""
        height, width = image.shape[:2]

        # 查找黄色区域（现价通常是黄色高亮）
        yellow_mask = self.create_color_mask(image, 'yellow')

        # 查找轮廓
        contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # 过滤小区域
            if w < 40 or h < 20:
                continue

            # 在黄色区域内查找数字
            price = self.extract_number_from_roi(image, x, y, w, h)

            if price is not None:
                return {
                    'price': price,
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h
                }

        return None

    def parse_screenshot_with_manual_data(self, image_path: str,
                                       manual_annotation: Dict) -> Dict:
        """
        使用人工标注数据指导解析
        """
        # 读取图像
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"无法读取图像：{image_path}")

        height, width = image.shape[:2]

        result = {
            'image_path': image_path,
            'image_size': {
                'width': width,
                'height': height
            },
            'manual_annotation': manual_annotation,
            'ocr_result': {},
            'ocr_comparison': {}
        }

        # 1. 解析主图（上半部分）
        main_chart_end = int(height * 0.45)
        main_chart = image[:main_chart_end, :]

        # 查找支撑线（绿色）
        green_lines = self.find_horizontal_lines_by_color(main_chart, 'green',
                                                       min_length=500)

        # 查找阻力线（红色）
        red_lines = self.find_horizontal_lines_by_color(main_chart, 'red',
                                                      min_length=500)

        # 查找现价（黄色）
        current_price = self.find_current_price_by_color(main_chart)

        result['ocr_result'] = {
            'support_lines': green_lines,
            'resistance_lines': red_lines,
            'current_price': current_price
        }

        # 2. 对比分析
        result['ocr_comparison'] = self._compare_with_manual(
            result['ocr_result'],
            manual_annotation
        )

        return result

    def _compare_with_manual(self, ocr_result: Dict,
                            manual_annotation: Dict) -> Dict:
        """与人工标注对比"""
        comparison = {}

        # 对比支撑线
        if ocr_result['support_lines']:
            comparison['support_lines_found'] = True
            comparison['support_line_count'] = len(ocr_result['support_lines'])
        else:
            comparison['support_lines_found'] = False

        # 对比阻力线
        if ocr_result['resistance_lines']:
            comparison['resistance_lines_found'] = True
            comparison['resistance_line_count'] = len(ocr_result['resistance_lines'])
        else:
            comparison['resistance_lines_found'] = False

        # 对比现价
        if ocr_result['current_price']:
            ocr_price = ocr_result['current_price']['price']
            manual_price = manual_annotation.get('current_price')

            if manual_price:
                diff = abs(ocr_price - manual_price)
                comparison['current_price_found'] = True
                comparison['current_price_ocr'] = ocr_price
                comparison['current_price_manual'] = manual_price
                comparison['current_price_diff'] = diff

                if diff < 0.1:
                    comparison['current_price_accuracy'] = 'perfect'
                elif diff < 1.0:
                    comparison['current_price_accuracy'] = 'good'
                else:
                    comparison['current_price_accuracy'] = 'poor'
        else:
            comparison['current_price_found'] = False

        return comparison


def main():
    """测试函数"""
    import os

    # 检查Tesseract
    try:
        pytesseract.get_tesseract_version()
        print(f"✓ Tesseract版本: {pytesseract.get_tesseract_version()}")
    except Exception as e:
        print(f"✗ 错误：Tesseract未安装")
        return

    # 创建解析器
    parser = WenHuaParserV3()

    # 测试图片和人工标注
    test_image = "/root/.openclaw/media/inbound/92ea67d8-5897-401a-825a-63df2f39ee75.jpg"

    # 人工标注数据
    manual_annotation = {
        'S2': 8.48,
        'current_price': 15.69,
        'R2': 17.58,
        'high_price': 20.10
    }

    if os.path.exists(test_image):
        print(f"\n正在解析截图：{test_image}")
        print(f"\n人工标注数据：")
        print(f"  S2（支撑位）：{manual_annotation['S2']}")
        print(f"  现价：{manual_annotation['current_price']}")
        print(f"  R2（阻力位）：{manual_annotation['R2']}")
        print(f"  图中高点：{manual_annotation['high_price']}")

        try:
            # 解析
            result = parser.parse_screenshot_with_manual_data(test_image,
                                                           manual_annotation)

            # 转换numpy类型
            class NumpyEncoder(json.JSONEncoder):
                def default(self, obj):
                    if isinstance(obj, (np.integer, np.int32, np.int64)):
                        return int(obj)
                    elif isinstance(obj, (np.floating, np.float32, np.float64)):
                        return float(obj)
                    elif isinstance(obj, np.ndarray):
                        return obj.tolist()
                    return super().default(obj)

            # 打印结果
            print("\n=== OCR识别结果 ===")

            # 打印对比
            comparison = result.get('ocr_comparison', {})
            if comparison.get('support_lines_found'):
                print(f"\n✓ 找到支撑线：{comparison['support_line_count']}条")
            else:
                print(f"\n✗ 未找到支撑线（人工标注：S2={manual_annotation['S2']}）")

            if comparison.get('resistance_lines_found'):
                print(f"✓ 找到阻力线：{comparison['resistance_line_count']}条")
            else:
                print(f"✗ 未找到阻力线（人工标注：R2={manual_annotation['R2']}）")

            if comparison.get('current_price_found'):
                ocr_price = comparison['current_price_ocr']
                manual_price = comparison['current_price_manual']
                diff = comparison['current_price_diff']
                accuracy = comparison['current_price_accuracy']

                print(f"\n现价识别：{accuracy}")
                print(f"  OCR：{ocr_price}")
                print(f"  人工：{manual_price}")
                print(f"  误差：{diff:.2f}")
            else:
                print(f"\n✗ 未找到现价（人工标注：现价={manual_annotation['current_price']}）")

            # 保存结果
            output_file = "/root/.openclaw/workspace/v3_parse_result.json"
            result_converted = json.loads(json.dumps(result, cls=NumpyEncoder))
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result_converted, f, indent=2, ensure_ascii=False)
            print(f"\n✓ 结果已保存到：{output_file}")

        except Exception as e:
            print(f"\n✗ 错误：{e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"✗ 错误：图像不存在：{test_image}")


if __name__ == "__main__":
    main()
