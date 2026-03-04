#!/usr/bin/env python3
"""
PDF文本提取工具
支持多种方法提取PDF内容
"""

import PyPDF2
import pdfplumber
import os

PDF_PATH = "/root/.openclaw/media/inbound/NTDF_数字净量分析教程_零基础小白快速上手---05bfea30-6690-4f89-bbd6-3acba048c712.pdf"

def method1_pypdf2():
    """方法1: PyPDF2提取"""
    print("=" * 60)
    print("方法1: 使用PyPDF2提取")
    print("=" * 60)

    try:
        with open(PDF_PATH, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            print(f"PDF页数: {len(reader.pages)}")

            for page_num in range(min(len(reader.pages), 5)):  # 只提取前5页
                page = reader.pages[page_num]
                text = page.extract_text()
                print(f"\n--- 第 {page_num + 1} 页 ---")
                if text.strip():
                    print(text[:500])  # 每页只显示前500字符
                else:
                    print("此页面没有可提取的文本（可能是图片）")

    except Exception as e:
        print(f"错误: {e}")

def method2_pdfplumber():
    """方法2: pdfplumber提取"""
    print("\n" + "=" * 60)
    print("方法2: 使用pdfplumber提取")
    print("=" * 60)

    try:
        with pdfplumber.open(PDF_PATH) as pdf:
            print(f"PDF页数: {len(pdf.pages)}")

            for page_num in range(min(len(pdf.pages), 5)):  # 只提取前5页
                page = pdf.pages[page_num]
                text = page.extract_text()
                print(f"\n--- 第 {page_num + 1} 页 ---")
                if text and text.strip():
                    print(text[:500])  # 每页只显示前500字符
                else:
                    print("此页面没有可提取的文本（可能是图片）")

    except Exception as e:
        print(f"错误: {e}")

def main():
    if not os.path.exists(PDF_PATH):
        print(f"错误: PDF文件不存在: {PDF_PATH}")
        return

    # 尝试两种方法
    method1_pypdf2()
    method2_pdfplumber()

    print("\n" + "=" * 60)
    print("总结")
    print("=" * 60)
    print("如果两种方法都无法提取文本，说明PDF使用了特殊的嵌入字体")
    print("（如Type3字体），文字以图片形式存储，需要OCR或Vision LLM处理。")

if __name__ == "__main__":
    main()
