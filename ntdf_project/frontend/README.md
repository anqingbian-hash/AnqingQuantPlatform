# NTDF 数字净量分析决策系统 - 前端

## 项目说明

**项目名称：** NTDF 数字净量分析决策系统
**版本：** MVP（Phase 1）
**开发阶段：** 方案D（简化功能，快速上线）

## 技术栈

- **框架：** Vue 3 + TypeScript + Vite
- **图表库：** ECharts 5.x
- **HTTP客户端：** Axios
- **路由：** Vue Router
- **状态管理：** Pinia

## 项目结构

```
ntdf_frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── assets/
│   ├── components/
│   │   ├── charts/
│   │   │   ├── CandlestickChart.vue  # K线图
│   │   │   ├── VolumeChart.vue       # 成交量图
│   │   │   ├── DeltaChart.vue        # Delta柱状图
│   │   │   └── SRChart.vue           # SR支撑压力图
│   │   ├── layout/
│   │   │   ├── Header.vue           # 顶部导航
│   │   │   ├── Sidebar.vue          # 侧边栏
│   │   │   └── Content.vue          # 主内容区
│   │   ├── views/
│   │   │   ├── Dashboard.vue        # 仪表盘
│   │   │   ├── Analysis.vue          # 分析页面
│   │   │   └── Settings.vue          # 设置页面
│   │   ├── api/
│   │   │   └── index.ts            # API接口
│   │   ├── stores/
│   │   │   └── market.ts           # 市场数据存储
│   │   ├── types/
│   │   │   ├── market.ts           # 市场数据类型
│   │   │   └── signal.ts           # 信号类型
│   │   ├── App.vue
│   │   └── main.ts
│   ├── index.html
│   └── vite.config.ts
├── package.json
└── README.md
```

## 核心功能（MVP版本）

### 1. K线图
- 支持日K、周K、月K、分钟K
- 价格显示：开盘价、最高价、最低价、收盘价
- 成交量显示
- 支持缩放、平移
- 支持十字光标

### 2. SR支撑压力图（方案D核心）
- 自动识别波峰波谷
- 自动绘制支撑线（绿色）
- 自动绘制压力线（红色）
- 黄金率位显示（68%、32%）
- 支持调整窗口大小

### 3. 信号识别（方案D简化版）
- 价格突破信号
- 价格跌破信号
- 顶背离标记
- 底背离标记
- 信号统计

### 4. 数据面板
- 实时价格显示
- 24小时涨跌幅
- 24小时成交量
- 当前趋势状态

## 开发计划

### 第1周：项目搭建

**Day 1-2:**
- [x] 创建Vue 3项目
- [x] 安装依赖
- [ ] 创建组件框架
- [ ] 设置路由

**Day 3-4:**
- [ ] 创建布局组件
- [ ] 创建图表组件基础
- [ ] 集成ECharts
- [ ] 创建API接口

**Day 5-7:**
- [ ] 实现K线图
- [ ] 实现SR支撑压力图
- [ ] 实现数据面板
- [ ] 实现实时数据更新

### 第2周：功能完善

**Day 8-10:**
- [ ] 实现信号识别
- [ ] 实现数据存储
- [ ] 实现历史数据查询
- [ ] 实现数据导出

**Day 11-14:**
- [ ] 优化图表性能
- [ ] 优化用户体验
- [ ] 添加帮助文档
- [ ] 测试所有功能

### 第3周：部署上线

**Day 15-17:**
- [ ] 打包前端项目
- [ ] 部署到服务器
- [ ] 配置Nginx
- [ ] 测试线上访问

**Day 18-21:**
- [ ] 修复Bug
- [ ] 优化性能
- [ ] 编写用户手册
- [ ] 准备发布

## API接口说明

### 获取市场数据

```
GET /api/market/alpha_vantage/quote?symbol=AAPL
GET /api/market/alpha_vantage/daily?symbol=AAPL
GET /api/market/alpha_vantage/intraday?symbol=AAPL&interval=1min
GET /api/market/yahoo/quote?symbol=AAPL
GET /api/market/yahoo/daily?symbol=AAPL&period=1mo
GET /api/market/yahoo/intraday?symbol=AAPL&period=5d
```

### 获取技术指标

```
GET /api/indicators/sma?symbol=AAPL&period=20
GET /api/indicators/ema?symbol=AAPL&period=20
GET /api/indicators/rsi?symbol=AAPL&period=14
```

### 获取SR支撑压力位

```
GET /api/technical/sr?symbol=AAPL
```

### 系统状态

```
GET /api/health
```

## 开发命令

```bash
# 安装依赖
npm install

# 开发模式
npm run dev

# 构建
npm run build

# 预览
npm run preview
```

## 部署说明

```bash
# 构建
npm run build

# 上传到服务器
scp -r dist/* ubuntu@122.51.142.248:/var/www/ntdf/frontend/

# 重启Nginx
sudo systemctl restart nginx
```

## 访问地址

**本地开发：** http://localhost:5173
**线上环境：** http://122.51.142.248

## API后端地址

**开发环境：** http://localhost:8000
**生产环境：** http://122.51.142.248:8000

## 技术支持

**后端开发：** 变形金刚（总经理）
**服务器：** 腾讯云 122.51.142.248
**文档：** http://122.51.142.248:8000/docs

## 版本历史

### v1.0.0 (2026-02-22)
- MVP版本
- K线图
- SR支撑压力图
- 数据面板
- 基础功能
