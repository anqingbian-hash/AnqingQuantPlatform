<template>
  <div class="chart-container">
    <div class="chart-header">
      <h3>{{ title }}</h3>
    </div>
    <div ref="chartRef" class="chart" style="width: 100%; height: 400px;"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

interface Props {
  title?: string
  symbol?: string
  data?: Array<{
    date: string
    open: number
    high: number
    low: number
    close: number
  }>
}

const props = withDefaults(defineProps<Props>(), {
  title: 'SR支撑压力',
  symbol: '',
  data: () => []
})

const chartRef = ref<HTMLDivElement>()
const chartInstance = ref<echarts.ECharts | null>(null)

// Calculate support and resistance levels
const calculateLevels = () => {
  if (!props.data.length) return null

  const closes = props.data.map(d => d.close)
  const highs = props.data.map(d => d.high)
  const lows = props.data.map(d => d.low)

  // Find peaks (resistance)
  const peaks: number[] = []
  for (let i = 2; i < highs.length - 2; i++) {
    if (highs[i] > highs[i-1] && highs[i] > highs[i-2] &&
        highs[i] > highs[i+1] && highs[i] > highs[i+2]) {
      peaks.push(highs[i])
    }
  }

  // Find valleys (support)
  const valleys: number[] = []
  for (let i = 2; i < lows.length - 2; i++) {
    if (lows[i] < lows[i-1] && lows[i] < lows[i-2] &&
        lows[i] < lows[i+1] && lows[i] < lows[i+2]) {
      valleys.push(lows[i])
    }
  }

  // Calculate average levels
  const resistance = peaks.length > 0
    ? peaks.reduce((a, b) => a + b, 0) / peaks.length
    : null

  const support = valleys.length > 0
    ? valleys.reduce((a, b) => a + b, 0) / valleys.length
    : null

  // Calculate golden ratio levels
  let golden68 = null
  let golden32 = null

  if (resistance && support) {
    const range = resistance - support
    golden68 = support + (range * 0.32)
    golden32 = support + (range * 0.68)
  }

  return {
    resistance,
    support,
    golden68,
    golden32,
    currentPrice: closes[closes.length - 1]
  }
}

const initChart = () => {
  if (!chartRef.value) return

  chartInstance.value = echarts.init(chartRef.value)
  updateChart()
}

const updateChart = () => {
  if (!chartInstance.value) return

  const levels = calculateLevels()

  if (!levels) {
    return
  }

  const dates = props.data.map(d => d.date)
  const values = props.data.map(d => d.close)

  const markLineData: any[] = []

  if (levels.resistance) {
    markLineData.push({
      name: '压力位',
      yAxis: levels.resistance,
      lineStyle: { color: '#ef5350', width: 2, type: 'solid' }
    })
  }

  if (levels.support) {
    markLineData.push({
      name: '支撑位',
      yAxis: levels.support,
      lineStyle: { color: '#26a69a', width: 2, type: 'solid' }
    })
  }

  if (levels.golden68) {
    markLineData.push({
      name: '黄金率68%',
      yAxis: levels.golden68,
      lineStyle: { color: '#ffd54f', width: 2, type: 'dashed' }
    })
  }

  if (levels.golden32) {
    markLineData.push({
      name: '黄金率32%',
      yAxis: levels.golden32,
      lineStyle: { color: '#4dd0e1', width: 2, type: 'dashed' }
    })
  }

  const option = {
    title: {
      text: props.title,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['价格', '压力位', '支撑位', '黄金率68%', '黄金率32%'],
      top: 30
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      scale: true,
      boundaryGap: false
    },
    yAxis: {
      type: 'value',
      scale: true
    },
    series: [
      {
        name: '价格',
        type: 'line',
        data: values,
        smooth: true,
        lineStyle: { width: 2 },
        markLine: {
          data: markLineData,
          symbol: ['none', 'none'],
          label: {
            show: true,
            position: 'end',
            formatter: '{b}'
          }
        }
      }
    ]
  }

  chartInstance.value.setOption(option)
}

const resizeChart = () => {
  if (chartInstance.value) {
    chartInstance.value.resize()
  }
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', resizeChart)
})

watch(() => props.data, () => {
  updateChart()
}, { deep: true })
</script>

<style scoped>
.chart-container {
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.chart-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.chart {
  margin-top: 20px;
}
</style>
