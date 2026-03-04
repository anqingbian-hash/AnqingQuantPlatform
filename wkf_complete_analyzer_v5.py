#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WKF Complete Analyzer V5
包含：SR线识别、Y坐标价格映射、顶部形态检测（BC/SC）、底部形态检测（LPS/SC）、WKF系统综合判断
"""

import cv2
import numpy as np
import json
import os
from typing import Dict, List, Tuple
import sys

sys.path.append('/root/.openclaw/workspace')

# Import pattern detectors
from wkf_bc_pattern_detector import WKFBCPatternDetector
from wkf_sc_pattern_detector import WKFSCPatternDetector
from wkf_lps_pattern_detector import WKFLPSPatternDetector
from wkf_lpsy_pattern_detector import WKFLPSYPatternDetector

from wkf_full_analyzer_fixed import WKFFullAnalyzerFixed

class NumpyEncoder(json.JSONEncoder):
    """Numpy type JSON encoder"""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int32, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


class WKFCompleteAnalyzerV5:
    """WKF Complete Analyzer V5 with Pattern Detection"""
    
    def __init__(self):
        """Initialize analyzer"""
        print("[WKF Complete Analyzer V5] Initializing...")
        
        # Initialize pattern detectors
        self.bc_detector = WKFBCPatternDetector()
        self.sc_detector = WKFSCPatternDetector()
        self.lps_detector = WKFLPSPatternDetector()
        self.lpsy_detector = WKFLPSYPatternDetector()
        
        # Initialize base WKF analyzer
        self.wkf_analyzer = WKFFullAnalyzerFixed()
        
        print("[WKF Complete Analyzer V5] Pattern detectors initialized")
    
    def analyze_image(self, image_path: str, period: str) -> Dict:
        """Complete WKF analysis with pattern detection"""
        print(f"\n{'='*80}")
        print(f"[WKF Complete Analyzer V5] Analyzing: {os.path.basename(image_path)}")
        print(f"{'='*80}")
        print(f"Period: {period}")
        print(f"{'='*80}")
        
        try:
            # 1. Detect BC pattern (Buying Climax)
            print("\n[1/5] Detecting BC Pattern (Buying Climax)...")
            bc_result = self.bc_detector.detect_bc_pattern(image_path)
            
            # 2. Detect SC pattern (Selling Climax)
            print("\n[2/5] Detecting SC Pattern (Selling Climax)...")
            sc_result = self.sc_detector.detect_sc_pattern(image_path)
            
            # 3. Detect LPS pattern (Last Point of Support)
            print("\n[3/5] Detecting LPS Pattern (Last Point of Support)...")
            lps_result = self.lps_detector.detect_lps_pattern(image_path)
            
            # 4. Detect LPSY pattern (Last Point of Supply)
            print("\n[4/5] Detecting LPSY Pattern (Last Point of Supply)...")
            lpsy_result = self.lpsy_detector.detect_lpsy_pattern(image_path)
            
            # 5. Base WKF analysis
            print("\n[5/5] Base WKF Analysis...")
            base_analysis = self.wkf_analyzer.analyze_image(image_path, period)
            
            # 6. Enhanced WKF judgment with patterns
            print("\n[6/5] Enhanced WKF Judgment...")
            enhanced_judgment = self._enhance_wkf_judgment(
                base_analysis,
                bc_result,
                sc_result,
                lps_result,
                lpsy_result
            )
            
            # 7. Generate recommendations
            print("\n[7/7] Generating Recommendations...")
            recommendations = self._generate_recommendations(enhanced_judgment)
            
            # 8. Print summary
            self._print_summary(
                period,
                bc_result,
                sc_result,
                lps_result,
                lpsy_result,
                enhanced_judgment,
                recommendations
            )
            
            return {
                'success': True,
                'image_path': image_path,
                'image_name': os.path.basename(image_path),
                'period': period,
                'bc_pattern': bc_result,
                'sc_pattern': sc_result,
                'lps_pattern': lps_result,
                'lpsy_pattern': lpsy_result,
                'base_analysis': base_analysis,
                'enhanced_judgment': enhanced_judgment,
                'recommendations': recommendations
            }
            
        except Exception as e:
            print(f"\n[ERROR] Analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'image_path': image_path,
                'image_name': os.path.basename(image_path),
                'period': period,
                'error': str(e)
            }
    
    def _enhance_wkf_judgment(self,
                              base_analysis: Dict,
                              bc_result: Dict,
                              sc_result: Dict,
                              lps_result: Dict,
                              lpsy_result: Dict) -> Dict:
        """Enhance WKF judgment with pattern detection"""
        
        # Get base WKF judgment
        base_judgment = base_analysis.get('wkf_judgment', {})
        wkf_phase = base_judgment.get('phase', 'unknown')
        wkf_signal = base_judgment.get('signal', 'wait')
        wkf_confidence = base_judgment.get('confidence', 0)
        
        # Get pattern detection results
        bc_detected = bc_result.get('detected', False)
        bc_confidence = bc_result.get('confidence', 0)
        
        sc_detected = sc_result.get('detected', False)
        sc_confidence = sc_result.get('confidence', 0)
        
        lps_detected = lps_result.get('detected', False)
        lps_confidence = lps_result.get('confidence', 0)
        
        lpsy_detected = lpsy_result.get('detected', False)
        lpsy_confidence = lpsy_result.get('confidence', 0)
        
        # Count detected patterns
        top_patterns_detected = sum([bc_detected, lpsy_detected])
        bottom_patterns_detected = sum([sc_detected, lps_detected])
        
        # Enhanced judgment
        enhanced_judgment = {
            'base_phase': wkf_phase,
            'base_signal': wkf_signal,
            'base_confidence': wkf_confidence,
            'top_patterns': {
                'bc': bc_detected,
                'lpsy': lpsy_detected,
                'count': top_patterns_detected
            },
            'bottom_patterns': {
                'sc': sc_detected,
                'lps': lps_detected,
                'count': bottom_patterns_detected
            },
            'enhanced_phase': wkf_phase,
            'enhanced_signal': wkf_signal,
            'enhanced_confidence': wkf_confidence,
            'enhancement_description': '无形态增强'
        }
        
        # Enhancement logic
        if bc_detected and bc_confidence >= 70:
            # BC pattern detected - reduce position
            enhanced_judgment['enhancement_description'] = 'BC形态：短期高点，注意回调，降低仓位'
            if wkf_signal == 'long':
                enhanced_judgment['enhanced_signal'] = 'wait'
                enhanced_judgment['enhanced_confidence'] = min(wkf_confidence + 20, 100)
        
        elif lpsy_detected and lpsy_confidence >= 70:
            # LPSY pattern detected - short signal
            enhanced_judgment['enhancement_description'] = 'LPSY形态：二卖位置，高抛参考'
            enhanced_judgment['enhanced_signal'] = 'short'
            enhanced_judgment['enhanced_confidence'] = min(wkf_confidence + 20, 100)
        
        elif lps_detected and lps_confidence >= 70:
            # LPS pattern detected - long signal
            enhanced_judgment['enhancement_description'] = 'LPS形态：二买位置，低吸参考'
            enhanced_judgment['enhanced_signal'] = 'long'
            enhanced_judgment['enhanced_confidence'] = min(wkf_confidence + 20, 100)
        
        elif sc_detected and sc_confidence >= 70:
            # SC pattern detected - consider bounce
            enhanced_judgment['enhancement_description'] = 'SC形态：短期低点，考虑反弹'
            if wkf_signal != 'long':
                enhanced_judgment['enhanced_signal'] = 'wait'
                enhanced_judgment['enhanced_confidence'] = min(wkf_confidence + 10, 100)
        
        return enhanced_judgment
    
    def _generate_recommendations(self, enhanced_judgment: Dict) -> Dict:
        """Generate trading recommendations"""
        
        enhanced_signal = enhanced_judgment.get('enhanced_signal', 'wait')
        enhanced_confidence = enhanced_judgment.get('enhanced_confidence', 0)
        enhancement_description = enhanced_judgment.get('enhancement_description', '无形态增强')
        
        # Default recommendations
        recommendations = {
            'trading_signal': enhanced_signal,
            'position_size': 0,
            'entry_zone': 'unknown',
            'stop_loss': None,
            'take_profit': None,
            'risk_level': 'high',
            'risk_warning': [],
            'action_plan': [],
            'enhancement': enhancement_description
        }
        
        # Generate recommendations based on signal
        if enhanced_signal == 'long':
            recommendations['trading_signal'] = 'long'
            recommendations['position_size'] = 12
            recommendations['entry_zone'] = '回踩SR线后入场'
            recommendations['stop_loss'] = 'S2下方3-5%'
            recommendations['take_profit'] = 'R2-2%'
            recommendations['risk_level'] = 'medium'
            recommendations['risk_warning'].append('严格止损，不扛单')
            recommendations['action_plan'].append('回踩SR线后做多单')
            
        elif enhanced_signal == 'short':
            recommendations['trading_signal'] = 'short'
            recommendations['position_size'] = 0
            recommendations['entry_zone'] = '回踩R2后入场'
            recommendations['stop_loss'] = None
            recommendations['take_profit'] = None
            recommendations['risk_level'] = 'high'
            recommendations['risk_warning'].append('高抛参考')
            recommendations['action_plan'].append('回踩R2后做空单')
            
        elif enhanced_signal == 'wait':
            recommendations['trading_signal'] = 'wait'
            recommendations['position_size'] = 8
            recommendations['entry_zone'] = '观望，等待明确信号'
            recommendations['stop_loss'] = None
            recommendations['take_profit'] = None
            recommendations['risk_level'] = 'medium'
            recommendations['action_plan'].append('观望，等待明确信号')
        
        # Add enhancement to warnings
        if enhancement_description != '无形态增强':
            recommendations['risk_warning'].append(enhancement_description)
        
        return recommendations
    
    def _print_summary(self,
                      period: str,
                      bc_result: Dict,
                      sc_result: Dict,
                      lps_result: Dict,
                      lpsy_result: Dict,
                      enhanced_judgment: Dict,
                      recommendations: Dict):
        """Print analysis summary"""
        
        print(f"\n{'='*80}")
        print(f"[WKF Complete Analyzer V5] Analysis Summary - {period}")
        print(f"{'='*80}")
        
        print(f"\n[Pattern Detection]")
        print(f"  BC (Buying Climax): {'Detected' if bc_result.get('detected') else 'Not Detected'} ({bc_result.get('confidence', 0)}%)")
        print(f"  SC (Selling Climax): {'Detected' if sc_result.get('detected') else 'Not Detected'} ({sc_result.get('confidence', 0)}%)")
        print(f"  LPS (Last Point of Support): {'Detected' if lps_result.get('detected') else 'Not Detected'} ({lps_result.get('confidence', 0)}%)")
        print(f"  LPSY (Last Point of Supply): {'Detected' if lpsy_result.get('detected') else 'Not Detected'} ({lpsy_result.get('confidence', 0)}%)")
        
        print(f"\n[Enhanced WKF Judgment]")
        print(f"  Base Phase: {enhanced_judgment.get('base_phase', 'unknown')}")
        print(f"  Base Signal: {enhanced_judgment.get('base_signal', 'wait')}")
        print(f"  Base Confidence: {enhanced_judgment.get('base_confidence', 0)}%")
        print(f"  Enhanced Signal: {enhanced_judgment.get('enhanced_signal', 'wait')}")
        print(f"  Enhanced Confidence: {enhanced_judgment.get('enhanced_confidence', 0)}%")
        print(f"  Enhancement: {enhanced_judgment.get('enhancement_description', '无形态增强')}")
        
        print(f"\n[Recommendations]")
        print(f"  Trading Signal: {recommendations.get('trading_signal', 'wait')}")
        print(f"  Position Size: {recommendations.get('position_size', 0)}%")
        print(f"  Entry Zone: {recommendations.get('entry_zone', 'unknown')}")
        print(f"  Risk Level: {recommendations.get('risk_level', 'high')}")
        
        if recommendations.get('risk_warning'):
            print(f"  Risk Warnings:")
            for warning in recommendations.get('risk_warning', []):
                print(f"    - {warning}")
        
        if recommendations.get('action_plan'):
            print(f"  Action Plan:")
            for i, action in enumerate(recommendations.get('action_plan', []), 1):
                print(f"    {i}. {action}")
        
        print(f"\n{'='*80}")


def batch_analyze_all_periods():
    """Batch analyze all 5 periods"""
    
    # 5 images
    stock_images = [
        ("9c5927d6-a315-4f12-9768-a9a2941aacfc.jpg", "周线"),
        ("437746cd-65be-4603-938c-85debf232d94.jpg", "日线"),
        ("19397363-b6cd-4344-93cc-870d7d872a83.jpg", "1小时"),
        ("7ce8ed01-8ac5-45c4-945c-e3b82dda8fe2.jpg", "15分钟"),
        ("6f492e6b-7b20-4356-b939-5b17422dadf2.jpg", "5分钟")
    ]
    
    # Create analyzer
    analyzer = WKFCompleteAnalyzerV5()
    
    print("=" * 80)
    print("WKF Complete Analyzer V5")
    print("=" * 80)
    print("包含：SR线识别 + Y坐标价格映射 + 顶部形态（BC/SC）+ 底部形态（LPS/SC）+ WKF综合判断")
    print("=" * 80)
    
    all_results = []
    
    for i, (image_name, period) in enumerate(stock_images, 1):
        image_path = f"/root/.openclaw/media/inbound/{image_name}"
        
        if not os.path.exists(image_path):
            print(f"\n[{i}/{len(stock_images)}] Image not found: {image_name}")
            continue
        
        try:
            result = analyzer.analyze_image(image_path, period)
            
            if result['success']:
                all_results.append(result)
            else:
                print(f"\n[{i}/{len(stock_images)}] Analysis failed: {result.get('error', 'Unknown')}")
                
        except Exception as e:
            print(f"\n[{i}/{len(stock_images)}] Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Save results
    output_file = "/root/.openclaw/workspace/wkf_v5_complete_analysis_results.json"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)
        print(f"\n{'='*80}")
        print(f"Results saved to: {output_file}")
        print(f"{'='*80}")
    except Exception as e:
        print(f"\nError saving results: {e}")
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"Batch Analysis Summary")
    print(f"{'='*80}")
    
    print(f"\nTotal images analyzed: {len(all_results)}")
    
    # Count phases
    phase_count = {}
    signal_count = {}
    pattern_count = {}
    
    for result in all_results:
        period = result.get('period', 'unknown')
        enhanced_judgment = result.get('enhanced_judgment', {})
        
        phase = enhanced_judgment.get('enhanced_phase', 'unknown')
        phase_count[phase] = phase_count.get(phase, 0) + 1
        
        signal = enhanced_judgment.get('enhanced_signal', 'wait')
        signal_count[signal] = signal_count.get(signal, 0) + 1
        
        # Count patterns
        top_patterns = enhanced_judgment.get('top_patterns', {})
        bottom_patterns = enhanced_judgment.get('bottom_patterns', {})
        
        if top_patterns.get('bc', False):
            pattern_count['bc'] = pattern_count.get('bc', 0) + 1
        if top_patterns.get('lpsy', False):
            pattern_count['lpsy'] = pattern_count.get('lpsy', 0) + 1
        if bottom_patterns.get('sc', False):
            pattern_count['sc'] = pattern_count.get('sc', 0) + 1
        if bottom_patterns.get('lps', False):
            pattern_count['lps'] = pattern_count.get('lps', 0) + 1
    
    print(f"\nPhase Statistics:")
    for phase, count in sorted(phase_count.items(), key=lambda x: x[1], reverse=True):
        phase_cn = {
            'accumulation': '吸筹期',
            'markup': '拉升期',
            'distribution': '派发期',
            'oscillation': '震荡期',
            'unknown': '未知'
        }.get(phase, phase)
        print(f"  {phase_cn}: {count}张")
    
    print(f"\nSignal Statistics:")
    for signal, count in sorted(signal_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {signal}: {count}张")
    
    print(f"\nPattern Statistics:")
    for pattern, count in sorted(pattern_count.items(), key=lambda x: x[1], reverse=True):
        pattern_cn = {
            'bc': 'BC（购买高潮）',
            'sc': 'SC（卖出密集区）',
            'lps': 'LPS（最后的支撑点）',
            'lpsy': 'LPSY（最后的供应点）'
        }.get(pattern, pattern)
        print(f"  {pattern_cn}: {count}张")
    
    print(f"\n{'='*80}")


if __name__ == "__main__":
    batch_analyze_all_periods()
