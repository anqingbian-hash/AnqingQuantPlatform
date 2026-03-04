#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文华财经截图精准解析器V2
基于实际截图格式优化
"""

import cv2
import numpy as np
import pytesseract
from typing import Dict, List, Optional, Tuple
import re
import json


class WenHuaParserV2:
    """文华财经截图解析器V2"""

    def __init__(self):
        """初始化"""
        # Tesseract配置
        self.tess_config = '--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789.-'

    def extract_price_label(self, image: np.ndarray, x: int, y: int) -> Optional[float]:
        """
        在指定坐标附近提取价格标签
        文华财经的价格标签通常在SR线右侧
        """
        height, width = image.shape[:2]

        # 提取ROI（标签区域：线右侧）
        roi_x = x + 5
        roi_y = max(0, y - 10)
        roi_w = 100
        roi_h = 25

        # 确保在图像范围内
        roi_x = min(roi_x, width - roi_w)
        roi_y = min(roi_y, height - roi_h)

        roi = image[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]

        # 转灰度
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # OCR识别
        text = pytesseract.image_to_string(gray, config=self.tess_config).strip()

        # 提取数字
        numbers = re.findall(r'\d+\.?\d*', text)
        if numbers:
            return float(numbers[0])

        return None

    def find_sr_lines(self, image: np.ndarray) -> Dict:
        """
        查找支撑/阻力线
        基于霍夫变换检测水平线
        """
        result = {
            'support_lines': [],
            'resistance_lines': []
        }

        # 转换为灰度
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 边缘检测
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        # 霍夫变换检测直线
        lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=50,
                               minLineLength=100, maxLineGap=20)

        if lines is not None:
            # 筛选水平线（角度接近0或180度）
            horizontal_lines = []

            for line in lines:
                x1, y1, x2, y2 = line[0]

                # 检查是否是水平线
                angle = abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)

                # 角度在±10度范围内
                if angle < 10 or angle > 170:
                    horizontal_lines.append({
                        'x1': x1,
                        'y1': y1,
                        'x2': x2,
                        'y2': y2,
                        'y': (y1 + y2) // 2,
                        'length': abs(x2 - x1)
                    })

            # 按y坐标排序
            horizontal_lines.sort(key=lambda l: l['y'])

            # 过滤短线和重叠线
            filtered_lines = self._filter_lines(horizontal_lines)

            # 分类支撑线和阻力线（基于颜色）
            for line in filtered_lines:
                y = line['y']
                x = line['x1']

                # 检查线中点颜色
                height, width = image.shape[:2]
                mid_x = x + line['length'] // 2

                if 0 <= mid_x < width and 0 <= y < height:
                    pixel = image[y, mid_x]

                    # BGR颜色判断
                    # 红色：B低，G低，R高
                    is_red = pixel[2] > 150 and pixel[0] < 100 and pixel[1] < 100
                    # 绿色：B低，G高，R低
                    is_green = pixel[1] > 150 and pixel[0] < 100 and pixel[2] < 100

                    # 提取价格标签
                    price = self.extract_price_label(image, mid_x, y)

                    if is_red:
                        result['resistance_lines'].append({
                            'y': y,
                            'price': price,
                            'line': line
                        })
                    elif is_green:
                        result['support_lines'].append({
                            'y': y,
                            'price': price,
                            'line': line
                        })

        return result

    def _filter_lines(self, lines: List[Dict]) -> List[Dict]:
        """
        过滤重叠的线
        """
        if not lines:
            return []

        filtered = []
        current_line = lines[0]

        for line in lines[1:]:
            # 检查y坐标是否接近（±5像素）
            if abs(line['y'] - current_line['y']) <= 5:
                # 选择更长的线
                if line['length'] > current_line['length']:
                    current_line = line
            else:
                filtered.append(current_line)
                current_line = line

        # 添加最后一条
        filtered.append(current_line)

        return filtered

    def find_annotations(self, image: np.ndarray) -> List[Dict]:
        """
        查找系统标注（LPS/LPSY/BC/SC）
        """
        annotations = []

        # 转换为灰度
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 二值化
        binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        # 查找轮廓
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # 过滤小区域
            if w < 20 or h < 10:
                continue

            # 提取ROI
            roi = image[y:y+h, x:x+w]

            # OCR识别
            text = pytesseract.image_to_string(roi, config=self.tess_config).strip().upper()

            # 检查是否是标注
            if text in ['LPS', 'LPSY', 'BC', 'SC', 'TEST', 'SOS', 'SOW']:
                annotations.append({
                    'type': text,
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h
                })

        return annotations

    def find_current_price(self, image: np.ndarray) -> Optional[Dict]:
        """
        查找现价
        现价通常是黄色高亮显示的数字
        """
        height, width = image.shape[:2]

        # 转换为HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # 黄色范围
        lower = np.array([20, 100, 100])
        upper = np.array([30, 255, 255])

        # 创建掩码
        mask = cv2.inRange(hsv, lower, upper)

        # 查找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # 过滤
            if w < 50 or h < 20:
                continue

            # 提取ROI
            roi = image[y:y+h, x:x+w]

            # 转灰度
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            # OCR识别
            text = pytesseract.image_to_string(gray, config=self.tess_config).strip()

            # 提取数字
            numbers = re.findall(r'\d+\.?\d*', text)
            if numbers:
                return {
                    'price': float(numbers[0]),
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h,
                    'text': text
                }

        return None

    def extract_net_volume(self, image: np.ndarray) -> Dict:
        """
        提取净量数据
        """
        result = {
            'value': None,
            'is_positive': None,
            'text': ''
        }

        # 转换为灰度
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # OCR识别整个副图
        text = pytesseract.image_to_string(gray, config=self.tess_config).strip()

        result['text'] = text

        # 提取数字
        numbers = re.findall(r'\d+\.?\d*', text)

        if numbers:
            # 判断正负（通过颜色）
            height, width = image.shape[:2]

            # 检查图像中心区域的颜色
            center_y = height // 2
            center_x = width // 4  # 左侧区域（数字通常在左侧）

            if 0 <= center_x < width and 0 <= center_y < height:
                pixel = image[center_y, center_x]

                # BGR颜色判断
                is_red = pixel[2] > 150 and pixel[0] < 100 and pixel[1] < 100
                is_green = pixel[1] > 150 and pixel[0] < 100 and pixel[2] < 100

                value = float(numbers[0])

                if is_red:
                    result['value'] = value
                    result['is_positive'] = True
                elif is_green:
                    result['value'] = -value
                    result['is_positive'] = False

        return result

    def extract_delta_info(self, image: np.ndarray) -> Dict:
        """
        提取DELTA曲线信息
        """
        result = {
            'slope': None,
            'curve_detected': False
        }

        # 转换为灰度
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 边缘检测
        edges = cv2.Canny(gray, 50, 150)

        # 查找轮廓
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # 找到最大的轮廓（主曲线）
            main_contour = max(contours, key=cv2.contourArea)

            # 获取点集
            points = []
            for point in main_contour:
                x, y = point[0]
                points.append((x, y))

            if len(points) >= 2:
                # 按x坐标排序
                points.sort(key=lambda p: p[0])

                # 计算斜率（简单方法：首尾点）
                first_point = points[0]
                last_point = points[-1]

                dy = last_point[1] - first_point[1]
                dx = last_point[0] - first_point[0]

                if dx != 0:
                    slope = dy / dx

                    if slope < -0.5:
                        result['slope'] = 'up'  # 图像y轴向下，负斜率表示向上
                    elif slope > 0.5:
                        result['slope'] = 'down'
                    else:
                        result['slope'] = 'flat'

                    result['curve_detected'] = True

        return result

    def parse_screenshot(self, image_path: str) -> Dict:
        """
        完整解析截图
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
            'sub_chart_1': {},
            'sub_chart_2': {},
            'summary': {}
        }

        # 1. 解析主图（上半部分）
        main_chart_end = int(height * 0.45)
        main_chart = image[:main_chart_end, :]

        # 查找现价
        current_price = self.find_current_price(main_chart)
        if current_price:
            result['main_chart']['current_price'] = current_price

        # 查找SR线
        sr_lines = self.find_sr_lines(main_chart)
        result['main_chart']['support_lines'] = sr_lines['support_lines']
        result['main_chart']['resistance_lines'] = sr_lines['resistance_lines']

        # 查找标注
        annotations = self.find_annotations(main_chart)
        result['main_chart']['annotations'] = annotations

        # 2. 解析净量副图（中间部分）
        net_volume_start = int(height * 0.45)
        net_volume_end = int(height * 0.72)
        net_volume_chart = image[net_volume_start:net_volume_end, :]

        net_volume_data = self.extract_net_volume(net_volume_chart)
        result['sub_chart_1'] = net_volume_data

        # 3. 解析DELTA副图（下半部分）
        delta_chart = image[net_volume_end:, :]

        delta_data = self.extract_delta_info(delta_chart)
        result['sub_chart_2'] = delta_data

        # 4. 生成摘要
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

        # 标注
        annotations = parse_result['main_chart'].get('annotations', [])
        if annotations:
            summary['annotations'] = [a['type'] for a in annotations]

        # 净量
        net_volume = parse_result['sub_chart_1']
        if net_volume.get('value') is not None:
            summary['net_volume'] = {
                'value': net_volume['value'],
                'is_positive': net_volume['is_positive']
            }

        # DELTA斜率
        delta = parse_result['sub_chart_2']
        if delta.get('slope'):
            summary['delta_slope'] = delta['slope']

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
    parser = WenHuaParserV2()

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
            output_file = "/root/.openclaw/workspace/wenhua_v2_parse_result.json"
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
