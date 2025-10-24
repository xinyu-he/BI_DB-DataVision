<template>
  <div class="report-viewer">
    <!-- 筛选条件表单 -->
    <el-card class="filter-card" v-if="filterableFields.length > 0">
      <template #header>
        <div class="card-header">
          <span>筛选条件</span>
          <div class="filter-actions">
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>查询
            </el-button>
            <el-button @click="handleReset">
              <el-icon><Refresh /></el-icon>重置
            </el-button>
          </div>
        </div>
      </template>
      
      <el-form :model="filterForm" label-width="100px" class="filter-form">
        <el-row :gutter="20">
          <el-col 
            v-for="field in filterableFields" 
            :key="field.field_name" 
            :span="8"
          >
            <el-form-item :label="field.display_name">
              <!-- 根据字段类型显示不同的输入控件 -->
              <el-input 
                v-if="field.field_type === 'string' || field.field_type === undefined"
                v-model="filterForm[field.field_name]" 
                :placeholder="`请输入${field.display_name}`" 
                clearable
              />
              <el-input-number
                v-else-if="field.field_type === 'number'"
                v-model="filterForm[field.field_name]"
                :placeholder="`请输入${field.display_name}`"
                style="width: 100%"
                controls-position="right"
              />
              <el-date-picker
                v-else-if="field.field_type === 'date'"
                v-model="filterForm[field.field_name]"
                type="date"
                value-format="YYYY-MM-DD"
                :placeholder="`请选择${field.display_name}`"
                style="width: 100%"
              />
              <el-date-picker
                v-else-if="field.field_type === 'datetime'"
                v-model="filterForm[field.field_name]"
                type="datetime"
                value-format="YYYY-MM-DD HH:mm:ss"
                :placeholder="`请选择${field.display_name}`"
                style="width: 100%"
              />
              <!-- 日期范围选择器 -->
              <div v-else-if="field.field_type === 'date-range'" style="display: flex; gap: 10px;">
                <el-date-picker
                  v-model="filterForm[`${field.field_name}_start`]"
                  type="date"
                  value-format="YYYY-MM-DD"
                  :placeholder="`开始${field.display_name}`"
                  style="flex: 1;"
                />
                <span style="line-height: 32px;">-</span>
                <el-date-picker
                  v-model="filterForm[`${field.field_name}_end`]"
                  type="date"
                  value-format="YYYY-MM-DD"
                  :placeholder="`结束${field.display_name}`"
                  style="flex: 1;"
                />
              </div>
              <!-- 日期时间范围选择器 -->
              <div v-else-if="field.field_type === 'datetime-range'" style="display: flex; gap: 10px;">
                <el-date-picker
                  v-model="filterForm[`${field.field_name}_start`]"
                  type="datetime"
                  value-format="YYYY-MM-DD HH:mm:ss"
                  :placeholder="`开始${field.display_name}`"
                  style="flex: 1;"
                />
                <span style="line-height: 32px;">-</span>
                <el-date-picker
                  v-model="filterForm[`${field.field_name}_end`]"
                  type="datetime"
                  value-format="YYYY-MM-DD HH:mm:ss"
                  :placeholder="`结束${field.display_name}`"
                  style="flex: 1;"
                />
              </div>
              <el-select
                v-else-if="field.field_type === 'boolean'"
                v-model="filterForm[field.field_name]"
                :placeholder="`请选择${field.display_name}`"
                style="width: 100%"
                clearable
              >
                <el-option label="是" value="true" />
                <el-option label="否" value="false" />
              </el-select>
              <el-input
                v-else
                v-model="filterForm[field.field_name]" 
                :placeholder="`请输入${field.display_name}`" 
                clearable
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>
    
    <!-- 图表可视化 -->
    <ChartViewer 
      v-if="showChart && reportData.data.length > 0" 
      :report-data="reportData.data" 
      :fields="displayFields" 
    />
    
    <!-- 报表数据表格 -->
    <el-card class="data-card">
      <template #header>
        <div class="card-header">
          <span>报表数据</span>
          <div class="data-actions">
            <el-button @click="toggleChart" :type="showChart ? 'primary' : 'default'">
              <el-icon><Histogram /></el-icon>{{ showChart ? '隐藏图表' : '显示图表' }}
            </el-button>
            <el-button @click="handleExport" :loading="exportLoading" type="success">
              <el-icon><Download /></el-icon>{{ exportLoading ? '导出中...' : '导出Excel' }}
            </el-button>
            <el-button @click="handleRefresh" :loading="loading">
              <el-icon><Refresh /></el-icon>{{ loading ? '刷新中...' : '刷新' }}
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table 
        :data="reportData.data" 
        stripe 
        style="width: 100%" 
        v-loading="loading"
        highlight-current-row
        height="400"
        class="data-table"
      >
        <el-table-column 
          v-for="field in displayFields" 
          :key="field.field_name"
          :prop="field.field_name"
          :label="field.display_name"
          :min-width="120"
        >
          <template #default="scope">
            <!-- 根据字段类型格式化显示 -->
            <span v-if="field.field_type === 'date' && scope.row[field.field_name]">
              {{ formatDate(scope.row[field.field_name], 'date') }}
            </span>
            <span v-else-if="field.field_type === 'datetime' && scope.row[field.field_name]">
              {{ formatDate(scope.row[field.field_name], 'datetime') }}
            </span>
            <span v-else-if="field.field_type === 'number' && scope.row[field.field_name] !== null && scope.row[field.field_name] !== undefined">
              {{ formatNumber(scope.row[field.field_name]) }}
            </span>
            <span v-else-if="field.field_type === 'boolean'">
              {{ formatBoolean(scope.row[field.field_name]) }}
            </span>
            <span v-else>
              {{ scope.row[field.field_name] }}
            </span>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <el-pagination
        v-if="reportData.total > 0"
        layout="prev, pager, next, jumper, ->, total"
        :total="reportData.total"
        :page-size="reportData.page_size"
        :current-page="reportData.page"
        @current-change="handlePageChange"
        background
        class="pagination"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Search, Refresh, Download, Histogram } from '@element-plus/icons-vue'
