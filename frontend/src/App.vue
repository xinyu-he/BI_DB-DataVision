<template>
  <div id="app">
    <el-container>
      <el-header class="app-header">
        <div class="header-content">
          <div class="logo-section">
            <el-icon :size="24" color="#fff"><DataAnalysis /></el-icon>
            <h1 class="app-title">报表配置与展示系统</h1>
          </div>
          <el-menu
            :default-active="activeIndex"
            class="app-menu"
            mode="horizontal"
            @select="handleSelect"
            background-color="transparent"
            text-color="#fff"
            active-text-color="#ffd04b"
            :ellipsis="false"
          >
            <el-menu-item index="/">
              <el-icon><House /></el-icon>首页
            </el-menu-item>
            <el-menu-item index="/reports">
              <el-icon><Document /></el-icon>报表展示
            </el-menu-item>
            <el-menu-item index="/config">
              <el-icon><Setting /></el-icon>报表配置
            </el-menu-item>
            <el-menu-item class="theme-toggle-item">
              <el-switch
                v-model="isDark"
                inline-prompt
                :active-icon="Moon"
                :inactive-icon="Sunny"
                @change="toggleTheme"
                style="--el-switch-on-color: #444; --el-switch-off-color: #ddd;"
              />
            </el-menu-item>
          </el-menu>
        </div>
      </el-header>
      <el-main class="app-main">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
      <el-footer class="app-footer">
        <div class="footer-content">
          <p>© 2025 报表配置与展示系统 - xinyu.he</p>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useThemeStore } from './stores/theme'
import { House, Document, Setting, DataAnalysis, Sunny, Moon } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const themeStore = useThemeStore()
const activeIndex = ref(route.path)
const isDark = ref(false)

// 初始化主题
onMounted(() => {
  themeStore.initTheme()
  themeStore.watchSystemTheme()
  isDark.value = themeStore.isDark
})

watch(route, (to) => {
  activeIndex.value = to.path
})

const handleSelect = (key) => {
  router.push(key)
}

const toggleTheme = () => {
  themeStore.toggleTheme()
}
</script>

<style scoped>
#app {
  height: 100vh;
  background: var(--background-color);
}

.app-header {
  background: var(--header-background);
  color: white;
  padding: 0;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.15);
  position: relative;
  z-index: 100;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 30px;
  max-width: 1200px;
  margin: 0 auto;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.app-title {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: white;
}

.app-menu {
  background: transparent !important;
  border: none !important;
  display: flex !important;
  flex-wrap: nowrap;
}

.app-menu :deep(.el-menu-item) {
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: white !important;
  height: 60px !important;
  line-height: 60px !important;
  margin: 0 15px;
  padding: 0 10px;
}

.app-menu :deep(.el-menu-item:hover) {
  background-color: var(--menu-hover-bg) !important;
  color: white !important;
}

.app-menu :deep(.el-menu-item.is-active) {
  background-color: var(--menu-active-bg) !important;
  border-bottom: 2px solid #ffd04b !important; /* Indicators */
}

.theme-toggle-item {
  display: flex;
  align-items: center;
  margin-left: 20px !important;
}

.app-main {
  background: var(--background-color);
  padding: 20px;
  min-height: calc(100vh - 120px);
}

.app-footer {
  background-color: var(--footer-bg);
  padding: 20px 0;
  text-align: center;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
}

.footer-content p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
}
</style>