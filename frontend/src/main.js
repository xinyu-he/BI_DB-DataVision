import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './assets/styles/global.css'
import './assets/styles/components.css'
import App from './App.vue'
import router from './router'

// 初始化主题
import { useThemeStore } from './stores/theme'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

// 初始化主题
const themeStore = useThemeStore()
themeStore.initTheme()

app.mount('#app')