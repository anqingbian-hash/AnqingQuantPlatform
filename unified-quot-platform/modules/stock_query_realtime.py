#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时股票查询模块 - 使用AKShare实时查询股票信息
避免硬编码数据，确保数据准确性
"""
import akshare as ak
import pandas as pd
import logging
from typing import Dict, Optional, List
from datetime import datetime
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StockQueryRealtime:
    """实时股票查询"""

    def __init__(self, cache_enabled: bool = True, cache_expiry: int = 300):
        """
        初始化

        参数:
            cache_enabled: 是否启用缓存
            cache_expiry: 缓存过期时间（秒）
        """
        self.cache_enabled = cache_enabled
        self.cache_expiry = cache_expiry
        self.cache = {}  # {code: {'data': info, 'time': timestamp}}

    def _get_cache(self, code: str) -> Optional[Dict]:
        """获取缓存"""
        if not self.cache_enabled:
            return None

        cached = self.cache.get(code)
        if cached:
            if time.time() - cached['time'] < self.cache_expiry:
                logger.debug(f"[StockQueryRealtime] 使用缓存: {code}")
                return cached['data']
            else:
                del self.cache[code]  # 缓存过期，删除

        return None

    def _set_cache(self, code: str, data: Dict):
        """设置缓存"""
        if self.cache_enabled:
            self.cache[code] = {'data': data, 'time': time.time()}

    def query_stock_info(self, code: str, retry: int = 3) -> Optional[Dict]:
        """
        查询股票信息

        参数:
            code: 股票代码（如 '000001', '600519'）
            retry: 重试次数

        返回:
            dict: 股票信息 {'code': '000001', 'name': '平安银行', 'sector': '银行', 'price': 12.34, ...}
                 或 None（查询失败）
        """
        # 检查缓存
        cached_data = self._get_cache(code)
        if cached_data:
            return cached_data

        logger.info(f"[StockQueryRealtime] 查询股票: {code}")

        # 尝试多种查询方法
        for attempt in range(retry):
            try:
                # 方法1: 个股详细信息
                stock_info = self._query_by_individual_info(code)
                if stock_info:
                    self._set_cache(code, stock_info)
                    return stock_info

                # 方法2: 实时行情
                stock_info = self._query_by_spot_em(code)
                if stock_info:
                    self._set_cache(code, stock_info)
                    return stock_info

            except Exception as e:
                logger.warning(f"[StockQueryRealtime] 第{attempt+1}次查询失败: {e}")
                if attempt < retry - 1:
                    time.sleep(1)

        logger.error(f"[StockQueryRealtime] 查询失败: {code}")
        return None

    def _query_by_individual_info(self, code: str) -> Optional[Dict]:
        """方法1: 通过个股详细信息查询"""
        try:
            stock_info = ak.stock_individual_info_em(symbol=code)

            # 提取关键信息
            name = stock_info[stock_info['item'] == '股票简称']['value'].values[0]
            industry = stock_info[stock_info['item'] == '行业']['value'].values[0] if '行业' in stock_info['item'].values else '未知'
            price = stock_info[stock_info['item'] == '最新']['value'].values[0] if '最新' in stock_info['item'].values else None

            # 转换价格
            try:
                price = float(price) if price else None
            except:
                price = None

            result = {
                'code': code,
                'name': name,
                'sector': industry,
                'price': price,
                'source': 'akshare.stock_individual_info_em',
                'query_time': datetime.now().isoformat()
            }

            logger.info(f"[StockQueryRealtime] 查询成功: {code} = {name} ({industry})")
            return result

        except Exception as e:
            logger.error(f"[StockQueryRealtime] 方法1失败: {e}")
            return None

    def _query_by_spot_em(self, code: str) -> Optional[Dict]:
        """方法2: 通过实时行情查询"""
        try:
            # 获取A股实时行情
            stock_zh_a_spot_df = ak.stock_zh_a_spot_em()

            # 查找目标股票
            stock_row = stock_zh_a_spot_df[stock_zh_a_spot_df['代码'] == code]

            if not stock_row.empty:
                row = stock_row.iloc[0]
                name = row['名称']
                industry = row.get('行业', '未知') if '行业' in stock_zh_a_spot_df.columns else '未知'
                price = float(row['最新价']) if '最新价' in stock_zh_a_spot_df.columns else None
                change_pct = float(row['涨跌幅']) if '涨跌幅' in stock_zh_a_spot_df.columns else None

                result = {
                    'code': code,
                    'name': name,
                    'sector': str(industry),
                    'price': price,
                    'change_pct': change_pct,
                    'source': 'akshare.stock_zh_a_spot_em',
                    'query_time': datetime.now().isoformat()
                }

                logger.info(f"[StockQueryRealtime] 查询成功: {code} = {name} ({industry})")
                return result
            else:
                logger.warning(f"[StockQueryRealtime] 未找到股票代码: {code}")
                return None

        except Exception as e:
            logger.error(f"[StockQueryRealtime] 方法2失败: {e}")
            return None

    def batch_query(self, codes: List[str]) -> Dict[str, Optional[Dict]]:
        """
        批量查询股票信息

        参数:
            codes: 股票代码列表

        返回:
            dict: {code: stock_info}
        """
        results = {}
        logger.info(f"[StockQueryRealtime] 批量查询 {len(codes)} 个股票")

        for code in codes:
            stock_info = self.query_stock_info(code)
            results[code] = stock_info

            # 避免请求过快
            time.sleep(0.3)

        return results

    def get_stock_name(self, code: str) -> str:
        """
        获取股票名称（便捷方法）

        参数:
            code: 股票代码

        返回:
            str: 股票名称，失败返回'未知'
        """
        stock_info = self.query_stock_info(code)
        if stock_info:
            return stock_info['name']
        return '未知'

    def validate_code_name(self, code: str, expected_name: str) -> bool:
        """
        验证股票代码和名称是否匹配

        参数:
            code: 股票代码
            expected_name: 期望的股票名称

        返回:
            bool: 是否匹配
        """
        actual_name = self.get_stock_name(code)
        is_match = actual_name == expected_name

        if is_match:
            logger.info(f"[StockQueryRealtime] 验证通过: {code} = {actual_name}")
        else:
            logger.error(f"[StockQueryRealtime] 验证失败: {code}, 期望={expected_name}, 实际={actual_name}")

        return is_match


def test_realtime_query():
    """测试实时查询"""
    print("=" * 60)
    print("实时股票查询测试")
    print("=" * 60)

    query = StockQueryRealtime()

    # 测试1: 查询002496
    print("\n=== 测试1: 查询002496 ===")
    stock_info = query.query_stock_info('002496')
    if stock_info:
        print(f"✓ 代码: {stock_info['code']}")
        print(f"✓ 名称: {stock_info['name']}")
        print(f"✓ 行业: {stock_info['sector']}")
        if stock_info['price']:
            print(f"✓ 价格: {stock_info['price']:.2f}")
        print(f"✓ 数据源: {stock_info['source']}")
    else:
        print("✗ 查询失败")

    # 测试2: 批量查询
    print("\n=== 测试2: 批量查询 ===")
    codes = ['000001', '600519', '603019']
    results = query.batch_query(codes)

    for code, info in results.items():
        if info:
            print(f"✓ {code}: {info['name']} ({info['sector']})")
        else:
            print(f"✗ {code}: 查询失败")

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
        is_valid = query.validate_code_name(code, expected_name)
        if is_valid:
            print(f"✓ {code}: {expected_name}")
        else:
            print(f"✗ {code}: 验证失败")
            all_passed = False

    if all_passed:
        print("\n✅ 所有验证通过！")
    else:
        print("\n❌ 部分验证失败")

    print("=" * 60)


if __name__ == '__main__':
    test_realtime_query()
