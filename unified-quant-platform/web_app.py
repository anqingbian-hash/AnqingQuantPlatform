#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 统一量化交易平台 v5.0 - 网页版
完整的前端界面
"""

import os
import sys
import datetime

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from flask import Flask, render_template_string, jsonify, request, send_from_directory
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'

# HTML 模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenClaw 统一量化交易平台 v5.0</title>
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
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 32px;
            margin-bottom: 10px;
            font-weight: 700;
        }

        .header p {
            font-size: 16px;
            opacity: 0.9;
        }

        .nav {
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
        }

        .nav ul {
            display: flex;
            justify-content: center;
            list-style: none;
            gap: 30px;
            flex-wrap: wrap;
        }

        .nav a {
            color: #495057;
            text-decoration: none;
            font-weight: 600;
            padding: 10px 20px;
            border-radius: 8px;
            transition: all 0.3s;
            cursor: pointer;
        }

        .nav a:hover, .nav a.active {
            background: #667eea;
            color: white;
        }

        .main {
            padding: 30px;
        }

        .section {
            display: none;
        }

        .section.active {
            display: block;
        }

        .card {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }

        .card h3 {
            color: #495057;
            margin-bottom: 20px;
            font-size: 20px;
            font-weight: 600;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #495057;
            font-weight: 500;
        }

        .form-group input, .form-group select {
            width: 100%;
            padding: 12px;
            border: 1px solid #ced4da;
            border-radius: 8px;
            font-size: 14px;
            transition: all 0.3s;
        }

        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: inline-block;
            text-align: center;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }

        .btn-logout {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }

        .btn-logout:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(255, 107, 107, 0.4);
        }

        .result-box {
            background: #e7f3ff;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin-top: 20px;
            border-radius: 8px;
            display: none;
        }

        .result-box.show {
            display: block;
        }

        .result-box h4 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 16px;
        }

        .result-box pre {
            background: white;
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
            font-size: 13px;
            line-height: 1.6;
        }

        .status-badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            background: #28a745;
            color: white;
            margin-left: 10px;
        }

        .footer {
            text-align: center;
            padding: 20px;
            color: #6c757d;
            font-size: 14px;
            border-top: 1px solid #e9ecef;
            background: #f8f9fa;
        }

        .loading {
            text-align: center;
            padding: 20px;
            display: none;
        }

        .loading.show {
            display: block;
        }

        .loading::after {
            content: '...';
            animation: dots 1.5s steps(5, end) infinite;
        }

        @keyframes dots {
            0%, 20% { content: '.'; }
            40% { content: '..'; }
            60% { content: '...'; }
            80%, 100% { content: ''; }
        }

        .two-columns {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        @media (max-width: 768px) {
            .two-columns {
                grid-template-columns: 1fr;
            }

            .nav ul {
                flex-direction: column;
                align-items: center;
            }
        }

        .success {
            color: #28a745;
            font-weight: 600;
        }

        .error {
            color: #dc3545;
            font-weight: 600;
        }

        .info {
            color: #17a2b8;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 OpenClaw 统一量化交易平台 v5.0</h1>
            <p>AI 驱动的智能量化交易系统 | 测试环境 <span class="status-badge">运行中</span></p>
        </div>

        <div class="nav">
            <ul>
                <li><a href="#" onclick="showSection('home')" class="active">🏠 首页</a></li>
                <li><a href="#" onclick="showSection('login-section')" id="nav-login">🔐 登录</a></li>
                <li><a href="#" onclick="showSection('realtime')">📈 实时分析</a></li>
                <li><a href="#" onclick="showSection('chip')">💰 筹码分布</a></li>
                <li><a href="#" onclick="showSection('market')">📊 市场分析</a></li>
                <li><a href="#" onclick="showSection('export')">📥 导出功能</a></li>
                <li><a href="#" onclick="showSection('about')">ℹ️ 关于</a></li>
                <li><button id="logout-btn" class="btn-logout" style="display: none;" onclick="logout()">🚪 退出</button></li>
            </ul>
            <div id="user-info" style="text-align: center; margin-top: 10px; color: #667eea; font-weight: 600; display: none;"></div>
        </div>

        <div class="main">
            <!-- 首页 -->
            <div id="home" class="section active">
                <!-- 快速登录区域 -->
                <div class="card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                    <h3 style="color: white;">🔐 快速登录</h3>
                    <p style="color: rgba(255,255,255,0.9); margin-bottom: 20px;">如果您还没有登录，请在此快速登录系统</p>
                    <div class="two-columns" style="align-items: center;">
                        <div>
                            <h4 style="color: white; margin-bottom: 10px;">📋 默认账号</h4>
                            <ul style="color: rgba(255,255,255,0.9); line-height: 2;">
                                <li>👤 用户名：<strong>admin</strong></li>
                                <li>🔑 密码：<strong>admin123</strong></li>
                                <li>👑 角色：管理员</li>
                            </ul>
                        </div>
                        <div style="text-align: center;">
                            <button onclick="quickLogin()" style="background: white; color: #667eea; border: none; padding: 15px 40px; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; transition: all 0.3s;">
                                🚀 一键登录
                            </button>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h3>🎯 欢迎使用 OpenClaw 统一量化交易平台</h3>
                    <p style="color: #6c757d; margin-bottom: 20px;">这是一个基于 AI 的智能量化交易系统，提供实时分析、市场扫描、智能选股等功能。</p>
                    <div class="two-columns">
                        <div>
                            <h4 style="color: #495057; margin-bottom: 10px;">✨ 核心功能</h4>
                            <ul style="color: #6c757d; line-height: 2;">
                                <li>✅ 5个数据源实时数据</li>
                                <li>✅ NTDF 信号系统 v2</li>
                                <li>✅ 8因子量化信号</li>
                                <li>✅ AI 智能选股</li>
                                <li>✅ 实时市场监控</li>
                            </ul>
                        </div>
                        <div>
                            <h4 style="color: #495057; margin-bottom: 10px;">🔧 技术特性</h4>
                            <ul style="color: #6c757d; line-height: 2;">
                                <li>🚀 Flask 3.0 + Python 3.11</li>
                                <li>🎨 现代化界面</li>
                                <li>📱 响应式设计</li>
                                <li>🔒 JWT 认证</li>
                                <li>⚡ 高性能架构</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 登录 -->
            <div id="login-section" class="section">
                <div class="card" style="max-width: 500px; margin: 0 auto;">
                    <h3>🔐 用户登录</h3>
                    <div class="form-group">
                        <label>用户名</label>
                        <input type="text" id="login-username" placeholder="请输入用户名" value="admin">
                    </div>
                    <div class="form-group">
                        <label>密码</label>
                        <input type="password" id="login-password" placeholder="请输入密码" value="admin123">
                    </div>
                    <button class="btn" onclick="login()">登录</button>
                    <div class="loading" id="login-loading">登录中</div>
                    <div class="result-box" id="login-result"></div>
                </div>
            </div>

            <!-- 实时分析 -->
            <div id="realtime" class="section">
                <div class="card">
                    <h3>📈 实时市场分析</h3>
                    <p style="color: #6c757d; margin-bottom: 20px;">分析指定股票的实时行情、技术指标和交易信号</p>
                    <div class="form-group">
                        <label>股票代码</label>
                        <input type="text" id="realtime-symbol" placeholder="例如：600000" value="600000">
                    </div>
                    <button class="btn" onclick="analyzeRealtime()">开始分析</button>
                    <div class="loading" id="realtime-loading">分析中</div>
                    <div class="result-box" id="realtime-result"></div>
                </div>
            </div>

            <!-- 筹码分布 -->
            <div id="chip" class="section">
                <div class="card">
                    <h3>💰 筹码分布分析</h3>
                    <p style="color: #6c757d; margin-bottom: 20px;">分析股票的筹码分布、集中度和成本区</p>
                    <div class="form-group">
                        <label>股票代码</label>
                        <input type="text" id="chip-symbol" placeholder="例如：600000" value="600000">
                    </div>
                    <button class="btn" onclick="analyzeChip()">开始分析</button>
                    <div class="loading" id="chip-loading">分析中</div>
                    <div class="result-box" id="chip-result"></div>
                </div>
            </div>

            <!-- 市场分析 -->
            <div id="market" class="section">
                <div class="card">
                    <h3>📊 市场综合分析</h3>
                    <p style="color: #6c757d; margin-bottom: 20px;">整体市场环境、趋势和热点分析</p>
                    <button class="btn" onclick="analyzeMarket()">开始分析</button>
                    <div class="loading" id="market-loading">分析中</div>
                    <div class="result-box" id="market-result"></div>
                </div>
            </div>

            <!-- 导出功能 -->
            <div id="export" class="section">
                <div class="card">
                    <h3>📥 导出功能</h3>
                    <div class="two-columns">
                        <div>
                            <h4 style="color: #495057; margin-bottom: 15px;">PDF 导出</h4>
                            <p style="color: #6c757d; margin-bottom: 15px;">将分析结果导出为 PDF 文件</p>
                            <button class="btn" onclick="exportPDF()">导出 PDF</button>
                            <div class="loading" id="pdf-loading">导出中</div>
                        </div>
                        <div>
                            <h4 style="color: #495057; margin-bottom: 15px;">飞书文档导出</h4>
                            <p style="color: #6c757d; margin-bottom: 15px;">将分析结果导出到飞书文档</p>
                            <button class="btn" onclick="exportFeishu()">导出到飞书</button>
                            <div class="loading" id="feishu-loading">导出中</div>
                        </div>
                    </div>
                    <div class="result-box" id="export-result"></div>
                </div>
            </div>

            <!-- 关于 -->
            <div id="about" class="section">
                <div class="card">
                    <h3>ℹ️ 关于 OpenClaw</h3>
                    <div style="color: #6c757d; line-height: 2;">
                        <p><strong>版本：</strong>v5.0</p>
                        <p><strong>开发团队：</strong>OpenClaw</p>
                        <p><strong>技术栈：</strong>Python 3.11 + Flask 3.0</p>
                        <p><strong>联系方式：</strong>contact@ntdf.com</p>
                        <p style="margin-top: 20px;">OpenClaw 统一量化交易平台是一个基于 AI 的智能量化交易系统，提供实时分析、市场扫描、智能选股、回测监控等功能。</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>© 2026 OpenClaw 统一量化交易平台 v5.0 | 仅供测试使用</p>
        </div>
    </div>

    <script>
        function showSection(sectionId) {
            // 隐藏所有 section
            document.querySelectorAll('.section').forEach(section => {
                section.classList.remove('active');
            });

            // 移除所有 nav 链接的 active 类
            document.querySelectorAll('.nav a').forEach(link => {
                link.classList.remove('active');
            });

            // 显示选中的 section
            document.getElementById(sectionId).classList.add('active');

            // 添加 active 类到对应的链接
            event.target.classList.add('active');
        }

        function login() {
            const username = document.getElementById('login-username').value;
            const password = document.getElementById('login-password').value;

            console.log('开始登录...');
            console.log('用户名:', username);
            console.log('密码长度:', password.length);

            if (!username || !password) {
                alert('请输入用户名和密码！');
                return;
            }

            document.getElementById('login-loading').classList.add('show');
            document.getElementById('login-result').classList.remove('show');

            const requestData = {
                username: username,
                password: password
            };
            console.log('请求数据:', JSON.stringify(requestData));

            fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            })
            .then(response => {
                console.log('响应状态:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('响应数据:', data);
                document.getElementById('login-loading').classList.remove('show');
                document.getElementById('login-result').classList.add('show');

                if (data.success) {
                    // 保存token和用户信息到localStorage
                    localStorage.setItem('token', data.token);
                    localStorage.setItem('user', JSON.stringify(data.user));

                    document.getElementById('login-result').innerHTML = `
                        <h4>✅ 登录成功！</h4>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    `;

                    // 更新UI显示已登录状态
                    updateLoginStatus();

                    // 跳转到主界面
                    showSection('home');

                    alert('登录成功！欢迎 ' + data.user.username);
                } else {
                    document.getElementById('login-result').innerHTML = `
                        <h4>❌ 登录失败</h4>
                        <p>${data.message}</p>
                        <pre>请检查用户名和密码<br>默认账户: admin / admin123</pre>
                    `;
                }
            })
            .catch(error => {
                console.error('登录错误:', error);
                document.getElementById('login-loading').classList.remove('show');
                document.getElementById('login-result').classList.add('show');
                document.getElementById('login-result').innerHTML = `
                    <h4>❌ 请求错误</h4>
                    <p>${error.message}</p>
                    <p>请检查网络连接或刷新页面重试</p>
                `;
                alert('登录请求失败: ' + error.message);
            });
        }

        function updateLoginStatus() {
            const user = JSON.parse(localStorage.getItem('user') || 'null');
            const navLogin = document.getElementById('nav-login');
            const logoutBtn = document.getElementById('logout-btn');

            if (user) {
                // 已登录
                if (navLogin) navLogin.style.display = 'none';
                if (logoutBtn) logoutBtn.style.display = 'inline-block';

                // 更新显示
                const userInfo = document.getElementById('user-info');
                if (userInfo) {
                    userInfo.innerHTML = `已登录: ${user.username} (${user.role})`;
                    userInfo.style.display = 'block';
                }
            } else {
                // 未登录
                if (navLogin) navLogin.style.display = 'block';
                if (logoutBtn) logoutBtn.style.display = 'none';

                // 隐藏用户信息
                const userInfo = document.getElementById('user-info');
                if (userInfo) userInfo.style.display = 'none';
            }
        }

        function quickLogin() {
            // 快速登录函数，直接使用默认账号
            const username = 'admin';
            const password = 'admin123';

            const requestData = {
                username: username,
                password: password
            };

            console.log('快速登录...');

            fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // 保存到 localStorage
                    localStorage.setItem('token', data.token);
                    localStorage.setItem('user', JSON.stringify(data.user));

                    // 更新UI
                    updateLoginStatus();

                    alert('✅ 登录成功！欢迎 ' + data.user.username);
                } else {
                    alert('❌ 登录失败：' + data.message);
                }
            })
            .catch(error => {
                console.error('快速登录错误:', error);
                alert('❌ 登录请求失败: ' + error.message);
            });
        }

        function logout() {
            // 清除localStorage
            localStorage.removeItem('token');
            localStorage.removeItem('user');

            // 更新UI
            updateLoginStatus();

            // 跳转到登录界面
            showSection('login-section');

            alert('已退出登录');
        }

        // 页面加载时检查登录状态
        window.addEventListener('DOMContentLoaded', function() {
            updateLoginStatus();

            // 如果已登录，跳转到首页
            const user = JSON.parse(localStorage.getItem('user') || 'null');
            if (user) {
                showSection('home');
            }
        });

        function analyzeRealtime() {
            const symbol = document.getElementById('realtime-symbol').value;

            document.getElementById('realtime-loading').classList.add('show');
            document.getElementById('realtime-result').classList.remove('show');

            fetch(`/api/analysis/realtime/${symbol}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('realtime-loading').classList.remove('show');
                document.getElementById('realtime-result').classList.add('show');
                document.getElementById('realtime-result').innerHTML = `
                    <h4>${data.success ? '✅ 分析完成' : '❌ 分析失败'}</h4>
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                `;
            })
            .catch(error => {
                document.getElementById('realtime-loading').classList.remove('show');
                document.getElementById('realtime-result').classList.add('show');
                document.getElementById('realtime-result').innerHTML = `
                    <h4>❌ 请求错误</h4>
                    <pre>${error.message}</pre>
                `;
            });
        }

        function analyzeChip() {
            const symbol = document.getElementById('chip-symbol').value;

            document.getElementById('chip-loading').classList.add('show');
            document.getElementById('chip-result').classList.remove('show');

            fetch(`/api/analysis/chip/${symbol}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('chip-loading').classList.remove('show');
                document.getElementById('chip-result').classList.add('show');
                document.getElementById('chip-result').innerHTML = `
                    <h4>${data.success ? '✅ 分析完成' : '❌ 分析失败'}</h4>
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                `;
            })
            .catch(error => {
                document.getElementById('chip-loading').classList.remove('show');
                document.getElementById('chip-result').classList.add('show');
                document.getElementById('chip-result').innerHTML = `
                    <h4>❌ 请求错误</h4>
                    <pre>${error.message}</pre>
                `;
            });
        }

        function analyzeMarket() {
            document.getElementById('market-loading').classList.add('show');
            document.getElementById('market-result').classList.remove('show');

            fetch('/api/analysis/market')
            .then(response => response.json())
            .then(data => {
                document.getElementById('market-loading').classList.remove('show');
                document.getElementById('market-result').classList.add('show');
                document.getElementById('market-result').innerHTML = `
                    <h4>${data.success ? '✅ 分析完成' : '❌ 分析失败'}</h4>
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                `;
            })
            .catch(error => {
                document.getElementById('market-loading').classList.remove('show');
                document.getElementById('market-result').classList.add('show');
                document.getElementById('market-result').innerHTML = `
                    <h4>❌ 请求错误</h4>
                    <pre>${error.message}</pre>
                `;
            });
        }

        function exportPDF() {
            document.getElementById('pdf-loading').classList.add('show');
            document.getElementById('export-result').classList.remove('show');

            fetch('/api/export/pdf')
            .then(response => response.json())
            .then(data => {
                document.getElementById('pdf-loading').classList.remove('show');
                document.getElementById('export-result').classList.add('show');
                document.getElementById('export-result').innerHTML = `
                    <h4>${data.success ? '✅ 导出成功' : '❌ 导出失败'}</h4>
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                `;
            })
            .catch(error => {
                document.getElementById('pdf-loading').classList.remove('show');
                document.getElementById('export-result').classList.add('show');
                document.getElementById('export-result').innerHTML = `
                    <h4>❌ 请求错误</h4>
                    <pre>${error.message}</pre>
                `;
            });
        }

        function exportFeishu() {
            document.getElementById('feishu-loading').classList.add('show');
            document.getElementById('export-result').classList.remove('show');

            fetch('/api/export/feishu')
            .then(response => response.json())
            .then(data => {
                document.getElementById('feishu-loading').classList.remove('show');
                document.getElementById('export-result').classList.add('show');
                document.getElementById('export-result').innerHTML = `
                    <h4>${data.success ? '✅ 导出成功' : '❌ 导出失败'}</h4>
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                `;
            })
            .catch(error => {
                document.getElementById('feishu-loading').classList.remove('show');
                document.getElementById('export-result').classList.add('show');
                document.getElementById('export-result').innerHTML = `
                    <h4>❌ 请求错误</h4>
                    <pre>${error.message}</pre>
                `;
            });
        }
    </script>
</body>
</html>
"""

