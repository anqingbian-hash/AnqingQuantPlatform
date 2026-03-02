#!/bin/bash

# 小红书发布技能安装脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== 小红书发布技能安装 ==="
echo ""

# 检查 Python 版本
echo "[1/4] 检查 Python 版本..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "    找到 Python $PYTHON_VERSION"
else
    echo "    错误: 未找到 Python3，请先安装 Python 3.10+"
    exit 1
fi

# 创建虚拟环境（可选）
echo ""
echo "[2/4] 安装依赖..."
cd "$SCRIPT_DIR"
pip3 install -r requirements.txt

# 创建配置文件
echo ""
echo "[3/4] 配置文件..."
if [ ! -f "config/accounts.json" ]; then
    cp config/accounts.json.example config/accounts.json
    echo "    已创建 config/accounts.json"
else
    echo "    config/accounts.json 已存在，跳过"
fi

# 创建临时目录
echo ""
echo "[4/4] 创建临时目录..."
mkdir -p images/publish_temp
echo "    已创建 images/publish_temp"

echo ""
echo "=== 安装完成 ==="
echo ""
echo "使用方法:"
echo "  1. 启动测试浏览器: python scripts/chrome_launcher.py"
echo "  2. 检查登录状态:   python scripts/cdp_publish.py check-login"
echo "  3. 发布内容:       python scripts/publish_pipeline.py --headless ..."
echo ""
echo "详细说明请查看 SKILL.md 文件"
