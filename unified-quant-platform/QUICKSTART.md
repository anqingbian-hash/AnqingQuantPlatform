# OpenClaw 统一量化交易平台 v5.0 - 快速开始指南

## 快速开始

### 1. 环境要求

- Python 3.11+
- Flask 3.0.0
- SQLite 3
- 依赖包：见 requirements.txt

### 2. 安装依赖

```bash
cd /root/.openclaw/workspace/unified-quant-platform
pip install -r requirements.txt
```

### 3. 配置环境

编辑配置文件：

```bash
# 测试环境
vi config/config_test.yaml

# 生产环境
vi config/config_prod.yaml
```

### 4. 启动服务器

```bash
# 测试环境（端口 5000）
python3 run_server.py test

# 生产环境（端口 8000）
python3 run_server.py prod
```

### 5. 访问应用

- 测试环境: http://localhost:5000
- 生产环境: http://localhost:8000
- 健康检查: http://localhost:5000/health

---

## API 使用

### 用户登录

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

响应：
```json
{
  "success": true,
  "message": "登录成功",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@ntdf.com",
    "role": "admin"
  }
}
```

### 实时分析

```bash
curl http://localhost:5000/api/analysis/realtime/600000
```

响应：
```json
{
  "success": true,
  "data": {
    "code": "600000",
    "name": "浦发银行",
    "price": 10.50,
    "change": 0.05,
    "indicators": {...},
    "signals": {...}
  }
}
```

### 市场分析

```bash
curl http://localhost:5000/api/analysis/market
```

### PDF 导出

```bash
curl -X POST http://localhost:5000/api/export/pdf \
  -H "Content-Type: application/json" \
  -d '{"type":"basic"}' \
  --output report.pdf
```

---

## 默认账户

### 管理员账户

- **用户名**: admin
- **密码**: admin123
- **权限**: 完整权限

**⚠️ 重要提示**: 首次登录后请立即修改密码！

---

## 功能特性

### 1. 双环境支持

- **测试环境**: 端口 5000，数据库 `quant_test.db`
- **生产环境**: 端口 8000，数据库 `quant_prod.db`
- **完全隔离**: 两个环境互不影响

### 2. 用户认证系统

- **注册功能**: 用户名、邮箱、密码
- **登录功能**: 用户名/密码登录，返回 JWT token
- **Token 验证**: API 请求需要携带 Bearer token
- **密码安全**: 使用 Werkzeug 密码哈希

### 3. 实时分析系统

- **实时市场分析**: 实时价格、技术指标、交易信号
- **筹码分布分析**: 价格区间分布、筹码集中度
- **市场综合分析**: 市场状态、涨跌统计、龙头榜

### 4. 导出功能

- **PDF 导出**: 分析报告导出为 PDF 文件
- **飞书导出**: 分析报告导出为飞书文档（Markdown 格式）

---

## API 文档

### 基础 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 首页 |
| GET | `/health` | 健康检查 |

### 认证 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 用户登录 |
| GET | `/api/auth/me` | 获取当前用户 |
| GET | `/api/users` | 用户列表 |
| GET | `/api/users/<id>` | 获取单个用户 |

### 实时分析 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/analysis/realtime/<code>` | 实时分析 |
| GET | `/api/analysis/chip/<code>` | 筹码分布分析 |
| GET | `/api/analysis/market` | 市场综合分析 |

### 导出 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/export/pdf` | 导出 PDF |
| POST | `/api/export/feishu` | 导出飞书文档 |

---

## 技术支持

### 问题反馈

如有问题，请联系：

- **邮箱**: support@ntdf.com
- **文档**: https://docs.openclaw.ai
- **社区**: https://discord.com/invite/clawd

### 版本信息

- **当前版本**: v5.0.0
- **发布日期**: 2026-03-01
- **Python 版本**: 3.11+

---

**快速开始指南** | OpenClaw 统一量化交易平台 v5.0
