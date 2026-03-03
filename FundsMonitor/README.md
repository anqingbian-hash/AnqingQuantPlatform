# FundsMonitor - 资金监控工作空间

## 项目说明
本工作空间专门用于所有资金监控相关任务，隔离记忆，避免干扰其他空间。

## 目录结构

```
FundsMonitor/
├── README.md              # 项目说明
├── data/                  # 数据文件目录
│   ├── margin/            # 两融数据
│   ├── north/              # 北向资金
│   ├── south/              # 南向资金
│   ├── institutional/      # 机构资金
│   ├── lhb/                # 龙虎榜
│   ├── blocks/             # 大宗交易
│   └── stock_flow/         # 个股资金流
├── output/                # 输出文件目录
│   ├── reports/           # 分析报告
│   ├── predictions/       # 预测结果
│   └── alerts/            # 警报列表
├── charts/                # 图表目录
│   ├── margin/            # 两融图表
│   ├── funds/             # 资金流向图表
│   └── stocks/            # 个股图表
├── logs/                  # 日志目录
│   ├── monitor.log        # 监控日志
│   └── alerts.log         # 警报日志
├── config/                # 配置目录
│   ├── monitor.yaml       # 监控配置
│   └── thresholds.yaml   # 风险阈值配置
├── modules/                # 模块目录
│   ├── margin_monitor.py  # 两融监控模块
│   ├── north_south.py    # 南北向资金模块
│   ├── institutional.py   # 机构资金模块
│   ├── lhb_monitor.py     # 龙虎榜监控模块
│   ├── blocks_monitor.py  # 大宗交易模块
│   └── stock_flow.py      # 个股资金流模块
└── alerts/                # 警报目录
    ├── margin_alerts.txt # 两融警报
    ├── funds_alerts.txt   # 资金流向警报
    └── risk_warnings.txt  # 风险预警
```

## 功能模块

### 1. 两融监控（Margin Monitor）
- 两融余额监控
- 融资融券分析
- 变化率预警
- 历史趋势分析

### 2. 南北向资金（North/South Funds）
- 北向资金流入流出
- 南向资金流入流出
- 跨市场资金分析
- 行业资金流向

### 3. 机构资金（Institutional Funds）
- 机构买卖盘分析
- 机构席位追踪
- 机构调研数据
- 机构持仓变化

### 4. 龙虎榜（Dragon & Tiger List）
- 龙虎榜每日更新
- 热点个股分析
- 机构席位识别
- 榜单个股追踪

### 5. 大宗交易（Block Trades）
- 大宗交易数据
- 折溢价率分析
- 买卖席位分析
- 重要交易提醒

### 6. 个股资金流（Stock Flow）
- 个股资金流入流出
- 主力资金分析
- 散户资金分析
- 持仓变化追踪

## 风险控制

### 两融风控
- 融资余额变化率 > 15%：高风险，建议减仓
- 融资余额变化率 < -5%：资金流出，注意风险
- 市场融资变化率 < -5%：全局警报，杠杆去化

### 资金流向风控
- 北向资金大幅流出：市场风险
- 南向资金大幅流入：市场机会
- 机构资金持续流出：谨慎
- 主力资金持续流入：机会

## 使用方法

### 启动监控
```bash
cd /root/.openclaw/workspace/FundsMonitor
python3 run_all_monitors.py
```

### 查看报告
```bash
cd /root/.openclaw/workspace/FundsMonitor
python3 generate_report.py
```

### 配置监控
编辑配置文件：
- `config/monitor.yaml` - 监控配置
- `config/thresholds.yaml` - 风险阈值

## 联系方式

- 负责人：卞安青（卞董）
- 创建时间：2026-03-03
- 版本：v1.0
