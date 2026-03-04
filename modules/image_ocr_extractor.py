#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文华财经截图OCR识别模块
使用OpenCV + Tesseract OCR提取关键数据
"""

import cv2
import numpy as np
import pytesseract
from typing import Dict, List, Optional, Tuple
import re
import json


class WenHuaScreenshotOCR:
    """文华财经截图OCR识别器"""

    def __init__(self):
        """初始化OCR识别器"""
        # 配置Tesseract参数
        self.tess_config = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789.-'

        # 颜色阈值（BGR格式）
        self.colors = {
            'red': (0, 0, 255),
            'green': (0, 255, 0),
            'yellow': (0, 255, 255),
            'blue': (255, 0, 0),
            'white': (255, 255, 255),
            'black': (0, 0, 0)
        }

        # 颜色范围（HSV格式）
        self.hsv_ranges = {
            'red': [(0, 120, 70), (10, 255, 255), (170, 120, 70), (180, 255, 255)],
            'green': [(40, 50, 50), (80, 255, 255)],
            'yellow': [(20, 100, 100), (30, 255, 255)],
            'blue': [(100, 100, 100), (130, 255, 255)]
        }

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        图像预处理
        :param image: 原始图像
        :return: 预处理后的图像
        """
        # 1. 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 2. 降噪
        denoised = cv2.fastNlMeansDenoising(gray, h=10)

        # 3. 增强对比度
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)

        # 4. 二值化（自适应阈值）
        binary = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)

        return binary

    def find_color_regions(self, image: np.ndarray, color_name: str) -> List[np.ndarray]:
        """
        查找特定颜色区域
        :param image: 原始图像
        :param color_name: 颜色名称（red/green/yellow/blue）
        :return: 掩码区域列表
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        if color_name in self.hsv_ranges:
            ranges = self.hsv_ranges[color_name]
            if len(ranges) == 4:  # 红色有两个范围
                lower1, upper1, lower2, upper2 = ranges
                mask1 = cv2.inRange(hsv, np.array(lower1), np.array(upper1))
                mask2 = cv2.inRange(hsv, np.array(lower2), np.array(upper2))
                mask = cv2.bitwise_or(mask1, mask2)
            else:
                lower, upper = ranges
                mask = cv2.inRange(hsv, np.array(lower), np.array(upper))

            # 形态学操作，去除小噪点
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

            # 查找轮廓
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            return contours

        return []

    def extract_text_from_region(self, image: np.ndarray, region: Tuple[int, int, int, int]) -> str:
        """
        从指定区域提取文本
        :param image: 原始图像
        :param region: 区域坐标 (x, y, width, height)
        :return: 提取的文本
        """
        x, y, w, h = region
        roi = image[y:y+h, x:x+w]

        # 预处理
        preprocessed = self.preprocess_image(roi)

        # OCR识别
        text = pytesseract.image_to_string(preprocessed, config=self.tess_config)

        return text.strip()

    def extract_numbers(self, text: str) -> List[float]:
        """
        从文本中提取数字
        :param text: 文本
        :return: 数字列表
        """
        # 匹配整数和小数
        pattern = r'\d+\.?\d*'
        matches = re.findall(pattern, text)
        return [float(m) for m in matches]

    def locate_price_label(self, image: np.ndarray) -> Optional[Dict]:
        """
        定位现价标签
        :param image: 原始图像
        :return: 现价信息字典
        """
        # 查找黄色区域（现价通常是黄色）
        yellow_contours = self.find_color_regions(image, 'yellow')

        for contour in yellow_contours:
            x, y, w, h = cv2.boundingRect(contour)

            # 如果区域足够大，可能是现价标签
            if w > 20 and h > 20:
                # 提取文本
                roi = image[y:y+h, x:x+w]
                preprocessed = self.preprocess_image(roi)
                text = pytesseract.image_to_string(preprocessed, config=self.tess_config)

                # 提取数字
                numbers = self.extract_numbers(text)
                if numbers:
                    return {
                        'x': x,
                        'y': y,
                        'width': w,
                        'height': h,
                        'price': numbers[0],
                        'text': text
                    }

        return None

    def locate_sr_lines(self, image: np.ndarray) -> List[Dict]:
        """
        定位支撑/阻力线
        :param image: 原始图像
        :return: 支撑/阻力线信息列表
        """
        sr_lines = []

        # 查找绿色区域（支撑线）
        green_contours = self.find_color_regions(image, 'green')
        for contour in green_contours:
            x, y, w, h = cv2.boundingRect(contour)
            # 水平线检测
            if w > 100 and h < 10:
                sr_lines.append({
                    'type': 'support',
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h
                })

        # 查找红色区域（阻力线）
        red_contours = self.find_color_regions(image, 'red')
        for contour in red_contours:
            x, y, w, h = cv2.boundingRect(contour)
            # 水平线检测
            if w > 100 and h < 10:
                sr_lines.append({
                    'type': 'resistance',
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h
                })

        return sr_lines

    def locate_annotations(self, image: np.ndarray) -> List[Dict]:
        """
        定位系统标注（LPS/LPSY/BC/SC）
        :param image: 原始图像
        :return: 标注信息列表
        """
        annotations = []

        # 查找文本区域
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        # 查找轮廓
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # 过滤掉过小的区域
            if w < 20 or h < 20:
                continue

            # 提取文本
            roi = image[y:y+h, x:x+w]
            preprocessed = self.preprocess_image(roi)
            text = pytesseract.image_to_string(preprocessed, config=self.tess_config).strip()

            # 检查是否是系统标注
            if text in ['LPS', 'LPSY', 'BC', 'SC', 'TEST']:
                annotations.append({
                    'type': text,
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h
                })

        return annotations

    def extract_net_volume(self, image: np.ndarray) -> Optional[Dict]:
        """
        提取净量数据
        :param image: 副图1（净量）图像
        :return: 净量数据字典
        """
        # 查找文本区域
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        # 提取文本
        preprocessed = self.preprocess_image(image)
        text = pytesseract.image_to_string(preprocessed, config=self.tess_config)

        # 提取数字
        numbers = self.extract_numbers(text)

        # 判断正负（通过颜色）
        red_contours = self.find_color_regions(image, 'red')
        green_contours = self.find_color_regions(image, 'green')

        if numbers:
            value = numbers[0]
            # 如果红色区域更多，可能是正值
            is_positive = len(red_contours) > len(green_contours)

            return {
                'value': value if is_positive else -value,
                'text': text,
                'is_positive': is_positive
            }

        return None

    def extract_delta_curve(self, image: np.ndarray) -> Optional[Dict]:
        """
        提取DELTA曲线信息
        :param image: 副图2（DELTA BAR）图像
        :return: DELTA曲线信息字典
        """
        # 查找曲线（蓝色区域）
        blue_contours = self.find_color_regions(image, 'blue')

        if blue_contours:
            # 找到最大的轮廓（主曲线）
            main_contour = max(blue_contours, key=cv2.contourArea)

            # 计算斜率
            x, y, w, h = cv2.boundingRect(main_contour)
            roi = image[y:y+h, x:x+w]

            # 简单斜率判断（基于轮廓的矩）
            M = cv2.moments(main_contour)
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])

                # 简单斜率判断（通过质心位置）
                slope_direction = 'up' if cy < h/2 else 'down'

                return {
                    'slope': slope_direction,
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h,
                    'contour_area': cv2.contourArea(main_contour)
                }

        return None

    def analyze_screenshot(self, image_path: str) -> Dict:
        """
        完整分析截图
        :param image_path: 图像路径
        :return: 分析结果字典
        """
        # 读取图像
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"无法读取图像：{image_path}")

        result = {
            'image_path': image_path,
            'main_chart': {},
            'sub_chart_1': {},  # 净量
            'sub_chart_2': {},  # DELTA
            'raw_data': {}
        }

        # 1. 定位现价
        price_info = self.locate_price_label(image)
        if price_info:
            result['main_chart']['current_price'] = price_info['price']
            result['main_chart']['price_region'] = {
                'x': price_info['x'],
                'y': price_info['y'],
                'width': price_info['width'],
                'height': price_info['height']
            }

        # 2. 定位支撑/阻力线
        sr_lines = self.locate_sr_lines(image)
        if sr_lines:
            result['main_chart']['sr_lines'] = sr_lines

        # 3. 定位系统标注
        annotations = self.locate_annotations(image)
        if annotations:
            result['main_chart']['annotations'] = annotations

        # 4. 假设副图区域（需要根据实际截图调整）
        # 这里假设副图在图像的下半部分
        height, width = image.shape[:2]

        # 副图1：净量（中间部分）
        if height > 300:
            sub_chart1 = image[height//3:2*height//3, :]
            net_volume = self.extract_net_volume(sub_chart1)
            if net_volume:
                result['sub_chart_1'] = net_volume

        # 副图2：DELTA（下半部分）
        if height > 400:
            sub_chart2 = image[2*height//3:, :]
            delta_curve = self.extract_delta_curve(sub_chart2)
            if delta_curve:
                result['sub_chart_2'] = delta_curve

        # 保存原始数据
        result['raw_data']['image_size'] = {
            'height': height,
            'width': width
        }

        return result


def main():
    """测试函数"""
    import sys
    import os

    # 检查Tesseract是否安装
    try:
        pytesseract.get_tesseract_version()
        print(f"Tesseract版本: {pytesseract.get_tesseract_version()}")
    except Exception as e:
        print(f"错误：Tesseract未安装或不在PATH中")
        print("请安装Tesseract OCR：")
        print("  Ubuntu/Debian: sudo apt-get install tesseract-ocr")
        print("  CentOS/RHEL: sudo yum install tesseract")
        print("  macOS: brew install tesseract")
        sys.exit(1)

    # 创建OCR识别器
    ocr = WenHuaScreenshotOCR()

    # 测试截图路径
    test_image = "/root/.openclaw/media/inbound/0c4062f0-7feb-4f68-a145-5a36a5d54e1c.jpg"

    if os.path.exists(test_image):
        print(f"\n正在分析截图：{test_image}")

        try:
            # 分析截图
            result = ocr.analyze_screenshot(test_image)

            # 打印结果
            print("\n=== 分析结果 ===")
            print(json.dumps(result, indent=2, ensure_ascii=False))

            # 保存结果
            output_file = "/root/.openclaw/workspace/ocr_analysis_result.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n结果已保存到：{output_file}")

        except Exception as e:
            print(f"错误：{e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"错误：测试图像不存在：{test_image}")


if __name__ == "__main__":
    main()
