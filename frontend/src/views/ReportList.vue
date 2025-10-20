<template>
  <div class="report-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>报表列表</span>
        </div>
      </template>
      
      <!-- 搜索栏 -->
      <el-form :model="searchForm" label-width="80px" class="search-form">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="报表名称">
              <el-input v-model="searchForm.name" placeholder="请输入报表名称" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="报表类型">
              <el-select v-model="searchForm.type" placeholder="请选择报表类型" clearable>
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
              <el-select v-model="searchForm.enable" placeholder="请选择启用状态" clearable>
                <el-option label="启用" :value="true" />
                <el-option label="禁用" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item>
              <el-button type="primary" @click="handleSearch">查询</el-button>
              <el-button @click="handleReset">重置</el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      
      <!-- 报表表格 -->
      <el-table :data="reportStore.reports" stripe style="width: 100%" v-loading="reportStore.loading">
        <el-table-column prop="name" label="报表名称" />
        <el-table-column prop="type" label="报表类型" />
        <el-table-column label="启用状态">
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
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="handleView(scope.row)">查看</el-button>
            <el-button size="small" type="primary" @click="handleConfig(scope.row)">配置</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 查看报表弹窗 -->
    <el-dialog v-model="dialogVisible" :title="currentReport?.name || '报表详情'" width="80%">
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
  return date.toLocaleString('zh-CN')
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
  // 跳转到配置页面
  console.log('配置报表:', report)
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
.search-form {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>