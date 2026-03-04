#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全A股查询模块 - JSON缓存格式，支持自动更新
优先使用缓存，定期尝试更新实时数据
"""
import akshare as ak
import pandas as pd
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import time
import json
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AllAStockQueryJSON:
    """全A股查询 - JSON缓存格式"""

    CACHE_DIR = '/root/.openclaw/workspace/unified-quot-platform/data'
    CACHE_FILE = os.path.join(CACHE_DIR, 'all_a_stocks.json')
    METADATA_FILE = os.path.join(CACHE_DIR, 'all_a_stocks_metadata.json')

    def __init__(self, cache_enabled: bool = True, cache_expiry: int = 3600):
        """
        初始化

        参数:
            cache_enabled: 是否启用缓存
            cache_expiry: 缓存过期时间（秒），默认1小时
        """
        self.cache_enabled = cache_enabled
        self.cache_expiry = cache_expiry
        self.query_cache = {}
        self.all_stocks = []  # 股票列表
        self.cache_metadata = None

        # 创建缓存目录
        os.makedirs(self.CACHE_DIR, exist_ok=True)

        # 加载缓存数据
        self._load_cache()

    def _load_cache(self):
        """加载缓存数据"""
        try:
            # 加载元数据
            if os.path.exists(self.METADATA_FILE):
                with open(self.METADATA_FILE, 'r', encoding='utf-8') as f:
                    self.cache_metadata = json.load(f)
                logger.info("[AllAStockQuery] 缓存元数据加载成功")

            # 检查缓存是否过期
            if self._is_cache_valid():
                # 加载股票数据
                if os.path.exists(self.CACHE_FILE):
                    with open(self.CACHE_FILE, 'r', encoding='utf-8') as f:
                        self.all_stocks = json.load(f)
                    logger.info(f"[AllAStockQuery] 缓存数据加载成功: {len(self.all_stocks)} 只股票")
                    return
                else:
                    logger.warning("[AllAStockQuery] 缓存文件不存在")
            else:
                logger.info("[AllAStockQuery] 缓存已过期，将尝试更新")

        except Exception as e:
            logger.error(f"[AllAStockQuery] 加载缓存失败: {e}")

        # 缓存无效，尝试更新
        self._try_update_cache()

    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        if not self.cache_metadata:
            return False

        cache_time = datetime.fromisoformat(self.cache_metadata.get('last_update', ''))
        age = (datetime.now() - cache_time).total_seconds()

        return age < self.cache_expiry

    def _try_update_cache(self, retry: int = 2):
        """尝试更新缓存"""
        for attempt in range(retry):
            try:
                logger.info(f"[AllAStockQuery] 尝试更新缓存 (第{attempt+1}次)...")
                df = ak.stock_zh_a_spot_em()

                # 转换为JSON格式
                stocks_list = []
                for _, row in df.iterrows():
                    stocks_list.append({
                        'code': str(row['代码']),
                        'name': str(row['名称']),
                        'sector': str(row.get('行业', '未知')) if '行业' in row.index else '未知',
                        'price': float(row.get('最新价', 0)) if '最新价' in row.index else None,
                        'change_pct': float(row.get('涨跌幅', 0)) if '涨跌幅' in row.index else None
                    })

                # 保存到缓存
                with open(self.CACHE_FILE, 'w', encoding='utf-8') as f:
                    json.dump(stocks_list, f, ensure_ascii=False, indent=2)

                # 更新元数据
                self.cache_metadata = {
                    'last_update': datetime.now().isoformat(),
                    'total_stocks': len(stocks_list),
                    'data_source': 'akshare.stock_zh_a_spot_em',
                    'cache_format': 'json'
                }

                with open(self.METADATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(self.cache_metadata, f, ensure_ascii=False, indent=2)

                self.all_stocks = stocks_list
                logger.info(f"[AllAStockQuery] 缓存更新成功: {len(stocks_list)} 只股票")
                return True

            except Exception as e:
                logger.warning(f"[AllAStockQuery] 更新失败: {e}")
                if attempt < retry - 1:
                    time.sleep(2)

        logger.error("[AllAStockQuery] 更新失败，使用现有缓存")
        return False

    def query_stock(self, code: str, force_refresh: bool = False) -> Dict:
        """
        查询股票信息

        参数:
            code: 股票代码
            force_refresh: 是否强制刷新

        返回:
            dict: 股票信息
        """
        # 检查查询缓存
        if not force_refresh:
            cached = self._get_query_cache(code)
            if cached:
                return cached

        # 强制刷新或首次查询，尝试更新缓存
        if force_refresh or len(self.all_stocks) == 0:
            if self._try_update_cache():
                pass

        # 从数据中查询
        stock_info = self._query_from_data(code)
        if stock_info:
            self._set_query_cache(code, stock_info)
            return stock_info

        # 未找到
        logger.error(f"[AllAStockQuery] 未找到股票: {code}")
        return self._get_unknown_stock(code)

    def _query_from_data(self, code: str) -> Optional[Dict]:
        """从数据中查询"""
        for stock in self.all_stocks:
            if stock['code'] == code:
                result = {
                    'code': stock['code'],
                    'name': stock['name'],
                    'sector': stock.get('sector', '未知'),
                    'price': stock.get('price'),
                    'change_pct': stock.get('change_pct'),
                    'data_source': 'cache',
                    'cache_time': self.cache_metadata.get('last_update', '') if self.cache_metadata else None,
                    'query_time': datetime.now().isoformat()
                }
                return result

        return None

    def _get_unknown_stock(self, code: str) -> Dict:
        """返回未知股票信息"""
        return {
            'code': code,
            'name': '未知',
            'sector': '未知',
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

    def refresh_cache(self):
        """刷新缓存"""
        logger.info("[AllAStockQuery] 手动刷新缓存...")
        return self._try_update_cache(retry=3)

    def get_all_stocks(self) -> List[Dict]:
        """获取所有股票数据"""
        return self.all_stocks

    def get_stock_count(self) -> int:
        """获取股票数量"""
        return len(self.all_stocks)

    def search_stock(self, keyword: str) -> List[Dict]:
        """搜索股票"""
        results = []
        for stock in self.all_stocks:
            if keyword in stock['code'] or keyword in stock['name']:
                results.append({
                    'code': stock['code'],
                    'name': stock['name'],
                    'sector': stock.get('sector', '未知')
                })

            if len(results) >= 20:
                break

        return results

    def batch_query(self, codes: List[str]) -> Dict[str, Dict]:
        """批量查询"""
        results = {}
        for code in codes:
            results[code] = self.query_stock(code)
        return results

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        cache_age = None
        if self.cache_metadata and self.cache_metadata.get('last_update'):
            cache_time = datetime.fromisoformat(self.cache_metadata['last_update'])
            cache_age = (datetime.now() - cache_time).total_seconds()

        return {
            'total': self.get_stock_count(),
            'cache_enabled': self.cache_enabled,
            'cache_age': cache_age,
            'cache_time': self.cache_metadata.get('last_update') if self.cache_metadata else None,
            'status': 'loaded' if len(self.all_stocks) > 0 else 'not_loaded',
            'cache_format': 'json'
        }


def test_all_stock_json():
    """测试全A股查询（JSON格式）"""
    print("=" * 70)
    print("全A股查询测试（JSON缓存格式）")
    print("=" * 70)

    # 初始化
    query = AllAStockQueryJSON(cache_enabled=True, cache_expiry=3600)

    # 获取统计信息
    print("\n=== 统计信息 ===")
    stats = query.get_statistics()
    print(f"股票总数: {stats['total']}")
    print(f"缓存时间: {stats['cache_time']}")
    print(f"缓存年龄: {stats['cache_age']:.1f} 秒" if stats['cache_age'] else "缓存年龄: 未知")
    print(f"状态: {stats['status']}")
    print(f"缓存格式: {stats['cache_format']}")

    if stats['total'] == 0:
        print("\n❌ 没有可用的缓存数据，无法继续测试")
        return

    # 测试1: 查询特定股票
    print("\n=== 测试1: 查询特定股票 ===")
    test_codes = ['000001', '600519', '002496', '603019']
    results = query.batch_query(test_codes)

    for code, info in results.items():
        if info['name'] != '未知':
            print(f"✓ {code}: {info['name']} ({info['sector']})")
            if info.get('price'):
                print(f"    价格: {info['price']:.2f}, 涨跌: {info.get('change_pct', 0):.2f}%")
            print(f"    缓存时间: {info.get('cache_time', 'N/A')}")
        else:
            print(f"✗ {code}: 查询失败")

    # 测试2: 搜索股票
    print("\n=== 测试2: 搜索股票 ===")
    keyword = "银行"
    results = query.search_stock(keyword)
    print(f"搜索 '{keyword}' 找到 {len(results)} 只股票:")
    for i, stock in enumerate(results[:5], 1):
        print(f"  {i}. {stock['code']}: {stock['name']} ({stock['sector']})")

    # 测试3: 验证关键股票
    print("\n=== 测试3: 验证关键股票 ===")
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
            print(f"✓ {code}: {stock_info['name']}")
        else:
            print(f"✗ {code}: 期望 {expected_name}, 实际 {stock_info['name']}")
            all_passed = False

    if all_passed:
        print("\n✅ 所有验证通过！")
    else:
        print("\n❌ 部分验证失败")

    print("\n" + "=" * 70)


if __name__ == '__main__':
    test_all_stock_json()
