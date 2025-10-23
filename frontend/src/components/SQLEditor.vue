<template>
  <div class="sql-editor-container">
    <div ref="editorContainer" class="editor-container"></div>
    <div v-if="successMessage" class="success-message">
      <el-alert
        :title="successMessage"
        type="success"
        show-icon
        :closable="false"
      />
    </div>
    <div v-if="errorMessage" class="error-message">
      <el-alert
        :title="errorMessage"
        type="error"
        show-icon
        :closable="false"
      />
    </div>
    <div class="editor-actions" v-if="showActions">
      <el-button size="small" @click="formatSQL">格式化</el-button>
      <el-button size="small" @click="validateSQL" :loading="validating">校验SQL</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { basicSetup } from 'codemirror'
import { EditorView, keymap } from '@codemirror/view'
import { EditorState } from '@codemirror/state'
import { sql } from '@codemirror/lang-sql'
import { autocompletion, completeFromList } from '@codemirror/autocomplete'
import { defaultKeymap } from '@codemirror/commands'
import { ElAlert, ElButton, ElMessage } from 'element-plus'
import axios from 'axios'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  data_source: {
    type: String,
    default: 'main'
  },
  showActions: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue', 'validation'])

const editorContainer = ref(null)
const view = ref(null)
const errorMessage = ref('')
const successMessage = ref('')
const validating = ref(false)

// SQL关键字补全列表
const sqlKeywords = [
  'SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'NOT', 'IN', 'LIKE', 'BETWEEN',
  'IS', 'NULL', 'AS', 'ORDER', 'BY', 'GROUP', 'HAVING', 'LIMIT', 'OFFSET',
  'JOIN', 'INNER', 'LEFT', 'RIGHT', 'OUTER', 'ON', 'INSERT', 'UPDATE',
  'DELETE', 'CREATE', 'DROP', 'ALTER', 'TABLE', 'INDEX', 'VIEW', 'DATABASE',
  'PRIMARY', 'KEY', 'FOREIGN', 'REFERENCES', 'CONSTRAINT', 'UNIQUE',
  'DEFAULT', 'AUTO_INCREMENT', 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX',
  'DISTINCT', 'UNION', 'ALL', 'EXISTS', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END',
  'CAST', 'CONVERT', 'DATE', 'TIME', 'TIMESTAMP', 'VARCHAR', 'INT', 'INTEGER',
  'FLOAT', 'DOUBLE', 'DECIMAL', 'BOOLEAN', 'TRUE', 'FALSE'
].map(keyword => ({ label: keyword, type: 'keyword' }))

// 创建编辑器
const createEditor = () => {
  if (!editorContainer.value) return

  const startState = EditorState.create({
    doc: props.modelValue,
    extensions: [
      basicSetup,
      sql(),
      autocompletion({
        override: [
          completeFromList(sqlKeywords)
        ]
      }),
      keymap.of(defaultKeymap),
      EditorView.updateListener.of((update) => {
        if (update.docChanged) {
          const value = update.state.doc.toString()
          emit('update:modelValue', value)
          // 清除之前的错误信息和成功信息
          errorMessage.value = ''
          successMessage.value = ''
        }
      })
    ]
  })

  view.value = new EditorView({
    state: startState,
    parent: editorContainer.value
  })
}

// 格式化SQL
const formatSQL = () => {
  if (!view.value) return
  
  // 简单的SQL格式化（实际项目中可以使用更专业的库）
  let sqlText = view.value.state.doc.toString()
  sqlText = sqlText
    .replace(/\s+/g, ' ') // 将多个空格替换为单个空格
    .replace(/\s*([(),;])\s*/g, '$1 ') // 处理括号和分号
    .replace(/(\b(SELECT|FROM|WHERE|AND|OR|ORDER BY|GROUP BY|HAVING|LIMIT)\b)/gi, '\n$1') // 关键字换行
    .replace(/^\s+|\s+$/g, '') // 去除首尾空格
  
  view.value.dispatch({
    changes: {
      from: 0,
      to: view.value.state.doc.length,
      insert: sqlText
    }
  })
}

// 校验SQL
const validateSQL = async () => {
  if (!view.value) return
  
  const sqlText = view.value.state.doc.toString().trim()
  if (!sqlText) {
    errorMessage.value = 'SQL语句不能为空'
    return
  }
  
  // 基本检查：必须以SELECT开头
  if (!/^SELECT\b/i.test(sqlText)) {
    errorMessage.value = 'SQL语句必须以SELECT开头'
    return
  }
  
  validating.value = true
  errorMessage.value = ''
  successMessage.value = ''
  
  try {
    const response = await axios.post('/api/reports/validate-sql', {
      sql_text: sqlText,
      data_source: props.data_source
    })
    
    if (response.data.valid) {
      successMessage.value = 'SQL校验通过'
      emit('validation', { valid: true })
      // 3秒后自动清除成功消息
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
    } else {
      errorMessage.value = response.data.error || 'SQL校验失败'
      emit('validation', { valid: false, error: response.data.error })
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '校验SQL时发生错误'
    emit('validation', { valid: false, error: errorMessage.value })
  } finally {
    validating.value = false
  }
}

// 监听modelValue变化
watch(() => props.modelValue, (newValue) => {
  if (view.value) {
    const currentValue = view.value.state.doc.toString()
    if (newValue !== currentValue) {
      view.value.dispatch({
        changes: {
          from: 0,
          to: view.value.state.doc.length,
          insert: newValue || ''
        }
      })
    }
  }
})

// 监听数据源变化
watch(() => props.data_source, () => {
  // 数据源变化时清除错误信息
  errorMessage.value = ''
  successMessage.value = ''
})

onMounted(() => {
  nextTick(() => {
    createEditor()
  })
})

onBeforeUnmount(() => {
  if (view.value) {
    view.value.destroy()
  }
})

// 暴露方法给父组件
defineExpose({
  validateSQL
})
</script>

<style scoped>
.sql-editor-container {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  min-width: 800px; /* 与字段配置表格宽度保持一致 */
}

.editor-container {
  min-height: 200px;
  font-size: 14px;
}

.editor-container :deep(.cm-editor) {
  min-height: 200px;
  border: none;
  outline: none;
}

.editor-container :deep(.cm-scroller) {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.success-message,
.error-message {
  padding: 10px;
  border-top: 1px solid #dcdfe6;
}

.editor-actions {
  padding: 10px;
  border-top: 1px solid #dcdfe6;
  text-align: right;
  background-color: #f5f7fa;
}
</style>