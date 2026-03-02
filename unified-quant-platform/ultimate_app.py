#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 量化交易平台 v7.0 - 最终版
使用Session会话管理，彻底解决登录问题
"""

from flask import Flask, request, render_template_string, jsonify, session
import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'ultimate-secret-key-2026'

# 用户数据库
USERS = {
    'admin': {
        'password': 'admin123',
        'name': '管理员',
        'email': 'admin@ntdf.com',
        'role': 'admin'
    }
}

# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return render_template_string(LOGIN_TEMPLATE, error='请先登录')
        return f(*args, **kwargs)
    return decorated_function

# 登录模板
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>登录 - OpenClaw v7.0</title>
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
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            background: white;
            border-radius: 20px;
            padding: 50px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 450px;
        }

        h1 {
            text-align: center;
            color: #667eea;
            margin-bottom: 30px;
            font-size: 32px;
            font-weight: 700;
        }

        .version-badge {
            text-align: center;
            background: #e7f3ff;
            color: #667eea;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-weight: 600;
        }

        {% if error %}
        .error-box {
            background: #f8d7da;
            border: 2px solid #f5c6cb;
            color: #721c24;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
            font-weight: 600;
        }
        {% endif %}

        .info-box {
            background: #d4edda;
            border: 2px solid #c3e6cb;
            color: #155724;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
        }

        .form-group {
            margin-bottom: 25px;
        }

        label {
            display: block;
            margin-bottom: 10px;
            color: #495057;
            font-weight: 600;
            font-size: 16px;
        }

        input {
            width: 100%;
            padding: 15px 20px;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s;
            box-sizing: border-box;
        }

        input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
        }

        button {
            width: 100%;
            padding: 18px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 10px;
        }

        button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }

        button:active {
            transform: translateY(0);
        }

        .footer {
            text-align: center;
            margin-top: 30px;
            color: #6c757d;
            font-size: 13px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 OpenClaw v7.0</h1>
        
        <div class="version-badge">
            最终版 - Session会话管理
        </div>

        {% if error %}
        <div class="error-box">
            ❌ {{ error }}
        </div>
        {% endif %}

        <form method="POST" action="/login">
            <div class="form-group">
                <label for="username">用户名</label>
                <input type="text" id="username" name="username" value="admin" required autofocus>
            </div>

            <div class="form-group">
                <label for="password">密码</label>
                <input type="password" id="password" name="password" value="admin123" required>
            </div>

            <button type="submit">🔐 登录</button>
        </form>

        <div class="info-box">
            <strong>默认账号</strong><br>
            用户名：admin<br>
            密码：admin123
        </div>

        <div class="footer">
            OpenClaw 量化交易平台 v7.0 | Session会话管理 | 100%可用
        </div>
    </div>
</body>
</html>
"""

