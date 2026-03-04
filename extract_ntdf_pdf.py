#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NTDF数字净量分析教程PDF文本提取脚本
提取Type3字体嵌入的PDF
"""

import sys
from PyPDF2 import PdfReader
from typing import List

def extract_pdf_text(pdf_path: str) -> dict:
    """
    提取PDF文件的文本内容
    返回包含:
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
        # 打开PDF文件
        reader = PdfReader(pdf_path)
        if reader.is_encrypted:
            print(f"PDF文件已加密，无法直接提取文本")
            result["error"] = "PDF文件已加密，无法直接提取文本"
            return result
        
        # 尝试提取文本
        text = ""
        for page in reader.pages:
            try:
                extracted_text = page.extract_text()
                if extracted_text.strip():
                    text += extracted_text + "\n\n"
                print(f"第{page+1}页提取成功")
            except Exception as e:
                print(f"第{page+1}页提取失败: {e}")
        
        if text.strip():
            result["success"] = True
            result["text"] = text
            result["pages"] = len(reader.pages)
            result["chars"] = len(text)
        
    except Exception as e:
        result["error"] = f"提取失败: {e}"
    
    return result

if __name__ == "__main__":
    pdf_path = "/root/.openclaw/media/inbound/NTDF_数字净量分析教程_零基础小白快速上手---d1550c50-956c-4f967aadece04ba60ddd.pdf"
    output = extract_pdf_text(pdf_path)
    
    print(f"\n{'='='*}")
    print(f"提取结果:")
    print(f"成功: {output['success']}")
    print(f"页数: {output['pages']}")
    print(f"字符数: {output['chars']}")
    if output['text']:
        print(f"\n文本预览（前500字符）:")
        print(output['text'][:500])
    if len(output['text']) > 500:
            print(f"...（共{len(output['text'])}字符）")
    if output['error']:
        print(f"\n错误: {output['error']}")
