---
name: "redbook-publish"
version: "1.0.0"
description: "自动发布内容到小红书，支持图文/视频发布、搜索笔记、评论互动等功能"
author: "white0dew"
tags: ["小红书", "发布", "自动化", "CDP", "社交媒体"]
requires: ["Python 3.10+", "Google Chrome"]
---

# 小红书发布技能

自动发布内容到小红书（Xiaohongshu/RED）的命令行工具，支持图文/视频发布、内容搜索、评论互动等功能。

## 技能描述

通过 Chrome DevTools Protocol (CDP) 实现自动化发布，支持多账号管理、无头模式运行、自动搜索素材与内容数据抓取等功能。

## 使用场景

- 用户要求"发布内容到小红书" → 进入发布流程
- 用户提供 `标题 + 正文 + 图片/视频` → 直接发布
- 用户要求"启动浏览器/检查登录/仅测试不发布" → 测试浏览器流程
- 用户要求"搜索笔记/找内容/查看笔记详情" → 内容检索流程
- 用户要求"给帖子评论" → 评论发布流程
- 用户要求"查看内容数据表" → 数据抓取流程

## 工具和依赖

### 工具列表

- `scripts/chrome_launcher.py`：Chrome 浏览器管理（启动/重启/关闭）
- `scripts/cdp_publish.py`：CDP 自动化与账号命令
- `scripts/publish_pipeline.py`：统一发布入口
- `scripts/image_downloader.py`：图片下载工具
- `scripts/account_manager.py`：账号管理模块
- `scripts/feed_explorer.py`：内容检索模块

### API密钥

无

### 外部依赖

- Python 3.10+
- Google Chrome 浏览器
- 依赖包见 requirements.txt

## 配置说明

### 安装依赖

```bash
pip install -r requirements.txt
```

### 多账号配置

基于 `config/accounts.json.example` 复制为 `config/accounts.json` 后配置。

## 使用示例

### 1) 启动/测试浏览器（不发布）

```bash
# 启动测试浏览器（有窗口，推荐）
python scripts/chrome_launcher.py

# 无头启动测试浏览器
python scripts/chrome_launcher.py --headless

# 检查当前登录状态
python scripts/cdp_publish.py check-login

# 重启测试浏览器
python scripts/chrome_launcher.py --restart

# 关闭测试浏览器
python scripts/chrome_launcher.py --kill
```

### 2) 首次登录

```bash
python scripts/cdp_publish.py login
```

### 3) 图文发布

```bash
# 使用图片 URL（无头模式）
python scripts/publish_pipeline.py --headless \
  --title-file title.txt \
  --content-file content.txt \
  --image-urls "URL1" "URL2"

# 使用本地图片（有窗口模式）
python scripts/publish_pipeline.py \
  --title-file title.txt \
  --content-file content.txt \
  --images "/abs/path/pic1.jpg" "/abs/path/pic2.jpg"
```

### 4) 视频发布

```bash
# 本地视频文件
python scripts/publish_pipeline.py --headless \
  --title-file title.txt \
  --content-file content.txt \
  --video "/abs/path/video.mp4"

# 视频 URL
python scripts/publish_pipeline.py --headless \
  --title-file title.txt \
  --content-file content.txt \
  --video-url "https://example.com/video.mp4"
```

### 5) 搜索内容与笔记详情

```bash
# 搜索笔记
python scripts/cdp_publish.py search-feeds --keyword "春招"

# 带筛选搜索
python scripts/cdp_publish.py search-feeds --keyword "春招" --sort-by 最新 --note-type 图文

# 获取笔记详情
python scripts/cdp_publish.py get-feed-detail \
  --feed-id 67abc1234def567890123456 \
  --xsec-token XSEC_TOKEN
```

### 6) 发表评论

```bash
python scripts/cdp_publish.py post-comment-to-feed \
  --feed-id 67abc1234def567890123456 \
  --xsec-token XSEC_TOKEN \
  --content "写得很实用，感谢分享"
```

