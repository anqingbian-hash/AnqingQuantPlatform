#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多数据源股票查询 - 新浪、腾讯、AKShare多数据源
快速、稳定、多样化
"""
import requests
import json
import logging
from typing import Dict, Optional, List
from datetime import datetime
import time
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataSourceSina:
    """新浪财经数据源"""

    def __init__(self):
        self.name = "新浪财经"
        self.base_url = "http://hq.sinajs.cn/list="

    def query_stock(self, code: str) -> Optional[Dict]:
        """查询单个股票"""
        try:
            # 转换代码格式
            sina_code = self._convert_code(code)
            url = self.base_url + sina_code

            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                # 解析返回数据
                data_str = response.text
                if '="' in data_str:
                    data = data_str.split('="')[1].split('"')[0].split(',')

                    if len(data) > 3:
                        name = data[0]
                        price = float(data[3]) if data[3] else 0
                        change_pct = ((float(data[3]) - float(data[2])) / float(data[2]) * 100) if data[2] and data[3] else 0

                        return {
                            'code': code,
                            'name': name,
                            'sector': '未知',  # 新浪不提供行业
                            'price': price,
                            'change_pct': change_pct,
                            'data_source': 'sina',
                            'source': '新浪财经API',
                            'query_time': datetime.now().isoformat()
                        }

        except Exception as e:
            logger.debug(f"[新浪财经] 查询失败 {code}: {e}")

        return None

    def _convert_code(self, code: str) -> str:
        """转换代码格式为新浪格式"""
        if code.startswith('6'):
            return f'sh{code}'
        else:
            return f'sz{code}'


class DataSourceTencent:
    """腾讯财经数据源"""

    def __init__(self):
        self.name = "腾讯财经"
        self.base_url = "http://qt.gtimg.cn/q="

    def query_stock(self, code: str) -> Optional[Dict]:
        """查询单个股票"""
        try:
            # 转换代码格式
            tencent_code = self._convert_code(code)
            url = self.base_url + tencent_code

            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                # 解析返回数据
                data_str = response.text
                if '~' in data_str:
                    data = data_str.split('~')

                    if len(data) > 3:
                        name = data[1]
                        price = float(data[3]) if data[3] else 0
                        close_prev = float(data[4]) if data[4] else 0
                        change_pct = ((price - close_prev) / close_prev * 100) if close_prev > 0 else 0

                        return {
                            'code': code,
                            'name': name,
                            'sector': '未知',  # 腾讯不提供行业
                            'price': price,
                            'change_pct': change_pct,
                            'data_source': 'tencent',
                            'source': '腾讯财经API',
                            'query_time': datetime.now().isoformat()
                        }

        except Exception as e:
            logger.debug(f"[腾讯财经] 查询失败 {code}: {e}")

        return None

    def _convert_code(self, code: str) -> str:
        """转换代码格式为腾讯格式"""
        if code.startswith('6'):
            return f'sh{code}'
        else:
            return f'sz{code}'


class DataSourceAKShare:
    """AKShare数据源"""

    def __init__(self):
        self.name = "AKShare"
        try:
            import akshare as ak
            self.ak = ak
            self.available = True
        except ImportError:
            self.available = False
            logger.warning("[AKShare] 未安装，跳过")

    def query_stock(self, code: str) -> Optional[Dict]:
        """查询单个股票"""
        if not self.available:
            return None

        try:
            stock_info = self.ak.stock_individual_info_em(symbol=code)
            name = stock_info[stock_info['item'] == '股票简称']['value'].values[0]
            industry = stock_info[stock_info['item'] == '行业']['value'].values[0] if '行业' in stock_info['item'].values else '未知'
            price = stock_info[stock_info['item'] == '最新']['value'].values[0] if '最新' in stock_info['item'].values else None

            if price:
                try:
                    price = float(price)
                except:
                    price = 0

            return {
                'code': code,
                'name': name,
                'sector': industry,
                'price': price,
                'change_pct': None,  # AKShare个股信息不提供涨跌
                'data_source': 'akshare',
                'source': 'AKShare API',
                'query_time': datetime.now().isoformat()
            }

        except Exception as e:
            logger.debug(f"[AKShare] 查询失败 {code}: {e}")

        return None


class DataSourceTusharePro:
    """Tushare Pro数据源"""

    def __init__(self):
        self.name = "Tushare Pro"
        self.pro = None
        self.available = False

        try:
            import tushare as ts
            # 尝试从环境变量获取token
            token = os.getenv('TUSHARE_TOKEN')
            if token:
                self.pro = ts.pro_api(token)
                self.available = True
                logger.info(f"[Tushare Pro] 已初始化，积分可用")
            else:
                logger.warning("[Tushare Pro] 未设置TUSHARE_TOKEN环境变量")
        except ImportError:
            logger.warning("[Tushare Pro] 未安装，跳过")

    def query_stock(self, code: str) -> Optional[Dict]:
        """查询单个股票"""
        if not self.available or not self.pro:
            return None

        try:
            # 转换TS代码格式
            ts_code = self._convert_code(code)

            # 获取日线行情（最新一条）
            df = self.pro.daily(ts_code=ts_code)
            if df.empty:
                return None

            # 获取最新数据
            latest = df.iloc[0]

            # 获取基本信息
            df_basic = self.pro.stock_basic(ts_code=ts_code)
            if df_basic.empty:
                name = '未知'
                industry = '未知'
            else:
                basic = df_basic.iloc[0]
                name = basic.get('name', '未知')
                industry = basic.get('industry', '未知')

            price = float(latest['close'])
            change_pct = float(latest['pct_chg'])

            return {
                'code': code,
                'name': name,
                'sector': industry,
                'price': price,
                'change_pct': change_pct,
                'data_source': 'tushare_pro',
                'source': 'Tushare Pro API',
                'query_time': datetime.now().isoformat()
            }

        except Exception as e:
            logger.debug(f"[Tushare Pro] 查询失败 {code}: {e}")

        return None

    def _convert_code(self, code: str) -> str:
        """转换代码格式为Tushare格式"""
        if code.startswith('6'):
            return f"{code}.SH"
        else:
            return f"{code}.SZ"


class MultiDataSource:
    """多数据源查询 - 智能切换"""

    CACHE_DIR = '/root/.openclaw/workspace/unified-quot-platform/data'
    CACHE_FILE = os.path.join(CACHE_DIR, 'stocks_multi_source.json')

    def __init__(self, cache_enabled: bool = True, cache_expiry: int = 300):
        """
        初始化

        参数:
            cache_enabled: 是否启用缓存
            cache_expiry: 缓存过期时间（秒）
        """
        self.cache_enabled = cache_enabled
        self.cache_expiry = cache_expiry
        self.query_cache = {}
        self.all_stocks = {}

        # 初始化数据源（按优先级排序）
        self.sources = [
            DataSourceTusharePro(),  # 优先使用Tushare Pro（积分5000+）
            DataSourceTencent(),     # 腾讯财经（快速稳定）
            DataSourceSina(),        # 新浪财经（快速稳定）
            DataSourceAKShare(),     # AKShare（备用）
        ]

        # 创建缓存目录
        os.makedirs(self.CACHE_DIR, exist_ok=True)

        # 加载缓存
        self._load_cache()

    def _load_cache(self):
        """加载缓存"""
        try:
            if os.path.exists(self.CACHE_FILE):
                with open(self.CACHE_FILE, 'r', encoding='utf-8') as f:
                    self.all_stocks = json.load(f)
                logger.info(f"[MultiDataSource] 缓存加载成功: {len(self.all_stocks)} 只股票")
        except Exception as e:
            logger.error(f"[MultiDataSource] 缓存加载失败: {e}")

    def _save_cache(self):
        """保存缓存"""
        try:
            with open(self.CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.all_stocks, f, ensure_ascii=False, indent=2)
            logger.debug(f"[MultiDataSource] 缓存已保存: {len(self.all_stocks)} 只股票")
        except Exception as e:
            logger.error(f"[MultiDataSource] 缓存保存失败: {e}")

    def query_stock(self, code: str, force_refresh: bool = False) -> Dict:
        """
        查询股票信息

        参数:
            code: 股票代码
            force_refresh: 是否强制刷新

        返回:
            dict: 股票信息
        """
        # 检查缓存
        if not force_refresh:
            cached = self._get_query_cache(code)
            if cached:
                return cached

        # 检查本地缓存
        if code in self.all_stocks:
            cached = self.all_stocks[code]
            cache_time = datetime.fromisoformat(cached.get('cache_time', ''))
            age = (datetime.now() - cache_time).total_seconds()

            if age < self.cache_expiry:
                logger.info(f"[MultiDataSource] 使用本地缓存: {code}")
                self._set_query_cache(code, cached)
                return cached

        # 尝试各个数据源
        for source in self.sources:
            try:
                stock_info = source.query_stock(code)
                if stock_info and stock_info['name'] != '未知':
                    stock_info['cache_time'] = datetime.now().isoformat()

                    # 更新缓存
                    self.all_stocks[code] = stock_info
                    self._save_cache()

                    self._set_query_cache(code, stock_info)
                    logger.info(f"[MultiDataSource] 查询成功: {code} = {stock_info['name']} ({source.name})")
                    return stock_info

            except Exception as e:
                logger.debug(f"[MultiDataSource] {source.name} 查询失败: {e}")

        # 所有数据源都失败
        if code in self.all_stocks:
            # 使用过期的本地缓存
            cached = self.all_stocks[code]
            logger.warning(f"[MultiDataSource] 使用过期缓存: {code}")
            self._set_query_cache(code, cached)
            return cached

        # 完全没有数据
        logger.error(f"[MultiDataSource] 所有数据源查询失败: {code}")
        return {
            'code': code,
            'name': '未知',
            'sector': '未知',
            'price': 0,
            'change_pct': 0,
            'data_source': 'none',
            'query_time': datetime.now().isoformat()
        }

    def _get_query_cache(self, code: str) -> Optional[Dict]:
        """获取查询缓存"""
        if not self.cache_enabled:
            return None

        cached = self.query_cache.get(code)
        if cached:
            if time.time() - cached['time'] < self.cache_expiry:
                return cached['data']
            else:
                del self.query_cache[code]

        return None

    def _set_query_cache(self, code: str, data: Dict):
        """设置查询缓存"""
        if self.cache_enabled:
            self.query_cache[code] = {'data': data, 'time': time.time()}

    def batch_query(self, codes: List[str]) -> Dict[str, Dict]:
        """批量查询"""
        results = {}
        logger.info(f"[MultiDataSource] 批量查询 {len(codes)} 个股票")

        for code in codes:
            results[code] = self.query_stock(code)
            time.sleep(0.1)  # 避免请求过快

        return results

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return {
            'total_cached': len(self.all_stocks),
            'total_sources': len(self.sources),
            'sources': [s.name for s in self.sources],
            'cache_enabled': self.cache_enabled
        }


def test_multi_data_source():
    """测试多数据源查询"""
    print("=" * 70)
    print("多数据源股票查询测试")
    print("=" * 70)

    # 初始化
    query = MultiDataSource(cache_enabled=True, cache_expiry=300)

    # 获取统计信息
    print("\n=== 统计信息 ===")
    stats = query.get_statistics()
    print(f"缓存股票数: {stats['total_cached']}")
    print(f"数据源数: {stats['total_sources']}")
    print(f"数据源: {', '.join(stats['sources'])}")

    # 测试1: 查询特定股票
    print("\n=== 测试1: 查询特定股票 ===")
    test_codes = ['000001', '600519', '002496', '603019']
    results = query.batch_query(test_codes)

    for code, info in results.items():
        if info['name'] != '未知':
            print(f"✓ {code}: {info['name']} ({info['sector']}) [{info['data_source']}]")
            print(f"    价格: {info['price']:.2f}, 涨跌: {info.get('change_pct', 0):.2f}%")
            print(f"    来源: {info['source']}")
        else:
            print(f"✗ {code}: 查询失败")

    # 测试2: 验证关键股票
    print("\n=== 测试2: 验证关键股票 ===")
    test_cases = [
        ('002496', '*ST辉丰'),
        ('000001', '平安银行'),
        ('600519', '贵州茅台'),
        ('603019', '中科曙光'),
    ]

    all_passed = True
    for code, expected_name in test_cases:
        stock_info = query.query_stock(code)
        if stock_info['name'] == expected_name:
            print(f"✓ {code}: {stock_info['name']} ({stock_info['data_source']})")
        else:
            print(f"✗ {code}: 期望 {expected_name}, 实际 {stock_info['name']}")
            all_passed = False

    if all_passed:
        print("\n✅ 所有验证通过！")
    else:
        print("\n❌ 部分验证失败")

    print("\n" + "=" * 70)


if __name__ == '__main__':
    test_multi_data_source()
