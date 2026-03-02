<template>
  <div id="app">
    <header class="header">
      <h1>NTDF 数字净量分析系统</h1>
      <div class="header-info">
        <span v-if="status" :class="status.status">{{ status.status }}</span>
      </div>
    </header>

    <main class="main-content">
      <div class="dashboard">
        <!-- Health Check -->
        <div class="card">
          <h2>系统状态</h2>
          <div class="status-info" v-if="status">
            <p><strong>后端:</strong> {{ status.backend || '检查中...' }}</p>
            <p><strong>数据库:</strong> {{ status.database || '检查中...' }}</p>
            <p><strong>时间:</strong> {{ status.timestamp || '未知' }}</p>
          </div>
        </div>

        <!-- Market Data -->
        <div class="card">
          <h2>市场数据</h2>
          <div class="market-input">
            <input
              v-model="symbol"
              placeholder="输入股票代码 (如: AAPL)"
              @keyup.enter="fetchQuote"
            />
            <button @click="fetchQuote">查询</button>
          </div>

          <div class="market-data" v-if="quote">
            <p><strong>股票代码:</strong> {{ quote.symbol }}</p>
            <p v-if="quote.price"><strong>当前价格:</strong> {{ quote.price }}</p>
            <p v-if="quote.high"><strong>最高价:</strong> {{ quote.high }}</p>
            <p v-if="quote.low"><strong>最低价:</strong> {{ quote.low }}</p>
            <p v-if="quote.volume"><strong>成交量:</strong> {{ quote.volume }}</p>
          </div>
        </div>

        <!-- Technical Indicators -->
        <div class="card">
          <h2>技术指标</h2>
          <div class="indicator-buttons">
            <button @click="fetchSMA">SMA (20日)</button>
            <button @click="fetchEMA">EMA (20日)</button>
            <button @click="fetchRSI">RSI (14日)</button>
          </div>

          <div class="indicator-data" v-if="indicator">
            <p><strong>指标:</strong> {{ indicator.type }}</p>
            <p v-if="indicator.value"><strong>当前值:</strong> {{ indicator.value }}</p>
          </div>
        </div>
      </div>
    </main>

    <footer class="footer">
      <p>NTDF Digital Net Analysis System v1.0.0</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

const apiBase = 'http://122.51.142.248:8000'

interface HealthStatus {
  status: string
  backend?: string
  database?: string
  timestamp?: string
}

interface Quote {
  symbol: string
  price?: number
  high?: number
  low?: number
  volume?: number
  company?: string
}

interface Indicator {
  type: string
  value?: number
}

const status = ref<HealthStatus | null>(null)
const quote = ref<Quote | null>(null)
const indicator = ref<Indicator | null>(null)
const symbol = ref('AAPL')

// Fetch health status
const fetchHealth = async () => {
  try {
    const response = await axios.get(`${apiBase}/health`)
    status.value = response.data
  } catch (error) {
    console.error('Health check failed:', error)
    status.value = { status: 'error', timestamp: new Date().toISOString() }
  }
}

// Fetch market quote
const fetchQuote = async () => {
  try {
    // Try Alpha Vantage first
    const response = await axios.get(`${apiBase}/api/market/alpha_vantage/quote`, {
      params: { symbol: symbol.value }
    })
    quote.value = response.data
  } catch (error) {
    console.error('Failed to fetch quote:', error)
    alert('获取报价失败')
  }
}

// Fetch SMA
const fetchSMA = async () => {
  try {
    const response = await axios.get(`${apiBase}/api/indicators/sma`, {
      params: { symbol: symbol.value, period: 20 }
    })
    indicator.value = {
      type: 'SMA (20日)',
      value: response.data.current_sma
    }
  } catch (error) {
    console.error('Failed to fetch SMA:', error)
    alert('获取SMA失败')
  }
}

// Fetch EMA
const fetchEMA = async () => {
  try {
    const response = await axios.get(`${apiBase}/api/indicators/ema`, {
      params: { symbol: symbol.value, period: 20 }
    })
    indicator.value = {
      type: 'EMA (20日)',
      value: response.data.current_ema
    }
  } catch (error) {
    console.error('Failed to fetch EMA:', error)
    alert('获取EMA失败')
  }
}

// Fetch RSI
const fetchRSI = async () => {
  try {
    const response = await axios.get(`${apiBase}/api/indicators/rsi`, {
      params: { symbol: symbol.value, period: 14 }
    })
    indicator.value = {
      type: 'RSI (14日)',
      value: response.data.current_rsi
    }
  } catch (error) {
    console.error('Failed to fetch RSI:', error)
    alert('获取RSI失败')
  }
}

onMounted(() => {
  fetchHealth()
  setInterval(fetchHealth, 30000) // 每30秒检查一次
})
</script>

<style scoped>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  background: rgba(255, 255, 255, 0.95);
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h1 {
  margin: 0;
  color: #333;
  font-size: 24px;
}

.header-info .healthy {
  color: #4caf50;
  font-weight: bold;
}

.header-info .error {
  color: #f44336;
  font-weight: bold;
}

.main-content {
  flex: 1;
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.dashboard {
  display: grid;
  gap: 20px;
}

.card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.card h2 {
  margin-top: 0;
  color: #333;
  font-size: 18px;
  border-bottom: 2px solid #667eea;
  padding-bottom: 10px;
}

.market-input {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.market-input input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
}

.market-input button,
.indicator-buttons button {
  padding: 10px 20px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.market-input button:hover,
.indicator-buttons button:hover {
  background: #5568d3;
}

.market-data,
.indicator-data {
  margin-top: 15px;
}

.market-data p,
.indicator-data p {
  margin: 8px 0;
  color: #555;
}

.indicator-buttons {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.footer {
  background: rgba(255, 255, 255, 0.95);
  text-align: center;
  padding: 20px;
  color: #666;
  font-size: 14px;
}

.status-info p {
  margin: 8px 0;
  color: #555;
}
</style>
