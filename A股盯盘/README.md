# OpenClaw A股盯盘系统 - 最终方案

## 📊 项目概述

**项目名称**：A股盯盘系统
**创建时间**：2026-03-02 23:30
**项目位置**：/root/.openclaw/workspace/A股盯盘/
**状态**：已创建

---

## 📋 功能设计

### 核心模块
1. **Planner（规划员）**
   - 每天9:00规划全天盯盘任务
   - 选择目标股票池
   - 制定监控策略

2. **Monitor（监控员）**
   - 每5分钟刷新全A股行情
   - 监控涨幅>5%的股票
   - 监控成交额>5000万的股票
   - 检测异常交易异动

3. **Analyzer（分析师）**
   - 分析K线趋势
   - 分析板块资金流向
   - 分析技术形态
   - 生成异动原因

4. **Pusher（推送员）**
   - 格式化Telegram/微信推送消息
   - 包含：股票代码、价格、涨幅、成交量、异动原因
   - 支持定时推送（9:00、15:30、15:35）

### 数据源
- **主数据源**：akshare（AkShare金融数据接口）
- **备用数据源**：tushare（Tushare真实数据）
- **模拟数据**：MockStockAPI（测试使用）

---

## 🎯 Agent架构

### Planner（规划员）- 角色：策略规划
```python
class Planner:
    def plan_daily_tasks():
        - 从量化平台选股池选择目标
        - 生成每日盯盘列表
        - 设置监控阈值（涨幅、成交额）
        - 输出配置文件给Monitor
```

### Monitor（监控员）- 角色：实时监控
```python
class Monitor:
    def refresh_all_stocks():
        - 调用akshare获取全A股行情
        - 过滤异动股票
        - 检测异动原因
        - 发送告警给Pusher
    
    def check_thresholds(stocks, thresholds):
        - 检查涨幅>5%
        - 检查成交额>5000万
        - 生成告警列表
```

### Analyzer（分析师）- 角色：技术分析
```python
class Analyzer:
    def analyze_alert(alert):
        - 分析K线形态
        - 分析板块资金流向
        - 判断异动类型：放量上涨/缩量上涨/主力拉升
        - 生成异动原因分析
```

### Pusher（推送员） - 角色：消息推送
```python
class Pusher:
    def send_telegram(alert):
        - 发送Telegram消息到指定频道
        - 格式化：股票代码 + 详情
    
    def send_wechat(alert):
        - 发送微信消息
        - 发送到用户微信号
        - 支持markdown格式
```

---

## 📁 配置文件

### config.yaml
```yaml
# 监控配置
monitor:
  enabled: true
  interval_minutes: 5
  channels:
    - telegram: ""
    wechat: ""

  filters:
    rise_threshold: 5.0  # 涨幅>5%
    volume_ratio: 1.5  # 量比>1.5
    amount_threshold: 5000000  # 成交额>5000万

# 推送配置
push:
  enabled: true
  daily_summary: true
  daily_time: "15:30"

# 数据源配置
data_sources:
  primary: akshare
  backup: tushare
  akshare_token: ""  # 如有可填入
  tushare_token: "8b159caa2bbf554707c20c3f44fea1e0e6ec75b6afc82c78fa47e47b"
```

# 风险控制
risk:
  max_daily_trades: 5      # 每日最大交易次数
  max_single_loss: -0.1      # 单只股票最大亏损率
  max_position_size: 100000    # 单只股票最大持仓

# 通知级别
notification:
  levels:
    high:
      trigger: "涨幅>7%且量比>2.0"
      channels: ["telegram", "wechat"]
      urgency: "立即关注"
    medium:
      trigger: "涨幅>5%且成交额>1000万"
      channels: ["telegram", "wechat"]
      urgency: "保持关注"
    low:
      trigger: "涨幅>3%或跌幅>5%"
      channels: ["telegram", "wechat"]
      urgency: "一般关注"

# 工作流配置
workflow:
  start_time: "09:00"      # 早盘开始时间
  monitor_start: "09:05"   # 监控开始
  analysis_time: "09:15"   # 分析时间
  push_time: "15:30"     # 尾盘总结
  end_time: "15:00"       # 收盘时间

# Agent配置
agents:
  planner:
    model: "gpt-4o"
    role: "经验丰富的A股分析师"
    task: "每天9:00规划盯盘任务，监控异动股票"
  
  monitor:
    model: "gpt-4o"
    role: "实时监控员，每5分钟刷新A股行情"
    task: "监控异动、筛选目标股票、检测交易异动"
  
  analyzer:
    model: "gpt-4o"
    role: "技术分析师，分析K线、板块、资金流向"
    task: "分析异动原因，判断主力行为"
  
  pusher:
    model: "gpt-4o"
    role: "推送员，格式化消息推送"
    task: "发送Telegram/微信推送"

# 技能启用
skills:
  quant-trading: true
  web-access: true
  auto-iteration: true
  ai-memory: true
