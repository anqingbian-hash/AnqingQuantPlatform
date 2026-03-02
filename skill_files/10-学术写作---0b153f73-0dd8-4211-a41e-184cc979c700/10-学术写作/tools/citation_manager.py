#!/usr/bin/env python3
"""
文献管理工具
自动生成参考文献，支持多种格式
"""

from typing import List, Dict
import json
from datetime import datetime


class CitationManager:
    """文献管理器"""

    # 引用格式模板
    STYLES = {
        "APA": "{author}. ({year}). {title}. *{journal}*, {volume}, {pages}.",
        "MLA": "{author}. \"{title}.\" *{journal}*, vol. {volume}, no. {issue}, {year}, pp. {pages}.",
        "Chicago": "{author}. \"{title}.\" {journal} {volume}, no. {issue} ({year}): {pages}.",
        "GB7714": "{author}. {title}[J]. {journal}, {year}, {volume}({issue}): {pages}."
    }

    def __init__(self, style: str = "APA"):
        """初始化"""
        self.style = style.upper()
        self.papers = []
        self.cited_papers = []

    def add_paper(self, paper: Dict):
        """添加文献"""
        required_fields = ["title", "author", "year"]
        for field in required_fields:
            if field not in paper:
                raise ValueError(f"缺少必需字段: {field}")

        paper["id"] = len(self.papers) + 1
        self.papers.append(paper)
        print(f"✅ 已添加文献: {paper['title'][:30]}...")

    def cite(self, paper_id: int, in_text: bool = True) -> str:
        """生成引用"""
        paper = self.papers[paper_id - 1]

        if in_text:
            # 文内引用
            if self.style == "APA":
                return f"({paper['author']}, {paper['year']})"
            elif self.style == "MLA":
                return f"({paper['author']} {paper['year']}, {paper['id']})"
            elif self.style == "Chicago":
                return f"({paper['author']} {paper['year']}, {paper['id']})"
            else:
                return f"[{paper['id']}]"
        else:
            # 参考文献列表格式
            return self._format_bibliography(paper)

    def _format_bibliography(self, paper: Dict) -> str:
        """格式化参考文献"""
        template = self.STYLES.get(self.style, "{author}. {title}.")

        # 准备所有可能的字段，使用默认值处理缺失字段
        format_data = {
            "author": paper.get("author", "Unknown"),
            "title": paper.get("title", ""),
            "year": paper.get("year", ""),
            "journal": paper.get("journal", ""),
            "volume": paper.get("volume", ""),
            "issue": paper.get("issue", ""),
            "pages": paper.get("pages", "")
        }

        # 根据不同格式处理缺失字段
        if self.style == "APA":
            # APA格式: Zhang. (2024). Title. *Journal*, volume, pages.
            parts = [f"{format_data['author']}. ({format_data['year']}). {format_data['title']}."]
            if format_data['journal']:
                parts.append(f"*{format_data['journal']}*")
            if format_data['volume']:
                parts.append(f"{format_data['volume']}")
            if format_data['pages']:
                parts.append(f"{format_data['pages']}")
            return " ".join(parts) + "."
        elif self.style == "MLA":
            # MLA格式
            parts = [f"{format_data['author']}. \"{format_data['title']}.\""]
            if format_data['journal']:
                parts.append(f"*{format_data['journal']}*")
            if format_data['volume']:
                parts.append(f"vol. {format_data['volume']}")
            if format_data['issue']:
                parts.append(f"no. {format_data['issue']}")
            parts.append(f"{format_data['year']}")
            if format_data['pages']:
                parts.append(f"pp. {format_data['pages']}")
            return ", ".join(parts) + "."
        elif self.style == "Chicago":
            # Chicago格式
            parts = [f"{format_data['author']}. \"{format_data['title']}.\""]
            if format_data['journal']:
                parts.append(f"{format_data['journal']}")
            if format_data['volume']:
                if format_data['issue']:
                    parts.append(f"{format_data['volume']}, no. {format_data['issue']}")
                else:
                    parts.append(f"{format_data['volume']}")
            parts.append(f"({format_data['year']})")
            if format_data['pages']:
                parts.append(f"{format_data['pages']}")
            return " ".join(parts) + "."
        elif self.style == "GB7714":
            # GB/T 7714格式
            parts = [f"{format_data['author']}. {format_data['title']}[J]."]
            if format_data['journal']:
                parts.append(f"{format_data['journal']}")
            parts.append(f"{format_data['year']}")
            if format_data['volume'] and format_data['issue']:
                parts.append(f"{format_data['volume']}({format_data['issue']})")
            elif format_data['volume']:
                parts.append(f"{format_data['volume']}")
            if format_data['pages']:
                parts.append(f"{format_data['pages']}")
            return ", ".join(parts) + "."
        else:
            # 默认格式
            return template.format(**format_data)

    def generate_bibliography(self) -> str:
        """生成参考文献列表"""
        if self.style == "APA":
            bib = "## 参考文献\n\n"
        else:
            bib = "## Bibliography\n\n"

        for paper in self.papers:
            bib += f"{self._format_bibliography(paper)}\n\n"

        return bib

    def export_bibtex(self, filename: str = "references.bib"):
        """导出为BibTeX格式"""
        bibtex = ""

        for paper in self.papers:
            bibtex += f"""@article{{{paper['id']}}},
  author = {{{paper['author']}}},
  title = {{{paper['title']}}},
  journal = {{{paper.get('journal', '')}}},
  year = {{{paper['year']}}},
  volume = {{{paper.get('volume', '')}}},
  number = {{{paper.get('issue', '')}}},
  pages = {{{paper.get('pages', '')}}}
}}

"""

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(bibtex)

        print(f"✅ BibTeX已导出: {filename}")

    def import_from_json(self, filename: str):
        """从JSON导入文献"""
        with open(filename, 'r', encoding='utf-8') as f:
            papers = json.load(f)

        for paper in papers:
            self.add_paper(paper)

        print(f"✅ 从 {filename} 导入了 {len(papers)} 篇文献")

    def export_to_json(self, filename: str = "references.json"):
        """导出为JSON格式"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.papers, f, ensure_ascii=False, indent=2)

        print(f"✅ JSON已导出: {filename}")


def main():
    """测试"""
    cite_mgr = CitationManager(style="APA")

    # 添加文献
    cite_mgr.add_paper({
        "title": "Deep Learning for Medical Image Analysis",
        "author": "Zhang, W., & Li, L.",
        "year": 2024,
        "journal": "Nature Medicine",
        "volume": "30",
        "issue": "4",
        "pages": "123-145"
    })

    cite_mgr.add_paper({
        "title": "AI in Healthcare: A Comprehensive Review",
        "author": "Wang, Y.",
        "year": 2023,
        "journal": "IEEE Transactions on Artificial Intelligence",
        "volume": "8",
        "issue": "2",
        "pages": "45-67"
    })

    # 生成引用
    print("\n文内引用:")
    print(f"APA格式: {cite_mgr.cite(1)}")
    print(f"APA格式: {cite_mgr.cite(2)}")

    # 生成参考文献列表
    print("\n参考文献列表:")
    print(cite_mgr.generate_bibliography())

    # 导出
    cite_mgr.export_bibtex()
    cite_mgr.export_to_json()


if __name__ == "__main__":
    main()
