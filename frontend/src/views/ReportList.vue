<template>
  <div class="report-list">
    <el-card class="list-card">
      <template #header>
        <div class="card-header">
          <span>报表列表</span>
          <div class="header-actions">
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>查询
            </el-button>
            <el-button @click="handleReset">
              <el-icon><Refresh /></el-icon>重置
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 搜索栏 -->
      <el-form :model="searchForm" label-width="80px" class="search-form">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="报表名称">
              <el-input 
                v-model="searchForm.name" 
                placeholder="请输入报表名称" 
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="报表类型">
              <el-select 
                v-model="searchForm.type" 
                placeholder="请选择报表类型" 
                clearable
                filterable
              >
                <el-option
                  v-for="type in reportStore.reportTypes"
                  :key="type"
                  :label="type"
                  :value="type"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="启用状态">
              <el-select 
                v-model="searchForm.enable" 
                placeholder="请选择启用状态" 
                clearable
              >
                <el-option label="启用" :value="true" />
                <el-option label="禁用" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      
      <!-- 报表表格 -->
      <el-table 
        :data="reportStore.reports" 
        stripe 
        style="width: 100%" 
        v-loading="reportStore.loading"
        highlight-current-row
        class="report-table"
      >
        <el-table-column prop="name" label="报表名称" min-width="150">
          <template #default="scope">
            <span class="report-name">{{ scope.row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="报表类型" min-width="120" />
        <el-table-column label="启用状态" min-width="100">
          <template #default="scope">
            <el-tag :type="scope.row.enable ? 'success' : 'danger'">
              {{ scope.row.enable ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button 
              size="small" 
              type="primary" 
              plain 
              @click="handleView(scope.row)"
            >
              <el-icon><View /></el-icon>查看
            </el-button>
            <el-button 
              size="small" 
              type="warning" 
              plain 
              @click="handleConfig(scope.row)"
            >
              <el-icon><Setting /></el-icon>配置
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 查看报表弹窗 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="currentReport?.name || '报表详情'" 
      width="85%"
      top="5vh"
      class="report-dialog"
    >
      <report-viewer 
        v-if="currentReport" 
        :report="currentReport" 
        @refresh="handleRefreshReportData"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Refresh, View, Setting } from '@element-plus/icons-vue'
import { useReportStore } from '../stores/report'
import ReportViewer from '../components/ReportViewer.vue'

const router = useRouter()
const reportStore = useReportStore()

const searchForm = ref({
  name: '',
  type: '',
  enable: undefined
})

const dialogVisible = ref(false)
const currentReport = ref(null)

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 查询报表
const handleSearch = async () => {
  const params = {}
  if (searchForm.value.name) params.name = searchForm.value.name
  if (searchForm.value.type) params.type = searchForm.value.type
  if (searchForm.value.enable !== undefined) params.enable = searchForm.value.enable
  
  await reportStore.fetchReports(params)
}

// 重置查询
const handleReset = () => {
  searchForm.value = {
    name: '',
    type: '',
    enable: undefined
  }
  handleSearch()
}

// 查看报表
const handleView = async (report) => {
  const reportDetail = await reportStore.fetchReportDetail(report.id)
  currentReport.value = reportDetail
  dialogVisible.value = true
}

// 配置报表
const handleConfig = (report) => {
  router.push('/config')
}

// 刷新报表数据
const handleRefreshReportData = () => {
  if (currentReport.value) {
    reportStore.fetchReportDetail(currentReport.value.id)
  }
}

// 初始化加载
onMounted(() => {
  handleSearch()
})
</script>

<style scoped>
.report-list {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.list-card {
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  border: none;
  background-color: var(--card-background);
}

.search-form {
  margin-bottom: 20px;
  padding: 20px;
  background-color: var(--table-row-hover);
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-actions {
  display: flex;
  gap: 10px;
}

.report-name {
  font-weight: 500;
  color: var(--primary-color);
}

.report-dialog :deep(.el-dialog) {
  background-color: var(--card-background);
}

.report-dialog :deep(.el-dialog__body) {
  padding: 10px;
  height: 70vh;
}

.report-dialog :deep(.el-dialog__header) {
  padding: 15px 20px;
  background-color: var(--card-background);
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-color);
}

.report-table :deep(.el-table__body) {
  background-color: var(--card-background);
}

.report-table :deep(.el-table__row) {
  background-color: var(--card-background);
}

.search-form :deep(.el-input__wrapper) {
  background-color: var(--card-background);
}

.search-form :deep(.el-input__inner) {
  background-color: var(--card-background);
  color: var(--text-primary);
}

.search-form :deep(.el-select) {
  background-color: var(--card-background);
}

.search-form :deep(.el-select__wrapper) {
  background-color: var(--card-background);
}
</style>