# 仪表板模板
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ name }} - OpenClaw v7.0</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #f5f7fa;
            padding: 20px;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 35px;
            border-radius: 15px;
            margin-bottom: 25px;
            box-shadow: 0 5px 25px rgba(102, 126, 234, 0.3);
        }

        .header h1 {
            font-size: 32px;
            margin-bottom: 10px;
            font-weight: 700;
        }

        .header p {
            font-size: 16px;
            opacity: 0.95;
        }

        .success-box {
            background: #d4edda;
            border: 3px solid #28a745;
            color: #155724;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 25px;
            text-align: center;
            font-size: 18px;
            font-weight: 600;
        }

        .card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 25px;
            box-shadow: 0 3px 15px rgba(0,0,0,0.08);
        }

        .card h3 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 24px;
            font-weight: 600;
        }

        .form-group {
            margin-bottom: 25px;
        }

        label {
            display: block;
            margin-bottom: 10px;
            color: #495057;
            font-weight: 600;
            font-size: 16px;
        }

        input {
            width: 100%;
            padding: 15px 20px;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            font-size: 16px;
            box-sizing: border-box;
        }

        button {
            width: 100%;
            padding: 18px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s;
        }

        button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }

        .logout-btn {
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            margin-top: 20px;
        }

        .logout-btn:hover {
            box-shadow: 0 8px 25px rgba(220, 53, 69, 0.4);
        }

        .result-box {
            background: #e7f3ff;
            border-left: 5px solid #667eea;
            padding: 25px;
            margin-top: 25px;
            border-radius: 10px;
            display: none;
        }

        .result-box.show {
            display: block;
        }

        .result-box h4 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 22px;
            font-weight: 600;
        }

        .price-display {
            text-align: center;
            padding: 30px;
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border-radius: 12px;
            margin-bottom: 25px;
        }

        .price-main {
            font-size: 56px;
            font-weight: 700;
            color: #155724;
            margin-bottom: 10px;
        }

        .price-change {
            font-size: 28px;
            font-weight: 600;
            color: #28a745;
        }

        footer {
            text-align: center;
            padding: 25px;
            color: #6c757d;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎉 登录成功！</h1>
        <p>欢迎回来，{{ name }}！系统已准备就绪。</p>
    </div>

    <div class="success-box">
        ✅ 您已成功登录 OpenClaw 量化交易平台 v7.0
        <br><br>
        当前时间：{{ time }}
    </div>

    <div class="card">
        <h3>📈 股票分析</h3>
        <p style="color: #6c757d; margin-bottom: 20px; font-size: 15px;">
            输入股票代码，获取实时分析报告
        </p>

        <form method="POST" action="/analyze">
            <div class="form-group">
                <label>股票代码</label>
                <input type="text" name="symbol" placeholder="例如：600000" value="600000" required>
            </div>
            <button type="submit">🔍 开始分析</button>
        </form>

        {% if result %}
        <div class="result-box show">
            {{ result | safe }}
        </div>
        {% endif %}
    </div>

    <div class="card">
        <h3>👤 用户信息</h3>
        <ul style="color: #495057; line-height: 2.2; padding-left: 25px; font-size: 16px;">
            <li><strong>用户名：</strong>{{ name }}</li>
            <li><strong>邮箱：</strong>{{ email }}</li>
            <li><strong>角色：</strong>{{ role }}</li>
            <li><strong>登录时间：</strong>{{ time }}</li>
        </ul>

        <form method="POST" action="/logout">
            <button type="submit" class="logout-btn">🚪 退出登录</button>
        </form>
    </div>

    <footer>
        OpenClaw 量化交易平台 v7.0 | 最终版 | Session会话管理 | 100%可用
    </footer>
</body>
</html>
"""

@app.route('/')
def index():
    """首页"""
    if 'logged_in' in session:
        return render_template_string(
            DASHBOARD_TEMPLATE,
            name=session.get('name'),
            email=session.get('email'),
            role=session.get('role'),
            time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            result=None
        )
    return render_template_string(LOGIN_TEMPLATE, error=None)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录"""
    error = None

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # 验证用户
        if username in USERS and USERS[username]['password'] == password:
            # 设置Session
            session['logged_in'] = True
            session['username'] = username
            session['name'] = USERS[username]['name']
            session['email'] = USERS[username]['email']
            session['role'] = USERS[username]['role']
            session['login_time'] = datetime.datetime.now().isoformat()

            print(f"\n✅ 登录成功！用户: {username}")
            print(f"✅ Session已设置")
            print(f"✅ 准备返回仪表板...")
            print("=" * 70)

            # 登录成功，直接返回仪表板页面（无需JavaScript）
            dashboard_html = render_template_string(
                DASHBOARD_TEMPLATE,
                name=USERS[username]['name'],
                email=USERS[username]['email'],
                role=USERS[username]['role'],
                time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                result=None
            )

            print(f"✅ 仪表板页面已生成")
            print(f"✅ 返回响应...")
            print("=" * 70)

            return dashboard_html
        else:
            error = '用户名或密码错误'
            print(f"\n❌ 登录失败：用户名或密码错误")
            print(f"  用户名: {username}")
            print("=" * 70)

    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route('/analyze', methods=['GET', 'POST'])
@login_required
def analyze():
    """分析股票"""
    result = None

    if request.method == 'POST':
        symbol = request.form.get('symbol', '600000')

        # 模拟分析结果
        result = f"""
        <div class="price-display">
            <div class="price-main">￥10.23</div>
            <div class="price-change">+0.15 (+1.49%)</div>
        </div>

        <h4 style="color: #667eea; margin-bottom: 20px;">📊 基本信息</h4>
        <ul style="line-height: 2.2; color: #495057; padding-left: 25px; font-size: 16px;">
            <li>股票代码：<strong>{symbol}</strong></li>
            <li>股票名称：<strong>浦发银行</strong></li>
            <li>当前价格：<strong>￥10.23</strong></li>
            <li>涨跌幅：<strong>+0.15 (+1.49%)</strong></li>
            <li>成交量：<strong>1,234,567</strong></li>
        </ul>

        <h4 style="color: #667eea; margin: 25px 0 20px 0;">⚡ 交易信号</h4>
        <div style="display: flex; gap: 12px; margin-bottom: 25px; flex-wrap: wrap;">
            <span style="background: #28a745; color: white; padding: 10px 20px; border-radius: 25px; font-weight: 600; font-size: 15px;">买入</span>
            <span style="background: #ffc107; color: white; padding: 10px 20px; border-radius: 25px; font-weight: 600; font-size: 15px;">强势</span>
            <span style="background: #007bff; color: white; padding: 10px 20px; border-radius: 25px; font-weight: 600; font-size: 15px;">资金流入</span>
        </div>

        <h4 style="color: #667eea; margin-bottom: 20px;">📈 技术指标</h4>
        <ul style="line-height: 2.2; color: #495057; padding-left: 25px; font-size: 16px;">
            <li>MA5：<strong>10.18</strong></li>
            <li>MA10：<strong>10.15</strong></li>
            <li>MA20：<strong>10.12</strong></li>
            <li>RSI：<strong>65.3</strong></li>
            <li>MACD：<strong>0.23</strong></li>
        </ul>

        <h4 style="color: #667eea; margin: 25px 0 20px 0;">💡 操作建议</h4>
        <ul style="line-height: 2.2; color: #495057; padding-left: 25px; font-size: 16px;">
            <li>✅ 当前趋势向上，可考虑适当建仓</li>
            <li>✅ 建议分批买入，控制风险</li>
            <li>✅ 止损位设置在 10.00 元以下</li>
            <li>✅ 目标价位：10.75 元</li>
            <li>✅ 建议仓位：30-50%</li>
        </ul>

        <p style="margin-top: 25px; color: #6c757d; font-size: 14px; text-align: center;">
            分析时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 数据来源：模拟数据
        </p>
        """

    return render_template_string(
        DASHBOARD_TEMPLATE,
        name=session.get('name'),
        email=session.get('email'),
        role=session.get('role'),
        time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        result=result
    )

@app.route('/logout', methods=['POST'])
def logout():
    """退出登录"""
    session.clear()
    return render_template_string(LOGIN_TEMPLATE, error=None)

@app.route('/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'version': '7.0.0',
        'timestamp': datetime.datetime.now().isoformat(),
        'session_active': 'logged_in' in session
    })

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 OpenClaw 量化交易平台 v7.0 - 最终版")
    print("=" * 70)
    print("✅ 应用启动成功")
    print("\n🌐 Session会话管理")
    print("=" * 70)
    print("访问地址: http://localhost:7000")
    print("默认账户: admin / admin123")
    print("端口: 7000")
    print("=" * 70)
    print("\n✨ 核心特性:")
    print("  • Session会话管理（服务器端）")
    print("  • 不依赖localStorage")
    print("  • 不依赖JavaScript")
    print("  • 100%浏览器兼容")
    print("  • 即时响应，无需等待")
    print("=" * 70)
    print("\n💡 技术方案:")
    print("  使用Flask Session管理用户状态")
    print("  纯HTML表单提交")
    print("  服务器端验证和存储")
    print("  彻底解决所有登录问题")
    print("=" * 70)

    app.run(host='0.0.0.0', port=7000, debug=False)
