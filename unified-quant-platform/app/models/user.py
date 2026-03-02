#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证模型
用户认证相关的数据模型
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class UserMixin:
    """User Mixin 类"""
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

class User(UserMixin):
    """用户模型"""

    def __init__(self, db):
        self.db = db
        self.__table__ = db.Table('users', db.metadata,
            db.Column('id', db.Integer, primary_key=True),
            db.Column('username', db.String(50), unique=True, nullable=False, index=True),
            db.Column('email', db.String(100), unique=True, nullable=False, index=True),
            db.Column('password_hash', db.String(255), nullable=False),
            db.Column('role', db.String(20), nullable=False, default='user'),
            db.Column('is_active', db.Boolean, default=True, nullable=False),
            db.Column('created_at', db.DateTime, default=datetime.utcnow, nullable=False),
            db.Column('updated_at', db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False),
            db.Column('last_login_at', db.DateTime),
            db.Column('login_count', db.Integer, default=0, nullable=False)
        )

    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'login_count': self.login_count
        }

    def __repr__(self):
        return f'<User {self.username}>'

class UserRole:
    """用户角色"""
    ADMIN = 'admin'
    USER = 'user'
    GUEST = 'guest'
