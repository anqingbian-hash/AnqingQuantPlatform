#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StrategyLoader - YAML策略加载器
支持均线金叉、缠论、动量等策略类型
"""
import pandas as pd
import yaml
import logging
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class StrategyLoader:
    """策略加载器"""
    
    def __init__(self, strategies_dir='./strategies'):
        self.name = "StrategyLoader"
        self.strategies_dir = strategies_dir
        
        # 创建策略目录
        os.makedirs(strategies_dir, exist_ok=True)
        
        # 默认策略
        self.default_strategy = {
            'name': '均线金叉策略',
            'type': 'ma_cross',
            'timeframe': '1D',
            'ma_short': 5,
            'ma_long': 20,
            'stop_loss': 0.03,
            'take_profit': 0.06,
            'position_size': 0.2,
            'risk_limit': 0.01,
            'max_trades_per_day': 3,
            'conditions': {
                'trend': 'bull',  # bull/bear/neutral
                'volume_increase': True,
                'rsi_range': [30, 70]
            }
        }
        
        logger.info(f"[StrategyLoader] 初始化完成，策略目录: {strategies_dir}")
    
    def load_strategy(self, strategy_file=None):
        """
        加载YAML策略文件
        
        参数:
            strategy_file: 策略文件路径
        
        返回:
            dict: 策略配置
        """
        try:
            if strategy_file is None:
                strategy_file = os.path.join(self.strategies_dir, 'default.yaml')
            
            logger.info(f"[StrategyLoader] 加载策略文件: {strategy_file}")
            
            # 读取YAML文件
            with open(strategy_file, 'r', encoding='utf-8') as f:
                strategy = yaml.safe_load(f)
            
            if strategy is None:
                logger.warning(f"[StrategyLoader] 策略文件为空，使用默认策略")
                return self.default_strategy
            
            # 验证策略配置
            self._validate_strategy(strategy)
            
            logger.info(f"[StrategyLoader] 策略加载成功: {strategy.get('name', '未命名')}")
            return strategy
            
        except FileNotFoundError:
            logger.warning(f"[StrategyLoader] 策略文件不存在，使用默认策略: {strategy_file}")
            return self.default_strategy
        except Exception as e:
            logger.error(f"[StrategyLoader] 加载策略失败: {e}")
            return self.default_strategy
    
    def save_strategy(self, strategy, filename=None):
        """
        保存策略到YAML文件
        
        参数:
            strategy: 策略配置字典
            filename: 文件名（默认：策略名.yaml）
        """
        try:
            if filename is None:
                filename = f"{strategy.get('name', 'strategy')}.yaml"
            
            filepath = os.path.join(self.strategies_dir, filename)
            
            # 保存YAML文件
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(strategy, f, allow_unicode=True, default_flow_style=False)
            
            logger.info(f"[StrategyLoader] 策略保存成功: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"[Strategy] 保存策略失败: {e}")
            return None
    
    def _validate_strategy(self, strategy):
        """
        验证策略配置
        """
        try:
            # 检查必填字段
            required_fields = ['name', 'type', 'timeframe', 'stop_loss', 'take_profit', 'position_size']
            
            for field in required_fields:
                if field not in strategy:
                    logger.warning(f"[StrategyLoader] 缺少必填字段: {field}，使用默认值")
                    strategy[field] = self.default_strategy[field]
            
            # 验证策略类型
            strategy_type = strategy.get('type', 'ma_cross')
            if strategy_type not in ['ma_cross', 'chanlun', 'momentum', 'breakout']:
                logger.warning(f"[StrategyLoader] 未知策略类型: {strategy_type}")
                strategy['type'] = 'ma_cross'
            
            # 验证时间周期
            timeframe = strategy.get('timeframe', '1D')
            if timeframe not in ['1m', '5m', '15m', '30m', '1h', '1D', '1W']:
                logger.warning(f"[StrategyLoader] 未知时间周期: {timeframe}")
                strategy['timeframe'] = '1D'
            
            # 验证止损止盈
            stop_loss = strategy.get('stop_loss', 0.03)
            if not (0 < stop_loss < 1):
                logger.warning(f"[StrategyLoader] 止损比例超出范围(0, 1): {stop_loss}，使用默认值0.03")
                strategy['stop_loss'] = 0.03
            
            take_profit = strategy.get('take_profit', 0.06)
            if not (0 < take_profit < 1):
                logger.warning(f"[StrategyLoader] 止盈比例超出范围(0, 1): {take_profit}，使用默认值0.06")
                strategy['take_profit'] = 0.06
            
            # 验证仓位大小
            position_size = strategy.get('position_size', 0.2)
            if not (0 < position_size < 1):
                logger.warning(f"[StrategyLoader] 仓位大小超出范围(0, 1): {position_size}，使用默认值0.2")
                strategy['position_size'] = 0.2
            
            # 验证风险限制
            risk_limit = strategy.get('risk_limit', 0.01)
            if not (0 < risk_limit < 0.05):
                logger.warning(f"[StrategyLoader] 风险限制超出范围(0, 0.05): {risk_limit}，使用默认值0.01")
                strategy['risk_limit'] = 0.01
            
            logger.info(f"[StrategyLoader] 策略验证通过: {strategy.get('name', '未命名')}")
            
        except Exception as e:
            logger.error(f"[StrategyLoader] 策略验证失败: {e}")
    
    def create_ma_cross_strategy(self):
        """创建均线金叉策略YAML"""
        try:
            strategy = {
                'name': '均线金叉策略',
                'type': 'ma_cross',
                'timeframe': '1D',
                'description': '短期均线上穿长期均线，金叉买入，死叉卖出',
                'indicators': {
                    'ma_short': 5,  # 短期均线周期
                    'ma_long': 20,  # 长期均线周期
                    'volume_avg': 20  # 成交量均线周期
                },
                'entry_conditions': {
                    'golden_cross': True,  # 金叉买入
                    'volume_confirm': True,  # 成交量确认
                    'trend_filter': 'bull'  # 只做多
                },
                'exit_conditions': {
                    'death_cross': True,  # 死叉卖出
                    'stop_loss': 0.03,  # 3%止损
                    'take_profit': 0.06,  # 6%止盈
                },
                'risk_management': {
                    'position_size': 0.2,  # 20%仓位
                    'max_positions': 5,  # 最多5个仓位
                    'daily_loss_limit': 0.01  # 单日亏损限制1%
                }
            }
            
            # 保存策略
            filepath = self.save_strategy(strategy)
            logger.info(f"[StrategyLoader] 均线金叉策略创建成功: {filepath}")
            
            return strategy
            
        except Exception as e:
            logger.error(f"[StrategyLoader] 创建均线金叉策略失败: {e}")
            return None
    
    def create_chanlun_strategy(self):
        """创建缠论策略YAML"""
        try:
            strategy = {
                'name': '缠论策略',
                'type': 'chanlun',
                'type2': 'chanlun',
                'timeframe': '30m',
                'description': '基于缠论的买卖点判断，支持中枢、盘整、趋势等',
                'indicators': {
                    'bi': 5,          # 短期均线
                    'ch': 20,         # 长期均线
                    'ch_type': 'zhongshu',  # 中枢类型：zhongshu/panzheng
                    'zhongshu': {
                        'high': 'high',  # 上沿
                        'low': 'low',    # 下沿
                        'middle': 'middle'  # 中轨
                    }
                },
                'entry_conditions': {
                    'type1_buy': True,  # 一类买点
                    'type2_buy': True,  # 二类买点
                    'volume_confirm': True,
                    'trend': 'up'
                },
                'exit_conditions': {
                    'type1_sell': True,  # 一类卖点
                    'type2_sell': True,  # 二类卖点
                    'stop_loss': 0.05,
                    'take_profit': 0.1
                },
                'risk_management': {
                    'position_size': 0.1,  # 10%仓位（缠论高风险）
                    'max_positions': 3,
                    'daily_loss_limit': 0.02
                }
            }
            
            # 保存策略
            filepath = self.save_strategy(strategy)
            logger.info(f"[StrategyLoader] 缠论策略创建成功: {filepath}")
            
            return strategy
            
        except Exception as e:
            logger.error(f"[StrategyLoader] 创建缠论策略失败: {e}")
            return None
    
    def generate_sample_strategies(self):
        """生成示例策略"""
        try:
            logger.info("[StrategyLoader] 生成示例策略...")
            
            strategies = []
            
            # 1. 均线金叉策略
            ma_cross = self.create_ma_cross_strategy()
            if ma_cross:
                strategies.append(ma_cross)
            
            # 2. 缠论策略
            chanlun = self.create_chanlun_strategy()
            if chanlun:
                strategies.append(chanlun)
            
            logger.info(f"[StrategyLoader] 示例策略生成完成: {len(strategies)} 个")
            
            return strategies
            
        except Exception as e:
            logger.error(f"[StrategyLoader] 生成示例策略失败: {e}")
            return []


# 测试函数
def test_strategy_loader():
    """测试策略加载器"""
    print("="*80)
    print("测试StrategyLoader - YAML策略加载器")
    print("="*80)
    
    # 创建StrategyLoader实例
    loader = StrategyLoader(strategies_dir='./strategies')
    
    # 测试1: 生成示例策略
    print("\n【测试1】生成示例策略...")
    strategies = loader.generate_sample_strategies()
    
    if strategies:
        print(f"✓ 示例策略生成成功: {len(strategies)} 个")
        for i, strategy in enumerate(strategies):
            print(f"  {i+1}. {strategy.get('name', '未命名')}")
            print(f"     类型: {strategy.get('type', 'N/A')}")
            print(f"     描述: {strategy.get('description', 'N/A')}")
    else:
        print("✗ 示例策略生成失败")
    
    # 测试2: 加载策略文件
    print("\n【测试2】加载策略文件...")
    loaded = loader.load_strategy()
    
    if loaded:
        print(f"✓ 策略加载成功")
        print(f"  名称: {loaded.get('name', 'N/A')}")
        print(f"  类型: {loaded.get('type', 'N/A')}")
        print(f"  时间周期: {loaded.get('timeframe', 'N/A')")
        print(f"  止损: {loaded.get('stop_loss', 'N/A')}")
        print(f"  止盈: {loaded.get('take_profit', 'N/A')}")
        print(f"  仓位: {loaded.get('position_size', 'N/A')}")
    else:
        print("✗ 策略加载失败")
    
    # 测试3: 验证YAML文件
    print("\n【测试3】验证YAML文件...")
    
    import os
    if os.path.exists('./strategies'):
        files = os.listdir('./strategies')
        print(f"✓ 策略目录存在，找到 {len(files)} 个YAML文件:")
        for i, file in enumerate(files):
            if file.endswith('.yaml'):
                print(f"  - {file}")
    else:
        print("⚠️ 策略目录不存在: ./strategies")
    
    print("\n" + "="*80)
    print("✅ StrategyLoader测试完成！")
    print("="*80)
    
    return True


if __name__ == '__main__':
    test_strategy_loader()
