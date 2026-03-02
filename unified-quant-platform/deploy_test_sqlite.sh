#!/bin/bash
# 测试环境部署脚本（SQLite 版本）
# 创建日期：2026-03-01

set -e  # 遇到错误立即退出

echo "================================================"
echo "🚀 开始部署测试环境（SQLite 版本）"
echo "================================================"

# 停止运行中的服务
echo "⏹️  停止服务..."
pkill -f "python main.py" || echo "服务未运行，跳过停止"

# 创建数据目录
echo "📁 创建数据目录..."
mkdir -p data/test
mkdir -p logs

# 检查目录创建
if [ -d "data/test" ] && [ -d "logs" ]; then
    echo "✅ 数据目录创建成功"
else
    echo "❌ 数据目录创建失败"
    exit 1
fi

# 初始化数据库
echo "🗄  初始化数据库..."
sqlite3 data/test/quant_test.db < database/db_test_sqlite.sql

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
        echo "⚠️  依赖安装失败，但继续..."
    fi
else
    echo "⚠️  未找到 requirements.txt，跳过依赖安装"
fi

# 停止服务（确保没有残留进程）
echo "⏹️ 停止残留服务..."
pkill -f "python main.py" || echo "没有残留进程"

# 等待 2 秒
sleep 2

# 启动服务
echo "▶️ 启动服务..."
nohup $PYTHON_CMD main.py --env=test > logs/test.log 2>&1 &
SERVICE_PID=$!

# 等待服务启动
echo "⏳ 皏待服务启动..."
sleep 5

# 检查服务状态
if ps -p $SERVICE_PID > /dev/null; then
    echo "✅ 服务启动成功 (PID: $SERVICE_PID)"
else
    echo "❌ 服务启动失败"
    echo "查看日志：logs/test.log"
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
echo "  数据库: data/test/quant_test.db"
echo ""
echo "🔍 健康检查:"
sleep 2
curl -s http://localhost:5000/api/test || echo "⚠️  API 响应异常，请检查日志"
echo ""
echo "📝 查看日志:"
echo "  tail -f logs/test.log"
echo ""
echo "🛑 停止服务:"
echo "  kill $SERVICE_PID"
echo ""
echo "⚠️  注意事项:"
echo "  当前使用 SQLite 数据库（测试环境）"
echo "  正式环境应使用 MySQL 数据库"
echo "  测试数据已插入：test_admin (admin123), test_user (user123)"
echo ""
echo "================================================"
echo "🎉 部署完成！"
echo "================================================"
