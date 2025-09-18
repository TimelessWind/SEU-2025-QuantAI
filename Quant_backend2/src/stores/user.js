import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || '')
  const loading = ref(false)

  const isLoggedIn = computed(() => !!token.value && !!user.value)

  // 登录
  const login = async (credentials) => {
    try {
      loading.value = true
      const response = await api.post('/auth/login', credentials)
      
      if (response.data.success) {
        token.value = response.data.token
        user.value = response.data.user
        localStorage.setItem('token', token.value)
        ElMessage.success('登录成功')
        return true
      } else {
        ElMessage.error(response.data.message || '登录失败')
        return false
      }
    } catch (error) {
      ElMessage.error('登录失败：' + (error.response?.data?.message || error.message))
      return false
    } finally {
      loading.value = false
    }
  }

  // 注册
  const register = async (userData) => {
    try {
      loading.value = true
      const response = await api.post('/auth/register', userData)
      
      if (response.data.success) {
        ElMessage.success('注册成功，请登录')
        return true
      } else {
        ElMessage.error(response.data.message || '注册失败')
        return false
      }
    } catch (error) {
      ElMessage.error('注册失败：' + (error.response?.data?.message || error.message))
      return false
    } finally {
      loading.value = false
    }
  }

  // 登出
  const logout = () => {
    user.value = null
    token.value = ''
    localStorage.removeItem('token')
    ElMessage.success('已退出登录')
  }

  // 检查认证状态
  const checkAuth = async () => {
    if (!token.value) return false
    
    try {
      const response = await api.get('/auth/me')
      if (response.data.success) {
        user.value = response.data.user
        return true
      } else {
        logout()
        return false
      }
    } catch (error) {
      logout()
      return false
    }
  }

  return {
    user,
    token,
    loading,
    isLoggedIn,
    login,
    register,
    logout,
    checkAuth
  }
})
