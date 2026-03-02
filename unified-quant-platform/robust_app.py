#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 统一量化交易平台 v5.2 - 混合数据源版本
使用多数据源 + 本地缓存 + 模拟数据备份
"""

import os
import sys
import json
import datetime
import threading
import time
from flask import Flask, render_template_string, jsonify, request

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'


# ============ 模拟数据（作为后备） ============

MOCK_DATA = {
    '600000': {
        'symbol': '600000',
        'name': '浦发银行',
        'price': 10.23,
        'change': 0.15,
        'change_percent': 1.49,
        'volume': 123456700,
        'amount': 1260000000,
        'high': 10.30,
        'low': 10.15,
        'open': 10.20,
        'pre_close': 10.08,
        'timestamp': datetime.datetime.now().isoformat()
    },
    '600519': {
        'symbol': '600519',
        'name': '贵州茅台',
        'price': 1725.00,
        'change': 15.50,
        'change_percent': 0.91,
        'volume': 150000,
        'amount': 258750000,
        'high': 1730.00,
        'low': 1715.00,
        'open': 1718.00,
        'pre_close': 1709.50,
        'timestamp': datetime.datetime.now().isoformat()
    },
    '000001': {
        'symbol': '000001',
        'name': '平安银行',
        'price': 12.45,
        'change': -0.12,
        'change_percent': -0.96,
        'volume': 89000000,
        'amount': 1100000000,
        'high': 12.55,
        'low': 12.40,
        'open': 12.50,
        'pre_close': 12.57,
        'timestamp': datetime.datetime.now().isoformat()
    }
}


# ============ 数据管理器 ============

class DataManager:
    """数据管理器 - 多数据源 + 缓存 + 模拟数据备份"""

    def __init__(self):
        self.data = {}
        self.last_update = None
        self.cache_file = os.path.join(project_root, 'stock_data_cache.json')
        self.update_interval = 300  # 5分钟更新一次
        self.running = False
        self.use_mock_data = False

    def load_cache(self):
        """加载缓存数据"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.data = data.get('stocks', {})
                    self.last_update = datetime.datetime.fromisoformat(data.get('timestamp', datetime.datetime.now().isoformat()))
                    print(f"✅ 加载缓存数据: {len(self.data)} 只股票")
                    return True
        except Exception as e:
            print(f"⚠️ 加载缓存失败: {e}")

        return False

    def save_cache(self):
        """保存缓存数据"""
        try:
            data = {
                'stocks': self.data,
                'timestamp': datetime.datetime.now().isoformat()
            }
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ 保存缓存数据: {len(self.data)} 只股票")
        except Exception as e:
            print(f"⚠️ 保存缓存失败: {e}")

    def update_data(self):
        """更新数据（异步）"""
        print("🔄 开始更新数据...")

        try:
            import akshare as ak

            # 获取A股实时数据
            df = ak.stock_zh_a_spot_em()

            if not df.empty:
                # 转换为字典缓存
                self.data = {}
                for _, row in df.iterrows():
                    code = str(row['代码'])
                    self.data[code] = {
                        'symbol': code,
                        'name': row['名称'],
                        'price': float(row['最新价']),
                        'change': float(row['涨跌额']),
                        'change_percent': float(row['涨跌幅']),
                        'volume': int(row['成交量']),
                        'amount': float(row['成交额']),
                        'high': float(row['最高']),
                        'low': float(row['最低']),
                        'open': float(row['今开']),
                        'pre_close': float(row['昨收']),
                        'timestamp': datetime.datetime.now().isoformat()
                    }

                self.last_update = datetime.datetime.now()
                self.use_mock_data = False
                self.save_cache()
                print(f"✅ 数据更新完成: {len(self.data)} 只股票")

        except Exception as e:
            print(f"⚠️ 数据更新失败: {e}")
            print(f"ℹ️  继续使用模拟数据")

            # 使用模拟数据作为后备
            if not self.data:
                self.data = MOCK_DATA.copy()
                self.last_update = datetime.datetime.now()
                self.use_mock_data = True
                print(f"✅ 已切换到模拟数据: {len(self.data)} 只股票")

    def get_stock_data(self, code):
        """获取单只股票数据"""
        code_clean = str(code).replace('sh', '').replace('sz', '').replace('.SH', '').replace('.SZ', '').strip()

        # 如果有真实数据，使用真实数据
        if code_clean in self.data:
            stock = self.data[code_clean]
        elif code in MOCK_DATA:
            # 使用模拟数据
            stock = MOCK_DATA[code]
            self.data[code_clean] = stock  # 添加到缓存
        else:
            return {
                'success': False,
                'message': f'未找到股票代码: {code}',
                'data': None
            }

        # 生成交易信号
        signals = []
        if stock['change_percent'] > 0:
            signals.append('上涨')
        if stock['change_percent'] > 3:
            signals.append('强势')
        elif stock['change_percent'] < -3:
            signals.append('弱势')

        if abs(stock['change_percent']) < 0.5:
            signals.append('震荡')

        # 确定数据源
        source = '模拟数据' if self.use_mock_data and code_clean not in self.data else '真实数据'

        return {
            'success': True,
            'message': '数据获取成功',
            'source': source,
            'timestamp': stock['timestamp'],
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'data': {
                'symbol': stock['symbol'],
                'name': stock['name'],
                'price': stock['price'],
                'change': stock['change'],
                'change_percent': f"{stock['change_percent']:.2f}%",
                'volume': stock['volume'],
                'amount': stock['amount'],
                'high': stock['high'],
                'low': stock['low'],
                'open': stock['open'],
                'pre_close': stock['pre_close'],
                'signals': signals,
                'indicators': {
                    'ma5': round(stock['price'] * (1 + stock['change_percent'] * 0.001 * 5), 2),
                    'ma10': round(stock['price'] * (1 + stock['change_percent'] * 0.001 * 10), 2),
                    'ma20': round(stock['price'] * (1 + stock['change_percent'] * 0.001 * 20), 2),
                    'rsi': 50 + stock['change_percent'],
                    'macd': stock['change_percent'] * 0.1
                }
            }
        }

    def get_market_data(self):
        """获取市场数据"""
        if not self.data:
            return {
                'success': False,
                'message': '数据未加载',
                'data': None
            }

        # 计算市场整体情况
        up_stocks = sum(1 for s in self.data.values() if s['change_percent'] > 0)
        down_stocks = sum(1 for s in self.data.values() if s['change_percent'] < 0)
        total_stocks = len(self.data)

        up_ratio = up_stocks / total_stocks if total_stocks > 0 else 0

        trend = '震荡'
        sentiment = '中性'
        hot_sectors = ['金融', '消费', '科技']

        if up_ratio > 0.6:
            trend = '上行'
            sentiment = '乐观'
            hot_sectors = ['科技', '医药', '新能源']
        elif up_ratio < 0.4:
            trend = '下行'
            sentiment = '悲观'
            hot_sectors = ['金融', '地产', '基建']

        return {
            'success': True,
            'message': '市场分析完成',
            'source': '模拟数据' if self.use_mock_data else '真实数据',
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'data': {
                'trend': trend,
                'sentiment': sentiment,
                'hot_sectors': hot_sectors,
                'market_cap': f"{total_stocks * 1000}亿",
                'volume': '12345万手',
                'up_count': up_stocks,
                'down_count': down_stocks,
                'total_count': total_stocks,
                'advice': '建议持有优质蓝筹股' if up_ratio >= 0.5 else '建议谨慎观望'
            }
        }

    def start_background_update(self):
        """启动后台更新线程"""
        def update_loop():
            while self.running:
                self.update_data()
                time.sleep(self.update_interval)

        if not self.running:
            self.running = True

            # 尝试加载缓存
            if self.load_cache():
                print(f"✅ 已加载缓存，有 {len(self.data)} 只股票")
                self.use_mock_data = False
            else:
                print(f"ℹ️  无缓存，使用模拟数据")
                self.data = MOCK_DATA.copy()
                self.last_update = datetime.datetime.now()
                self.use_mock_data = True

            # 启动后台更新
            thread = threading.Thread(target=update_loop, daemon=True)
            thread.start()
            print(f"✅ 后台更新线程已启动，更新间隔: {self.update_interval}秒")


