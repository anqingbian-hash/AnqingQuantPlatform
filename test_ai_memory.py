#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ai-memory 技能测试脚本"""

import sys
import json

# 添加技能路径
skill_dir = "/root/.openclaw/skills/01-长期记忆---1bdd00e8-15ac-42f2-8aa2-014f776a8129"
sys.path.insert(0, skill_dir)

try:
    exec(open(f"{skill_dir}/ai_memory.py").read())
    
    # 获取实例
    memory = locals().get('AIMemory')
    if not memory:
        memory = locals().get('AIMemory')
    
    if not memory:
        # 尝试直接调用
        try:
            result = AIMemory().add('集成测试', tags=['测试', 'ai-memory'])
            print(f"✅ AIMemory.add() 成功")
            print(f"返回: {result}")
        except Exception as e:
            print(f"❌ AIMemory.add() 失败: {e}")
    else:
        # 使用实例
        try:
            m = memory()
            result = m.add('集成测试', tags=['测试', 'ai-memory'])
            print(f"✅ AI Memory 集成测试成功")
            print(f"结果: {result}")
        except Exception as e:
            print(f"❌ 测试失败: {e}")

except Exception as e:
    print(f"❌ 导入失败: {e}")
    print("尝试直接导入...")
    
    # 尝试直接导入
    try:
        from ai_memory import AIMemory
        m = AIMemory()
        result = m.add('测试内容', tags=['test', 'integration'])
        print(f"✅ 直接导入成功: {result}")
    except Exception as e2:
        print(f"❌ 直接导入也失败: {e2}")
