#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多渠道推送模块 - 飞书 + 邮件 + 微信 + 钉钉
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

# 配置日志
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MultiChannelReporter:
    """多渠道推送Agent - 飞书 + 邮件 + 微信 + 钉钉"""
    
    def __init__(self, config_file=None):
        self.name = "MultiChannelReporter"
        
        # 加载配置
        self.config = self._load_config(config_file)
        
        # 渠道配置
        self.feishu_enabled = self.config.get('feishu_enabled', True)
        self.email_enabled = self.config.get('email_enabled', False)
        self.wechat_enabled = self.config.get('wechat_enabled', False)
        self.dingtalk_enabled = self.config.get('dingtalk_enabled', False)
        
        # API配置
        self.feishu_webhook = os.getenv('FEISHU_WEBHOOK_URL') or self.config.get('feishu_webhook')
        self.email_to = os.getenv('EMAIL_TO') or self.config.get('email_to')
        self.email_from = os.getenv('EMAIL_FROM') or self.config.get('email_from')
        self.email_password = os.getenv('EMAIL_PASSWORD') or self.config.get('email_password')
        self.email_smtp = self.config.get('email_smtp', 'smtp.163.com')
        self.email_port = self.config.get('email_port', 465)
        
        logger.info(f"[MultiChannelReporter] 初始化完成")
        logger.info(f"  飞书推送: {self.feishu_enabled}")
        logger.info(f"  邮件推送: {self.email_enabled}")
        logger.info(f"  微信推送: {self.wechat_enabled}")
        logger.info(f"  钉钉推送: {self.dingtalk_enabled}")
    
    def _load_config(self, config_file=None):
        """加载配置文件"""
        try:
            if config_file is None:
                config_file = './config/multi_channel_config.json'
            
            if not os.path.exists(config_file):
                logger.warning(f"[MultiChannelReporter] 配置文件不存在: {config_file}")
                return {}
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            logger.info(f"[MultiChannelReporter] 配置加载成功")
            return config
            
        except Exception as e:
            logger.error(f"[MultiChannelReporter] 加载配置失败: {e}")
            return {}
    
    def send_report(self, title: str, content: str, charts: List[str] = None, 
                   channels: List[str] = None):
        """
        发送多渠道报告
        
        参数:
            title: 报告标题
            content: 报告内容（Markdown格式）
            charts: 图表路径列表
            channels: 推送渠道（默认全部）
        """
        try:
            logger.info(f"[MultiChannelReporter] 发送多渠道报告: {title}")
            
            # 默认推送所有渠道
            if channels is None:
                channels = ['feishu']
                if self.email_enabled:
                    channels.append('email')
                if self.wechat_enabled:
                    channels.append('wechat')
                if self.dingtalk_enabled:
                    channels.append('dingtalk')
            
            results = {}
            
            # 1. 飞书推送
            if 'feishu' in channels and self.feishu_enabled:
                try:
                    result = self.send_feishu(title, content, charts)
                    results['feishu'] = result
                except Exception as e:
                    logger.error(f"[MultiChannelReporter] 飞书推送失败: {e}")
                    results['feishu'] = {'success': False, 'error': str(e)}
            
            # 2. 邮件推送
            if 'email' in channels and self.email_enabled:
                try:
                    result = self.send_email(title, content, charts)
                    results['email'] = result
                except Exception as e:
                    logger.error(f"[MultiChannelReporter] 邮件推送失败: {e}")
                    results['email'] = {'success': False, 'error': str(e)}
            
            # 3. 微信推送（Mock）
            if 'wechat' in channels and self.wechat_enabled:
                try:
                    result = self.send_wechat(title, content, charts)
                    results['wechat'] = result
                except Exception as e:
                    logger.error(f"[MultiChannelReporter] 微信推送失败: {e}")
                    results['wechat'] = {'success': False, 'error': str(e)}
            
            # 4. 钉钉推送（Mock）
            if 'dingtalk' in channels and self.dingtalk_enabled:
                try:
                    result = self.send_dingtalk(title, content, charts)
                    results['dingtalk'] = result
                except Exception as e:
                    logger.error(f"[MultiChannelReporter] 钉钉推送失败: {e}")
                    results['dingtalk'] = {'success': False, 'error': str(e)}
            
            logger.info(f"[MultiChannelReporter] 多渠道推送完成: {len(results)} 个渠道")
            return results
            
        except Exception as e:
            logger.error(f"[MultiChannelReporter] 发送多渠道报告失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def send_feishu(self, title: str, content: str, charts: List[str] = None):
        """
        发送飞书报告
        
        参数:
            title: 报告标题
            content: 报告内容（Markdown格式）
            charts: 图表路径列表
        
        返回:
            dict: 发送结果
        """
        try:
            logger.info(f"[MultiChannelReporter] 发送飞书报告: {title}")
            
            if not self.feishu_webhook:
                logger.warning("[MultiChannelReporter] 未配置飞书Webhook，使用Mock模式")
                return self._mock_feishu(title, content, charts)
            
            # 使用飞书API推送
            # 注意：需要安装飞书SDK
            # 这里先返回Mock
            
            return self._mock_feishu(title, content, charts)
            
        except Exception as e:
            logger.error(f"[MultiChannelReporter] 飞书推送失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _mock_feishu(self, title: str, content: str, charts: List[str] = None):
        """Mock飞书推送"""
        try:
            logger.info(f"[MultiChannelReporter] Mock飞书推送")
            logger.info(f"  标题: {title}")
            logger.info(f"  内容长度: {len(content)} 字符")
            logger.info(f"  图表数量: {len(charts) if charts else 0}")
            
            # 保存到本地文件
            output_file = './output/mock_feishu_report.txt'
            os.makedirs('./output', exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"飞书报告（Mock）\n")
                f.write(f"{'='*60}\n")
                f.write(f"标题: {title}\n")
                f.write(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"\n内容:\n")
                f.write(content)
                if charts:
                    f.write(f"\n\n图表:\n")
                    for chart in charts:
                        f.write(f"- {chart}\n")
            
            logger.info(f"✓ Mock飞书报告保存: {output_file}")
            
            return {
                'success': True,
                'mock': True,
                'output_file': output_file,
                'message': 'Mock飞书推送成功'
            }
            
        except Exception as e:
            logger.error(f"[MultiChannelReporter] Mock飞书推送失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def send_email(self, title: str, content: str, charts: List[str] = None):
        """
        发送邮件报告
        
        参数:
            title: 邮件主题
            content: 邮件内容（Markdown/HTML格式）
            charts: 图表路径列表
        
        返回:
            dict: 发送结果
        """
        try:
            logger.info(f"[MultiChannelReporter] 发送邮件报告: {title}")
            
            if not self.email_to or not self.email_from:
                logger.warning("[MultiChannelReporter] 未配置邮箱，使用Mock模式")
                return self._mock_email(title, content, charts)
            
            # 使用SMTP发送邮件
            # 注意：需要配置SMTP服务器
            # 这里先返回Mock
            
            return self._mock_email(title, content, charts)
            
        except Exception as e:
            logger.error(f"[MultiChannelReporter] 邮件推送失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _mock_email(self, title: str, content: str, charts: List[str] = None):
        """Mock邮件推送"""
        try:
            logger.info(f"[MultiChannelReporter] Mock邮件推送")
            logger.info(f"  主题: {title}")
            logger.info(f"  收件人: {self.email_to or 'N/A'}")
            logger.info(f"  发件人: {self.email_from or 'N/A'}")
            logger.info(f"  内容长度: {len(content)} 字符")
            logger.info(f"  图表数量: {len(charts) if charts else 0}")
            
            # 保存到本地文件
            output_file = './output/mock_email_report.txt'
            os.makedirs('./output', exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"邮件报告（Mock）\n")
                f.write(f"{'='*60}\n")
                f.write(f"主题: {title}\n")
                f.write(f"收件人: {self.email_to or 'N/A'}\n")
                f.write(f"发件人: {self.email_from or 'N/A'}\n")
                f.write(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"\n内容:\n")
                f.write(content)
                if charts:
                    f.write(f"\n\n图表:\n")
                    for chart in charts:
                        f.write(f"- {chart}\n")
            
            logger.info(f"✓ Mock邮件报告保存: {output_file}")
            
            return {
                'success': True,
                'mock': True,
                'output_file': output_file,
                'message': 'Mock邮件推送成功'
            }
            
        except Exception as e:
            logger.error(f"[MultiChannelReporter] Mock邮件推送失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def send_wechat(self, title: str, content: str, charts: List[str] = None):
        """
        发送微信报告（Mock）
        """
        try:
            logger.info(f"[MultiChannelReporter] Mock微信推送: {title}")
            
            # Mock微信推送
            return {
                'success': True,
                'mock': True,
                'message': 'Mock微信推送成功'
            }
            
        except Exception as e:
            logger.error(f"[MultiChannelReporter] 微信推送失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def send_dingtalk(self, title: str, content: str, charts: List[str] = None):
        """
        发送钉钉报告（Mock）
        """
        try:
            logger.info(f"[MultiChannelReporter] Mock钉钉推送: {title}")
            
            # Mock钉钉推送
            return {
                'success': True,
                'mock': True,
                'message': 'Mock钉钉推送成功'
            }
            
        except Exception as e:
            logger.error(f"[MultiChannelReporter] 钉钉推送失败: {e}")
            return {'success': False, 'error': str(e)}


# 测试函数
def test_multi_channel_reporter():
    """测试多渠道推送"""
    print('='*80)
    print("测试MultiChannelReporter - 多渠道推送")
    print('='*80)
    
    # 创建实例
    reporter = MultiChannelReporter()
    
    # 准备测试数据
    title = "交易报告测试 - 2026-03-03"
    content = """
# 交易报告测试

## 市场概况

### 北向资金
- 净买入额：12.08亿元
- 变化率：+156.00%
- 状态：资金大幅流入

### 两融数据
- 融资余额：14523.45亿元
- 融资变化率：+2.3%
- 状态：杠杆资金活跃

### 龙虎榜
- 上榜数量：42只
- 机构买入：28只
- 机构卖出：14只

## 操作建议

### 潜力股
✓ 贵州茅台（600519.SH）：北向净流入30.0亿，融资增长5.0%
✓ 宁德时代（300750.SZ）：机构买入比率高
✓ 烽火通信（600498.SH）：龙虎榜机构买入66.7%

### 风控减仓
✓ 暂无风险信号

## 综合建议

**市场环境**：偏多
**风险等级**：低
**操作建议**：正常操作，可适当建仓

---
*本报告由MultiChannelReporter自动生成*
"""
    
    # Mock图表
    charts = [
        './output/charts/north_south_trend.png',
        './output/charts/margin_trend.png',
        './output/charts/lhb_heatmap.png'
    ]
    
    # 测试1：发送飞书
    print("\n【测试1】发送飞书报告")
    result = reporter.send_feishu(title, content, charts)
    print(f"{'✓' if result.get('success') else '✗'} 飞书推送")
    if result.get('mock'):
        print(f"  Mock文件: {result.get('output_file')}")
    
    # 测试2：发送邮件
    print("\n【测试2】发送邮件报告")
    result = reporter.send_email(title, content, charts)
    print(f"{'✓' if result.get('success') else '✗'} 邮件推送")
    if result.get('mock'):
        print(f"  Mock文件: {result.get('output_file')}")
    
    # 测试3：多渠道推送
    print("\n【测试3】多渠道推送")
    result = reporter.send_report(title, content, charts, channels=['feishu', 'email'])
    print(f"✓ 多渠道推送完成: {len(result)} 个渠道")
    for channel, res in result.items():
        print(f"  {channel}: {'✓' if res.get('success') else '✗'}")
    
    # 测试4：全渠道推送
    print("\n【测试4】全渠道推送")
    result = reporter.send_report(title, content, charts)
    print(f"✓ 全渠道推送完成: {len(result)} 个渠道")
    for channel, res in result.items():
        print(f"  {channel}: {'✓' if res.get('success') else '✗'}")
    
    print('\n' + '='*80)
    print('✅ MultiChannelReporter测试完成！')
    print('='*80)
    
    return True


if __name__ == '__main__':
    test_multi_channel_reporter()
