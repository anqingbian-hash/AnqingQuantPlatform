#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务器启动脚本 v2.0
最简化版本
"""

import os
import sys

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from flask import Flask

# 创建简化版应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'

@app.route('/')
def index():
    return jsonify({
        'message': 'OpenClaw 统一量化交易平台 v5.0',
        'version': '5.0.0',
        'environment': 'test',
        'status': 'running'
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy'
    })

def main():
    """主函数"""
    # 获取环境参数
    env = sys.argv[1] if len(sys.argv) > 1 else "test"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000

    print("=" * 70)
    print("OpenClaw 统一量化交易平台 v5.0")
    print("=" * 70)
    print(f"环境: {env}")
    print(f"端口: {port}")
    print(f"访问地址: http://localhost:{port}")
    print(f"健康检查: http://localhost:{port}/health")
    print("=" * 70)

    # 启动服务器
    try:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=True,
            use_reloader=False
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  服务器已停止")
        print("=" * 70)

if __name__ == "__main__":
    main()
