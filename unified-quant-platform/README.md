# unified_quant_platform - 统一量化交易平台

**项目名称**：统一量化交易平台
**版本**：v5.0 Dual-Env
**完成度**：75% + 双环境架构

---

## 项目描述

统一的量化交易平台，支持双环境（测试/正式）部署，提供完整的股票分析、信号生成、回测和实时监控功能。

---

## 功能特性

### 核心功能
1. **双环境支持**
   - 测试环境：快速迭代，调试模式
   - 正式环境：稳定可靠，生产模式
   - 环境隔离：数据库、缓存、日志完全分开

2. **数据源管理**
   - 5个数据源：Local, AKShare, Efinance, Tushare, Baostock
   - 自动故障切换
   - 冷却机制

3. **信号系统**
   - NTDF信号系统（v2，7种信号类型）
   - Quant Trading 8因子信号（v2，完整版）
   - 信号融合引擎（v2，资金流向+技术形态）

4. **分析功能**
   - 单股票分析
   - 市场扫描
   - AI智能选股
   - 市场环境分析
   - 资金流向分析
   - 技术形态识别

5. **交易功能**
   - 回测系统
   - 实时监控系统
   - 信号推送

6. **报告功能**
   - 图表生成器
   - PDF导出
   - 飞书文档导出

---

## 技术栈

### 后端
- Python 3.11
- Flask（Web框架）
- pandas, numpy（数据处理）
- matplotlib（图表生成）
- MySQL（数据库）
- Redis（缓存）

### 前端
- Vue 3.0
- Element Plus
- Pinia（状态管理）
- Axios（HTTP客户端）

### 数据库
- MySQL 8.0（关系型数据库）
- Redis 7.x（缓存）

---

## 项目结构

```
unified-quant-platform/
├── app/                          # 应用代码
│   ├── __init__.py
│   ├── config.py                 # 配置管理器
│   ├── routes/
│   │   ├── api.py
│   │   └── analysis.py
│   └── services/
│       ├── analyzer.py
│       └── scanner.py
├── config/                       # 配置文件
│   ├── config_test.yaml
│   ├── config_prod.yaml
│   └── config.py
├── data/                         # 数据目录
│   ├── test/
│   │   ├── cache/
│   │   ├── logs/
│   │   └── temp/
│   └── prod/
│       ├── cache/
│       ├── logs/
│       └── temp/
├── database/                     # 数据库脚本
│   ├── db_test.sql
│   └── db_prod.sql
├── logs/                         # 运行日志
│   ├── test.log
│   └── prod.log
└── main.py                       # 主入口
```

---

## 安装说明

### 1. 环境准备
```bash
# 创建虚拟环境
python3.11 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据库初始化
```bash
# 初始化测试数据库
mysql -u root -p < database/db_test.sql

# 初始化正式数据库
mysql -u root -p < database/db_prod.sql
```

### 3. 启动服务
```bash
# 启动测试环境
python main.py --env=test

# 启动正式环境
python main.py --env=prod
```

---

## 使用说明

### API 接口

#### 测试环境
- 基础URL: http://localhost:5000
- 健康检查: GET http://localhost:5000/api/test
- 分析接口: POST http://localhost:5000/api/analyze
- 扫描接口: POST http://localhost:5000/api/scan

#### 正式环境
- 基础URL: http://localhost:8000
- 健康检查: GET http://localhost:8000/api/analyze
- 分析接口: POST http://localhost:8000/api/analyze
- 扫描接口: POST http://localhost:8000/api/scan

---

## 配置说明

### 环境变量
```bash
# 设置环境
export APP_ENV=test  # 或 prod

# 或使用命令行参数
python main.py --env=prod
```

### 配置文件
- 测试环境: `config/config_test.yaml`
- 正式环境: `config/config_prod.yaml`

---

## 日志说明

### 测试环境日志
- 位置: `data/test/logs/test.log`
- 级别: DEBUG
- 内容: 详细的调试信息

### 正式环境日志
- 位置: `data/prod/logs/prod.log`
- 级别: INFO
- 内容: 生产运行日志

---

## 开发说明

### 代码规范
- 遵循 PEP 8 规范
- 使用类型注解
- 编写单元测试
- 添加文档注释

### 版本控制
- 使用 Git 进行版本控制
- 主分支: `main`
- 开发分支: `develop`

---

## 部署说明

### 测试环境部署
1. 更新代码到测试环境
2. 切换到测试环境配置
3. 重启服务
4. 验证功能

### 正式环境部署
1. 更新代码到正式环境
2. 切换到正式环境配置
3. 备份现有数据
4. 重启服务
5. 验证功能

---

## 文档说明

### 项目文档
- 系统架构: `dual-env-arch-design.md`
- API 文档: `docs/api.md`
- 部署文档: `docs/deployment.md`

---

## 许可证

MIT License

---

## 联系方式

- 项目负责人: 变形金刚（AI 总经理）
- 审核: 卞安青（公司董事长）
- 邮箱: marketing@ntdf.com
- 飞书: https://feishu.cn/docx/Yv1ndJWuHoWdOixajIPc7qSUn5c

---

**版本**: v5.0 Dual-Env
**最后更新**: 2026-03-01
**状态**: 开发中（75% 完成）
