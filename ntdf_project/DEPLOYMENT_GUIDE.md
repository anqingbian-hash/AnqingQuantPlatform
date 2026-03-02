# NTDF 数字净量分析系统 - 完整部署指南

## 📊 项目概述

**项目名称：** NTDF (Digital Net Analysis System) 数字净量分析系统
**版本：** 1.0.0 (MVP Phase 1)
**开发周期：** 2026年2月 - 3月

## 🏗️ 系统架构

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────┐
│   Nginx     │  (80)
└──────┬──────┘
       │
       ├──────────┐
       │          │
       ▼          ▼
┌──────────┐  ┌──────────┐
│ Frontend │  │ Backend  │ (8000)
│  (Vue3)  │  │ (FastAPI)│
└──────────┘  └─────┬────┘
                    │
                    ├──────────┬──────────┐
                    │          │          │
                    ▼          ▼          ▼
              ┌────────┐ ┌───────┐ ┌──────────┐
              │Alpha   │ │Yahoo  │ │PostgreSQL│
              │Vantage │ │Finance│ │(Optional)│
              └────────┘ └───────┘ └──────────┘
```

## 🚀 快速开始

### 第1步：准备服务器环境

在腾讯云WebShell中执行：

```bash
# 更新系统
sudo apt-get update && sudo apt-get upgrade -y

# 安装基础工具
sudo apt-get install -y curl git python3 python3-pip nodejs npm

# 检查版本
python3 --version
node --version
npm --version
```

### 第2步：部署后端

```bash
# 创建后端目录
mkdir -p /var/www/ntdf/backend
cd /var/www/ntdf/backend

# 创建文件（见后端部分）
# - simple_main.py
# - requirements.txt
# - start.sh

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务器
uvicorn simple_main:app --host 0.0.0.0 --port 8000
```

### 第3步：部署前端

```bash
# 创建前端目录
mkdir -p /var/www/ntdf/frontend
cd /var/www/ntdf/frontend

# 创建文件（见前端部分）
# - package.json
# - vite.config.ts
# - index.html
# - src/main.ts
# - src/App.vue

# 安装依赖
npm install

# 开发模式
npm run dev

# 或构建生产版本
npm run build
```

### 第4步：配置Nginx

```bash
# 创建Nginx配置
sudo nano /etc/nginx/sites-available/ntdf
```

添加以下内容：

```nginx
server {
    listen 80;
    server_name 122.51.142.248;

    # 前端静态文件
    root /var/www/ntdf/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

启用配置：

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/ntdf /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

## 📦 后端API文档

### 基础接口

#### 健康检查
```
GET /health
```

返回：
```json
{
  "status": "healthy",
  "timestamp": "2026-02-22T12:00:00Z",
  "version": "1.0.0"
}
```

### 市场数据接口

#### Alpha Vantage 实时报价
```
GET /api/market/alpha_vantage/quote?symbol=AAPL
```

#### Yahoo Finance 实时报价
```
GET /api/market/yahoo/quote?symbol=AAPL
```

#### Alpha Vantage 日线数据
```
GET /api/market/alpha_vantage/daily?symbol=AAPL&outputsize=compact
```

#### Yahoo Finance 日线数据
```
GET /api/market/yahoo/daily?symbol=AAPL&period=1mo
```

### 技术指标接口

#### SMA (Simple Moving Average)
```
GET /api/indicators/sma?symbol=AAPL&period=20
```

#### EMA (Exponential Moving Average)
```
GET /api/indicators/ema?symbol=AAPL&period=20
```

#### RSI (Relative Strength Index)
```
GET /api/indicators/rsi?symbol=AAPL&period=14
```

## 🎨 前端功能

### 当前实现

- ✅ 系统健康检查
- ✅ 市场数据查询
- ✅ 技术指标计算
- ✅ 响应式设计

### 后续功能

- ⏳ K线图表
- ⏳ SR支撑压力线
- ⏳ Delta净量图
- ⏳ 交易信号标记
- ⏳ 数据导出

## 🔧 故障排除

### 后端无法启动

```bash
# 检查端口占用
sudo netstat -tuln | grep 8000

# 杀死占用进程
sudo kill -9 <PID>

# 检查日志
tail -f /var/log/ntdf/error.log
```

### 前端无法访问

```bash
# 检查Nginx状态
sudo systemctl status nginx

# 查看Nginx日志
sudo tail -f /var/log/nginx/error.log

# 检查文件权限
ls -la /var/www/ntdf/frontend/dist/
```

### API调用失败

```bash
# 检查后端状态
curl http://localhost:8000/health

# 检查网络连接
curl http://122.51.142.248:8000/health
```

## 📞 联系支持

如有问题，请联系：
- 项目经理：卞安青
- 开发团队：变形金刚

## 📄 许可证

版权所有 © 2026 NTDF Digital Net Analysis System
