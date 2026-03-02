# NTDF Frontend Deployment

## 📦 安装依赖

```bash
cd /var/www/ntdf/frontend
npm install
```

## 🚀 启动开发服务器

```bash
npm run dev
```

## 🏗️ 构建生产版本

```bash
npm run build
```

## 📋 部署到服务器

### 方法1：手动部署

```bash
# 1. 在服务器上创建目录
mkdir -p /var/www/ntdf/frontend
cd /var/www/ntdf/frontend

# 2. 复制所有文件
# - package.json
# - package-lock.json
# - vite.config.ts
# - index.html
# - src/

# 3. 安装依赖
npm install

# 4. 构建
npm run build

# 5. 配置 Nginx
sudo cp dist/* /var/www/html/
```

### 方法2：使用Nginx

Nginx配置示例：

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

## 🎯 访问地址

- 开发环境: http://localhost:3000
- 生产环境: http://122.51.142.248
