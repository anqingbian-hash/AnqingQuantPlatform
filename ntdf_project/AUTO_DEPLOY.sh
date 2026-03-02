#!/bin/bash

# ===========================================
# NTDF 项目完整自动化部署脚本
# 版本：2.0
# 目标：一键完成所有开发工作
# ===========================================

echo "=========================================="
echo "  NTDF 项目自动化部署"
echo "  版本 2.0"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 函数：打印成功消息
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# 函数：打印警告消息
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 函数：打印错误消息
error() {
    echo -e "${RED}❌ $1${NC}"
}

# ===========================================
# 步骤1：添加后端功能
# ===========================================

echo ""
echo "=========================================="
echo "  步骤1/5: 添加后端API接口"
echo "=========================================="
echo ""

cd /var/www/ntdf/backend

# 添加Alpha Vantage日线数据接口
echo "" >> simple_main.py
echo "@app.get(\"/api/market/alpha_vantage/daily\")" >> simple_main.py
echo "async def get_alpha_vantage_daily(symbol: str, outputsize: str = \"compact\"):" >> simple_main.py
echo "    try:" >> simple_main.py
echo "        params = {\"function\": \"TIME_SERIES_DAILY\", \"symbol\": symbol, \"apikey\": \"X9GC2MV7P1GCODRZ\", \"outputsize\": outputsize}" >> simple_main.py
echo "        response = requests.get(\"https://www.alphavantage.co/query\", params=params, timeout=10)" >> simple_main.py
echo "        data = response.json()" >> simple_main.py
echo "        if \"Time Series (Daily)\" in data:" >> simple_main.py
echo "            time_series = data[\"Time Series (Daily)\"]" >> simple_main.py
echo "            return {\"success\": True, \"symbol\": symbol, \"interval\": \"daily\", \"data\": time_series}" >> simple_main.py
echo "        return {\"success\": False, \"error\": \"No data available\"}" >> simple_main.py
echo "    except Exception as e:" >> simple_main.py
echo "        return {\"success\": False, \"error\": str(e)}" >> simple_main.py

# 添加Yahoo Finance日线数据接口
echo "" >> simple_main.py
echo "@app.get(\"/api/market/yahoo/daily\")" >> simple_main.py
echo "async def get_yahoo_daily(symbol: str, period: str = \"1mo\"):" >> simple_main.py
echo "    try:" >> simple_main.py
echo "        ticker = yf.Ticker(symbol)" >> simple_main.py
echo "        hist = ticker.history(period=period)" >> simple_main.py
echo "        if not hist.empty:" >> simple_main.py
echo "            data_list = []" >> simple_main.py
echo "            for index, row in hist.iterrows():" >> simple_main.py
echo "                data_list.append({\"date\": index.strftime(\"%Y-%m-%d\"), \"open\": float(row['Open']), \"high\": float(row['High']), \"low\": float(row['Low']), \"close\": float(row['Close']), \"volume\": int(row['Volume'])})" >> simple_main.py
echo "            return {\"success\": True, \"symbol\": symbol, \"period\": period, \"data\": data_list}" >> simple_main.py
echo "        return {\"success\": False, \"error\": \"No data available\"}" >> simple_main.py
echo "    except Exception as e:" >> simple_main.py
echo "        return {\"success\": False, \"error\": str(e)}" >> simple_main.py

# 添加技术指标接口
echo "" >> simple_main.py
echo "@app.get(\"/api/indicators/sma\")" >> simple_main.py
echo "async def calculate_sma(symbol: str, period: int = 20):" >> simple_main.py
echo "    try:" >> simple_main.py
echo "        ticker = yf.Ticker(symbol)" >> simple_main.py
echo "        hist = ticker.history(period=\"3mo\")" >> simple_main.py
echo "        if not hist.empty:" >> simple_main.py
echo "            closes = hist['Close'].tolist()" >> simple_main.py
echo "            sma_values = []" >> simple_main.py
echo "            for i in range(len(closes)):" >> simple_main.py
echo "                if i >= period:" >> simple_main.py
echo "                    window = closes[i-period:i]" >> simple_main.py
echo "                    ma = sum(window) / period" >> simple_main.py
echo "                else:" >> simple_main.py
echo "                    ma = None" >> simple_main.py
echo "                sma_values.append(ma)" >> simple_main.py
echo "            return {\"success\": True, \"symbol\": symbol, \"period\": period, \"sma\": sma_values}" >> simple_main.py
echo "        return {\"success\": False, \"error\": \"No data available\"}" >> simple_main.py
echo "    except Exception as e:" >> simple_main.py
echo "        return {\"success\": False, \"error\": str(e)}" >> simple_main.py

