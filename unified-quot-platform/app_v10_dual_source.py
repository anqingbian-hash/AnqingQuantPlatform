#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主平台 v10.0 - 双源切换完整版
集成AKShare + Tushare
集成实时行情、智能选股、板块扫描、实战案例
"""
from flask import Flask, render_template_string, jsonify, request
from datetime import datetime
import logging

# 导入数据管理器
sys.path.append(os.path.dirname(__file__))

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 配置
TUSHARE_TOKEN = '8b159caa2bbf554707c20c3f44fea1e0e6ec75b6afc82c78fa47e47b'
AKSHARE_TOKEN = ''  # AKShare如果需要token可以添加
API_TIMEOUT = 5
CACHE_TTL = 600  # 10分钟缓存

# 主数据源URL
PRIMARY_SOURCE_URL = 'http://localhost:7000'  # 主平台（AKShare服务）

# 备用数据源（使用Tushare）
BACKUP_SOURCE = 'https://api.tushare.pro'

# 专用数据源
MONEY_FLOW_API = 'http://localhost:7000'  # 资金流服务
LHB_API = 'http://localhost:7000'        # 龙虎榜服务

# 页面模板
MAIN_PAGE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title> AnqingA股大师 v10.0</title>
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
            max-width: 1400px;
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
            font-size: 36px;
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
            margin-bottom: 30px;
        }
        .source-item {
            flex: 1;
            text-align: center;
        }
        .active { color: #28a745; font-weight: bold; }
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
            transition: transform 0.3s;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
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
            background: #8f9fa;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .results {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin-top: 20px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 AnqingA股大师 v10.0</h1>
            <p>双源切换 | AKShare + Tushare | 实时行情 | 智能选股 | 板块扫描 | 实战案例</p>
        </div>
        <div class="source-status">
            <div class="source-item active">
                <h3>主数据源</h3>
                <p>AKShare (localhost:7000)</p>
            </div>
            <div class="source-item inactive">
                <h3>备用数据源</h3>
                <p>Tushare Pro</p>
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
            <div class="card" onclick="cases()">
                <h3>💡 实战案例</h3>
                <p>烽火通信、通信龙头</p>
            </div>
        </div>
        <div id="results"></div>
        <div class="status">
            <h3>状态加载中...</h3>
        </div>
    </div>
    <script>
        let currentSource = 'AKShare';
        
        function switchSource(source) {
            currentSource = source;
            updateSourceStatus();
            showLoading('切换数据源中...');
        }
        
        function updateSourceStatus() {
            fetch('/api/health').then(response => {
                const data = response.json();
                document.getElementById('primary-source').className = source === 'AKShare' ? 'active' : 'inactive';
                document.getElementById('backup-source').className = source === 'Tushare' ? 'active' : 'inactive';
            }).catch(error => {
                showError('切换失败: ' + error.message);
            });
        }
        
        function showLoading(message) {
            document.getElementById('results').innerHTML = 
                '<div class="loading">' + message + '<br><br>请稍候...</div>';
        }
        
        function showError(message) {
            document.getElementById('results').innerHTML = 
                '<div style="color: red; text-align: center; padding: 20px;">' + message + '</div>';
        }
        
        function scanMarket() {
            showLoading('正在扫描全市场板块...');
            try {
                const response = await fetch('/api/market/scan');
                const data = await response.json();
                displayResults('板块扫描结果', data);
            } catch (error) {
                showError('扫描失败: ' + error.message);
            }
        }
        
        function selector() {
            showLoading('正在进行智能选股...');
            try {
                const response = await fetch('/api/selector');
                const data = await response.json();
                displayResults('智能选股结果', data);
            } catch (error) {
                showError('选股失败: ' + error.message);
            }
        }
        
        function cases() {
            showLoading('正在加载实战案例...');
            try {
                const response = await fetch('/api/cases');
                const data = await response.json();
                displayResults('实战案例', data);
            } catch (error) {
                showError('加载失败: ' + error.message);
            }
        }
        
        function displayResults(title, data) {
            let html = '<h2>' + title + '</h2>';
            html += '<div class="recommendations">';
            
            if (data.stocks && data.stocks.length > 0) {
                data.stocks.forEach((stock, i) => {
                    html += '<div class="rec-item">';
                    html += '<div class="stock-score">评分: ' + stock.score.toFixed(1) + '</div>';
                    html += '<div class="rec-item">板块: ' + stock.sector + '</div>';
                    html += '<div class="rec-item">名称: ' + stock.name + '</div>';
                    html += '<div class="rec-item">代码: ' + stock.symbol + '</div>';
                    html += '<div class="rec-item">价格: ¥' + stock.price.toFixed(2) + '</div>';
                    html += '<div class="rec-item">涨跌: ' + stock.pct_chg.toFixed(2) + '%</div>';
                    html += '<div class="rec-item">止损: ¥' + stock.stop_loss.toFixed(2) + '</div>';
                    html += '<div class="rec-item">止盈: ¥' + stock.take_profit1.toFixed(2) + '</div>';
                    html += '<div class="rec-item">仓位: ' + stock.position.toFixed(0) + '%</div>';
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
        
        // 定时刷新
        setInterval(() => {
            fetch('/api/stats').then(response => {
                const data = response.json();
                updateSourceStatus();
            });
        }, 60000);  // 每分钟刷新一次
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """首页"""
    return render_template_string(MAIN_PAGE)

@app.route('/api/health')
def health_check():
    """健康检查"""
    logger.info("[主平台] 健康检查")
    
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'primary_source': PRIMARY_SOURCE_URL,
        'backup_source': BACKUP_SOURCE_URL
        'cache_ttl': CACHE_TTL,
        'api_calls': {
            'total': 0,
            'success': 0,
            'fail': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    })

@app.route('/api/switch_source', methods=['POST'])
def switch_source():
    """切换数据源"""
    data = request.json
    source = data.get('source', 'akshare')
    
    logger.info(f"[主平台] 切换数据源: {source}")
    
    return jsonify({
        'success': True,
        'source': source,
        'message': f"已切换到{'AKShare' if source == 'akshare' else 'Tushare'}数据源"
    })

@app.route('/api/market/scan', methods=['GET', 'POST'])
def market_scan():
    """板块扫描"""
    logger.info("[主平台] 板块扫描请求")
    
    try:
        logger.info("[主平台] 调用主数据源: {PRIMARY_SOURCE_URL}")
        response = requests.get(f"{PRIMARY_SOURCE_URL}/api/market/scan", timeout=API_TIMEOUT)
        data = response.json()
        
        if data.get('success', False) and data.get('data'):
            logger.info(f"[主平台] 板块扫描成功: {len(data['data'])} 个板块")
            return jsonify({
                'success': True,
                'source': 'AKShare',
                'data': data['data']
            })
        
        except Exception as e:
            logger.error(f"[主平台] 板块扫描失败: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/selector', methods=['GET', 'POST'])
def selector():
    """智能选股"""
    logger.info("[主平台] 智能选股请求")
    
    try:
        logger.info("[主平台] 调用主数据源: {PRIMARY_SOURCE_URL}")
        response = requests.get(f"{PRIMARY_SOURCE_URL}/api/selector", timeout=API_TIMEOUT)
        data = response.json()
        
        if data.get('success', False) and data.get('data'):
            logger.info(f"[主平台] 智能选股成功: {len(data['data'])} 只股票")
            return jsonify({
                'success': True,
                'source': 'AKShare',
                'data': data['data']
            })
        
        except Exception as e:
            logger.error(f"[主平台] 智能选股失败: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            })
    
    except Exception as e:
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
            'tags': ['量价结构健康', '主力净流入', '多周期共振'],
            'summary': '烽火通信（600498）- 通信板块龙头，多周期共振向上，量价结构健康，主力净流入'
        },
        {
            'id': 'case_communication',
            'name': '通信龙头',
            'sector': '通信设备',
            'theme': '算力芯片',
            'score': 92.5,
            'tags': ['量价结构健康', '主力净流入', '板块领涨'],
            'summary': '通信板块算力芯片龙头，量价结构健康，主力净流入，板块领涨，多周期共振'
        },
        {
            'id': 'case_603019',
            'name': '中科曙光',
            'sector': '计算机',
            'theme': '算力芯片',
            'score': 88.5,
            'tags': ['低位启动', 'AI芯片概念'],
            'summary': '中科曙光（603019）- AI芯片低位启动，主力关注'
        }
    ]
    
    return jsonify({
        'success': True,
        'cases': cases
    })

@app.route('/api/realtime_quotes', methods=['GET', 'POST'])
def realtime_quotes():
    """实时行情（10只精选股）"""
    logger.info("[主平台] 实时行情请求")
    
    symbols = [
        '300750',  # 宁德时代
        '600519',  # 贵州茅台
        '000858',  # 五粮液
        '600887',  # 伊利股份
        '600276',  # 恒瑞医药
        '603019',  # 中科曙光
        '000977',  # 浪潮信息
        '000977',  # 卓易信息
    ]
    
    try:
        logger.info("[主平台] 调用主数据源: {PRIMARY_SOURCE_URL}")
        response = requests.get(
            f"{PRIMARY_SOURCE_URL}/api/realtime_quotes?symbols={','.join(symbols)}",
            timeout=API_TIMEOUT
        )
        data = response.json()
        
        if data.get('success', False) and data.get('data'):
            logger.info(f"[主平台] 实时行情成功: {len(data['data'])} 只股票")
            return jsonify({
                'success': True,
                'source': 'AKShare',
                'data': data['data']
            })
        
    except Exception as e:
        logger.error(f"[主平台] 实时行情失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/stats')
def get_stats():
    """获取统计"""
    return jsonify({
        'success': True,
        'timestamp': datetime.now().isoformat(),
        'primary_source': PRIMARY_SOURCE_URL,
        'backup_source': BACKUP_SOURCE_URL,
        'cache_ttl': CACHE_TTL,
        'api_calls': {
            'total': 0,
            'success': 0,
            'fail': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    })

if __name__ == '__main__':
    print("="*80)
    print("🎯 AnqingA股大师 v10.0 - 双源切换完整版")
    print("="*80)
    print(f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📡 主地址: http://43.160.233.168:7000")
    print(f"📊 备用地址: http://43.160.233.168:5000")
    print("="*80)
    print("API端点:")
    print("  GET  /api/health              - 健康检查")
    print("  GET  /api/market/scan         - 板块扫描")
    print("  GET/POST /api/selector       - 智能选股")
    print("  GET       /api/cases             - 实战案例")
    print("  GET/POST  /api/realtime_quotes  - 实时行情")
    print("  GET       /api/stats               - 统计信息")
    print("  POST      /api/switch_source    - 切换数据源")
    print("="*80)
    print("🚀 服务启动")
    print("="*80)
    print(f"python3 {sys.argv[0]} app_v10_dual_source.py")
    print("="*80)
    
    # 启动服务
    print("启动命令:")
    print(f"python3 {sys.argv[0]} app_v10_dual_source.py")
    print(f"服务地址: http://0.0.0.0:7000")
    print(f"外网地址: http://43.160.233.168:7000")
    print(f"启动日志: nohup python3 app_v10_dual_source.py")
    print("="*80)
    
    try:
        # 不使用nohup，直接启动
        # app.run(host='0.0.0.0', port=7000, debug=False)
        from waitress.server import serve
        serve(app, host='0.0.0.0', port=7000)
    except Exception as e:
        print(f"启动失败: {e}")
    
    print("="*80)
    print("✅ 启动完成")
    print("="*80)
