#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DecisionMaker - LLM决策Agent
使用litellm调用DeepSeek/Gemini，输入行情/资金/新闻，输出决策结论
"""
import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List, Any
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 检查是否安装了litellm
try:
    from litellm import completion
    LITELM_AVAILABLE = True
    logger.info("[DecisionMaker] litellm已安装，LLM功能可用")
except ImportError:
    LITELM_AVAILABLE = False
    logger.warning("[DecisionMaker] litellm未安装，将使用Mock模式")


class DecisionMaker:
    """LLM决策Agent"""
    
    def __init__(self, model=None, api_key=None):
        self.name = "DecisionMaker"
        
        # LLM模型配置
        self.model = model or "deepseek/deepseek-chat"
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        
        if LITELM_AVAILABLE:
            logger.info(f"[DecisionMaker] LLM模型: {self.model}")
        else:
            logger.warning("[DecisionMaker] LLM不可用，使用Mock模式")
    
    def analyze_market_data(self, market_data: Dict[str, Any]) -> str:
        """
        分析市场数据
        
        参数:
            market_data: 市场数据字典
                {
                    'stock_quote': {'code': '600519', 'name': '贵州茅台', 'price': 1440.00, 'change_pct': 0.5},
                    'fund_flow': {'north_inflow': 30.0, 'margin_growth': 5.0},
                    'news': [{'title': '...', 'score': 0.8}, ...]
                }
        
        返回:
            str: 市场分析摘要
        """
        try:
            logger.info("[DecisionMaker] 开始分析市场数据...")
            
            # 1. 股票行情分析
            quote = market_data.get('stock_quote', {})
            stock_analysis = ""
            
            if quote:
                name = quote.get('name', 'N/A')
                price = quote.get('price', 0)
                change_pct = quote.get('change_pct', 0)
                
                if change_pct > 0:
                    stock_analysis = f"{name}价格{price:.2f}元，上涨{change_pct:.2f}%，走势偏强。"
                elif change_pct < 0:
                    stock_analysis = f"{name}价格{price:.2f}元，下跌{abs(change_pct):.2f}%，走势偏弱。"
                else:
                    stock_analysis = f"{name}价格{price:.2f}元，平盘。"
            
            # 2. 资金流向分析
            fund = market_data.get('fund_flow', {})
            fund_analysis = ""
            
            if fund:
                north_inflow = fund.get('north_inflow', 0)
                margin_growth = fund.get('margin_growth', 0)
                
                if north_inflow > 30:
                    fund_analysis = f"北向资金大幅净流入{north_inflow:.2f}亿元，市场看好。"
                elif north_inflow > 0:
                    fund_analysis = f"北向资金净流入{north_inflow:.2f}亿元，资金活跃。"
                elif north_inflow < -50:
                    fund_analysis = f"北向资金净流出{abs(north_inflow):.2f}亿元，市场悲观。"
                else:
                    fund_analysis = f"北向资金平衡。"
                
                if margin_growth > 5:
                    fund_analysis += f"融资余额增长{margin_growth:.2f}%，杠杆资金活跃。"
            
            # 3. 新闻舆情分析
            news = market_data.get('news', [])
            news_analysis = ""
            
            if news:
                # 提取高分新闻
                top_news = sorted(news, key=lambda x: x.get('score', 0), reverse=True)[:3]
                
                if top_news:
                    news_summary = "; ".join([n['title'][:50] for n in top_news])
                    news_analysis = f"近期新闻摘要：{news_summary}"
                else:
                    news_analysis = "暂无新闻。"
            else:
                news_analysis = "暂无新闻数据。"
            
            # 综合分析
            analysis = f"""
【市场数据分析】

股票行情：{stock_analysis}

资金流向：{fund_analysis}

