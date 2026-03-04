#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时行情数据源 - 腾讯、新浪API
获取盘中实时数据
"""
import requests
import logging
from datetime import datetime
from typing import Dict, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RealtimeQuote:
    """实时行情查询"""

    def __init__(self):
        self.name = "实时行情"

    def query_tencent(self, code: str) -> Optional[Dict]:
        """
        查询腾讯实时行情

        参数:
            code: 股票代码（6位）

        返回:
            dict: 实时行情数据
        """
        try:
            # 转换代码格式
            tencent_code = self._convert_code(code, 'tencent')
            url = f"http://qt.gtimg.cn/q={tencent_code}"

            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                # 解析返回数据
                data_str = response.text
                if '~' in data_str:
                    data = data_str.split('~')

                    if len(data) > 40:  # 确保数据完整
                        return {
                            'code': code,
                            'name': data[1],
                            'price': float(data[3]) if data[3] else 0,
                            'open': float(data[5]) if data[5] else 0,
                            'high': float(data[33]) if data[33] else 0,
                            'low': float(data[34]) if data[34] else 0,
                            'close_prev': float(data[4]) if data[4] else 0,
                            'volume': float(data[6]) if data[6] else 0,
                            'amount': float(data[37]) if data[37] else 0,
                            'data_source': 'tencent_realtime',
                            'source': '腾讯财经实时行情',
                            'query_time': datetime.now().isoformat()
                        }

        except Exception as e:
            logger.debug(f"[RealtimeQuote] 腾讯查询失败 {code}: {e}")

        return None

    def query_sina(self, code: str) -> Optional[Dict]:
        """
        查询新浪实时行情

        参数:
            code: 股票代码（6位）

        返回:
            dict: 实时行情数据
        """
        try:
            # 转换代码格式
            sina_code = self._convert_code(code, 'sina')
            url = f"http://hq.sinajs.cn/list={sina_code}"

            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                # 解析返回数据
                data_str = response.text
                if '="' in data_str:
                    data = data_str.split('="')[1].split('"')[0].split(',')

                    if len(data) > 3:
                        open_price = float(data[1]) if data[1] else 0
                        close_prev = float(data[2]) if data[2] else 0
                        current_price = float(data[3]) if data[3] else 0

                        # 计算涨跌幅
                        change_pct = 0
                        if close_prev > 0:
                            change_pct = ((current_price - close_prev) / close_prev) * 100

                        return {
                            'code': code,
                            'name': data[0],
                            'price': current_price,
                            'open': open_price,
                            'high': float(data[4]) if len(data) > 4 and data[4] else 0,
                            'low': float(data[5]) if len(data) > 5 and data[5] else 0,
                            'close_prev': close_prev,
                            'volume': float(data[8]) if len(data) > 8 and data[8] else 0,
                            'amount': float(data[9]) if len(data) > 9 and data[9] else 0,
                            'change_pct': change_pct,
                            'data_source': 'sina_realtime',
                            'source': '新浪财经实时行情',
                            'query_time': datetime.now().isoformat()
                        }

        except Exception as e:
            logger.debug(f"[RealtimeQuote] 新浪查询失败 {code}: {e}")

        return None

    def _convert_code(self, code: str, platform: str) -> str:
        """
        转换代码格式

        参数:
            code: 6位代码
            platform: 'tencent' | 'sina'

        返回:
            str: 转换后的代码
        """
        if platform == 'tencent':
            if code.startswith('6'):
                return f'sh{code}'
            else:
                return f'sz{code}'
        elif platform == 'sina':
            if code.startswith('6'):
                return f'sh{code}'
            else:
                return f'sz{code}'
        return code

    def query(self, code: str, prefer_source: str = 'tencent') -> Optional[Dict]:
        """
        查询实时行情（多数据源）

        参数:
            code: 股票代码
            prefer_source: 优先数据源（'tencent' | 'sina'）

        返回:
            dict: 实时行情数据
        """
        logger.info(f"[RealtimeQuote] 查询实时行情: {code}")

        # 按优先级尝试数据源
        sources = ['tencent', 'sina']
        if prefer_source == 'sina':
            sources = ['sina', 'tencent']

        for source in sources:
            try:
                if source == 'tencent':
                    data = self.query_tencent(code)
                else:
                    data = self.query_sina(code)

                if data and data['price'] > 0:
                    logger.info(f"[RealtimeQuote] 查询成功: {code} = {data['name']} ({source})")
                    return data

            except Exception as e:
                logger.debug(f"[RealtimeQuote] {source}查询失败: {e}")

        logger.error(f"[RealtimeQuote] 所有数据源查询失败: {code}")
        return None


def test_realtime_quote():
    """测试实时行情查询"""
    print("=" * 70)
    print("实时行情查询测试")
    print("=" * 70)

    quote = RealtimeQuote()

    # 测试中国核建
    code = '601611'

    print(f"\n=== 查询 {code} 中国核建 ===")

    # 测试腾讯
    print("\n1. 腾讯财经实时行情")
    tencent_data = quote.query_tencent(code)
    if tencent_data:
        print(f"✓ 股票: {tencent_data['name']}")
        print(f"✓ 价格: {tencent_data['price']:.2f}")
        print(f"✓ 开盘: {tencent_data['open']:.2f}")
        print(f"✓ 最高: {tencent_data['high']:.2f}")
        print(f"✓ 最低: {tencent_data['low']:.2f}")
        print(f"✓ 成交量: {tencent_data['volume']:,.0f}")
        print(f"✓ 成交额: {tencent_data['amount']:,.0f}")
        print(f"✓ 查询时间: {tencent_data['query_time']}")
    else:
        print("✗ 查询失败")

    # 测试新浪
    print("\n2. 新浪财经实时行情")
    sina_data = quote.query_sina(code)
    if sina_data:
        print(f"✓ 股票: {sina_data['name']}")
        print(f"✓ 价格: {sina_data['price']:.2f}")
        print(f"✓ 涨跌幅: {sina_data['change_pct']:.2f}%")
        print(f"✓ 开盘: {sina_data['open']:.2f}")
        print(f"✓ 最高: {sina_data['high']:.2f}")
        print(f"✓ 最低: {sina_data['low']:.2f}")
        print(f"✓ 成交量: {sina_data['volume']:,.0f}")
        print(f"✓ 成交额: {sina_data['amount']:,.0f}")
        print(f"✓ 查询时间: {sina_data['query_time']}")
    else:
        print("✗ 查询失败")

    # 综合查询
    print("\n3. 综合查询（自动选择）")
    combined_data = quote.query(code)
    if combined_data:
        print(f"✓ 数据源: {combined_data['source']}")
        print(f"✓ 股票: {combined_data['name']}")
        print(f"✓ 价格: {combined_data['price']:.2f}")
        if 'change_pct' in combined_data:
            print(f"✓ 涨跌幅: {combined_data['change_pct']:.2f}%")
        print(f"✓ 查询时间: {combined_data['query_time']}")
    else:
        print("✗ 查询失败")

    print("\n" + "=" * 70)


if __name__ == '__main__':
    test_realtime_quote()
