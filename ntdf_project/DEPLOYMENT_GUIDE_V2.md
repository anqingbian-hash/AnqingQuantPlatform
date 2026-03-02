# NTDF 项目部署指南 - 版本2.0

## 📋 快速部署（3步）

### 步骤1：替换后端文件

```bash
cd /var/www/ntdf/backend
```

**复制粘贴下面的Python代码，覆盖 simple_main.py 文件**

（由于文件太长，我会分段发送，请分段复制粘贴）

### 步骤2：替换前端文件

```bash
cd /var/www/ntdf/frontend/src
```

**复制粘贴下面的Vue3代码，覆盖 App.vue 文件**

### 步骤3：重启服务

```bash
# 重启后端
cd /var/www/ntdf/backend
source ~/.nvm/nvm.sh
nvm use 20
pkill -f uvicorn
python3 -m uvicorn simple_main:app --host 0.0.0.0 --port 8000 &

# 重启前端
cd /var/www/ntdf/frontend
pkill -f "npm run dev"
source ~/.nvm/nvm.sh
nvm use 20
npm run dev &
```

## ✅ 部署完成后

**访问地址：**
- 前端：http://122.51.142.248:3001
- 后端：http://122.51.142.248:8000
- 健康检查：http://122.51.142.248:8000/health

## 🎯 新增功能

### 后端（10个接口）
1. ✅ /health - 健康检查
2. ✅ /api/market/alpha_vantage/quote - Alpha Vantage报价
3. ✅ /api/market/alpha_vantage/daily - Alpha Vantage日线数据
4. ✅ /api/market/yahoo/quote - Yahoo Finance报价
5. ✅ /api/market/yahoo/daily - Yahoo Finance日线数据
6. ✅ /api/indicators/sma - SMA技术指标
7. ✅ /api/indicators/ema - EMA技术指标
8. ✅ /api/indicators/rsi - RSI技术指标

### 前端（8个功能）
1. ✅ 系统状态监控
2. ✅ 股票代码查询
3. ✅ 实时报价获取
4. ✅ 日线数据查询
5. ✅ SMA技术指标
6. ✅ EMA技术指标
7. ✅ RSI技术指标
8. ✅ 响应式设计

## 🚀 快速开始

1. **复制Python代码** → 覆盖 simple_main.py
2. **复制Vue3代码** → 覆盖 App.vue
3. **重启服务**
4. **刷新浏览器**

完成！
