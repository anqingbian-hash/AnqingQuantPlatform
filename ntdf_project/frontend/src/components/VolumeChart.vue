<template>
  <div class="chart-container">
    <div class="chart-header">
      <h3>{{ title }}</h3>
    </div>
    <div ref="chartRef" class="chart" style="width: 100%; height: 300px;"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

interface Props {
  title?: string
  data?: number[]
}

const props = withDefaults(defineProps<Props>(), {
  title: '成交量图',
  data: () => []
})

const chartRef = ref<HTMLDivElement>()
const chartInstance = ref<echarts.ECharts | null>(null)

const initChart = () => {
  if (!chartRef.value) return

  chartInstance.value = echarts.init(chartRef.value)
  updateChart()
}

const updateChart = () => {
  if (!chartInstance.value || !props.data.length) return

  const colors = props.data.map((value, index) => {
    if (index === 0) return '#26a69a'
    return value >= props.data[index - 1] ? '#ef5350' : '#26a69a'
  })

  const option = {
    title: {
      text: props.title,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: props.data.map((_, index) => index + 1),
      axisLabel: {
        show: false
      }
    },
    yAxis: {
      type: 'value',
      scale: true
    },
    series: [
      {
        name: '成交量',
        type: 'bar',
        data: props.data,
        itemStyle: {
          color: (params: any) => colors[params.dataIndex]
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
