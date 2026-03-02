#!/usr/bin/env python3
"""
NTDF 项目启动脚本
启动后端服务器、安装依赖
"""

import os
import subprocess
import sys

def main():
    print("=== NTDF 项目启动 ===")
    print("")
    
    # 1. 激活虚拟环境
    print("1. 激活Python虚拟环境...")
    venv_path = "/var/www/ntdf/backend/venv"
    if os.path.exists(venv_path):
        print(f"   虚拟环境已存在: {venv_path}")
    else:
        print(f"   创建虚拟环境...")
        subprocess.run(["python3", "-m", "venv", venv_path])
    
    print("")
    
    # 2. 安装/更新依赖
    print("2. 安装/更新Python依赖...")
    subprocess.run([
        "source", venv_path + "/bin/activate",
        "&&",
        "pip", "install", "--upgrade", "pip",
        "&&",
        "pip", "install", "fastapi", "uvicorn[standard]", 
        "sqlalchemy", "psycopg2-binary", "pandas", "numpy",
        "requests", "yfinance"
    ], shell=True)
    
    print("")
    
    # 3. 启动后端服务
    print("3. 启动后端服务...")
    print(f"   服务地址: http://122.51.142.248:8000")
    print(f"   API文档: http://122.51.142.248:8000/docs")
    print(f"   健康检查: http://122.51.142.248:8000/api/health")
    print("")
    print("=== 服务启动完成 ===")
    print("")
    print("后端服务正在运行...")
    print("使用 Ctrl+C 停止服务")
    print("")
    
    # 启动服务
    activate_cmd = f"source {venv_path}/bin/activate && cd /var/www/ntdf/backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
    subprocess.run(activate_cmd, shell=True)

if __name__ == "__main__":
    main()