import { useReportStore } from '../stores/report'
import ChartViewer from './ChartViewer.vue'

const props = defineProps({
  report: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['refresh'])

const reportStore = useReportStore()

const filterForm = ref({})
const reportData = ref({
  data: [],
  total: 0,
  page: 1,
  page_size: 20
})
const loading = ref(false)
const exportLoading = ref(false)
const showChart = ref(false)

// 可筛选字段
const filterableFields = computed(() => {
  return props.report.fields?.filter(field => field.filterable) || []
})

// 显示字段
const displayFields = computed(() => {
  return props.report.fields || []
})

// 格式化日期
const formatDate = (dateString, type = 'date') => {
  if (!dateString) return ''
  try {
    const date = new Date(dateString)
    if (type === 'date') {
      return date.toLocaleDateString('zh-CN')
    } else {
      return date.toLocaleString('zh-CN')
    }
  } catch (e) {
    return dateString
  }
}

// 格式化数字
const formatNumber = (value) => {
  if (value === null || value === undefined) return ''
  return Number(value).toLocaleString('zh-CN')
}

// 格式化布尔值
const formatBoolean = (value) => {
  if (value === true || value === 'true') return '是'
  if (value === false || value === 'false') return '否'
  return value
}

// 切换图表显示
const toggleChart = () => {
  showChart.value = !showChart.value
}

// 初始化筛选表单
const initFilterForm = () => {
  const form = {}
  filterableFields.value.forEach(field => {
    // 为范围查询字段添加开始和结束字段
    if (field.field_type === 'date-range' || field.field_type === 'datetime-range') {
      form[`${field.field_name}_start`] = ''
      form[`${field.field_name}_end`] = ''
    } else {
      form[field.field_name] = ''
    }
  })
  filterForm.value = form
}

// 查询数据
const fetchData = async (page = 1) => {
  if (!props.report) return
  
  loading.value = true
  try {
    // 处理筛选条件，特别是日期范围
    const processedFilters = {}
    for (const [key, value] of Object.entries(filterForm.value)) {
      // 查找字段类型
      const field = filterableFields.value.find(f => f.field_name === key || 
        key.startsWith(`${f.field_name}_`))
      
      if (field) {
        const fieldType = field.field_type
        
        // 处理日期范围
        if ((fieldType === 'date-range' || fieldType === 'datetime-range') && 
            (key.endsWith('_start') || key.endsWith('_end'))) {
          const baseFieldName = key.replace(/_(start|end)$/, '')
          const startValue = filterForm.value[`${baseFieldName}_start`]
          const endValue = filterForm.value[`${baseFieldName}_end`]
          
          if (startValue && endValue) {
            processedFilters[baseFieldName] = `${startValue}~${endValue}`
          } else if (startValue) {
            processedFilters[baseFieldName] = `${startValue}~`
          } else if (endValue) {
            processedFilters[baseFieldName] = `~${endValue}`
          }
        } else if (value !== '' && value !== null && value !== undefined) {
          processedFilters[key] = value
        }
      } else if (value !== '' && value !== null && value !== undefined) {
        // 处理非范围字段
        processedFilters[key] = value
      }
    }
    
    const filters = {
      filters: processedFilters,
      page: page,
      page_size: reportData.value.page_size
    }
    
    const result = await reportStore.fetchReportData(props.report.id, filters)
    reportData.value = result || { data: [], total: 0, page: 1, page_size: 20 }
  } catch (error) {
    console.error('获取报表数据失败:', error)
    reportData.value = { data: [], total: 0, page: 1, page_size: 20 }
  } finally {
    loading.value = false
  }
}

// 导出数据
const handleExport = async () => {
  if (!props.report) return
  
  exportLoading.value = true
  try {
    // 处理筛选条件，特别是日期范围
    const processedFilters = {}
    for (const [key, value] of Object.entries(filterForm.value)) {
      // 查找字段类型
      const field = filterableFields.value.find(f => f.field_name === key || 
        key.startsWith(`${f.field_name}_`))
      
      if (field) {
        const fieldType = field.field_type
        
        // 处理日期范围
        if ((fieldType === 'date-range' || fieldType === 'datetime-range') && 
            (key.endsWith('_start') || key.endsWith('_end'))) {
          const baseFieldName = key.replace(/_(start|end)$/, '')
          const startValue = filterForm.value[`${baseFieldName}_start`]
          const endValue = filterForm.value[`${baseFieldName}_end`]
          
          if (startValue && endValue) {
            processedFilters[baseFieldName] = `${startValue}~${endValue}`
          } else if (startValue) {
            processedFilters[baseFieldName] = `${startValue}~`
          } else if (endValue) {
            processedFilters[baseFieldName] = `~${endValue}`
          }
        } else if (value !== '' && value !== null && value !== undefined) {
          processedFilters[key] = value
        }
      } else if (value !== '' && value !== null && value !== undefined) {
        // 处理非范围字段
        processedFilters[key] = value
      }
    }
    
    const filters = {
      filters: processedFilters
    }
    
    await reportStore.exportReportData(props.report.id, filters)
  } catch (error) {
    console.error('导出报表数据失败:', error)
  } finally {
    exportLoading.value = false
  }
}

// 查询
const handleSearch = () => {
  fetchData(1)
}

// 重置
const handleReset = () => {
  initFilterForm()
  fetchData(1)
}

// 刷新
const handleRefresh = () => {
  fetchData(reportData.value.page)
  emit('refresh')
}

// 分页变化
const handlePageChange = (page) => {
  fetchData(page)
}

// 监听报表变化
watch(() => props.report, (newReport) => {
  if (newReport) {
    initFilterForm()
    fetchData(1)
  }
}, { immediate: true })

// 初始化
onMounted(() => {
  initFilterForm()
  fetchData(1)
})
</script>

<style scoped>
.report-viewer {
  height: 100%;
}

.filter-card {
  margin-bottom: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: none;
  background-color: var(--card-background);
}

.data-card {
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

.filter-form {
  margin-bottom: 10px;
  padding: 15px 0;
}

.filter-form :deep(.el-form-item__label) {
  color: var(--text-primary);
}

.filter-actions, .data-actions {
  display: flex;
  gap: 10px;
}

.pagination {
  margin-top: 20px;
  padding: 15px 0;
  display: flex;
  justify-content: flex-end;
}

.pagination :deep(.el-pagination__ jumper) {
  margin-left: 20px;
}

.data-table :deep(.el-table__body) {
  background-color: var(--card-background);
}

.data-table :deep(.el-table__row) {
  background-color: var(--card-background);
}

.filter-form :deep(.el-input__wrapper) {
  background-color: var(--card-background);
}

.filter-form :deep(.el-input__inner) {
  background-color: var(--card-background);
  color: var(--text-primary);
}

.filter-form :deep(.el-select) {
  background-color: var(--card-background);
}

.filter-form :deep(.el-select__wrapper) {
  background-color: var(--card-background);
}

.filter-form :deep(.el-date-editor) {
  background-color: var(--card-background);
}

.filter-form :deep(.el-date-editor .el-input__wrapper) {
  background-color: var(--card-background);
}
</style>