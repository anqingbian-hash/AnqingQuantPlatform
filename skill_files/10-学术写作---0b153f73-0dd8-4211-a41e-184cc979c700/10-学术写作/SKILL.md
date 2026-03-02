---
name: "academic-writing"
version: "1.0.0"
description: "AI辅助学术写作与降重工具，支持论文生成和查重优化"
author: "AI Skills Team"
tags: ["学术", "写作", "论文", "降重"]
requires: []
---

# 学术写作技能

AI辅助学术写作与降重工具，整合网络资源、AI重写和论文格式化。

## 技能描述

提供完整的学术写作辅助功能，包括网络资源搜集、AI内容重写降重、论文格式化输出、文献管理和查重优化。

## 使用场景

- 用户："帮我写一篇关于人工智能的论文" → 生成论文初稿
- 用户："降重这篇论文" → 智能改写降低查重率
- 用户："搜集这个主题的学术资源" → 搜索相关论文和资料
- 用户："格式化参考文献" → 自动生成引用格式

## 工具和依赖

### 工具列表

位于 `tools/` 目录：
- `paper_writer.py`：论文写作助手
- `plagiarism_reducer.py`：降重工具
- `citation_manager.py`：文献管理
- `web_researcher.py`：网络研究助手

### API密钥

**可选**（用于AI重写）：
- `OPENAI_API_KEY`：OpenAI API密钥
- `ZHIPU_API_KEY`：智谱AI API密钥

### 外部依赖

- Python 3.7+
- 可选：openai, anthropic（用于AI重写）

## 配置说明

### 安装方法

```bash
cd 10-学术写作
bash install.sh
```

### 论文模板

位于 `templates/` 目录：
- `thesis_template.md`：学位论文模板
- `paper_template.md`：期刊论文模板

## 使用示例

### 场景1：快速生成论文初稿

用户："帮我写一篇关于人工智能在医疗中应用的论文"

AI：
```python
from tools.paper_writer import PaperWriter

writer = PaperWriter()

# 搜集资源
resources = writer.collect_resources("人工智能在医疗中的应用", sources=5)

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

# 导出Word
writer.export_paper(paper, format="word", output="我的论文.docx")
```

### 场景2：降重优化

用户："帮我降重这篇论文"

AI：
```python
from tools.plagiarism_reducer import PlagiarismReducer

reducer = PlagiarismReducer()

# 读取论文
with open("original.txt", "r") as f:
    original = f.read()

# 综合降重
rewritten = reducer.reduce_all(original, intensity=0.7)

# 保存
with open("rewritten.txt", "w") as f:
    f.write(rewritten)

print("✅ 降重完成！")
```

### 场景3：网络资源整合

用户："搜集机器学习算法相关的学术资源"

AI：
```python
from tools.web_researcher import WebResearcher

researcher = WebResearcher()

# 搜索论文
papers = researcher.search_papers("machine learning in healthcare", num=10)

# 提取摘要
for paper in papers:
    abstract = researcher.extract_abstract(paper["url"])
    print(f"✅ {paper['title']}")
    print(f"   {abstract[:100]}...")
```

### 场景4：文献管理

用户："生成APA格式的参考文献"

AI：
```python
from tools.citation_manager import CitationManager

cite_mgr = CitationManager(style="APA")

# 添加文献
cite_mgr.add_paper({
    "title": "Deep Learning for Healthcare",
    "author": "Smith, J.",
    "year": 2024,
    "journal": "Nature Medicine"
})

# 生成参考文献列表
bibliography = cite_mgr.generate_bibliography()
print(bibliography)
```

## 降重技巧

### 技巧1：同义词替换

```python
text = "人工智能技术在医疗领域有着广泛的应用前景"
new_text = reducer.synonym_replace(text)
# → "AI技术在医疗行业具有巨大的运用潜力"
```

### 技巧2：被动转主动

```python
new_text = reducer.change_voice("实验结果被记录在表1中")
# → "表1展示了实验结果"
```

### 技巧3：扩展细节

```python
new_text = reducer.expand_paragraph("机器学习算法可以用于疾病诊断")
# → "机器学习算法通过分析患者的医学影像数据、病历信息以及生化指标，能够辅助医生进行更准确的疾病诊断..."
```

### 技巧4：综合降重（推荐）

```python
# 强度控制
# 0.3-0.5: 轻度降重（保持原意，小幅改动）
# 0.5-0.7: 中度降重（常用，平衡质量和原创性）
# 0.7-0.9: 重度降重（大幅改写，原创性高）

new_text = reducer.reduce_all(
    original_text,
    intensity=0.7,
    techniques=[
        "synonym_replace",
        "change_voice",
        "restructure_sentence",
        "expand_paragraph"
    ]
)
```

## 查重率控制标准

| 文档类型 | 查重率要求 |
|---------|-----------|
| 本科论文 | < 30% |
| 硕士论文 | < 20% |
| 博士论文 | < 15% |
| 期刊论文 | < 10-15% |

## 论文写作流程

### 阶段1：选题与资料搜集

1. 确定研究方向
2. 搜集网络资源
3. 确定创新点

### 阶段2：大纲设计

1. 确定章节结构
2. 编写详细大纲

### 阶段3：初稿写作

1. 使用AI辅助写作
2. 整合网络资源
3. 添加引用

### 阶段4：降重优化

1. 使用降重工具
2. 逐段降重
3. 查重检查

### 阶段5：格式化与提交

1. 格式化输出
2. 检查规范
3. 提交

## 故障排除

### 问题1：降重效果不理想

**解决**：
- 调整intensity参数（0.5-0.7）
- 使用更多降重技巧
- 手动修改降重后的内容

### 问题2：论文生成质量不高

**解决**：
- 提供更详细的大纲
- 搜集更多相关资源
- 手动编辑生成的内容

### 问题3：文献搜索结果少

**解决**：
- 使用更通用的关键词
- 尝试不同的学术搜索引擎
- 手动补充文献

## 学术诚信

### ✅ 正确用法

- 辅助搜集资料
- 帮助改写降重
- 提供写作建议
- 格式化输出

### ❌ 错误用法

- 直接代写整篇论文
- 抄袭他人成果
- 虚假数据
- 学术不端

## 注意事项

1. **理解为先**：理解原材料再重写
2. **适当引用**：标注出处，避免抄袭
3. **原创为主**：添加自己的见解
4. **多次查重**：及时修改重复内容
5. **学术诚信**：本技能辅助写作，但不等于代写
