#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ai-memory 技能测试"""

import sys
import json

# 添加技能路径
skill_dir = "/root/.openclaw/skills/temp_ai_memory/01-长期记忆"
sys.path.insert(0, skill_dir)

try:
    # 执行技能代码
    with open(f"{skill_dir}/ai_memory.py", 'r', encoding='utf-8') as f:
        code = f.read()
    
    # 创建执行环境
    exec_globals = {
        '__name__': '__main__',
        '__file__': f"{skill_dir}/ai_memory.py"
    }
    exec(code, exec_globals)
    
    # 调用函数
    memory = exec_globals.get('AIMemory')
    if memory:
        m = memory()
        result = m.add('集成测试成功', tags=['test', 'integration'])
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"error": "AIMemory class not found"}, ensure_ascii=False, indent=2))
        
except Exception as e:
    print(json.dumps({"error": str(e)}, ensure_ascii=False, indent=2))
