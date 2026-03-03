#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AKShare全接口整合器
包含：行情、资金流、龙虎榜、概念板块、财务数据
"""
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import time
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AKShareFullIntegrator:
    """AKShare全接口整合器"""
    
    def __init__(self, cache_ttl: int = 600):
        """初始化
        
        Args:
            cache_ttl: 缓存时间（秒），默认10分钟
        """
        self.cache = {}
        self.cache_ttl = cache_ttl
        logger.info("AKShare全接口整合器初始化完成")
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """检查缓存是否有效"""
        if cache_key not in self.cache:
            return False
        
        cached_time = datetime.fromisoformat(self.cache[cache_key]['timestamp'])
        return (datetime.now() - cached_time).total_seconds() < self.cache_ttl
    
    def _get_cache(self, cache_key: str) -> Optional[Any]:
        """获取缓存"""
        if self._is_cache_valid(cache_key):
            logger.info(f"[缓存] 从缓存获取: {cache_key}")
            return self.cache[cache_key]['data']
        return None
    
    def _set_cache(self, cache_key: str, data: Any):
        """设置缓存"""
        self.cache[cache_key] = {
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        logger.info(f"[缓存] 已缓存: {cache_key}")
    
    # ==================== 行情接口 ====================
    
    def get_realtime_quotes(self, symbols: List[str] = None) -> pd.DataFrame:
        """获取实时行情（支持沪深A股）"""
        cache_key = f"realtime_quotes_{symbols}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached
        
        logger.info("[AKShare] 获取实时行情: stock_zh_a_spot_em()")
        
        try:
            # 获取实时行情
            df = ak.stock_zh_a_spot_em()
            
            if symbols:
                # 筛选指定股票
                df = df[df['代码'].isin(symbols)]
            
            self._set_cache(cache_key, df)
            logger.info(f"[AKShare] 实时行情获取成功: {len(df)} 只股票")
            return df
            
        except Exception as e:
            logger.error(f"[AKShare] 实时行情获取失败: {e}")
            return pd.DataFrame()
    
    def get_stock_info(self, symbol: str) -> pd.DataFrame:
        """获取股票基本信息"""
        cache_key = f"stock_info_{symbol}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached
        
        logger.info(f"[AKShare] 获取股票基本信息: {symbol}")
        
        try:
            # 获取基本信息
            df = ak.stock_individual_info_em(symbol=symbol)
            
            self._set_cache(cache_key, df)
            logger.info(f"[AKShare] 股票基本信息获取成功: {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"[AKShare] 股票基本信息获取失败: {symbol}, {e}")
            return pd.DataFrame()
    
    def get_history_data(self, symbol: str, period: str = "daily", 
                     start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """获取历史行情数据
        
        Args:
            symbol: 股票代码
            period: 周期（daily/weekly/monthly）
            start_date: 开始日期（YYYYMMDD）
            end_date: 结束日期（YYYYMMDD）
        """
        cache_key = f"history_{symbol}_{period}_{start_date}_{end_date}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached
        
        logger.info(f"[AKShare] 获取历史行情: {symbol}, {period}")
        
        try:
            # 计算默认日期
            if end_date is None:
                end_date = datetime.now().strftime('%Y%m%d')
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            
            # 获取历史数据
            if period == "daily":
                df = ak.stock_zh_a_hist(symbol=symbol, period="daily", 
                                       start_date=start_date, end_date=end_date, adjust="qfq")
            else:
                df = ak.stock_zh_a_hist(symbol=symbol, period=period,
                                       start_date=start_date, end_date=end_date)
            
            self._set_cache(cache_key, df)
            logger.info(f"[AKShare] 历史行情获取成功: {symbol}, {len(df)} 条记录")
            return df
            
        except Exception as e:
            logger.error(f"[AKShare] 历史行情获取失败: {symbol}, {e}")
            return pd.DataFrame()
    
    # ==================== 资金流接口 ====================
    
    def get_individual_fund_flow(self, symbol: str) -> pd.DataFrame:
        """个股资金流向"""
        cache_key = f"fund_flow_individual_{symbol}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached
        
        logger.info(f"[AKShare] 获取个股资金流: {symbol}")
        
        try:
            df = ak.stock_individual_fund_flow(stock=symbol, market="sh" if symbol.endswith('SH') else "sz")
            
            self._set_cache(cache_key, df)
            logger.info(f"[AKShare] 个股资金流获取成功: {symbol}, {len(df)} 条记录")
            return df
            
        except Exception as e:
            logger.error(f"[AKShare] 个股资金流获取失败: {symbol}, {e}")
            return pd.DataFrame()
    
    def get_market_fund_flow(self, date: str = None) -> pd.DataFrame:
        """大盘资金流向"""
        cache_key = f"fund_flow_market_{date}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached
        
        logger.info(f"[AKShare] 获取大盘资金流")
        
        try:
            df = ak.stock_fund_flow_individual(stock="sh000001", market="sh")
            
            if date:
                df = df[df['date'] == date]
            
            self._set_cache(cache_key, df)
            logger.info(f"[AKShare] 大盘资金流获取成功: {len(df)} 条记录")
            return df
            
        except Exception as e:
            logger.error(f"[AKShare] 大盘资金流获取失败: {e}")
            return pd.DataFrame()
    
    # ==================== 龙虎榜接口 ====================
    
    def get_longhub_top_list(self, date: str = None) -> pd.DataFrame:
        """龙虎榜每日列表"""
        cache_key = f"longhub_top_{date}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached
        
        logger.info(f"[AKShare] 获取龙虎榜列表")
        
        try:
            df = ak.stock_lhb_detail_em(date=date)
            
            self._set_cache(cache_key, df)
            logger.info(f"[AKShare] 龙虎榜获取成功: {len(df)} 条记录")
            return df
            
        except Exception as e:
            logger.error(f"[AKShare] 龙虎榜获取失败: {e}")
            return pd.DataFrame()
    
    def get_longhub_detail(self, symbol: str) -> pd.DataFrame:
        """个股龙虎榜详情"""
        cache_key = f"longhub_detail_{symbol}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached
        
        logger.info(f"[AKShare] 获取个股龙虎榜: {symbol}")
        
        try:
            df = ak.stock_lhb_detail_daily_em(symbol=symbol)
            
            self._set_cache(cache_key, df)
            logger.info(f"[AKShare] 个股龙虎榜获取成功: {symbol}, {len(df)} 条记录")
            return df
            
        except Exception as e:
            logger.error(f"[AKShare] 个股龙虎榜获取失败: {symbol}, {e}")
            return pd.DataFrame()
    
    # ==================== 概念板块接口 ====================
    
    def get_concept_stocks(self, concept_name: str = None) -> pd.DataFrame:
        """概念板块成分股"""
        cache_key = f"concept_stocks_{concept_name}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached
        
        logger.info(f"[AKShare] 获取概念板块: {concept_name}")
        
        try:
            # 获取概念板块
            if concept_name:
                df = ak.stock_board_concept_name_em(em=concept_name)
            else:
                df = ak.stock_board_concept_name_em()
            
            self._set_cache(cache_key, df)
            logger.info(f"[AKShare] 概念板块获取成功: {len(df)} 个板块")
            return df
            
        except Exception as e:
            logger.error(f"[AKShare] 概念板块获取失败: {e}")
            return pd.DataFrame()
    
    def get_industry_stocks(self, industry_name: str = None) -> pd.DataFrame:
        """行业板块成分股"""
        cache_key = f"industry_stocks_{industry_name}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached
        
        logger.info(f"[AKShare] 获取行业板块: {industry_name}")
        
        try:
            if industry_name:
                df = ak.stock_board_industry_name_em(em=industry_name)
            else:
                df = ak.stock_board_industry_name_em()
            
            self._set_cache(cache_key, df)
            logger.info(f"[AKShare] 行业板块获取成功: {len(df)} 个板块")
            return df
            
        except Exception as e:
            logger.error(f"[AKShare] 行业板块获取失败: {e}")
            return pd.DataFrame()
    
    # ==================== 财务数据接口 ====================
    
    def get_financial_indicator(self, symbol: str) -> pd.DataFrame:
        """关键财务指标"""
        cache_key = f"financial_indicator_{symbol}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached
        
        logger.info(f"[AKShare] 获取财务指标: {symbol}")
        
        try:
            df = ak.stock_financial_analysis_indicator(symbol=symbol)
            
            self._set_cache(cache_key, df)
            logger.info(f"[AKShare] 财务指标获取成功: {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"[AKShare] 财务指标获取失败: {symbol}, {e}")
            return pd.DataFrame()
    
    def get_balance_sheet(self, symbol: str) -> pd.DataFrame:
        """资产负债表"""
        cache_key = f"balance_sheet_{symbol}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached
        
        logger.info(f"[AKShare] 获取资产负债表: {symbol}")
        
        try:
            df = ak.stock_balance_sheet_by_yearly_em(symbol=symbol)
            
            self._set_cache(cache_key, df)
            logger.info(f"[AKShare] 资产负债表获取成功: {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"[AKShare] 资产负债表获取失败: {symbol}, {e}")
            return pd.DataFrame()
    
    def get_profit_sheet(self, symbol: str) -> pd.DataFrame:
        """利润表"""
        cache_key = f"profit_sheet_{symbol}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached
        
        logger.info(f"[AKShare] 获取利润表: {symbol}")
        
        try:
            df = ak.stock_profit_sheet_by_yearly_em(symbol=symbol)
            
            self._set_cache(cache_key, df)
            logger.info(f"[AKShare] 利润表获取成功: {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"[AKShare] 利润表获取失败: {symbol}, {e}")
            return pd.DataFrame()
    
    # ==================== 综合查询 ====================
    
    def get_comprehensive_stock_data(self, symbol: str) -> Dict[str, Any]:
        """综合股票数据（行情+资金流+龙虎榜+财务）"""
        cache_key = f"comprehensive_{symbol}_{datetime.now().strftime('%Y%m%d')}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached
        
        logger.info(f"[AKShare] 获取综合数据: {symbol}")
        
        result = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'quote': None,
            'fund_flow': None,
            'longhub': None,
            'financial': None
        }
        
        # 1. 实时行情
        try:
            quote_df = self.get_realtime_quotes([symbol])
            if not quote_df.empty and len(quote_df) > 0:
                result['quote'] = quote_df.iloc[0].to_dict()
                logger.info(f"[AKShare] 实时行情: {result['quote']}")
        except:
            pass
        
        # 2. 资金流
        try:
            fund_df = self.get_individual_fund_flow(symbol)
            if not fund_df.empty:
                result['fund_flow'] = fund_df.to_dict('records')
                logger.info(f"[AKShare] 资金流: {len(result['fund_flow'])} 条记录")
        except:
            pass
        
        # 3. 龙虎榜
        try:
            longhub_df = self.get_longhub_detail(symbol)
            if not longhub_df.empty:
                result['longhub'] = longhub_df.to_dict('records')
                logger.info(f"[AKShare] 龙虎榜: {len(result['longhub'])} 条记录")
        except:
            pass
        
        # 4. 财务数据
        try:
            financial_df = self.get_financial_indicator(symbol)
            if not financial_df.empty and len(financial_df) > 0:
                result['financial'] = financial_df.iloc[0].to_dict()
                logger.info(f"[AKShare] 财务指标: {result['financial']}")
        except:
            pass
        
        self._set_cache(cache_key, result)
        logger.info(f"[AKShare] 综合数据获取完成: {symbol}")
        
        return result


# 测试
if __name__ == '__main__':
    print("="*80)
    print("🔧 AKShare全接口整合器")
    print("="*80)
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 初始化
    integrator = AKShareFullIntegrator(cache_ttl=600)  # 10分钟缓存
    
    # 测试1：实时行情
    print("\n测试1: 实时行情")
    print("-"*60)
    quotes = integrator.get_realtime_quotes(['300750', '600519'])
    print(f"获取到 {len(quotes)} 只股票实时行情")
    if not quotes.empty:
        print(quotes.head())
    
    # 测试2：个股资金流
    print("\n测试2: 个股资金流")
    print("-"*60)
    fund_flow = integrator.get_individual_fund_flow('300750')
    print(f"宁德时代资金流: {len(fund_flow)} 条记录")
    if not fund_flow.empty:
        print(fund_flow.head())
    
    # 测试3：龙虎榜
    print("\n测试3: 龙虎榜")
    print("-"*60)
    longhub = integrator.get_longhub_top_list()
    print(f"龙虎榜: {len(longhub)} 条记录")
    if not longhub.empty:
        print(longhub.head())
    
    # 测试4：概念板块
    print("\n测试4: 概念板块")
    print("-"*60)
    concepts = integrator.get_concept_stocks('人工智能')
    print(f"人工智能概念: {len(concepts)} 个板块")
    if not concepts.empty:
        print(concepts.head())
    
    # 测试5：财务数据
    print("\n测试5: 财务数据")
    print("-"*60)
    financial = integrator.get_financial_indicator('300750')
    print(f"宁德时代财务指标:")
    if not financial.empty and len(financial) > 0:
        print(financial.iloc[0])
    
    # 测试6：综合数据
    print("\n测试6: 综合数据")
    print("-"*60)
    comprehensive = integrator.get_comprehensive_stock_data('300750')
    print(f"宁德时代综合数据:")
    print(f"  实时行情: {comprehensive.get('quote')}")
    print(f"  资金流: {len(comprehensive.get('fund_flow', []))} 条记录")
    print(f"  龙虎榜: {len(comprehensive.get('longhub', []))} 条记录")
    print(f"  财务指标: {comprehensive.get('financial')}")
    
    print("\n" + "="*80)
    print("✅ 测试完成")
    print("="*80)
