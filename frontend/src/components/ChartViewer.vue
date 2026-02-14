<template>
  <div class="chart-viewer">
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <span>数据图表</span>
          <div class="chart-controls">
            <el-select 
              v-model="chartType" 
              placeholder="选择图表类型" 
              size="small"
              @change="renderChart"
            >
              <el-option label="柱状图" value="bar" />
              <el-option label="折线图" value="line" />
              <el-option label="饼图" value="pie" />
              <el-option label="散点图" value="scatter" />
            </el-select>
            <el-select 
              v-model="xAxisField" 
              placeholder="选择X轴字段" 
              size="small"
              @change="renderChart"
            >
              <el-option 
                v-for="field in displayFields" 
                :key="field.field_name" 
                :label="field.display_name" 
                :value="field.field_name" 
              />
            </el-select>
            <el-select 
              v-model="yAxisField" 
              placeholder="选择Y轴字段" 
              size="small"
              @change="renderChart"
            >
              <el-option 
                v-for="field in numericFields" 
                :key="field.field_name" 
                :label="field.display_name" 
                :value="field.field_name" 
              />
            </el-select>
            <el-button @click="renderChart" size="small" type="primary">
              <el-icon><Refresh /></el-icon>刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <div v-if="!hasValidData" class="no-data">
        <el-empty description="暂无可用数据绘制图表" />
      </div>
      <div v-else ref="chartContainer" class="chart-container"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const props = defineProps({
  reportData: {
    type: Array,
    required: true
  },
  fields: {
    type: Array,
    required: true
  }
})

const chartContainer = ref(null)
const chartInstance = ref(null)
const chartType = ref('bar')
const xAxisField = ref('')
const yAxisField = ref('')

// 检查是否有有效数据
const hasValidData = computed(() => {
  return props.reportData && 
         props.reportData.length > 0 && 
         props.fields && 
         props.fields.length > 0 &&
         xAxisField.value &&
         yAxisField.value
})

// 显示字段
const displayFields = computed(() => {
  return props.fields || []
})

// 数字类型字段
const numericFields = computed(() => {
  return props.fields?.filter(field => field.field_type === 'number') || []
})

// 初始化字段选择
const initFieldSelection = () => {
  // 初始化X轴字段
  if (displayFields.value.length > 0) {
    // 如果还没有选择X轴字段，或者已选择的字段不存在于当前字段列表中
    if (!xAxisField.value || !displayFields.value.find(f => f.field_name === xAxisField.value)) {
      xAxisField.value = displayFields.value[0].field_name
    }
  } else {
    xAxisField.value = ''
  }
  
  // 初始化Y轴字段（必须是数字类型）
  if (numericFields.value.length > 0) {
    // 如果还没有选择Y轴字段，或者已选择的字段不存在于当前数字字段列表中
    if (!yAxisField.value || !numericFields.value.find(f => f.field_name === yAxisField.value)) {
      yAxisField.value = numericFields.value[0].field_name
    }
  } else {
    yAxisField.value = ''
  }
}

// 渲染图表
const renderChart = async () => {
  // 确保有有效数据
  if (!hasValidData.value || !chartContainer.value) {
    if (chartInstance.value) {
      chartInstance.value.clear()
    }
    return
  }
  
  // 等待DOM更新
  await nextTick()
  
  // 初始化ECharts实例
  if (!chartInstance.value) {
    chartInstance.value = echarts.init(chartContainer.value)
  }
  
  // 准备数据
  const xAxisData = []
  const seriesData = []
  
  props.reportData.forEach(item => {
    // 确保字段存在且有值
    if (item.hasOwnProperty(xAxisField.value) && item.hasOwnProperty(yAxisField.value)) {
      xAxisData.push(item[xAxisField.value])
      seriesData.push({
        name: item[xAxisField.value],
        value: item[yAxisField.value]
      })
    }
  })
  
  // 如果没有有效数据点，清空图表
  if (xAxisData.length === 0) {
    chartInstance.value.clear()
    return
  }
  
  // 图表配置
  const option = {
    title: {
      text: '报表数据图表',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: chartType.value === 'pie' ? 'shadow' : 'line'
      }
    },
    grid: chartType.value !== 'pie' ? {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    } : undefined,
    xAxis: chartType.value !== 'pie' ? {
      type: 'category',
      data: xAxisData,
      axisLabel: {
        rotate: 45
      }
    } : undefined,
    yAxis: chartType.value !== 'pie' ? {
      type: 'value'
    } : undefined,
    series: [{
      type: chartType.value,
      data: chartType.value === 'pie' ? seriesData : seriesData.map(item => item.value),
      emphasis: {
        focus: 'series'
      },
      label: {
        show: chartType.value === 'pie',
        position: 'outside'
      }
    }]
  }
  
  // 渲染图表
  chartInstance.value.setOption(option, true)
}

// 窗口大小改变时重置图表大小
const resizeChart = () => {
  if (chartInstance.value) {
    chartInstance.value.resize()
  }
}

// 监听数据变化
watch(() => [props.reportData, props.fields], () => {
  initFieldSelection()
  renderChart()
}, { deep: true, immediate: true })

// 监听图表类型、X轴、Y轴字段变化
watch([chartType, xAxisField, yAxisField], () => {
  renderChart()
})

// 组件挂载时初始化
onMounted(() => {
  initFieldSelection()
  window.addEventListener('resize', resizeChart)
})

// 组件卸载前清理
onBeforeUnmount(() => {
  if (chartInstance.value) {
    chartInstance.value.dispose()
  }
  window.removeEventListener('resize', resizeChart)
})
</script>

<style scoped>
.chart-viewer {
  margin-top: 20px;
}

.chart-card {
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: none;
  background-color: var(--card-background);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.chart-controls {
  display: flex;
  gap: 10px;
}

.chart-container {
  width: 100%;
  height: 400px;
}

.no-data {
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>