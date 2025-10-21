<template>
  <div class="report-config">
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span>报表配置</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>新建报表
          </el-button>
        </div>
      </template>
      
      <!-- 报表配置表格 -->
      <el-table 
        :data="reportStore.reports" 
        stripe 
        style="width: 100%" 
        v-loading="reportStore.loading"
        highlight-current-row
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
              @click="handleEdit(scope.row)"
            >
              <el-icon><Edit /></el-icon>编辑
            </el-button>
            <el-button 
              size="small" 
              type="danger" 
              plain 
              @click="handleDelete(scope.row)"
            >
              <el-icon><Delete /></el-icon>删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 报表配置弹窗 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="editingReport ? '编辑报表' : '新建报表'" 
      width="65%"
      top="3vh"
      class="config-dialog"
      :before-close="handleBeforeClose"
    >
      <el-form 
        :model="form" 
        :rules="rules" 
        ref="formRef" 
        label-width="100px" 
        class="config-form"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="报表名称" prop="name">
              <el-input 
                v-model="form.name" 
                placeholder="请输入报表名称" 
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="报表类型" prop="type">
              <el-input 
                v-model="form.type" 
                placeholder="请输入报表类型" 
                clearable
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="查询SQL" prop="sql_text">
          <el-input 
            v-model="form.sql_text" 
            type="textarea" 
            :rows="6" 
            placeholder="请输入查询SQL（仅支持SELECT语句）" 
            class="sql-input"
          />
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="启用状态" prop="enable">
              <el-switch 
                v-model="form.enable" 
                active-text="启用" 
                inactive-text="禁用"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="数据源">
              <el-select 
                v-model="form.data_source" 
                placeholder="请选择数据源" 
                style="width: 100%"
              >
                <el-option label="主数据库" value="main" />
                <el-option label="业务数据库" value="business" />
                <el-option label="订单数据库" value="order" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- 字段配置 -->
        <el-form-item label="字段配置">
          <div class="field-config-container">
            <el-table 
              :data="form.fields" 
              style="width: 100%; min-width: 800px;"
              border
            >
              <el-table-column label="字段名" width="180">
                <template #default="scope">
                  <el-input 
                    v-model="scope.row.field_name" 
                    placeholder="字段名" 
                    clearable
                  />
                </template>
              </el-table-column>
              <el-table-column label="显示名" width="180">
                <template #default="scope">
                  <el-input 
                    v-model="scope.row.display_name" 
                    placeholder="显示名" 
                    clearable
                  />
                </template>
              </el-table-column>
              <el-table-column label="字段类型" width="120" align="center">
                <template #default="scope">
                  <el-select 
                    v-model="scope.row.field_type" 
                    placeholder="请选择类型"
                    style="width: 100%"
                  >
                    <el-option label="字符串" value="string" />
                    <el-option label="数字" value="number" />
                    <el-option label="日期" value="date" />
                    <el-option label="日期范围" value="date-range" />
                    <el-option label="时间" value="datetime" />
                    <el-option label="时间范围" value="datetime-range" />
                    <el-option label="布尔值" value="boolean" />
                  </el-select>
                </template>
              </el-table-column>
              <el-table-column label="可筛选" width="100" align="center">
                <template #default="scope">
                  <el-checkbox v-model="scope.row.filterable" />
                </template>
              </el-table-column>
              <el-table-column label="顺序" width="100" align="center">
                <template #default="scope">
                  <el-input-number 
                    v-model="scope.row.order" 
                    :min="0" 
                    controls-position="right" 
                    style="width: 80px;" 
                  />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100" align="center">
                <template #default="scope">
                  <el-button 
                    @click="removeField(scope.$index)" 
                    type="danger" 
                    size="small"
                    plain
                  >
                    <el-icon><Delete /></el-icon>删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <el-button 
            @click="addField" 
            type="primary" 
            plain 
            style="margin-top: 15px"
          >
            <el-icon><Plus /></el-icon>添加字段
          </el-button>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleCancel">取消</el-button>
          <el-button type="primary" @click="handleSubmit">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import { useReportStore } from '../stores/report'

