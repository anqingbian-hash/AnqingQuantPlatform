# 统一量化交易平台 - 双环境架构设计

**设计时间**：2026-03-01 16:08
**执行人**：变形金刚（AI 总经理）

---

## 🎯 设计目标

### 核心需求
1. **双环境支持**：测试环境和正式环境同时运行
2. **环境隔离**：两个环境完全独立，互不影响
3. **配置管理**：独立配置文件，便于管理
4. **数据隔离**：数据库、缓存、日志完全分开
5. **统一代码**：同一套代码支持两个环境

---

## 🏗 系统架构

### 目录结构
```
/unified-quant-platform/
├── app/                          # 应用代码（统一）
│   ├── __init__.py
│   ├── config.py                 # 配置管理器
│   ├── database.py               # 数据库连接管理
│   └── ...
├── config/                       # 配置文件
│   ├── config_test.yaml          # 测试环境配置
│   ├── config_prod.yaml          # 正式环境配置
│   └── config.py                # 配置加载器
├── data/                         # 数据目录（环境隔离）
│   ├── test/                    # 测试环境数据
│   │   ├── cache/                # 测试环境缓存
│   │   ├── logs/                 # 测试环境日志
│   │   └── temp/                # 测试环境临时文件
│   └── prod/                   # 正式环境数据
│       ├── cache/                # 正式环境缓存
│       ├── logs/                 # 正式环境日志
│       └── temp/                # 正式环境临时文件
├── database/                     # 数据库配置
│   ├── db_test.sql              # 测试环境数据库
│   └── db_prod.sql              # 正式环境数据库
├── logs/                         # 运行日志
│   ├── test.log                 # 测试环境日志
│   └── prod.log                # 正式环境日志
├── tests/                        # 测试脚本
│   ├── test_env.py              # 环境切换测试
│   └── integration_test.py       # 集成测试
└── main.py                       # 主入口（支持环境参数）
```

---

## 🔧 配置管理

