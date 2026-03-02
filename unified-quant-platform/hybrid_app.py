#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 统一量化交易平台 v5.2 - 混合数据版本
模拟数据 + 真实数据源配置
"""

import os
import sys
import json
import datetime
from flask import Flask, render_template_string, jsonify, request, send_from_directory

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'


# ============ 模拟数据 ============

def get_mock_realtime_data(symbol):
    """获取模拟实时数据"""
    symbol_clean = str(symbol).replace('sh', '').replace('sz', '').replace('.SH', '').replace('.SZ', '').strip()

    # 模拟股票名称映射
    stock_names = {
        '600519': '贵州茅台',
        '600000': '浦发银行',
        '000001': '平安银行',
        '000002': '万科A',
        '601318': '中国平安'
    }

    name = stock_names.get(symbol_clean, f'股票{symbol_clean}')

    # 模拟价格数据
    import random
    base_price = float(symbol_clean) / 100000 if len(symbol_clean) == 6 else 10.0
    if base_price < 1:
        base_price = 10.0

    price = round(base_price * (0.95 + random.random() * 0.1), 2)
    change_percent = round(random.uniform(-5, 5), 2)
    change = round(price * change_percent / 100, 2)

    # 生成交易信号
    signals = []
    if change_percent > 0:
        signals.append('上涨')
    if change_percent > 3:
        signals.append('强势')
    elif change_percent < -3:
        signals.append('弱势')

    if abs(change_percent) < 0.5:
        signals.append('震荡')

    if change_percent > 2:
        signals.append('买入')
    elif change_percent < -2:
        signals.append('卖出')

    return {
        'success': True,
        'message': '数据获取成功（演示版本）',
        'source': 'demo',
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'is_demo': True,  # 标记为演示数据
        'data': {
            'symbol': symbol_clean,
            'name': name,
            'price': price,
            'change': change,
            'change_percent': f"{change_percent:+.2f}%",
            'volume': random.randint(100000, 10000000),
            'amount': random.randint(10000000, 1000000000),
            'high': round(price * 1.05, 2),
            'low': round(price * 0.95, 2),
            'open': round(price * (0.98 + random.random() * 0.04), 2),
            'pre_close': round(price - change, 2),
            'signals': signals,
            'indicators': {
                'ma5': round(price * (1 + change_percent * 0.001 * 5), 2),
                'ma10': round(price * (1 + change_percent * 0.001 * 10), 2),
                'ma20': round(price * (1 + change_percent * 0.001 * 20), 2),
                'rsi': 50 + change_percent,
                'macd': change_percent * 0.1
            }
        }
    }


def get_mock_market_data():
    """获取模拟市场数据"""
    import random

    # 模拟市场数据
    total_stocks = random.randint(5000, 6000)
    up_ratio = random.random()
    up_stocks = int(total_stocks * up_ratio)
    down_stocks = total_stocks - up_stocks

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
        'message': '市场分析完成（演示版本）',
        'source': 'demo',
        'is_demo': True,
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'data': {
            'trend': trend,
            'sentiment': sentiment,
            'hot_sectors': hot_sectors,
            'market_cap': f"{random.randint(450000, 550000)}亿",
            'volume': f"{random.randint(10000, 20000)}万手",
            'up_count': up_stocks,
            'down_count': down_stocks,
            'total_count': total_stocks,
            'advice': '建议持有优质蓝筹股' if up_ratio >= 0.5 else '建议谨慎观望'
        }
    }


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

        .demo-notice {
            background: #fff3e0;
            color: #e65100;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            border-left: 4px solid #ff9800;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .demo-notice h3 {
            font-size: 16px;
            margin-bottom: 5px;
            color: #e65100;
        }

        .demo-notice p {
            font-size: 14px;
            color: #ff6f00;
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

        .error-message {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
        }

        .demo-badge {
            background: #ff9800;
            color: white;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: bold;
            margin-left: 5px;
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

        <div class="demo-notice">
            <h3>⚠️ 演示版本提示</h3>
            <p>当前使用模拟数据进行演示，仅供界面功能展示。真实数据功能开发中，如需使用真实数据请联系管理员配置数据源。</p>
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
                <input type="text" id="realtime-symbol" placeholder="例如：600519" value="600519">
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
                <input type="text" id="chip-symbol" placeholder="例如：600519" value="600519">
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

            let html = `
                <div class="data-header">
                    <h3>${stock.name} (${stock.symbol})</h3>
                    <div class="data-source">
                        数据源: ${data.source === 'demo' ? '模拟数据' : data.source}
                        ${data.is_demo ? '<span class="demo-badge">演示</span>' : ''}
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

            let html = `
                <div class="data-header">
                    <h3>市场综合分析</h3>
                    <div class="data-source">
                        数据源: ${data.source === 'demo' ? '模拟数据' : data.source}
                        ${data.is_demo ? '<span class="demo-badge">演示</span>' : ''}
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

                        let html = `
                            <div class="data-header">
                                <h3>${stock.name} (${stock.symbol}) - 筹码分布</h3>
                                <div class="data-source">
                                    数据源: ${data.source === 'demo' ? '模拟数据' : data.source}
                                    ${data.is_demo ? '<span class="demo-badge">演示</span>' : ''}
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

        // 页面加载完成后自动执行实时分析
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
    return jsonify(get_mock_realtime_data(symbol))


@app.route('/api/market')
def market():
    """市场分析API"""
    return jsonify(get_mock_market_data())


@app.route('/api/chip/<symbol>')
def chip(symbol):
    """筹码分析API"""
    return jsonify(get_mock_realtime_data(symbol))


@app.route('/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'version': '5.2-hybrid',
        'data_source': 'demo',
        'message': '演示版本 - 使用模拟数据'
    })


# ============ 启动应用 ============

if __name__ == '__main__':
    print("""
======================================================================
🚀 OpenClaw 统一量化交易平台 v5.2 - 混合数据版本
======================================================================

✅ 特性:
  • 完整的量化分析界面
  • 模拟数据演示
  • 毫秒级响应速度
  • 清晰的演示标识

💡 数据源:
  • 当前: 模拟数据（演示版本）
  • 未来: 可配置真实数据源

⚠️  注意:
  • 当前数据为模拟数据，仅供演示
  • 如需使用真实数据，请配置数据源

======================================================================

🌐 应用启动中...
访问地址: http://localhost:7000
默认账户: admin / admin123

======================================================================
    """)

    app.run(host='0.0.0.0', port=7000, debug=False)
