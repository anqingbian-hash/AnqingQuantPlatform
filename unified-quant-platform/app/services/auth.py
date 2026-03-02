#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证服务 v2.0
支持密码哈希、JWT token、权限控制
"""

import datetime
import hashlib
import secrets
import jwt
from functools import wraps
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

class AuthService:
    """认证服务类"""

    def __init__(self, config=None):
        """
        初始化认证服务

        Args:
            config: 配置对象（可选）
        """
        self.config = config
        if config:
            self.jwt_config = config.get_jwt_config()
        else:
            # 默认配置
            self.jwt_config = {
                'secret_key': 'your-secret-key-change-in-production',
                'algorithm': 'HS256',
                'expiration_hours': 24
            }

    def register_user(self, username, email, password, role='user'):
        """
        注册新用户

        Args:
            username: 用户名
            email: 邮箱
            password: 密码
            role: 角色（默认为 user）

        Returns:
            注册结果
        """
        try:
            # 导入必要的模块
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

            from app import app

            # 检查用户名是否已存在
            existing_user = app.db.query('SELECT * FROM users WHERE username = ?', (username,))
            if existing_user:
                return {
                    'success': False,
                    'message': '用户名已存在'
                }

            # 检查邮箱是否已存在
            existing_email = app.db.query('SELECT * FROM users WHERE email = ?', (email,))
            if existing_email:
                return {
                    'success': False,
                    'message': '邮箱已被注册'
                }

            # 生成密码哈希
            password_hash = self.generate_password_hash(password)

            # 插入新用户
            app.db.execute(
                'INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)',
                (username, email, password_hash, role)
            )

            # 获取新用户ID
            user_id = app.db.lastrowid

            # 生成 token
            token = self.generate_token(user_id, username, role)

            return {
                'success': True,
                'message': '注册成功',
                'data': {
                    'token': token,
                    'user': {
                        'id': user_id,
                        'username': username,
                        'email': email,
                        'role': role
                    }
                }
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'注册失败: {str(e)}'
            }

    def authenticate_user(self, username, password):
        """
        验证用户登录

        Args:
            username: 用户名
            password: 密码

        Returns:
            认证结果
        """
        try:
            # 导入必要的模块
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

            from app import app

            # 查询用户
            users = app.db.query('SELECT * FROM users WHERE username = ?', (username,))

            if not users:
                return {
                    'success': False,
                    'message': '用户名或密码错误'
                }

            user = users[0]

            # 检查账户是否激活
            if not user[5]:  # is_active
                return {
                    'success': False,
                    'message': '账户已被禁用'
                }

            # 验证密码
            password_hash = user[3]  # password_hash
            is_valid = self.check_password(password_hash, password)

            if not is_valid:
                return {
                    'success': False,
                    'message': '用户名或密码错误'
                }

            # 更新最后登录时间和登录次数
            import datetime
            now = datetime.datetime.utcnow()
            login_count = user[8] + 1  # login_count
            app.db.execute(
                'UPDATE users SET last_login_at = ?, login_count = ? WHERE id = ?',
                (now, login_count, user[0])
            )

            # 生成 token
            token = self.generate_token(user[0], user[1], user[4])

            return {
                'success': True,
                'message': '登录成功',
                'data': {
                    'token': token,
                    'user': {
                        'id': user[0],
                        'username': user[1],
                        'email': user[2],
                        'role': user[4],
                        'is_active': user[5],
                        'created_at': user[6].isoformat() if user[6] else None,
                        'last_login_at': user[7].isoformat() if user[7] else None,
                        'login_count': login_count
                    }
                }
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'登录失败: {str(e)}'
            }

    def generate_password_hash(self, password):
        """
        生成密码哈希

        Args:
            password: 明文密码

        Returns:
            密码哈希
        """
        return generate_password_hash(password)

    def check_password(self, password_hash, password):
        """
        验证密码

        Args:
            password_hash: 密码哈希
            password: 明文密码

        Returns:
            是否匹配
        """
        return check_password_hash(password_hash, password)

    def generate_token(self, user_id, username, role):
        """
        生成 JWT token

        Args:
            user_id: 用户ID
            username: 用户名
            role: 用户角色

        Returns:
            JWT token
        """
        payload = {
            'user_id': user_id,
            'username': username,
            'role': role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=self.jwt_config['expiration_hours']),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, self.jwt_config['secret_key'], algorithm=self.jwt_config['algorithm'])
        return token

    def verify_token(self, token):
        """
        验证 JWT token

        Args:
            token: JWT token

        Returns:
            解码后的 payload，验证失败返回 None
        """
        try:
            payload = jwt.decode(token, self.jwt_config['secret_key'], algorithms=[self.jwt_config['algorithm']])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

def login_required(f):
    """
    登录验证装饰器

    Args:
        f: 被装饰的函数

    Returns:
        装饰后的函数
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 从请求头获取 token
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'success': False, 'message': '未提供认证令牌'}), 401

        # 移除 "Bearer " 前缀
        if token.startswith('Bearer '):
            token = token[7:]

        # 验证 token
        from app import app
        auth_service = AuthService(app.config['CONFIG'])

        payload = auth_service.verify_token(token)

        if not payload:
            return jsonify({'success': False, 'message': '认证令牌无效或已过期'}), 401

        # 将用户信息保存到 request 对象
        request.current_user = payload

        return f(*args, **kwargs)

    return decorated_function

def admin_required(f):
    """
    管理员权限验证装饰器

    Args:
        f: 被装饰的函数

    Returns:
        装饰后的函数
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 首先检查是否登录
        from flask import request
        if not hasattr(request, 'current_user'):
            return jsonify({'success': False, 'message': '需要登录'}), 401

        # 检查是否为管理员
        if request.current_user.get('role') != 'admin':
            return jsonify({'success': False, 'message': '需要管理员权限'}), 403

        return f(*args, **kwargs)

    return decorated_function

# 测试
if __name__ == "__main__":
    print("=" * 70)
    print("认证服务 v2.0 测试")
    print("=" * 70)

    # 创建模拟配置
    class MockConfig:
        def get_jwt_config(self):
            return {
                'secret_key': 'test-secret-key',
                'algorithm': 'HS256',
                'expiration_hours': 24
            }

    config = MockConfig()
    auth_service = AuthService(config)

    # 测试密码哈希
    password = "test_password"
    password_hash = auth_service.generate_password_hash(password)
    print(f"\n✅ 密码哈希: {password_hash[:50]}...")

    # 测试密码验证
    is_valid = auth_service.check_password(password_hash, password)
    print(f"✅ 密码验证: {is_valid}")

    # 测试 JWT token 生成
    token = auth_service.generate_token(1, "admin", "admin")
    print(f"✅ JWT Token: {token[:50]}...")

    # 测试 JWT token 验证
    payload = auth_service.verify_token(token)
    print(f"✅ Token 验证: {payload is not None}")
    if payload:
        print(f"  用户ID: {payload['user_id']}")
        print(f"  用户名: {payload['username']}")
        print(f"  角色: {payload['role']}")

    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)
