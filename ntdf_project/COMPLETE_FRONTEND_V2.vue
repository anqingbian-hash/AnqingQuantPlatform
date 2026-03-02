<template>
  <div id="app">
    <header style="padding: 20px; background: #667eea; color: white;">
      <h1>NTDF 数字净量分析系统 v2.0</h1>
    </header>
    <main style="padding: 20px;">
      <!-- 系统状态 -->
      <div style="background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h2>系统状态</h2>
        <p v-if="status">状态: {{ status.status }}</p>
        <p v-if="status">时间: {{ status.timestamp }}</p>
        <p v-if="status">版本: {{ status.version }}</p>
      </div>

      <!-- 市场数据 -->
      <div style="background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h2>市场数据</h2>
        <input v-model="symbol" placeholder="输入股票代码 (如: IBM)" 
               style="padding: 10px; margin-right: 10px; width: 200px;" />
        <button @click="fetchQuote" style="padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 5px;">
          查询报价
        </button>
        <button @click="fetchDaily" style="padding: 10px 20px; background: #4caf50; color: white; border: none; border-radius: 5px; margin-left: 10px;">
          查询日线
        </button>

        <div v-if="quote" style="margin-top: 20px;">
          <p>代码: {{ quote.symbol }}</p>
          <p>价格: {{ quote.price }}</p>
        </div>

        <div v-if="dailyData" style="margin-top: 20px;">
          <h3>日线数据</h3>
          <div v-for="(item, index) in dailyData.slice(-5)" :key="index">
            <p>{{ item.date }}: 开盘={{ item.open }}, 收盘={{ item.close }}</p>
          </div>
        </div>
      </div>

      <!-- 技术指标 -->
      <div style="background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h2>技术指标</h2>
        <div style="display: flex; gap: 10px; flex-wrap: wrap;">
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