const reportStore = useReportStore()

const dialogVisible = ref(false)
const editingReport = ref(null)
const formRef = ref(null)

const form = ref({
  name: '',
  type: '',
  sql_text: '',
  data_source: 'main',
  enable: true,
  fields: []
})

const rules = {
  name: [{ required: true, message: '请输入报表名称', trigger: 'blur' }],
  type: [{ required: true, message: '请输入报表类型', trigger: 'blur' }],
  sql_text: [{ required: true, message: '请输入查询SQL', trigger: 'blur' }]
}

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

// 添加字段
const addField = () => {
  form.value.fields.push({
    field_name: '',
    display_name: '',
    field_type: 'string',
    filterable: false,
    order: form.value.fields.length
  })
}

// 删除字段
const removeField = (index) => {
  ElMessageBox.confirm(
    '确定要删除这个字段吗？',
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    form.value.fields.splice(index, 1)
  }).catch(() => {
    // 取消删除
  })
}

// 新建报表
const handleCreate = () => {
  editingReport.value = null
  form.value = {
    name: '',
    type: '',
    sql_text: '',
    data_source: 'main',
    enable: true,
    fields: []
  }
  dialogVisible.value = true
}

// 编辑报表
const handleEdit = async (report) => {
  try {
    // 获取完整的报表详情（包含字段配置）
    const reportDetail = await reportStore.fetchReportDetail(report.id)
    editingReport.value = reportDetail
    form.value = {
      name: reportDetail.name,
      type: reportDetail.type,
      sql_text: reportDetail.sql_text,
      data_source: reportDetail.data_source || 'main',
      enable: reportDetail.enable,
      fields: reportDetail.fields ? [...reportDetail.fields] : []
    }
    dialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取报表详情失败: ' + (error.message || '未知错误'))
  }
}

// 删除报表
const handleDelete = (report) => {
  ElMessageBox.confirm(
    `确定要删除报表 "${report.name}" 吗？`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await reportStore.deleteReport(report.id)
      ElMessage.success('删除成功')
    } catch (error) {
      ElMessage.error('删除失败: ' + (error.message || '未知错误'))
    }
  }).catch(() => {
    // 取消删除
  })
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    try {
      if (editingReport.value) {
        // 更新报表
        await reportStore.updateReport(editingReport.value.id, form.value)
        ElMessage.success('更新成功')
      } else {
        // 创建报表
        await reportStore.createReport(form.value)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
    } catch (error) {
      ElMessage.error('操作失败: ' + (error.message || '未知错误'))
    }
  })
}

// 取消操作
const handleCancel = () => {
  ElMessageBox.confirm(
    '确定要取消操作吗？未保存的数据将会丢失',
    '确认取消',
    {
      confirmButtonText: '确定',
      cancelButtonText: '继续编辑',
      type: 'warning'
    }
  ).then(() => {
    dialogVisible.value = false
  }).catch(() => {
    // 继续编辑
  })
}

// 关闭前确认
const handleBeforeClose = (done) => {
  ElMessageBox.confirm(
    '确定要关闭吗？未保存的数据将会丢失',
    '确认关闭',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    done()
  }).catch(() => {
    // 取消关闭
  })
}

// 初始化加载
onMounted(() => {
  reportStore.fetchReports()
})
</script>

<style scoped>
.report-config {
  padding: 20px;
}

.config-card {
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  border: none;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: 600;
}

.dialog-footer {
  text-align: right;
}

.field-config-container {
  max-height: 300px;
  overflow: auto;
  border-radius: 8px;
}

.sql-input :deep(.el-textarea__inner) {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.5;
}

.report-name {
  font-weight: 500;
  color: #409eff;
}

.config-dialog :deep(.el-dialog__body) {
  padding: 20px;
}

.config-form {
  padding: 10px 0;
}
</style>