# API申请和服务器配置指南
# 生成时间: 2026-02-22 10:47

## 一、TradingView API密钥申请指南

### 1.1 TradingView API说明

**重要认知：**
- TradingView官方**没有公开的免费API**
- TradingView Charting Library需要付费许可（$999+/年）
- **免费替代方案：使用第三方数据源**

### 1.2 免费替代方案（推荐）

#### 方案A：使用TradingView数据widget（免费）

**适用场景：**
- 网页版产品
- 只需要展示图表
- 不需要实时交易数据

**优点：**
- 完全免费
- 官方支持
- 易于集成

**缺点：**
- 只能展示，不能获取数据
- 受限于TradingView的widget

#### 方案B：使用免费金融数据API（推荐）

**推荐数据源：**

1. **Alpha Vantage（免费额度高）**
   - 官网：https://www.alphavantage.co/
   - 注册：免费
   - 免费额度：25次请求/天，500次请求/天（部分功能）
   - 支持市场：美股、外汇、加密货币
   - **申请步骤：**
     1. 访问官网
     2. 点击"Get Free API Key"
     3. 填写邮箱和姓名
     4. 邮箱验证
     5. 获取API Key

2. **Yahoo Finance（免费）**
   - 官网：https://finance.yahoo.com/
   - 注册：免费
   - 免费额度：无限制
   - 支持市场：美股、港股、A股
   - **申请步骤：**
     1. 使用Python库yfinance
     2. pip install yfinance
     3. 无需API Key

3. **Tushare Pro（A股，免费+付费）**
   - 官网：https://tushare.pro/
   - 注册：免费
   - 免费额度：120次/分钟
   - 支持市场：A股、港股、美股、期货
   - **申请步骤：**
     1. 访问官网
     2. 注册账号
     3. 实名认证
     4. 获取Token（API Key）

4. **Quandl（部分免费）**
   - 官网：https://www.quandl.com/
   - 注册：免费
   - 免费额度：50次请求/天
   - 支持市场：美股、经济数据

5. **IEX Cloud（免费+付费）**
   - 官网：https://iexcloud.io/
   - 注册：免费
   - 免费额度：50,000条/月
   - 支持市场：美股

### 1.3 我们的建议

**优先级：**
1. **Tushare Pro**（A股+期货，免费额度高）
2. **Alpha Vantage**（美股，免费额度高）
3. **Yahoo Finance**（港股，免费无限制）

**申请顺序：**
1. 今天申请Tushare Pro
2. 今天申请Alpha Vantage
3. Yahoo Finance无需申请

---

## 二、Tushare API密钥申请指南（优先）

### 2.1 申请步骤（5分钟）

**第1步：注册账号**
1. 访问官网：https://tushare.pro/
2. 点击右上角"注册"
3. 填写：
   - 手机号
   - 密码
   - 确认密码
   - 图形验证码
4. 点击"注册"

**第2步：实名认证**
1. 登录账号
2. 点击右上角"个人中心"
3. 点击"实名认证"
4. 上传身份证正反面
5. 填写姓名和身份证号
6. 等待审核（1-3个工作日，通常1小时）

**第3步：获取Token**
1. 登录账号
2. 点击右上角"个人中心"
3. 点击"接口TOKEN"
4. 点击"复制Token"（这是您的API Key）

### 2.2 免费额度

**免费用户：**
- 120次请求/分钟
- 每日无限制（但受分钟限制）
- 可以访问大部分接口

**接口限制：**
- 实时数据：免费版部分接口可用
- 历史数据：大部分免费
- 高级数据：需要积分或付费

### 2.3 需要的数据

**我们可以获取的数据：**
1. **实时行情数据**
   - 股票实时行情
   - 期货实时行情
   - K线数据（日K、周K、月K、分钟K）

2. **成交量数据**
   - 成交量（vol）
   - 成交金额（amount）

3. **持仓量数据（期货）**
   - 日线持仓量
   - 持仓变化

4. **多空数据**
   - 注意：Tushare不直接提供多空数据
   - 需要我们自己计算或从其他数据源获取

### 2.4 Python调用示例