echo "" >> simple_main.py
echo "@app.get(\"/api/indicators/ema\")" >> simple_main.py
echo "async def calculate_ema(symbol: str, period: int = 20):" >> simple_main.py
echo "    try:" >> simple_main.py
echo "        ticker = yf.Ticker(symbol)" >> simple_main.py
echo "        hist = ticker.history(period=\"3mo\")" >> simple_main.py
echo "        if not hist.empty:" >> simple_main.py
echo "            closes = hist['Close'].tolist()" >> simple_main.py
echo "            multiplier = 2 / (period + 1)" >> simple_main.py
echo "            ema_values = []" >> simple_main.py
echo "            ema = closes[0]" >> simple_main.py
echo "            ema_values.append(ema)" >> simple_main.py
echo "            for price in closes[1:]:" >> simple_main.py
echo "                ema = (price - ema) * multiplier + ema" >> simple_main.py
echo "                ema_values.append(ema)" >> simple_main.py
echo "            return {\"success\": True, \"symbol\": symbol, \"period\": period, \"ema\": ema_values}" >> simple_main.py
echo "        return {\"success\": False, \"error\": \"No data available\"}" >> simple_main.py
echo "    except Exception as e:" >> simple_main.py
echo "        return {\"success\": False, \"error\": str(e)}" >> simple_main.py

echo "" >> simple_main.py
echo "@app.get(\"/api/indicators/rsi\")" >> simple_main.py
echo "async def calculate_rsi(symbol: str, period: int = 14):" >> simple_main.py
echo "    try:" >> simple_main.py
echo "        ticker = yf.Ticker(symbol)" >> simple_main.py
echo "        hist = ticker.history(period=\"6mo\")" >> simple_main.py
echo "        if not hist.empty:" >> simple_main.py
echo "            closes = hist['Close'].tolist()" >> simple_main.py
echo "            deltas = []" >> simple_main.py
echo "            for i in range(1, len(closes)):" >> simple_main.py
echo "                deltas.append(closes[i] - closes[i-1])" >> simple_main.py
echo "            gains = []" >> simple_main.py
echo "            losses = []" >> simple_main.py
echo "            for delta in deltas:" >> simple_main.py
echo "                if delta > 0:" >> simple_main.py
echo "                    gains.append(delta)" >> simple_main.py
echo "                    losses.append(0)" >> simple_main.py
echo "                else:" >> simple_main.py
echo "                    gains.append(0)" >> simple_main.py
echo "                    losses.append(abs(delta))" >> simple_main.py
echo "            avg_gains = sum(gains[-period:]) / period" >> simple_main.py
echo "            avg_losses = sum(losses[-period:]) / period" >> simple_main.py
echo "            if avg_losses == 0:" >> simple_main.py
echo "                rs = 100" >> simple_main.py
echo "            else:" >> simple_main.py
echo "                rs = avg_gains / avg_losses" >> simple_main.py
echo "                rs = 100 - (100 / (1 + rs))" >> simple_main.py
echo "            rsi_values = []" >> simple_main.py
echo "            for delta in deltas:" >> simple_main.py
echo "                if delta > 0:" >> simple_main.py
echo "                    avg_gains = ((avg_gains * (period - 1)) + delta) / period" >> simple_main.py
echo "                else:" >> simple_main.py
echo "                    avg_losses = ((avg_losses * (period - 1)) + abs(delta)) / period" >> simple_main.py
echo "                if avg_losses == 0:" >> simple_main.py
echo "                    rs = 100" >> simple_main.py
echo "                else:" >> simple_main.py
echo "                    rs = avg_gains / avg_losses" >> simple_main.py
echo "                    rs = 100 - (100 / (1 + rs))" >> simple_main.py
echo "                rsi_values.append(rs)" >> simple_main.py
echo "            return {\"success\": True, \"symbol\": symbol, \"period\": period, \"rsi\": rsi_values}" >> simple_main.py
echo "        return {\"success\": False, \"error\": \"No data available\"}" >> simple_main.py
echo "    except Exception as e:" >> simple_main.py
echo "        return {\"success\": False, \"error\": str(e)}" >> simple_main.py

