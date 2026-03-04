#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM模型配置 - 统一使用DeepSeek
"""
import os

# DeepSeek API配置
# 从环境变量获取，没有则使用默认值
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'sk-446299a62b7c414ba2af12873290a071')

# Gemini API配置（备用）
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

# OpenAI API配置（备用）
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# 模型选择
# 优先级：deepseek > gemini > openai > mock
MODEL_PREFERENCE = 'deepseek/deepseek-chat'

# LLM配置
LLM_CONFIG = {
    'model': MODEL_PREFERENCE,
    'api_key': DEEPSEEK_API_KEY,
    'temperature': 0.7,
    'max_tokens': 2000,
    'timeout': 30,
    'retry': 3
}

# 是否启用LLM
LLM_ENABLED = True if DEEPSEEK_API_KEY else False

# 是否在特定模块启用LLM
ENABLE_DECISION_MAKER = True
ENABLE_AI_BACKTESTER = True
ENABLE_MODEL_BUILDER = True
ENABLE_REPORTER = True

# 导出配置
__all__ = {
    'DEEPSEEK_API_KEY': DEEPSEEK_API_KEY,
    'GEMINI_API_KEY': GEMINI_API_KEY,
    'OPENAI_API_KEY': OPENAI_API_KEY,
    'MODEL_PREFERENCE': MODEL_PREFERENCE,
    'LLM_ENABLED': LLM_ENABLED,
    'ENABLE_DECISION_MAKER': ENABLE_DECISION_MAKER,
    'ENABLE_AI_BACKTESTER': ENABLE_AI_BACKTESTER,
    'ENABLE_MODEL_BUILDER': ENABLE_MODEL_BUILDER,
    'ENABLE_REPORTER': ENABLE_REPORTER,
    'LLM_CONFIG': LLM_CONFIG
}


def get_model():
    """获取LLM配置"""
    return LLM_CONFIG['model']


def get_api_key():
    """获取API密钥"""
    return LLM_CONFIG['api_key']


def is_llm_enabled():
    """检查LLM是否可用"""
    return LLM_ENABLED


def is_module_enabled(module_name: str) -> bool:
    """检查特定模块是否启用LLM"""
    modules = {
        'decision_maker': ENABLE_DECISION_MAKER,
        'ai_backtester': ENABLE_AI_BACKTESTER,
        'model_builder': ENABLE_MODEL_BUILDER,
        'reporter': ENABLE_REPORTER
    }
    return modules.get(module_name.lower(), False)


if __name__ == '__main__':
    print("=" * 70)
    print("LLM模型配置")
    print("=" * 70)

    print(f"\n模型: {get_model()}")
    print(f"API Key: {get_api_key()[:10]}...}")
    print(f"LLM启用: {is_llm_enabled()}")
    print(f"温度: {LLM_CONFIG['temperature']}")
    print(f"最大令牌数: {LLM_CONFIG['max_tokens']}")

    print(f"\n模块启用状态：")
    for module, enabled in modules.items():
        status = "✅" if enabled else "❌"
        print(f"  {status} {module}")

    print("\n" + "=" * 70)
