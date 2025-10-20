import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import ReportList from '../views/ReportList.vue'
import ReportConfig from '../views/ReportConfig.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/reports',
    name: 'ReportList',
    component: ReportList
  },
  {
    path: '/config',
    name: 'ReportConfig',
    component: ReportConfig
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router