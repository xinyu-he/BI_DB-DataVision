import { defineStore } from 'pinia'
import axios from 'axios'

const API_BASE = '/api'

export const useReportStore = defineStore('report', {
  state: () => ({
    reports: [],
    currentReport: null,
    reportData: [],
    loading: false,
    error: null
  }),

  getters: {
    enabledReports: (state) => state.reports.filter(report => report.enable),
    reportTypes: (state) => {
      const types = [...new Set(state.reports.map(report => report.type))]
      return types.filter(type => type)
    }
  },

  actions: {
    async fetchReports(params = {}) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.get(`${API_BASE}/reports`, { params })
        this.reports = response.data
      } catch (error) {
        this.error = error.message || '获取报表列表失败'
        console.error('获取报表列表失败:', error)
      } finally {
        this.loading = false
      }
    },

    async fetchReportDetail(id) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.get(`${API_BASE}/reports/${id}`)
        this.currentReport = response.data
        return response.data
      } catch (error) {
        this.error = error.message || '获取报表详情失败'
        console.error('获取报表详情失败:', error)
      } finally {
        this.loading = false
      }
    },

    async fetchReportData(id, filters = {}) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.post(`${API_BASE}/reports/${id}/data`, filters)
        this.reportData = response.data
        return response.data
      } catch (error) {
        this.error = error.message || '获取报表数据失败'
        console.error('获取报表数据失败:', error)
      } finally {
        this.loading = false
      }
    },

    async exportReportData(id, filters = {}) {
      this.loading = true
      this.error = null
      try {
        // 发送请求并下载文件
        const response = await axios.post(`${API_BASE}/reports/${id}/export`, filters, {
          responseType: 'blob' // 重要：设置响应类型为blob以处理文件下载
        })
        
        // 创建下载链接
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `报表_${id}.xlsx`) // 默认文件名
        document.body.appendChild(link)
        link.click()
        
        // 清理
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        return response.data
      } catch (error) {
        this.error = error.message || '导出报表数据失败'
        console.error('导出报表数据失败:', error)
      } finally {
        this.loading = false
      }
    },

    async createReport(reportData) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.post(`${API_BASE}/reports`, reportData)
        // 重新获取报表列表
        await this.fetchReports()
        return response.data
      } catch (error) {
        this.error = error.message || '创建报表失败'
        console.error('创建报表失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateReport(id, reportData) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.put(`${API_BASE}/reports/${id}`, reportData)
        // 重新获取报表列表
        await this.fetchReports()
        return response.data
      } catch (error) {
        this.error = error.message || '更新报表失败'
        console.error('更新报表失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteReport(id) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.delete(`${API_BASE}/reports/${id}`)
        // 重新获取报表列表
        await this.fetchReports()
        return response.data
      } catch (error) {
        this.error = error.message || '删除报表失败'
        console.error('删除报表失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})