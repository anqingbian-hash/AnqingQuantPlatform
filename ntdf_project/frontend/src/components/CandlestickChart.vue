<template>
  <div class="chart-container">
    <div class="chart-header">
      <h3>{{ title }}</h3>
      <div class="chart-controls">
        <button @click="changePeriod('1mo')">1月</button>
        <button @click="changePeriod('3mo')">3月</button>
        <button @click="changePeriod('6mo')">6月</button>
        <button @click="changePeriod('1y')">1年</button>
      </div>
    </div>
    <div ref="chartRef" class="chart" style="width: 100%; height: 500px;"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

interface Props {
  symbol: string
  title?: string
  data?: Array<{
    date: string
    open: number
    high: number
    low: number
    close: number
    volume: number
  }>
}

const props = withDefaults(defineProps<Props>(), {
  title: 'K线图',
  data: () => []
})

const emit = defineEmits<{
  periodChange: [period: string]
}>()

const chartRef = ref<HTMLDivElement>()
const chartInstance = ref<echarts.ECharts | null>(null)
const period = ref('1mo')

const initChart = () => {
  if (!chartRef.value) return

  chartInstance.value = echarts.init(chartRef.value)
  updateChart()
}

const updateChart = () => {
  if (!chartInstance.value) return

  const dates = props.data.map(item => item.date)
  const values = props.data.map(item => [
    item.open,
    item.close,
    item.low,
    item.high
  ])
  const volumes = props.data.map(item => item.volume)

  const option = {
    title: {
      text: props.title,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['K线', '成交量'],
      top: 30
    },
    grid: [
      {
        left: '10%',
        right: '8%',
        top: '10%',
        height: '50%'
      },
      {
        left: '10%',
        right: '8%',
        top: '70%',
        height: '15%'
      }
    ],
    xAxis: [
      {
        type: 'category',
        data: dates,
        scale: true,
        boundaryGap: false,
        axisLine: { onZero: false },
        splitLine: { show: false },
        min: 'dataMin',
        max: 'dataMax'
      },
      {
        type: 'category',
        gridIndex: 1,
        data: dates,
        scale: true,
        boundaryGap: false,
        axisLine: { onZero: false },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        min: 'dataMin',
        max: 'dataMax'
      }
    ],
    yAxis: [
      {
        scale: true,
        splitArea: {
          show: true
        }
      },
      {
        scale: true,
        gridIndex: 1,
        splitNumber: 2,
        axisLabel: { show: false },
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { show: false }
      }
    ],
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1],
        start: 50,
        end: 100
      },
      {
        show: true,
        xAxisIndex: [0, 1],
        type: 'slider',
        top: '90%',
        start: 50,
        end: 100
      }
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: values,
        itemStyle: {
          color: '#ef5350',
          color0: '#26a69a',
          borderColor: '#ef5350',
          borderColor0: '#26a69a'
        }
      },
      {
        name: 'MA5',
        type: 'line',
        data: calculateMA(5, props.data),
        smooth: true,
        lineStyle: { opacity: 0.5 }
      },
      {
        name: 'MA10',
        type: 'line',
        data: calculateMA(10, props.data),
        smooth: true,
        lineStyle: { opacity: 0.5 }
      },
      {
        name: 'MA20',
        type: 'line',
        data: calculateMA(20, props.data),
        smooth: true,
        lineStyle: { opacity: 0.5 }
      },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: volumes,
        itemStyle: {
          color: (params: any) => {
            const dataIndex = params.dataIndex
            if (dataIndex === 0) return '#26a69a'
            if (values[dataIndex][1] >= values[dataIndex][0]) {
              return '#ef5350'
            }
            return '#26a69a'
          }
        }
      }
    ]
  }

  chartInstance.value.setOption(option)
}

const calculateMA = (dayCount: number, data: Props['data']) => {
  const result = []
  for (let i = 0, len = data.length; i < len; i++) {
    if (i < dayCount) {
      result.push('-')
      continue
    }
    let sum = 0
    for (let j = 0; j < dayCount; j++) {
      sum += data[i - j].close
    }
    result.push((sum / dayCount).toFixed(2))
  }
  return result
}

const changePeriod = (newPeriod: string) => {
  period.value = newPeriod
  emit('periodChange', newPeriod)
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

watch(() => props.symbol, () => {
  updateChart()
})
</script>

<style scoped>
.chart-container {
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.chart-controls {
  display: flex;
  gap: 10px;
}

.chart-controls button {
  padding: 5px 15px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 12px;
  transition: background 0.3s;
}

.chart-controls button:hover {
  background: #5568d3;
}

.chart {
  margin-top: 20px;
}
</style>
