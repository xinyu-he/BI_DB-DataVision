<template>
  <div class="home">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>报表配置与展示系统</span>
        </div>
      </template>
      
      <div class="welcome-content">
        <h2>欢迎使用报表配置与展示系统</h2>
        <p>本系统支持动态报表配置与展示，您可以：</p>
        
        <el-row :gutter="20" class="features">
          <el-col :span="12">
            <el-card class="feature-card">
              <div class="feature-content">
                <h3>报表配置</h3>
                <p>管理员可以配置报表SQL、展示字段、可筛选字段等</p>
                <el-button type="primary" @click="goToConfig">前往配置</el-button>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="feature-card">
              <div class="feature-content">
                <h3>报表展示</h3>
                <p>用户可以查看已配置的报表，支持筛选和分页</p>
                <el-button type="primary" @click="goToList">查看报表</el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
        
        <div class="theme-tip">
          <p>💡 使用右上角的切换按钮可以切换浅色/深色主题</p>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goToConfig = () => {
  router.push('/config')
}

const goToList = () => {
  router.push('/reports')
}
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-content {
  text-align: center;
  padding: 20px;
}

.welcome-content h2 {
  color: var(--text-primary);
  margin-bottom: 10px;
}

.welcome-content p {
  color: var(--text-secondary);
  font-size: 16px;
  margin-bottom: 30px;
}

.features {
  margin-top: 30px;
}

.feature-card {
  height: 200px;
  background-color: var(--card-background);
  border: 1px solid var(--border-color);
  transition: transform 0.3s, box-shadow 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.feature-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.feature-content h3 {
  color: var(--text-primary);
  margin-bottom: 15px;
}

.feature-content p {
  color: var(--text-secondary);
  margin-bottom: 20px;
}

.theme-tip {
  margin-top: 40px;
  padding: 15px;
  background-color: var(--table-row-hover);
  border-radius: 8px;
  border-left: 4px solid var(--primary-color);
}

.theme-tip p {
  color: var(--text-secondary);
  margin: 0;
  font-size: 14px;
}
</style>