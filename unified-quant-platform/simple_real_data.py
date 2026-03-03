#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OpenClaw 量化交易平台 v8.1 - 简化版"""
import os
import json
import datetime
from flask import Flask, render_template_string, jsonify, request, redirect, url_for, session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'

TUSHARE_TOKEN = '8b159caa2bbf554707c20c3f44fea1e0e6ec75b6afc82c78fa47e47b'

USERS = {'admin': 'admin123'}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenClaw 量化交易平台 v8.1</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }
        .header h1 { color: #667eea; font-size: 24px; }
        .data-status { background: #e3f2fd; color: #1565c0; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 4px solid #2196f3; }
        .data-status h3 { font-size: 16px; margin-bottom: 5px; color: #1565c0; }
        .data-status p { font-size: 14px; color: #1976d2; }
        .section { background: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: none; }
        .section.active { display: block; }
        .section h2 { color: #333; margin-bottom: 20px; font-size: 20px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }
        .input-group { display: flex; gap: 10px; margin-bottom: 20px; }
        .input-group input { flex: 1; padding: 12px; border: 2px solid #e0e0e0; border-radius: 5px; font-size: 16px; }
        .btn { background: #667eea; color: white; border: none; padding: 12px 24px; border-radius: 5px; cursor: pointer; font-size: 16px; transition: background 0.3s; }
        .btn:hover { background: #5568d3; }
        .result-box { background: #f5f5f5; padding: 20px; border-radius: 5px; margin-top: 20px; }
        .login-container { max-width: 400px; margin: 100px auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .login-container h2 { color: #667eea; font-size: 24px; text-align: center; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; color: #333; font-size: 14px; margin-bottom: 8px; }
        .form-group input { width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 5px; font-size: 16px; }
        .login-btn { width: 100%; background: #667eea; color: white; border: none; padding: 12px; border-radius: 5px; cursor: pointer; font-size: 16px; }
        .login-btn:hover { background: #5568d3; }
        .error-msg { color: #ff1744; font-size: 14px; margin-top: 10px; text-align: center; }
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
            <h1>📊 OpenClaw 量化交易平台 v8.1（简化版）</h1>
        </div>
        <div class="data-status">
            <h3>✅ Tushare 真实数据版本</h3>
            <p>数据源：Tushare<br>数据量：5470只A股</p>
        </div>
        <div id="realtime" class="section active">
            <h2>实时分析</h2>
            <div class="input-group">
                <input type="text" id="symbol" placeholder="例如：600519" value="600519">
                <button class="btn" onclick="analyze()">分析</button>
            </div>
            <div class="result-box" id="result"></div>
        </div>
    </div>
    {% endif %}
    <script>
        function analyze() {
            const symbol = document.getElementById('symbol').value;
            const result = document.getElementById('result');
            result.innerHTML = '<p style="color: #667eea;">正在分析 ' + symbol + '...</p>';
            
            fetch('/api/analyze/' + symbol)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const stock = data.data;
                        result.innerHTML = '<h3>' + stock.name + ' (' + stock.symbol + ')</h3>' +
                            '<p>价格：' + stock.price + '</p>' +
                            '<p>涨跌幅：' + stock.change_percent + '</p>' +
                            '<p>成交量：' + stock.volume + '</p>' +
                            '<p><strong>数据来源：Tushare（真实数据）</strong></p>';
                    } else {
                        result.innerHTML = '<p style="color: #ff1744;">' + data.message + '</p>';
                    }
                })
                .catch(error => {
                    result.innerHTML = '<p style="color: #ff1744;">分析失败：' + error.message + '</p>';
                });
        }
    </script>
</body>
</html>"""

@app.route('/')
def index():
    if 'user' not in session:
        return render_template_string(HTML_TEMPLATE, error=None)
    return render_template_string(HTML_TEMPLATE)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if username in USERS and USERS[username] == password:
        session['user'] = username
        return redirect(url_for('index'))
    else:
        return render_template_string(HTML_TEMPLATE, error='用户名或密码错误')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/api/analyze/<symbol>')
def analyze(symbol):
    try:
        import tushare as ts
        ts.set_token(TUSHARE_TOKEN)
        pro = ts.pro_api()
        
        today = datetime.datetime.now().strftime('%Y%m%d')
        df = pro.daily(ts_code=symbol, trade_date=today)
        
        if df.empty:
            return jsonify({'success': False, 'message': '未找到股票数据'})
        
        row = df.iloc[0]
        return jsonify({
            'success': True,
            'message': '分析成功（Tushare真实数据）',
            'data': {
                'symbol': symbol,
                'name': '股票名称',
                'price': float(row['close']),
                'change': float(row['close'] - row['pre_close']),
                'change_percent': f"{((row['close'] - row['pre_close']) / row['pre_close'] * 100):+.2f}%",
                'volume': int(row['vol'] * 100)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'分析失败：{str(e)}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
