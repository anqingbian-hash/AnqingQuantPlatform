#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量分析卞董提供的所有截图
"""

import cv2
import numpy as np
import json
import os
import sys
from typing import List, Dict

sys.path.append('/root/.openclaw/workspace')

from wkf_smart_analyzer_v2 import WKFSmartAnalyzerV2


class WKFBatchAnalyzer:
    """WKF系统批量分析器"""

    def __init__(self):
        """初始化"""
        self.analyzer = WKFSmartAnalyzerV2()

    def analyze_image(self, image_path: str, manual_data: dict = None) -> Dict:
        """
        分析单张图片
        """
        print(f"\n正在分析：{image_path}")

        if not os.path.exists(image_path):
            return {
                'success': False,
                'error': f"图片不存在：{image_path}"
            }

        try:
            # 读取图像
            image = cv2.imread(image_path)
            if image is None:
                return {
                    'success': False,
                    'error': f"无法读取图像：{image_path}"
                }

            # 分析
            result = self.analyzer.analyze_screenshot(image_path)

            # 添加人工标注数据（如果有）
            if manual_data:
                result['manual_annotation'] = manual_data

            # 生成WKF判断
            wkf_judgment = self._make_wkf_judgment(result)

            result['wkf_judgment'] = wkf_judgment

            return {
                'success': True,
                'image_path': image_path,
                'image_name': os.path.basename(image_path),
                'result': result
            }

        except Exception as e:
            return {
                'success': False,
                'image_path': image_path,
                'image_name': os.path.basename(image_path),
                'error': str(e)
            }

    def _make_wkf_judgment(self, analysis_result: Dict) -> Dict:
        """
        根据WKF系统规则生成判断
        """
        judgment = {
            'phase': 'unknown',  # 吸筹期、拉升期、派发期
            'signal': 'wait',  # wait、long、short、avoid
            'confidence': 0,
            'position_size': 0,
            'stop_loss': None,
            'take_profit': None,
            'risk_level': 'high'
        }

        # 获取分析数据
        main_chart = analysis_result.get('main_chart', {})
        sub_chart_1 = analysis_result.get('sub_chart_1', {})
        sub_chart_2 = analysis_result.get('sub_chart_2', {})

        # 获取支撑线和阻力线
        support_lines = main_chart.get('support_lines', [])
        resistance_lines = main_chart.get('resistance_lines', [])

        # 获取净量状态
        net_long = sub_chart_1.get('net_long', False)
        net_short = sub_chart_1.get('net_short', False)

        # 获取DELTA斜率
        delta_slope = sub_chart_2.get('slope', 'unknown')

        # WKF第一铁律判断
        # 派发期判断：只有净量是净空且DELTA向下
        if delta_slope == 'down' and not net_long and net_short:
            # 可能是派发期
            judgment['phase'] = 'distribution'
            judgment['confidence'] = 60
            judgment['signal'] = 'avoid'
            judgment['risk_level'] = 'high'

        # 拉升期判断：净量是净多且DELTA向上
        elif delta_slope == 'up' and net_long and not net_short:
            judgment['phase'] = 'markup'
            judgment['confidence'] = 80
            judgment['signal'] = 'long'
            judgment['risk_level'] = 'medium'

        # 震荡期判断：有支撑也有阻力，净量在零轴附近
        elif len(support_lines) > 0 and len(resistance_lines) > 0 and (abs(net_long - net_short) < 1000 or
                (net_long + net_short) < 1000):
            judgment['phase'] = 'accumulation'
            judgment['confidence'] = 50
            judgment['signal'] = 'wait'
            judgment['risk_level'] = 'medium'

        # 吸筹期判断：有支撑且净多
        elif len(support_lines) > 0 and net_long and not net_short:
            judgment['phase'] = 'accumulation'
            judgment['confidence'] = 60
            judgment['signal'] = 'wait'
            judgment['position_size'] = 8  # 吸筹期8%仓位

        # 默认：震荡期
        else:
            judgment['phase'] = 'distribution'
            judgment['confidence'] = 20
            judgment['signal'] = 'wait'

        return judgment

    def generate_wkf_report(self, image_name: str, analysis_result: Dict,
                              wkf_judgment: Dict,
                              image_number: int, total_images: int) -> Dict:
        """
        生成WKF格式报告
        """
        # 基本信息
        report = {
            'image_number': image_number,
            'total_images': total_images,
            'image_name': image_name,
            'timestamp': '2026-03-04 23:45',
            'analyst': '变形金刚（AI总经理）',
            'system': '君居合智金WKF时空选股系统'
        }

        # WKF分析结果
        wkf_analysis = {
            'phase': wkf_judgment['phase'],
            'confidence': wkf_judgment['confidence'],
            'trading_signal': wkf_judgment['signal'],
            'position_size': wkf_judgment['position_size'],
            'risk_level': wkf_judgment['risk_level']
        }

        # 技术指标
        technical_indicators = {
            'support_count': len(analysis_result.get('main_chart', {}).get('support_lines', [])),
            'resistance_count': len(analysis_result.get('main_chart', {}).get('resistance_lines', [])),
            'net_volume_state': {
                'is_long': analysis_result.get('sub_chart_1', {}).get('net_long', False),
                'is_short': analysis_result.get('sub_chart_1', {}).get('net_short', False)
            },
            'delta_slope': analysis_result.get('sub_chart_2', {}).get('slope', 'unknown')
        }

        report['wkf_analysis'] = wkf_analysis
        report['technical_indicators'] = technical_indicators

        # 操作建议
        recommendations = self._generate_recommendations(wkf_judgment, technical_indicators)

        report['recommendations'] = recommendations

        return report

    def _generate_recommendations(self, wkf_judgment: Dict,
                                  technical_indicators: Dict) -> Dict:
        """
        根据WKF规则生成操作建议
        """
        recs = {
            'trading_signal': 'wait',
            'position_size': 0,
            'entry_zone': 'unknown',
            'stop_loss': None,
            'take_profit': None,
            'risk_warning': [],
            'action_plan': []
        }

        phase = wkf_judgment.get('phase', 'unknown')
        signal = wkf_judgment.get('signal', 'wait')
        confidence = wkf_judgment.get('confidence', 0)

        support_count = technical_indicators.get('support_count', 0)
        resistance_count = technical_indicators.get('resistance_count', 0)
        net_long = technical_indicators.get('net_volume_state', {}).get('is_long', False)
        delta_slope = technical_indicators.get('delta_slope', 'unknown')

        # 根据相位和信号生成建议
        if phase == 'distribution':
            recs['trading_signal'] = 'avoid'
            recs['risk_warning'].append('第一铁律：派发期=全局无效（0分，0%仓位）')
            recs['risk_level'] = 'high'
            recs['action_plan'].append('观望，等待派发期结束')
            recs['position_size'] = 0

        elif phase == 'accumulation':
            recs['trading_signal'] = 'wait'
            recs['position_size'] = 8
            recs['entry_zone'] = '等待LPS或SC信号'
            recs['risk_warning'].append('吸筹期，轻仓试错')
            recs['risk_level'] = 'medium'

        elif phase == 'markup':
            if signal == 'long':
                recs['trading_signal'] = 'long'
                recs['position_size'] = 12
                recs['entry_zone'] = '等待回踩阻力线后入场'
                recs['action_plan'].append('等待回踩SR线后做多单')
                recs['risk_warning'].append('止损位设为最近支撑线下方，跌破无条件离场')
                recs['risk_level'] = 'medium'

            elif signal == 'short':
                recs['trading_signal'] = 'wait'
                recs['position_size'] = 0
                recs['entry_zone'] = '等待信号明确'
                recs['risk_warning'].append('信号不明确，继续观望')
                recs['risk_level'] = 'high'

            recs['risk_warning'].append('严格止损，不扛单')

        elif phase == 'distribution':
            recs['trading_signal'] = 'avoid'
            recs['position_size'] = 0
            recs['entry_zone'] = 'none'
            recs['risk_warning'].append('观望，等待市场明确方向')
            recs['risk_level'] = 'high'

        else:
            recs['trading_signal'] = 'wait'
            recs['position_size'] = 0
            recs['risk_warning'].append('需要更多信息判断周期阶段')

        return recs


def batch_analyze_all_images():
    """批量分析所有图片"""

    # 创建分析器
    analyzer = WKFBatchAnalyzer()

    # 图片目录
    image_dir = "/root/.openclaw/media/inbound"

    # 临时列表（用于测试）
    test_images = [
        "8a8bbb757c624437-a245-d6bf4d7ae2d7.jpg",  # 周线
        "32acd752777d43bd8-a245-d6bf4d7ae2d7.jpg",  # 日线
        "8625397b70bd4e5a-a245-d6bf4d7ae2d7.jpg",  # 1小时
        "ef91c1049e7d4cc9-b9e3-c7284fcaeeb4.jpg",  # 15分钟
        "98cba3566e422b451-a245-d6bf4d7ae2d7.jpg",  # 5分钟
        "f69a0f9e3443f93-9a324d4b5a28c7.jpg"   # 原图
    ]

    print("=" * 80)
    print("WKF系统批量分析")
    print("=" * 80)

    all_reports = []

    for i, image_name in enumerate(test_images, 1):
        image_path = f"{image_dir}/{image_name}"

        print(f"\n[{i}/{len(test_images)}] 正在分析：{image_name}")

        # 分析图片
        result = analyzer.analyze_image(image_path)

        if result['success']:
            # 生成报告
            report = analyzer.generate_wkf_report(
                image_name,
                result['result'],
                result.get('wkf_judgment', {}),
                i,
                len(test_images)
            )

            all_reports.append(report)

            # 打印关键信息
            print(f"  周期阶段：{report['wkf_analysis']['phase']}")
            print(f"  交易信号：{report['recommendations']['trading_signal']}")
            print(f"  仓位建议：{report['recommendations']['position_size']}%")
            print(f"  风险等级：{report['recommendations']['risk_level']}")
            print(f"  置信度：{report['wkf_analysis']['confidence']}%")
            print(f"  风险提示")
            for warning in report['recommendations']['risk_warning']:
                print(f"  ⚠️  {warning}")

        else:
            print(f"错误：{result.get('error', '未知错误')}")

    # 保存所有报告
    output_file = "/root/.openclaw/workspace/wkf_batch_analysis_reports.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_reports, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)

    # 打印统计
    print("\n" + "=" * 80)
    print("分析完成，统计摘要")
    print("=" * 80)

    # 统计周期阶段
    phase_count = {}
    signal_count = {}

    for report in all_reports:
        phase = report['wkf_analysis']['phase']
        phase_count[phase] = phase_count.get(phase, 0) + 1

    print(f"\n周期阶段分布：")
    for phase, count in phase_count.items():
        print(f"  {phase}：{count}张")

    # 统计交易信号
    for report in all_reports:
        signal = report['recommendations']['trading_signal']
        signal_count[signal] = signal_count.get(signal, 0) + 1

    print(f"\n交易信号分布：")
    for signal, count in signal_count.items():
        print(f"  {signal}：{count}张")

    print(f"\n总计：{len(all_reports)}张截图")
    print(f"结果已保存到：{output_file}")


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


if __name__ == "__main__":
    batch_analyze_all_images()
