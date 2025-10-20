<template>
  <div class="report-viewer">
    <!-- 筛选条件表单 -->
    <el-card class="filter-card" v-if="filterableFields.length > 0">
      <template #header>
        <div class="card-header">
          <span>筛选条件</span>
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
              <el-input 
                v-model="filterForm[field.field_name]" 
                :placeholder="`请输入${field.display_name}`" 
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 报表数据表格 -->
    <el-card class="data-card">
      <template #header>
        <div class="card-header">
          <span>报表数据</span>
          <div>
            <el-button @click="handleRefresh" :loading="loading">刷新</el-button>
          </div>
        </div>
      </template>
      
      <el-table 
        :data="reportData.data" 
        stripe 
        style="width: 100%" 
        v-loading="loading"
      >
        <el-table-column 
          v-for="field in displayFields" 
          :key="field.field_name"
          :prop="field.field_name"
          :label="field.display_name"
        />
      </el-table>
      
      <!-- 分页 -->
      <el-pagination
        v-if="reportData.total > 0"
        layout="prev, pager, next, jumper, ->, total"
        :total="reportData.total"
        :page-size="reportData.page_size"
        :current-page="reportData.page"
        @current-change="handlePageChange"
        style="margin-top: 20px; text-align: right;"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useReportStore } from '../stores/report'

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

// 可筛选字段
const filterableFields = computed(() => {
  return props.report.fields?.filter(field => field.filterable) || []
})

// 显示字段
const displayFields = computed(() => {
  return props.report.fields || []
})

// 初始化筛选表单
const initFilterForm = () => {
  const form = {}
  filterableFields.value.forEach(field => {
    form[field.field_name] = ''
  })
  filterForm.value = form
}

// 查询数据
const fetchData = async (page = 1) => {
  if (!props.report) return
  
  loading.value = true
  try {
    const filters = {
      filters: { ...filterForm.value },
      page: page,
      page_size: reportData.value.page_size
    }
    
    console.log('查询参数:', filters);
    const result = await reportStore.fetchReportData(props.report.id, filters)
    reportData.value = result || { data: [], total: 0, page: 1, page_size: 20 }
  } catch (error) {
    console.error('获取报表数据失败:', error)
    reportData.value = { data: [], total: 0, page: 1, page_size: 20 }
  } finally {
    loading.value = false
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
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-form {
  margin-bottom: 10px;
}
</style>