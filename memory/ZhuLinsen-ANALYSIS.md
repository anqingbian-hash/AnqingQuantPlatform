# ZhuLinsen/daily_stock_analysis 项目分析

## 项目信息

**仓库地址：** https://github.com/ZhuLinsen/daily_stock_analysis
**项目名称：** ZhuLinsen/daily_stock_analysis - 每日智能分析器
**项目类型：** LLM驱动的A股/港股/美股智能分析系统

## 核心功能

### 🤖 AI智能分析
- 多维度市场分析
- 决策仪表盘推荐
- 情绪分析
- AI模型推荐（支持Claude、DeepSeek、通义千问等）

### 📊 数据来源
- A股：AkShare、Tushare、腾讯财经
- 港股：腾讯财经
- 美股：Alpha Vantage
- 新闻：百度搜索、财新、新浪、财联社

### 🎯 交易功能
- 基本面分析
- 技术指标分析
- 买卖信号识别
- 风险提示
- 筹码管理

### 📮 推送渠道
- 微信（企业微信）
- 飞书
- Telegram
- 邮箱
- 钉钉
- Server酱

## 技术栈

### 前端技术
- React 18
- Vite 5
- TailwindCSS 3.4
- shadcn/ui（类似Material-UI）
- shadcn/charts（图表库）
- Lucide React（图标）
- Zustand（状态管理）

### 后端技术
- Python 3.10+
- FastAPI 0.100+
- SQLAlchemy 2.0
- PostgreSQL 15+
- Alembic（数据库迁移）
- Uvicorn（ASGI服务器）

### AI模型支持
- Anthropic Claude（主要）
- Google Gemini
- OpenAI GPT-4
- DeepSeek V3
- 通义千问
- Ollama（本地模型）

### 部署方式
1. GitHub Actions（推荐，免费）
2. Docker部署
3. 本地运行

## 数据库模型

### 市场数据（market_data）
- id（主键）
- symbol（股票代码）
- date（日期）
- date_timestamp（时间戳）
- open_price（开盘价）
- high_price（最高价）
- low_price（最低价）
- close_price（收盘价）
- volume（成交量）
- created_at（创建时间）

### 交易信号（trading_signals）
- id（主键）
- symbol（股票代码）
- signal_type（信号类型：breakout/reversal/volume_spike）
- signal_price（信号价格）
- delta_value（Delta值）
- timestamp（时间戳）
- is_active（是否活跃）
- created_at（创建时间）

### 系统配置（system_config）
- id（主键）
- key（配置键）
- value（配置值）
- updated_at（更新时间）

### 用户（users）
- id（主键）
- username（用户名）
- email（邮箱）
- hashed_password（加密密码）
- created_at（创建时间）
- is_active（是否活跃）

## API接口设计

### 健康检查
- GET /health - 系统健康状态

### 市场数据
- GET /api/market/{source}/quote - 获取实时报价
- GET /api/market/{source}/daily - 获取日线数据
- GET /api/market/{source}/history - 获取历史数据

### 技术指标
- GET /api/indicators/sma - SMA指标
- GET /api/indicators/ema - EMA指标
- GET /api/indicators/rsi - RSI指标
- GET /api/indicators/macd - MACD指标
- GET /api/indicators/kdj - KDJ指标

### 交易信号
- POST /api/signals/breakout - 突破信号
- POST /api/signals/reversal - 反转信号
- POST /api/signals/volume_spike - 转量信号
- GET /api/signals/list - 信号列表

### 数据管理
- POST /api/data/market - 存储市场数据
- GET /api/data/history - 查询历史数据
- DELETE /api/data/{id} - 删除数据

### 用户管理
- POST /api/user/register - 用户注册
- POST /api/user/login - 用户登录
- GET /api/user/profile - 用户信息
- PUT /api/user/profile - 更新用户信息

### 配置管理
- GET /api/config - 获取配置
- PUT /api/config - 更新配置
- DELETE /api/config/{key} - 删除配置

## 部署配置

### GitHub Actions（推荐）
- 零成本
- 自动运行
- 定时触发（每个工作日18:00）

### Docker部署
```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/ntdf
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=ntdf
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
```

### 本地运行
```bash
# 克隆项目
git clone https://github.com/ZhuLinsen/daily_stock_analysis.git
cd daily_stock_analysis

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
vim .env

# 运行分析
python main.py
```

## 与NTDF项目的对比

### 相同点
- 都是基于AI的股票分析系统
- 都提供AI决策建议
- 都支持A股/港股/美股
- 都有推送功能
- 都使用FastAPI + React/Vue架构

### 不同点
- ZhuLinsen：更成熟，代码更完整，功能更丰富
- NTDF：更专注于Delta净量分析，技术指标更精准

### 可借鉴的设计
1. 数据库模型设计
2. API接口设计
3. 前端UI设计
4. 推送配置方式
5. AI模型集成方式

## 推荐借鉴方案

### 1. 数据库模型
直接参考ZhuLinsen的4张核心表：
- market_data
- trading_signals
- system_config
- users

### 2. API接口设计
参考RESTful API设计规范：
- 统一前缀：/api/
- 资源命名：复数形式
- HTTP方法：GET/POST/PUT/DELETE

### 3. 前端UI设计
参考shadcn/ui组件库：
- 响应式设计
- 现代化界面
- 清晰的信息层次

### 4. 推送配置
参考多渠道推送设计：
- 企业微信
- 飞书
- Telegram
- 邮箱

### 5. AI模型集成
参考灵活的模型配置：
- 支持多个AI模型
- 可配置API Key
- 可切换模型

## 保持NTDF特色

### 1. Delta净量计算
保持NTDF的核心特色：
- Delta净量算法
- 波峰波谷识别
- 黄金率位计算

### 2. SR支撑压力
保持技术分析特色：
- 自动识别SR High
- 自动识别SR Low
- 黄金率位（68%、32%）

### 3. 交易信号模型
保持信号系统特色：
- 突破信号
- 反转信号
- 转量信号

## 下一步行动

1. 学习ZhuLinsen的数据库模型
2. 参考API接口设计
3. 借鉴前端UI组件
4. 学习推送配置方式
5. 集成AI模型功能
