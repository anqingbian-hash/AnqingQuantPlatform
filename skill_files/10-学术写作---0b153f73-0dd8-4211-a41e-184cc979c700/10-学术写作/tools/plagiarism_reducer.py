#!/usr/bin/env python3
"""
降重工具 - 降低查重率
多种技巧组合使用
"""

import re
import random
from typing import List


class PlagiarismReducer:
    """降重工具"""

    def __init__(self):
        """初始化"""
        # 同义词库
        self.synonyms = {
            "研究": ["探讨", "探究", "分析", "研究", "考察"],
            "分析": ["研究", "探讨", "解析", "剖析", "分析"],
            "表明": ["显示", "揭示", "指出", "说明", "表明"],
            "使用": ["运用", "采用", "应用", "利用", "使用"],
            "方法": ["方式", "手段", "路径", "策略", "方法"],
            "结果": ["成果", "成效", "结论", "结果", "产出"],
            "技术": ["技术", "工艺", "技巧", "方法", "手段"],
            "系统": ["体系", "架构", "框架", "平台", "系统"],
            "模型": ["架构", "框架", "结构", "范式", "模型"],
            "算法": ["流程", "程序", "规则", "方法", "算法"],
            "数据": ["信息", "资料", "素材", "数据", "数值"],
            "问题": ["难题", "困难", "挑战", "问题", "议题"],
            "应用": ["运用", "采用", "实施", "应用", "使用"],
            "发现": ["揭示", "识别", "察觉", "发现", "得出"],
            "提出": ["建议", "提议", "提出", "给出", "提供"],
            "认为": ["指出", "表明", "主张", "认为", "觉得"],
            "需要": ["必须", "应该", "需要", "要求", "有必要"],
            "可以": ["能够", "可以", "可能", "有机会", "有能力"],
            "非常": ["十分", "极其", "相当", "非常", "特别"],
            "很多": ["大量", "众多", "许多", "诸多", "很多"],
            "通过": ["借助", "依靠", "利用", "通过", "经由"],
            "关于": ["涉及", "有关", "关于", "针对", "围绕"],
            "以及": ["和", "与", "及", "以及", "还有"],
            "因此": ["所以", "因而", "故而", "因此", "据此"],
            "但是": ["然而", "不过", "但是", "反之", "相比之下"]
        }

    def synonym_replace(self, text: str) -> str:
        """同义词替换"""
        words = text.split()
        replaced = []

        for word in words:
            # 去除标点
            clean_word = re.sub(r'[，。！？、：；""''（）]', '', word)

            if clean_word in self.synonyms:
                # 随机选择同义词
                replacement = random.choice(self.synonyms[clean_word])
                # 保持标点
                punctuation = re.sub(r'[\\u4e00-\\u9fa5]', '', word)
                if punctuation:
                    replaced.append(replacement + punctuation)
                else:
                    replaced.append(replacement)
            else:
                replaced.append(word)

        return "".join(replaced)

    def change_voice(self, text: str) -> str:
        """被动转主动"""
        # 被动句式
        passive_patterns = [
            (r'(.+)被(.+)', r'\2\1'),
            (r'(.+)由(.+)', r'\2\1'),
            (r'(.+)是通过(.+)', r'\2\1实现了'),
            (r'(.+)进行了(.+)', r'\1\2'),
        ]

        result = text
        for pattern, replacement in passive_patterns:
            result = re.sub(pattern, replacement, result)

        return result

    def restructure_sentence(self, text: str) -> str:
        """重组句子结构"""
        sentences = re.split(r'[。！？]', text)
        restructured = []

        for sentence in sentences:
            if not sentence.strip():
                continue

            # 改变语序
            words = sentence.split()
            if len(words) > 6:
                # 交换前半部分和后半部分
                mid = len(words) // 2
                new_order = words[mid:] + words[:mid]
                restructured.append("".join(new_order) + "。")
            else:
                restructured.append(sentence + "。")

        return "".join(restructured)

    def expand_paragraph(self, text: str, expansion_factor: float = 2.0) -> str:
        """扩展段落"""
        sentences = re.split(r'。', text)
        expanded = []

        for sentence in sentences:
            if not sentence.strip():
                continue

            expanded.append(sentence)

            # 添加扩展内容
            if "技术" in sentence:
                expanded.append(f"这项技术具有重要的应用价值和推广前景。")
            if "方法" in sentence:
                expanded.append(f"该方法在实践中表现出了良好的效果和可靠性。")
            if "研究" in sentence:
                expanded.append(f"相关研究为这一领域的进一步发展奠定了基础。")

        return "。".join(expanded)

    def add_examples(self, text: str, examples: List[str] = None) -> str:
        """添加实例"""
        if not examples:
            examples = [
                "例如，在实际应用中...",
                "以某行业为例...",
                "通过案例分析可以看到..."
            ]

        result = text
        # 在适当位置插入实例
        sentences = result.split("。")
        for i in range(0, len(sentences), 3):
            if i < len(examples):
                sentences.insert(i, examples[i % len(examples)])

        return "。".join(sentences)

    def restructure_logic(self, text: str) -> str:
        """逻辑重组"""
        # 识别因果关系词并重组
        connectors = {
            "首先": "首要的是",
            "然后": "接下来",
            "最后": "最终",
            "因为": "由于",
            "所以": "因此"
        }

        result = text
        for old, new in connectors.items():
            result = result.replace(old, new)

        return result

    def reduce_all(self, text: str, intensity: float = 0.7,
                   techniques: List[str] = None) -> str:
        """综合降重（推荐使用）

        Args:
            text: 原文
            intensity: 降重强度 0-1
            techniques: 使用的技巧列表

        Returns:
            降重后的文本
        """
        if techniques is None:
            techniques = [
                "synonym_replace",
                "change_voice",
                "restructure_sentence",
                "expand_paragraph"
            ]

        result = text

        # 根据强度选择技巧数量
        num_techniques = int(len(techniques) * intensity)
        selected_techniques = techniques[:num_techniques]

        print(f"🔄 降重强度: {int(intensity*100)}%")
        print(f"📝 使用技巧: {', '.join(selected_techniques)}")

        # 依次应用技巧
        for technique in selected_techniques:
            if technique == "synonym_replace":
                result = self.synonym_replace(result)
            elif technique == "change_voice":
                result = self.change_voice(result)
            elif technique == "restructure_sentence":
                result = self.restructure_sentence(result)
            elif technique == "expand_paragraph":
                result = self.expand_paragraph(result, expansion_factor=1.5)
            elif technique == "add_examples":
                result = self.add_examples(result)
            elif technique == "restructure_logic":
                result = self.restructure_logic(result)

        return result

    def check_similarity(self, text1: str, text2: str) -> float:
        """检查相似度（简单实现）"""
        # 简单的词向量相似度
        words1 = set(text1.split())
        words2 = set(text2.split())

        intersection = words1 & words2
        union = words1 | words2

        similarity = len(intersection) / len(union) if union else 0
        return similarity


def main():
    """测试"""
    reducer = PlagiarismReducer()

    # 测试文本
    original = "人工智能技术在医疗领域有着广泛的应用。通过深度学习算法，可以实现对医学影像的准确分析。研究表明，这一技术在早期疾病诊断方面具有很大潜力。"

    print("原文:")
    print(original)
    print()

    # 综合降重
    rewritten = reducer.reduce_all(original, intensity=0.7)
    print("降重后:")
    print(rewritten)
    print()


if __name__ == "__main__":
    main()