```

---

## 📁 工作流程

### 每天9:00
```
Planner启动
  ↓
1. 查看量化平台选股池
2. 选择目标股票（10-20只）
3. 监控阈值设置
4. 输出：target_stocks.yaml
  ↓
```

### 每天9:05-15
```
Monitor启动
  ↓
1. 每5分钟刷新全A股行情
2. 实时监控异动
3. 记录交易异动
  ↓
```

### 每天15:30
```
Analyzer启动
  ↓
1. 收集全天异动数据
2. 分析K线、板块、资金流向
3. 生成异动原因
4. 输出：daily_analysis.json
  ↓
```

### 每天15:35
```
Pusher启动
  ↓
1. 汇总全天异动
2. 格式化推送消息
3. 发送到指定频道
4. 发送尾盘总结
  ↓
```

### 每天15:00
```
Planner更新
  ↓
1. 分析全天异动模式
2. 更新选股池
3. 调整监控策略
4. 输出：next_targets.yaml
 ↓
```

---

## 🚀 快速启动

```bash
# 1. 创建目录
cd /root/.openclaw/workspace/A股盯盘

# 2. 创建配置文件
cat > config.yaml << 'EOF'
monitor:
  enabled: true
  interval_minutes: 5
  channels:
    telegram: ""
    wechat: ""
  filters:
    rise_threshold: 5.0
    volume_ratio: 1.5
    amount_threshold: 5000000
push:
  enabled: true
  daily_summary: true
  daily_time: "15:30"
data_sources:
  primary: akshare
  backup: tushare
  tushare_token: "8b159caa2bbf554707c20c3f44fea1e0e6ec75b6afc82c78fa47e47e47b"
agents:
  planner:
    model: "gpt-4o"
    role: "经验丰富的A股分析师"
  task: "每天9:00规划盯盘任务"
  monitor:
    model: "gpt4o"
    role: "实时监控员，每5分钟刷新A股行情"
  task: "监控异动、筛选目标股票、检测交易异动"
  analyzer:
    model: "gpt4o"
    role: "技术分析师，分析K线、板块、资金流向"
    task: "分析异动原因，判断主力行为"
  pusher:
    model: "gpt4o"
    role: "推送员，格式化消息推送"
    task: "发送Telegram/微信推送"
  skills:
  quant-trading: true
  web-access: true
  auto-iteration: true
  ai-memory: true
risk:
    max_daily_trades: 5
  max_single_loss: -0.1
  max_position_size: 100000
  notification:
    levels:
      high:
        trigger: "涨幅>7%且量比>2.0"
        channels: ["telegram", "wechat"]
        urgency: "立即关注"
      medium:
        trigger: "涨幅>5%且成交额>1000万"
        channels: ["telegram", "wechat"]
        urgency: "保持关注"
      low:
        trigger: "涨幅>3%或跌幅>5%"
        channels: ["telegram", "wechat"]
        urgency: "一般关注"
workflow:
  start_time: "09:00"
  monitor_start: "09:05"
  analysis_time: "09:15"
  push_time: "15:30"
  end_time: "15:00"
EOF

# 3. 创建启动脚本
cat > start_monitor.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A股盯盘启动脚本"""

import json
from pathlib import Path

def main():
    print("=== A股盯盘启动 ===")
    
    # 加载配置
    config_file = Path("config.yaml")
    if not config_file.exists():
        print("❌ 配置文件不存在，创建中...")
        config = {
            "monitor": {
                "enabled": True,
                "interval_minutes": 5,
                "filters": {
                    "rise_threshold": 5.0,
                    "volume_ratio": 1.5,
                    "amount_threshold": 5000000
                }
            },
            "data_sources": {
                "primary": "akshare",
                "backup": "tushare",
                "tushare_token": "8b159caa2bbf554707c20c3f44fea1e0e6ec75b6afc82c78fa47e47e47b"
            }
        }
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print("✅ 配置文件已创建")
    else:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("✅ 配置文件已加载")
    
    print("✅ A股盯盘系统启动完成！")
    print("等待9:00开始全天盯盘任务...")

if __name__ == '__main__':
    main()
EOF

# 4. 创建测试脚本
cat > test_monitor.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A股盯盘测试脚本"""

from mock_agent import MockStockAPI

def main():
    print("=== A股盯盘测试 ===")
    
    api = MockStockAPI()
    
    # 测试3只股票
    test_symbols = ['600519', '000001', '000002']
    
    print("监控股票：")
    for sym in test_symbols:
        stock = api.get_stock_realtime(sym)
        print(f"  {sym} 价格: {stock['price']}  涨幅: {stock['change_percent']} 量比: {stock['volume']/10000:.2f}万手")
    
    print("=== 测试完成 ===")
    print("❓模拟数据，待集成akshare真实数据")

if __name__ == '__main__':
    main()
EOF

# 5. 运行
echo "✅ 文件已创建" && python3 test_monitor.py
EOF

chmod +x start_monitor.py test_monitor.py
python3 start_monitor.py
