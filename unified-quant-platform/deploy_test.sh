#!/bin/bash
# 测试环境部署脚本
# 创建日期：2026-03-01

set -e  # 遇到错误立即退出

echo "================================================"
echo "🚀 开始部署测试环境"
echo "================================================"

# 停止运行中的服务
echo "⏹️  停止服务..."
systemctl stop quant-trading-test || echo "服务未运行，跳过停止"

# 创建数据目录
echo "📁 创建数据目录..."
mkdir -p data/test/cache
mkdir -p data/test/logs
mkdir -p data/test/temp

# 检查目录创建
if [ -d "data/test/cache" ] && [ -d "data/test/logs" ] && [ -d "data/test/temp" ]; then
    echo "✅ 数据目录创建成功"
else
    echo "❌ 数据目录创建失败"
    exit 1
fi

# 初始化数据库
echo "🗄  初始化数据库..."
mysql -u root -p < database/db_test.sql

if [ $? -eq 0 ]; then
    echo "✅ 数据库初始化成功"
else
    echo "❌ 数据库初始化失败"
    exit 1
fi

# 检查 Python 环境
echo "🐍 检查 Python 环境..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
else
    echo "❌ Python 3 未安装"
    exit 1
fi

# 检查虚拟环境
if [ -d "venv" ]; then
    echo "🐍 使用虚拟环境: venv/"
    PYTHON_CMD="venv/bin/python"
else
    echo "⚠️  未找到虚拟环境，使用系统 Python"
fi

# 安装依赖
echo "📦 安装依赖..."
if [ -f "requirements.txt" ]; then
    $PYTHON_CMD -m pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "✅ 依赖安装成功"
    else
        echo "❌ 依赖安装失败"
        exit 1
    fi
else
    echo "⚠️  未找到 requirements.txt，跳过依赖安装"
fi

# 停止服务（确保没有残留进程）
echo "⏹️  停止残留服务..."
pkill -f "python main.py" || echo "没有残留进程"

# 等待 2 秒
sleep 2

# 启动服务
echo "▶️ 启动服务..."
nohup $PYTHON_CMD main.py --env=test > logs/test.log 2>&1 &
SERVICE_PID=$!

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
if ps -p $SERVICE_PID > /dev/null; then
    echo "✅ 服务启动成功 (PID: $SERVICE_PID)"
else
    echo "❌ 服务启动失败"
    exit 1
fi

# 显示服务信息
echo ""
echo "================================================"
echo "✅ 测试环境部署完成"
echo "================================================"
echo ""
echo "📊 服务信息:"
echo "  服务地址: http://localhost:5000"
echo "  进程 ID: $SERVICE_PID"
echo "  日志文件: logs/test.log"
echo "  配置文件: config/config_test.yaml"
echo "  数据库: quant_test"
echo ""
echo "🔍 健康检查:"
sleep 2
curl -s http://localhost:5000/api/test || echo "⚠️  API 响应异常"
echo ""
echo "📝 查看日志:"
echo "  tail -f logs/test.log"
echo ""
echo "🛑 停止服务:"
echo "  kill $SERVICE_PID"
echo "  或"
echo "  systemctl stop quant-trading-test"
echo ""
echo "================================================"
echo "🎉 部署完成！"
echo "================================================"
