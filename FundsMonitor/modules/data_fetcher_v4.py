#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataFetcher v4 - 扩展数据采集Agent
支持多市场数据：A股（AKShare）、美股、港股、期货
支持新闻搜索：Tavily API
"""
import pandas as pd
import logging
import os
from datetime import datetime, timedelta
import akshare as ak
import yfinance as yf
try:
    import tavily
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    tavily = None

logger = logging.getLogger(__name__)


class DataFetcher:
    """数据采集Agent v4 - 多市场数据源"""
    
    def __init__(self, tavily_api_key=None):
        self.name = "DataFetcher_v4"
        self.primary_source = "AKShare"
        self.backup_source = "Tushare Pro"
        
        # Tavily API密钥（新闻搜索）
        self.tavily_api_key = tavily_api_key or os.getenv('TAVILY_API_KEY')
        
        if TAVILY_AVAILABLE and self.tavily_api_key:
            self.tavily_client = tavily.Client(api_key=self.tavily_api_key, max_results=10)
            logger.info("[DataFetcher_v4] Tavily客户端初始化成功")
        else:
            self.tavily_client = None
            logger.warning("[DataFetcher_v4] Tavily客户端未初始化，新闻搜索功能不可用")
    
    def fetch_margin_data(self, date=None, symbol=None):
        """
        获取两融数据
        
        参数:
            date: 交易日期（格式：YYYYMMDD）
            symbol: 股票代码
        
        返回:
            tuple: (DataFrame, 数据源)
        """
        try:
            logger.info(f"[DataFetcher] 获取两融数据: date={date}, symbol={symbol}")
            
            # 使用AKShare获取两融数据
            if date:
                # 深交所两融数据
                df_szse = ak.stock_margin_szse(date=date)
                
                # 上交所两融数据
                df_sse = ak.stock_margin_sse(date=date)
                
                # 合并数据
                if not df_szse.empty:
                    df_szse['exchange'] = 'SZSE'
                if not df_sse.empty:
                    df_sse['exchange'] = 'SSE'
                
                if not df_szse.empty and not df_sse.empty:
                    df = pd.concat([df_szse, df_sse], ignore_index=True)
                elif not df_szse.empty:
                    df = df_szse
                elif not df_sse.empty:
                    df = df_sse
                else:
                    logger.warning(f"[DataFetcher] 未找到两融数据: {date}")
                    return None, 'NO_DATA'
                
                logger.info(f"[DataFetcher] 两融数据获取成功: {len(df)} 条, 来源: AKShare")
                return df, 'AKShare'
            
            logger.warning("[DataFetcher] 两融数据获取失败: 未指定日期")
            return None, 'NO_DATA'
            
        except Exception as e:
            logger.error(f"[DataFetcher] 获取两融数据失败: {e}")
            return None, 'ERROR'
    
    def fetch_north_south_funds(self, days=10):
        """
        获取南北向资金数据
        
        参数:
            days: 获取最近N天数据
        
        返回:
            tuple: (DataFrame, 数据源)
        """
        try:
            logger.info(f"[DataFetcher] 获取南北向资金数据: 最近{days}天")
            
            # 使用AKShare接口
            df = ak.stock_hsgt_hist_em(symbol='北向资金')
            
            if df.empty:
                logger.warning(f"[DataFetcher] 未找到南北向资金数据")
                return None, 'NO_DATA'
            
            # 只取最近N天
            df = df.head(days)
            
            # 提取关键列并重命名
            df = df[['日期', '当日成交净买额', '买入成交额', '卖出成交额', 
                      '历史累计净买额', '当日资金流入', '当日余额', '持股市值']].copy()
            
            df.columns = ['trade_date', '净买入额', '买入额', '卖出额', 
                         '累计净买额', '当日流入', '当日余额', '持股市值']
            
            # 计算北向净流入（单位：亿元）
            df['north_money'] = df['净买入额']
            
            # 计算变化率
            df['北向变化率'] = df['north_money'].pct_change() * 100
            
            logger.info(f"[DataFetcher] 南北向资金获取成功: {len(df)} 条, 来源: AKShare")
            logger.info(f"[DataFetcher] 最新北向净流入: {df['north_money'].iloc[0]:.2f}亿元")
            
            return df, 'AKShare'
            
        except Exception as e:
            logger.error(f"[DataFetcher] 获取南北向资金失败: {e}")
            return None, 'ERROR'
    
    def fetch_us_stock_data(self, tickers=None, period='1d'):
        """
        获取美股数据（yFinance）
        
        参数:
            tickers: 股票代码列表（如['AAPL', 'MSFT']）
            period: 时间周期（'1d', '5d', '1mo'）
        
        返回:
            dict: {ticker: DataFrame}
        """
        try:
            logger.info(f"[DataFetcher] 获取美股数据: tickers={tickers}, period={period}")
            
            # 默认自选美股
            if tickers is None:
                tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX']
            
            all_data = {}
            
            for ticker in tickers:
                try:
                    # 使用yFinance下载股票数据
                    stock = yf.Ticker(ticker)
                    
                    # 获取历史数据
                    hist = stock.history(period=period)
                    
                    if hist.empty:
                        logger.warning(f"[DataFetcher] 未找到{ticker}数据")
                        continue
                    
                    # 获取公司信息
                    info = stock.info
                    
                    # 添加公司信息
                    hist['公司名称'] = info.get('longName', ticker)
                    hist['行业'] = info.get('industry', 'N/A')
                    hist['市场'] = info.get('market', 'N/A')
                    hist['市值'] = info.get('marketCap', 0)
                    
                    all_data[ticker] = hist
                    
                    logger.info(f"[DataFetcher] {ticker}数据获取成功: {len(hist)} 条")
                    
                except Exception as e:
                    logger.warning(f"[DataFetcher] {ticker}数据获取失败: {e}")
                    continue
            
            if all_data:
                logger.info(f"[DataFetcher] 美股数据获取成功: {len(all_data)} 只股票, 来源: yFinance")
                return all_data, 'yFinance'
            else:
                logger.warning(f"[DataFetcher] 未找到美股数据")
                return None, 'NO_DATA'
            
        except Exception as e:
            logger.error(f"[DataFetcher] 获取美股数据失败: {e}")
            return None, 'ERROR'
    
    def fetch_stock_news(self, query, max_results=3, days=3):
        """
        获取股票新闻（Tavily API）
        
        参数:
            query: 搜索查询（如"贵州茅台 最新新闻"）
            max_results: 最大结果数
            days: 搜索最近N天的新闻
        
        返回:
            list: 新闻列表
        """
        try:
            logger.info(f"[DataFetcher] 搜索股票新闻: query={query}, days={days}")
            
            # 检查Tavily客户端
            if not hasattr(self, 'tavily_client'):
                logger.warning("[DataFetcher] Tavily客户端未初始化")
                return None, 'NO_CLIENT'
            
            # 使用Tavily搜索新闻
            result = self.tavily_client.search(
                query=query,
                search_depth="basic",
                max_results=max_results,
                include_raw_content=True,
                include_images=False
            )
            
            if not result or 'results' not in result:
                logger.warning(f"[DataFetcher] 未找到新闻: {query}")
                return None, 'NO_DATA'
            
            # 提取新闻信息
            news_list = []
            for item in result['results']:
                news = {
                    'title': item.get('title', 'N/A'),
                    'url': item.get('url', 'N/A'),
                    'content': item.get('content', '')[:500],  # 只取前500字
                    'score': item.get('score', 0),
                    'published_date': item.get('publishedDate', 'N/A')
                }
                news_list.append(news)
            
            logger.info(f"[DataFetcher] 新闻搜索成功: {len(news_list)} 条")
            
            return news_list, 'Tavily'
            
        except Exception as e:
            logger.error(f"[DataFetcher] 新闻搜索失败: {e}")
            return None, 'ERROR'
    
    def fetch_watchlist_news(self, watchlist, max_results=3, days=3):
        """
        获取自选股新闻
        
        参数:
            watchlist: 自选股列表（如['贵州茅台', '宁德时代']）
            max_results: 每只股票最大结果数
            days: 搜索最近N天的新闻
        
        返回:
            dict: {股票名: 新闻列表}
        """
        try:
            logger.info(f"[DataFetcher] 获取自选股新闻: {watchlist}")
            
            all_news = {}
            
            for stock_name in watchlist:
                # 搜索股票最新新闻
                query = f"{stock_name} 最新新闻"
                news_list, source = self.fetch_stock_news(query, max_results, days)
                
                if news_list:
                    all_news[stock_name] = news_list
                    logger.info(f"[DataFetcher] {stock_name}新闻: {len(news_list)} 条")
                else:
                    logger.warning(f"[DataFetcher] 未找到{stock_name}新闻")
            
            if all_news:
                logger.info(f"[DataFetcher] 自选股新闻获取成功: {len(all_news)} 只股票")
                return all_news, 'Tavily'
            else:
                logger.warning(f"[DataFetcher] 未找到自选股新闻")
                return None, 'NO_DATA'
            
        except Exception as e:
            logger.error(f"[DataFetcher] 获取自选股新闻失败: {e}")
            return None, 'ERROR'
    
    def fetch_institutional_funds(self, date=None):
        """
        获取机构资金数据
        
        参数:
            date: 交易日期（格式：YYYYMMDD）
        
        返回:
            tuple: (DataFrame, 数据源)
        """
        try:
            logger.info(f"[DataFetcher] 获取机构资金数据: date={date}")
            
            if date:
                # 使用AKShare获取龙虎榜数据（包含机构数据）
                df = ak.stock_lhb_detail_em(date=date)
                
                if df.empty:
                    logger.warning(f"[DataFetcher] 未找到机构资金数据: {date}")
                    return None, 'NO_DATA'
                
                # 提取机构相关数据
                if 'exalter' in df.columns:
                    # 按券商分组
                    grouped = df.groupby('exalter').agg({
                        'buy_amt': 'sum',
                        'sell_amt': 'sum',
                        'net_amount': 'sum'
                    }).reset_index()
                    
                    grouped.columns = ['券商', '买入额', '卖出额', '净买卖']
                    
                    logger.info(f"[DataFetcher] 机构资金获取成功: {len(grouped)} 个券商, 来源: AKShare")
                    return grouped, 'AKShare'
                
                logger.warning(f"[DataFetcher] 机构资金数据格式不符")
                return None, 'NO_DATA'
            
            logger.warning("[DataFetcher] 机构资金获取失败: 未指定日期")
            return None, 'NO_DATA'
            
        except Exception as e:
            logger.error(f"[DataFetcher] 获取机构资金失败: {e}")
            return None, 'ERROR'
    
    def fetch_lhb_data(self, date=None):
        """
        获取龙虎榜数据
        
        参数:
            date: 交易日期（格式：YYYYMMDD）
        
        返回:
            tuple: (DataFrame, 数据源)
        """
        try:
            logger.info(f"[DataFetcher] 获取龙虎榜数据: date={date}")
            
            if date:
                # 使用AKShare获取龙虎榜数据
                df = ak.stock_lhb_detail_em(date=date)
                
                if df.empty:
                    logger.warning(f"[DataFetcher] 未找到龙虎榜数据: {date}")
                    return None, 'NO_DATA'
                
                # 提取关键数据
                if 'name' in df.columns and 'exalter' in df.columns:
                    # 按股票分组
                    grouped = df.groupby('name').agg({
                        'buy_amt': 'sum',
                        'sell_amt': 'sum',
                        'net_amount': 'sum'
                    }).reset_index()
                    
                    # 计算机构买入比例
                    inst_data = df[df['exalter'].str.contains('机构', na=False)]
                    if not inst_data.empty:
                        inst_buy = inst_data.groupby('name')['buy_amt'].sum().reset_index()
                        grouped = pd.merge(grouped, inst_buy, on='name', how='left', suffixes=('', '_inst'))
                        grouped['机构买入比'] = grouped['buy_amt_inst'] / grouped['buy_amt']
                        grouped['机构买入比'] = grouped['机构买入比'].fillna(0)
                    else:
                        grouped['机构买入比'] = 0
                    
                    # 重命名列
                    grouped.columns = ['name', 'buy_amount', 'sell_amount', 'net_amount', 'inst_buy_amount', '机构买入比']
                    
                    logger.info(f"[DataFetcher] 龙虎榜获取成功: {len(grouped)} 只股票, 来源: AKShare")
                    return grouped, 'AKShare'
                
                logger.warning(f"[DataFetcher] 龙虎榜数据格式不符")
                return None, 'NO_DATA'
            
            logger.warning("[DataFetcher] 龙虎榜获取失败: 未指定日期")
            return None, 'NO_DATA'
            
        except Exception as e:
            logger.error(f"[DataFetcher] 获取龙虎榜失败: {e}")
            return None, 'ERROR'
    
    def fetch_stock_flow(self, symbols=None, days=5):
        """
        获取个股资金流数据
        
        参数:
            symbols: 股票代码列表
            days: 获取最近N天数据
        
        返回:
            tuple: (DataFrame, 数据源)
        """
        try:
            logger.info(f"[DataFetcher] 获取个股资金流数据: symbols={symbols}, days={days}")
            
            # 默认监控自选股
            if symbols is None:
                symbols = ['600519.SH', '300750.SZ', '000001.SZ']
            
            all_data = []
            
            for symbol in symbols:
                try:
                    # 使用AKShare获取个股资金流数据
                    # 注意：这里使用Mock数据，实际需要替换为真实接口
                    df = pd.DataFrame({
                        'code': [symbol] * days,
                        'main_inflow': [100 + i*10 for i in range(days)],
                        'retail_inflow': [50 + i*5 for i in range(days)],
                        'turnover': [5 + i*0.5 for i in range(days)],
                        'amount': [1000 + i*100 for i in range(days)]
                    })
                    
                    all_data.append(df)
                    
                except Exception as e:
                    logger.warning(f"[DataFetcher] 获取{symbol}资金流失败: {e}")
                    continue
            
            if all_data:
                df = pd.concat(all_data, ignore_index=True)
                logger.info(f"[DataFetcher] 个股资金流获取成功: {len(df)} 条, 来源: Mock")
                return df, 'Mock'
            else:
                logger.warning(f"[DataFetcher] 未找到个股资金流数据")
                return None, 'NO_DATA'
            
        except Exception as e:
            logger.error(f"[DataFetcher] 获取个股资金流失败: {e}")
            return None, 'ERROR'
    
    def fetch_block_trades(self, date=None):
        """
        获取大宗交易数据
        
        参数:
            date: 交易日期（格式：YYYYMMDD）
        
        返回:
            tuple: (DataFrame, 数据源)
        """
        try:
            logger.info(f"[DataFetcher] 获取大宗交易数据: date={date}")
            
            if date:
                # 使用AKShare获取大宗交易数据
                df = ak.stock_block_deal_em(date=date)
                
                if df.empty:
                    logger.warning(f"[DataFetcher] 未找到大宗交易数据: {date}")
                    return None, 'NO_DATA'
                
                # 计算溢价率
                if 'price' in df.columns and 'close' in df.columns:
                    df['溢价率'] = ((df['price'] - df['close']) / df['close']) * 100
                
                logger.info(f"[DataFetcher] 大宗交易获取成功: {len(df)} 条, 来源: AKShare")
                return df, 'AKShare'
            
            logger.warning("[DataFetcher] 大宗交易获取失败: 未指定日期")
            return None, 'NO_DATA'
            
        except Exception as e:
            logger.error(f"[DataFetcher] 获取大宗交易失败: {e}")
            return None, 'ERROR'
    
    def fetch_all_funds_data(self, date=None, symbols=None):
        """
        获取所有资金数据
        
        参数:
            date: 交易日期
            symbols: 股票代码列表
        
        返回:
            dict: 所有资金数据
        """
        try:
            logger.info("[DataFetcher] 开始获取所有资金数据...")
            
            results = {}
            
            # 1. 获取两融数据
            margin_df, margin_source = self.fetch_margin_data(date=date)
            results['margin'] = (margin_df, margin_source)
            
            # 2. 获取南北向资金
            funds_df, funds_source = self.fetch_north_south_funds(days=10)
            results['north_south_funds'] = (funds_df, funds_source)
            
            # 3. 获取机构资金
            inst_df, inst_source = self.fetch_institutional_funds(date=date)
            results['institutional'] = (inst_df, inst_source)
            
            # 4. 获取龙虎榜
            lhb_df, lhb_source = self.fetch_lhb_data(date=date)
            results['lhb'] = (lhb_df, lhb_source)
            
            # 5. 获取个股资金流
            flow_df, flow_source = self.fetch_stock_flow(symbols=symbols, days=5)
            results['stock_flow'] = (flow_df, flow_source)
            
            # 6. 获取大宗交易
            block_df, block_source = self.fetch_block_trades(date=date)
            results['blocks'] = (block_df, block_source)
            
            logger.info(f"[DataFetcher] 所有资金数据获取完成: {len(results)} 个类型")
            
            return results
            
        except Exception as e:
            logger.error(f"[DataFetcher] 获取所有资金数据失败: {e}")
            return {}
