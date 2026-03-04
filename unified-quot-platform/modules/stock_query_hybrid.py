#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能股票查询模块 - 混合实时数据和备用数据库
优先使用实时数据，失败时使用经过验证的备用数据库
"""
import akshare as ak
import logging
from typing import Dict, Optional, List
from datetime import datetime
import time

# 导入备用数据库
try:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from modules.stock_codes_db import VALIDATED_STOCK_CODES, get_stock_info as get_backup_info
    BACKUP_DB_AVAILABLE = True
except ImportError:
    BACKUP_DB_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("[StockQueryHybrid] 备用数据库不可用")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StockQueryHybrid:
    """智能股票查询 - 混合模式"""

    def __init__(self, prefer_realtime: bool = True, cache_enabled: bool = True):
        """
        初始化

        参数:
            prefer_realtime: 是否优先使用实时数据
            cache_enabled: 是否启用缓存
        """
        self.prefer_realtime = prefer_realtime
        self.cache_enabled = cache_enabled
        self.cache = {}  # {code: {'data': info, 'time': timestamp, 'source': 'realtime'|'backup'}}
        self.cache_expiry = 300  # 缓存5分钟

    def query_stock(self, code: str) -> Optional[Dict]:
        """
        查询股票信息（智能选择数据源）

        参数:
            code: 股票代码

        返回:
            dict: 股票信息
        """
        # 检查缓存
        cached = self._get_cache(code)
        if cached:
            return cached

        # 优先使用实时数据
        if self.prefer_realtime:
            # 尝试实时查询
            realtime_info = self._query_realtime(code)
            if realtime_info:
                realtime_info['data_source'] = 'realtime'
                self._set_cache(code, realtime_info)
                logger.info(f"[StockQueryHybrid] 实时数据: {code} = {realtime_info['name']}")
                return realtime_info

        # 实时数据失败，使用备用数据库
        if BACKUP_DB_AVAILABLE:
            backup_info = self._get_backup_info(code)
            if backup_info:
                backup_info['data_source'] = 'backup'
                backup_info['note'] = '使用备用数据库'
                self._set_cache(code, backup_info)
                logger.warning(f"[StockQueryHybrid] 备用数据: {code} = {backup_info['name']}")
                return backup_info

        # 全部失败
        logger.error(f"[StockQueryHybrid] 查询失败: {code}")
        return None

    def _query_realtime(self, code: str, retry: int = 2) -> Optional[Dict]:
        """实时查询"""
        for attempt in range(retry):
            try:
                # 方法1: 个股详细信息
                stock_info = ak.stock_individual_info_em(symbol=code)

                name = stock_info[stock_info['item'] == '股票简称']['value'].values[0]
                industry = stock_info[stock_info['item'] == '行业']['value'].values[0] if '行业' in stock_info['item'].values else '未知'

                result = {
                    'code': code,
                    'name': name,
                    'sector': industry,
                    'source': 'akshare.stock_individual_info_em',
                    'query_time': datetime.now().isoformat()
                }

                return result

            except Exception as e:
                logger.debug(f"[StockQueryHybrid] 实时查询失败(第{attempt+1}次): {e}")
                if attempt < retry - 1:
                    time.sleep(0.5)

        return None

    def _get_backup_info(self, code: str) -> Optional[Dict]:
        """获取备用数据库信息"""
        if not BACKUP_DB_AVAILABLE:
            return None

        backup_info = get_backup_info(code)
        if backup_info:
            return {
                'code': code,
                'name': backup_info['name'],
                'sector': backup_info['sector'],
                'source': 'backup_database',
                'query_time': datetime.now().isoformat()
            }
        return None

    def _get_cache(self, code: str) -> Optional[Dict]:
        """获取缓存"""
        if not self.cache_enabled:
            return None

        cached = self.cache.get(code)
        if cached:
            if time.time() - cached['time'] < self.cache_expiry:
                logger.debug(f"[StockQueryHybrid] 使用缓存: {code}")
                return cached['data']
            else:
                del self.cache[code]

        return None

    def _set_cache(self, code: str, data: Dict):
        """设置缓存"""
        if self.cache_enabled:
            self.cache[code] = {'data': data, 'time': time.time()}

    def batch_query(self, codes: List[str]) -> Dict[str, Optional[Dict]]:
        """批量查询"""
        results = {}
        logger.info(f"[StockQueryHybrid] 批量查询 {len(codes)} 个股票")

        for code in codes:
            stock_info = self.query_stock(code)
            results[code] = stock_info

            time.sleep(0.2)

        return results

    def validate_stock(self, code: str) -> Dict[str, any]:
        """
        验证股票（返回验证结果）

        返回:
            dict: {
                'valid': bool,
                'code': str,
                'name': str,
                'sector': str,
                'data_source': 'realtime'|'backup'|'none',
                'note': str
            }
        """
        stock_info = self.query_stock(code)

        if stock_info:
            return {
                'valid': True,
                'code': stock_info['code'],
                'name': stock_info['name'],
                'sector': stock_info['sector'],
                'data_source': stock_info['data_source'],
                'note': stock_info.get('note', '')
            }
        else:
            return {
                'valid': False,
                'code': code,
                'name': '未知',
                'sector': '未知',
                'data_source': 'none',
                'note': '查询失败'
            }


def test_hybrid_query():
    """测试混合查询"""
    print("=" * 70)
    print("智能股票查询测试（混合模式）")
    print("=" * 70)

    query = StockQueryHybrid(prefer_realtime=True)

    # 测试1: 查询002496
    print("\n=== 测试1: 查询002496 ===")
    result = query.validate_stock('002496')
    if result['valid']:
        print(f"✓ 代码: {result['code']}")
        print(f"✓ 名称: {result['name']}")
        print(f"✓ 行业: {result['sector']}")
        print(f"✓ 数据源: {result['data_source']}")
        if result['note']:
            print(f"  注: {result['note']}")
    else:
        print(f"✗ 查询失败: {result['note']}")

    # 测试2: 批量查询
    print("\n=== 测试2: 批量查询 ===")
    codes = ['000001', '600519', '603019']
    results = query.batch_query(codes)

    for code, info in results.items():
        if info:
            source_emoji = "⚡" if info['data_source'] == 'realtime' else "💾"
            print(f"{source_emoji} {code}: {info['name']} ({info['sector']})")
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
        result = query.validate_stock(code)
        if result['valid'] and result['name'] == expected_name:
            source = "实时" if result['data_source'] == 'realtime' else "备用"
            print(f"✓ {code}: {result['name']} [{source}数据]")
        else:
            print(f"✗ {code}: 期望 {expected_name}, 实际 {result['name']}")
            all_passed = False

    if all_passed:
        print("\n✅ 所有验证通过！")
    else:
        print("\n❌ 部分验证失败")

    print("\n" + "=" * 70)


if __name__ == '__main__':
    test_hybrid_query()
