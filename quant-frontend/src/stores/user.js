import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../utils/api'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value)
  
  // 用户角色相关计算属性
  const userRole = computed(() => userInfo.value?.role || 'viewer')
  const isAdmin = computed(() => userRole.value === 'admin')
  const isAnalyst = computed(() => userRole.value === 'analyst')
  const canCreateStrategy = computed(() => isAdmin.value || isAnalyst.value)

  // 初始化认证状态
  const initAuth = () => {
    if (token.value) {
      // 验证token有效性
      validateToken()
    }
  }

  // 验证token
  const validateToken = async () => {
    try {
      const response = await api.get('/auth/me')
      userInfo.value = response.data
    } catch (error) {
      logout()
    }
  }

  // 登录
  const login = async (credentials) => {
    loading.value = true
    try {
      const response = await api.post('/auth/login', credentials)
      const { token: newToken, user } = response.data
      
      token.value = newToken
      userInfo.value = user
      localStorage.setItem('token', newToken)
      
      ElMessage.success('登录成功')
      return true
    } catch (error) {
      ElMessage.error(error.response?.data?.message || '登录失败')
      return false
    } finally {
      loading.value = false
    }
  }

  // 注册
  const register = async (userData) => {
    loading.value = true
    try {
      const response = await api.post('/auth/register', userData)
      ElMessage.success('注册成功，请登录')
      return true
    } catch (error) {
      ElMessage.error(error.response?.data?.message || '注册失败')
      return false
    } finally {
      loading.value = false
    }
  }

  // 登出
  const logout = () => {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    ElMessage.success('已退出登录')
  }

  return {
    token,
    userInfo,
    loading,
    isAuthenticated,
    userRole,
    isAdmin,
    isAnalyst,
    canCreateStrategy,
    initAuth,
    login,
    register,
    logout
  }
})
