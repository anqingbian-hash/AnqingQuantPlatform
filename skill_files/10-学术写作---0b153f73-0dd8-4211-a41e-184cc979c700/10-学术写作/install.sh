#!/bin/bash
# 10-学术写作技能 - 一键安装脚本

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "10-学术写作技能 - 安装"
echo "=========================================="

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装"
    exit 1
fi

echo "✓ Python版本: $(python3 --version)"

# 询问是否创建虚拟环境
read -p "是否创建虚拟环境？(推荐) (y/n): " create_venv

if [ "$create_venv" = "y" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✓ 虚拟环境已激活"
fi

# 升级pip
echo "升级pip..."
pip install --upgrade pip -q

# 安装依赖
echo "安装依赖包..."
pip install requests beautifulsoup4 -q 2>/dev/null || echo "  ⚠️  部分依赖安装失败"

# 如果有LLM，安装相关依赖
read -p "是否配置LLM（用于AI重写）？(y/n): " use_llm

if [ "$use_llm" = "y" ]; then
    echo "安装LLM依赖..."
    pip install openai anthropic -q 2>/dev/null || echo "  ⚠️  LLM库安装失败（可选）"
fi

# 创建测试脚本
cat > test_tools.sh << 'EOF'
#!/bin/bash
# 测试学术写作工具

echo "测试学术写作工具..."
echo ""

# 测试1: 降重工具
echo "[1/3] 测试降重工具..."
python3 << PYTEST
from tools.plagiarism_reducer import PlagiarismReducer
reducer = PlagiarismReducer()
original = "人工智能技术在医疗领域有着广泛的应用。"
rewritten = reducer.synonym_replace(original)
print(f"✅ 原文: {original}")
print(f"✅ 重写: {rewritten}")
PYTEST

# 测试2: 文献管理
echo ""
echo "[2/3] 测试文献管理..."
python3 << PYTEST
from tools.citation_manager import CitationManager
cite_mgr = CitationManager()
cite_mgr.add_paper({
    "title": "测试论文",
    "author": "张三",
    "year": 2024,
    "journal": "测试期刊"
})
print(f"✅ 文献管理正常")
PYTEST

# 测试3: 论文生成
echo ""
echo "[3/3] 测试论文生成..."
python3 << PYTEST
from tools.paper_writer import PaperWriter
writer = PaperWriter()
section = writer.generate_section("测试章节", ["要点1", "要点2"], length=50)
print(f"✅ 论文生成正常")
PYTEST

echo ""
echo "✅ 所有测试通过！"
EOF

chmod +x test_tools.sh

# 创建使用示例
cat > example_usage.sh << 'EOF'
#!/bin/bash
# 学术写作使用示例

echo "学术写作技能 - 使用示例"
echo "========================"
echo ""
echo "示例1: 快速降重"
echo ""
python3 << 'PYTHON'
from tools.plagiarism_reducer import PlagiarismReducer

reducer = PlagiarismReducer()
original = "人工智能技术在医疗领域有着广泛的应用。通过深度学习算法，可以实现对医学影像的准确分析。"

# 综合降重（强度70%）
rewritten = reducer.reduce_all(original, intensity=0.7)

print("原文:")
print(original)
print("")
print("降重后:")
print(rewritten)
PYTHON

echo ""
echo "示例2: 生成论文章节"
echo ""
python3 << 'PYTHON'
from tools.paper_writer import PaperWriter

writer = PaperWriter()

# 生成章节
section = writer.generate_section(
    title="研究背景",
    outline=["AI发展现状", "医疗应用需求"],
    length=200
)

print(section)
PYTHON

echo ""
echo "示例3: 管理参考文献"
echo ""
python3 << 'PYTHON'
from tools.citation_manager import CitationManager

cite_mgr = CitationManager(style="APA")

# 添加文献
cite_mgr.add_paper({
    "title": "Deep Learning in Healthcare",
    "author": "Zhang, W.",
    "year": 2024,
    "journal": "Nature Medicine",
    "volume": "30",
    "pages": "123-145"
})

# 生成引用
print("文内引用:")
print(cite_mgr.cite(1))

# 生成参考文献
print("")
print("参考文献:")
print(cite_mgr.generate_bibliography())
PYTHON

echo ""
echo "✅ 示例演示完成！"
EOF

chmod +x example_usage.sh

# 创建快速开始脚本
cat > quickstart.sh << 'EOF'
#!/bin/bash
# 快速开始

echo "10-学术写作技能 - 快速开始"
echo "=========================="
echo ""
echo "【第一步】查看文档"
echo "cat README.md"
echo ""
echo "【第二步】运行示例"
echo "./example_usage.sh"
echo ""
echo "【第三步】降重实战"
echo ""
python3 << 'PYTHON'
from tools.plagiarism_reducer import PlagiarismReducer

reducer = PlagiarismReducer()

# 你的论文段落
your_text = """
人工智能技术近年来取得了显著进展。在医疗领域，AI技术被广泛应用于疾病诊断、药物研发和个性化治疗。研究表明，基于深度学习的医学影像分析系统在早期癌症筛查方面表现优异。
"""

# 降重
rewritten = reducer.reduce_all(your_text, intensity=0.7)

print("原文:")
print(your_text.strip())
print("")
print("降重后:")
print(rewritten.strip())
PYTHON

echo ""
echo "【第四步】生成论文框架"
echo ""
python3 << 'PYTHON'
from tools.paper_writer import PaperWriter

writer = PaperWriter()

# 生成论文
paper = writer.generate_paper(
    title="人工智能在医疗诊断中的应用研究",
    structure="thesis",
    chapters={
        "第一章": {
            "1.1 研究背景": ["AI发展现状", "医疗需求"],
            "1.2 研究意义": ["理论意义", "实用价值"]
        }
    }
)

# 导出
writer.export_paper(paper, format="markdown", output="my_paper.md")
print("✅ 论文框架已生成: my_paper.md")
PYTHON

echo ""
echo "✅ 快速体验完成！"
echo ""
echo "下一步:"
echo "  - 查看 my_paper.md"
echo "  - 编辑添加内容"
echo "  - 使用降重工具优化"
echo "  - 格式化输出"
EOF

chmod +x quickstart.sh

# 完成
echo ""
echo "=========================================="
echo "✅ 安装完成！"
echo "=========================================="
echo ""
echo "使用方法:"
echo "  快速体验: ./quickstart.sh"
echo "  运行示例: ./example_usage.sh"
echo "  测试工具: ./test_tools.sh"
echo ""
echo "核心工具:"
echo "  - tools/paper_writer.py      # 论文写作"
echo "  - tools/plagiarism_reducer.py # 降重工具"
echo "  - tools/citation_manager.py   # 文献管理"
echo "  - tools/web_researcher.py     # 网络研究"
echo ""
echo "文档:"
echo "  - README.md                   # 完整文档"
echo "  - guides/writing_guide.md     # 写作指南"
echo "  - guides/anti_plagiarism_guide.md  # 降重技巧"
echo ""
echo "位置: $(pwd)"
