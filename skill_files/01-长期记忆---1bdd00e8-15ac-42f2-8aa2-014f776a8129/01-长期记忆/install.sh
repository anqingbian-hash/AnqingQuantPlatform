#!/bin/bash
# AI长期记忆技能 - 快速安装脚本

echo "=========================================="
echo "AI长期记忆技能 - 安装向导"
echo "=========================================="

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.7+"
    exit 1
fi

echo "✓ Python版本: $(python3 --version)"

# 创建虚拟环境（推荐）
read -p "是否创建虚拟环境? (y/n): " create_venv

if [ "$create_venv" = "y" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv

    echo "激活虚拟环境..."
    source venv/bin/activate

    echo "✓ 虚拟环境已创建"
fi

# 升级pip
echo "升级pip..."
pip install --upgrade pip -q

# 安装依赖
echo "安装依赖包..."
pip install -r requirements.txt

# 创建启动脚本
cat > run.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
python ai_memory.py
EOF

chmod +x run.sh

echo ""
echo "=========================================="
echo "安装完成！"
echo "=========================================="
echo ""
echo "使用方法:"
echo "  方式1: ./run.sh"
echo "  方式2: python ai_memory.py"
echo ""
echo "如需卸载，删除此目录即可: rm -rf $(pwd)"
