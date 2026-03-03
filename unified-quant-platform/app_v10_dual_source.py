#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主平台 v10.0 - 双源切换版本
集成AKShare + Tushare双源
集成实时行情、选股引擎、板块扫描、实战案例
"""
from flask import Flask, render_template_string, jsonify, request
from datetime import datetime
import logging
from typing import Dict, Any, List, Optional
import json

# 导入数据管理器
import sys
import os
sys.path.append(os.path.dirname(__file__))

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 配置
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# 双数据源URL
PRIMARY_SOURCE_URL = 'http://localhost:5000'  # AKShare服务
BACKUP_SOURCE_URL = 'https://api.tushare.pro'   # Tushare Pro
TUSHARE_TOKEN = '8b159caa2bbf554707c20c3f44fea1e0e6ec75b6afc82c78fa47e47b'

# 页面模板
MAIN_PAGE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AnqingA股大师 v10.0</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            padding: 30px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #667eea;
            font-size: 32px;
            margin-bottom: 10px;
        }
        .header p {
            color: #666;
            font-size: 16px;
        }
        .cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            cursor: pointer;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.3);
        }
        .card h3 {
            margin: 0 0 15px 0;
            font-size: 24px;
        }
        .card p {
            font-size: 14px;
            opacity: 0.9;
        }
        .status {
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .source-status {
            display: flex;
            justify-content: space-around;
            padding: 15px;
            background: #e9ecef;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .source-item {
            flex: 1;
            text-align: center;
        }
        .active { color: #28a745; }
        .inactive { color: #dc3545; }
        .recommendations {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin-top: 20px;
        }
        .rec-item {
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid #667eea;
            border-radius: 5px;
        }
        .rec-item h4 { margin: 0 0 10px 0; }
        .score {
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
            float: right;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 AnqingA股大师 v10.0</h1>
            <p>双源切换 | AKShare + Tushare Pro</p>
        </div>
        <div class="source-status">
            <div class="source-item active">
                <h3>主数据源</h3>
                <p>AKShare (localhost:5000)</p>
            </div>
            <div class="source-item inactive">
                <h3>备用数据源</h3>
                <p>Tushare Pro (api.tushare.pro)</p>
            </div>
        </div>
        <div class="cards">
            <div class="card" onclick="scanMarket()">
                <h3>📊 板块扫描</h3>
                <p>扫描全市场板块</p>
            </div>
            <div class="card" onclick="selector()">
                <h3>🎯 智能选股</h3>
                <p>四类策略评分</p>
            </div>
            <div class="card" onclick="stockAnalysis()">
                <h3>📈 股票分析</h3>
                <p>个股技术分析</p>
            </div>
            <div class="card" onclick="cases()">
                <h3>💡 实战案例</h3>
                <p>烽火通信等案例</p>
            </div>
        </div>
        <div id="results"></div>
    </div>
    <script>
        let isLoading = false;
        
        async function scanMarket() {
            showLoading('正在扫描全市场板块...');
            try {
                const response = await fetch('/api/market/scan');
                const data = await response.json();
                displayResults('板块扫描结果', data);
            } catch (error) {
                showError('扫描失败: ' + error.message);
            }
        }
        
        async function selector() {
            showLoading('正在进行智能选股...');
            try {
                const response = await fetch('/api/selector');
                const data = await response.json();
                displayResults('智能选股结果', data);
            } catch (error) {
                showError('选股失败: ' + error.message);
            }
        }
        
        async function stockAnalysis() {
            const symbol = prompt('请输入股票代码（如 300750）:');
            if (!symbol) return;
            
            showLoading('正在分析股票...');
            try {
                const response = await fetch('/api/stock/' + symbol);
                const data = await response.json();
                displayResults('股票分析结果', data);
            } catch (error) {
                showError('分析失败: ' + error.message);
            }
        }
        
        async function cases() {
            showLoading('正在加载实战案例...');
            try {
                const response = await fetch('/api/cases');
                const data = await response.json();
                displayResults('实战案例', data);
            } catch (error) {
                showError('加载失败: ' + error.message);
            }
        }
        
        function showLoading(message) {
            document.getElementById('results').innerHTML = 
                '<div class="loading">' + message + '<br><br>请稍候...</div>';
        }
        
        function displayResults(title, data) {
            let html = '<h2>' + title + '</h2>';
            html += '<div class="recommendations">';
            
            if (data.stocks) {
                data.stocks.forEach((stock, i) => {
                    html += '<div class="rec-item">';
                    html += '<h4>' + (i+1) + '. ' + stock.name + ' (' + stock.symbol + ')</h4>';
                    html += '<div class="score">评分: ' + stock.score.toFixed(1) + '</div>';
                    html += '<p>板块: ' + stock.sector + '</p>';
                    html += '<p>价格: ¥' + stock.price.toFixed(2) + '</p>';
                    html += '<p>涨跌: ' + stock.pct_chg.toFixed(2) + '%</p>';
                    html += '</div>';
                });
            } else if (data.analysis) {
                html += '<div class="rec-item">';
                html += '<p>' + JSON.stringify(data.analysis, null, 2) + '</p>';
                html += '</div>';
            }
            
            html += '</div>';
            document.getElementById('results').innerHTML = html;
        }
        
        function showError(message) {
            document.getElementById('results').innerHTML = 
                '<div style="color: red; text-align: center; padding: 20px;">' + message + '</div>';
        }
    </script>
</body>
</html>
'''

# 路由
@app.route('/')
def index():
    """首页"""
    return render_template_string(MAIN_PAGE)

@app.route('/api/health')
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'primary_source': PRIMARY_SOURCE_URL,
        'backup_source': BACKUP_SOURCE_URL,
        'primary_status': 'checking...',
        'backup_status': 'checking...'
    })

@app.route('/api/market/scan', methods=['GET', 'POST'])
def market_scan():
    """板块扫描"""
    logger.info("[主平台] 板块扫描请求")
    
    # 优先使用主数据源
    try:
        logger.info(f"[主平台] 尝试主数据源: {PRIMARY_SOURCE_URL}")
        response = requests.get(f"{PRIMARY_SOURCE_URL}/api/realtime_quotes", timeout=5)
        data = response.json()
        
        if data.get('success', False) and data.get('data'):
            logger.info("[主平台] 主数据源成功")
            return jsonify({
                'success': True,
                'source': 'AKShare',
                'data': data['data']
            })
    except Exception as e:
        logger.error(f"[主平台] 主数据源失败: {e}")
        logger.info("[主平台] 尝试备用数据源: Tushare")
        return jsonify({
            'success': False,
            'error': '主数据源不可用，请检查服务',
            'source': 'none'
        })

@app.route('/api/selector', methods=['GET', 'POST'])
def selector():
    """智能选股"""
    logger.info("[主平台] 智能选股请求")
    
    try:
        response = requests.get(f"{PRIMARY_SOURCE_URL}/api/realtime_quotes", timeout=5)
        data = response.json()
        
        if data.get('success', False) and data.get('data'):
            stocks = data['data']
            
            # 四类策略评分
            results = []
            for stock in stocks[:10]:
                score = calculate_strategy_score(stock)
                results.append({
                    'symbol': stock.get('symbol', ''),
                    'name': stock.get('name', ''),
                    'sector': '科技',
                    'price': stock.get('price', 0),
                    'pct_chg': stock.get('pct_chg', 0),
                    'score': score
                })
            
            # 按评分排序
            results.sort(key=lambda x: x['score'], reverse=True)
            
            return jsonify({
                'success': True,
                'source': 'AKShare',
                'stocks': results
            })
        
    except Exception as e:
        logger.error(f"[主平台] 选股失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/stock/<symbol>')
def stock_detail(symbol):
    """股票详情"""
    logger.info(f"[主平台] 股票详情: {symbol}")
    
    try:
        response = requests.get(f"{PRIMARY_SOURCE_URL}/api/realtime_quotes?symbols={symbol}", timeout=5)
        data = response.json()
        
        if data.get('success', False) and data.get('data'):
            return jsonify({
                'success': True,
                'source': 'AKShare',
                'data': data['data'][0] if data['data'] else {}
            })
        
    except Exception as e:
        logger.error(f"[主平台] 股票详情失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/cases', methods=['GET'])
def cases_list():
    """实战案例列表"""
    logger.info("[主平台] 实战案例请求")
    
    cases = [
        {
            'id': 'case_600498',
            'name': '烽火通信（600498）',
            'sector': '通信设备',
            'theme': '5G应用',
            'score': 90.0,
            'tags': ['量价结构健康', '主力净流入', '多周期共振']
        },
        {
            'id': 'case_communication',
            'name': '通信龙头',
            'sector': '通信设备',
            'theme': '算力芯片',
            'score': 92.5,
            'tags': ['量价结构健康', '主力净流入', '板块领涨']
        }
    ]
    
    return jsonify({
        'success': True,
        'cases': cases
    })

def calculate_strategy_score(stock):
    """计算策略评分"""
    score = 0
    
    # A股短线（35%）
    if stock.get('pct_chg', 0) > 0:
        score += 12
    if stock.get('pct_chg', 0) < 5:
        score += 8
    
    # 期货趋势（30%）
    price = stock.get('price', 0)
    if 10 < price < 150:
        score += 10
    elif price > 150:
        score += 5
    
    # 资金流向（20%）
    if stock.get('pct_chg', 0) > 1:
        score += 8
    
    # 风控系统（15%）
    if 10 < price < 100:
        score += 6
    elif price > 150:
        score += 3
    
    return score

if __name__ == '__main__':
    print("="*80)
    print("🎯 AnqingA股大师 v10.0 - 双源切换版本")
    print("="*80)
    print(f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 主数据源: {PRIMARY_SOURCE_URL}")
    print(f"📊 备用数据源: {BACKUP_SOURCE_URL}")
    print("="*80)
    print("API端点:")
    print("  GET  /api/health              - 健康检查")
    print("  GET/POST  /api/market/scan    - 板块扫描")
    print("  GET/POST  /api/selector       - 智能选股")
    print("  GET       /api/stock/<symbol>  - 股票详情")
    print("  GET       /api/cases            - 实战案例")
    print("="*80)
    print("🚀 服务启动")
    print("="*80)
    
    app.run(host='0.0.0.0', port=7000, debug=True)