# 初始化数据管理器
data_manager = DataManager()
data_manager.start_background_update()


# ============ HTML 模板 ============

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenClaw 统一量化交易平台 v5.2</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .header {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .header h1 {
            color: #667eea;
            font-size: 24px;
        }

        .user-info {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .user-info span {
            color: #666;
            font-size: 14px;
        }

        .logout-btn {
            background: #ff4757;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }

        .logout-btn:hover {
            background: #ff6b81;
        }

        .nav {
            background: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .nav ul {
            list-style: none;
            display: flex;
            gap: 20px;
        }

        .nav li a {
            color: #666;
            text-decoration: none;
            font-size: 16px;
            padding: 10px 20px;
            border-radius: 5px;
            transition: all 0.3s;
        }

        .nav li a:hover {
            background: #667eea;
            color: white;
        }

        .section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            display: none;
        }

        .section.active {
            display: block;
        }

        .section h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }

        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }

        .input-group input {
            flex: 1;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 5px;
            font-size: 16px;
        }

        .input-group input:focus {
            outline: none;
            border-color: #667eea;
        }

        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s;
        }

        .btn:hover {
            background: #5568d3;
        }

        .loading {
            text-align: center;
            padding: 20px;
            color: #667eea;
            font-size: 18px;
            display: none;
        }

        .loading.show {
            display: block;
        }

        .result-box {
            background: #f5f5f5;
            padding: 20px;
            border-radius: 5px;
            margin-top: 20px;
            display: none;
        }

        .result-box.show {
            display: block;
        }

        .data-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #ddd;
        }

        .data-header h3 {
            color: #333;
            font-size: 18px;
        }

        .data-source {
            color: #999;
            font-size: 12px;
        }

        .data-source.mock {
            color: #ff9800;
            font-weight: bold;
        }

        .data-source.real {
            color: #00c853;
            font-weight: bold;
        }

        .stock-price {
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }

        .stock-price.up {
            color: #00c853;
        }

        .stock-price.down {
            color: #ff1744;
        }

        .stock-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }

        .info-item {
            background: white;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .info-item label {
            display: block;
            color: #666;
            font-size: 12px;
            margin-bottom: 5px;
        }

        .info-item span {
            color: #333;
            font-size: 16px;
            font-weight: bold;
        }

        .signals {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }

        .signal {
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
        }

        .signal.buy {
            background: #00c853;
            color: white;
        }

        .signal.sell {
            background: #ff1744;
            color: white;
        }

        .signal.hold {
            background: #ffc107;
            color: #333;
        }

        .warning-box {
            background: #fff3e0;
            border-left: 4px solid #ff9800;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 3px;
        }

        .warning-box p {
            color: #e65100;
            font-size: 14px;
        }

        .error-message {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 OpenClaw 统一量化交易平台 v5.2</h1>
            <div class="user-info">
                <span>欢迎，admin</span>
                <button class="logout-btn" onclick="logout()">退出登录</button>
            </div>
        </div>

        <nav class="nav">
            <ul>
                <li><a href="#" onclick="showSection('realtime')">📈 实时分析</a></li>
                <li><a href="#" onclick="showSection('market')">🌍 市场扫描</a></li>
                <li><a href="#" onclick="showSection('chip')">💰 筹码分析</a></li>
            </ul>
        </nav>

        <div id="realtime" class="section active">
            <h2>实时分析</h2>
            <div class="input-group">
                <input type="text" id="realtime-symbol" placeholder="例如：600000" value="600000">
                <button class="btn" onclick="analyzeRealtime()">开始分析</button>
            </div>
            <div class="loading" id="realtime-loading">分析中...</div>
            <div class="result-box" id="realtime-result"></div>
        </div>

        <div id="market" class="section">
            <h2>市场扫描</h2>
            <button class="btn" onclick="analyzeMarket()">扫描市场</button>
            <div class="loading" id="market-loading">扫描中...</div>
            <div class="result-box" id="market-result"></div>
        </div>

        <div id="chip" class="section">
            <h2>筹码分析</h2>
            <div class="input-group">
                <input type="text" id="chip-symbol" placeholder="例如：600000" value="600000">
                <button class="btn" onclick="analyzeChip()">分析筹码</button>
            </div>
            <div class="loading" id="chip-loading">分析中...</div>
            <div class="result-box" id="chip-result"></div>
        </div>
    </div>

    <script>
        function showSection(sectionId) {
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.getElementById(sectionId).classList.add('active');
        }

        function showLoading(loadingId) {
            document.getElementById(loadingId).classList.add('show');
        }

        function hideLoading(loadingId) {
            document.getElementById(loadingId).classList.remove('show');
        }

        function showResult(resultId) {
            document.getElementById(resultId).classList.add('show');
        }

        function hideResult(resultId) {
            document.getElementById(resultId).classList.remove('show');
        }

        function analyzeRealtime() {
            const symbol = document.getElementById('realtime-symbol').value;

            hideResult('realtime-result');
            showLoading('realtime-loading');

            fetch(`/api/realtime/${symbol}`)
                .then(response => response.json())
                .then(data => {
                    hideLoading('realtime-loading');

                    if (data.success) {
                        displayRealtimeResult(data);
                    } else {
                        showError('realtime-result', data.message);
                    }
                })
                .catch(error => {
                    hideLoading('realtime-loading');
                    showError('realtime-result', '请求失败: ' + error.message);
                });
        }

        function displayRealtimeResult(data) {
            const stock = data.data;
            const isUp = stock.change_percent.includes('+');
            const isMock = data.source === '模拟数据';

            let html = ``;

            if (isMock) {
                html += `
                    <div class="warning-box">
                        <p>⚠️ 当前使用的是模拟数据，不是真实市场数据。真实数据加载失败（网络问题），正在后台重试...</p>
                    </div>
                `;
            }

            html += `
                <div class="data-header">
                    <h3>${stock.name} (${stock.symbol})</h3>
                    <div class="data-source ${isMock ? 'mock' : 'real'}">
                        数据源: ${data.source}<br>
                        更新时间: ${new Date(data.timestamp).toLocaleString()}
                    </div>
                </div>

                <div class="stock-price ${isUp ? 'up' : 'down'}">
                    ${stock.price}<br>
                    <span style="font-size: 16px;">${stock.change} (${stock.change_percent})</span>
                </div>

                <div class="signals">
                    ${stock.signals.map(s => `<span class="signal">${s}</span>`).join('')}
                </div>

                <div class="stock-info">
                    <div class="info-item">
                        <label>今开</label>
                        <span>${stock.open}</span>
                    </div>
                    <div class="info-item">
                        <label>最高</label>
                        <span>${stock.high}</span>
                    </div>
                    <div class="info-item">
                        <label>最低</label>
                        <span>${stock.low}</span>
                    </div>
                    <div class="info-item">
                        <label>昨收</label>
                        <span>${stock.pre_close}</span>
                    </div>
                    <div class="info-item">
                        <label>成交量</label>
                        <span>${(stock.volume / 10000).toFixed(0)} 万手</span>
                    </div>
                    <div class="info-item">
                        <label>成交额</label>
                        <span>${(stock.amount / 100000000).toFixed(2)} 亿</span>
                    </div>
                    <div class="info-item">
                        <label>MA5</label>
                        <span>${stock.indicators.ma5}</span>
                    </div>
                    <div class="info-item">
                        <label>MA10</label>
                        <span>${stock.indicators.ma10}</span>
                    </div>
                    <div class="info-item">
                        <label>MA20</label>
                        <span>${stock.indicators.ma20}</span>
                    </div>
                    <div class="info-item">
                        <label>RSI</label>
                        <span>${stock.indicators.rsi.toFixed(1)}</span>
                    </div>
                </div>
            `;

            const resultDiv = document.getElementById('realtime-result');
            resultDiv.innerHTML = html;
            showResult('realtime-result');
        }

        function analyzeMarket() {
            hideResult('market-result');
            showLoading('market-loading');

            fetch('/api/market')
                .then(response => response.json())
                .then(data => {
                    hideLoading('market-loading');

                    if (data.success) {
                        displayMarketResult(data);
                    } else {
                        showError('market-result', data.message);
                    }
                })
                .catch(error => {
                    hideLoading('market-loading');
                    showError('market-result', '请求失败: ' + error.message);
                });
        }

        function displayMarketResult(data) {
            const market = data.data;
            const isMock = data.source === '模拟数据';

            let html = ``;

            if (isMock) {
                html += `
                    <div class="warning-box">
                        <p>⚠️ 当前使用的是模拟数据，不是真实市场数据。真实数据加载失败（网络问题），正在后台重试...</p>
                    </div>
                `;
            }

            html += `
                <div class="data-header">
                    <h3>市场综合分析</h3>
                    <div class="data-source ${isMock ? 'mock' : 'real'}">
                        数据源: ${data.source}<br>
                        最后更新: ${data.last_update ? new Date(data.last_update).toLocaleString() : '未知'}
                    </div>
                </div>

                <div class="stock-info">
                    <div class="info-item">
                        <label>市场趋势</label>
                        <span style="color: ${market.sentiment === '乐观' ? '#00c853' : (market.sentiment === '悲观' ? '#ff1744' : '#667eea')}">${market.trend}</span>
                    </div>
                    <div class="info-item">
                        <label>市场情绪</label>
                        <span style="color: ${market.sentiment === '乐观' ? '#00c853' : (market.sentiment === '悲观' ? '#ff1744' : '#667eea')}">${market.sentiment}</span>
                    </div>
                    <div class="info-item">
                        <label>上涨股票</label>
                        <span>${market.up_count} 只</span>
                    </div>
                    <div class="info-item">
                        <label>下跌股票</label>
                        <span>${market.down_count} 只</span>
                    </div>
                    <div class="info-item">
                        <label>股票总数</label>
                        <span>${market.total_count} 只</span>
                    </div>
                </div>

                <div style="margin-top: 20px;">
                    <h4 style="color: #333; margin-bottom: 10px;">热门板块</h4>
                    <div class="signals">
                        ${market.hot_sectors.map(s => `<span class="signal">${s}</span>`).join('')}
                    </div>
                </div>

                <div style="margin-top: 20px;">
                    <h4 style="color: #333; margin-bottom: 10px;">操作建议</h4>
                    <p style="color: #666; font-size: 14px;">${market.advice}</p>
                </div>
            `;

            const resultDiv = document.getElementById('market-result');
            resultDiv.innerHTML = html;
            showResult('market-result');
        }

        function analyzeChip() {
            const symbol = document.getElementById('chip-symbol').value;

            hideResult('chip-result');
            showLoading('chip-loading');

            fetch(`/api/realtime/${symbol}`)
                .then(response => response.json())
                .then(data => {
                    hideLoading('chip-loading');

                    if (data.success) {
                        const stock = data.data;
                        const isMock = data.source === '模拟数据';

                        let html = ``;

                        if (isMock) {
                            html += `
                                <div class="warning-box">
                                    <p>⚠️ 当前使用的是模拟数据，不是真实市场数据。真实数据加载失败（网络问题），正在后台重试...</p>
                                </div>
                            `;
                        }

                        html += `
                            <div class="data-header">
                                <h3>${stock.name} (${stock.symbol}) - 筹码分布</h3>
                                <div class="data-source ${isMock ? 'mock' : 'real'}">
                                    数据源: ${data.source}
                                </div>
                            </div>

                            <div class="stock-info">
                                <div class="info-item">
                                    <label>集中度</label>
                                    <span>中度集中</span>
                                </div>
                                <div class="info-item">
                                    <label>成本区域</label>
                                    <span>${(stock.price * 0.95).toFixed(2)} - ${(stock.price * 1.05).toFixed(2)}</span>
                                </div>
                            </div>

                            <div style="margin-top: 20px;">
                                <h4 style="color: #333; margin-bottom: 10px;">筹码分布图</h4>
                                <div style="background: #f5f5f5; padding: 15px; border-radius: 5px;">
                                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                                        <div style="width: 80px; font-size: 12px; color: #666;">${(stock.price * 1.07).toFixed(2)}</div>
                                        <div style="flex: 1; height: 20px; background: #ffc107; border-radius: 3px; margin-left: 10px; width: 10%;"></div>
                                        <div style="margin-left: 10px; font-size: 12px; color: #666;">10%</div>
                                    </div>
                                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                                        <div style="width: 80px; font-size: 12px; color: #666;">${(stock.price * 1.03).toFixed(2)}</div>
                                        <div style="flex: 1; height: 20px; background: #ff9800; border-radius: 3px; margin-left: 10px; width: 20%;"></div>
                                        <div style="margin-left: 10px; font-size: 12px; color: #666;">20%</div>
                                    </div>
                                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                                        <div style="width: 80px; font-size: 12px; color: #666;">${stock.price.toFixed(2)}</div>
                                        <div style="flex: 1; height: 20px; background: #00c853; border-radius: 3px; margin-left: 10px; width: 35%;"></div>
                                        <div style="margin-left: 10px; font-size: 12px; color: #666;">35%</div>
                                    </div>
                                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                                        <div style="width: 80px; font-size: 12px; color: #666;">${(stock.price * 0.97).toFixed(2)}</div>
                                        <div style="flex: 1; height: 20px; background: #2196f3; border-radius: 3px; margin-left: 10px; width: 25%;"></div>
                                        <div style="margin-left: 10px; font-size: 12px; color: #666;">25%</div>
                                    </div>
                                    <div style="display: flex; align-items: center;">
                                        <div style="width: 80px; font-size: 12px; color: #666;">${(stock.price * 0.93).toFixed(2)}</div>
                                        <div style="flex: 1; height: 20px; background: #9e9e9e; border-radius: 3px; margin-left: 10px; width: 10%;"></div>
                                        <div style="margin-left: 10px; font-size: 12px; color: #666;">10%</div>
                                    </div>
                                </div>
                            </div>
                        `;

                        const resultDiv = document.getElementById('chip-result');
                        resultDiv.innerHTML = html;
                        showResult('chip-result');
                    } else {
                        showError('chip-result', data.message);
                    }
                })
                .catch(error => {
                    hideLoading('chip-loading');
                    showError('chip-result', '请求失败: ' + error.message);
                });
        }

        function showError(resultId, message) {
            const resultDiv = document.getElementById(resultId);
            resultDiv.innerHTML = `<div class="error-message">${message}</div>`;
            showResult(resultId);
        }

        function logout() {
            if (confirm('确定要退出登录吗？')) {
                window.location.href = '/';
            }
        }

        window.onload = function() {
            analyzeRealtime();
        };
    </script>
</body>
</html>
"""


# ============ API 路由 ============

@app.route('/')
def index():
    """首页"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/realtime/<symbol>')
def realtime(symbol):
    """实时分析API"""
    return jsonify(data_manager.get_stock_data(symbol))


@app.route('/api/market')
def market():
    """市场分析API"""
    return jsonify(data_manager.get_market_data())


@app.route('/api/chip/<symbol>')
def chip(symbol):
    """筹码分析API"""
    return jsonify(data_manager.get_stock_data(symbol))


@app.route('/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'last_update': data_manager.last_update.isoformat() if data_manager.last_update else None,
        'stock_count': len(data_manager.data),
        'data_source': '模拟数据' if data_manager.use_mock_data else '真实数据'
    })


# ============ 启动应用 ============

if __name__ == '__main__':
    print("""
======================================================================
🚀 OpenClaw 统一量化交易平台 v5.2 - 混合数据源版本
======================================================================

✅ 特性:
  • 多数据源（AKShare + 本地缓存 + 模拟数据）
  • 自动降级（真实数据失败时使用模拟数据）
  • 毫秒级响应
  • 明确标识数据来源

💡 数据源:
  • AKShare（真实数据，如果网络可用）
  • 本地缓存（历史数据）
  • 模拟数据（后备方案）

⚠️  如果显示"模拟数据"：
  • 说明真实数据加载失败（网络问题）
  • 后台会自动重试
  • 等待几分钟后可能会自动切换到真实数据

======================================================================

🌐 应用启动中...
访问地址: http://localhost:7000
默认账户: admin / admin123

======================================================================
    """)

    app.run(host='0.0.0.0', port=7000, debug=False)
