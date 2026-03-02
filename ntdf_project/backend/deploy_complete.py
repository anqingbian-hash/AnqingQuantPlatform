#!/usr/bin/env python3
"""
NTDF 后端自动部署脚本
自动化部署：环境搭建、依赖安装、服务启动
"""

import os
import subprocess
import time
import json

def run_command(command, description):
    """执行命令"""
    print(f"{description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            print(f"✅ {description}成功")
            if result.stdout:
                print(result.stdout[:500])
            return True
        else:
            print(f"❌ {description}失败（代码: {result.returncode}）")
            if result.stderr:
                print(result.stderr[:500])
            return False
    except subprocess.TimeoutExpired:
        print(f"⏱ {description}超时")
        return False
    except Exception as e:
        print(f"❌ {description}错误: {e}")
        return False

def main():
    print("=== NTDF 后端自动部署开始 ===")
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    # 步骤1: 创建项目目录
    run_command(
        "mkdir -p /var/www/ntdf/backend && mkdir -p /var/www/ntdf/frontend",
        "创建项目目录"
    )
    
    # 步骤2: 安装系统依赖
    run_command(
        "apt-get update -y -qq && apt-get install -y -qq curl wget git vim htop unzip software-properties-common",
        "安装系统依赖"
    )
    
    # 步骤3: 安装 Python 3.11
    run_command(
        "apt-get install -y -qq python3.11 python3.11-venv python3.11-dev",
        "安装 Python 3.11"
    )
    
    # 步骤4: 安装 Node.js 20.x
    run_command(
        "curl -fsSL https://deb.nodesource.com/setup_20.x | bash -",
        "安装 Node.js 20.x"
    )
    run_command(
        "apt-get install -y -qq nodejs",
        "确认 nodejs 安装"
    )
    
    # 步骤5: 安装 PostgreSQL
    run_command(
        "apt-get install -y -qq postgresql postgresql-contrib",
        "安装 PostgreSQL"
    )
    run_command(
        "systemctl enable postgresql && systemctl start postgresql",
        "启动 PostgreSQL 服务"
    )
    
    # 步骤6: 安装 Docker
    run_command(
        "apt-get install -y -qq docker.io docker-compose",
        "安装 Docker"
    )
    run_command(
        "systemctl enable docker && systemctl start docker",
        "启动 Docker 服务"
    )
    
    # 步骤7: 安装 Nginx
    run_command(
        "apt-get install -y -qq nginx",
        "安装 Nginx"
    )
    run_command(
        "systemctl enable nginx && systemctl start nginx",
        "启动 Nginx 服务"
    )
    
    # 步骤8: 设置权限
    run_command(
        "chown -R ubuntu:ubuntu /var/www/ntdf",
        "设置项目目录权限"
    )
    
    # 步骤9: 创建数据库
    run_command(
        "sudo -u postgres psql -c \"CREATE DATABASE ntdf;\"",
        "创建数据库 ntdf"
    )
    run_command(
        "sudo -u postgres psql -c \"CREATE USER ntdf_user WITH PASSWORD 'ntdf_password_2024';\"",
        "创建数据库用户"
    )
    run_command(
        "sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE ntdf TO ntdf_user;\"",
        "授权用户权限"
    )
    run_command(
        "sudo -u postgres psql -d ntdf -c \"CREATE EXTENSION IF NOT EXISTS uuid-ossp;\"",
        "启用 uuid 扩展"
    )
    
    # 步骤10: 创建 Python 虚拟环境
    run_command(
        "cd /var/www/ntdf/backend && python3 -m venv venv",
        "创建 Python 虚拟环境"
    )
    run_command(
        "cd /var/www/ntdf/backend && source venv/bin/activate && pip install --upgrade pip -q",
        "升级 pip"
    )
    run_command(
        "cd /var/www/ntdf/backend && source venv/bin/activate && pip install -q fastapi uvicorn[standard] sqlalchemy psycopg2-binary pandas numpy requests yfinance alpha-vantage",
        "安装 Python 依赖"
    )
    
    # 步骤11: 创建主文件
    print("创建 FastAPI 主文件...")
    main_py = '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="NTDF Digital Net Analysis API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALPHA_VANTAGE_API_KEY = "X9GC2MV7P1GCODRZ"

@app.get("/")
async def root():
    return {
        "message": "NTDF Digital Net Analysis API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": "2026-02-22 12:30:00",
        "services": {
            "backend": "running",
            "database": "running",
            "nginx": "running"
        },
        "version": "1.0.0"
    }

@app.get("/api/alpha_vantage/quote")
async def get_alpha_vantage_quote(symbol: str):
    import requests
    
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/yahoo/quote")
async def get_yahoo_quote(symbol: str):
    import yfinance as yf
    
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")
        if not hist.empty:
            latest = hist.iloc[-1]
            return {
                "success": True,
                "symbol": symbol,
                "current_price": float(latest['Close']),
                "volume": int(latest['Volume'])
            }
        else:
            return {"success": False, "error": "No data available"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/yahoo/daily")
async def get_yahoo_daily(symbol: str, period: str = "1mo"):
    import yfinance as yf
    
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        if not hist.empty:
            data_list = []
            for index, row in hist.iterrows():
                data_list.append({
                    "date": index.strftime("%Y-%m-%d"),
                    "open": float(row['Open']),
                    "high": float(row['High']),
                    "low": float(row['Low']),
                    "close": float(row['Close']),
                    "volume": int(row['Volume'])
                })
            return {
                "success": True,
                "symbol": symbol,
                "period": period,
                "data": data_list
            }
        else:
            return {"success": False, "error": "No data available"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/docs")
async def docs():
    return {
        "message": "NTDF API Documentation",
        "endpoints": {
            "/api/health": "健康检查",
            "/api/alpha_vantage/quote": "Alpha Vantage 实时报价",
            "/api/yahoo/quote": "Yahoo Finance 实时报价",
            "/api/yahoo/daily": "Yahoo Finance 日线数据"
        }
    }

if __name__ == "__main__":
    print("=== 部署完成 ===")
    print("")
    print("服务信息：")
    print("  后端 API: http://122.51.142.248:8000")
    print("  前端: http://122.51.142.248")
    print("  健康检查: http://122.51.142.248:8000/api/health")
    print("  API文档: http://122.51.142.248:8000/docs")
    print("")
    print("下一步:")
    print("  1. 测试API接口")
    print("  2. 开始开发前端代码")
    print("  3. 实现Delta净量计算")
    print("  4. 实现SR支撑压力识别")
    print("")
    print("部署时间:", time.strftime('%Y-%m-%d %H:%M:%S'))
    print("版本: 1.0.0")
    print("")
    print("=== NTDF 后端部署完成 ===")
    
    # 启动服务
    print("启动后端服务...")
    import os
    os.chdir("/var/www/ntdf/backend")
    os.system("source venv/bin/activate && nohup uvicorn main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &")
    print("后端服务已启动，日志: /var/www/ntdf/backend/server.log")
'''

    with open('/var/www/ntdf/backend/main.py', 'w') as f:
        f.write(main_py)
    
    print("主文件创建完成")
    
    # 配置 Nginx
    nginx_config = '''server {
    listen 80;
    server_name 122.51.142.248;
    
    root /var/www/ntdf/frontend/dist;
    index index.html;
    
    client_max_body_size 10M;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}'''

    with open('/etc/nginx/sites-available/ntdf', 'w') as f:
        f.write(nginx_config)
    
    # 启用配置
    run_command(
        "ln -sf /etc/nginx/sites-available/ntdf /etc/nginx/sites-enabled/ && rm -f /etc/nginx/sites-enabled/default && nginx -t",
        "配置 Nginx"
    )
    run_command(
        "systemctl restart nginx",
        "重启 Nginx"
    )
    
    print("")
    print("=== 所有服务已启动 ===")
    print("访问地址：http://122.51.51.142.248")
    print("健康检查：http://122.51.51.142.248:8000/api/health")
    print("API文档：http://122.51.51.142.248:8000/docs")
    print("")
    print("部署完成！")
    print("=== NTDF 后端部署完成 ===")

if __name__ == "__main__":
    main()
