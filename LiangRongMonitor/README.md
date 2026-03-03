# LiangRongMonitor - 两融额度监控系统

## 项目说明

本工作空间专门用于：
- 两融额度实时监控
- 两融数据趋势预判
- 风险控制预警
- 数据可视化分析

## 目录结构

```
LiangRongMonitor/
├── README.md              # 项目说明
├── data/                  # 数据文件目录
│   ├── margin_raw.csv      # 两融原始数据
│   ├── margin_processed.csv # 两融处理后数据
│   └── alerts.csv         # 风险预警记录
├── output/                # 输出文件目录
│   ├── reports/           # 分析报告
│   └── predictions/       # 预测结果
├── charts/                # 图表目录
│   ├── margin_trend.png   # 两融趋势图
│   └── risk_alert.png     # 风险预警图
├── logs/                  # 日志目录
│   ├── monitor.log        # 监控日志
│   └── alerts.log        # 预警日志
└── config/                # 配置目录
    ├── monitor.yaml       # 监控配置
    └── thresholds.yaml   # 风险阈值配置
```

## 功能模块

1. **数据采集**
   - 实时获取两融数据
   - 数据清洗和验证
   - 数据存储管理

2. **趋势分析**
   - 移动平均线分析
   - 趋势识别算法
   - 波动率计算

3. **风险预警**
   - 异常检测
   - 阈值报警
   - 预警推送

4. **可视化**
   - 两融趋势图
   - 风险预警图
   - 统计报表

## 使用方法

### 启动监控
```bash
python3 monitor.py
```

### 查看报告
```bash
python3 generate_report.py
```

### 配置监控
编辑 `config/monitor.yaml`

## 联系方式

- 负责人：卞安青（卞董）
- 创建时间：2026-03-03
- 版本：v1.0
