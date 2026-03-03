#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI回测 & 图片识别 - 评估历史警报准确率和命中率
使用LLM + Vision LLM（Gemini）
"""
import pandas as pd
import logging
from datetime import datetime, timedelta, date
import json
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AI_Backtester:
    """AI回测Agent - 评估历史警报准确率和命中率"""
    
    def __init__(self, api_key=None):
        self.name = "AI_Backtester"
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        # LLM配置
        self.model = "gemini-1.5-pro"
        self.temperature = 0.7
        self.max_tokens = 500
        
        # 回测参数
        self.lookback_days = 30  # 回测最近30天
        self.accuracy_threshold = 0.6  # 准确率阈值
        self.hit_rate_threshold = 0.7    # 命中率阈值
        
        # 统计数据
        self.stats = {
            'total_signals': 0,
            'correct_signals': 0,
            'wrong_signals': 0,
            'accuracy': 0.0,
            'hit_rate': 0.0
            'false_positives': 0,
            'false_negatives': 0
        }
        
        # 历史警报记录
        self.alert_history = []
    
    def load_alert_history(self, alert_file=None):
        """
        加载历史警报记录
        
        参数:
            alert_file: 警报文件路径
        
        返回:
            DataFrame: 警报历史
        """
        try:
            if alert_file is None:
                alert_file = './output/alerts_history.json'
            
            if not os.path.exists(alert_file):
                logger.warning(f"[AI_Backtester] 警报历史文件不存在: {alert_file}")
                return None
            
            # 读取JSON文件
            with open(alert_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                df = pd.DataFrame(data)
            
            # 转换日期格式
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
            
            logger.info(f"[AI_Backtester] 警报历史加载成功: {len(df)} 条记录")
            return df
            
        except Exception as e:
            logger.error(f"[AI_Backtester] 加载警报历史失败: {e}")
            return None
    
    def calculate_accuracy(self, alerts_df, results_df):
        """
        计算准确率和命中率
        
        参数:
            alerts_df: 警报DataFrame
            results_df: 实际结果DataFrame
        
        返回:
            dict: 统计数据
        """
        try:
            logger.info("[AI_Backtester] 开始计算准确率...")
            
            if alerts_df is None or results_df is None:
                return self.stats
            
            # 合并警报和实际结果
            merged = pd.merge(alerts_df, results_df, on=['date', 'symbol'], how='inner')
            
            if merged.empty:
                logger.warning("[AI_Backtester] 无匹配数据，无法计算准确率")
                return self.stats
            
            # 计算总信号数
            self.stats['total_signals'] = len(merged)
            
            # 计算正确信号
            correct_direction = (merged['predicted_direction'] == merged['actual_direction'])
            correct_points = (merged['predicted_point'] <= merged['actual_high']) & (merged['predicted_point'] >= merged['actual_low'])
            
            self.stats['correct_signals'] = correct_direction.sum()
            self.stats['hit_rate'] = correct_points.sum() / len(merged)
            
            # 计算错误信号
            self.stats['false_positives'] = ((merged['predicted_direction'] == 'up') & (merged['actual_direction'] == 'down')).sum()
            self.stats['false_negatives'] = ((merged['predicted_direction'] == 'down') & (merged['actual_direction'] == 'up')).sum()
            
            # 计算准确率
            self.stats['accuracy'] = self.stats['correct_signals'] / self.stats['total_signals']
            
            # 计算方向准确率
            if 'predicted_direction' in merged.columns:
                direction_accuracy = (merged['predicted_direction'] == merged['actual_direction']).sum() / len(merged)
                self.stats['direction_accuracy'] = direction_accuracy
            
            logger.info(f"[AI_Backtester] 准确率计算完成")
            logger.info(f"  总信号数: {self.stats['total_signals']}")
            logger.info(f"  命中率: {self.stats['hit_rate']:.2%}")
            logger.info(f"  方向准确率: {self.stats.get('direction_accuracy', 0):.2%}")
            logger.info(f"  假阳性: {self.stats['false_positives} 个")
            logger.info(f"  假阴性: {self.stats['false_negatives'] 个")
            
            return self.stats
            
        except Exception as e:
            logger.error(f"[AI_Backtester] 计算准确率失败: {e}")
            return self.stats
    
    def analyze_alert_performance(self, fund_type):
        """
        分析警报性能（按资金类型）
        
        参数:
            fund_type: 资金类型（margin/north_south/institutional/lhb/stock_flow）
        
        返回:
            dict: 分析结果
        """
        try:
            logger.info(f"[AI_Backtester] 分析{fund_type}警报性能...")
            
            # 加载警报历史
            alerts_df = self.load_alert_history()
            
            if alerts_df is None:
                logger.warning(f"[AI_Backtester] 未找到警报历史")
                return None
            
            # 按资金类型过滤
            if fund_type and 'fund_type' in alerts_df.columns:
                df = alerts_df[alerts_df['fund_type'] == fund_type].copy()
            else:
                df = alerts_df.copy()
            
            if df.empty:
                logger.warning(f"[AI_Backtester] 未找到{fund_type}警报数据")
                return None
            
            # 计算每日警报数量
            daily_alerts = df.groupby(['date', 'fund_type']).size().reset_index()
            daily_alerts.columns = ['date', 'fund_type', 'alert_count']
            
            # 计算警报类型分布
            alert_type_dist = df.groupby('alert_type').size().reset_index()
            
            # 计算风险等级分布
            if 'risk_level' in df.columns:
                risk_dist = df.groupby('risk_level').size().reset_index()
            
            logger.info(f"[AI_Backtester] {fund_type}警报分析完成")
            logger.info(f"  历史警报数: {len(df)} 条")
            logger.info(f"  日期范围: {df['date'].min()} 至 {df['date'].max()}")
            logger.info(f"  警报类型分布: {dict(alert_type_dist)}")
            
            return {
                'df': df,
                'daily_alerts': daily_alerts,
                'alert_type_dist': dict(alert_type_dist),
                'risk_dist': dict(risk_dist),
                'fund_type': fund_type
            }
            
        except Exception as e:
            logger.error(f"[AI_Backtester] 分析警报性能失败: {e}")
            return None
    
    def generate_llm_report(self, stats, fund_type):
        """
        生成LLM回测报告
        
        参数:
            stats: 统计数据
            fund_type: 资金类型
        
        返回:
            str: 回测报告
        """
        try:
            logger.info(f"[AI_Backtester] 生成{fund_type}LLM回测报告...")
            
            # 判断准确率等级
            accuracy = stats.get('accuracy', 0)
            hit_rate = stats.get('hit_rate', 0)
            
            if accuracy >= 0.7:
                accuracy_level = "优秀"
            elif accuracy >= 0.6:
                accuracy_level = "良好"
            elif accuracy >= 0.5:
                accuracy_level = "及格"
            else:
                accuracy_level = "需要优化"
            
            # 判断胜率等级
            if hit_rate >= 0.8:
                hit_rate_level = "优秀"
            elif hit_rate >= 0.7:
                hit_rate_level = "良好"
            elif hit_rate >= 0.6:
                hit_rate_level = "及格"
            else:
                hit_rate_level = "需要优化"
            
            # 生成报告
            report = f"""
