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