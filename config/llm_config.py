#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LLM模型配置"""
import os

# DeepSeek API
os.environ['DEEPSEEK_API_KEY'] = 'sk-446299a62b7c414ba2af12873290a071'
os.environ['TUSHARE_TOKEN'] = '8b159caa2bbf554707c20c3f44fea1e0e6ec75bafc82c78fa47e47b'

# Gemini API（备用）
os.environ['GEMINI_API_KEY'] = ''

# OpenAI API（备用）
os.environ['OPENAI_API_KEY'] = ''

# 模型配置
# DeepSeek Chat（推荐，性价比最高）
# DeepSeek Coder（编程任务）
# Gemini Pro（多模态，但费用高）
# GPT-4（通用，但费用高）

# 温度配置
# DeepSeek: 0.7（创意和准确性的平衡）
# Gemini: 0.7（创意性）
# GPT-4: 0.7-1.0（创意性更高）

# 最大Token数
# DeepSeek: 8K-32K（推荐：4K-8K）
# Gemini: 128K（多模态）
# GPT-4: 8K（推荐）

# 预算Token估计（按DeepSeek价格）
# DeepSeek: ¥1/M input + ¥0.5/M output
# 5000积分 ≈ 2.5M input可输出 ≈ 5M output
# 深天5000积分，够用

def get_model_info():
    """获取模型信息"""
    model = os.getenv('MODEL', 'deepseek/deepseek-chat')

    if 'deepseek' in model.lower():
        return {
            'name': 'DeepSeek Chat',
            'provider': 'DeepSeek',
            'model': 'deepseek/deepseek-chat',
            'api': 'deepseek',
            'api_key': 'sk-446299a62b7c414ba2af12873290a071',
            'temperature': 0.7,
            'max_tokens': 4000,  # 4K tokens
            'pricing': '¥1/M input + ¥0.5/M output',
            'tokens_per_day': 20000, 5000积分 ≈ 10000 tokens/day
            'strengths': '代码任务、中文理解、性价比最高',
            'weaknesses': '实时性一般、上下文较短'
        }
    elif 'gemini' in model.lower():
        return {
            'name': 'Gemini Pro',
            'provider': 'Google',
            'model': 'gemini-pro',
            'api': 'gemini-pro',
            'api_key': os.getenv('GEMINI_API_KEY', ''),
            'temperature': 0.7,
            'max_tokens': 128000,  # 128K tokens
            'pricing': '免费（已付费5000积分）',
            'tokens_per_day': 'unlimited',
            'strengths': '多模态、数学推理、代码理解',
            'weaknesses': '中文较弱、价格昂贵'
        }
    elif 'gpt' in model.lower():
        return {
            'name': 'GPT-4',
            'provider': 'OpenAI',
            'model': 'gpt-4-turbo',
            'api': 'openai',
            'api_key': os.getenv('OPENAI_API_KEY', ''),
            'temperature': 0.7,
            'max_tokens': 8000,  # 8K tokens
            'pricing': '¥0.003/1K input tokens',
            'tokens_per_day': 'unlimited',
            'strengths': '通用性强、中文好',
            'weaknesses': '中文理解仍有限'
        }
    else:
        return {
            'name': 'DeepSeek Chat (默认）',
            'provider': 'DeepSeek',
            'model': 'deepseek/deepseek-chat',
            'api': 'deepseek',
            'api_key': 'sk-446299a62b7c414ba2af12873290a071',
            'temperature': 0.7,
            'max_tokens': 4000,
            'pricing': '¥1/M input + ¥0.5/M output'
        }


def get_recommended_model():
    """获取推荐模型"""
    return 'deepseek/deepseek-chat'


def get_temperature(model: str = None) -> float:
    """获取模型温度"""
    if model is None:
        model = get_recommended_model()

    model = model.lower()
    if 'gemini' in model:
        return 0.9  # Gemini需要更高的温度
    elif 'gpt' in model:
        return 0.7
    elif 'deepseek' in model:
        return 0.7
    else:
        return 0.7


def get_max_tokens(model: str = None) -> int:
    """获取最大Token数"""
    if model is None:
        model = get_recommended_model()

    model = model.lower()
    if 'deepseek' in model:
        return 4000
    elif 'gemini' in model:
        return 128000
    elif 'gpt' in model:
        return 8000
    else:
        return 4000


def get_temperature_for_task(task_type: str, model: str = None) -> float:
    """
    根据任务类型推荐温度

    参数:
        task_type: 任务类型
        model: 模型名称

    返回:
        float: 温度
    """
    if model is None:
        model = get_recommended_model()

    model = model.lower()

    # 任务类型推荐温度
    temps = {
        # 代码/编程: 更高的温度更有创意
        'coding': 0.85,   # deepseek-chat
        'math': 0.7,      # deepseek-coder
        'writing': 0.8,     # deepseek-v3
        'reasoning': 0.7, # gemini-pro
        'creative': 0.9,    # gemini-1.5-pro
        'analysis': 0.3,     # gpt-4-turbo
        'general': 0.7,    # deepseek-chat
    }

    return temps.get(task_type, 0.7)
