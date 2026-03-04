#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文华财经截图精准解析器V6 - Y坐标映射策略
不依赖OCR，直接通过Y坐标映射价格
"""

import cv2
import numpy as np
from typing import Dict, List, Optional
import json


class WenHuaParserV6:
    """文华财经截图解析器V6 - Y坐标映射"""

    def __init__(self):
        """初始化"""
        # 基于人工标注，建立Y坐标到价格的映射
        # 人工标注：S2=8.48, 现价=15.69, R2=17.58, 图中高点=20.10

    def find_price_axis(self, image: np.ndarray) -> Optional[Dict]:
        """
        查找价格坐标轴（Y轴）
        假设价格标签在左侧Y轴上
        """
        height, width = image.shape[:2]

        # 分割左侧区域（前15%用于价格轴）
        price_axis_width = int(width * 0.15)
        price_axis = image[:, :price_axis_width]

        # 查找白色背景
        white_mask = cv2.inRange(price_axis, np.array([200, 200, 200]),
                                     np.array([255, 255, 255]))

        # 查找黑色文字
        text_mask = cv2.inRange(price_axis, np.array([0, 0, 0]),
                                   np.array([50, 50, 50]))

        # 查找包含文字的行
        rows_with_text = []
        for y in range(height):
            if text_mask[y, :].any():
                rows_with_text.append(y)

        return {
            'price_axis_width': price_axis_width,
            'rows_with_text': rows_with_text
        }

    def find_horizontal_lines(self, image: np.ndarray, color_threshold: tuple) -> List[Dict]:
        """
        查找水平线（不依赖颜色，只依赖线条特征）
        """
        # 转换为灰度
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 边缘检测
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        # 霍夫变换
        lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=100,
                               minLineLength=500, maxLineGap=50)

        horizontal_lines = []

        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]

                # 计算角度
                angle = abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)

                # 筛选水平线（角度接近0或180）
                if angle < 5 or angle > 175:
                    horizontal_lines.append({
                        'x1': int(x1),
                        'y1': int(y1),
                        'x2': int(x2),
                        'y2': int(y2),
                        'y': int((y1 + y2) / 2),
                        'length': int(abs(x2 - x1))
                    })

        # 按y坐标排序
        horizontal_lines.sort(key=lambda l: l['y'])

        # 过滤重叠线
        filtered = self._filter_lines(horizontal_lines)

        return filtered

    def _filter_lines(self, lines: List[Dict]) -> List[Dict]:
        """过滤重叠的线"""
        if not lines:
            return []

        filtered = []
        current_line = lines[0]

        for line in lines[1:]:
            # 检查y坐标是否接近（±10像素）
            if abs(line['y'] - current_line['y']) <= 10:
                # 选择更长的线
                if line['length'] > current_line['length']:
                    current_line = line
            else:
                filtered.append(current_line)
                current_line = line

        # 添加最后一条
        filtered.append(current_line)

        return filtered

    def estimate_price_from_y(self, y: int, y_to_price_mapping: Dict[int, float]) -> Optional[float]:
        """
        根据Y坐标估算价格（使用插值）
        """
        # 如果Y坐标恰好有映射，直接返回
        if y in y_to_price_mapping:
            return y_to_price_mapping[y]

        # 否则进行线性插值
        y_values = sorted(y_to_price_mapping.keys())

        # 找到相邻的Y坐标
        for i in range(len(y_values) - 1):
            y1 = y_values[i]
            y2 = y_values[i + 1]

            if y1 <= y <= y2:
                # 线性插值
                price1 = y_to_price_mapping[y1]
                price2 = y_to_price_mapping[y2]

                if y2 != y1:
                    ratio = (y - y1) / (y2 - y1)
                    price = price1 + ratio * (price2 - price1)
                    return price

        return None

    def parse_screenshot_v6(self, image_path: str, manual_annotation: Dict) -> Dict:
        """
        使用V6方法解析截图
        需要人工标注数据建立Y坐标到价格的映射
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

        # 1. 查找所有水平线
        all_lines = self.find_horizontal_lines(main_chart, (0, 0, 0))

        # 2. 基于人工标注建立Y坐标映射
        # 需要通过视觉判断找到S2、R2、现价对应的Y坐标
        # 这里假设（实际需要人工标注每个价格的Y坐标）
        y_to_price_mapping = {
            # 需要人工标注这些值
            # y_s2: 8.48,
            # y_current: 15.69,
            # y_r2: 17.58,
            # y_high: 20.10
        }

        # 3. 根据Y坐标匹配价格
        result['main_chart']['horizontal_lines'] = all_lines

        # 4. 暂时返回原始数据
        result['summary'] = {
            'total_lines': len(all_lines),
            'note': '需要人工标注Y坐标到价格的映射'
        }

        return result

    def create_y_mapping_from_visual_analysis(self, image_path: str,
                                           manual_annotation: Dict) -> Dict[int, float]:
        """
        通过视觉分析创建Y坐标映射
        这需要人工查看图像并标注每个价格的Y坐标
        """
        return {
            's2_y': None,      # 需要人工标注
            'current_y': None,  # 需要人工标注
            'r2_y': None,       # 需要人工标注
            'high_y': None,     # 需要人工标注
        }


def main():
    """测试函数"""
    import os

    # 创建解析器
    parser = WenHuaParserV6()

    # 测试图片
    test_image = "/root/.openclaw/media/inbound/92ea67d8-5897-401a-825a-63df2f39ee75.jpg"

    # 人工标注
    manual_annotation = {
        'S2': 8.48,
        'current_price': 15.69,
        'R2': 17.58,
        'high_price': 20.10
    }

    if os.path.exists(test_image):
        print(f"\n正在解析截图：{test_image}")
        print(f"\n人工标注：")
        for key, value in manual_annotation.items():
            print(f"  {key}: {value}")

        try:
            # 解析
            result = parser.parse_screenshot_v6(test_image, manual_annotation)

            # 打印结果
            print("\n=== V6解析结果 ===")
            print(f"找到 {result['summary']['total_lines']} 条水平线")

            # 打印前10条线
            lines = result['main_chart'].get('horizontal_lines', [])
            for i, line in enumerate(lines[:10], 1):
                print(f"线{i}: y={line['y']}, 长度={line['length']}")

            # 保存结果
            output_file = "/root/.openclaw/workspace/v6_parse_result.json"
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
