<template>
  <div class="report-config">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>报表配置</span>
          <el-button type="primary" @click="handleCreate">新建报表</el-button>
        </div>
      </template>
      
      <!-- 报表配置表格 -->
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
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 报表配置弹窗 -->
    <el-dialog v-model="dialogVisible" :title="editingReport ? '编辑报表' : '新建报表'" width="60%">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="报表名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入报表名称" />
        </el-form-item>
        <el-form-item label="报表类型" prop="type">
          <el-input v-model="form.type" placeholder="请输入报表类型" />
        </el-form-item>
        <el-form-item label="查询SQL" prop="sql_text">
          <el-input 
            v-model="form.sql_text" 
            type="textarea" 
            :rows="6" 
            placeholder="请输入查询SQL（仅支持SELECT语句）" 
          />
        </el-form-item>
        <el-form-item label="启用状态" prop="enable">
          <el-switch v-model="form.enable" />
        </el-form-item>
        <el-form-item label="数据源">
          <el-select v-model="form.data_source" placeholder="请选择数据源">
            <el-option label="主数据库" value="main" />
            <el-option label="业务数据库" value="business" />
            <el-option label="订单数据库" value="order" />
          </el-select>
        </el-form-item>
        
        <!-- 字段配置 -->
        <el-form-item label="字段配置">
          <div class="field-config-container">
            <el-table :data="form.fields" style="width: 100%; min-width: 700px;">
              <el-table-column label="字段名" width="150">
                <template #default="scope">
                  <el-input v-model="scope.row.field_name" placeholder="字段名" />
                </template>
              </el-table-column>
              <el-table-column label="显示名" width="150">
                <template #default="scope">
                  <el-input v-model="scope.row.display_name" placeholder="显示名" />
                </template>
              </el-table-column>
              <el-table-column label="可筛选" width="80" align="center">
                <template #default="scope">
                  <el-checkbox v-model="scope.row.filterable" />
                </template>
              </el-table-column>
              <el-table-column label="顺序" width="80" align="center">
                <template #default="scope">
                  <el-input-number v-model="scope.row.order" :min="0" controls-position="right" style="width: 70px;" />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="80" align="center">
                <template #default="scope">
                  <el-button @click="removeField(scope.$index)" type="danger" size="small">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <el-button @click="addField" style="margin-top: 10px">添加字段</el-button>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
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
  return date.toLocaleString('zh-CN')
}

// 添加字段
const addField = () => {
  form.value.fields.push({
    field_name: '',
    display_name: '',
    filterable: false,
    order: form.value.fields.length
  })
}

// 删除字段
const removeField = (index) => {
  form.value.fields.splice(index, 1)
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

// 初始化加载
onMounted(() => {
  reportStore.fetchReports()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-footer {
  text-align: right;
}

.field-config-container {
  max-height: 300px;
  overflow: auto;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}
</style>