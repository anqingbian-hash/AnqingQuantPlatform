#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理器
支持双环境配置
"""

import os
import yaml
from typing import Dict, Any

class ConfigManager:
    """配置管理器"""

    def __init__(self, env: str = "test"):
        """
        初始化配置管理器

        Args:
            env: 环境名称（test/prod）
        """
        self.env = env
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        config_file = f"config/config_{self.env}.yaml"

        if not os.path.exists(config_file):
            raise FileNotFoundError(f"配置文件不存在: {config_file}")

        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self.config

    def get_database_url(self) -> str:
        """获取数据库连接字符串"""
        db_type = self.get('database.type', 'sqlite')

        if db_type == 'sqlite':
            db_path = self.get('database.sqlite.path', 'data/test/quant_test.db')
            return f"sqlite:///{db_path}"
        elif db_type == 'mysql':
            host = self.get('database.mysql.host', 'localhost')
            port = self.get('database.mysql.port', 3306)
            user = self.get('database.mysql.user', 'root')
            password = self.get('database.mysql.password', '')
            database = self.get('database.mysql.database', 'quant_test')
            return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
        else:
            raise ValueError(f"不支持的数据库类型: {db_type}")

    def get_secret_key(self) -> str:
        """获取密钥"""
        return self.get('security.secret_key', 'dev-secret-key')

    def get_jwt_config(self) -> Dict[str, Any]:
        """获取 JWT 配置"""
        return {
            'secret_key': self.get('security.jwt.secret_key', self.get_secret_key()),
            'algorithm': self.get('security.jwt.algorithm', 'HS256'),
            'expiration_hours': self.get('security.jwt.expiration_hours', 24)
        }

    def get_cors_config(self) -> Dict[str, Any]:
        """获取 CORS 配置"""
        return {
            'enabled': self.get('cors.enabled', True),
            'origins': self.get('cors.origins', ['*'])
        }

    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return {
            'level': self.get('logging.level', 'INFO'),
            'file': self.get('logging.file', f"logs/{self.env}.log")
        }

# 全局配置管理器实例
_config_managers = {}

def get_config(env: str = "test") -> ConfigManager:
    """
    获取配置管理器实例（单例模式）

    Args:
        env: 环境名称（test/prod）

    Returns:
        配置管理器实例
    """
    if env not in _config_managers:
        _config_managers[env] = ConfigManager(env)
    return _config_managers[env]

def get_test_config() -> ConfigManager:
    """获取测试环境配置"""
    return get_config('test')

def get_prod_config() -> ConfigManager:
    """获取生产环境配置"""
    return get_config('prod')

if __name__ == "__main__":
    # 测试
    print("=" * 70)
    print("配置管理器测试")
    print("=" * 70)

    # 测试环境配置
    print("\n测试环境配置:")
    test_config = get_test_config()
    print(f"  环境: {test_config.env}")
    print(f"  数据库类型: {test_config.get('database.type')}")
    print(f"  数据库连接: {test_config.get_database_url()}")
    print(f"  密钥: {test_config.get_secret_key()[:10]}...")

    # JWT 配置
    jwt_config = test_config.get_jwt_config()
    print(f"  JWT 算法: {jwt_config['algorithm']}")
    print(f"  JWT 过期时间: {jwt_config['expiration_hours']} 小时")

    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)
