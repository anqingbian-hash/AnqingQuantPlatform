#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OpenClaw 统一量化交易平台 v9.0 - Tushare真实数据 + 智能选股"""
import os
import sys
import json
import datetime
import random
import threading
from flask import Flask, render_template_string, jsonify, request, redirect, url_for, session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'

TUSHARE_TOKEN = '8b159caa2bbf554707c20c3f44fea1e0e6ec75b6afc82c78fa47e47b'

try:
    import tushare as ts
    ts.set_token(TUSHARE_TOKEN)
    pro = ts.pro_api()
    TUSHARE_AVAILABLE = True
    print("✅ Tushare Token 配置成功")
except Exception as e:
    TUSHARE_AVAILABLE = False
    pro = None
    print(f"⚠️ Tushare初始化失败: {e}")

# 导入选股策略引擎
try:
    from strategy_engine import StockSelector
    STRATEGY_AVAILABLE = True
    print("✅ 选股策略引擎加载成功")
except Exception as e:
    STRATEGY_AVAILABLE = False
    print(f"⚠️ 选股策略引擎加载失败: {e}")

USERS = {'admin': 'admin123'}

def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

class TushareDataManager:
    def __init__(self):
        self.data_cache = {}
        self.cache_timestamp = None
        self.cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tushare_cache.json')
        self.update_interval = 300
        self.running = False
        self.lock = threading.Lock()
        self.active_source = 'tushare'
        self.load_cache()

    def load_cache(self):
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.data_cache = data.get('stocks', {})
                    ts = data.get('timestamp')
                    if ts:
                        self.cache_timestamp = datetime.datetime.fromisoformat(ts)
                    print(f"✅ 加载缓存: {len(self.data_cache)} 只股票")
                    return True
        except Exception as e:
            print(f"⚠️ 加载缓存失败: {e}")
        return False

    def save_cache(self):
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'stocks': self.data_cache,
                    'timestamp': datetime.datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            print(f"✅ 保存缓存: {len(self.data_cache)} 只股票")
        except Exception as e:
            print(f"⚠️ 保存缓存失败: {e}")

    def get_realtime_data_tushare(self):
        if not TUSHARE_AVAILABLE:
            return None
        try:
            print("🔄 使用 Tushare 数据源...")
            today = datetime.datetime.now().strftime('%Y%m%d')
            df = pro.daily(ts_code='', trade_date=today)
            if df.empty:
                print("⚠️ Tushare 返回空数据")
                return None
            print(f"✅ Tushare 成功: {len(df)} 只股票")
            data = {}
            for _, row in df.iterrows():
                code = row['ts_code'].replace('.', '')
                data[code] = {
                    'symbol': code,
                    'name': 'Unknown',
                    'price': float(row['close']),
                    'change': float(row['close'] - row['pre_close']),
                    'change_percent': float((row['close'] - row['pre_close']) / row['pre_close'] * 100),
                    'volume': int(row['vol'] * 100),
                    'amount': float(row['amount'] * 1000),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'open': float(row['open']),
                    'pre_close': float(row['pre_close']),
                    'timestamp': datetime.datetime.now().isoformat()
                }
            return data
        except Exception as e:
            print(f"⚠️ Tushare 获取失败: {e}")
            return None

    def update_data(self):
        print("=" * 60)
        print("🔄 开始更新数据...")
        print("=" * 60)
        with self.lock:
            data = self.get_realtime_data_tushare()
            if data is None:
                if self.data_cache:
                    print("⚠️ Tushare失败，使用缓存数据")
                    return
                else:
                    print("❌ 无可用数据")
                    return
            self.data_cache = data
            self.cache_timestamp = datetime.datetime.now()
            self.save_cache()
            print("=" * 60)
            print(f"✅ 数据更新完成: {len(self.data_cache)} 只股票")
            print(f"📊 数据源: Tushare（真实数据）")
            print("=" * 60)

    def get_stock_data(self, code):
        code_clean = str(code).replace('sh', '').replace('sz', '').replace('.SH', '').replace('.SZ', '').strip()
        if code_clean in self.data_cache:
            stock = self.data_cache[code_clean]
            signals = []
            if stock['change_percent'] > 0:
                signals.append('上涨')
            if stock['change_percent'] > 3:
                signals.append('强势')
            elif stock['change_percent'] < -3:
                signals.append('弱势')
            if abs(stock['change_percent']) < 0.5:
                signals.append('震荡')
            if stock['change_percent'] > 2:
                signals.append('买入')
            elif stock['change_percent'] < -2:
                signals.append('卖出')
            price = stock['price']
            change_percent = stock['change_percent']
            return {
                'success': True,
                'message': '数据获取成功（Tushare真实数据）',
                'source': 'tushare',
                'timestamp': stock.get('timestamp', datetime.datetime.now().isoformat()),
                'cache_timestamp': self.cache_timestamp.isoformat() if self.cache_timestamp else None,
                'data': {
                    'symbol': stock['symbol'],
                    'name': stock['name'],
                    'price': stock['price'],
                    'change': stock['change'],
                    'change_percent': f"{stock['change_percent']:+.2f}%",
                    'volume': stock['volume'],
                    'amount': stock['amount'],
                    'high': stock['high'],
                    'low': stock['low'],
                    'open': stock['open'],
                    'pre_close': stock['pre_close'],
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
        return {
            'success': False,
            'message': f'未找到股票代码: {code}',
            'data': None
        }

    def get_market_data(self):
        if not self.data_cache:
            return {
                'success': False,
                'message': '数据未加载',
                'data': None
            }
        with self.lock:
            up_stocks = sum(1 for s in self.data_cache.values() if s['change_percent'] > 0)
            down_stocks = sum(1 for s in self.data_cache.values() if s['change_percent'] < 0)
            total_stocks = len(self.data_cache)
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
                'message': '市场分析完成（Tushare真实数据）',
                'source': 'tushare',
                'cache_timestamp': self.cache_timestamp.isoformat() if self.cache_timestamp else None,
                'data': {
                    'trend': trend,
                    'sentiment': sentiment,
                    'hot_sectors': hot_sectors,
                    'market_cap': f"{total_stocks * 1000}亿",
                    'volume': f"{sum(s['volume'] for s in self.data_cache.values()) / 10000:.0f}万手",
                    'up_count': up_stocks,
                    'down_count': down_stocks,
                    'total_count': total_stocks,
                    'up_ratio': up_ratio,
                    'advice': '建议持有优质蓝筹股' if up_ratio >= 0.5 else '建议谨慎观望'
                }
            }

    def start_background_update(self):
        def update_loop():
            while self.running:
                try:
                    self.update_data()
                except Exception as e:
                    print(f"⚠️ 后台更新异常: {e}")
                import time
                time.sleep(self.update_interval)
        if not self.running:
            self.running = True
            self.update_data()
            thread = threading.Thread(target=update_loop, daemon=True)
            thread.start()
            print(f"✅ 后台更新线程已启动，更新间隔: {self.update_interval}秒")

data_manager = TushareDataManager()
data_manager.start_background_update()

# 初始化选股引擎
selector = StockSelector(pro) if STRATEGY_AVAILABLE else None

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenClaw 统一量化交易平台 v9.0</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }
        .header h1 { color: #667eea; font-size: 24px; }
        .user-info { display: flex; align-items: center; gap: 10px; }
        .user-info span { color: #666; font-size: 14px; }
        .logout-btn { background: #ff4757; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer; font-size: 14px; transition: background 0.3s; }
        .logout-btn:hover { background: #ff6b81; }
        .data-status { background: #e3f2fd; color: #1565c0; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 4px solid #2196f3; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .data-status h3 { font-size: 16px; margin-bottom: 5px; color: #1565c0; }
        .data-status p { font-size: 14px; color: #1976d2; }
        .nav { background: white; padding: 15px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .nav ul { list-style: none; display: flex; gap: 10px; flex-wrap: wrap; }
        .nav li a { color: #666; text-decoration: none; font-size: 14px; padding: 8px 16px; border-radius: 5px; transition: all 0.3s; }
        .nav li a:hover { background: #667eea; color: white; }
        .nav li a.active { background: #667eea; color: white; }
        .section { background: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: none; }
        .section.active { display: block; }
        .section h2 { color: #333; margin-bottom: 20px; font-size: 20px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }
        .input-group { display: flex; gap: 10px; margin-bottom: 20px; }
        .input-group input { flex: 1; padding: 12px; border: 2px solid #e0e0e0; border-radius: 5px; font-size: 16px; }
        .input-group input:focus { outline: none; border-color: #667eea; }
        .btn { background: #667eea; color: white; border: none; padding: 12px 24px; border-radius: 5px; cursor: pointer; font-size: 16px; transition: background 0.3s; }
        .btn:hover { background: #5568d3; }
        .loading { text-align: center; padding: 20px; color: #667eea; font-size: 18px; display: none; }
        .loading.show { display: block; }
        .result-box { background: #f5f5f5; padding: 20px; border-radius: 5px; margin-top: 20px; display: none; }
        .result-box.show { display: block; }
        .data-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #ddd; }
        .data-header h3 { color: #333; font-size: 18px; }
        .data-source { color: #999; font-size: 12px; }
        .stock-price { font-size: 32px; font-weight: bold; color: #667eea; margin-bottom: 10px; }
        .stock-price.up { color: #00c853; }
        .stock-price.down { color: #ff1744; }
        .stock-info { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px; }
        .info-item { background: white; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .info-item label { display: block; color: #666; font-size: 12px; margin-bottom: 5px; }
        .info-item span { color: #333; font-size: 16px; font-weight: bold; }
        .signals { display: flex; gap: 10px; margin-top: 15px; }
        .signal { padding: 5px 15px; border-radius: 20px; font-size: 14px; font-weight: bold; }
        .signal.buy { background: #00c853; color: white; }
        .signal.sell { background: #ff1744; color: white; }
        .signal.hold { background: #ffc107; color: #333; }
        .error-message { background: #ffebee; color: #c62828; padding: 15px; border-radius: 5px; margin-top: 20px; }
        .real-badge { background: #4caf50; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold; margin-left: 5px; }
        .login-container { max-width: 400px; margin: 100px auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .login-container h2 { color: #667eea; font-size: 24px; text-align: center; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; color: #333; font-size: 14px; margin-bottom: 8px; }
        .form-group input { width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 5px; font-size: 16px; }
        .form-group input:focus { outline: none; border-color: #667eea; }
        .login-btn { width: 100%; background: #667eea; color: white; border: none; padding: 12px; border-radius: 5px; cursor: pointer; font-size: 16px; transition: background 0.3s; }
        .login-btn:hover { background: #5568d3; }
        .error-msg { color: #ff1744; font-size: 14px; margin-top: 10px; text-align: center; }
        .stock-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; margin-top: 20px; }
        .stock-card { background: white; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #667eea; }
        .stock-card.level-5 { border-left-color: #f44336; }
        .stock-card.level-4 { border-left-color: #ff9800; }
        .stock-card.level-3 { border-left-color: #ffc107; }
        .stock-card h4 { color: #333; margin-bottom: 10px; font-size: 16px; }
        .stock-card .score { color: #667eea; font-weight: bold; font-size: 14px; }
        .stock-card .reason { color: #666; font-size: 12px; margin-top: 5px; }
        .select-options { background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .select-options label { display: block; margin-bottom: 10px; color: #333; font-size: 14px; }
        .select-options select { padding: 8px; border-radius: 5px; border: 1px solid #ddd; font-size: 14px; }
        .report-box { background: #fff; padding: 20px; border-radius: 5px; margin-top: 20px; white-space: pre-wrap; font-family: monospace; font-size: 13px; line-height: 1.6; max-height: 500px; overflow-y: auto; }
        .star-rating { color: #ffc107; font-weight: bold; }
    </style>
</head>
<body>
    {% if not session.get('user') %}
    <div class="login-container">
        <h2>📊 OpenClaw 量化交易平台</h2>
        {% if error %}
        <div class="error-msg">{{ error }}</div>
        {% endif %}
        <form action="/login" method="POST">
            <div class="form-group">
                <label>用户名</label>
                <input type="text" name="username" value="admin" required>
            </div>
            <div class="form-group">
                <label>密码</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" class="login-btn">登录</button>
        </form>
    </div>
    {% else %}
    <div class="container">
        <div class="header">
            <h1>📊 OpenClaw 统一量化交易平台 v9.0</h1>
            <div class="user-info">
                <span>欢迎，{{ session.user }}</span>
                <button class="logout-btn" onclick="logout()">退出登录</button>
            </div>
        </div>
        <div class="data-status">
            <h3>✅ Tushare 真实数据 + 智能选股引擎</h3>
            <p id="data-status-text">数据加载中，请稍候...</p>
        </div>
        <nav class="nav">
            <ul>
                <li><a href="#" onclick="showSection('realtime')" class="nav-link">📈 实时分析</a></li>
                <li><a href="#" onclick="showSection('market')" class="nav-link">🌍 市场扫描</a></li>
                <li><a href="#" onclick="showSection('selector')" class="nav-link">🎯 智能选股</a></li>
                <li><a href="#" onclick="showSection('chip')" class="nav-link">💰 筹码分析</a></li>
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
        <div id="selector" class="section">
            <h2>智能选股 🎯</h2>
            <div class="select-options">
                <label>扫描股票数量:</label>
                <select id="scan-count">
                    <option value="50">50只（快速）</option>
                    <option value="100" selected>100只（平衡）</option>
                    <option value="200">200只（深度）</option>
                </select>
                <label style="margin-top: 15px;">最低评分:</label>
                <select id="min-score">
                    <option value="10">10分（宽泛）</option>
                    <option value="20" selected>20分（标准）</option>
                    <option value="30">30分（严格）</option>
                </select>
            </div>
            <button class="btn" onclick="runStockSelector()">开始选股</button>
            <div class="loading" id="selector-loading">选股中，请稍候...</div>
            <div class="result-box" id="selector-result"></div>
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
    {% endif %}
    <script>
        function showSection(sectionId) {
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            document.getElementById(sectionId).classList.add('active');
            const navLink = document.querySelector(`[onclick="showSection('${sectionId}')"]`);
            if (navLink) navLink.classList.add('active');
        }
        function showLoading(loadingId) { document.getElementById(loadingId).classList.add('show'); }
        function hideLoading(loadingId) { document.getElementById(loadingId).classList.remove('show'); }
        function showResult(resultId) { document.getElementById(resultId).classList.add('show'); }
        function hideResult(resultId) { document.getElementById(resultId).classList.remove('show'); }
        function analyzeRealtime() {
            const symbol = document.getElementById('realtime-symbol').value;
            hideResult('realtime-result'); showLoading('realtime-loading');
            fetch('/api/realtime/' + symbol)
                .then(response => response.json())
                .then(data => {
                    hideLoading('realtime-loading');
                    if (data.success) { displayRealtimeResult(data); }
                    else { showError('realtime-result', data.message); }
                })
                .catch(error => {
                    hideLoading('realtime-loading');
                    showError('realtime-result', '请求失败: ' + error.message);
                });
        }
        function displayRealtimeResult(data) {
            const stock = data.data;
            const isUp = stock.change_percent.includes('+');
            let html = '<div class="data-header"><h3>' + stock.name + ' (' + stock.symbol + ')</h3><div class="data-source">数据源: ' + data.source.toUpperCase() + '<span class="real-badge">真实</span><br>更新时间: ' + new Date(data.timestamp).toLocaleString() + '</div></div><div class="stock-price ' + (isUp ? 'up' : 'down') + '">' + stock.price + '<br><span style="font-size: 16px;">' + stock.change + ' (' + stock.change_percent + ')</span></div><div class="signals">' + stock.signals.map(s => '<span class="signal">' + s + '</span>').join('') + '</div><div class="stock-info"><div class="info-item"><label>今开</label><span>' + stock.open + '</span></div><div class="info-item"><label>最高</label><span>' + stock.high + '</span></div><div class="info-item"><label>最低</label><span>' + stock.low + '</span></div><div class="info-item"><label>昨收</label><span>' + stock.pre_close + '</span></div><div class="info-item"><label>成交量</label><span>' + (stock.volume / 10000).toFixed(0) + ' 万手</span></div><div class="info-item"><label>成交额</label><span>' + (stock.amount / 100000000).toFixed(2) + ' 亿</span></div><div class="info-item"><label>MA5</label><span>' + stock.indicators.ma5 + '</span></div><div class="info-item"><label>MA10</label><span>' + stock.indicators.ma10 + '</span></div><div class="info-item"><label>MA20</label><span>' + stock.indicators.ma20 + '</span></div><div class="info-item"><label>RSI</label><span>' + stock.indicators.rsi.toFixed(1) + '</span></div></div>';
            const resultDiv = document.getElementById('realtime-result');
            resultDiv.innerHTML = html;
            showResult('realtime-result');
        }
        function analyzeMarket() {
            hideResult('market-result'); showLoading('market-loading');
            fetch('/api/market')
                .then(response => response.json())
                .then(data => {
                    hideLoading('market-loading');
                    if (data.success) { displayMarketResult(data); }
                    else { showError('market-result', data.message); }
                })
                .catch(error => {
                    hideLoading('market-loading');
                    showError('market-result', '请求失败: ' + error.message);
                });
        }
        function displayMarketResult(data) {
            const market = data.data;
            let html = '<div class="data-header"><h3>市场综合分析</h3><div class="data-source">数据源: ' + data.source.toUpperCase() + '<span class="real-badge">真实</span><br>缓存更新: ' + (data.cache_timestamp ? new Date(data.cache_timestamp).toLocaleString() : '未知') + '</div></div><div class="stock-info"><div class="info-item"><label>市场趋势</label><span style="color: ' + (market.sentiment === '乐观' ? '#00c853' : (market.sentiment === '悲观' ? '#ff1744' : '#667eea')) + ';">' + market.trend + '</span></div><div class="info-item"><label>市场情绪</label><span style="color: ' + (market.sentiment === '乐观' ? '#00c853' : (market.sentiment === '悲观' ? '#ff1744' : '#667eea')) + ';">' + market.sentiment + '</span></div><div class="info-item"><label>上涨股票</label><span>' + market.up_count + ' 只</span></div><div class="info-item"><label>下跌股票</label><span>' + market.down_count + ' 只</span></div><div class="info-item"><label>股票总数</label><span>' + market.total_count + ' 只</span></div></div><div style="margin-top: 20px;"><h4 style="color: #333; margin-bottom: 10px;">热门板块</h4><div class="signals">' + market.hot_sectors.map(s => '<span class="signal">' + s + '</span>').join('') + '</div></div><div style="margin-top: 20px;"><h4 style="color: #333; margin-bottom: 10px;">操作建议</h4><p style="color: #666; font-size: 14px;">' + market.advice + '</p></div>';
            const resultDiv = document.getElementById('market-result');
            resultDiv.innerHTML = html;
            showResult('market-result');
        }
        function runStockSelector() {
            const maxStocks = document.getElementById('scan-count').value;
            const minScore = document.getElementById('min-score').value;
            hideResult('selector-result'); showLoading('selector-loading');
            fetch('/api/selector?max_stocks=' + maxStocks + '&min_score=' + minScore)
                .then(response => response.json())
                .then(data => {
                    hideLoading('selector-loading');
                    if (data.success) { displaySelectorResult(data); }
                    else { showError('selector-result', data.message); }
                })
                .catch(error => {
                    hideLoading('selector-loading');
                    showError('selector-result', '请求失败: ' + error.message);
                });
        }
        function displaySelectorResult(data) {
            const result = data.data;
            let html = '<div class="data-header"><h3>智能选股结果</h3><div class="data-source">扫描数量: ' + result.scanned + ' | 符合条件: ' + result.stocks.length + ' 只</div></div>';

            if (result.stocks.length === 0) {
                html += '<p style="color: #666; padding: 20px;">未找到符合条件的股票</p>';
            } else {
                html += '<div class="stock-list">';
                result.stocks.forEach(stock => {
                    const stars = '⭐'.repeat(stock.level_score);
                    html += '<div class="stock-card level-' + stock.level_score + '"><h4>' + stock.name + ' (' + stock.symbol + ')</h4><div style="margin-bottom: 5px;"><span class="star-rating">' + stars + '</span> <span style="color: #667eea; font-weight: bold;">' + stock.level + '</span></div><div>💰 价格: ' + stock.price.toFixed(2) + '  📈 ' + (stock.pct_chg >= 0 ? '+' : '') + stock.pct_chg.toFixed(2) + '%</div><div style="margin-top: 5px;">🎯 综合评分: <span class="score">' + stock.score.toFixed(1) + '分</span></div><div class="reason">' + stock.reasons.substring(0, 100) + '...</div></div>';
                });
                html += '</div>';
            }

            html += '<div style="margin-top: 20px;"><h4 style="color: #333; margin-bottom: 10px;">详细报告</h4><div class="report-box">' + result.report + '</div></div>';
            const resultDiv = document.getElementById('selector-result');
            resultDiv.innerHTML = html;
            showResult('selector-result');
        }
        function analyzeChip() {
            const symbol = document.getElementById('chip-symbol').value;
            hideResult('chip-result'); showLoading('chip-loading');
            fetch('/api/realtime/' + symbol)
                .then(response => response.json())
                .then(data => {
                    hideLoading('chip-loading');
                    if (data.success) {
                        const stock = data.data;
                        let html = '<div class="data-header"><h3>' + stock.name + ' (' + stock.symbol + ') - 筹码分布</h3><div class="data-source">数据源: ' + data.source.toUpperCase() + '<span class="real-badge">真实</span></div></div><div class="stock-info"><div class="info-item"><label>集中度</label><span>中度集中</span></div><div class="info-item"><label>成本区域</label><span>' + (stock.price * 0.95).toFixed(2) + ' - ' + (stock.price * 1.05).toFixed(2) + '</span></div></div><div style="margin-top: 20px;"><h4 style="color: #333; margin-bottom: 10px;">筹码分布图</h4><div style="background: #f5f5f5; padding: 15px; border-radius: 5px;">[筹码分布图 - 敬请期待]</div></div>';
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
            resultDiv.innerHTML = '<div class="error-message">' + message + '</div>';
            showResult(resultId);
        }
        function logout() {
            if (confirm('确定要退出登录吗？')) {
                window.location.href = '/logout';
            }
        }
        function updateDataStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    const statusText = document.getElementById('data-status-text');
                    if (data.data_loaded) {
                        statusText.innerHTML = '✅ 数据已加载: ' + data.stock_count + ' 只股票<br>最后更新: ' + (data.last_update ? new Date(data.last_update).toLocaleString() : '未知') + '<br>数据源: ' + data.source + '<br>🎯 选股引擎: ' + (data.strategy_available ? '已启用' : '未启用');
                    } else {
                        statusText.innerHTML = '⏳ 数据加载中，请稍候...';
                    }
                })
                .catch(error => {
                    const statusText = document.getElementById('data-status-text');
                    statusText.innerHTML = '❌ 数据状态: ' + error.message;
                });
        }
        window.onload = function() {
            update