#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一量化交易平台主入口 v2
支持双环境、用户认证、JWT Token
"""

import os
import sys
import argparse

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def main(env: str = "test"):
    """
    主函数

    Args:
        env: 环境名称（test/prod）
    """
    print("=" * 70)
    print(f"🚀 启动统一量化交易平台 - {env.upper()} 环境")
    print("=" * 70)

    # 加载配置
    print(f"\n📄 环境配置:")
    print(f"  环境: {env}")
    print(f"  数据库: SQLite")
    print(f"  日志: logs/{env}.log")

    # 打印服务信息
    print(f"\n🌐 服务信息:")
    print(f"  访问地址: http://localhost:5000")
    print(f"  测试接口: http://localhost:5000/api/test")
    print(f"  注册接口: http://localhost:5000/auth/register")
    print(f"  登录接口: http://localhost:5000/auth/login")
    print("=" * 70)

    try:
        # 创建应用
        app = create_app(env)

        # 启动服务
        print("\n▶️ 启动服务...")
        print("服务地址: http://localhost:5000")
        print("按 Ctrl+C 停止")
        print("=" * 70)

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
        return

if __name__ == '__main__':
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='统一量化交易平台 v2')
    parser.add_argument(
        '--env',
        choices=['test', 'prod'],
        default='test',
        help='运行环境（test/prod）'
    )

    args = parser.parse_args()

    # 启动应用
    main(env=args.env)