新闻舆情：{news_analysis}
"""
            
            logger.info(f"[DecisionMaker] 市场数据分析完成")
            return analysis
            
        except Exception as e:
            logger.error(f"[DecisionMaker] 市场数据分析失败: {e}")
            return "市场数据分析失败。"
    
    def generate_decision(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成交易决策
        
        参数:
            market_data: 市场数据字典
        
        返回:
            dict: 决策结果
        """
        try:
            logger.info("[DecisionMaker] 开始生成交易决策...")
            
            # 分析市场数据
            analysis = self.analyze_market_data(market_data)
            
            # 提取关键指标
            quote = market_data.get('stock_quote', {})
            fund = market_data.get('fund_flow', {})
            
            change_pct = quote.get('change_pct', 0)
            north_inflow = fund.get('north_inflow', 0)
            
            # 判断市场环境
            market_env = "中性"
            if change_pct > 0 and north_inflow > 0:
                market_env = "偏多"
            elif change_pct < 0 and north_inflow < 0:
                market_env = "偏空"
            
            # 判断风险等级
            risk_level = "低"
            if abs(change_pct) > 3:
                risk_level = "中"
            if abs(change_pct) > 5:
                risk_level = "高"
            
            # 生成买卖建议
            action = "观望"
            entry_point = quote.get('price', 0) * 0.98  # 回调2%入场
            stop_loss = quote.get('price', 0) * 0.97  # 回调3%止损
            take_profit = quote.get('price', 0) * 1.06  # 涨6%止盈
            
            if market_env == "偏多" and risk_level in ["低", "中"]:
                action = "买入"
            elif market_env == "偏空" or risk_level == "高":
                action = "减仓或观望"
            else:
                action = "观望"
            
            # 生成决策结论
            if LITELM_AVAILABLE and self.api_key:
                decision_text = self._llm_decision(analysis, market_data)
            else:
                decision_text = self._mock_decision(analysis, market_data)
            
            # 生成检查清单
            checklist = self._generate_checklist(market_data)
            
            logger.info(f"[DecisionMaker] 交易决策生成完成: {action}")
            
            return {
                'analysis': analysis,
                'decision': decision_text,
                'action': action,
                'entry_point': f"{entry_point:.2f}元",
                'stop_loss': f"{stop_loss:.2f}元",
                'take_profit': f"{take_profit:.2f}元",
                'market_env': market_env,
                'risk_level': risk_level,
                'checklist': checklist,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            logger.error(f"[DecisionMaker] 生成交易决策失败: {e}")
            return {
                'error': f"生成决策失败: {e}",
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def _llm_decision(self, analysis: str, market_data: Dict[str, Any]) -> str:
        """
        使用LLM生成决策
        """
        try:
            prompt = f"""你是一位专业的股票分析师。请根据以下市场数据，生成简洁的交易决策建议：

{analysis}

要求：
1. 用一句话总结市场环境（偏多/偏空/中性）
2. 给出明确的买卖建议（买入/减仓/观望）
3. 提供买卖点位
4. 列出3-5条关键风险点
5. 控制在200字以内

请直接输出决策建议，不要重复问题。"""
            
            response = completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的股票分析师。"},
                    {"role": "user", "content": prompt}
                ],
                api_key=self.api_key,
                temperature=0.7,
                max_tokens=300
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"[DecisionMaker] LLM决策生成失败: {e}")
            return self._mock_decision(analysis, market_data)
    
    def _mock_decision(self, analysis: str, market_data: Dict[str, Any]) -> str:
        """
        Mock决策生成（无LLM时使用）
        """
        try:
            quote = market_data.get('stock_quote', {})
            fund = market_data.get('fund_flow', {})
            
            name = quote.get('name', 'N/A')
            change_pct = quote.get('change_pct', 0)
            north_inflow = fund.get('north_inflow', 0)
            
            # Mock决策逻辑
            if change_pct > 2 and north_inflow > 30:
                decision = f"{name}走势强劲，北向资金大幅流入，市场环境偏多。建议回调{2}%后买入，目标涨幅6%，止损3%。风险：短期涨幅过大，注意回调。"
            elif change_pct < -2:
                decision = f"{name}走势偏弱，建议观望或轻仓试错。如果跌破支撑位，及时止损。"
            elif change_pct > 0 and north_inflow > 0:
                decision = f"{name}稳步上涨，北向资金持续流入，可适当建仓。建议分批买入，控制仓位。"
            else:
                decision = f"{name}震荡整理，建议观望，等待明确信号。"
            
            return decision
            
        except Exception as e:
            logger.error(f"[DecisionMaker] Mock决策生成失败: {e}")
            return "市场分析不足，建议观望。"
    
    def _generate_checklist(self, market_data: Dict[str, Any]) -> List[str]:
        """
        生成检查清单
        """
        try:
            checklist = []
            
            quote = market_data.get('stock_quote', {})
            fund = market_data.get('fund_flow', {})
            
            # 1. 技术指标检查
            change_pct = quote.get('change_pct', 0)
            
            if change_pct > 0:
                checklist.append("✓ 价格上涨，趋势向上")
            elif change_pct < 0:
                checklist.append("✗ 价格下跌，趋势向下")
            else:
                checklist.append("○ 价格平盘，震荡整理")
            
            # 2. 资金流向检查
            north_inflow = fund.get('north_inflow', 0)
            
            if north_inflow > 30:
                checklist.append("✓ 北向资金大幅流入")
            elif north_inflow > 0:
                checklist.append("✓ 北向资金净流入")
            elif north_inflow < -50:
                checklist.append("✗ 北向资金大幅流出")
            else:
                checklist.append("○ 北向资金平衡")
            
            # 3. 融资余额检查
            margin_growth = fund.get('margin_growth', 0)
            
            if margin_growth > 5:
                checklist.append("✓ 融资余额增长")
            elif margin_growth < -5:
                checklist.append("✗ 融资余额下降")
            else:
                checklist.append("○ 融资余额稳定")
            
            # 4. 新闻舆情检查
            news = market_data.get('news', [])
            
            if news and len(news) > 0:
                top_news = sorted(news, key=lambda x: x.get('score', 0), reverse=True)[0]
                if top_news.get('score', 0) > 0.7:
                    checklist.append(f"✓ 利好新闻: {top_news['title'][:30]}...")
                else:
                    checklist.append("○ 新闻中性")
            else:
                checklist.append("○ 暂无新闻")
            
            return checklist
            
        except Exception as e:
            logger.error(f"[DecisionMaker] 生成检查清单失败: {e}")
            return ["生成检查清单失败"]
    
    def generate_dashboard(self, decision: Dict[str, Any]) -> str:
        """
        生成决策仪表盘文本
        
        参数:
            decision: 决策结果字典
        
        返回:
            str: 仪表盘文本
        """
        try:
            logger.info("[DecisionMaker] 生成决策仪表盘...")
            
            dashboard = f"""
{'='*80}
LLM决策仪表盘
{'='*80}
生成时间: {decision.get('timestamp', 'N/A')}

【交易决策】
{decision.get('decision', 'N/A')}

【操作建议】
- 操作方向: {decision.get('action', 'N/A')}
- 入场点位: {decision.get('entry_point', 'N/A')}
- 止损位: {decision.get('stop_loss', 'N/A')}
- 止盈位: {decision.get('take_profit', 'N/A')}
- 市场环境: {decision.get('market_env', 'N/A')}
- 风险等级: {decision.get('risk_level', 'N/A')}

【检查清单】
{chr(10).join(decision.get('checklist', []))}

【市场分析】
{decision.get('analysis', 'N/A')}

{'='*80}
"""
            
            return dashboard
            
        except Exception as e:
            logger.error(f"[DecisionMaker] 生成决策仪表盘失败: {e}")
            return "生成仪表盘失败。"


