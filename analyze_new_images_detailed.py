#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成详细的WKF系统分析报告
"""

import cv2
import numpy as np
import json
from typing import Dict, List
import os
import sys
sys.path.append('/root/.openclaw/workspace')

from wkf_smart_analyzer_v2 import WKFSmartAnalyzerV2


def generate_wkf_report(image_path: str) -> Dict:
    """生成WKF系统分析报告"""

    # 创建分析器
    analyzer = WKFSmartAnalyzerV2()

    # 分析
    result = analyzer.parse_screenshot(image_path)

    # WKF判断
    judgment = {
        'phase': 'unknown',
        'confidence': 0,
        'trading_signal': 'wait',
        'position_size': 0
        'stop_loss': None,
        'take_profit': None,
        'risk_level': 'high'
    }

    # 简化判断逻辑
    delta_slope = result['sub_chart_2'].get('slope', 'unknown')
    net_long = result['sub_chart_1'].get('net_long', False)
    support_count = len(result['main_chart'].get('support_lines', []))
    resistance_count = len(result['main_chart'].get('resistance_lines', []))

    if delta_slope == 'down' and not net_long:
        judgment['phase'] = 'distribution'
        judgment['confidence'] = 70
        judgment['trading_signal'] = 'avoid'
        judgment['risk_level'] = 'high'
    elif support_count > 0 and net_long:
        judgment['phase'] = 'markup'
        judgment['confidence'] = 60
        judgment['trading_signal'] = 'wait'
        judgment['position_size'] = 8
        judgment['risk_level'] = 'medium'
    elif resistance_count > 0 and net_long:
        judgment['phase'] = 'markup'
        judgment['confidence'] = 80
        judgment['trading_signal'] = 'long'
        judgment['position_size'] = 12
        judgment['risk_level'] = 'medium'
    elif support_count > 0 and not net_long:
        judgment['phase'] = 'accumulation'
        judgment['confidence'] = 40
        judgment['trading_signal'] = 'wait'
        judgment['position_size'] = 8
        judgment['risk_level'] = 'medium'
    else:
        judgment['phase'] = 'unknown'
        judgment['confidence'] = 20
        judgment['trading_signal'] = 'wait'
        judgment['risk_level'] = 'high'

    return {
        'image_path': image_path,
        'wkf_analysis': judgment,
        'raw_data': result
    }


def batch_analyze_with_wkf():
    """批量分析"""

    # 新提供的5张图片
    new_images = [
        "d3b66f9a-005f-4a53-8029-6d894692ab2a.jpg",
        "33f51085-22f2-494d-ab9d-a349324ca5c8.jpg",
        "b021ec8-2284-420e-bc8a-071d846f44e6.jpg",
        "19f178cc-d9f4-4cc9-b9e3-c7284fcaeeb4.jpg",
        "753d9e92-3070-4a89-88dd-6def6e8e543c.jpg"
    ]

    print("=" * 80)
    print("开始WKF系统批量分析")
    print("=" * 80)

    all_results = []

    for i, image_name in enumerate(new_images, 1):
        image_path = f"/root/.openclaw/media/inbound/{image_name}"

        if not os.path.exists(image_path):
            print(f"\n{i}/{len(new_images)} 图片不存在：{image_name}")
            continue

        print(f"\n{'='*80}")
        print(f"[{i}/{len(new_images)}] 正在分析：{image_name}")
        print("=" * 80)

        try:
            # WKF分析
            result = generate_wkf_report(image_path)

            # 打印结果
            print("\n=== WKF系统判断 ===")

            # 周期阶段
            phase = result['wkf_analysis']['phase']
            phase_cn = {
                'accumulation': '吸筹期',
                'markup': '拉升期',
                'distribution': '派发期',
                'unknown': '未知'
            }.get(phase, phase)

            confidence = result['wkf_analysis']['confidence']
            signal = result['wkf_analysis']['trading_signal']
            signal_cn = {
                'long': '做多',
                'short': '做空',
                'wait': '观望',
                'avoid': '避开'
            }.get(signal, signal)
            position_size = result['wkf_analysis']['position_size']
            risk_level = result['wkf_analysis']['risk_level']
            risk_level_cn = {
                'low': '低',
                'medium': '中',
                'high': '高'
            }.get(risk_level, risk_level)

            print(f"周期阶段：{phase_cn}")
            print(f"置信度：{confidence}%")
            print(f"交易信号：{signal_cn}")
            print(f"建议仓位：{position_size}%")

            # 风险等级
            print(f"风险等级：{risk_level_cn}")

            # SR线
            print(f"\nSR线分析：")
            support_lines = result['raw_data']['main_chart'].get('support_lines', [])
            resistance_lines = result['raw_data']['main_chart'].get('resistance_lines', [])

            print(f"支撑线：{len(support_lines)}条")
            for j, line in enumerate(support_lines[:3], 1):
                print(f"  支撑{j}: y={line.get('y', 'N/A')}")

            print(f"阻力线：{len(resistance_lines)}条")
            for j, line in enumerate(resistance_lines[:3], 1):
                print(f"  阻力{j}: y={line.get('y', 'N/A')}")

            # 净量
            net_volume = result['raw_data']['sub_chart_1']
            print(f"\n净量分析：")
            if net_long:
                print(f"  状态：净多（红）")
                print(f"  红色像素：{net_volume.get('red_count', 0)}")
            else:
                print(f"  状态：净空（绿）")
                print(f"  绿色像素：{net_volume.get('green_count', 0)}")

            # DELTA
            delta = result['raw_data']['sub_chart_2']
            print(f"\nDELTA分析：")
            print(f"  斜率：{delta.get('slope', 'unknown')}")

            # 操作建议
            print(f"\n=== 操作建议 ===")

            if signal == 'avoid':
                print("✗ 当前处于派发期，禁止开仓")
                print("   建议：观望，等待派发期结束")
            elif signal == 'wait':
                print("⏳ 信号不明确，建议观望")
                print("   建议：继续观察")
            elif signal == 'long':
                print(f"✓ 建议开多单")
                print(f"   仓位：{position_size}%")
                print(f"   风险：{risk_level_cn}")
            elif signal == 'short':
                print(f"✓ 建议开空单")
                print(f"   仓位：{position_size}%")
                print(f"   风险：{risk_level_cn}")

            # 保存结果
            all_results.append(result)

        except Exception as e:
            print(f"\n错误：{e}")
            import traceback
            traceback.print_exc()

    # 保存所有结果
    output_file = "/root/.openclaw/workspace/wkf_batch_analysis_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print(f"所有分析结果已保存到：{output_file}")

    # 打印统计摘要
    print("\n=== 统计摘要 ===")

    phase_stats = {}
    for result in all_results:
        phase = result['wkf_analysis']['phase']
        phase_stats[phase] = phase_stats.get(phase, 0) + 1

    print("周期阶段统计：")
    for phase, count in phase_stats.items():
        print(f"  {phase}：{count}张")


if __name__ == "__main__":
    batch_analyze_with_wkf()
