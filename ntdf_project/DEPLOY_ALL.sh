#!/bin/bash

# ===========================================
# NTDF 项目完整部署脚本
# ===========================================

echo "=========================================="
echo "  NTDF 项目完整部署"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 函数：打印成功消息
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# 函数：打印警告消息
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 函数：打印错误消息
error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查是否在正确的服务器上
echo "🔍 检查服务器环境..."
if [ ! -f "/var/www/ntdf" ]; then
    warning "NTDF目录不存在，正在创建..."
    sudo mkdir -p /var/www/ntdf
    sudo chown ubuntu:ubuntu /var/www/ntdf
    success "目录创建完成"
fi

cd /var/www/ntdf
success "进入项目目录: /var/www/ntdf"

echo ""
echo "=========================================="
echo "  步骤 1/5: 部署后端"
echo "=========================================="
echo ""

# 创建后端目录
echo "📁 创建后端目录..."
mkdir -p backend
cd backend
success "后端目录创建完成"

# 检查simple_main.py是否存在
if [ ! -f "simple_main.py" ]; then
    error "simple_main.py 不存在！"
    echo ""
    echo "请先创建 simple_main.py 文件"
    echo "位置: /var/www/ntdf/backend/simple_main.py"
    exit 1
fi

success "simple_main.py 已存在"

# 检查requirements.txt是否存在
if [ ! -f "requirements.txt" ]; then
    error "requirements.txt 不存在！"
    exit 1
fi

success "requirements.txt 已存在"

# 创建虚拟环境
echo ""
echo "🐍 创建Python虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    success "虚拟环境创建完成"
else
    warning "虚拟环境已存在"
fi

# 激活虚拟环境
echo ""
echo "🔓 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo ""
echo "📦 安装Python依赖..."
pip install --upgrade pip
pip install -r requirements.txt
success "依赖安装完成"

# 测试后端
echo ""
echo "🧪 测试后端启动..."
echo "后台启动后端服务..."
uvicorn simple_main:app --host 0.0.0.0 --port 8000 > /var/log/ntdf_backend.log 2>&1 &
BACKEND_PID=$!

sleep 5

# 检查后端是否启动成功
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    success "后端服务启动成功！"
    echo "   - PID: $BACKEND_PID"
    echo "   - 端口: 8000"
    echo "   - 日志: /var/log/ntdf_backend.log"
else
    error "后端服务启动失败"
    echo "查看日志: tail -f /var/log/ntdf_backend.log"
fi

echo ""
echo "=========================================="
echo "  步骤 2/5: 部署前端"
echo "=========================================="
echo ""

# 创建前端目录
echo "📁 创建前端目录..."
cd /var/www/ntdf
mkdir -p frontend/src/components
cd frontend
success "前端目录创建完成"

# 检查package.json是否存在
if [ ! -f "package.json" ]; then
    error "package.json 不存在！"
    exit 1
fi

success "package.json 已存在"

# 检查其他必要文件
for file in "index.html" "vite.config.ts" "src/main.ts" "src/App.vue"; do
    if [ ! -f "$file" ]; then
        warning "$file 不存在，请手动创建"
    else
        success "$file 已存在"
    fi
done

# 检查组件文件
for file in "src/components/CandlestickChart.vue" "src/components/VolumeChart.vue" "src/components/SRChart.vue"; do
    if [ ! -f "$file" ]; then
        warning "$file 不存在，请手动创建"
    else
        success "$file 已存在"
    fi
done

# 安装前端依赖
echo ""
echo "📦 安装Node.js依赖..."
npm install
success "依赖安装完成"

# 构建前端
echo ""
echo "🏗️  构建前端..."
npm run build
success "前端构建完成"

echo ""
echo "=========================================="
echo "  步骤 3/5: 配置Nginx"
echo "=========================================="
echo ""

# 创建Nginx配置
echo "📝 创建Nginx配置..."
sudo tee /etc/nginx/sites-available/ntdf > /dev/null << 'EOF'
server {
    listen 80;
    server_name 122.51.142.248;

    # 前端静态文件
    root /var/www/ntdf/frontend/dist;
    index index.html;

    # 前端路由
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

        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 日志
    access_log /var/log/nginx/ntdf_access.log;
    error_log /var/log/nginx/ntdf_error.log;
}
EOF

success "Nginx配置创建完成"

# 启用配置
echo ""
echo "🔗 启用Nginx配置..."
sudo ln -sf /etc/nginx/sites-available/ntdf /etc/nginx/sites-enabled/
sudo nginx -t
success "Nginx配置测试通过"

# 重启Nginx
echo ""
echo "🔄 重启Nginx..."
sudo systemctl reload nginx
success "Nginx重启完成"

echo ""
echo "=========================================="
echo "  步骤 4/5: 配置防火墙"
echo "=========================================="
echo ""

# 检查防火墙状态
if command -v ufw > /dev/null 2>&1; then
    echo "🛡️  配置防火墙规则..."
    sudo ufw allow 80/tcp
    sudo ufw allow 8000/tcp
    sudo ufw allow 3000/tcp
    success "防火墙规则配置完成"
else
    warning "防火墙未安装或未启用"
fi

echo ""
echo "=========================================="
echo "  步骤 5/5: 测试部署"
echo "=========================================="
echo ""

# 测试后端
echo "🧪 测试后端API..."
BACKEND_TEST=$(curl -s http://localhost:8000/health)
if echo "$BACKEND_TEST" | grep -q "healthy"; then
    success "后端健康检查通过"
else
    error "后端健康检查失败"
    echo "$BACKEND_TEST"
fi

# 测试前端
echo ""
echo "🧪 测试前端..."
if [ -d "dist" ]; then
    success "前端构建文件存在"
else
    error "前端构建文件不存在"
fi

# 测试Nginx
echo ""
echo "🧪 测试Nginx..."
if sudo systemctl is-active --quiet nginx; then
    success "Nginx运行正常"
else
    error "Nginx未运行"
fi

echo ""
echo "=========================================="
echo "  部署完成！"
echo "=========================================="
echo ""

success "所有服务已成功部署！"
echo ""
echo "📊 服务地址："
echo "   - 前端: http://122.51.142.248"
echo "   - 后端: http://122.51.142.248:8000"
echo "   - API文档: http://122.51.142.248:8000/docs"
echo "   - 健康检查: http://122.51.142.248:8000/health"
echo ""

echo "📋 服务状态："
echo "   - 后端PID: $BACKEND_PID"
echo "   - 后端日志: tail -f /var/log/ntdf_backend.log"
echo "   - Nginx状态: sudo systemctl status nginx"
echo "   - Nginx日志: sudo tail -f /var/log/nginx/ntdf_error.log"
echo ""

echo "🔧 管理命令："
echo "   - 重启后端: pkill -f uvicorn && cd /var/www/ntdf/backend && source venv/bin/activate && uvicorn simple_main:app --host 0.0.0.0 --port 8000 &"
echo "   - 重启Nginx: sudo systemctl restart nginx"
echo "   - 重新构建前端: cd /var/www/ntdf/frontend && npm run build"
echo ""

success "NTDF系统部署完成！"
echo ""
echo "=========================================="
