#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文华财经截图精准解析器V5 - 终极版
采用多策略组合提升识别准确率
"""

import cv2
import numpy as np
import pytesseract
from typing import Dict, List, Optional
import re
import json


class WenHuaParserV5:
    """文华财经截图解析器V5 - 终极版"""

    def __init__(self):
        """初始化"""
        # Tesseract配置
        self.tess_config_digit = '--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789.'
        self.tess_config_text = '--oem 3 --psm 7'

    def create_color_masks(self, image: np.ndarray) -> Dict[str, np.ndarray]:
        """创建多个颜色掩码（更宽松的阈值）"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        masks = {}

        # 红色（阻力线）：非常宽松的范围
        lower1 = np.array([0, 50, 50])
        upper1 = np.array([20, 255, 255])
        lower2 = np.array([160, 50, 50])
        upper2 = np.array([180, 255, 255])
        mask1 = cv2.inRange(hsv, lower1, upper1)
        mask2 = cv2.inRange(hsv, lower2, upper2)
        masks['red'] = cv2.bitwise_or(mask1, mask2)

        # 绿色（支撑线）：非常宽松的范围
        lower = np.array([30, 30, 30])
        upper = np.array([100, 255, 255])
        masks['green'] = cv2.inRange(hsv, lower, upper)

        # 黄色（现价）：非常宽松的范围
        lower = np.array([15, 100, 100])
        upper = np.array([40, 255, 255])
        masks['yellow'] = cv2.inRange(hsv, lower, upper)

        # 白色（零轴）
        lower = np.array([0, 0, 200])
        upper = np.array([180, 50, 255])
        masks['white'] = cv2.inRange(hsv, lower, upper)

        return masks

    def find_all_text_regions(self, image: np.ndarray) -> List[Dict]:
        """查找所有文本区域"""
        # 转换为灰度
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 二值化
        binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        # 查找轮廓
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        text_regions = []

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # 过滤小区域
            if w < 20 or h < 10:
                continue

            # 提取ROI
            roi = image[y:y+h, x:x+w]

            # OCR识别
            text = pytesseract.image_to_string(roi, config=self.tess_config_digit).strip()

            # 提取数字
            numbers = re.findall(r'\d+\.?\d*', text)

            if numbers:
                try:
                    value = float(numbers[0])
                    text_regions.append({
                        'x': int(x),
                        'y': int(y),
                        'width': int(w),
                        'height': int(h),
                        'text': text,
                        'value': value
                    })
                except ValueError:
                    pass

        # 按x坐标排序
        text_regions.sort(key=lambda r: r['x'])

        return text_regions

    def classify_text_regions(self, image: np.ndarray, text_regions: List[Dict]) -> Dict[str, List[Dict]]:
        """分类文本区域（根据颜色）"""
        classified = {
            'red': [],      # 阻力线
            'green': [],    # 支撑线
            'yellow': [],   # 现价
            'white': []     # 零轴
        }

        # 创建颜色掩码
        masks = self.create_color_masks(image)

        for region in text_regions:
            x, y, w, h = region['x'], region['y'], region['width'], region['height']

            # 计算区域中心的像素
            center_x = x + w // 2
            center_y = y + h // 2

            height, width = image.shape[:2]

            if 0 <= center_x < width and 0 <= center_y < height:
                # 检查每个颜色掩码
                for color_name, mask in masks.items():
                    if 0 <= center_y < mask.shape[0] and 0 <= center_x < mask.shape[1]:
                        if mask[center_y, center_x] > 0:
                            classified[color_name].append(region)
                            break

        return classified

    def find_horizontal_lines_by_region(self, classified_regions: Dict[str, List[Dict]],
                                    min_width: int = 100) -> Dict[str, List[Dict]]:
        """根据文本区域查找水平线"""
        horizontal_lines = {
            'red': [],      # 阻力线
            'green': []     # 支撑线
        }

        for color_name, regions in classified_regions.items():
            if color_name not in ['red', 'green']:
                continue

            # 按y坐标分组
            y_groups = {}
            for region in regions:
                y = region['y']
                if y not in y_groups:
                    y_groups[y] = []
                y_groups[y].append(region)

            # 为每个y坐标创建一条水平线
            for y, group in y_groups.items():
                # 检查宽度是否足够
                x_values = [r['x'] for r in group]
                if max(x_values) - min(x_values) >= min_width:
                    horizontal_lines[color_name].append({
                        'y': y,
                        'regions': group,
                        'x': min(x_values),
                        'width': max(x_values) - min(x_values),
                        'values': [r['value'] for r in group]
                    })

            # 按y坐标排序
            horizontal_lines[color_name].sort(key=lambda l: l['y'])

        return horizontal_lines

    def parse_screenshot_v5(self, image_path: str) -> Dict:
        """使用V5方法解析截图"""
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

        # 1. 查找所有文本区域
        text_regions = self.find_all_text_regions(main_chart)

        # 2. 根据颜色分类文本区域
        classified_regions = self.classify_text_regions(main_chart, text_regions)

        # 3. 根据文本区域查找水平线
        horizontal_lines = self.find_horizontal_lines_by_region(classified_regions)

        # 4. 提取现价（黄色区域中的数字）
        yellow_regions = classified_regions.get('yellow', [])
        if yellow_regions:
            # 选择最大的黄色区域（最可能是现价）
            largest_yellow = max(yellow_regions, key=lambda r: r['width'] * r['height'])
            result['main_chart']['current_price'] = {
                'price': largest_yellow['value'],
                'x': largest_yellow['x'],
                'y': largest_yellow['y'],
                'width': largest_yellow['width'],
                'height': largest_yellow['height']
            }

        # 5. 提取支撑线
        support_lines = horizontal_lines.get('green', [])
        result['main_chart']['support_lines'] = []

        for line in support_lines:
            # 选择该行中最显著的数字（假设只有一个主要数字）
            values = [v for v in line['values'] if 5.0 <= v <= 30.0]  # 合理的价格范围
            if values:
                result['main_chart']['support_lines'].append({
                    'y': line['y'],
                    'x': line['x'],
                    'width': line['width'],
                    'price': values[0],  # 取第一个值
                    'all_values': values
                })

        # 6. 提取阻力线
        resistance_lines = horizontal_lines.get('red', [])
        result['main_chart']['resistance_lines'] = []

        for line in resistance_lines:
            # 选择该行中最显著的数字
            values = [v for v in line['values'] if 5.0 <= v <= 30.0]  # 合理的价格范围
            if values:
                result['main_chart']['resistance_lines'].append({
                    'y': line['y'],
                    'x': line['x'],
                    'width': line['width'],
                    'price': values[0],  # 取第一个值
                    'all_values': values
                })

        # 7. 生成摘要
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
    parser = WenHuaParserV5()

    # 测试图片
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
            result = parser.parse_screenshot_v5(test_image)

            # 打印结果
            print("\n=== V5解析结果 ===")

            # 打印支撑线
            support_lines = result['main_chart'].get('support_lines', [])
            print(f"\n支撑线（绿色）：{len(support_lines)}条")
            for i, line in enumerate(support_lines, 1):
                print(f"  线{i}: y={line['y']}, price={line.get('price', 'N/A')}, 所有值={line.get('all_values', [])}")

            # 打印阻力线
            resistance_lines = result['main_chart'].get('resistance_lines', [])
            print(f"\n阻力线（红色）：{len(resistance_lines)}条")
            for i, line in enumerate(resistance_lines, 1):
                print(f"  线{i}: y={line['y']}, price={line.get('price', 'N/A')}, 所有值={line.get('all_values', [])}")

            # 打印现价
            current_price = result['main_chart'].get('current_price')
            if current_price:
                print(f"\n现价（黄色）：{current_price['price']}")
            else:
                print(f"\n现价：未识别到")

            # 对比分析
            print(f"\n=== 对比分析 ===")

            # 对比S2
            if support_prices := [s['price'] for s in support_lines if s.get('price')]:
                if manual_annotation['S2'] in support_prices:
                    print(f"✓ 支撑线识别准确（S2={manual_annotation['S2']}）")
                elif support_prices:
                    print(f"△ 支撑线识别到{len(support_prices)}条价格：{support_prices}")
                    print(f"  人工标注：S2={manual_annotation['S2']}")
                else:
                    print(f"✗ 支撑线未识别到价格")
            else:
                print(f"✗ 支撑线未识别到（人工标注：S2={manual_annotation['S2']}）")

            # 对比R2
            if resistance_prices := [r['price'] for r in resistance_lines if r.get('price')]:
                if manual_annotation['R2'] in resistance_prices:
                    print(f"✓ 阻力线识别准确（R2={manual_annotation['R2']}）")
                elif resistance_prices:
                    print(f"△ 阻力线识别到{len(resistance_prices)}条价格：{resistance_prices}")
                    print(f"  人工标注：R2={manual_annotation['R2']}")
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
            output_file = "/root/.openclaw/workspace/v5_parse_result.json"
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