success "后端API接口添加完成"

# ===========================================
# 步骤2：重启后端服务
# ===========================================

echo ""
echo "=========================================="
echo "  步骤2/5: 重启后端服务"
echo "=========================================="
echo ""

pkill -f uvicorn
sleep 2

cd /var/www/ntdf/backend
source ~/.nvm/nvm.sh
nvm use 20
python3 -m uvicorn simple_main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

sleep 5

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    success "后端服务启动成功 (PID: $BACKEND_PID)"
else
    error "后端服务启动失败"
    exit 1
fi

# ===========================================
# 步骤3：更新前端App.vue
# ===========================================

echo ""
echo "=========================================="
echo "  步骤3/5: 更新前端App.vue"
echo "=========================================="
echo ""

cd /var/www/ntdf/frontend/src

# 创建更新后的App.vue
cat > App.vue << 'EOFPPEVUE'
<template>
  <div id="app">
    <header style="padding: 20px; background: #667eea; color: white;">
      <h1>NTDF 数字净量分析系统</h1>
    </header>
    <main style="padding: 20px;">
      <div style="background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h2>系统状态</h2>
        <p v-if="status">状态: {{ status.status }}</p>
        <p v-if="status">时间: {{ status.timestamp }}</p>
        <p v-if="status">版本: {{ status.version }}</p>
      </div>
      <div style="background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h2>市场数据</h2>
        <input v-model="symbol" placeholder="输入股票代码 (如: IBM)" 
               style="padding: 10px; margin-right: 10px; width: 200px;" />
        <button @click="fetchQuote" style="padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 5px;">
          查询
        </button>
        <button @click="fetchDaily" style="padding: 10px 20px; background: #4caf50; color: white; border: none; border-radius: 5px; margin-left: 10px;">
          日线数据
        </button>
        <div v-if="quote" style="margin-top: 20px;">
          <p>代码: {{ quote.symbol }}</p>
          <p>价格: {{ quote.price }}</p>
        </div>
        <div v-if="dailyData" style="margin-top: 20px;">
          <h3>日线数据</h3>
          <p v-for="(item, index) in dailyData.slice(-5)" :key="index">
            {{ item.date }}: 开盘={{ item.open }}, 收盘={{ item.close }}
          </p>
        </div>
      </div>
      <div style="background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h2>技术指标</h2>
        <div style="display: flex; gap: 10px;">
          <button @click="fetchSMA" style="padding: 10px 20px; background: #ff9800; color: white; border: none; border-radius: 5px;">
            SMA (20日)
          </button>
          <button @click="fetchEMA" style="padding: 10px 20px; background: #e91e63; color: white; border: none; border-radius: 5px;">
            EMA (20日)
          </button>
          <button @click="fetchRSI" style="padding: 10px 20px; background: #9c27b0; color: white; border: none; border-radius: 5px;">
            RSI (14日)
          </button>
        </div>
        <div v-if="indicators" style="margin-top: 20px;">
          <p>SMA最新值: {{ indicators.sma && indicators.sma.slice(-1)[0] }}</p>
          <p>EMA最新值: {{ indicators.ema && indicators.ema.slice(-1)[0] }}</p>
          <p>RSI最新值: {{ indicators.rsi && indicators.rsi.slice(-1)[0] }}</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const apiBase = 'http://122.51.142.248:8000'
const status = ref(null)
const quote = ref(null)
const dailyData = ref(null)
const indicators = ref(null)
const symbol = ref('IBM')

const fetchHealth = async () => {
  try {
    const response = await axios.get(`${apiBase}/health`)
    status.value = response.data
  } catch (error) {
    console.error(error)
  }
}

const fetchQuote = async () => {
  try {
    const response = await axios.get(`${apiBase}/api/market/alpha_vantage/quote`, {
      params: { symbol: symbol.value }
    })
    quote.value = response.data
  } catch (error) {
    alert('获取报价失败')
  }
}

