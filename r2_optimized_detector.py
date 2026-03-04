#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
R2（阻力线）优化检测器
"""

import cv2
import numpy as np


class R2OptimizedDetector:
    """R2（阻力线）优化检测器"""

    def __init__(self):
        """初始化"""
        self.regions = {
            'main_chart': (0, int(1377 * 0.45))
        }

        # 优化后的白色阈值（放宽范围）
        self.white_lower = np.array([200, 200, 200])
        self.white_upper = np.array([255, 255, 255])

    def detect_r2(self, image_path: str) -> dict:
        """检测R2（阻力线）"""
        print(f"\n正在检测R2（阻力线）：{os.path.basename(image_path)}")

        # 读取图像
        image = cv2.imread(image_path)
        if image is None:
            return {'success': False, 'error': '无法读取图像'}

        height, width = image.shape[:2]

        # 提取主图区域
        main_chart = image[self.regions['main_chart'][0]:self.regions['main_chart'][1], :]

        # 方法1：颜色检测（简单快速）
        print(f"\n[方法1] 颜色检测...")
        r2_method1 = self._detect_r2_by_color_simple(main_chart, width)

        # 方法2：霍夫变换检测（优化参数）
        print(f"\n[方法2] 霍夫变换检测（优化参数）...")
        r2_method2 = self._detect_r2_by_hough_optimized(main_chart, width)

        # 综合结果（优先使用方法2）
        r2_y = None
        method = 'none'

        if r2_method2.get('detected', False):
            r2_y = r2_method2['y']
            method = 'hough'
        elif r2_method1.get('detected', False):
            r2_y = r2_method1['y']
            method = 'color'
        else:
            return {'success': True, 'r2_y': None, 'method': 'none', 'error': '未检测到R2'}

        result = {
            'success': True,
            'image_path': image_path,
            'image_name': os.path.basename(image_path),
            'r2_y': r2_y,
            'method': method,
            'method1': r2_method1,
            'method2': r2_method2
        }

        # 打印结果
        self._print_result(result)

        return result

    def _detect_r2_by_color_simple(self, image: np.ndarray, width: int) -> dict:
        """方法1：通过颜色检测R2（阻力线）- 简单快速"""
        # 白色掩码
        white_mask = cv2.inRange(image, self.white_lower, self.white_upper)

        # 统计每行的白色像素数
        row_white_counts = np.sum(white_mask, axis=1)

        if np.max(row_white_counts) < 100:
            return {'detected': False, 'error': '白色像素太少'}

        # 找到白色像素最多的20行
        top_rows = np.argsort(row_white_counts)[-20:]

        # 选择图片上半部分（Y<300）的最强白线
        for y in top_rows:
            if y < 300 and row_white_counts[y] > width * 0.3:
                return {
                    'detected': True,
                    'y': int(y + self.regions['main_chart'][0]),
                    'pixel_count': int(row_white_counts[y])
                }

        return {'detected': False, 'error': '未找到符合条件的R2'}

    def _detect_r2_by_hough_optimized(self, image: np.ndarray, width: int) -> dict:
        """方法2：优化的霍夫变换检测"""
        # 边缘检测
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 30, 100, apertureSize=3)

        # 霍夫变换检测水平线（优化参数）
        lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180,
                               threshold=40,  # 降低阈值
                               minLineLength=width * 0.2,  # 降低最小长度
                               maxLineGap=200)  # 增加最大间隔

        if lines is None or len(lines) == 0:
            return {'detected': False, 'error': '未检测到水平线'}

        # 筛选：水平线、在图片上半部分、白色
        candidate_lines = []
        for line in lines:
            x1, y1, x2, y2 = line[0]

            # 必须是水平线
            if abs(y1 - y2) > 5:
                continue

            # 必须在图片上半部分（Y<300）
            if y1 >= 300 or y2 >= 300:
                continue

            # 长度检查
            line_length = abs(x2 - x1)
            if line_length < width * 0.1:  # 降低最小长度要求
                continue

            # 检查颜色（白色）
            line_pixels = image[y1:y1+5, x1:x2]

            # 计算白色像素占比
            white_pixels = np.sum(
                (line_pixels[:, :, 0] >= 200) &
                (line_pixels[:, :, 1] >= 200) &
                (line_pixels[:, :, 2] >= 200)
            )
            white_ratio = white_pixels / (line_pixels.shape[0] * line_pixels.shape[1])

            # 白色占比>50%
            if white_ratio > 0.5:
                candidate_lines.append({
                    'y': int(y1),
                    'length': line_length,
                    'pixel_count': int(white_pixels),
                    'white_ratio': float(white_ratio)
                })

        if not candidate_lines:
            return {'detected': False, 'error': '未找到符合条件的R2'}

        # 选择Y值最小的（最上面的线）
        candidate_lines.sort(key=lambda x: x['y'])
        r2_line = candidate_lines[0]

        print(f"  找到{len(candidate_lines)}条候选线")
        print(f"  选择R2：y={r2_line['y']}, 长度={r2_line['length']}, 白色占比={r2_line['white_ratio']:.2f}")

        return {
            'detected': True,
            'y': r2_line['y'],
            'length': r2_line['length'],
            'pixel_count': r2_line['pixel_count'],
            'white_ratio': r2_line['white_ratio']
        }

    def _print_result(self, result: dict):
        """打印结果"""
        print(f"\n=== R2检测结果 ===")
        if result['r2_y'] is not None:
            print(f"R2 Y坐标：{result['r2_y']}")
            print(f"检测方法：{result['method']}")
        else:
            print(f"未检测到R2：{result.get('method1', {}).get('error', '未知')}")


def test_r2_detection():
    """测试R2检测"""

    # 5张图片
    test_images = [
        "9c5927d6-a315-4f12-9768-a9a2941aacfc.jpg",
        "437746cd-65be-4603-938c-85debf232d94.jpg",
        "19397363-b6cd-4344-93cc-870d7d872a83.jpg",
        "7ce8ed01-8ac5-45c4-945c-e3b82dda8fe2.jpg",
        "6f492e6b-7b20-4356-b939-5b17422dadf2.jpg"
    ]

    periods = ['周线', '日线', '1小时', '15分钟', '5分钟']

    detector = R2OptimizedDetector()

    print("=" * 80)
    print("R2（阻力线）优化检测测试")
    print("=" * 80)

    all_results = []

    for i, image_name in enumerate(test_images):
        image_path = f"/root/.openclaw/media/inbound/{image_name}"

        if not os.path.exists(image_path):
            print(f"\n{i+1}/{len(test_images)} 图片不存在：{image_name}")
            continue

        print(f"\n{'='*80}")
        print(f"[{i+1}/{len(test_images)}] {periods[i]}R2检测")
        print(f"{'='*80}")

        try:
            result = detector.detect_r2(image_path)
            result['period'] = periods[i]
            all_results.append(result)

        except Exception as e:
            print(f"\n错误：{e}")
            import traceback
            traceback.print_exc()

    # 打印汇总
    print("\n" + "=" * 80)
    print("R2检测汇总")
    print("=" * 80)

    detected_count = 0
    for result in all_results:
        if result.get('r2_y') is not None:
            detected_count += 1
            period = result.get('period', 'unknown')
            r2_y = result.get('r2_y', 'unknown')
            method = result.get('method', 'unknown')
            print(f"{period}: R2 Y={r2_y}, 检测方法={method}")
        else:
            period = result.get('period', 'unknown')
            error = result.get('method1', {}).get('error', '未知')
            print(f"{period}: 未检测到R2（{error}）")

    print(f"\n总计：{detected_count}/{len(all_results)}个周期检测到R2")


if __name__ == "__main__":
    test_r2_detection()
