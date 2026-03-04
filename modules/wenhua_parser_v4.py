#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文华财经截图精准解析器V4
基于实际测量的像素值优化
"""

import cv2
import numpy as np
import pytesseract
from typing import Dict, List, Optional, Tuple
import re
import json


class WenHuaParserV4:
    """文华财经截图解析器V4 - 基于实际像素值"""

    def __init__(self):
        """初始化"""
        # Tesseract配置
        self.tess_config_digit = '--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789.'

        # 基于实际测量的BGR颜色阈值（更精确）
        self.bgr_thresholds = {
            # 红色（阻力线）：淡紫色/粉红色 B=[90-100, 90-100, 160-170]
            'red': {
                'lower': np.array([70, 70, 140], dtype=np.uint8),
                'upper': np.array([120, 120, 190], dtype=np.uint8)
            },

            # 绿色（支撑线）：标准绿色 B=[40-50, 170-220, 40-50]
            'green': {
                'lower': np.array([30, 150, 30], dtype=np.uint8),
                'upper': np.array([60, 230, 60], dtype=np.uint8)
            },

            # 黄色（现价）：淡青色/黄色 B=[50-80, 210-215, 210-215]
            'yellow': {
                'lower': np.array([40, 200, 200], dtype=np.uint8),
                'upper': np.array([90, 220, 220], dtype=np.uint8)
            },

            # 白色（零轴）：白色 B=[220-255, 220-255, 220-255]
            'white': {
                'lower': np.array([200, 200, 200], dtype=np.uint8),
                'upper': np.array([255, 255, 255], dtype=np.uint8)
            }
        }

    def create_bgr_mask(self, image: np.ndarray, color_name: str) -> np.ndarray:
        """创建BGR颜色掩码"""
        if color_name not in self.bgr_thresholds:
            return np.zeros(image.shape[:2], dtype=np.uint8)

        threshold = self.bgr_thresholds[color_name]
        lower = threshold['lower']
        upper = threshold['upper']

        # 创建颜色掩码
        mask = cv2.inRange(image, lower, upper)

        # 形态学操作，去除噪点
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        return mask

    def find_horizontal_lines_by_bgr(self, image: np.ndarray, color_name: str,
                                      min_length: int = 500) -> List[Dict]:
        """通过BGR颜色查找水平线"""
        height, width = image.shape[:2]

        # 创建颜色掩码
        mask = self.create_bgr_mask(image, color_name)

        # 查找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)

        horizontal_lines = []

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # 检查是否是水平线（长而细）
            if w >= min_length and h < 15:
                horizontal_lines.append({
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h)
                })

        # 按y坐标排序
        horizontal_lines.sort(key=lambda l: l['y'])

        # 过滤重叠线
        filtered_lines = self._filter_overlapping_lines(horizontal_lines)

        return filtered_lines

    def _filter_overlapping_lines(self, lines: List[Dict]) -> List[Dict]:
        """过滤重叠的线"""
        if not lines:
            return []

        filtered = []
        current_line = lines[0]

        for line in lines[1:]:
            # 检查y坐标是否接近（±8像素）
            if abs(line['y'] - current_line['y']) <= 8:
                # 选择更长的线
                if line['width'] > current_line['width']:
                    current_line = line
            else:
                filtered.append(current_line)
                current_line = line

        # 添加最后一条
        filtered.append(current_line)

        return filtered

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

    def extract_price_label_near_line(self, image: np.ndarray, line: Dict,
                                     direction: str = 'right',
                                     offset: int = 5,
                                     roi_w: int = 150,
                                     roi_h: int = 30) -> Optional[Dict]:
        """提取线条附近的价格标签"""
        x, y, w, h = line['x'], line['y'], line['width'], line['height']

        # 定义ROI区域
        if direction == 'right':
            roi_x = x + w + offset
            roi_y = max(0, y - 5)
        else:
            roi_x = max(0, x - roi_w - offset)
            roi_y = max(0, y - 5)

        # 提取数字
        price = self.extract_number_from_roi(image, roi_x, roi_y, roi_w, roi_h)

        if price is not None:
            return {
                'price': price,
                'roi_x': roi_x,
                'roi_y': roi_y,
                'roi_w': roi_w,
                'roi_h': roi_h
            }

        return None

    def find_current_price_by_bgr(self, image: np.ndarray) -> Optional[Dict]:
        """通过BGR颜色查找现价"""
        # 创建黄色掩码
        yellow_mask = self.create_bgr_mask(image, 'yellow')

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
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h)
                }

        return None

    def parse_screenshot_v4(self, image_path: str) -> Dict:
        """
        使用V4方法解析截图
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
            'main_chart': {},
            'summary': {}
        }

        # 解析主图（上半部分）
        main_chart_end = int(height * 0.45)
        main_chart = image[:main_chart_end, :]

        # 查找支撑线（绿色）
        green_lines = self.find_horizontal_lines_by_bgr(main_chart, 'green',
                                                       min_length=500)

        # 查找阻力线（红色）
        red_lines = self.find_horizontal_lines_by_bgr(main_chart, 'red',
                                                      min_length=500)

        # 查找现价（黄色）
        current_price = self.find_current_price_by_bgr(main_chart)

        # 提取价格标签
        green_lines_with_price = []
        for line in green_lines:
            price_info = self.extract_price_label_near_line(main_chart, line,
                                                         direction='right')
            if price_info:
                line['price'] = price_info['price']
                green_lines_with_price.append(line)

        red_lines_with_price = []
        for line in red_lines:
            price_info = self.extract_price_label_near_line(main_chart, line,
                                                         direction='right')
            if price_info:
                line['price'] = price_info['price']
                red_lines_with_price.append(line)

        result['main_chart'] = {
            'support_lines': green_lines_with_price,
            'resistance_lines': red_lines_with_price,
            'current_price': current_price
        }

        # 生成摘要
        result['summary'] = self._generate_summary(result)

        return result

    def _generate_summary(self, parse_result: Dict) -> Dict:
        """生成摘要"""
        summary = {}

        # 当前价格
        if 'current_price' in parse_result['main_chart']:
            price = parse_result['main_chart']['current_price']
            if price:
                summary['current_price'] = price['price']

        # 支撑位
        support_prices = [s['price'] for s in parse_result['main_chart'].get('support_lines', []) if s.get('price')]
        if support_prices:
            summary['support_prices'] = support_prices

        # 阻力位
        resistance_prices = [r['price'] for r in parse_result['main_chart'].get('resistance_lines', []) if r.get('price')]
        if resistance_prices:
            summary['resistance_prices'] = resistance_prices

        return summary


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
    parser = WenHuaParserV4()

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
            result = parser.parse_screenshot_v4(test_image)

            # 打印结果
            print("\n=== V4解析结果 ===")

            # 打印支撑线
            support_lines = result['main_chart'].get('support_lines', [])
            print(f"\n支撑线（绿色）：{len(support_lines)}条")
            for i, line in enumerate(support_lines, 1):
                print(f"  线{i}: y={line['y']}, price={line.get('price', 'N/A')}")

            # 打印阻力线
            resistance_lines = result['main_chart'].get('resistance_lines', [])
            print(f"\n阻力线（红色）：{len(resistance_lines)}条")
            for i, line in enumerate(resistance_lines, 1):
                print(f"  线{i}: y={line['y']}, price={line.get('price', 'N/A')}")

            # 打印现价
            current_price = result['main_chart'].get('current_price')
            if current_price:
                print(f"\n现价：{current_price['price']}")
            else:
                print(f"\n现价：未识别到")

            # 对比分析
            print(f"\n=== 对比分析 ===")

            # 对比支撑线
            if support_lines:
                support_prices = [s['price'] for s in support_lines if s.get('price')]
                if manual_annotation['S2'] in support_prices:
                    print(f"✓ 支撑线识别准确（S2={manual_annotation['S2']}）")
                elif support_prices:
                    print(f"△ 支撑线识别到{len(support_prices)}条价格：{support_prices}")
                    print(f"  人工标注：S2={manual_annotation['S2']}")
                else:
                    print(f"✗ 支撑线未识别到价格")
            else:
                print(f"✗ 支撑线未识别到（人工标注：S2={manual_annotation['S2']}）")

            # 对比阻力线
            if resistance_lines:
                resistance_prices = [r['price'] for r in resistance_lines if r.get('price')]
                if manual_annotation['R2'] in resistance_prices:
                    print(f"✓ 阻力线识别准确（R2={manual_annotation['R2']}）")
                elif resistance_prices:
                    print(f"△ 阻力线识别到{len(resistance_prices)}条价格：{resistance_prices}")
                    print(f"  人工标注：R2={manual_annotation['R2']}）")
                else:
                    print(f"✗ 阻力线未识别到价格")
            else:
                print(f"✗ 阻力线未识别到（人工标注：R2={manual_annotation['R2']}）")

            # 对比现价
            if current_price and current_price.get('price'):
                ocr_price = current_price['price']
                manual_price = manual_annotation['current_price']

                diff = abs(ocr_price - manual_price)

                if diff < 0.1:
                    print(f"✓ 现价识别准确（OCR：{ocr_price}, 人工：{manual_price}）")
                elif diff < 1.0:
                    print(f"△ 现价识别基本准确（误差{diff:.2f}）")
                    print(f"  OCR：{ocr_price}, 人工：{manual_price}")
                else:
                    print(f"✗ 现价识别不准确（误差{diff:.2f}）")
                    print(f"  OCR：{ocr_price}, 人工：{manual_price}")
            else:
                print(f"✗ 现价未识别到（人工标注：现价={manual_annotation['current_price']}）")

            # 保存结果
            output_file = "/root/.openclaw/workspace/v4_parse_result.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n✓ 结果已保存到：{output_file}")

        except Exception as e:
            print(f"\n✗ 错误：{e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"✗ 错误：图像不存在：{test_image}")


if __name__ == "__main__":
    main()
