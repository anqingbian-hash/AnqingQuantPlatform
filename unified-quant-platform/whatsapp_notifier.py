#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WhatsApp通知服务
用于量化平台推送股票推荐、止损止盈提醒
"""

import requests
from datetime import datetime
from typing import Dict, Any

class WhatsAppNotifier:
    """WhatsApp通知器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.business_id = config.get('business_id', '')
        self.phone_number_id = config.get('phone_number_id', '')
        self.access_token = config.get('access_token', '')
        self.api_url = f"https://graph.facebook.com/v17.0/{self.phone_number_id}/messages"
    
    def send_stock_recommendation(self, recipient: str, stock_data: Dict[str, Any]):
        """
        发送股票推荐通知
        
        Args:
            recipient: 接收者手机号（国际格式，如8613800138000）
            stock_data: 股票数据字典
        """
        message = f"""
📊 AnqingA股大师推荐
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

【{stock_data['name']}】({stock_data['symbol']})
板块: {stock_data['sector']}
价格: ¥{stock_data['price']:.2f}
涨跌: {stock_data['pct_chg']:+.2f}%
综合评分: {stock_data['total_score']:.1f}/100

🛑️ 止损: ¥{stock_data['stop_loss']:.2f}
🎯 止盈: ¥{stock_data['tp1']:.2f}
📦 仓位: {stock_data['position']*100:.0f}%

⚠️ 风险提示：
- 严格执行止损止盈
- 分批止盈，锁定利润
- 不恋战，快进快出
        """.strip()
        
        return self.send_message(recipient, message)
    
    def send_alert(self, recipient: str, alert_type: str, stock_name: str, price: float):
        """
        发送止损止盈提醒
        
        Args:
            recipient: 接收者手机号
            alert_type: 提醒类型（'stop_loss'或'take_profit'）
            stock_name: 股票名称
            price: 价格
        """
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        if alert_type == 'stop_loss':
            message = f"""
🛑️ 止损触发！
⏰ {timestamp}
{stock_name}已到达止损位
价格: ¥{price:.2f}

请立即平仓止损！
            """.strip()
        elif alert_type == 'take_profit':
            message = f"""
🎯 止盈触发！
⏰ {timestamp}
{stock_name}已到达目标位
价格: ¥{price:.2f}

建议部分或全部止盈！
            """.strip()
        else:
            message = f"⚠️ 提醒：{stock_name} {alert_type}"
        
        return self.send_message(recipient, message)
    
    def send_sector_scan_result(self, recipient: str, results: list):
        """
        发送板块扫描结果
        
        Args:
            recipient: 接收者手机号
            results: 扫描结果列表
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        message = f"""
📊 板块扫描结果
⏰ {timestamp}

推荐板块：
"""
        for i, result in enumerate(results[:5], 1):
            message += f"\n{i}. {result['sector']} ({result['score']:.1f}分)"
        
        message += f"""

推荐个股：
"""
        for i, result in enumerate(results[:3], 1):
            message += f"\n{i}. {result['name']} ({result['symbol']}) - {result['total_score']:.1f}分"
        
        return self.send_message(recipient, message)
    
    def send_message(self, recipient: str, message: str):
        """
        发送WhatsApp消息
        
        Args:
            recipient: 接收者手机号
            message: 消息内容
            
        Returns:
            API响应
        """
        # 注意：实际使用需要配置WhatsApp Business API
        # 这里是模拟发送
        print(f"[WhatsApp] 发送到 {recipient}:")
        print(f"[WhatsApp] {message[:100]}...")
        
        # 实际发送代码（需要配置Business API）：
        # headers = {
        #     'Authorization': f'Bearer {self.access_token}',
        #     'Content-Type': 'application/json'
        # }
        # 
        # data = {
        #     'messaging_product': 'whatsapp',
        #     'to': recipient,
        #     'type': 'template',
        #     'template': {
        #         'name': 'notification',
        #         'language': {'code': 'zh_CN'},
        #         'components': [{
        #             'type': 'body',
        #             'parameters': [{'type': 'text', 'text': message}]
        #         }]
        #     }
        # }
        # 
        # response = requests.post(self.api_url, json=data, headers=headers)
        # return response.json()
        
        return {'status': 'success', 'message': '模拟发送成功'}


# 配置示例
WHATSAPP_CONFIG = {
    'business_id': 'YOUR_BUSINESS_ID',
    'phone_number_id': 'YOUR_PHONE_NUMBER_ID',
    'access_token': 'YOUR_ACCESS_TOKEN',
    'recipients': {
        'default': '8613800138000',  # 您的号码
        'test': '8613900139000'
    }
}

# 测试代码
if __name__ == '__main__':
    notifier = WhatsAppNotifier(WHATSAPP_CONFIG)
    
    # 测试股票推荐
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
    
    print("="*80)
    print("📱 WhatsApp通知测试")
    print("="*80)
    print("\n1. 测试股票推荐通知:")
    notifier.send_stock_recommendation(
        recipient='8613800138000',
        stock_data=test_stock
    )
    
    print("\n2. 测试止损提醒:")
    notifier.send_alert(
        recipient='8613800138000',
        alert_type='stop_loss',
        stock_name='宁德时代',
        price=330.01
    )
    
    print("\n3. 测试止盈提醒:")
    notifier.send_alert(
        recipient='8613800138000',
        alert_type='take_profit',
        stock_name='宁德时代',
        price=374.24
    )
    
    print("\n" + "="*80)
    print("✅ 测试完成")
    print("="*80)
