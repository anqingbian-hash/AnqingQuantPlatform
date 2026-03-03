#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试真实飞书推送
"""
import os
import sys
from datetime import datetime

# 配置飞书Webhook
os.environ['FEISHU_WEBHOOK_URL'] = 'https://open.feishu.cn/open-apis/bot/v2/hook/087e8eb0-9f93-4e9f-938d-35830294c8a0'

# 添加路径
sys.path.append('/root/.openclaw/workspace/FundsMonitor')
sys.path.append('/root/.openclaw/workspace/FundsMonitor/modules')

# 导入模块
from multi_channel_reporter import MultiChannelReporter

# 配置日志
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_real_feishu():
    """测试真实飞书推送"""
    print('='*80)
    print('测试真实飞书推送')
    print('='*80)
    
    try:
        # 创建Reporter实例
        reporter = MultiChannelReporter()
        
        # 准备测试消息
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        title = "OpenClaw 测试成功"
        content = f"""【OpenClaw 测试成功】飞书 Webhook 已配置完成！

当前时间：{current_time}
系统状态：正常
DeepSeek 真实决策已就位。

---
*本消息由 OpenClaw 自动发送*"""
        
        # 发送飞书报告
        print('\n发送飞书报告...')
        result = reporter.send_feishu(title, content)
        
        # 检查结果
        print('\n' + '='*80)
        print('推送结果')
        print('='*80)
        
        if result.get('success'):
            if result.get('mock'):
                print('⚠️  Mock模式（未使用真实Webhook）')
                print(f'  Mock文件: {result.get("output_file")}')
            else:
                print('✅ 真实飞书推送成功！')
                print(f'  响应: {result.get("response")}')
        else:
            print(f'❌ 推送失败: {result.get("error")}')
            return False
        
        print('='*80)
        print('✅ 测试完成！')
        print('='*80)
        
        return True
        
    except Exception as e:
        print(f'❌ 测试失败: {e}')
        logger.error(f"测试失败: {e}")
        return False


if __name__ == '__main__':
    success = test_real_feishu()
    
    if success:
        print('\n✅ 真实飞书推送测试成功！')
        sys.exit(0)
    else:
        print('\n❌ 真实飞书推送测试失败！')
        sys.exit(1)
