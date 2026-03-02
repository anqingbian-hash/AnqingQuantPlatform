#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最简化的启动脚本
绕过缓存问题，直接运行应用
"""

import sys
import os

# 确保使用正确的 Python 路径
if len(sys.argv) > 1:
    project_root = sys.argv[1]
else:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print(f"项目根目录: {project_root}")

# 添加项目根目录到 Python 路径
sys.path.insert(0, project_root)

# 导入应用
try:
    from app import create_app
    app = create_app('test')

    # 简单的测试路由
    @app.route('/')
    def index():
        return {
            'success': True,
            'message': '统一量化交易平台测试环境运行正常',
            'timestamp': '2026-03-01 17:10'
        }

    @app.route('/api/test')
    def api_test():
        return jsonify({
            'success': True,
            'message': 'API 测试接口正常',
            'data': {
                'service': '统一量化交易平台',
                'version': 'v5.0 Dual-Env',
                'environment': 'test',
                'auth_enabled': False
            }
        })

    print("\n🚀 启动服务...")
    print("访问地址: http://localhost:5000")
    print("测试接口: http://localhost:5000/api/test")
    print("按 Ctrl+C 停止\n")

    # 启动服务
    from werkzeug.serving import run_simple
    run_simple(
        hostname='0.0.0.0',
        port=5000,
        application=app,
        use_reloader=True,
        use_debugger=True
    )

except Exception as e:
    print(f"\n❌ 启动失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
