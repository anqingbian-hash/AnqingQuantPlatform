#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 统一量化交易平台 v5.0 - 简化版应用
只保留基础功能
"""

import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from flask import Flask, jsonify, request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'

# 简单的用户数据库（内存存储）
users_db = {
    'admin': {
        'username': 'admin',
        'password': 'admin123',
        'email': 'admin@ntdf.com',
        'role': 'admin'
    }
}

@app.route('/')
def index():
    return jsonify({
        'message': 'OpenClaw 统一量化交易平台 v5.0',
        'version': '5.0.0',
        'status': 'running',
        'timestamp': '2026-03-01T12:35:00'
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy'
    })

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '缺少请求数据'}), 400

    username = data.get('username')
    password = data.get('password')

    # 简化版验证
    if username in users_db and users_db[username]['password'] == password:
        return jsonify({
            'success': True,
            'message': '登录成功',
            'user': {
                'username': username,
                'email': users_db[username]['email'],
                'role': users_db[username]['role']
            }
        })
    else:
        return jsonify({
            'success': False,
            'message': '用户名或密码错误'
        }), 401

if __name__ == "__main__":
    print("=" * 70)
    print("OpenClaw 统一量化交易平台 v5.0 - 简化版")
    print("=" * 70)
    print("✅ 应用创建成功")
    print("\n🌐 测试环境启动")
    print("=" * 70)
    print("访问地址: http://localhost:6000")
    print("默认账户: admin / admin123")
    print("健康检查: http://localhost:6000/health")
    print("=" * 70)
