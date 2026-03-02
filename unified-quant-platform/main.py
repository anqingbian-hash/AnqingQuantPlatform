#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一量化交易平台主入口
支持双环境（测试/正式）
"""

import os
import sys
import argparse

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import get_config

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
    config = get_config(env)

    # 打印配置信息
    print(f"\n📄 环境配置:")
    print(f"  环境: {config.env}")
    print(f"  数据库: {config.get_database_name()}")
    print(f"  缓存目录: {config.get_cache_dir()}")
    print(f"  日志目录: {config.get_log_dir()}")
    print(f"  临时目录: {config.get_temp_dir()}")
    print(f"  调试模式: {config.get_debug_mode()}")

    # 打印服务信息
    print(f"\n🌐 服务配置:")
    api_config = config.get('api', {})
    print(f"  主机: {api_config.get('host', '0.0.0.0')}")
    print(f"  端口: {api_config.get('port', 5000)}")
    print(f"  调试: {api_config.get('debug', False)}")

    # 检查数据库连接
    print(f"\n🗄 数据库连接:")
    try:
        print(f"  连接串: {config.get_database_url()}")
        print(f"  ✅ 数据库配置正常")
    except Exception as e:
        print(f"  ❌ 数据库配置错误: {e}")
        return

    # 检查数据目录
    print(f"\n📁 数据目录检查:")
    dirs_to_check = [
        ("缓存目录", config.get_cache_dir()),
        ("日志目录", config.get_log_dir()),
        ("临时目录", config.get_temp_dir())
    ]

    for name, dir_path in dirs_to_check:
        if os.path.exists(dir_path):
            print(f"  ✅ {name}: {dir_path}")
        else:
            print(f"  ⚠️ {name}: {dir_path} (不存在)")

    # 创建缺失的目录
    print(f"\n🔧 创建缺失的目录...")
    for name, dir_path in dirs_to_check:
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
                print(f"  ✅ 已创建: {name}")
            except Exception as e:
                print(f"  ❌ 创建失败: {name}, {e}")

    # 初始化应用
    print(f"\n⚙️ 初始化应用...")
    try:
        from app import create_app
        app = create_app(env)

        print(f"  ✅ 应用�成功")

        # 启动服务
        host = api_config.get('host', '0.0.0.0')
        port = api_config.get('port', 5000)
        debug = config.get_debug_mode()

        print(f"\n🎯 启动服务...")
        print(f"  访问地址: http://{host}:{port}")
        print(f"  调试模式: {debug}")
        print("=" * 70)

        # 启动 Flask 应用
        if __name__ == '__main__':
            from werkzeug.serving import run_simple
            run_simple(
                hostname=host,
                port=port,
                application=app,
                use_reloader=debug,
                use_debugger=debug
            )

    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == '__main__':
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='统一量化交易平台')
    parser.add_argument(
        '--env',
        choices=['test', 'prod'],
        default='test',
        help='运行环境（test/prod）'
    )

    args = parser.parse_args()

    # 启动应用
    main(env=args.env)
