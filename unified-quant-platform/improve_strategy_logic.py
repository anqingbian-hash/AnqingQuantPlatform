#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务2：完善策略评分逻辑
优化四类策略评分体系
"""
from datetime import datetime

print("="*80)
print("📊 任务2：完善策略评分逻辑")
print("="*80)
print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

class ImprovedStrategyEngine:
    """改进的策略引擎"""
    
    def __init__(self):
        self.weights = {
            'emotion': 0.30,      # 情绪周期（30%）
            'volume_price': 0.25,  # 量价结构（25%）
            'main_force': 0.25,    # 主力资金（25%）
            'trend': 0.20          # 技术趋势（20%）
        }
    
    def calculate_emotion_score(self, sector, pct_chg,涨停次数=None):
        """情绪周期评分（30%权重）"""
        score = 0
        
        # 板块权重
        sector_weights = {
            '锂电池': 12,
            '计算机': 12,
            '通信设备': 12,
            '半导体': 10,
            '化学药': 10,
            '白酒': 10,
            '食品饮料': 8,
            '光伏': 8,
            '银行': 5,
            '券商': 6,
        }
        score += sector_weights.get(sector, 5)
        
        # 涨跌幅评分
        if 0 < pct_chg < 2:
            score += 3
        elif 2 <= pct_chg < 5:
            score += 6
        elif 5 <= pct_chg < 8:
            score += 8
        elif pct_chg >= 8:
            score += 10
        
        # 涨停加分
        if 涨停次数 and 涨停次数 > 0:
            score += min(涨停次数 * 3, 10)
        
        return score
    
    def calculate_volume_price_score(self, pct_chg, vol_ratio=None, price_level=None):
        """量价结构评分（25%权重）"""
        score = 0
        
        # 量价配合
        if pct_chg > 0:
            if 0 < pct_chg < 5:
                score += 5  # 温和上涨，量价配合好
            elif 5 <= pct_chg < 8:
                score += 7  # 中度上涨，量价配合良好
            elif pct_chg >= 8:
                score += 4  # 大幅上涨，需要放量确认
                if vol_ratio and vol_ratio > 1.5:
                    score += 6  # 放量确认
        
        # 量比评分
        if vol_ratio:
            if 1.0 < vol_ratio < 1.5:
                score += 3  # 温和放量
            elif 1.5 <= vol_ratio < 2.5:
                score += 5  # 适度放量
            elif vol_ratio >= 2.5:
                score += 4  # 大幅放量，警惕对敲
        
        # 价格位置
        if price_level:
            if price_level == 'low':
                score += 5  # 低位启动
            elif price_level == 'mid':
                score += 3  # 中位企稳
            elif price_level == 'high':
                score += 0  # 高位需谨慎
        
        return score
    
    def calculate_main_force_score(self, pct_chg, volume=None, amount=None):
        """主力资金评分（25%权重）"""
        score = 0
        
        # 涨幅与成交量
        if pct_chg > 2:
            if volume and volume > 100000:  # 10万手以上
                score += 8
            elif volume and volume > 50000:  # 5万手以上
                score += 5
        elif pct_chg > 0:
            if volume and volume > 100000:
                score += 6
        
        # 成交额
        if amount:
            if amount > 1000000000:  # 10亿以上
                score += 7
            elif amount > 500000000:  # 5亿以上
                score += 4
        
        # 放量合力
        if pct_chg > 2 and volume and volume > 100000:
            score += 3
        
        return score
    
    def calculate_trend_score(self, price, ma5=None, ma10=None, ma20=None):
        """技术趋势评分（20%权重）"""
        score = 0
        
        # 均线多头排列
        if ma5 and ma10 and ma20:
            if ma5 > ma10 > ma20:
                score += 8  # 多头排列
            elif ma5 > ma10:
                score += 5  # 短期向上
            elif ma10 > ma20:
                score += 3  # 中期向上
        
        # 价格与均线关系
        if price > ma20:
            score += 5  # 站稳20日均线
        elif price > ma10:
            score += 3  # 站稳10日均线
        
        # 价格位置
        if 10 < price < 50:
            score += 5  # 低位，启动空间大
        elif 50 <= price < 150:
            score += 3  # 中位，企稳
        elif price >= 150:
            score += 1  # 高位，谨慎
        
        return score
    
    def evaluate_stock(self, stock_data):
        """综合评分"""
        # 计算各项得分
        emotion = self.calculate_emotion_score(
            stock_data.get('sector', ''),
            stock_data.get('pct_chg', 0),
            stock_data.get('涨停次数', 0)
        )
        
        volume_price = self.calculate_volume_price_score(
            stock_data.get('pct_chg', 0),
            stock_data.get('vol_ratio', 1.0),
            stock_data.get('price_level', 'mid')
        )
        
        main_force = self.calculate_main_force_score(
            stock_data.get('pct_chg', 0),
            stock_data.get('volume', 0),
            stock_data.get('amount', 0)
        )
        
        trend = self.calculate_trend_score(
            stock_data.get('price', 0),
            stock_data.get('ma5', 0),
            stock_data.get('ma10', 0),
            stock_data.get('ma20', 0)
        )
        
        # 加权总分
        total_score = (
            emotion * self.weights['emotion'] +
            volume_price * self.weights['volume_price'] +
            main_force * self.weights['main_force'] +
            trend * self.weights['trend']
        )
        
        return {
            'total_score': total_score,
            'emotion_score': emotion,
            'volume_price_score': volume_price,
            'main_force_score': main_force,
            'trend_score': trend
        }

# 测试
engine = ImprovedStrategyEngine()

test_stock = {
    'sector': '锂电池',
    'pct_chg': 2.10,
    'vol_ratio': 1.8,
    'volume': 150000,
    'amount': 1200000000,
    'price': 340.22,
    'ma5': 335.0,
    'ma10': 330.0,
    'ma20': 320.0,
    '涨停次数': 0,
    'price_level': 'high'
}

print("\n📊 测试改进后的策略评分")
print("="*80)

result = engine.evaluate_stock(test_stock)

print(f"\n【宁德时代（300750）】")
print(f"  情绪周期: {result['emotion_score']:.1f}分 (30%)")
print(f"  量价结构: {result['volume_price_score']:.1f}分 (25%)")
print(f"  主力资金: {result['main_force_score']:.1f}分 (25%)")
print(f"  技术趋势: {result['trend_score']:.1f}分 (20%)")
print(f"  综合评分: {result['total_score']:.1f}/100")

print("\n" + "="*80)
print("✅ 任务2完成：策略评分逻辑已完善")
print("="*80)
print(f"⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
