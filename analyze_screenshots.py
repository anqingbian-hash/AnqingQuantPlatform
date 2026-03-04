#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用Gemini Vision LLM分析文华财经截图
提取S2、R2、NetVolume、DeltaBar等指标
"""

import os
import json
import base64
from PIL import Image

try:
    from google.generativeai import configure, GenerativeModel
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("⚠️ google.generativeai 不可用")

class ScreenshotAnalyzer:
    """截图分析器"""

    def __init__(self, api_key=None):
        """初始化分析器"""
        self.api_key = api_key or 'AIzaSyC570BwP3UFNhCI5p6hTg-8YKZ7pQhQ9XU'
        self.model = None

        if GENAI_AVAILABLE:
            try:
                configure(api_key=self.api_key)
                self.model = GenerativeModel('gemini-1.5-flash')
                print("✅ Gemini模型初始化成功")
            except Exception as e:
                print(f"⚠️ Gemini初始化失败: {e}")
                self.model = None

    def encode_image(self, image_path):
        """编码图片为base64"""
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    def analyze_image(self, image_path, period_name):
        """分析单张图片"""
        if not self.model:
            return {
                'error': 'Gemini模型不可用',
                'period': period_name,
                'image_path': image_path
            }

        print(f"\n📊 分析 {period_name}: {os.path.basename(image_path)}")

        # 编码图片
        try:
            image_base64 = self.encode_image(image_path)
        except Exception as e:
            return {
                'error': f'图片编码失败: {e}',
                'period': period_name,
                'image_path': image_path
            }

        # 构建提示词
        prompt = '''
请仔细分析这张文华财经筹码对冲系统的截图，提取以下关键指标：

## 第一部分：主图信息（价格走势）
1. **股票代码和名称**：截图左上角或标题栏显示的股票代码（如3000766）和股票名称（如每日互动）
2. **当前价格**：截图右上角或价格栏显示的现价（最新成交价）
3. **S2支撑位**：主图中绿色虚线显示的支撑位数值（如果有）
4. **R2阻力位**：主图中红色虚线显示的阻力位数值（如果有）
5. **K线形态**：
   - 是否站稳S2？（是/否）
   - 是否突破R2？（是/否）
   - 是否跌破S2？（是/否）
   - 高点是否持续抬升？（是/否）
   - 箱体振幅大小？（百分比）

## 第二部分：副图1 - NetVolume（净量能）
6. **净量数值**：副图1中显示的数字（正数=净多，负数=净空）
7. **净量状态**：
   - 净多稳定？（是/否）
   - 净多萎缩？（是/否）
   - 净空主导？（是/否）
   - 净空爆发？（是/否）
   - 净多环比增长率？（百分比）

## 第三部分：副图2 - DeltaBar（动能柱）
8. **Delta状态**：
   - 斜率方向？（向上/向下/水平）
   - 是否持续正值？（是/否）
   - 是否存在顶背离？（是/否）
   - 是否存在底背离？（是/否）

## 第四部分：其他标识
9. **关键标注**：主图中是否有LPS、LPSY、BC、SC等标注？（有/无，具体是什么）
10. **时间周期**：截图是什么周期的？（周线/日线/1小时/15分钟/5分钟）

请以JSON格式返回，格式如下：
{
  "period": "周期名称（如：日线）",
  "stock_code": "股票代码",
  "stock_name": "股票名称",
  "current_price": 现价数值,
  "price_structure": {
    "s2_support": S2支撑位数值或null,
    "r2_resistance": R2阻力位数值或null,
    "s2_stable": 是否站稳S2（true/false）,
    "r2_broken": 是否突破R2（true/false）,
    "s2_broken": 是否跌破S2（true/false）,
    "highs_rising": 高点是否持续抬升（true/false）,
    "box_range_pct": 箱体振幅百分比或null,
    "pullback_not_broken": 回踩不破（true/false）,
    "box_breakout_pct": 突破箱体百分比或null,
    "range_expanding": 振幅扩大（true/false）
  },
  "net_volume": {
    "current_value": 净量当前数值或null,
    "is_positive": 是否为正值（true/false）,
    "net_long_stable": 净多稳定（true/false）,
    "net_long_shrinking": 净多萎缩（true/false）,
    "net_short_dominant": 净空主导（true/false）,
    "net_short_explosion": 净空爆发（true/false）,
    "net_long_growth_pct": 净多环比增长百分比或null,
    "net_short_growth_pct": 净空增幅百分比或null
  },
  "delta_bar": {
    "slope": "斜率方向（up/down/flat）",
    "is_positive": 是否持续正值（true/false）,
    "divergence_top": 是否存在顶背离（true/false）,
    "divergence_bottom": 是否存在底背离（true/false）,
    "effort_no_result": 努力没结果（true/false）
  },
  "key_markers": ["标注列表"],
  "confidence": "置信度（高/中/低）"
}

只返回JSON，不要其他文字。如果某个指标无法识别，请使用null。
'''

        try:
            # 调用Gemini API
            response = self.model.generate_content([
                prompt,
                {'mime_type': 'image/jpeg', 'data': image_base64}
            ])

            # 解析响应
            result_text = response.text.strip()

            # 提取JSON
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()

            result = json.loads(result_text)
            result['period'] = period_name
            result['image_path'] = image_path

            print(f"  ✅ 分析成功")
            print(f"  - 股票代码: {result.get('stock_code', 'N/A')}")
            print(f"  - 当前价格: {result.get('current_price', 'N/A')}")
            print(f"  - S2: {result.get('price_structure', {}).get('s2_support', 'N/A')}")
            print(f"  - R2: {result.get('price_structure', {}).get('r2_resistance', 'N/A')}")
            print(f"  - 净量: {result.get('net_volume', {}).get('current_value', 'N/A')}")
            print(f"  - Delta斜率: {result.get('delta_bar', {}).get('slope', 'N/A')}")

            return result

        except json.JSONDecodeError as e:
            print(f"  ❌ JSON解析失败: {e}")
            print(f"  原始响应: {result_text[:500]}")
            return {
                'error': f'JSON解析失败: {e}',
                'raw_response': result_text[:1000],
                'period': period_name,
                'image_path': image_path
            }
        except Exception as e:
            print(f"  ❌ 分析失败: {e}")
            return {
                'error': str(e),
                'period': period_name,
                'image_path': image_path
            }

    def analyze_all(self, image_paths, period_names):
        """分析所有图片"""
        results = {}

        for image_path, period_name in zip(image_paths, period_names):
            result = self.analyze_image(image_path, period_name)
            results[period_name] = result

        return results


def main():
    """主函数"""
    # 图片列表
    images = [
        '/root/.openclaw/media/inbound/d26b567e-5226-4f77-8f21-6a4efb71f821.jpg',  # 周线
        '/root/.openclaw/media/inbound/36f9f23a-a21a-4d8f-afc2-64767a132d36.jpg',  # 日线
        '/root/.openclaw/media/inbound/dc663f79-16cf-4be9-a98f-5866150f8076.jpg',  # 1小时
        '/root/.openclaw/media/inbound/0bbb9ba2-cc9a-490e-9232-1d94ec9c2e54.jpg',  # 15分钟
        '/root/.openclaw/media/inbound/b173264f-fd2a-46eb-accd-215776d44527.jpg',  # 5分钟
        '/root/.openclaw/media/inbound/ecf6f1ef-2167-48e2-89ed-8bf0d7e72264.jpg',  # 额外1
        '/root/.openclaw/media/inbound/f77ac0f4-bc1f-4306-91dd-56d3a6e7f4f4.jpg'   # 额外2
    ]

    # 周期名称
    period_names = ['周线', '日线', '1小时', '15分钟', '5分钟', '额外1', '额外2']

    # 创建分析器
    analyzer = ScreenshotAnalyzer()

    # 分析所有图片
    print("=" * 70)
    print("开始分析文华财经截图")
    print("=" * 70)

    results = analyzer.analyze_all(images, period_names)

    # 保存结果
    output_file = '/root/.openclaw/workspace/analysis_results/screenshot_analysis.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print(f"✅ 分析完成，结果已保存到: {output_file}")
    print("=" * 70)

    return results


if __name__ == '__main__':
    main()