### 7) 获取内容数据表

```bash
# 抓取笔记基础信息数据
python scripts/cdp_publish.py content-data

# 导出 CSV
python scripts/cdp_publish.py content-data --csv-file "/abs/path/content_data.csv"
```

### 8) 多账号管理

```bash
# 列出所有账号
python scripts/cdp_publish.py list-accounts

# 添加新账号
python scripts/cdp_publish.py add-account work --alias "工作号"

# 登录指定账号
python scripts/cdp_publish.py --account work login

# 使用指定账号发布
python scripts/publish_pipeline.py --account work --headless \
  --title-file title.txt --content-file content.txt --image-urls "URL1"
```

## 输入判断流程

优先按以下顺序判断：

1. 用户明确要求"测试浏览器/启动浏览器/检查登录/只打开不发布"：进入测试浏览器流程
2. 用户要求"搜索笔记/找内容/查看某篇笔记详情/查看内容数据表/给帖子评论/查看评论和@通知"：进入内容检索与互动流程
3. 用户已提供 `标题 + 正文 + 视频(本地路径或URL)`：直接进入视频发布流程
4. 用户已提供 `标题 + 正文 + 图片(本地路径或URL)`：直接进入图文发布流程
5. 用户只提供网页 URL：先提取网页内容与图片/视频，再给出可发布草稿，等待用户确认
6. 信息不全：先补齐缺失信息，不要直接发布

## 必做约束

- 发布前必须让用户确认最终标题、正文和图片/视频
- 图文发布时，没有图片不得发布（小红书发图文必须有图片）
- 视频发布时，没有视频不得发布。图片和视频不可混合使用（二选一）
- 默认使用无头模式；若检测到未登录，切换有窗口模式登录
- 标题长度不超过 38（中文/中文标点按 2，英文数字按 1）
- 用户要求"仅测试浏览器"时，不得触发发布命令
- 如果使用文件路径，必定使用绝对路径，禁止使用相对路径

## 参数顺序提醒

请严格按下面顺序写命令，避免 `unrecognized arguments`：

- 全局参数放在子命令前：`--host --port --headless --account --timing-jitter --reuse-existing-tab`
- 子命令参数放在子命令后：如 `search-feeds` 的 `--keyword --sort-by --note-type`

示例（正确）：

```bash
python scripts/cdp_publish.py --reuse-existing-tab search-feeds --keyword "春招" --sort-by 最新 --note-type 图文
```

## 话题标签规则

- 从正文中提取规则：若"最后一个非空行"全部由 `#标签` 组成，则提取为话题标签并从正文移除
- 标签输入策略：逐个输入 `#标签`，等待 `3` 秒，再发送 `Enter` 进行确认
- 建议数量：`1-10` 个标签

## 故障排除

### 问题1：登录失败

**现象**：无法检测登录状态

**解决**：提示用户重新扫码登录并重试

```bash
python scripts/cdp_publish.py login
```

### 问题2：图片下载失败

**现象**：图片 URL 无法下载

**解决**：提示更换图片 URL 或改用本地图片

### 问题3：页面选择器失效

**现象**：发布失败，找不到页面元素

**解决**：检查 `scripts/cdp_publish.py` 中选择器并更新

### 问题4：远程 CDP 连接失败

**现象**：无法连接远程 Chrome

**解决**：确保远程 Chrome 已开启调试端口

```bash
# 远程 Chrome 启动示例
google-chrome --remote-debugging-port=9222 --remote-debugging-address=0.0.0.0
```

## 注意事项

1. **仅供学习研究**：请遵守小红书平台规则，不要用于违规内容发布
2. **登录安全**：Cookie 存储在本地 Chrome Profile 中，请勿泄露
3. **选择器更新**：如果小红书页面结构变化导致发布失败，需要更新选择器
4. **远程模式**：当 `--host` 非 `127.0.0.1/localhost` 时为远程模式，会跳过本地 `chrome_launcher.py` 的自动启动/重启逻辑