```python
import tushare as ts

# 设置Token
ts.set_token('您的Token')
pro = ts.pro_api()

# 获取股票日线数据
df = pro.daily(ts_code='000001.SZ', start_date='20240101', end_date='20240201')

# 获取期货数据
df = pro.fut_daily(ts_code='IF2401', exchange='CFFEX', start_date='20240101', end_date='20240201')

# 获取实时行情
df = pro.realtime_quote(ts_code='000001.SZ,IF2401')
```

---

## 三、Alpha Vantage API密钥申请指南

### 3.1 申请步骤（3分钟）

**第1步：注册账号**
1. 访问官网：https://www.alphavantage.co/
2. 点击"Get Free API Key"
3. 填写：
   - First Name（名）
   - Last Name（姓）
   - Email（邮箱）
   - Organization（组织，可以填个人）
4. 点击"Get Free API Key"

**第2步：验证邮箱**
1. 查收邮箱
2. 点击验证链接
3. 登录账号

**第3步：获取API Key**
1. 登录后自动跳转到Dashboard
2. API Key显示在页面顶部
3. 点击"Copy API Key"

### 3.2 免费额度

**免费用户：**
- 25次请求/天（基础功能）
- 500次请求/天（部分功能）

**功能限制：**
- 实时数据：5次/分钟
- 历史数据：完整
- 技术指标：完整

### 3.3 支持的市场

- 美股
- 外汇
- 加密货币

### 3.4 Python调用示例

```python
from alpha_vantage.timeseries import TimeSeries

# 设置API Key
ts = TimeSeries(key='您的API_Key', output_format='pandas')

# 获取美股日线数据
data, meta_data = ts.get_daily(symbol='AAPL')

# 获取实时数据
data, meta_data = ts.get_intraday(symbol='AAPL',interval='1min', outputsize='full')
```

---

## 四、云服务器申请指南

### 4.1 推荐云服务商

#### 选项A：阿里云（推荐）

**原因：**
- 国内访问速度快
- 服务稳定
- 价格合理
- 中文支持好

**推荐配置：**
- CPU：2核
- 内存：4G
- 硬盘：40G SSD
- 带宽：3M
- 操作系统：Ubuntu 22.04 LTS

**价格：**
- 新用户首月：约50元
- 续费：约200元/月
- 年付：约2000元/年

**申请步骤：**

1. **注册账号**
   - 访问：https://www.aliyun.com/
   - 点击"免费注册"
   - 手机号验证
   - 实名认证（上传身份证）

2. **购买云服务器**
   - 点击"产品" → "云服务器ECS"
   - 选择"立即购买"
   - 选择配置：
     - 付费方式：包年包月（推荐年付，更便宜）
     - 地域：华东1（杭州）或其他
     - 实例规格：2核4G
     - 镜像：Ubuntu 22.04 LTS
     - 存储：40G SSD
     - 带宽：3M
   - 设置密码（记住！）
   - 点击"立即购买"
   - 支付

3. **获取服务器信息**
   - 登录控制台
   - 进入"云服务器ECS"
   - 查看实例
   - 记录：
     - 公网IP（重要！）
     - 用户名（root）
     - 密码（您设置的）

#### 选项B：腾讯云

**价格：**
- 新用户首月：约50元
- 续费：约200元/月
- 年付：约2000元/年

**申请步骤：**
1. 访问：https://cloud.tencent.com/
2. 注册账号
3. 实名认证
4. 购买云服务器（CVM）
5. 配置：2核4G，40G SSD，Ubuntu 22.04
6. 记录公网IP、用户名、密码

#### 选项C：华为云

**价格：**
- 新用户首月：约50元
- 续费：约200元/月
- 年付：约2000元/年

**申请步骤：**
1. 访问：https://www.huaweicloud.com/
2. 注册账号
3. 实名认证
4. 购买云服务器（ECS）
5. 配置：2核4G，40G SSD，Ubuntu 22.04
6. 记录公网IP、用户名、密码

### 4.2 我们的建议

**推荐：阿里云**

**原因：**
- 国内访问速度快
- 价格合理
- 服务稳定
- 文档齐全

**配置建议：**
- CPU：2核（可以升级）
- 内存：4G（可以升级）
- 硬盘：40G SSD（可以扩容）
- 带宽：3M（可以升级）
- 操作系统：Ubuntu 22.04 LTS

