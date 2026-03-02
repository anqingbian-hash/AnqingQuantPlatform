#!/usr/bin/env python3
"""
论文写作助手 - 核心工具
整合网络资源、AI重写、论文生成
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Any
import json

# 尝试导入依赖
try:
    from core.llm_client import UniversalLLMClient
    LLM_AVAILABLE = True
except:
    LLM_AVAILABLE = False


class PaperWriter:
    """论文写作助手"""

    def __init__(self, provider: str = "zhipu"):
        """初始化"""
        self.provider = provider
        if LLM_AVAILABLE:
            self.client = UniversalLLMClient(provider)
        else:
            self.client = None
            print("⚠️  LLM客户端不可用，将使用基础功能")

        # 论文结构
        self.thesis_structure = {
            "title": "",
            "author": "",
            "abstract": "",
            "keywords": [],
            "chapters": {}
        }

    def collect_resources(self, topic: str, sources: int = 5) -> List[Dict]:
        """搜集网络资源"""
        print(f"🔍 搜集关于'{topic}'的资源...")

        # 这里可以集成 07-互联网访问 技能
        resources = []

        # 模拟资源（实际使用时调用web_researcher）
        for i in range(sources):
            resources.append({
                "id": f"resource_{i+1}",
                "title": f"{topic}相关资源{i+1}",
                "url": f"https://example.com/{i+1}",
                "type": "paper" if i % 2 == 0 else "blog"
            })

        print(f"✅ 搜集到 {len(resources)} 个资源")
        return resources

    def rewrite_content(self, content: str, technique: str = "paraphrase") -> str:
        """重写内容降重"""
        if not self.client:
            # 基础重写（无LLM）
            return self._basic_rewrite(content, technique)

        print(f"✍️  使用AI重写内容...")

        # 使用LLM重写
        prompt = f"""请改写以下内容，保持原意但用不同的表达方式：

{content}

要求：
1. 使用同义词替换
2. 改变句式结构
3. 保持专业性
4. 控制篇幅相当

重写后的内容："""

        result = self.client.chat([{"role": "user", "content": prompt}])

        if result.get("success"):
            return result["content"]
        else:
            return self._basic_rewrite(content, technique)

    def _basic_rewrite(self, content: str, technique: str) -> str:
        """基础重写（无LLM）"""
        # 简单的同义词替换
        synonyms = {
            "研究": "探讨",
            "分析": "研究",
            "表明": "显示",
            "使用": "运用",
            "方法": "方式",
            "结果": "成果"
        }

        rewritten = content
        for old, new in synonyms.items():
            rewritten = rewritten.replace(old, new)

        return rewritten

    def generate_section(self, title: str, outline: List[str],
                        resources: List[str] = None,
                        length: int = 1000) -> str:
        """生成章节内容"""
        print(f"📝 生成章节: {title}")

        if not self.client:
            # 基础生成
            return self._basic_generate_section(title, outline, length)

        # 使用LLM生成
        prompt = f"""请撰写以下章节内容：

章节标题: {title}

要点:
{chr(10).join(f'- {point}' for point in outline)}

要求：
1. 学术性语言
2. 逻辑清晰
3. 每个要点展开2-3句话
4. 字数约{length}字

章节内容："""

        result = self.client.chat([{"role": "user", "content": prompt}])

        if result.get("success"):
            return result["content"]
        else:
            return self._basic_generate_section(title, outline, length)

    def _basic_generate_section(self, title: str, outline: List[str],
                               length: int) -> str:
        """基础生成（无LLM）"""
        content = f"# {title}\n\n"

        for point in outline:
            content += f"## {point}\n\n"
            content += f"关于{point}的详细阐述...\n\n"

        return content

    def generate_paper(self, title: str, structure: str = "thesis",
                       chapters: Dict = None) -> Dict:
        """生成论文"""
        print(f"📄 开始生成论文: {title}")

        paper = {
            "title": title,
            "structure": structure,
            "chapters": chapters or {},
            "metadata": {
                "created_at": str(Path.cwd()),
                "generator": "10-学术写作"
            }
        }

        # 生成各章节
        for chapter_name, chapter_content in paper["chapters"].items():
            print(f"  生成章节: {chapter_name}")

            if isinstance(chapter_content, dict):
                # 有子章节
                paper["chapters"][chapter_name] = {}
                for section_name, section_points in chapter_content.items():
                    paper["chapters"][chapter_name][section_name] = \
                        self.generate_section(section_name, section_points)
            else:
                # 章节列表
                paper["chapters"][chapter_name] = \
                    self.generate_section(chapter_name, chapter_content)

        print("✅ 论文生成完成！")
        return paper

    def export_paper(self, paper: Dict, format: str = "markdown",
                     output: str = None) -> str:
        """导出论文"""
        print(f"📤 导出论文为 {format.upper()} 格式...")

        if format == "markdown":
            content = self._export_markdown(paper)
            ext = ".md"
        elif format == "latex":
            content = self._export_latex(paper)
            ext = ".tex"
        elif format == "word":
            # Word需要python-docx库
            content = self._export_markdown(paper)  # 先用markdown
            ext = ".md"
            print("⚠️  Word导出需要pandoc转换")
        else:
            content = str(paper)
            ext = ".txt"

        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 已导出到: {output}")

        return content

    def _export_markdown(self, paper: Dict) -> str:
        """导出为Markdown"""
        md = f"# {paper['title']}\n\n"

        for chapter_name, chapter_content in paper["chapters"].items():
            md += f"## {chapter_name}\n\n"

            if isinstance(chapter_content, dict):
                for section_name, section_content in chapter_content.items():
                    md += f"### {section_name}\n\n{section_content}\n\n"
            else:
                md += f"{chapter_content}\n\n"

        return md

    def _export_latex(self, paper: Dict) -> str:
        """导出为LaTeX"""
        latex = f"""\\documentclass{{article}}
\\usepackage{{utf8}}
\\title{{{paper['title']}}}
\\author{{作者姓名}}
\\date{{\\today}}

\\begin{{document}}

\\maketitle

"""

        for chapter_name, chapter_content in paper["chapters"].items():
            latex += f"\\section{{{chapter_name}}}\n\n"

            if isinstance(chapter_content, dict):
                for section_name, section_content in chapter_content.items():
                    latex += f"\\subsection{{{section_name}}}\n\n{section_content}\n\n"
            else:
                latex += f"{chapter_content}\n\n"

        latex += "\\end{document}\n"
        return latex


def main():
    """测试"""
    writer = PaperWriter()

    # 测试1: 搜集资源
    resources = writer.collect_resources("人工智能", 3)
    print(f"资源: {resources}\n")

    # 测试2: 重写内容
    original = "人工智能技术在医疗领域有着广泛的应用。"
    rewritten = writer.rewrite_content(original)
    print(f"原文: {original}")
    print(f"重写: {rewritten}\n")

    # 测试3: 生成章节
    section = writer.generate_section(
        "研究背景",
        ["AI发展现状", "医疗需求"],
        length=200
    )
    print(f"章节预览:\n{section[:200]}...\n")


if __name__ == "__main__":
    main()