const fetchDaily = async () => {
  try {
    const response = await axios.get(`${apiBase}/api/market/yahoo/daily`, {
      params: { symbol: symbol.value, period: '1mo' }
    })
    dailyData.value = response.data.data
  } catch (error) {
    alert('获取日线数据失败')
  }
}

const fetchSMA = async () => {
  try {
    const response = await axios.get(`${apiBase}/api/indicators/sma`, {
      params: { symbol: symbol.value, period: 20 }
    })
    indicators.value = response.data
  } catch (error) {
    alert('获取SMA失败')
  }
}

const fetchEMA = async () => {
  try {
    const response = await axios.get(`${apiBase}/api/indicators/ema`, {
      params: { symbol: symbol.value, period: 20 }
    })
    indicators.value = response.data
  } catch (error) {
    alert('获取EMA失败')
  }
}

const fetchRSI = async () => {
  try {
    const response = await axios.get(`${apiBase}/api/indicators/rsi`, {
      params: { symbol: symbol.value, period: 14 }
    })
    indicators.value = response.data
  } catch (error) {
    alert('获取RSI失败')
  }
}

onMounted(() => {
  fetchHealth()
})
</script>
EOFPPEVUE

success "前端App.vue更新完成"

# ===========================================
# 步骤4：重启前端服务
# ===========================================

echo ""
echo "=========================================="
echo "  步骤4/5: 重启前端服务"
echo "=========================================="
echo ""

cd /var/www/ntdf/frontend
source ~/.nvm/nvm.sh
nvm use 20

pkill -f "npm run dev"
sleep 2

npm run dev &
FRONTEND_PID=$!

sleep 5

success "前端服务重启完成"

# ===========================================
# 步骤5：测试系统
# ===========================================

echo ""
echo "=========================================="
echo "  步骤5/5: 测试系统"
echo "=========================================="
echo ""

# 测试后端健康检查
echo ""
echo "测试后端健康检查..."
BACKEND_HEALTH=$(curl -s http://localhost:8000/health)
echo "后端健康状态: $BACKEND_HEALTH"

# 测试Alpha Vantage报价
echo ""
echo "测试Alpha Vantage报价..."
AV_QUOTE=$(curl -s "http://localhost:8000/api/market/alpha_vantage/quote?symbol=IBM")
echo "Alpha Vantage报价: $AV_QUOTE"

# 测试Yahoo Finance日线数据
echo ""
echo "测试Yahoo Finance日线数据..."
YF_DAILY=$(curl -s "http://localhost:8000/api/market/yahoo/daily?symbol=IBM&period=1mo")
echo "Yahoo Finance日线: $YF_DAILY"

# 测试SMA指标
echo ""
echo "测试SMA指标..."
SMA_RESULT=$(curl -s "http://localhost:8000/api/indicators/sma?symbol=IBM&period=20")
echo "SMA指标: $SMA_RESULT"

# 测试EMA指标
echo ""
echo "测试EMA指标..."
EMA_RESULT=$(curl -s "http://localhost:8000/api/indicators/ema?symbol=IBM&period=20")
echo "EMA指标: $EMA_RESULT"

# 测试RSI指标
echo ""
echo "测试RSI指标..."
RSI_RESULT=$(curl -s "http://localhost:8000/api/indicators/rsi?symbol=IBM&period=14")
echo "RSI指标: $RSI_RESULT"

success "系统测试完成"

# ===========================================
# 总结
# ===========================================

echo ""
echo "=========================================="
echo "  部署完成！"
echo "=========================================="
echo ""

echo "🎯 系统访问地址："
echo "   前端: http://122.51.142.248:3001"
echo "   后端: http://122.51.142.248:8000"
echo "   健康检查: http://122.51.142.248:8000/health"
echo "   API文档: http://122.51.142.248:8000/docs"
echo ""

echo "📊 新增功能："
echo "   ✅ Alpha Vantage日线数据"
echo "   ✅ Yahoo Finance日线数据"
echo "   ✅ SMA技术指标"
echo "   ✅ EMA技术指标"
echo "   ✅ RSI技术指标"
echo "   ✅ 日线数据展示"
echo "   ✅ 技术指标展示"
echo ""

echo "🎉 卞董，恭喜您！"
echo "   NTDF系统MVP版本升级完成！"
echo "   现在可以查询日线数据和技术指标了！"
echo ""

echo "=========================================="
