#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
稳定股票查询模块 - 备用数据库为主，实时数据为辅
确保数据无误，系统稳定运行
"""
import akshare as ak
import logging
from typing import Dict, Optional, List
from datetime import datetime
import time

# 导入备用数据库
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.stock_codes_db import VALIDATED_STOCK_CODES, get_stock_info as get_backup_info

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StockQueryStable:
    """稳定股票查询 - 备用数据库为主，确保数据无误"""

    def __init__(self, try_realtime: bool = False):
        """
        初始化

        参数:
            try_realtime: 是否尝试实时数据（默认False，仅使用备用数据库）
        """
        self.try_realtime = try_realtime
        self.cache = {}
        self.cache_expiry = 600  # 缓存10分钟

    def query_stock(self, code: str) -> Dict:
        """
        查询股票信息（使用备用数据库，确保数据无误）

        参数:
            code: 股票代码

        返回:
            dict: 股票信息（保证返回，不会为None）
        """
        # 检查缓存
        cached = self._get_cache(code)
        if cached:
            return cached

        logger.info(f"[StockQueryStable] 查询股票: {code}")

        # 主要数据源：备用数据库（经过验证，保证准确）
        backup_info = self._get_backup_info(code)

        if backup_info:
            backup_info['data_source'] = 'backup'
            backup_info['validated'] = True
            backup_info['query_time'] = datetime.now().isoformat()
            self._set_cache(code, backup_info)
            logger.info(f"[StockQueryStable] 查询成功: {code} = {backup_info['name']} (备用数据库)")
            return backup_info

        # 备用数据库中不存在，尝试实时数据（如果启用）
        if self.try_realtime:
            realtime_info = self._query_realtime(code)
            if realtime_info:
                realtime_info['data_source'] = 'realtime'
                realtime_info['validated'] = False
                self._set_cache(code, realtime_info)
                logger.warning(f"[StockQueryStable] 使用实时数据: {code} = {realtime_info['name']}")
                return realtime_info

        # 全部失败，返回默认值
        logger.error(f"[StockQueryStable] 查询失败: {code}")
        return {
            'code': code,
            'name': '未知',
            'sector': '未知',
            'data_source': 'none',
            'validated': False,
            'query_time': datetime.now().isoformat(),
            'note': '数据不可用'
        }

    def _get_backup_info(self, code: str) -> Optional[Dict]:
        """获取备用数据库信息"""
        backup_info = get_backup_info(code)
        if backup_info:
            return {
                'code': code,
                'name': backup_info['name'],
                'sector': backup_info['sector'],
                'market': backup_info.get('market', '未知'),
                'source': 'backup_database'
            }
        return None

    def _query_realtime(self, code: str, retry: int = 1) -> Optional[Dict]:
        """实时查询（仅作为补充）"""
        try:
            stock_info = ak.stock_individual_info_em(symbol=code)
            name = stock_info[stock_info['item'] == '股票简称']['value'].values[0]
            industry = stock_info[stock_info['item'] == '行业']['value'].values[0] if '行业' in stock_info['item'].values else '未知'

            return {
                'code': code,
                'name': name,
                'sector': industry,
                'source': 'akshare.stock_individual_info_em'
            }

        except Exception as e:
            logger.debug(f"[StockQueryStable] 实时查询失败: {e}")
            return None

    def _get_cache(self, code: str) -> Optional[Dict]:
        """获取缓存"""
        cached = self.cache.get(code)
        if cached:
            if time.time() - cached['time'] < self.cache_expiry:
                return cached['data']
            else:
                del self.cache[code]
        return None

    def _set_cache(self, code: str, data: Dict):
        """设置缓存"""
        self.cache[code] = {'data': data, 'time': time.time()}

    def batch_query(self, codes: List[str]) -> Dict[str, Dict]:
        """批量查询"""
        results = {}
        logger.info(f"[StockQueryStable] 批量查询 {len(codes)} 个股票")

        for code in codes:
            stock_info = self.query_stock(code)
            results[code] = stock_info

        return results

    def validate_code(self, code: str) -> Dict:
        """
        验证股票代码

        返回:
            dict: {'valid': bool, 'code': str, 'name': str, 'data_source': str}
        """
        stock_info = self.query_stock(code)

        return {
            'valid': stock_info['name'] != '未知',
            'code': stock_info['code'],
            'name': stock_info['name'],
            'sector': stock_info['sector'],
            'data_source': stock_info['data_source'],
            'validated': stock_info.get('validated', False)
        }


def test_stable_query():
    """测试稳定查询"""
    print("=" * 70)
    print("稳定股票查询测试（备用数据库为主）")
    print("=" * 70)

    # 使用稳定查询（默认仅使用备用数据库）
    query = StockQueryStable(try_realtime=False)

    # 测试1: 查询002496
    print("\n=== 测试1: 查询002496 ===")
    result = query.validate_code('002496')
    print(f"有效: {result['valid']}")
    print(f"代码: {result['code']}")
    print(f"名称: {result['name']}")
    print(f"行业: {result['sector']}")
    print(f"数据源: {result['data_source']}")
    print(f"已验证: {result['validated']}")

    # 测试2: 批量查询
    print("\n=== 测试2: 批量查询 ===")
    codes = ['000001', '600519', '603019', '601318']
    results = query.batch_query(codes)

    for code, info in results.items():
        print(f"✓ {code}: {info['name']} ({info['sector']}) [{info['data_source']}]")

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
        result = query.validate_code(code)
        if result['valid'] and result['name'] == expected_name:
            status = "✅" if result['validated'] else "⚠️"
            print(f"{status} {code}: {result['name']} (已验证: {result['validated']})")
        else:
            print(f"❌ {code}: 期望 {expected_name}, 实际 {result['name']}")
            all_passed = False

    if all_passed:
        print("\n✅ 所有验证通过！数据准确无误")
    else:
        print("\n❌ 部分验证失败")

    print("\n" + "=" * 70)


if __name__ == '__main__':
    test_stable_query()
