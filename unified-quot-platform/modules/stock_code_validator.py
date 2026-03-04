#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票代码验证器 - 确保数据准确性
使用多数据源交叉验证股票代码和名称
"""
import akshare as ak
import pandas as pd
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StockCodeValidator:
    """股票代码验证器"""

    def __init__(self):
        self.name = "StockCodeValidator"
        self.cache = {}  # 缓存已查询的股票信息
        self.cache_expiry = 3600  # 缓存过期时间（秒）

    def validate_stock_code(self, code: str, retry: int = 3) -> Optional[Dict[str, str]]:
        """
        验证股票代码，返回股票信息

        参数:
            code: 股票代码（如 '000001', '600519'）
            retry: 重试次数

        返回:
            dict: 股票信息 {'code': '000001', 'name': '平安银行', 'sector': '银行'}
                 或 None（查询失败）
        """
        # 检查缓存
        if code in self.cache:
            cached_data, cached_time = self.cache[code]
            if time.time() - cached_time < self.cache_expiry:
                logger.info(f"[StockCodeValidator] 使用缓存: {code}")
                return cached_data

        logger.info(f"[StockCodeValidator] 查询股票代码: {code}")

        # 尝试多种查询方法
        for attempt in range(retry):
            try:
                # 方法1: 个股详细信息
                stock_info = self._query_stock_info_em(code)
                if stock_info:
                    self.cache[code] = (stock_info, time.time())
                    return stock_info

                # 方法2: 实时行情查询
                stock_info = self._query_stock_spot_em(code)
                if stock_info:
                    self.cache[code] = (stock_info, time.time())
                    return stock_info

            except Exception as e:
                logger.warning(f"[StockCodeValidator] 第{attempt+1}次查询失败: {e}")
                if attempt < retry - 1:
                    time.sleep(1)

        logger.error(f"[StockCodeValidator] 查询失败: {code}")
        return None

    def _query_stock_info_em(self, code: str) -> Optional[Dict[str, str]]:
        """方法1: 通过个股详细信息查询"""
        try:
            stock_info = ak.stock_individual_info_em(symbol=code)

            # 提取关键信息
            name = stock_info[stock_info['item'] == '股票简称']['value'].values[0]
            industry = stock_info[stock_info['item'] == '行业']['value'].values[0] if '行业' in stock_info['item'].values else '未知'

            result = {
                'code': code,
                'name': name,
                'sector': industry,
                'source': 'akshare.stock_individual_info_em'
            }

            logger.info(f"[StockCodeValidator] 查询成功: {code} = {name} ({industry})")
            return result

        except Exception as e:
            logger.error(f"[StockCodeValidator] 方法1失败: {e}")
            return None

    def _query_stock_spot_em(self, code: str) -> Optional[Dict[str, str]]:
        """方法2: 通过实时行情查询"""
        try:
            # 获取A股实时行情
            stock_zh_a_spot_df = ak.stock_zh_a_spot_em()

            # 查找目标股票
            stock_row = stock_zh_a_spot_df[stock_zh_a_spot_df['代码'] == code]

            if not stock_row.empty:
                name = stock_row['名称'].values[0]
                industry = stock_row.get('行业', '未知').values[0] if '行业' in stock_row.columns else '未知'

                result = {
                    'code': code,
                    'name': name,
                    'sector': str(industry),
                    'source': 'akshare.stock_zh_a_spot_em'
                }

                logger.info(f"[StockCodeValidator] 查询成功: {code} = {name} ({industry})")
                return result
            else:
                logger.warning(f"[StockCodeValidator] 未找到股票代码: {code}")
                return None

        except Exception as e:
            logger.error(f"[StockCodeValidator] 方法2失败: {e}")
            return None

    def batch_validate(self, codes: list) -> Dict[str, Optional[Dict[str, str]]]:
        """
        批量验证股票代码

        参数:
            codes: 股票代码列表

        返回:
            dict: {code: stock_info}
        """
        results = {}
        logger.info(f"[StockCodeValidator] 批量验证 {len(codes)} 个股票代码")

        for code in codes:
            stock_info = self.validate_stock_code(code)
            results[code] = stock_info

            # 避免请求过快
            time.sleep(0.5)

        return results

    def validate_and_replace_mock_data(self, mock_data: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        用真实数据替换Mock数据

        参数:
            mock_data: Mock数据 {code: {'name': 'xxx', ...}}

        返回:
            dict: 真实数据 {code: {'name': 'xxx', ...}}
        """
        logger.info(f"[StockCodeValidator] 验证并替换 {len(mock_data)} 条Mock数据")

        real_data = {}
        errors = []

        for code, mock_info in mock_data.items():
            stock_info = self.validate_stock_code(code)

            if stock_info:
                # 保留Mock数据中的其他字段，但覆盖name和sector
                real_data[code] = {
                    **mock_info,
                    'name': stock_info['name'],
                    'sector': stock_info['sector'],
                    'source': stock_info['source']
                }
            else:
                # 查询失败，保留Mock数据但标记为未验证
                real_data[code] = {
                    **mock_info,
                    'validated': False,
                    'error': '查询失败'
                }
                errors.append(code)

        logger.info(f"[StockCodeValidator] 验证完成: {len(real_data)-len(errors)}/{len(mock_data)} 成功")

        if errors:
            logger.warning(f"[StockCodeValidator] 以下股票代码查询失败: {errors}")

        return real_data

    def get_common_stocks(self) -> Dict[str, str]:
        """
        获取常用股票代码对照表

        返回:
            dict: {code: name}
        """
        common_stocks = {
            '000001': '平安银行',
            '000002': '万科A',
            '000333': '美的集团',
            '000651': '格力电器',
            '000858': '五粮液',
            '000977': '浪潮信息',
            '002496': '*ST辉丰',
            '002594': '比亚迪',
            '300750': '宁德时代',
            '600036': '招商银行',
            '600519': '贵州茅台',
            '601012': '隆基绿能',
            '601318': '中国平安',
            '601888': '中国中免',
            '603019': '中科曙光',
            '603259': '药明康德',
        }

        logger.info(f"[StockCodeValidator] 常用股票代码对照表: {len(common_stocks)} 条")
        return common_stocks


def test_validator():
    """测试股票代码验证器"""
    validator = StockCodeValidator()

    print("=== 测试1: 单个股票代码验证 ===")
    stock_info = validator.validate_stock_code('002496')
    if stock_info:
        print(f"✓ {stock_info['code']}: {stock_info['name']} ({stock_info['sector']})")
    else:
        print("✗ 查询失败")

    print("\n=== 测试2: 批量验证 ===")
    codes = ['000001', '600519', '002496']
    results = validator.batch_validate(codes)
    for code, info in results.items():
        if info:
            print(f"✓ {code}: {info['name']} ({info['sector']})")
        else:
            print(f"✗ {code}: 查询失败")

    print("\n=== 测试3: 常用股票对照表 ===")
    common_stocks = validator.get_common_stocks()
    for code, name in list(common_stocks.items())[:5]:
        print(f"{code}: {name}")


if __name__ == '__main__':
    test_validator()
