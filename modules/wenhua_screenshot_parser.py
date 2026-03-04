#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文华财经截图专业解析器
针对文华财经6 ATS指标截图的专用识别模块
"""

import cv2
import numpy as np
import pytesseract
from typing import Dict, List, Optional, Tuple
import re
import json


class WenHuaScreenshotParser:
    """文华财经截图解析器"""

    def __init__(self):
        """初始化解析器"""
        # Tesseract配置 - 针对数字优化
        self.tess_config = '--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789.-'

        # 颜色定义（BGR格式）
        self.colors = {
            'red': (0, 0, 255),
            'green': (0, 255, 0),
            'yellow': (0, 255, 255),
            'blue': (255, 0, 0),
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'cyan': (255, 255, 0),
            'magenta': (255, 0, 255)
        }

        # 颜色范围（HSV格式）
        self.hsv_ranges = {
            'red': [(0, 120, 70), (10, 255, 255), (170, 120, 70), (180, 255, 255)],
            'green': [(40, 50, 50), (80, 255, 255)],
            'yellow': [(20, 100, 100), (30, 255, 255)],
            'blue': [(100, 100, 100), (130, 255, 255)],
            'cyan': [(80, 100, 100), (100, 255, 255)]
        }

    def enhance_image(self, image: np.ndarray) -> np.ndarray:
        """
        增强图像质量
        """
        # 1. 降噪
        denoised = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)

        # 2. 锐化
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1],
                          [-1,-1,-1]])
        sharpened = cv2.filter2D(denoised, -1, kernel)

        # 3. 提升对比度
        lab = cv2.cvtColor(sharpened, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

        return enhanced

    def find_horizontal_lines(self, image: np.ndarray, color_name: str,
                            min_width: int = 100, max_height: int = 8) -> List[Tuple[int, int, int, int]]:
        """
        查找水平线
        :param image: 图像
        :param color_name: 颜色名称
        :param min_width: 最小宽度
        :param max_height: 最大高度
        :return: 线条坐标列表 [(x, y, width, height), ...]
        """
        lines = []

        # 转换为HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # 创建颜色掩码
        if color_name in self.hsv_ranges:
            ranges = self.hsv_ranges[color_name]
            if len(ranges) == 4:  # 红色
                lower1, upper1, lower2, upper2 = ranges
                mask1 = cv2.inRange(hsv, np.array(lower1), np.array(upper1))
                mask2 = cv2.inRange(hsv, np.array(lower2), np.array(upper2))
                mask = cv2.bitwise_or(mask1, mask2)
            else:
                lower, upper = ranges
                mask = cv2.inRange(hsv, np.array(lower), np.array(upper))

            # 查找轮廓
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)

                # 检查是否是水平线
                if w >= min_width and h <= max_height:
                    lines.append((x, y, w, h))

            # 按y坐标排序
            lines.sort(key=lambda x: x[1])

        return lines

    def extract_text_near_line(self, image: np.ndarray, line: Tuple[int, int, int, int],
                            direction: str = 'right', offset: int = 5) -> str:
        """
        提取线条附近的文本
        :param image: 图像
        :param line: 线条坐标 (x, y, width, height)
        :param direction: 方向（left/right）
        :param offset: 偏移量
        :return: 提取的文本
        """
        x, y, w, h = line

        if direction == 'right':
            # 线条右侧
            text_x = x + w + offset
            text_y = y - 10
            text_w = 150
            text_h = 30
        else:
            # 线条左侧
            text_x = x - 150 - offset
            text_y = y - 10
            text_w = 150
            text_h = 30

        # 确保在图像范围内
        height, width = image.shape[:2]
        text_x = max(0, min(text_x, width - text_w))
        text_y = max(0, min(text_y, height - text_h))

        # 提取ROI
        roi = image[text_y:text_y+text_h, text_x:text_x+text_w]

        # 转灰度
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # OCR识别
        text = pytesseract.image_to_string(gray, config=self.tess_config).strip()

        return text

    def extract_number_from_text(self, text: str) -> Optional[float]:
        """
        从文本中提取数字
        """
        # 匹配数字（包括小数）
        pattern = r'\d+\.?\d*'
        matches = re.findall(pattern, text)

        if matches:
            return float(matches[0])

        return None

    def parse_main_chart(self, image: np.ndarray) -> Dict:
        """
        解析主图
        :param image: 主图图像
        :return: 主图数据
        """
        result = {
            'current_price': None,
            'support_lines': [],
            'resistance_lines': [],
            'annotations': []
        }

        # 1. 查找支撑线（绿色水平线）
        green_lines = self.find_horizontal_lines(image, 'green')
        for line in green_lines:
            x, y, w, h = line
            # 提取价格标签
            price_text = self.extract_text_near_line(image, line, direction='right')
            price = self.extract_number_from_text(price_text)

            result['support_lines'].append({
                'x': x,
                'y': y,
                'width': w,
                'height': h,
                'price': price,
                'label_text': price_text
            })

        # 2. 查找阻力线（红色水平线）
        red_lines = self.find_horizontal_lines(image, 'red')
        for line in red_lines:
            x, y, w, h = line
            # 提取价格标签
            price_text = self.extract_text_near_line(image, line, direction='right')
            price = self.extract_number_from_text(price_text)

            result['resistance_lines'].append({
                'x': x,
                'y': y,
                'width': w,
                'height': h,
                'price': price,
                'label_text': price_text
            })

        # 3. 查找现价（黄色区域）
        height, width = image.shape[:2]

        # 查找黄色区域
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower, upper = self.hsv_ranges['yellow']
        yellow_mask = cv2.inRange(hsv, np.array(lower), np.array(upper))

        # 查找轮廓
        contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # 过滤：应该是一个较大的矩形区域
            if w > 50 and h > 20:
                # 提取文本
                roi = image[y:y+h, x:x+w]
                gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                text = pytesseract.image_to_string(gray, config=self.tess_config).strip()

                # 提取数字
                price = self.extract_number_from_text(text)
                if price:
                    result['current_price'] = {
                        'price': price,
                        'x': x,
                        'y': y,
                        'width': w,
                        'height': h,
                        'text': text
                    }
                    break

        # 4. 查找标注（LPS/LPSY/BC/SC）
        # 查找所有文本区域
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        # 查找轮廓
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # 过滤小区域
            if w < 30 or h < 15:
                continue

            # 提取文本
            roi = image[y:y+h, x:x+w]
            text = pytesseract.image_to_string(roi, config=self.tess_config).strip().upper()

            # 检查是否是标注
            if text in ['LPS', 'LPSY', 'BC', 'SC', 'TEST', 'SOS', 'SOW']:
                result['annotations'].append({
                    'type': text,
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h
                })

        return result

    def parse_net_volume_chart(self, image: np.ndarray) -> Dict:
        """
        解析净量副图
        :param image: 净量副图图像
        :return: 净量数据
        """
        result = {
            'current_value': None,
            'is_positive': None,
            'zero_line_y': None
        }

        # 1. 查找零轴（中间的水平线）
        height, width = image.shape[:2]

        # 查找白色或灰色水平线（零轴）
        lines = self.find_horizontal_lines(image, 'cyan', min_width=50, max_height=5)
        if lines:
            # 取中间的线作为零轴
            zero_lines = [l for l in lines if abs(l[1] - height/2) < height/4]
            if zero_lines:
                result['zero_line_y'] = zero_lines[0][1]

        # 2. 提取数值
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        # 查找所有文本区域
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # 过滤
            if w < 20 or h < 15:
                continue

            # 提取文本
            roi = image[y:y+h, x:x+w]
            text = pytesseract.image_to_string(roi, config=self.tess_config).strip()

            # 提取数字
            value = self.extract_number_from_text(text)
            if value is not None:
                # 检查颜色判断正负
                roi_center = image[y+h//2, x+w//2]

                # 判断是否红色
                is_red = roi_center[2] > 200 and roi_center[0] < 50 and roi_center[1] < 50
                # 判断是否绿色
                is_green = roi_center[1] > 200 and roi_center[0] < 50 and roi_center[2] < 50

                if is_red or is_green:
                    result['current_value'] = value if is_red else -value
                    result['is_positive'] = is_red
                    break

        return result

    def parse_delta_chart(self, image: np.ndarray) -> Dict:
        """
        解析DELTA副图
        :param image: DELTA副图图像
        :return: DELTA数据
        """
        result = {
            'slope': None,
            'curve_points': [],
            'zero_line_y': None
        }

        # 1. 查找零轴
        height, width = image.shape[:2]
        lines = self.find_horizontal_lines(image, 'cyan', min_width=50, max_height=5)
        if lines:
            zero_lines = [l for l in lines if abs(l[1] - height/2) < height/4]
            if zero_lines:
                result['zero_line_y'] = zero_lines[0][1]

        # 2. 查找DELTA曲线（蓝色）
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower, upper = self.hsv_ranges['blue']
        blue_mask = cv2.inRange(hsv, np.array(lower), np.array(upper))

        # 查找轮廓
        contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # 找到最大的轮廓（主曲线）
            main_contour = max(contours, key=cv2.contourArea)

            # 获取所有点
            points = []
            for point in main_contour:
                x, y = point[0]
                points.append((x, y))

            # 按x坐标排序
            points.sort(key=lambda p: p[0])

            result['curve_points'] = points

            # 计算斜率（简单方法：比较第一个和最后一个点）
            if len(points) >= 2:
                first_point = points[0]
                last_point = points[-1]

                if last_point[1] < first_point[1]:
                    result['slope'] = 'up'
                elif last_point[1] > first_point[1]:
                    result['slope'] = 'down'
                else:
                    result['slope'] = 'flat'

        return result

    def parse_screenshot(self, image_path: str) -> Dict:
        """
        完整解析截图
        :param image_path: 图像路径
        :return: 解析结果
        """
        # 读取图像
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"无法读取图像：{image_path}")

        # 增强图像
        enhanced = self.enhance_image(image)

        height, width = enhanced.shape[:2]

        result = {
            'image_path': image_path,
            'image_size': {
                'width': width,
                'height': height
            },
            'main_chart': {},
            'sub_chart_1': {},  # 净量
            'sub_chart_2': {},  # DELTA
            'summary': {}
        }

        # 1. 解析主图（上半部分）
        main_chart_y = int(height * 0.45)
        main_chart = enhanced[:main_chart_y, :]
        main_chart_data = self.parse_main_chart(main_chart)
        result['main_chart'] = main_chart_data

        # 2. 解析净量副图（中间部分）
        net_volume_start_y = int(height * 0.45)
        net_volume_end_y = int(height * 0.72)
        net_volume_chart = enhanced[net_volume_start_y:net_volume_end_y, :]
        net_volume_data = self.parse_net_volume_chart(net_volume_chart)
        result['sub_chart_1'] = net_volume_data

        # 3. 解析DELTA副图（下半部分）
        delta_chart = enhanced[net_volume_end_y:, :]
        delta_data = self.parse_delta_chart(delta_chart)
        result['sub_chart_2'] = delta_data

        # 4. 生成摘要
        result['summary'] = self.generate_summary(result)

        return result

    def generate_summary(self, parse_result: Dict) -> Dict:
        """
        生成摘要
        """
        summary = {}

        # 当前价格
        if 'current_price' in parse_result['main_chart']:
            price = parse_result['main_chart']['current_price']
            if price:
                summary['current_price'] = price['price']

        # 支撑位
        support_prices = [s['price'] for s in parse_result['main_chart'].get('support_lines', []) if s['price']]
        if support_prices:
            summary['support_prices'] = support_prices

        # 阻力位
        resistance_prices = [r['price'] for r in parse_result['main_chart'].get('resistance_lines', []) if r['price']]
        if resistance_prices:
            summary['resistance_prices'] = resistance_prices

        # 标注
        annotations = parse_result['main_chart'].get('annotations', [])
        if annotations:
            summary['annotations'] = [a['type'] for a in annotations]

        # 净量
        net_volume = parse_result['sub_chart_1']
        if 'current_value' in net_volume and net_volume['current_value']:
            summary['net_volume'] = {
                'value': net_volume['current_value'],
                'is_positive': net_volume['is_positive']
            }

        # DELTA斜率
        delta = parse_result['sub_chart_2']
        if 'slope' in delta and delta['slope']:
            summary['delta_slope'] = delta['slope']

        return summary


def main():
    """测试函数"""
    import sys
    import os

    # 检查Tesseract
    try:
        pytesseract.get_tesseract_version()
        print(f"✓ Tesseract版本: {pytesseract.get_tesseract_version()}")
    except Exception as e:
        print(f"✗ 错误：Tesseract未安装")
        sys.exit(1)

    # 创建解析器
    parser = WenHuaScreenshotParser()

    # 测试截图
    test_image = "/root/.openclaw/media/inbound/0c4062f0-7feb-4f68-a145-5a36a5d54e1c.jpg"

    if os.path.exists(test_image):
        print(f"\n正在解析截图：{test_image}")

        try:
            # 解析
            result = parser.parse_screenshot(test_image)

            # 打印结果
            print("\n=== 解析结果 ===")
            print(json.dumps(result, indent=2, ensure_ascii=False))

            # 保存结果
            output_file = "/root/.openclaw/workspace/wenhua_parse_result.json"
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
