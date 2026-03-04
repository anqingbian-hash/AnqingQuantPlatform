#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全A股实时查询模块 - 对接全部A股数据，实时更新
"""
import akshare as ak
import pandas as pd
import logging
from typing import Dict, Optional, List
from datetime import datetime
import time
import json
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AllAStockQuery:
    """全A股实时查询"""

    def __init__(self, cache_enabled: bool = True, cache_expiry: int = 300):
        """
        初始化

        参数:
            cache_enabled: 是否启用缓存
            cache_expiry: 缓存过期时间（秒）
        """
        self.cache_enabled = cache_enabled
        self.cache_expiry = cache_expiry
        self.cache = {}
        self.all_stock_df = None  # 完整A股行情数据
        self.last_update_time = None

        # 尝试加载完整A股数据
        self._load_all_stock_data()

    def _load_all_stock_data(self, retry: int = 3):
        """加载完整A股数据"""
        for attempt in range(retry):
            try:
                logger.info(f"[AllAStockQuery] 加载完整A股数据 (尝试 {attempt+1}/{retry})...")
                self.all_stock_df = ak.stock_zh_a_spot_em()
                self.last_update_time = datetime.now()

                logger.info(f"[AllAStockQuery] 成功加载 {len(self.all_stock_df)} 只A股")
                return True

            except Exception as e:
                logger.warning(f"[AllAStockQuery] 加载失败: {e}")
                if attempt < retry - 1:
                    time.sleep(2)
                else:
                    logger.error("[AllAStockQuery] 加载A股数据失败")
                    self.all_stock_df = None

        return False

    def refresh_data(self):
        """刷新A股数据"""
        logger.info("[AllAStockQuery] 刷新A股数据...")
        return self._load_all_stock_data()

    def query_stock(self, code: str) -> Dict:
        """
        查询股票信息

        参数:
            code: 股票代码（如 '000001', '600519'）

        返回:
            dict: 股票信息
        """
        # 检查缓存
        cached = self._get_cache(code)
        if cached:
            return cached

        logger.info(f"[AllAStockQuery] 查询股票: {code}")

        # 如果A股数据未加载，先加载
        if self.all_stock_df is None:
            if not self._load_all_stock_data():
                # 加载失败，尝试单个查询
                return self._query_single(code)

        # 从完整数据中查找
        stock_info = self._query_from_all(code)
        if stock_info:
            self._set_cache(code, stock_info)
            return stock_info

        # 未找到，尝试单个查询
        stock_info = self._query_single(code)
        if stock_info:
            self._set_cache(code, stock_info)
            return stock_info

        # 全部失败
        logger.error(f"[AllAStockQuery] 查询失败: {code}")
        return {
            'code': code,
            'name': '未知',
            'sector': '未知',
            'data_source': 'none',
            'query_time': datetime.now().isoformat()
        }

    def _query_from_all(self, code: str) -> Optional[Dict]:
        """从完整数据中查询"""
        if self.all_stock_df is None:
            return None

        try:
            stock_row = self.all_stock_df[self.all_stock_df['代码'] == code]

            if not stock_row.empty:
                row = stock_row.iloc[0]
                name = row['名称']
                price = float(row.get('最新价', 0)) if '最新价' in row.index else None
                change_pct = float(row.get('涨跌幅', 0)) if '涨跌幅' in row.index else None
                industry = str(row.get('行业', '未知')) if '行业' in row.index else '未知'

                result = {
                    'code': code,
                    'name': name,
                    'sector': industry,
                    'price': price,
                    'change_pct': change_pct,
                    'data_source': 'realtime_all',
                    'source': 'akshare.stock_zh_a_spot_em',
                    'query_time': datetime.now().isoformat(),
                    'last_update': self.last_update_time.isoformat() if self.last_update_time else None
                }

                logger.info(f"[AllAStockQuery] 查询成功: {code} = {name} ({industry})")
                return result
            else:
                return None

        except Exception as e:
            logger.error(f"[AllAStockQuery] 从完整数据查询失败: {e}")
            return None

    def _query_single(self, code: str, retry: int = 2) -> Optional[Dict]:
        """单个查询"""
        for attempt in range(retry):
            try:
                stock_info = ak.stock_individual_info_em(symbol=code)
                name = stock_info[stock_info['item'] == '股票简称']['value'].values[0]
                industry = stock_info[stock_info['item'] == '行业']['value'].values[0] if '行业' in stock_info['item'].values else '未知'

                result = {
                    'code': code,
                    'name': name,
                    'sector': industry,
                    'data_source': 'realtime_single',
                    'source': 'akshare.stock_individual_info_em',
                    'query_time': datetime.now().isoformat()
                }

                logger.info(f"[AllAStockQuery] 单个查询成功: {code} = {name}")
                return result

            except Exception as e:
                logger.debug(f"[AllAStockQuery] 单个查询失败(第{attempt+1}次): {e}")
                if attempt < retry - 1:
                    time.sleep(1)

        return None

    def _get_cache(self, code: str) -> Optional[Dict]:
        """获取缓存"""
        if not self.cache_enabled:
            return None

        cached = self.cache.get(code)
        if cached:
            if time.time() - cached['time'] < self.cache_expiry:
                return cached['data']
            else:
                del self.cache[code]

        return None

    def _set_cache(self, code: str, data: Dict):
        """设置缓存"""
        if self.cache_enabled:
            self.cache[code] = {'data': data, 'time': time.time()}

    def get_all_stocks(self) -> Optional[pd.DataFrame]:
        """获取所有A股数据"""
        return self.all_stock_df

    def get_stock_count(self) -> int:
        """获取股票数量"""
        if self.all_stock_df is not None:
            return len(self.all_stock_df)
        return 0

    def search_stock(self, keyword: str) -> List[Dict]:
        """
        搜索股票（按名称或代码）

        参数:
            keyword: 关键词

        返回:
            list: 匹配的股票列表
        """
        if self.all_stock_df is None:
            return []

        try:
            # 按代码搜索
            code_matches = self.all_stock_df[self.all_stock_df['代码'].str.contains(keyword)]

            # 按名称搜索
            name_matches = self.all_stock_df[self.all_stock_df['名称'].str.contains(keyword)]

            # 合并结果
            results = pd.concat([code_matches, name_matches]).drop_duplicates()

            return [
                {
                    'code': row['代码'],
                    'name': row['名称'],
                    'sector': str(row.get('行业', '未知')) if '行业' in row.index else '未知'
                }
                for _, row in results.head(20).iterrows()
            ]

        except Exception as e:
            logger.error(f"[AllAStockQuery] 搜索失败: {e}")
            return []

    def batch_query(self, codes: List[str]) -> Dict[str, Dict]:
        """批量查询"""
        results = {}
        logger.info(f"[AllAStockQuery] 批量查询 {len(codes)} 个股票")

        for code in codes:
            stock_info = self.query_stock(code)
            results[code] = stock_info

        return results

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        if self.all_stock_df is None:
            return {
                'total': 0,
                'last_update': None,
                'status': 'not_loaded'
            }

        return {
            'total': len(self.all_stock_df),
            'last_update': self.last_update_time.isoformat() if self.last_update_time else None,
            'status': 'loaded',
            'cache_size': len(self.cache)
        }


def test_all_stock_query():
    """测试全A股查询"""
    print("=" * 70)
    print("全A股实时查询测试")
    print("=" * 70)

    # 初始化
    query = AllAStockQuery(cache_enabled=True, cache_expiry=300)

    # 等待数据加载
    time.sleep(2)

    # 获取统计信息
    print("\n=== 统计信息 ===")
    stats = query.get_statistics()
    print(f"股票总数: {stats['total']}")
    print(f"最后更新: {stats['last_update']}")
    print(f"状态: {stats['status']}")

    # 测试1: 查询特定股票
    print("\n=== 测试1: 查询特定股票 ===")
    test_codes = ['000001', '600519', '002496', '603019']
    results = query.batch_query(test_codes)

    for code, info in results.items():
        if info['name'] != '未知':
            print(f"✓ {code}: {info['name']} ({info['sector']}) [{info['data_source']}]")
            if info.get('price'):
                print(f"    价格: {info['price']:.2f}, 涨跌: {info.get('change_pct', 0):.2f}%")
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
    test_all_stock_query()
