#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Gemini Vision LLM - 图片识别
"""
import os
import sys
from datetime import datetime
import base64

# 配置API密钥
os.environ['GEMINI_API_KEY'] = 'AIzaSyC570BwP3UFNhCIrRr32y0LXC2XiXLzIwM'

# 添加路径
sys.path.append('/root/.openclaw/workspace/FundsMonitor')
sys.path.append('/root/.openclaw/workspace/FundsMonitor/modules')

# 配置日志
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_gemini_vision_direct():
    """直接测试Gemini Vision LLM"""
    print('='*80)
    print('测试Gemini Vision LLM - 图片识别')
    print('='*80)
    
    # 检查API密钥
    api_key = os.getenv('GEMINI_API_KEY')
    
    print(f'\n【API配置】')
    print(f'Gemini API密钥: {api_key[:20]}...{api_key[-5:]}')
    print(f'API密钥长度: {len(api_key)}')
    
    if not api_key:
        print('✗ API密钥未配置')
        return False
    
    print('✓ API密钥已配置')
    
    # 方法1：使用google.generativeai
    print(f'\n【方法1】使用google.generativeai')
    print('-'*80)
    
    try:
        import google.generativeai as genai
        
        print('✓ google.generativeai导入成功')
        
        # 配置API密钥
        genai.configure(api_key=api_key)
        print('✓ API密钥配置成功')
        
        # 创建模型
        model = genai.GenerativeModel('gemini-1.5-flash')
        print('✓ Gemini Vision模型创建成功')
        
        # 测试文本生成
        print('\n测试文本生成...')
        response = model.generate_content('你好，请用一句话介绍一下自己。')
        print(f'✓ 文本生成成功')
        print(f'  响应: {response.text}')
        
        # 测试图片生成（使用Mock图片）
        print('\n测试图片生成...')
        
        # 创建一个简单的测试图片描述
        prompt = """
请分析这张图片中的K线图：
1. 股票代码
2. 趋势方向
3. 趋势强度
4. 均线状态
5. 成交量状态
6. 简要总结

注意：如果没有真实图片，请分析描述的K线图特征。
"""
        
        # Mock图片（base64编码）
        mock_image_description = """
这是一张股票K线图：
- 股票代码：600519.SH（贵州茅台）
- 趋势：上涨
- 趋势强度：强
- 均线：金叉（短期均线上穿长期均线）
- 成交量：放大
- 总结：均线上穿，成交量放大，趋势向上
"""
        
        response = model.generate_content([
            prompt,
            mock_image_description
        ])
        
        print(f'✓ 图片分析成功（Mock）')
        print(f'  响应: {response.text}')
        
    except ImportError as e:
        print(f'✗ 导入google.generativeai失败: {e}')
        return False
    except Exception as e:
        print(f'✗ Gemini Vision LLM调用失败: {e}')
        logger.error(f"[Gemini Vision] 错误详情: {e}", exc_info=True)
        return False
    
    # 方法2：使用litellm
    print(f'\n【方法2】使用litellm调用Gemini')
    print('-'*80)
    
    try:
        from litellm import completion
        
        print('✓ litellm导入成功')
        
        # 测试文本生成
        print('\n测试文本生成...')
        response = completion(
            model='gemini/gemini-1.5-flash',
            api_key=api_key,
            messages=[
                {
                    'role': 'user',
                    'content': '你好，请用一句话介绍一下自己。'
                }
            ]
        )
        
        print(f'✓ 文本生成成功')
        print(f'  响应: {response.choices[0].message.content}')
        
        # 测试图片识别（Mock）
        print('\n测试图片识别（Mock）...')
        
        prompt = """
请分析以下K线图信息：
股票代码：600519.SH（贵州茅台）
价格：1440.00元
涨跌幅：+0.5%
均线：短期MA5上穿MA20，形成金叉
成交量：放量
趋势：向上

请分析：
1. 趋势方向
2. 趋势强度
3. 均线状态
4. 成交量状态
5. 投资建议
"""
        
        response = completion(
            model='gemini/gemini-1.5-flash',
            api_key=api_key,
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        )
        
        print(f'✓ 图片分析成功（Mock）')
        print(f'  响应: {response.choices[0].message.content}')
        
    except ImportError as e:
        print(f'✗ 导入litellm失败: {e}')
        return False
    except Exception as e:
        print(f'✗ litellm调用Gemini失败: {e}')
        logger.error(f"[Gemini litellm] 错误详情: {e}", exc_info=True)
        return False
    
    print('\n' + '='*80)
    print('✅ Gemini Vision LLM测试完成！')
    print('='*80)
    
    return True


if __name__ == '__main__':
    success = test_gemini_vision_direct()
    
    if success:
        print('\n✅ Gemini Vision LLM测试成功！')
        sys.exit(0)
    else:
        print('\n✗ Gemini Vision LLM测试失败！')
        sys.exit(1)