# 模拟数据
MOCK_DATA = {
    'realtime': {
        'success': True,
        'message': '实时分析完成',
        'data': {
            'symbol': '600000',
            'name': '浦发银行',
            'price': 10.23,
            'change': '+0.15',
            'change_percent': '+1.49%',
            'volume': 1234567,
            'signals': ['买入', '强势', '资金流入'],
            'indicators': {
                'ma5': 10.18,
                'ma10': 10.15,
                'ma20': 10.12,
                'rsi': 65.3,
                'macd': 0.23
            }
        }
    },
    'chip': {
        'success': True,
        'message': '筹码分布完成',
        'data': {
            'symbol': '600000',
            'name': '浦发银行',
            'concentration': '高度集中',
            'cost_area': [9.8, 10.5],
            'distribution': [
                {'price': 10.0, 'ratio': 15},
                {'price': 10.2, 'ratio': 35},
                {'price': 10.5, 'ratio': 30},
                {'price': 11.0, 'ratio': 20}
            ]
        }
    },
    'market': {
        'success': True,
        'message': '市场综合分析完成',
        'data': {
            'trend': '震荡上行',
            'sentiment': '乐观',
            'hot_sectors': ['银行', '新能源', '半导体'],
            'market_cap': 500000,
            'volume': 123456789,
            'advice': '建议持有优质蓝筹股'
        }
    },
    'export': {
        'success': True,
        'message': '导出成功',
        'data': {
            'file': 'analysis_report.pdf',
            'size': '2.5MB'
        }
    }
}

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/login-test')
def login_test():
    with open('quick_login.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # 简单验证
    if username == 'admin' and password == 'admin123':
        return jsonify({
            'success': True,
            'message': '登录成功',
            'token': 'mock_token_123456',
            'user': {
                'username': 'admin',
                'email': 'admin@ntdf.com',
                'role': 'admin'
            }
        })
    else:
        return jsonify({
            'success': False,
            'message': '用户名或密码错误'
        }), 401

@app.route('/api/analysis/realtime/<symbol>')
def realtime_analysis(symbol):
    return jsonify(MOCK_DATA['realtime'])

@app.route('/api/analysis/chip/<symbol>')
def chip_analysis(symbol):
    return jsonify(MOCK_DATA['chip'])

@app.route('/api/analysis/market')
def market_analysis():
    return jsonify(MOCK_DATA['market'])

@app.route('/api/export/pdf')
def export_pdf():
    return jsonify(MOCK_DATA['export'])

@app.route('/api/export/feishu')
def export_feishu():
    return jsonify({
        'success': True,
        'message': '飞书文档导出成功',
        'content': '# 分析报告\\n\\n实时分析完成...'
    })

@app.route('/test-login')
def test_login_page():
    with open('test_login.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/simple-login')
def simple_login_page():
    with open('simple_login.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/pure-login', methods=['GET', 'POST'])
def pure_login():
    """纯HTML登录页面，使用表单提交"""
    from flask import render_template_string

    with open('pure_login.html', 'r', encoding='utf-8') as f:
        template = f.read()

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # 验证用户名和密码
        if username == 'admin' and password == 'admin123':
            # 登录成功，直接跳转到主页面
            user = {
                'username': 'admin',
                'email': 'admin@ntdf.com',
                'role': 'admin'
            }
            return render_template_string(open('main_no_js.html', 'r', encoding='utf-8').read(), user=user)
        else:
            # 登录失败
            return render_template_string(template, error='用户名或密码错误')

    return render_template_string(template)

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    """分析股票（无需JavaScript）"""
    from flask import render_template_string

    result = None
    if request.method == 'POST':
        symbol = request.form.get('symbol')

        # 调用实际的模拟数据
        data = MOCK_DATA['realtime']
        data['data']['symbol'] = symbol

        # 格式化分析结果
        result = f"""股票分析报告 - {symbol}

【基本信息】
  • 股票代码：{symbol}
  • 当前价格：{data['data']['price']} 元
  • 涨跌幅：{data['data']['change']} ({data['data']['change_percent']})
  • 成交量：{data['data']['volume']:,}

【交易信号】
  • 信号强度：⭐⭐⭐⭐⭐
  • 交易信号：{" | ".join(data['data']['signals'])}
  • 资金流向：流入
  • 买入建议：⚡ 建议买入

【技术指标】
  • MA5：{data['data']['indicators']['ma5']} 元
  • MA10：{data['data']['indicators']['ma10']} 元
  • MA20：{data['data']['indicators']['ma20']} 元
  • RSI：{data['data']['indicators']['rsi']}
  • MACD：{data['data']['indicators']['macd']}

【技术分析】
  • 趋势：上涨 📈
  • 强度：中等偏强
  • 支撑位：{data['data']['price'] * 0.98:.2f} 元
  • 阻力位：{data['data']['price'] * 1.02:.2f} 元

【操作建议】
  1. 当前趋势向上，可考虑适当建仓
  2. 建议分批买入，控制风险
  3. 止损位设置在支撑位以下（{data['data']['price'] * 0.98:.2f} 元）
  4. 目标价位：{data['data']['price'] * 1.05:.2f} 元

【风险提示】
  • 风险等级：中等
  • 建议仓位：30-50%
  • 止损比例：2-3%

分析时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
数据来源：模拟数据（测试环境）
"""

    user = {
        'username': 'admin',
        'email': 'admin@ntdf.com',
        'role': 'admin'
    }
    return render_template_string(open('main_no_js.html', 'r', encoding='utf-8').read(), user=user, result=result)

@app.route('/visual-analyze', methods=['GET', 'POST'])
def visual_analyze():
    """可视化分析报告"""
    from flask import render_template_string

    if request.method == 'POST':
        symbol = request.form.get('symbol')

        # 获取模拟数据
        data = MOCK_DATA['realtime']
        data['data']['symbol'] = symbol

        # 计算支撑位、阻力位、目标价
        price = data['data']['price']
        support_price = price * 0.98
        resistance_price = price * 1.02
        target_price = price * 1.05

        # 准备模板数据
        template_data = {
            'symbol': symbol,
            'price': f"￥{price:.2f}",
            'change': data['data']['change'],
            'change_percent': data['data']['change_percent'],
            'volume': data['data']['volume'],
            'volume_formatted': f"{data['data']['volume']:,}",
            'signals': data['data']['signals'],
            'ma5': data['data']['indicators']['ma5'],
            'ma10': data['data']['indicators']['ma10'],
            'ma20': data['data']['indicators']['ma20'],
            'rsi': data['data']['indicators']['rsi'],
            'macd': data['data']['indicators']['macd'],
            'support_price': f"￥{support_price:.2f}",
            'resistance_price': f"￥{resistance_price:.2f}",
            'target_price': f"￥{target_price:.2f}",
            'analysis_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        return render_template_string(
            open('visual_report.html', 'r', encoding='utf-8').read(),
            **template_data
        )

    # GET请求，返回分析页面
    return render_template_string(
        open('main_no_js.html', 'r', encoding='utf-8').read(),
        user={'username': 'admin', 'email': 'admin@ntdf.com', 'role': 'admin'}
    )

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 OpenClaw 统一量化交易平台 v5.0 - 网页版")
    print("=" * 70)
    print("✅ 应用启动成功")
    print("\n🌐 测试环境启动")
    print("=" * 70)
    print("访问地址: http://localhost:7000")
    print("默认账户: admin / admin123")
    print("=" * 70)

    app.run(host='0.0.0.0', port=7000, debug=False)