### config/config.py
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理器
支持双环境配置
"""

import os
import yaml
from typing import Dict, Any

class ConfigManager:
    """配置管理器"""

    def __init__(self, env: str = "test"):
        """
        初始化配置管理器

        Args:
            env: 环境名称（test/prod）
        """
        self.env = env
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        config_file = f"config/config_{self.env}.yaml"

        if not os.path.exists(config_file):
            raise FileNotFoundError(f"配置文件不存在: {config_file}")

        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value if value is not None else default

    def get_database_url(self) -> str:
        """获取数据库连接"""
        return self.get('database.url')

    def get_database_name(self) -> str:
        """获取数据库名称"""
        return self.get('database.name')

    def get_cache_dir(self) -> str:
        """获取缓存目录"""
        return self.get('cache.dir')

    def get_log_dir(self) -> str:
        """获取日志目录"""
        return self.get('logs.dir')

    def get_temp_dir(self) -> str:
        """获取临时文件目录"""
        return self.get('temp.dir')

    def get_debug_mode(self) -> bool:
        """获取调试模式"""
        return self.get('debug.enabled', False)

# 创建单例
_config_manager = None

def get_config(env: str = None) -> ConfigManager:
    """获取配置管理器单例"""
    global _config_manager

    if _config_manager is None:
        # 从环境变量读取环境
        env = env or os.getenv('APP_ENV', 'test')
        _config_manager = ConfigManager(env)

    return _config_manager
```

---

## 📄 配置文件

### config/config_test.yaml
```yaml
# 测试环境配置

# 环境标识
environment: test

# 数据库配置
database:
  type: mysql
  host: localhost
  port: 3306
  user: test_user
  password: test_password
  name: quant_test
  charset: utf8mb4

# 缓存配置
cache:
  type: redis
  host: localhost
  port: 6379
  db: 0
  password: null
  dir: data/test/cache

# 日志配置
logs:
  dir: data/test/logs
  level: DEBUG
  format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# 临时文件配置
temp:
  dir: data/test/temp

# API 配置
api:
  host: 0.0.0.0
  port: 5000
  debug: true

# 数据源配置
data_sources:
  akshare:
    enabled: true
  timeout: 30
  retry_count: 3

  efinance:
    enabled: true
    timeout: 30
    retry_count: 3

  tushare:
    enabled: false
    token: null

  baostock:
    enabled: true
    timeout: 30

# 邮件通知配置
email:
  enabled: true
  smtp_server: smtp.qq.com
  smtp_port: 587
  sender: test@ntdf.com
  password: test_password

# 调试配置
debug:
  enabled: true
  verbose: true
  sql_logging: true
```

### config/config_prod.yaml
```yaml
# 正式环境配置

# 环境标识
environment: prod

# 数据库配置
database:
  type: mysql
  host: 127.0.0.1
  port: 3306
  user: prod_user
  password: prod_password
  name: quant_prod
  charset: utf8mb4

# 缓存配置
cache:
  type: redis
  host: 127.0.0.1
  port: 6379
  db: 0
  password: prod_redis_password
  dir: data/prod/cache

# 日志配置
logs:
  dir: data/prod/logs
  level: INFO
  format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# 临时文件配置
temp:
  dir: data/prod/temp

# API 配置
api:
  host: 0.0.0.0
  port: 8000
  debug: false

# 数据源配置
data_sources:
  akshare:
    enabled: true
    timeout: 30
    retry_count: 5

  efinance:
    enabled: true
    timeout: 30
    retry_count: 5

  tushare:
    enabled: true
    token: your_tushare_token

  baostock:
    enabled: true
    timeout: 30

# 邮件通知配置
email:
  enabled: true
  smtp_server: smtp.qq.com
  smtp_port: 587
  sender: prod@ntdf.com
  password: prod_password

# 调试配置
debug:
  enabled: false
  verbose: false
  sql_logging: false
```

---

## 🗄 数据库设计

### database/db_test.sql
```sql
-- 测试环境数据库
CREATE DATABASE IF NOT EXISTS quant_test
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE quant_test;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 股票自选表
CREATE TABLE IF NOT EXISTS watchlists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    stocks TEXT NOT NULL COMMENT 'JSON格式的股票列表',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 分析任务表
CREATE TABLE IF NOT EXISTS analysis_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    stock_code VARCHAR(20) NOT NULL,
    task_type VARCHAR(50) NOT NULL,
    status ENUM('pending', 'running', 'completed', 'failed') DEFAULT 'pending',
    result TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 测试数据
INSERT INTO users (username, email, password_hash, role) VALUES
    ('test_admin', 'admin@ntdf.com', MD5('admin123'), 'admin'),
    ('test_user', 'user@ntdf.com', MD5('user123'), 'user');
```

### database/db_prod.sql
```sql
-- 正式环境数据库
CREATE DATABASE IF NOT EXISTS quant_prod
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE quant_prod;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 股票自选表
CREATE TABLE IF NOT EXISTS watchlists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    stocks TEXT NOT NULL COMMENT 'JSON格式的股票列表',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 分析任务表
CREATE TABLE IF NOT EXISTS analysis_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    stock_code VARCHAR(20) NOT NULL,
    task_type VARCHAR(50) NOT NULL,
    status ENUM('pending', 'running', 'completed', 'failed') DEFAULT 'pending',
    result TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 索引优化
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_watchlists_user_id ON watchlists(user_id);
CREATE INDEX idx_analysis_tasks_user_id ON analysis_tasks(user_id);
CREATE INDEX idx_analysis_tasks_status ON analysis_tasks(status);
```

---

## 🚀 部署脚本

### deploy_test.sh
```bash
#!/bin/bash
# 测试环境部署脚本

echo "🚀 开始部署测试环境..."

# 停止运行中的服务
echo "⏹️ 停止服务..."
systemctl stop quant-trading-test || true

# 创建数据目录
echo "📁 创建数据目录..."
mkdir -p data/test/cache
mkdir -p data/test/logs
mkdir -p data/test/temp

# 初始化数据库
echo "🗄 初始化数据库..."
mysql -u root -p < database/db_test.sql

# 安装依赖
echo "📦 安装依赖..."
pip install -r requirements.txt

# 启动服务
echo "▶️ 启动服务..."
systemctl start quant-trading-test

echo "✅ 测试环境部署完成！"
echo "服务地址: http://localhost:5000"
echo "日志路径: data/test/logs/"
```

### deploy_prod.sh
```bash
#!/bin/bash
# 正式环境部署脚本

echo "🚀 开始部署正式环境..."

# 停止运行中的服务
echo "⏹️ 停止服务..."
systemctl stop quant-trading-prod || true

# 创建数据目录
echo "📁 创建数据目录..."
mkdir -p data/prod/cache
mkdir -p data/prod/logs
mkdir -p data/prod/temp

# 初始化数据库
echo "🗄 初始化数据库..."
mysql -u root -p < database/db_prod.sql

# 安装依赖
echo "📦 安装依赖..."
pip install -r requirements.txt

# 启动服务
echo "▶️ 启动服务..."
systemctl start quant-trading-prod

echo "✅ 正式环境部署完成！"
echo "服务地址: http://localhost:8000"
echo "日志路径: data/prod/logs/"
```

---

## 🎯 使用方法

### 启动测试环境
```bash
# 方法1：使用环境变量
export APP_ENV=test
python main.py

# 方法2：使用命令行参数
python main.py --env=test

# 方法3：使用部署脚本
bash deploy_test.sh
```

### 启动正式环境
```bash
# 方法1：使用环境变量
export APP_ENV=prod
python main.py

# 方法2：使用命令行参数
python main.py --env=prod

# 方法3：使用部署脚本
bash deploy_prod.sh
```

### 查看日志
```bash
# 测试环境日志
tail -f logs/test.log

# 正式环境日志
tail -f logs/prod.log
```

---

## 🔒 环境隔离机制

### 完全隔离
1. **数据库**：test/prod 两个独立数据库
2. **缓存**：Redis 使用不同的 DB 索引
3. **日志**：独立的日志文件
4. **临时文件**：独立的临时目录
5. **配置**：独立的配置文件

### 安全措施
1. **正式环境关闭调试模式**
2. **正式环境使用生产密码**
3. **正式环境不输出敏感信息**
4. **定期备份正式环境数据**

---

## 📋 实施清单

### 阶段1：基础架构（1天）
- [ ] 创建目录结构
- [ ] 创建配置管理器
- [ ] 创建配置文件
- [ ] 创建数据库脚本

### 阶段2：数据库初始化（0.5天）
- [ ] 初始化测试数据库
- [ ] 初始化正式数据库
- [ ] 创建测试数据

### 阶段3：部署脚本（0.5天）
- [ ] 创建测试环境部署脚本
- [ ] 创建正式环境部署脚本
- [ ] 测试部署脚本

### 阶段4：系统测试（1天）
- [ ] 测试环境切换
- [ ] 测试数据隔离
- [ ] 测试日志隔离
- [ ] 测试配置加载

### 阶段5：文档完善（0.5天）
- [ ] 创建部署文档
- [ ] 创建使用文档
- [ ] 创建故障排除文档

---

## 🎯 预期效果

### 功能完整性
1. ✅ 支持测试环境和正式环境
2. ✅ 环境完全隔离
3. ✅ 配置统一管理
4. ✅ 部署自动化

### 系统稳定性
1. ✅ 正式环境稳定可靠
2. ✅ 测试环境灵活可调试
3. ✅ 环境切换简单快速
4. ✅ 数据安全隔离

---

**设计人**：变形金刚（AI 总经理）
**审核人**：卞安青（公司董事长）
**日期**：2026-03-01 16:08
**状态**：设计完成，待实施