# 测试函数
def test_decision_maker():
    """测试DecisionMaker"""
    print("="*80)
    print("测试DecisionMaker - LLM决策Agent")
    print("="*80)
    
    # 创建DecisionMaker实例
    # 注意：需要配置DEEPSEEK_API_KEY环境变量
    maker = DecisionMaker()
    
    # 准备测试数据（贵州茅台）
    market_data = {
        'stock_quote': {
            'code': '600519.SH',
            'name': '贵州茅台',
            'price': 1440.00,
            'change_pct': 0.5
        },
        'fund_flow': {
            'north_inflow': 30.0,  # 亿元
            'margin_growth': 5.0,     # %
        },
        'news': [
            {
                'title': '贵州茅台2025年业绩超预期，机构上调评级',
                'score': 0.9,
                'url': 'https://example.com'
            },
            {
                'title': '贵州茅台新产品上市，销量突破预期',
                'score': 0.8,
                'url': 'https://example.com'
            },
            {
                'title': '贵州茅台股价创新高，短期回调风险增加',
                'score': 0.6,
                'url': 'export://example.com'
            }
        ]
    }
    
    # 生成决策
    print("\n【步骤1】生成交易决策...")
    decision = maker.generate_decision(market_data)
    
    print("\n【步骤2】生成决策仪表盘...")
    dashboard = maker.generate_dashboard(decision)
    
    print(dashboard)
    
    print("\n" + "="*80)
    print("✅ DecisionMaker测试完成！")
    print("="*80)
    
    return decision


if __name__ == '__main__':
    test_decision_maker()
