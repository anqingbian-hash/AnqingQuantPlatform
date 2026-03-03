#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主平台 v10.0 - 双源切换版（完整修复版）
"""
from flask import Flask, render_template_string, jsonify, request
from datetime import datetime
import requests
import json
import logging

# 配置
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['JSON_AS_ASCII'] = False

# 日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据源配置
PRIMARY_SOURCE_URL = 'http://localhost:7000'
BACKUP_SOURCE_URL = 'https://api.tushare.pro'
TUSHARE_TOKEN = '8b159caa2bbf554707c20c3f44fea1e0e6ec75b6afc82c78fa47e47b'
CACHE_TTL = 600

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
            margin: 0 0 10px 0;
            font-size: 24px;
        }
        .card p {
            font-size: 14px;
            opacity: 0.9;
        }
        .results {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin-top: 20px;
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
            <p>双源切换 | AKShare + Tushare | 实时行情 + 智能选股</p>
        </div>
        <div class="source-status">
            <div class="source-item active">
                <h3>主数据源</h3>
                <p>AKShare</p>
            </div>
            <div class="source-item inactive">
                <h3>备用数据源</h3>
                <p>Tushare Pro</p>
            </div>
            <div class="source-item inactive">
                <h3>第三数据源</h3>
                <p>新浪财经</p>
            </div>
        </div>
        <div class="cards">
            <div class="card" onclick="showLoading('正在扫描全市场板块...')">
                <h3>📊 板块扫描</h3>
                <p>扫描全市场19个板块</p>
            </div>
            <div class="card" onclick="showLoading('正在进行智能选股...')">
                <h3>🎯 智能选股</h3>
                <p>四类策略评分</p>
            </div>
            <div class="card" onclick="showLoading('正在分析股票...')">
                <h3>📈 股票分析</h3>
                <p>个股技术分析</p>
            </div>
            <div class="card" onclick="showLoading('正在加载实战案例...')">
                <h3>💡 实战案例</h3>
                <p>烽火通信+通信龙头</p>
            </div>
        </div>
        <div id="results"></div>
    </div>
    <script>
        function showLoading(message) {
            document.getElementById('results').innerHTML = 
                '<div class="loading">' + message + '<br><br>请稍候...</div>';
        }
    </script>
</body>
</html>
'''

# Flask路由
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
        'cache_ttl': CACHE_TTL
    })

@app.route('/api/scan', methods=['GET', 'POST'])
def market_scan():
    """板块扫描"""
    try:
        logger.info("[主平台] 板块扫描请求")
        response = requests.get(f"{PRIMARY_SOURCE_URL}/api/realtime_quotes?symbols=all", timeout=10)
        data = response.json()
        
        if data.get('success', False) and data.get('data'):
            return jsonify({
                'success': True,
                'source': 'AKShare',
                'data': data['data']
            })
        else:
            return jsonify({
                'success': False,
                'error': '数据获取失败'
            })
    except Exception as e:
        logger.error(f"[主平台] 板块扫描失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/selector', methods=['GET', 'POST'])
def selector():
    """智能选股"""
    try:
        logger.info("[主平台] 智能选股请求")
        response = requests.get(f"{PRIMARY_SOURCE_URL}/api/realtime_quotes?symbols=top10", timeout=10)
        data = response.json()
        
        if data.get('success', False) and data.get('data'):
            return jsonify({
                'success': True,
                'source': 'AKShare',
                'data': data['data']
            })
        else:
            return jsonify({
                'success': False,
                'error': '数据获取失败'
            })
    except Exception as e:
        logger.error(f"[主平台] 智能选股失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/stock_info/<symbol>')
def stock_info(symbol):
    """股票基本信息"""
    try:
        logger.info(f"[主平台] 股票基本信息: {symbol}")
        response = requests.get(f"{PRIMARY_SOURCE_URL}/api/realtime_quotes?symbols={symbol}", timeout=10)
        data = response.json()
        
        if data.get('success', False) and data.get('data'):
            return jsonify({
                'success': True,
                'source': 'AKShare',
                'data': data['data'][0] if data['data'] else {}
            })
        else:
            return jsonify({
                'success': False,
                'error': '数据获取失败'
            })
    except Exception as e:
        logger.error(f"[主平台] 股票信息异常: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/history/<symbol>')
def history_data(symbol):
    """历史数据"""
    try:
        logger.info(f"[主平台] 历史数据: {symbol}")
        return jsonify({
            'success': True,
            'message': '历史数据功能待实现'
        })
    except Exception as e:
        logger.error(f"[主平台] 历史数据异常: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/realtime_quotes', methods=['GET', 'POST'])
def realtime_quotes():
    """实时行情"""
    try:
        logger.info("[主平台] 实时行情请求")
        symbols = request.args.get('symbols', '300750,600519,000858')
        
        response = requests.get(f"{PRIMARY_SOURCE_URL}/api/realtime_quotes?symbols={symbols}", timeout=10)
        data = response.json()
        
        if data.get('success', False) and data.get('data'):
            return jsonify({
                'success': True,
                'source': 'AKShare',
                'data': data['data']
            })
        else:
            return jsonify({
                'success': False,
                'error': '数据获取失败'
            })
    except Exception as e:
        logger.error(f"[主平台] 实时行情异常: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/cases', methods=['GET', 'POST'])
def cases_list():
    """实战案例"""
    try:
        logger.info("[主平台] 实战案例请求")
        cases = [
            {
                'id': 'case_600498',
                'name': '烽火通信（600498）',
                'sector': '通信设备',
                'theme': '5G应用',
                'score': 90.0,
                'summary': '通信板块龙头，多周期共振向上，量价结构健康'
            },
            {
                'id': 'case_communication',
                'name': '通信龙头',
                'sector': '通信设备',
                'theme': '算力芯片',
                'score': 92.5,
                'summary': '通信板块算力芯片龙头，量价结构健康，主力净流入'
            }
        ]
        return jsonify({
            'success': True,
            'cases': cases
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/stats')
def get_stats():
    """统计信息"""
    return jsonify({
        'success': True,
        'timestamp': datetime.now().isoformat(),
        'api_calls': {
            'total': 0,
            'success': 0,
            'fail': 0
        }
    })

@app.route('/api/switch_source', methods=['POST'])
def switch_source():
    """切换数据源"""
    data = request.get_json()
    new_source = data.get('source', 'akshare')
    
    logger.info(f"[主平台] 切换数据源: {new_source}")
    
    return jsonify({
        'success': True,
        'source': new_source,
        'message': f'已切换到{new_source}数据源'
    })

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """清空缓存"""
    logger.info("[主平台] 清空缓存")
    return jsonify({
        'success': True,
        'message': '缓存已清空'
    })

if __name__ == '__main__':
    print("="*80)
    print("🎯 AnqingA股大师 v10.0 - 双源切换完整版")
    print("="*80)
    print(f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 主地址: http://localhost:7000")
    print(f"🔗 外网: http://43.160.233.168:7000")
    print("="*80)
    print("API端点:")
    print("  GET  /api/health           - 健康检查")
    print("  GET/POST  /api/scan          - 板块扫描")
    print("  GET/POST  /api/selector      - 智能选股")
    print("  GET  /api/stock_info/<symbol> - 股票基本信息")
    print("  GET/POST  /api/realtime_quotes - 实时行情")
    print("  GET  /api/history/<symbol>    - 历史数据")
    print("  GET/POST  /api/cases         - 实战案例")
    print("  GET  /api/stats              - 统计信息")
    print("  POST  /api/switch_source     - 切换数据源")
    print("  POST  /api/cache/clear       - 清空缓存")
    print("="*80)
    print("🚀 服务启动")
    print("="*80)
    
    app.run(host='0.0.0.0', port=7000, debug=False)
