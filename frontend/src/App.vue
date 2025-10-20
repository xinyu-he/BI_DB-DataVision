<template>
  <div id="app">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>报表配置与展示系统</h1>
          <el-menu
            :default-active="activeIndex"
            class="el-menu-demo"
            mode="horizontal"
            @select="handleSelect"
            background-color="#409eff"
            text-color="#fff"
            active-text-color="#ffd04b"
          >
            <el-menu-item index="/"><el-icon><House /></el-icon>首页</el-menu-item>
            <el-menu-item index="/reports"><el-icon><Document /></el-icon>报表展示</el-menu-item>
            <el-menu-item index="/config"><el-icon><Setting /></el-icon>报表配置</el-menu-item>
          </el-menu>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { House, Document, Setting } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const activeIndex = ref(route.path)

watch(route, (to) => {
  activeIndex.value = to.path
})

const handleSelect = (key) => {
  router.push(key)
}
</script>

<style scoped>
#app {
  height: 100vh;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
}

.el-header {
  background-color: #409eff;
  color: white;
  text-align: center;
  line-height: 60px;
}

.el-main {
  background-color: #f5f5f5;
  padding: 20px;
}
</style>