【{fund_type}回测报告】

【准确率分析】
- 总信号数：{stats.get('total_signals', 0)} 个
- 正确信号数：{stats.get('correct_signals', 0)} 个
- 命中率：{stats.get('hit_rate', 0):.2%}
- 方向准确率：{stats.get('direction_accuracy', 0):.2%}（趋势判断）
- 准确率等级：{accuracy_level}（阈值：{self.accuracy_threshold}）
- 胜率等级：{hit_rate_level}（阈值：{self.hit_rate_threshold}）

【错误分析】
- 假阳性：{stats.get('false_positives', 0)} 个（错误看多，应该观望）
- 假阴性：{stats.get('false_negatives, 0)} 个（错过机会，应该买入）
- 错误率：{(stats.get('false_positives', 0) + stats.get('false_negatives', 0)) / max(stats.get('total_signals', 1):.2%}

【优化建议】
"""
            
            if accuracy_level == "优秀":
                report += f"✓ {fund_type}策略表现优秀，继续使用！\n"
            elif accuracy_level == "良好":
                report += f"✓ {fund_type}策略表现良好，可适当优化。\n"
            elif accuracy_level == "及格":
                report += f"⚠️ {fund_type}策略表现一般，需要优化。\n"
            else:
                report += f"❌ {fund_type}策略表现较差，紧急优化！\n"
            
            if hit_rate_level == "优秀":
                report += f"✓ 盈利能力优秀，可适当增加仓位\n"
            elif hit_rate_level == "良好":
                report += f"✓ 盈利能力良好，保持现状\n"
            elif hit_rate_level == "及格":
                report += f"⚠️ 盈利能力一般，控制仓位\n"
            else:
                report += f"❌ 盈利能力较差，减少仓位或停止使用\n"
            
            # 具体优化建议
            report += f"""
【具体优化建议】

1. 准确率优化（当前{accuracy:.1f}%）
   - 提高{fund_type}数据质量
   - 增加技术指标验证
   - 优化信号生成逻辑

2. 降低假阳性
   - 增加成交量确认
   - 添加多指标共振确认
   - 延迟信号确认时间

3. 降低假阴性
   - 优化阈值参数
   - 增加辅助指标
   - 增加预判断逻辑

4. 命中率优化（当前{hit_rate:.1f}%）
   - 优化入场点位计算
   - 调整止损止盈比例
   - 优化分批建仓策略
"""
            
            report += "---
*本报告由AI Backtester自动生成*"
            
            logger.info(f"[AI_Backtester] LLM回测报告生成完成")
            return report
            
        except Exception as e:
            logger.error(f"[AI_Backtester] 生成LLM报告失败: {e}")
            return "生成LLM报告失败。"
    
    def evaluate_current_strategy(self, fund_type, alerts):
        """
        评估当前策略表现
        
        参数:
            fund_type: 资金类型
            alerts: 当前警报列表
        
        返回:
            dict: 评估结果
        """
        try:
            logger.info(f"[AI_Backtester] 评估{fund_type}当前策略...")
            
            # 判断风险等级
            high_risk_count = len([a for a in alerts if 'high' in a.lower()])
            medium_risk_count = len([a for a in alerts if 'medium' in a.lower()])
            
            if high_risk_count > 3:
                strategy_status = "高风险"
                strategy_suggestion = "建议减仓观望"
            elif high_risk_count > 0:
                strategy_status = "中风险"
                strategy_suggestion = "建议控制仓位"
            elif medium_risk_count > 2:
                strategy_status = "中风险"
                strategy_suggestion = "建议谨慎操作"
            else:
                strategy_status = "低风险"
                strategy_suggestion = "正常操作"
            
            logger.info(f"[AI_Backtester] 策略评估完成: {strategy_status}")
            
            return {
                'fund_type': fund_type,
                'strategy_status': strategy_status,
                'strategy_suggestion': strategy_suggestion,
                'high_risk_count': high_risk_count,
                'medium_rount': medium_risk_count,
                'total_alerts': len(alerts)
            }
            
        except Exception as e:
            logger.error(f"[AI_Backtester] 评估当前策略失败: {e}")
            return {}


class Vision_LLM:
    """视觉LLM - 图片识别Agent使用Gemini Vision识别"""
    
    def __init__(self, api_key=None):
        self.name = "Vision_LLM"
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        # Gemini Vision模型
        self.model = "gemini-1.5-pro-vision"
        self.temperature = 0.4
        self.max_tokens = 500
        
        if self.api_key:
            logger.info("[Vision_LLM] Gemini Vision客户端初始化成功")
        else:
            logger.warning("[Vision_LLM] 未配置Gemini API密钥，使用Mock模式")
    
    def extract_stock_code(self, image_path):
        """
        从图片中提取股票代码
        
        参数:
            image_path: 图片路径
        
        返回:
            str: 股票代码（如"600519.SH"）
        """
        try:
            logger.info(f"[Vision_LLM] 从图片提取股票代码: {image_path}")
            
            if not os.path.exists(image_path):
                logger.error(f"[Vision_LLM] 图片不存在: {image_path}")
                return None
            
            # 使用Mock模式
            if not self.api_key:
                logger.warning("[Vision_LLM] 未配置Gemini API，使用Mock模式")
                
                # Mock识别结果
                mock_results = {
                    '/root/.openclaw/workspace/FundsMonitor/output/charts/margin_trend_*.png': '600519.SH',  # 贵州茅台K线图
                    '/root/.openclaw/workspace/FundsMonitor/output/charts/north_south_trend_*.png': '000001.SZ',  # 平安银行K线图
                    '/root/.openclaw/workspace/FundsMonitor/output/charts/lhb_heatmap_*.png': '600498.SH',  # 烽火通信热力图
                }
                
                return mock_results.get(image_path, 'N/A')
            
            # 使用Gemini Vision API
            # 注意：需要安装google-cloud-storage和google-cloud-vision
            # 这里先返回Mock，实际需要配置API
            
            logger.info(f"[Vision_LLM] 股票代码提取完成")
            return 'Mock模式：股票代码识别'
            
        except Exception as e:
            logger.error(f"[Vision_LLM] 提取股票代码失败: {e}")
            return None
    
    def analyze_chart(self, image_path):
        """
        分析图表（K线图、热力图等）
        
        参数:
            image_path: 图片路径
        
        返回:
            dict: 分析结果
        """
        try:
            logger.info(f"[Vision_LLM] 分析图表: {image_path}")
            
            if not os.path.exists(image_path):
                logger.error(f"[Vision_LLM] 图片不存在: {image_path}")
                return None
            
            # 判断图表类型
            filename = os.path.basename(image_path)
            
            if 'margin' in filename or 'margin' in filename:
                chart_type = 'margin_trend'
            elif 'north' in filename or 'north_south' in filename:
                chart_type = 'north_south_trend'
            elif 'lhb' in filename or 'heat' in filename:
                chart_type = 'lhb_heatmap'
            else:
                chart_type = 'unknown'
            
            # 使用Mock模式
            if not self.api_key:
                logger.warning("[Vision_LLM] 未配置Gemini API，使用Mock模式")
                
                # Mock分析结果
                mock_results = {
                    'margin_trend': {
                        'trend': 'up',
                        'trend_strength': 'strong',
                        'ma_status': 'golden_cross',
                        'volume_status': 'increasing',
                        'summary': '融资余额上升，均线金叉，成交量放大，趋势向上'
                    },
                    'north_south_trend': {
                        'trend': 'up',
                        'trend_strength': 'moderate',
                        'flow_status': 'net_inflow',
                        'summary': '北向资金净流入，市场看好'
                    },
                    'lhb_heatmap': {
                        'hot_count': 5,
                        'market_condition': 'hot',
                        'top_stocks': [
                            {'name': '烽火通信', 'inst_ratio': 0.66},
                            {'name': '浪潮信息', 'inst_ratio': 0.67},
                            {'name': '中科曙光', 'inst_ratio': 0.65}
                        ],
                        'summary': '市场过热，龙虎榜热点过多，需谨慎'
                    }
                }
                
                return mock_results.get(chart_type, {})
            
            # 使用Gemini Vision API
            # 注意：需要配置API并实现
            logger.info(f"[Vision_LLM] 图表分析完成: {chart_type}")
            return f"Mock模式：{chart_type}图表分析"
            
        except Exception as e:
            logger.error(f"[Vision_LLM] 分析图表失败: {e}")
            return None


# 测试函数
def test_ai_backtester():
    """测试AI回测功能"""
    print('='*80)
    print("测试AI Backtester - 回测功能")
    print('='*80)
    
    # 创建实例
    backtester = AI_Backtester()
    
    # 测试1：计算准确率
    print("\n【测试1】计算准确率（测试数据）")
    
    # 创建测试数据
    alerts_df = pd.DataFrame({
        'date': pd.date_range(start='2026-02-01', end='2026-03-03'),
        'symbol': ['600519.SH'] * 20 + ['300750.SZ'] * 20,
        'fund_type': ['margin'] * 40,
        'alert_type': ['买入', '减仓', '观望', '买入', '减仓'],
        'predicted_direction': ['up', 'down', 'hold', 'up', 'down', 'hold', 'up', 'down'],
        'predicted_point': [1420.0 + i*2 for i in range(40)],
        'actual_direction': ['up', 'down', 'up', 'up', 'up', 'up', 'down'],
        'actual_high': [1430.0 + i*3 for i in range(40)],
        'actual_low': [1410.0 + i*1 for i in range(40)]
    })
    
    results_df = pd.DataFrame({
        'date': pd.date_range(start='2026-02-01', end='2026-03-03'),
        'symbol': ['600519.SH'] * 20 + ['300750.SZ'] * 20,
        'actual_direction': ['up', 'down', 'up', 'up', 'up', 'up', 'down'],
        'actual_high': [1430.0 + i*3 for i in range(40)],
        'actual_low': [1410.0 + i*1 for i in range(40)]
    })
    
    stats = backtester.calculate_accuracy(alerts_df, results_df)
    
    print(f"✓ 准确率: {stats['accuracy']:.1%}")
    print(f"✓ 命中率: {stats['hit_rate']:.1%}")
    print(f"  假阳性: {stats['false_positives']} 个")
    print(f"  假阴性: {stats['false_negatives']} 个")
    
    # 测试2：分析警报性能
    print("\n【测试2】分析警报性能（两融）")
    result = backtester.analyze_alert_performance('margin')
    
    if result:
        print(f"✓ {result['fund_type']}分析完成")
        print(f"  历史警报数: {len(result['df'])} 条")
        print(f"  警报类型分布: {result['alert_type_dist']}")
    else:
        print("✗ 警报分析失败")
    
    # 测试3：生成LLM报告
    print("\n【测试3】生成LLM回测报告")
    report = backtester.generate_llm_report(stats, 'margin')
    print(report)
    
    # 测试4：Vision LLM图片识别
    print("\n【测试4】Vision LLM图片识别")
    vision = Vision_LLM()
    
    mock_images = [
        '/root/.openclaw/workspace/FundsMonitor/output/charts/margin_trend_*.png',
        '/root/.openclaw/workspace/FundsMonitor/output/charts/north_south_trend_*.png',
        '/root/.openclaw/workspace/FundsMonitor/output/charts/lhb_heatmap_*.png'
    ]
    
    for image_path in mock_images:
        result = vision.extract_stock_code(image_path)
        if result:
            print(f"✓ {image_path}: {result}")
        else:
            print(f"✗ {image_path}: 识别失败")
    
    print('\n' + '='*80)
    print('✅ AI Backtester & Vision LLM测试完成！')
    print('='*80)
    
    return stats


if __name__ == '__main__':
    test_ai_backtester()
