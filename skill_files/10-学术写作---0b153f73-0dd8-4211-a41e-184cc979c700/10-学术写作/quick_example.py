#!/usr/bin/env python3
"""
学术写作技能 - 实用示例
快速上手：降重、生成论文、管理文献
"""

import sys
sys.path.insert(0, 'tools')

from paper_writer import PaperWriter
from plagiarism_reducer import PlagiarismReducer
from citation_manager import CitationManager
from web_researcher import WebResearcher


def example_1_plagiarism_reduction():
    """示例1: 降重实战"""
    print("=" * 60)
    print("示例1: 降重实战")
    print("=" * 60)
    print()

    reducer = PlagiarismReducer()

    # 原始段落
    original = """
    人工智能技术在医疗领域有着广泛的应用前景。通过深度学习算法，
    可以实现对医学影像的准确分析。研究表明，这一技术在早期疾病诊断
    方面具有很大潜力，可以提高诊断准确率和效率。
    """

    print("【原文】")
    print(original.strip())
    print()

    # 方法1: 轻度降重（30%强度）
    light = reducer.reduce_all(original, intensity=0.3,
                             techniques=["synonym_replace", "change_voice"])

    print("【轻度降重（30%强度）】")
    print(light.strip())
    print()

    # 方法2: 中度降重（60%强度）
    medium = reducer.reduce_all(original, intensity=0.6,
                               techniques=["synonym_replace", "change_voice",
                                           "restructure_sentence"])

    print("【中度降重（60%强度）】")
    print(medium.strip())
    print()

    # 方法3: 重度降重（90%强度）
    heavy = reducer.reduce_all(original, intensity=0.9,
                            techniques=["synonym_replace", "change_voice",
                                          "restructure_sentence", "expand_paragraph",
                                          "add_examples"])

    print("【重度降重（90%强度）】")
    print(heavy.strip())
    print()


def example_2_generate_section():
    """示例2: 生成论文章节"""
    print("=" * 60)
    print("示例2: 生成论文章节")
    print("=" * 60)
    print()

    writer = PaperWriter()

    section = writer.generate_section(
        title="1.1 研究背景",
        outline=[
            "人工智能技术的快速发展",
            "医疗行业的信息化需求",
            "AI在医疗诊断中的应用现状"
        ],
        length=300
    )

    print("【生成的章节】")
    print(section)
    print()


def example_3_citation():
    """示例3: 文献管理"""
    print("=" * 60)
    print("示例3: 文献管理")
    print("=" * 60)
    print()

    cite_mgr = CitationManager(style="APA")

    # 添加文献
    cite_mgr.add_paper({
        "title": "Deep Learning for Medical Image Analysis: A Comprehensive Survey",
        "author": "Zhang, W., & Li, L.",
        "year": 2024,
        "journal": "Nature Medicine",
        "volume": "30",
        "issue": "4",
        "pages": "123-145"
    })

    cite_mgr.add_paper({
        "title": "AI in Healthcare: Applications and Challenges",
        "author": "Wang, Y., & Chen, X.",
        "year": 2023,
        "journal": "IEEE Transactions on Artificial Intelligence",
        "volume": "8",
        "issue": "2",
        "pages": "45-67"
    })

    print("【添加了2篇文献】")
    print()

    # 生成引用
    print("【文内引用示例】")
    print(f"  {cite_mgr.cite(1)} 介绍了深度学习在医学影像中的应用")
    print(f"  {cite_mgr.cite(2)}  探讨了AI在医疗领域的挑战")
    print()

    # 生成参考文献列表
    print("【参考文献列表】")
    print(cite_mgr.generate_bibliography())
    print()


def example_4_complete_workflow():
    """示例4: 完整工作流"""
    print("=" * 60)
    print("示例4: 完整写作工作流")
    print("=" * 60)
    print()

    # 初始化工具
    researcher = WebResearcher()
    reducer = PlagiarismReducer()
    writer = PaperWriter()
    cite_mgr = CitationManager(style="APA")

    print("【场景】写一篇关于'AI在医疗诊断中的应用'的论文章节")
    print()

    # 1. 搜集资源
    print("步骤1: 搜集网络资源")
    print("-" * 40)
    researcher = WebResearcher()
    resources = researcher.search_papers("AI医疗诊断", num=3)
    print()

    # 2. 提取关键点
    print("步骤2: 提取关键信息")
    print("-" * 40)
    for resource in resources[:2]:
        points = researcher.extract_key_points(resource)
        print(f"  {resource['title']}:")
        for point in points:
            print(f"    - {point}")
    print()

    # 3. 重写降重
    print("步骤3: AI重写降重")
    print("-" * 40)
    reducer = PlagiarismReducer()
    original_content = "深度学习技术通过分析医学影像，能够辅助医生进行疾病诊断。"
    rewritten = reducer.reduce_all(original_content, intensity=0.7,
                                techniques=["expand_paragraph", "add_examples"])
    print(f"原文: {original_content}")
    print(f"重写: {rewritten}")
    print()

    # 4. 生成章节
    print("步骤4: 生成论文章节")
    print("-" * 40)
    writer = PaperWriter()
    section = writer.generate_section(
        title="1.2 研究现状",
        outline=["AI在医疗诊断中的应用", "现有技术的局限性", "本文的创新点"],
        length=400
    )
    print(section[:200] + "...")
    print()

    # 5. 添加引用
    print("步骤5: 添加文献引用")
    print("-" * 40)
    print(f"  参考: {cite_mgr.cite(1)}")
    print()

    print("✅ 完整工作流演示完成！")


def main():
    """运行所有示例"""
    print()
    print("🎓 学术写作技能 - 实用示例")
    print("=" * 60)
    print()

    # 运行示例
    example_1_plagiarism_reduction()
    print()
    example_2_generate_section()
    print()
    example_3_citation()
    print()
    example_4_complete_workflow()

    print()
    print("=" * 60)
    print("✅ 所有示例演示完成！")
    print()
    print("💡 使用建议:")
    print("  1. 运行 bash quickstart.sh 快速体验")
    print("  2. 查看 guides/ 目录下的详细指南")
    print("  3. 根据自己的论文主题定制使用")
    print()


if __name__ == "__main__":
    main()
