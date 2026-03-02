#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证路由
提供用户注册、登录、Token 相关的 API 接口
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from flask_httpauth import HTTPBasicAuth

auth_api = Blueprint('auth_api', __name__)

from app.services.auth import AuthService

# 初始化认证服务
auth_service = AuthService()

# HTTP 基本认证（用于 API）
basic_auth = HTTPBasicAuth()

@basic_auth.verify_password
def verify_password(username, password):
    """验证密码（简化版，用于测试）"""
    # 从数据库验证
    user = auth_service.authenticate_user(username, password)
    if user and user.get('success'):
        return username
    return None

@auth_api.route('/register', methods=['POST'])
def register():
    """用户注册接口"""
    try:
        data = request.get_json()

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not all([username, email, password]):
            return jsonify({
                'success': False,
                'message': '用户名、邮箱和密码不能为空'
            }), 400

        # 验证邮箱格式
        if '@' not in email or '.' not in email.split('@')[-1]:
            return jsonify({
                'success': False,
                'message': '邮箱格式不正确'
            }), 400

        # 注册用户
        result = auth_service.register_user(username, email, password)

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'注册失败: {str(e)}'
        }), 500

@auth_api.route('/login', methods=['POST'])
def login():
    """用户登录接口"""
    try:
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        if not all([username, password]):
            return jsonify({
                'success': False,
                'message': '用户名和密码不能为空'
            }), 400

        # 认证用户
        result = auth_service.authenticate_user(username, password)

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'登录失败: {str(e)}'
        }), 500

@auth_api.route('/me', methods=['GET'])
@login_required
def get_current_user_info():
    """获取当前用户信息"""
    return jsonify({
        'success': True,
        'data': current_user.to_dict()
    })

@auth_api.route('/token/refresh', methods=['POST'])
@login_required
def refresh_token():
    """刷新 Token"""
    # 刷新当前用户的 Token
    token = auth_service.generate_token(current_user.id, current_user.role)

    return jsonify({
        'success': True,
        'data': {
            'token': token,
            'user': current_user.to_dict()
        }
    })
