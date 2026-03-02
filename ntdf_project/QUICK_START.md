# 🚀 NTDF 项目快速部署指南

## ⚡ 快速开始（3步完成）

### 步骤1：准备文件（5分钟）

```bash
# 在腾讯云WebShell中执行
cd /var/www/ntdf
```

**后端需要的文件：**
```
backend/
├── simple_main.py        # FastAPI主文件
├── requirements.txt      # Python依赖
└── start.sh             # 启动脚本
```

**前端需要的文件：**
```
frontend/
├── package.json         # Node.js配置
├── vite.config.ts       # Vite配置
├── index.html           # HTML入口
├── src/
│   ├── main.ts         # TypeScript入口
│   ├── App.vue         # 主组件
│   └── components/
│       ├── CandlestickChart.vue  # K线图
│       ├── VolumeChart.vue      # 成交量图
│       └── SRChart.vue          # SR支撑压力图
```

### 步骤2：自动部署（10分钟）

```bash
# 1. 复制所有文件到服务器（手动或通过WebShell上传）
# 2. 执行部署脚本
bash DEPLOY_ALL.sh
```

### 步骤3：访问系统（完成！）

- 前端: http://122.51.142.248
- 后端: http://122.51.142.248:8000
- API文档: http://122.51.142.248:8000/docs

---

## 📋 手动部署步骤（如果自动部署失败）

### 1. 后端部署

```bash
cd /var/www/ntdf/backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn simple_main:app --host 0.0.0.0 --port 8000 &
```

### 2. 前端部署

```bash
cd /var/www/ntdf/frontend

# 安装依赖
npm install

# 构建生产版本
npm run build
```

### 3. 配置Nginx

```bash
# 创建配置文件
sudo nano /etc/nginx/sites-available/ntdf
```

添加以下内容：

```nginx
server {
    listen 80;
    server_name 122.51.142.248;

    root /var/www/ntdf/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

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
sudo ln -s /etc/nginx/sites-available/ntdf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🧪 测试部署

### 测试后端

```bash
curl http://122.51.142.248:8000/health
curl "http://122.51.142.248:8000/api/market/yahoo/quote?symbol=AAPL"
```

### 测试前端

在浏览器中访问：
- http://122.51.142.248

---

## 🔧 故障排除

### 后端无法启动

```bash
# 查看日志
tail -f /var/log/ntdf_backend.log

# 检查端口占用
sudo netstat -tuln | grep 8000

# 手动启动
cd /var/www/ntdf/backend
source venv/bin/activate
uvicorn simple_main:app --host 0.0.0.0 --port 8000
```

### 前端无法访问

```bash
# 检查Nginx状态
sudo systemctl status nginx

# 查看日志
sudo tail -f /var/log/nginx/ntdf_error.log

# 重新构建
cd /var/www/ntdf/frontend
npm run build
```

### API调用失败

```bash
# 测试本地连接
curl http://localhost:8000/health

# 检查防火墙
sudo ufw status
```

---

## 📞 联系支持

- 项目经理：变形金刚
- 负责人：卞董
- 服务器：122.51.142.248

---

**祝部署顺利！** 🎉
