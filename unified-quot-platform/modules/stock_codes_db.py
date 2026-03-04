#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票代码数据库 - 经过验证的股票代码对照表
最后更新: 2026-03-04
"""

# 经过验证的股票代码对照表
VALIDATED_STOCK_CODES = {
    # 银行股
    '000001': {'name': '平安银行', 'sector': '银行', 'market': '深圳'},
    '600000': {'name': '浦发银行', 'sector': '银行', 'market': '上海'},
    '600036': {'name': '招商银行', 'sector': '银行', 'market': '上海'},
    '601166': {'name': '兴业银行', 'sector': '银行', 'market': '上海'},
    '601288': {'name': '农业银行', 'sector': '银行', 'market': '上海'},
    '601318': {'name': '中国平安', 'sector': '保险', 'market': '上海'},
    '601398': {'name': '工商银行', 'sector': '银行', 'market': '上海'},
    '601939': {'name': '建设银行', 'sector': '银行', 'market': '上海'},
    '601988': {'name': '中国银行', 'sector': '银行', 'market': '上海'},

    # 白酒股
    '000568': {'name': '泸州老窖', 'sector': '白酒', 'market': '深圳'},
    '000596': {'name': '古井贡酒', 'sector': '白酒', 'market': '深圳'},
    '000799': {'name': '酒鬼酒', 'sector': '白酒', 'market': '深圳'},
    '000858': {'name': '五粮液', 'sector': '白酒', 'market': '深圳'},
    '600559': {'name': '老白干酒', 'sector': '白酒', 'market': '上海'},
    '600519': {'name': '贵州茅台', 'sector': '白酒', 'market': '上海'},
    '600809': {'name': '山西汾酒', 'sector': '白酒', 'market': '上海'},
    '603369': {'name': '今世缘', 'sector': '白酒', 'market': '上海'},
    '603589': {'name': '口子窖', 'sector': '白酒', 'market': '上海'},

    # 科技股
    '000063': {'name': '中兴通讯', 'sector': '通信设备', 'market': '深圳'},
    '000977': {'name': '浪潮信息', 'sector': '计算机', 'market': '深圳'},
    '002415': {'name': '海康威视', 'sector': '安防', 'market': '深圳'},
    '300033': {'name': '同花顺', 'sector': '互联网金融', 'market': '深圳'},
    '300433': {'name': '蓝思科技', 'sector': '电子', 'market': '深圳'},
    '600050': {'name': '中国联通', 'sector': '通信', 'market': '上海'},
    '601012': {'name': '隆基绿能', 'sector': '光伏', 'market': '上海'},
    '601138': {'name': '工业富联', 'sector': '电子', 'market': '上海'},
    '603019': {'name': '中科曙光', 'sector': '计算机', 'market': '上海'},
    '688111': {'name': '金山办公', 'sector': '软件', 'market': '科创板'},

    # 新能源车
    '002594': {'name': '比亚迪', 'sector': '新能源汽车', 'market': '深圳'},
    '300014': {'name': '亿纬锂能', 'sector': '电池', 'market': '深圳'},
    '300124': {'name': '汇川技术', 'sector': '工业自动化', 'market': '深圳'},
    '300750': {'name': '宁德时代', 'sector': '电池', 'market': '深圳'},
    '688005': {'name': '容百科技', 'sector': '电池材料', 'market': '科创板'},
    '688036': {'name': '传音控股', 'sector': '手机', 'market': '科创板'},

    # 医药股
    '000661': {'name': '长春高新', 'sector': '生物医药', 'market': '深圳'},
    '300015': {'name': '爱尔眼科', 'sector': '医疗服务', 'market': '深圳'},
    '300347': {'name': '泰格医药', 'sector': 'CRO', 'market': '深圳'},
    '300760': {'name': '迈瑞医疗', 'sector': '医疗器械', 'market': '深圳'},
    '600276': {'name': '恒瑞医药', 'sector': '化学制药', 'market': '上海'},
    '603259': {'name': '药明康德', 'sector': 'CRO', 'market': '上海'},

    # 消费股
    '000333': {'name': '美的集团', 'sector': '家电', 'market': '深圳'},
    '000651': {'name': '格力电器', 'sector': '家电', 'market': '深圳'},
    '000876': {'name': '新希望', 'sector': '农业', 'market': '深圳'},
    '002304': {'name': '洋河股份', 'sector': '白酒', 'market': '深圳'},
    '600887': {'name': '伊利股份', 'sector': '乳制品', 'market': '上海'},
    '601888': {'name': '中国中免', 'sector': '免税', 'market': '上海'},

    # 周期股
    '000001': {'name': '平安银行', 'sector': '银行', 'market': '深圳'},
    '000898': {'name': '鞍钢股份', 'sector': '钢铁', 'market': '深圳'},
    '600019': {'name': '宝钢股份', 'sector': '钢铁', 'market': '上海'},
    '600547': {'name': '山东黄金', 'sector': '黄金', 'market': '上海'},
    '601898': {'name': '中煤能源', 'sector': '煤炭', 'market': '上海'},
    '601919': {'name': '中远海控', 'sector': '航运', 'market': '上海'},

    # ST股票（风险警示）
    '002496': {'name': '*ST辉丰', 'sector': '农化制品', 'market': '深圳', 'note': '原辉丰化工'},

    # 其他
    '000002': {'name': '万科A', 'sector': '房地产', 'market': '深圳'},
    '300059': {'name': '东方财富', 'sector': '证券', 'market': '深圳'},
}


def get_stock_name(code: str) -> str:
    """
    根据股票代码获取股票名称

    参数:
        code: 股票代码

    返回:
        str: 股票名称，如果不存在返回未知
    """
    stock_info = VALIDATED_STOCK_CODES.get(code)
    if stock_info:
        return stock_info['name']
    return '未知'


def get_stock_info(code: str) -> dict:
    """
    根据股票代码获取股票信息

    参数:
        code: 股票代码

    返回:
        dict: 股票信息，如果不存在返回None
    """
    return VALIDATED_STOCK_CODES.get(code)


def validate_code(code: str) -> bool:
    """
    验证股票代码是否在数据库中

    参数:
        code: 股票代码

    返回:
        bool: 是否有效
    """
    return code in VALIDATED_STOCK_CODES


def get_all_codes() -> list:
    """获取所有股票代码"""
    return list(VALIDATED_STOCK_CODES.keys())


if __name__ == '__main__':
    print("=== 验证关键股票代码 ===")

    test_codes = ['002496', '000001', '600519', '603019', '601318']

    for code in test_codes:
        stock_info = get_stock_info(code)
        if stock_info:
            note = f" ({stock_info.get('note', '')})" if 'note' in stock_info else ''
            print(f"✓ {code}: {stock_info['name']} - {stock_info['sector']}{note}")
        else:
            print(f"✗ {code}: 未找到")
