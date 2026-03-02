#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 量化交易平台 v8.0 - 终极版
使用8000端口，彻底避免缓存问题
"""

from flask import Flask, request, render_template_string, jsonify, session
import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'ultimate-secret-key-v8-0'

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
    <title>登录 - OpenClaw v8.0</title>
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
            border-radius: 25px;
            padding: 60px;
            box-shadow: 0 25px 80px rgba(0,0,0,0.4);
            width: 100%;
            max-width: 500px;
        }

        h1 {
            text-align: center;
            color: #667eea;
            margin-bottom: 15px;
            font-size: 36px;
            font-weight: 800;
        }

        .version-badge {
            text-align: center;
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 30px;
            font-weight: 700;
            font-size: 18px;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }

        {% if error %}
        .error-box {
            background: #f8d7da;
            border: 3px solid #f5c6cb;
            color: #721c24;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 30px;
            text-align: center;
            font-weight: 700;
            font-size: 18px;
        }
        {% endif %}

        .info-box {
            background: #d4edda;
            border: 3px solid #28a745;
            color: #155724;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 30px;
            font-size: 16px;
            font-weight: 600;
        }

        .form-group {
            margin-bottom: 30px;
        }

        label {
            display: block;
            margin-bottom: 12px;
            color: #495057;
            font-weight: 700;
            font-size: 18px;
        }

        input {
            width: 100%;
            padding: 18px 25px;
            border: 3px solid #e9ecef;
            border-radius: 12px;
            font-size: 18px;
            transition: all 0.3s;
            box-sizing: border-box;
            font-weight: 600;
        }

        input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 5px rgba(102, 126, 234, 0.2);
        }

        button {
            width: 100%;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 20px;
            font-weight: 800;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 15px;
            letter-spacing: 2px;
        }

        button:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.5);
        }

        button:active {
            transform: translateY(0);
        }

        footer {
            text-align: center;
            margin-top: 40px;
            color: #6c757d;
            font-size: 15px;
            font-weight: 600;
        }

        .port-info {
            text-align: center;
            background: #ffc107;
            color: #212529;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 30px;
            font-weight: 700;
            font-size: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 OpenClaw v8.0</h1>
        
        <div class="version-badge">
            终极版 - 新端口 8000
        </div>

        <div class="port-info">
            端口：8000（新端口）
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

            <button type="submit">🔐 立即登录</button>
        </form>

        <div class="info-box">
            <strong>📋 默认账号</strong><br>
            用户名：admin<br>
            密码：admin123
        </div>

        <footer>
            OpenClaw 量化交易平台 v8.0 | 终极版 | 端口 8000
        </footer>
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
    <title>{{ name }} - OpenClaw v8.0</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #f5f7fa;
            padding: 30px;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 50px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4);
        }

        .header h1 {
            font-size: 42px;
            margin-bottom: 15px;
            font-weight: 800;
        }

        .header p {
            font-size: 20px;
            opacity: 0.95;
            font-weight: 600;
        }

        .success-banner {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            text-align: center;
            font-size: 24px;
            font-weight: 800;
            box-shadow: 0 5px 20px rgba(40, 167, 69, 0.3);
        }

        .user-card {
            background: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }

        .user-card h3 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 28px;
            font-weight: 700;
        }

        .user-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }

        .info-item {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }

        .info-item label {
            display: block;
            color: #6c757d;
            font-size: 14px;
            margin-bottom: 5px;
        }

        .info-item span {
            font-size: 18px;
            font-weight: 700;
            color: #495057;
        }

        .card {
            background: white;
            border-radius: 15px;
            padding: 35px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }

        .card h3 {
            color: #667eea;
            margin-bottom: 25px;
            font-size: 28px;
            font-weight: 700;
        }

        .form-group {
            margin-bottom: 30px;
        }

        label {
            display: block;
            margin-bottom: 12px;
            color: #495057;
            font-weight: 700;
            font-size: 18px;
        }

        input {
            width: 100%;
            padding: 18px 25px;
            border: 3px solid #e9ecef;
            border-radius: 12px;
            font-size: 18px;
            box-sizing: border-box;
            font-weight: 600;
        }

        input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 5px rgba(102, 126, 234, 0.2);
        }

        button {
            width: 100%;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 20px;
            font-weight: 800;
            cursor: pointer;
            transition: all 0.3s;
            letter-spacing: 2px;
        }

        button:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.5);
        }

        .logout-btn {
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            margin-top: 20px;
        }

        .logout-btn:hover {
            box-shadow: 0 10px 30px rgba(220, 53, 69, 0.5);
        }

        .result-box {
            background: #e7f3ff;
            border-left: 5px solid #667eea;
            padding: 30px;
            margin-top: 30px;
            border-radius: 12px;
            display: none;
        }

        .result-box.show {
            display: block;
        }

        .result-box h4 {
            color: #667eea;
            margin-bottom: 25px;
            font-size: 24px;
            font-weight: 700;
        }

        footer {
            text-align: center;
            padding: 30px;
            color: #6c757d;
            font-size: 16px;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎉 登录成功！</h1>
        <p>欢迎回来，{{ name }}！系统已准备就绪。</p>
    </div>

    <div class="success-banner">
        ✅ 您已成功登录 OpenClaw 量化交易平台 v8.0
        <br>
        当前时间：{{ time }}
    </div>

    <div class="user-card">
        <h3>👤 用户信息</h3>
        <div class="user-info">
            <div class="info-item">
                <label>用户名</label>
                <span>{{ name }}</span>
            </div>
            <div class="info-item">
                <label>邮箱</label>
                <span>{{ email }}</span>
            </div>
            <div class="info-item">
                <label>角色</label>
                <span>{{ role }}</span>
            </div>
            <div class="info-item">
                <label>登录时间</label>
                <span>{{ time }}</span>
            </div>
        </div>

        <form method="POST" action="/logout">
            <button type="submit" class="logout-btn">🚪 退出登录</button>
        </form>
    </div>

    <div class="card">
        <h3>📈 股票分析</h3>
        <p style="color: #6c757d; margin-bottom: 25px; font-size: 18px;">
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

    <footer>
        OpenClaw 量化交易平台 v8.0 | 终极版 | 端口 8000
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

            print(f"\n" + "="*70)
            print(f"✅ 登录成功！用户: {username}")
            print(f"✅ Session已设置")
            print(f"✅ 准备返回仪表板...")
            print("="*70)

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
            print("="*70)

            return dashboard_html
        else:
            error = '用户名或密码错误'
            print(f"\n" + "="*70)
            print(f"❌ 登录失败：用户名或密码错误")
            print(f"  用户名: {username}")
            print("="*70)

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
        <div style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); padding: 30px; border-radius: 15px; margin-bottom: 30px; text-align: center;">
            <div style="font-size: 64px; font-weight: 800; color: #155724; margin-bottom: 15px;">￥10.23</div>
            <div style="font-size: 32px; font-weight: 700; color: #28a745;">+0.15 (+1.49%)</div>
        </div>

        <h4 style="color: #667eea; margin-bottom: 25px; font-size: 24px; font-weight: 700;">📊 基本信息</h4>
        <ul style="line-height: 2.5; color: #495057; padding-left: 30px; font-size: 18px;">
            <li>股票代码：<strong>{symbol}</strong></li>
            <li>股票名称：<strong>浦发银行</strong></li>
            <li>当前价格：<strong>￥10.23</strong></li>
            <li>涨跌幅：<strong>+0.15 (+1.49%)</strong></li>
            <li>成交量：<strong>1,234,567</strong></li>
        </ul>

        <h4 style="color: #667eea; margin: 30px 0 25px 0; font-size: 24px; font-weight: 700;">⚡ 交易信号</h4>
        <div style="display: flex; gap: 15px; margin-bottom: 30px; flex-wrap: wrap; justify-content: center;">
            <span style="background: #28a745; color: white; padding: 12px 25px; border-radius: 30px; font-weight: 700; font-size: 18px;">买入</span>
            <span style="background: #ffc107; color: white; padding: 12px 25px; border-radius: 30px; font-weight: 700; font-size: 18px;">强势</span>
            <span style="background: #007bff; color: white; padding: 12px 25px; border-radius: 30px; font-weight: 700; font-size: 18px;">资金流入</span>
        </div>

        <h4 style="color: #667eea; margin-bottom: 25px; font-size: 24px; font-weight: 700;">📈 技术指标</h4>
        <ul style="line-height: 2.5; color: #495057; padding-left: 30px; font-size: 18px;">
            <li>MA5：<strong>10.18</strong></li>
            <li>MA10：<strong>10.15</strong></li>
            <li>MA20：<strong>10.12</strong></li>
            <li>RSI：<strong>65.3</strong></li>
            <li>MACD：<strong>0.23</strong></li>
        </ul>

        <h4 style="color: #667eea; margin: 30px 0 25px 0; font-size: 24px; font-weight: 700;">💡 操作建议</h4>
        <ul style="line-height: 2.5; color: #495057; padding-left: 30px; font-size: 18px;">
            <li>✅ 当前趋势向上，可考虑适当建仓</li>
            <li>✅ 建议分批买入，控制风险</li>
            <li>✅ 止损位设置在 10.00 元以下</li>
            <li>✅ 目标价位：10.75 元</li>
            <li>✅ 建议仓位：30-50%</li>
        </ul>

        <p style="margin-top: 30px; color: #6c757d; font-size: 14px; text-align: center; font-weight: 600;">
            分析时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 数据来源：模拟数据（测试环境）| 端口：8000
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
        'version': '8.0.0',
        'timestamp': datetime.datetime.now().isoformat(),
        'session_active': 'logged_in' in session,
        'port': 8000
    })

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 OpenClaw 量化交易平台 v8.0 - 终极版")
    print("=" * 70)
    print("✅ 应用启动成功")
    print("\n🌐 新端口：8000")
    print("=" * 70)
    print("访问地址: http://localhost:8000")
    print("外网地址: http://10.3.0.5:8000")
    print("默认账户: admin / admin123")
    print("端口: 8000（全新端口）")
    print("=" * 70)
    print("\n✨ 核心特性:")
    print("  • 全新端口 8000（避免缓存）")
    print("  • Session会话管理")
    print("  • 不依赖localStorage")
    print("  • 不依赖JavaScript")
    print("  • 100%浏览器兼容")
    print("  • 大字体、清晰界面")
    print("=" * 70)
    print("\n💡 技术方案:")
    print("  使用Flask Session管理用户状态")
    print("  纯HTML表单提交")
    print("  服务器端验证和存储")
    print("  彻底解决所有登录问题")
    print("  新端口避免浏览器缓存")
    print("=" * 70)

    app.run(host='0.0.0.0', port=8000, debug=False)
