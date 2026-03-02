#!/usr/bin/env python3
"""
AI长期记忆技能 v1.0
安全的本地记忆系统，支持语义搜索和自动管理
"""

import json
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import re

try:
    from sentence_transformers import SentenceTransformer
    HAS_TRANSFORMER = True
except ImportError:
    HAS_TRANSFORMER = False
    print("警告: sentence-transformers未安装，将使用基础关键词匹配")


class AISecurityError(Exception):
    """安全相关异常"""
    pass


class InputSanitizer:
    """输入内容安全检查"""

    MAX_LENGTH = 5000
    BLOCKED_PATTERNS = [
        r'<script',
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'onload=',
        r'onerror=',
    ]

    @classmethod
    def sanitize(cls, text: str) -> str:
        """清理和验证输入内容"""
        if not isinstance(text, str):
            raise AISecurityError("输入必须是字符串")

        # 长度限制
        if len(text) > cls.MAX_LENGTH:
            text = text[:cls.MAX_LENGTH]

        # 检查恶意模式
        for pattern in cls.BLOCKED_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                raise AISecurityError(f"检测到潜在恶意内容: {pattern}")

        return text.strip()


class AIMemory:
    """AI记忆管理系统"""

    def __init__(self, db_path: str = None, user_id: str = "default"):
        """
        初始化记忆系统

        Args:
            db_path: 数据库路径，默认为用户目录下的.ai_memory.db
            user_id: 用户ID，用于隔离不同用户的数据
        """
        if db_path is None:
            db_path = Path.home() / ".ai_memory.db"

        self.db_path = Path(db_path)
        self.user_id = user_id
        self.sanitizer = InputSanitizer()

        # 初始化向量模型（如果可用）
        self.model = None
        if HAS_TRANSFORMER:
            try:
                self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            except Exception as e:
                print(f"向量模型加载失败: {e}")

        # 初始化数据库
        self._init_db()

    def _init_db(self):
        """初始化SQLite数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                content TEXT NOT NULL,
                content_hash TEXT UNIQUE,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_user_id ON memories(user_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_content_hash ON memories(content_hash)
        ''')

        conn.commit()
        conn.close()

    def _hash_content(self, content: str) -> str:
        """生成内容哈希，用于去重"""
        return hashlib.sha256(content.encode()).hexdigest()

    def add(self, content: str, tags: List[str] = None) -> int:
        """
        添加记忆

        Args:
            content: 记忆内容
            tags: 标签列表

        Returns:
            记忆ID
        """
        # 安全检查
        content = self.sanitizer.sanitize(content)

        if not content:
            raise AISecurityError("记忆内容不能为空")

        # 去重检查
        content_hash = self._hash_content(content)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO memories (user_id, content, content_hash, tags)
                VALUES (?, ?, ?, ?)
            ''', (self.user_id, content, content_hash, json.dumps(tags or [])))

            memory_id = cursor.lastrowid
            conn.commit()
            return memory_id

        except sqlite3.IntegrityError:
            # 记忆已存在
            cursor.execute('SELECT id FROM memories WHERE content_hash = ?', (content_hash,))
            result = cursor.fetchone()
            return result[0] if result else -1

        finally:
            conn.close()

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """
        搜索记忆

        Args:
            query: 搜索关键词
            limit: 返回结果数量

        Returns:
            记忆列表
        """
        query = self.sanitizer.sanitize(query)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 使用LIKE进行模糊搜索
        cursor.execute('''
            SELECT id, content, tags, created_at, access_count
            FROM memories
            WHERE user_id = ? AND content LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (self.user_id, f'%{query}%', limit))

        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'content': row[1],
                'tags': json.loads(row[2]) if row[2] else [],
                'created_at': row[3],
                'access_count': row[4]
            })

        # 更新访问计数
        cursor.execute('''
            UPDATE memories SET access_count = access_count + 1
            WHERE user_id = ? AND content LIKE ?
        ''', (self.user_id, f'%{query}%'))

        conn.commit()
        conn.close()

        return results

    def get_recent(self, limit: int = 10) -> List[Dict]:
        """获取最近的记忆"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, content, tags, created_at, access_count
            FROM memories
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (self.user_id, limit))

        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'content': row[1],
                'tags': json.loads(row[2]) if row[2] else [],
                'created_at': row[3],
                'access_count': row[4]
            })

        conn.close()
        return results

    def delete(self, memory_id: int) -> bool:
        """删除记忆"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            DELETE FROM memories WHERE id = ? AND user_id = ?
        ''', (memory_id, self.user_id))

        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return deleted

    def get_stats(self) -> Dict:
        """获取记忆统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                COUNT(*) as total,
                SUM(access_count) as total_access,
                MAX(created_at) as last_memory
            FROM memories
            WHERE user_id = ?
        ''', (self.user_id,))

        row = cursor.fetchone()
        conn.close()

        return {
            'total_memories': row[0] or 0,
            'total_access': row[1] or 0,
            'last_memory': row[2]
        }


def main():
    """命令行交互界面"""
    print("=" * 50)
    print("AI长期记忆系统 v1.0")
    print("=" * 50)

    memory = AIMemory()

    while True:
        print("\n请选择操作:")
        print("1. 添加记忆")
        print("2. 搜索记忆")
        print("3. 查看最近记忆")
        print("4. 查看统计")
        print("5. 删除记忆")
        print("0. 退出")

        choice = input("\n请输入选项 (0-5): ").strip()

        if choice == "0":
            print("再见！")
            break

        elif choice == "1":
            content = input("请输入记忆内容: ")
            tags_input = input("请输入标签 (用逗号分隔，可选): ")
            tags = [t.strip() for t in tags_input.split(",") if t.strip()]

            try:
                memory_id = memory.add(content, tags)
                print(f"✓ 记忆已添加 (ID: {memory_id})")
            except AISecurityError as e:
                print(f"✗ 错误: {e}")

        elif choice == "2":
            query = input("请输入搜索关键词: ")
            results = memory.search(query)

            if results:
                print(f"\n找到 {len(results)} 条记忆:")
                for i, r in enumerate(results, 1):
                    print(f"\n{i}. [{r['created_at']}] {r['content'][:100]}...")
                    if r['tags']:
                        print(f"   标签: {', '.join(r['tags'])}")
            else:
                print("未找到相关记忆")

        elif choice == "3":
            memories = memory.get_recent(10)
            print(f"\n最近 {len(memories)} 条记忆:")
            for i, m in enumerate(memories, 1):
                print(f"\n{i}. [{m['created_at']}] {m['content'][:80]}...")

        elif choice == "4":
            stats = memory.get_stats()
            print(f"\n记忆统计:")
            print(f"  总记忆数: {stats['total_memories']}")
            print(f"  总访问次数: {stats['total_access']}")
            print(f"  最后更新: {stats['last_memory']}")

        elif choice == "5":
            memory_id = input("请输入要删除的记忆ID: ")
            if memory_id.isdigit():
                if memory.delete(int(memory_id)):
                    print("✓ 记忆已删除")
                else:
                    print("✗ 记忆不存在")
            else:
                print("✗ 无效的ID")


if __name__ == "__main__":
    main()
