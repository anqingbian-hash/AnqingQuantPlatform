#!/usr/bin/env python3
"""
PDF全文提取工具
"""

import PyPDF2

PDF_PATH = "/root/.openclaw/media/inbound/NTDF_数字净量分析教程_零基础小白快速上手---05bfea30-6690-4f89-bbd6-3acba048c712.pdf"
OUTPUT_PATH = "/root/.openclaw/workspace/NTDF_数字净量分析教程_完整文本.txt"

def extract_full_text():
    """提取全部内容"""
    print("开始提取PDF全文...")

    try:
        with open(PDF_PATH, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            print(f"PDF总页数: {len(reader.pages)}")

            full_text = []

            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text = page.extract_text()
                full_text.append(f"\n{'='*80}\n")
                full_text.append(f"第 {page_num + 1} 页\n")
                full_text.append(f"{'='*80}\n")
                full_text.append(text)

            # 保存到文件
            with open(OUTPUT_PATH, 'w', encoding='utf-8') as out:
                out.writelines(full_text)

            print(f"\n✅ 成功提取全部内容并保存到: {OUTPUT_PATH}")
            print(f"总字符数: {sum(len(text) for text in full_text)}")

            return ''.join(full_text)

    except Exception as e:
        print(f"错误: {e}")
        return None

if __name__ == "__main__":
    extract_full_text()
