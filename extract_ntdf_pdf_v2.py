#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NTDF数字净量分析教程PDF文本提取脚本v2
处理Type3字体嵌入的PDF
"""

import sys
from PyPDF2 import PdfReader
from typing import List

def extract_pdf_text_v2(pdf_path: str) -> dict:
    """
    提取PDF文件的文本内容（v2版本，处理Type3字体嵌入）
    返回包含：
    - success: 是否成功提取
    - text: 提取的文本内容
    - pages: 提取的页数
    - chars: 提取的字符数
    - error: 错误信息（如果有）
    """
    result = {
        "success": False,
        "text": "",
        "pages": 0,
        "chars": 0,
        "error": ""
    }
    
    try:
        # 尝试读取PDF文件
        reader = PdfReader(pdf_path)
        print(f"PDF文件总页数: {len(reader.pages)}")
        
        # 尝试逐页提取文本
        full_text = ""
        for page_num, page in enumerate(reader.pages, 1):
            try:
                page = reader.pages[page_num]
                extracted = page.extract_text()
                print(f"第{page_num+1}页提取: {len(extracted)}字符")
                full_text += extracted + "\n\n"
            except Exception as e:
                    print(f"第{page_num+1}页提取失败: {e}")
        
        if full_text.strip():
            result["success"] = True
            result["text"] = full_text
            result["pages"] = len(reader.pages)
            result["chars"] = len(full_text)
            
        print(f"\n成功提取!")
            print(f"总字符数: {result['chars']}")
            print(f"\n文本预览（前1000字符）:")
            print(full_text[:1000])
            
    except Exception as e:
        result["error"] = f"提取失败: {e}"
        return result

if __name__ == "__main__":
    pdf_path = "/root/.openclaw/media/inbound/NTDF_数字净量分析教程_零基础小白快速上手---d1550c50-956c-4f967aadece04ba60ddd.pdf"
    output = extract_pdf_text_v2(pdf_path)
    
    print(f"\n{'='='*}")
    print(f"开始提取...")
    output = extract_pdf_text_v2(pdf_path)
    
    print(f"\n提取结果:")
    print(f"成功: {output['success']}")
    print(f"页数: {output['pages']}")
    print(f"字符数: {output['chars']}")
    if output['text']:
        print(f"\n完整文本预览（前800字符）:")
        print(output['text'][:800])
        if len(output['text']) > 800:
            print(f"...（共{len(output['text'])}字符）")
    if output['error']:
        print(f"\n错误: {output['error']}")
