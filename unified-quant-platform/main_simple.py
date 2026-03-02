#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一量化交易平台主入口（简化版）
支持双环境（测试/正式）
"""

import os
import sys
import argparse

def main(env: str = "test"):
    """
    主函数

    Args:
        env: 环境名称（test/prod）
    """
    print("=" * 70)
    print(f"🚀 启动统一量化交易平台 - {env.upper()} 环境")
    print("=" * 70)

    # 打印配置信息
    print(f"\n📄 环境配置:")
    print(f"  环境: {env}")
    print(f"  数据库: SQLite (测试环境)")
    print(f"  日志路径: logs/test.log")

    # 简单的 HTTP 服务器测试
    try:
        from http.server import HTTPServer, SimpleHTTPRequestHandler

        class TestHandler(SimpleHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write("OK - 服务正常运行")

        print(f"\n🌐 启动服务...")
        server = HTTPServer(('localhost', 5000), TestHandler)
        print(f"  访问地址: http://localhost:5000")
        print("=" * 70)
        print("服务已启动，按 Ctrl+C 停止")
        print("=" * 70)

        server.serve_forever()

    except Exception as e:
        print(f"\n❌ 服务启动失败: {e}")
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
