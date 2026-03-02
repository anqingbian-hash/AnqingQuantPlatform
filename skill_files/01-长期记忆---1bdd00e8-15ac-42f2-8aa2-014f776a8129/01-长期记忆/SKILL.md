---
name: "ai-memory"
version: "1.0.0"
description: "安全的本地记忆系统，帮助AI助手记住重要信息"
author: "AI Skills Team"
tags: ["记忆", "存储", "AI", "SQLite"]
requires: []
---

# AI长期记忆技能

安全的本地记忆系统，帮助AI助手记住重要信息。

## 技能描述

本技能提供一个本地SQLite存储的记忆系统，支持语义搜索、标签分类和自动去重。所有数据完全存储在本地，保护隐私安全。

## 使用场景

- 用户说："记住我喜欢用Python编程" → 存储用户偏好
- 用户问："我之前说过什么？" → 搜索相关记忆
- 用户说："总结你记住的信息" → 展示最近记忆
- 用户说："我有什么偏好？" → 根据标签筛选

## 工具和依赖

### 工具列表

- `scripts/ai_memory.py`：核心记忆模块

### API密钥

无

### 外部依赖

- Python 3.7+
- SQLite3（Python内置）
- sentence-transformers（可选，用于语义搜索）

## 配置说明

### 环境变量

```bash
# 可选：语义搜索模型
pip install sentence-transformers
```

### 数据存储位置

默认：`~/.ai_memory.db`

## 使用示例

### 基本用法

```python
from ai_memory import AIMemory

# 创建记忆实例
memory = AIMemory()

# 添加记忆
memory.add("用户偏好使用Python编程", tags=["编程", "偏好"])

# 搜索记忆
results = memory.search("Python")

# 查看最近记忆
recent = memory.get_recent()

# 统计信息
stats = memory.get_stats()
```

### 场景1：存储用户偏好

用户："记住我喜欢用Python编程"

AI：
```python
memory.add("用户偏好使用Python编程", tags=["编程", "偏好"])
# ✅ 已记住：用户喜欢Python编程
```

### 场景2：搜索记忆

用户："我之前说过什么关于编程的？"

AI：
```python
results = memory.search("编程")
# 找到: "用户偏好使用Python编程"
```

### 场景3：查看记忆统计

用户："你记住了多少信息？"

AI：
```python
stats = memory.get_stats()
# 总共15条记忆，涉及编程、工作、偏好等标签
```

## 故障排除

### 问题1：语义搜索不可用

**现象**：搜索功能受限

**解决**：
```bash
pip install sentence-transformers
```

### 问题2：数据库文件损坏

**现象**：无法读取记忆

**解决**：
```bash
rm ~/.ai_memory.db
# 重启程序自动创建新数据库
```

### 问题3：重复记忆

**现象**：相同内容被多次存储

**解决**：系统会自动检测并去重，无需手动处理

## 注意事项

1. **隐私安全**：所有数据存储在本地，不经过云端
2. **备份建议**：定期备份 `~/.ai_memory.db` 文件
3. **模型下载**：首次使用语义搜索会下载模型（约100MB）
4. **降级使用**：不安装 sentence-transformers 仍可使用基础功能
