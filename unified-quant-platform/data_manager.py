
# 数据管理器实现
import requests
import pandas as pd
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class TushareDataManager:
    """Tushare数据管理器"""
    
    def __init__(self, token: str):
        self.token = token
        self.api_url = "https://api.tushare.pro"
        self.cache_file = "tushare_cache.json"
        self.cache = {}
        
    def _api_call(self, api_name: str, params: dict = None, fields: str = None):
        """调用Tushare API"""
        if params is None:
            params = {}
        
        data = {
            'api_name': api_name,
            'token': self.token,
            'params': params,
            'fields': fields
        }
        
        for attempt in range(3):
            try:
                r = requests.post(
                    self.api_url,
                    json=data,
                    timeout=30
                )
                r.raise_for_status()
                result = r.json()
                
                if result['code'] != 0:
                    print(f"API Error: {result['msg']}")
                    return None
                
                return result['data']
            except Exception as e:
                print(f"API Error (attempt {attempt+1}): {e}")
                time.sleep(2)
        
        return None
    
    def get_realtime_quotes(self, ts_codes: List[str]) -> Dict:
        """获取实时行情"""
        # 使用新浪财经API获取实时数据
        sina_url = "http://hq.sinajs.cn/list="
        quotes = {}
        
        for code in ts_codes:
            try:
                # 格式化代码
                if code.endswith('.SH'):
                    symbol = f"sh{code[:6]}"
                elif code.endswith('.SZ'):
                    symbol = f"sz{code[:6]}"
                else:
                    symbol = code
                
                r = requests.get(f"{sina_url}{symbol}", timeout=10)
                r.encoding = 'gbk'
                content = r.text
                
                if content and "=" in content:
                    data_str = content.split("=")[1].strip('";')
                    if data_str:
                        values = data_str.split(",")
                        if len(values) >= 32:
                            quotes[code] = {
                                'name': values[0],
                                'open': float(values[1]),
                                'pre_close': float(values[2]),
                                'price': float(values[3]),
                                'high': float(values[4]),
                                'low': float(values[5]),
                                'bid': float(values[6]),
                                'ask': float(values[7]),
                                'volume': int(values[8]),
                                'amount': float(values[9]),
                                'date': values[30],
                                'time': values[31],
                                'pct_chg': round((float(values[3]) - float(values[2])) / float(values[2]) * 100, 2)
                            }
            except Exception as e:
                print(f"获取{code}行情失败: {e}")
                continue
        
        return quotes
    
    def get_stock_basic(self, ts_code: str = None, list_status: str = 'L'):
        """获取股票基本信息"""
        params = {'list_status': list_status}
        if ts_code:
            params['ts_code'] = ts_code
        
        return self._api_call('stock_basic', params)
    
    def get_daily(self, ts_code: str, start_date: str = None, end_date: str = None):
        """获取日线数据"""
        params = {
            'ts_code': ts_code,
            'adj': 'qfq'  # 前复权
        }
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        
        return self._api_call('daily', params)
    
    def get_daily_basic(self, ts_code: str = None, trade_date: str = None):
        """获取每日指标"""
        params = {}
        if ts_code:
            params['ts_code'] = ts_code
        if trade_date:
            params['trade_date'] = trade_date
        
        return self._api_call('daily_basic', params)