---

## 五、域名申请指南

### 5.1 推荐域名注册商

#### 选项A：阿里云

**申请步骤：**
1. 登录阿里云
2. 点击"产品" → "域名注册"
3. 搜索域名（如：ntdf.com, ntdftrading.com）
4. 选择域名（.com/.cn/.net等）
5. 添加购物车
6. 支付

**价格：**
- .com：约60元/年
- .cn：约30元/年
- .net：约60元/年

#### 选项B：腾讯云

**申请步骤：**
1. 登录腾讯云
2. 点击"产品" → "域名注册"
3. 搜索域名
4. 选择域名
5. 支付

**价格：**
- .com：约60元/年
- .cn：约30元/年
- .net：约60元/年

### 5.2 域名解析

**申请步骤（以阿里云为例）：**

1. **添加解析记录**
   - 登录阿里云控制台
   - 点击"域名"
   - 点击您的域名
   - 点击"解析"
   - 点击"添加记录"
   - 填写：
     - 记录类型：A
     - 主机记录：@（或www）
     - 记录值：您的云服务器公网IP
     - TTL：600
   - 点击"确认"

2. **等待生效**
   - 通常10-30分钟生效
   - 可以用ping命令测试

---

## 六、SSL证书申请指南（免费）

### 6.1 Let's Encrypt（免费，推荐）

**申请步骤：**

1. **安装Certbot**
   ```bash
   sudo apt update
   sudo apt install certbot
   ```

2. **申请证书**
   ```bash
   sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
   ```

3. **证书位置**
   - 证书：/etc/letsencrypt/live/yourdomain.com/fullchain.pem
   - 私钥：/etc/letsencrypt/live/yourdomain.com/privkey.pem

4. **自动续期**
   ```bash
   sudo certbot renew --dry-run
   ```

### 6.2 阿里云免费SSL（3个月）

**申请步骤：**

1. 登录阿里云控制台
2. 点击"产品" → "SSL证书"
3. 点击"购买证书"
4. 选择"免费证书"
5. 填写域名信息
6. 提交申请
7. 等待审核（通常1-2小时）
8. 下载证书

---

## 七、立即行动清单

### 今天必须做（卞董）：

**1. 申请Tushare API密钥**
- [ ] 访问：https://tushare.pro/
- [ ] 注册账号
- [ ] 实名认证（上传身份证）
- [ ] 获取Token
- [ ] 发送Token给我

**2. 申请Alpha Vantage API密钥**
- [ ] 访问：https://www.alphavantage.co/
- [ ] 注册账号
- [ ] 验证邮箱
- [ ] 获取API Key
- [ ] 发送API Key给我

**3. 申请云服务器（阿里云）**
- [ ] 访问：https://www.aliyun.com/
- [ ] 注册账号
- [ ] 实名认证
- [ ] 购买云服务器（2核4G，40G SSD，Ubuntu 22.04）
- [ ] 记录：
  - 公网IP：________
  - 用户名：root
  - 密码：________
- [ ] 发送公网IP和密码给我

**4. 申请域名（可选）**
- [ ] 搜索域名（如：ntdftrading.com）
- [ ] 购买域名
- [ ] 域名解析到云服务器IP

### 我今天会做的：

**1. 搭建开发环境**
- [ ] 安装Python 3.11
- [ ] 安装Vue3开发环境
- [ ] 安装PostgreSQL
- [ ] 安装Docker

**2. 开始学习**
- [ ] 学习Vue3基础
- [ ] 学习ECharts
- [ ] 学习WebSocket

**3. 设计数据库架构**
- [ ] 设计用户表
- [ ] 设计数据表
- [ ] 设计配置表

**4. 开始数据接入开发**
- [ ] Tushare API对接
- [ ] 数据库存储
- [ ] 实时数据推送

---

## 八、卞董，请立即告诉我

**1. Tushare Token**
- 您的Token：________

**2. Alpha Vantage API Key**
- 您的API Key：________

**3. 阿里云服务器信息**
- 公网IP：________
- 密码：________

**4. 域名（如果申请了）**
- 域名：________

---

卞董，这就是申请指南。请立即按照指南操作，完成后告诉我API密钥和服务器信息，我会立即开始开发！
