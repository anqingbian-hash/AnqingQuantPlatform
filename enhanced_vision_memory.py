#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强图片识别与记忆技能
"""
import base64
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import os
import re

class EnhancedVisionMemory:
    """增强的视觉记忆系统"""
    
    def __init__(self, memory_file: str = 'vision_memory.json'):
        self.memory_file = memory_file
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict[str, Any]:
        """加载记忆"""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'images': [],
            'texts': [],
            'stocks': [],
            'context': []
        }
    
    def _save_memory(self):
        """保存记忆"""
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)
    
    def remember_image(self, image_data: str, description: str, 
                    ocr_result: str, tags: List[str] = None):
        """
        记住图片
        
        Args:
            image_data: 图片数据（base64或文件路径）
            description: 图片描述
            ocr_result: OCR识别结果
            tags: 标签
        """
        memory_item = {
            'timestamp': datetime.now().isoformat(),
            'image_type': self._detect_image_type(image_data),
            'description': description,
            'ocr_result': ocr_result,
            'tags': tags or [],
            'content': ocr_result  # 主要内容
        }
        
        self.memory['images'].append(memory_item)
        self._save_memory()
        
        print(f"[记忆] 已保存图片记忆:")
        print(f"  类型: {memory_item['image_type']}")
        print(f"  OCR结果: {ocr_result[:100]}...")
        print(f"  标签: {', '.join(tags or [])}")
        
        return memory_item
    
    def remember_text(self, text: str, source: str = 'chat', 
                   context: Dict[str, Any] = None):
        """
        记住文本
        
        Args:
            text: 文本内容
            source: 来源
            context: 上下文信息
        """
        memory_item = {
            'timestamp': datetime.now().isoformat(),
            'text': text,
            'source': source,
            'context': context or {}
        }
        
        self.memory['texts'].append(memory_item)
        self._save_memory()
        
        print(f"[记忆] 已保存文本记忆:")
        print(f"  来源: {source}")
        print(f"  内容: {text[:100]}...")
        
        return memory_item
    
    def search_images(self, query: str) -> List[Dict[str, Any]]:
        """搜索图片记忆"""
        results = []
        query_lower = query.lower()
        
        for item in self.memory['images']:
            # 搜索OCR结果
            if query_lower in item['ocr_result'].lower():
                results.append(item)
                continue
            
            # 搜索标签
            if any(query_lower in tag.lower() for tag in item.get('tags', [])):
                results.append(item)
                continue
            
            # 搜索描述
            if query_lower in item['description'].lower():
                results.append(item)
        
        return results
    
    def search_texts(self, query: str) -> List[Dict[str, Any]]:
        """搜索文本记忆"""
        results = []
        query_lower = query.lower()
        
        for item in self.memory['texts']:
            if query_lower in item['text'].lower():
                results.append(item)
        
        return results
    
    def get_recent_images(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的图片记忆"""
        return sorted(self.memory['images'], 
                   key=lambda x: x['timestamp'], 
                   reverse=True)[:limit]
    
    def get_recent_texts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的文本记忆"""
        return sorted(self.memory['texts'], 
                   key=lambda x: x['timestamp'], 
                   reverse=True)[:limit]
    
    def _detect_image_type(self, image_data: str) -> str:
        """检测图片类型"""
        image_data_lower = image_data.lower()
        
        # K线图检测
        if any(keyword in image_data_lower for keyword in 
               ['kline', 'candlestick', 'k线', '蜡烛图', '分时图']):
            return 'K线图'
        
        # 股票代码检测
        if any(keyword in image_data_lower for keyword in 
               ['股票代码', 'stock code', '代码', '600', '000', '300', '688']):
            return '股票代码'
        
        # 表格数据检测
        if any(keyword in image_data_lower for keyword in 
               ['table', '表格', '数据', 'data', '列表']):
            return '表格数据'
        
        # 截图检测
        if image_data_lower.startswith('data:image'):
            return '图片截图'
        
        # 文件路径
        if image_data_lower.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
            return '图片文件'
        
        return '未知类型'


# 增强的OCR识别器
class EnhancedOCR:
    """增强的OCR识别器"""
    
    def __init__(self):
        self.vision_ai = None  # 初始化Vision AI
        
        # 股票代码正则表达式
        import re
        self.stock_code_patterns = [
            re.compile(r'[06]\d{5}\.[S|Z]{2}'),  # 沪深代码
            re.compile(r'[0-9]{6}'),  # 纯数字
            re.compile(r'(SH|SZ|sh|sz)\d{6}'),  # 带交易所
        ]
    
    def extract_stock_codes(self, text: str) -> List[str]:
        """从文本中提取股票代码"""
        codes = set()
        
        # 使用正则匹配
        for pattern in self.stock_code_patterns:
            matches = pattern.findall(text)
            for match in matches:
                codes.add(match)
        
        # 常见股票代码格式
        import re
        for match in re.findall(r'\b(600|000|300|688|002)\d{3}\b', text):
            codes.add(match)
        
        return list(codes)
    
    def extract_numbers(self, text: str) -> List[float]:
        """从文本中提取数字"""
        import re
        
        # 提取整数和小数
        numbers = re.findall(r'\d+\.?\d*', text)
        result = []
        
        for num in numbers:
            try:
                result.append(float(num))
            except:
                pass
        
        return result
    
    def extract_table_data(self, text: str) -> List[Dict[str, Any]]:
        """从文本中提取表格数据"""
        # 简单的表格数据提取
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        data = []
        
        for line in lines:
            # 按空格或制表符分割
            columns = re.split(r'[\t\s]+', line)
            if len(columns) > 1:
                data.append({
                    'raw': line,
                    'columns': columns
                })
        
        return data
    
    def enhanced_ocr(self, image_data: str) -> Dict[str, Any]:
        """
        增强的OCR识别
        
        Args:
            image_data: 图片数据
            
        Returns:
            识别结果字典
        """
        result = {
            'text': '',
            'confidence': 0.0,
            'stock_codes': [],
            'numbers': [],
            'tables': [],
            'type': 'unknown'
        }
        
        # 检测图片类型
        image_type = self._detect_image_type(image_data)
        result['type'] = image_type
        
        # 这里调用实际的OCR API
        # 由于当前环境限制，返回模拟结果
        if image_type == '股票代码':
            result['stock_codes'] = self.extract_stock_codes(image_data)
        elif image_type == '表格数据':
            result['tables'] = self.extract_table_data(image_data)
        elif image_type == 'K线图':
            result['type'] = 'K线图'
            result['text'] = 'K线图表'
        
        return result
    
    def _detect_image_type(self, image_data: str) -> str:
        """检测图片类型"""
        image_data_lower = image_data.lower()
        
        # K线图
        if any(kw in image_data_lower for kw in 
               ['kline', 'k线', '蜡烛图', '分时图', '行情图']):
            return 'K线图'
        
        # 股票代码
        if any(kw in image_data_lower for kw in 
               ['股票代码', 'code', '代码', '600', '000', '300', '688']):
            return '股票代码'
        
        # 表格
        if any(kw in image_data_lower for kw in 
               ['table', '表格', '数据', 'data', '列表']):
            return '表格数据'
        
        # 截图
        if image_data_lower.startswith('data:image'):
            return '图片截图'
        
        return '未知类型'


# 测试
if __name__ == '__main__':
    print("="*80)
    print("📸 增强图片识别与记忆技能")
    print("="*80)
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 初始化
    memory_system = EnhancedVisionMemory()
    ocr_system = EnhancedOCR()
    
    # 测试1：模拟图片识别
    print("\n测试1: 图片识别")
    print("-"*60)
    
    test_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg..."
    test_ocr = "600519.SH 茅台 1648.50 -1.23%"
    
    ocr_result = ocr_system.enhanced_ocr(test_image)
    print(f"OCR识别结果:")
    print(f"  类型: {ocr_result['type']}")
    print(f"  文本: {ocr_result['text']}")
    print(f"  股票代码: {ocr_result['stock_codes']}")
    print(f"  数字: {ocr_result['numbers']}")
    
    # 测试2：保存记忆
    print("\n测试2: 保存图片记忆")
    print("-"*60)
    
    memory_item = memory_system.remember_image(
        image_data=test_image,
        description='股票代码测试图片',
        ocr_result=test_ocr,
        tags=['股票代码', '茅台', '行情']
    )
    
    # 测试3：保存文本记忆
    print("\n测试3: 保存文本记忆")
    print("-"*60)
    
    memory_system.remember_text(
        text='卞董要求优化图片识别和记忆技能',
        source='user_request',
        context={'priority': 'high', 'task': 'vision_memory'}
    )
    
    # 测试4：搜索记忆
    print("\n测试4: 搜索记忆")
    print("-"*60)
    
    images = memory_system.search_images('茅台')
    print(f"搜索'茅台'找到 {len(images)} 个图片记忆:")
    for img in images[:3]:
        print(f"  - {img['timestamp']}: {img['description']}")
    
    texts = memory_system.search_texts('优化')
    print(f"搜索'优化'找到 {len(texts)} 个文本记忆:")
    for txt in texts[:3]:
        print(f"  - {txt['timestamp']}: {txt['text'][:50]}...")
    
    # 测试5：获取最近记忆
    print("\n测试5: 获取最近记忆")
    print("-"*60)
    
    recent_images = memory_system.get_recent_images(5)
    print(f"最近5个图片记忆:")
    for img in recent_images:
        print(f"  - {img['timestamp']}: {img['description']}")
    
    recent_texts = memory_system.get_recent_texts(5)
    print(f"最近5个文本记忆:")
    for txt in recent_texts:
        print(f"  - {txt['timestamp']}: {txt['text'][:50]}...")
    
    print("\n" + "="*80)
    print("✅ 测试完成")
    print("="*80)
