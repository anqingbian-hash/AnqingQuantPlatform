# WhatsApp完整配置指南

## 一、📱 WhatsApp个人账号登录

### 1. 使用命令行登录
```bash
openclaw channels login
```

这会显示二维码，用WhatsApp扫码即可。

### 2. 配置文件设置
创建或编辑Gateway配置文件：

```yaml
# gateway.yaml
channels:
  whatsapp:
    type: whatsapp
    enabled: true
    # WhatsApp相关配置
```

### 3. 验证登录
```bash
openclaw channels list
```

---

## 二、🏢 WhatsApp Business API（企业级）

### 1. 创建WhatsApp Business账号
1. 访问：https://business.facebook.com/
2. 创建Business账号
3. 获取Business ID

### 2. 设置WhatsApp Business API
1. 访问：https://developers.facebook.com/docs/whatsapp/
2. 创建App
3. 获取App ID和App Secret
4. 配置Webhook

### 3. 配置Gateway

```yaml
# gateway.yaml
channels:
  whatsapp_business:
    type: whatsapp_business
    enabled: true
    config:
      business_id: YOUR_BUSINESS_ID
      phone_number_id: YOUR_PHONE_NUMBER_ID
      access_token: YOUR_ACCESS_TOKEN
      webhook_url: YOUR_WEBHOOK_URL
      verify_token: YOUR_VERIFY_TOKEN
```

### 4. 获取API凭证
- Business ID
- Phone Number ID
- Access Token
- Webhook URL

---

## 三、📊 量化平台WhatsApp通知集成

### 1. 安装依赖
```bash
pip install yowsup2  # WhatsApp库
# 或者
pip install python-telegram-bot  # 如果用Telegram中转
```

### 2. 创建WhatsApp通知服务

```python
# whatsapp_notifier.py
import requests

class WhatsAppNotifier:
    def __init__(self, config):
        self.business_id = config['business_id']
        self.access_token = config['access_token']
        self.phone_number_id = config['phone_number_id']
        self.api_url = f"https://graph.facebook.com/v17.0/{self.phone_number_id}/messages"
    
    def send_stock_recommendation(self, recipient, stock_data):
        """发送股票推荐"""
        message = f"""
📊 AnqingA股大师推荐

【{stock_data['name']}】({stock_data['symbol']})
板块: {stock_data['sector']}
价格: ¥{stock_data['price']:.2f}
涨跌: {stock_data['pct_chg']:+.2f}%
综合评分: {stock_data['total_score']:.1f}/100

止损: ¥{stock_data['stop_loss']:.2f}
止盈: ¥{stock_data['tp1']:.2f}
仓位: {stock_data['position']*100:.0f}%
        """
        
        self.send_message(recipient, message)
    
    def send_alert(self, recipient, alert_type, stock_name, price):
        """发送止损止盈提醒"""
        if alert_type == 'stop_loss':
            message = f"🛑️ 止损触发！\n{stock_name}已到达止损位¥{price:.2f}"
        elif alert_type == 'take_profit':
            message = f"🎯 止盈触发！\n{stock_name}已到达目标位¥{price:.2f}"
        
        self.send_message(recipient, message)
    
    def send_message(self, recipient, message):
        """发送WhatsApp消息"""
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'messaging_product': 'whatsapp',
            'to': recipient,
            'type': 'template',
            'template': {
                'name': 'notification',
                'language': {'code': 'zh_CN'},
                'components': [{
                    'type': 'body',
                    'parameters': [{'type': 'text', 'text': message}]
                }]
            }
        }
        
        response = requests.post(self.api_url, json=data, headers=headers)
        return response.json()
```

### 3. 集成到量化平台

在`app_v9_complete.py`中添加WhatsApp通知：

```python
# 在Flask应用中添加
from whatsapp_notifier import WhatsAppNotifier

# 初始化通知器
whatsapp_notifier = WhatsAppNotifier(whatsapp_config)

# 股票推荐后发送通知
@app.route('/api/selector')
def selector():
    result = strategy_engine.scan_market()
    
    # 发送WhatsApp通知
    for stock in result['stocks'][:3]:
        whatsapp_notifier.send_stock_recommendation(
            recipient='用户手机号',
            stock_data=stock
        )
    
    return jsonify(result)
```

### 4. 创建通知配置

```python
# whatsapp_config.py
WHATSAPP_CONFIG = {
    'business_id': 'YOUR_BUSINESS_ID',
    'phone_number_id': 'YOUR_PHONE_NUMBER_ID',
    'access_token': 'YOUR_ACCESS_TOKEN',
    'recipients': {
        'default': '8613800138000',  # 您的号码
        'test': '8613900139000'
    }
}
```

---

## 四、🚀 快速启动

### 1. 启动步骤

```bash
# 1. 安装依赖
cd /root/.openclaw/workspace/unified-quant-platform
pip install requests

# 2. 配置Gateway
openclaw gateway config.get

# 3. 登录WhatsApp
openclaw channels login

# 4. 启动Gateway
openclaw gateway start

# 5. 启动量化平台
python3 app_v9_complete.py
```

### 2. 测试通知

```python
# test_whatsapp.py
from whatsapp_notifier import WhatsAppNotifier
from whatsapp_config import WHATSAPP_CONFIG

notifier = WhatsAppNotifier(WHATSAPP_CONFIG)

# 测试发送
test_stock = {
    'name': '宁德时代',
    'symbol': '300750',
    'sector': '锂电池',
    'price': 340.22,
    'pct_chg': 2.10,
    'total_score': 18.9,
    'stop_loss': 330.01,
    'tp1': 374.24,
    'position': 0.10
}

notifier.send_stock_recommendation(
    recipient='8613800138000',
    stock_data=test_stock
)
```

---

## 五、📋 检查清单

- [ ] WhatsApp个人账号已登录
- [ ] WhatsApp Business账号已创建
- [ ] Business ID已获取
- [ ] Access Token已生成
- [ ] Phone Number ID已配置
- [ ] Webhook已设置
- [ ] 量化平台已集成WhatsApp通知
- [ ] 测试消息已发送成功

---

## 六、📞 配置信息

### 需要提供的信息

1. **WhatsApp Business**
   - Business ID
   - Phone Number ID
   - Access Token
   - Webhook URL

2. **个人WhatsApp**
   - 手机号码（用于登录）
   - 验证码

3. **量化平台通知**
   - 接收通知的手机号
   - 通知类型（推荐、止损、止盈）

---

**配置向导**：https://docs.openclaw.ai/gateway/configuration
