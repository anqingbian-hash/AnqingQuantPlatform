#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量分析新提供的5张截图
"""

import cv2
import numpy as np
import json
import os
import sys
sys.path.append('/root/.openclaw/workspace')

from wkf_smart_analyzer_v2 import WKFSmartAnalyzerV2


def batch_analyze_images(image_dir: str):
    """批量分析图片"""
    
    # 新提供的5张图片
    new_images = [
        "4c346616-9e34-4393-98a6-7ad18166bb88.jpg",
        "bd68ec0c-7ef9-46cc-a6a5-9ec681af151a.jpg",
        "22da1809-bc46-425c-a119-df520e144d5a.jpg",
        "73c6ceb1-f3d3-4c63-8f1a-763c46a2ebdf.jpg",
        "af41ac9b-a52f-4d69-af01-d9e47a938bbf.jpg"
    ]
    
    # 创建分析器
    analyzer = WKFSmartAnalyzerV2()
    
    print("=" * 60)
    print("开始批量分析5张新截图")
    print("=" * 60)
    
    all_results = []
    
    for i, image_name in enumerate(new_images, 1):
        image_path = os.path.join(image_dir, image_name)
        
        if not os.path.exists(image_path):
            print(f"\n{i}. 图片不存在：{image_name}")
            continue
        
        print(f"\n{'='*60}")
        print(f"[{i}/5] 正在分析：{image_name}")
        print(f"{'='*60}")
        
        try:
            # 读取图像
            image = cv2.imread(image_path)
            height, width = image.shape[:2]
            print(f"尺寸：{width}x{height}")
            
            # 分割主图（上半部分）
            main_chart_end = int(height * 0.45)
            main_chart = image[:main_chart_end, :]
            
            # 1. 查找SR线
            print("\n[1] 查找SR线...")
            sr_lines = analyzer.find_sr_lines(main_chart)
            
            print(f"  支撑线（绿色）：{len(sr_lines['support_lines'])}条")
            for j, line in enumerate(sr_lines['support_lines'][:5], 1):
                print(f"    支撑{j}: y={line['y']}, 长度={line['length']}")
            
            print(f"  阻力线（红色）：{len(sr_lines['resistance_lines'])}条")
            for j, line in enumerate(sr_lines['resistance_lines'][:5], 1):
                print(f"    阻力{j}: y={line['y']}, 长度={line['length']}")
            
            # 2. 分析净量
            print("\n[2] 分析净量副图...")
            net_volume_start = int(height * 0.45)
            net_volume_end = int(height * 0.72)
            net_volume_chart = image[net_volume_start:net_volume_end, :]
            
            net_volume_analysis = analyzer.analyze_net_volume_color(net_volume_chart)
            
            print(f"  净量状态：{'净多（红）' if net_volume_analysis['net_long'] else '净空（绿）' if net_volume_analysis['net_short'] else '平衡'}")
            print(f"  红色像素：{net_volume_analysis['red_count']}")
            print(f"  绿色像素：{net_volume_analysis['green_count']}")
            
            # 3. 分析DELTA
            print("\n[3] 分析DELTA副图...")
            delta_chart = image[net_volume_end:, :]
            
            delta_analysis = analyzer.analyze_delta_slope(delta_chart)
            
            print(f"  DELTA斜率：{delta_analysis['slope']}")
            print(f"  曲线检测：{'是' if delta_analysis['curve_detected'] else '否'}")
            
            # 4. 综合判断
            print("\n[4] WKF系统综合判断...")
            
            # 基于规则的初步判断
            phase = "未知"
            confidence = 0
            
            if len(sr_lines['resistance_lines']) > 0 and len(sr_lines['support_lines']) > 0:
                # 有支撑线也有阻力线
                if net_volume_analysis['net_long']:
                    phase = "拉升期"
                    confidence = 60
                else:
                    phase = "震荡期"
                    confidence = 30
            elif len(sr_lines['resistance_lines']) > 0:
                # 只有阻力线
                if net_volume_analysis['net_short']:
                    phase = "派发期"
                    confidence = 70
                else:
                    phase = "震荡期"
                    confidence = 40
            elif len(sr_lines['support_lines']) > 0:
                # 只有支撑线
                if net_volume_analysis['net_long']:
                    phase = "拉升期"
                    confidence = 60
                else:
                    phase = "吸筹期"
                    confidence = 50
            else:
                # 没有明显SR线
                phase = "震荡期"
                confidence = 20
            
            print(f"  周期阶段：{phase}")
            print(f"  置信度：{confidence}%")
            
            # 保存结果
            result = {
                'image_name': image_name,
                'image_size': {'width': width, 'height': height},
                'support_lines': sr_lines['support_lines'][:5],
                'resistance_lines': sr_lines['resistance_lines'][:5],
                'net_volume_analysis': net_volume_analysis,
                'delta_analysis': delta_analysis,
                'wkf_judgment': {
                    'phase': phase,
                    'confidence': confidence
                }
            }
            
            all_results.append(result)
            
        except Exception as e:
            print(f"\n错误：{e}")
            import traceback
            traceback.print_exc()
    
    # 保存所有结果
    print("\n" + "=" * 60)
    print("批量分析完成，保存结果...")
    print("=" * 60)
    
    output_file = "/root/.openclaw/workspace/batch_analysis_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)
    
    print(f"\n结果已保存到：{output_file}")
    
    # 打印摘要
    print("\n" + "=" * 60)
    print("分析摘要")
    print("=" * 60)
    
    phase_count = {}
    for result in all_results:
        phase = result['wkf_judgment']['phase']
        if phase not in phase_count:
            phase_count[phase] = 0
        phase_count[phase] += 1
    
    for phase, count in phase_count.items():
        print(f"{phase}：{count}张")


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


def main():
    """主函数"""
    image_dir = "/root/.openclaw/media/inbound"
    
    if not os.path.exists(image_dir):
        print(f"错误：图片目录不存在：{image_dir}")
        return
    
    batch_analyze_images(image_dir)


if __name__ == "__main__":
    main()
