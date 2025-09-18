<template>
  <div class="login-container">
    <div class="login-wrapper">
      <div class="login-form">
        <div class="login-header">
          <h1 class="login-title">量化交易选股系统</h1>
          <p class="login-subtitle">智能选股，科学投资</p>
        </div>
        
        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          class="form"
          size="large"
        >
          <el-form-item prop="account">
            <el-input
              v-model="loginForm.account"
              placeholder="请输入账号"
              prefix-icon="User"
              clearable
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              prefix-icon="Lock"
              show-password
              clearable
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="userStore.loading"
              @click="handleLogin"
              class="login-button"
            >
              登录
            </el-button>
          </el-form-item>
        </el-form>
        
        <div class="login-footer">
          <el-link @click="$router.push('/register')" type="primary">
            还没有账号？立即注册
          </el-link>
        </div>
      </div>
      
      <div class="login-banner">
        <div class="banner-content">
          <h2>专业的量化交易平台</h2>
          <ul class="feature-list">
            <li>
              <el-icon><TrendCharts /></el-icon>
              <span>智能股票筛选</span>
            </li>
            <li>
              <el-icon><DataAnalysis /></el-icon>
              <span>多维度数据分析</span>
            </li>
            <li>
              <el-icon><Monitor /></el-icon>
              <span>实时策略回测</span>
            </li>
            <li>
              <el-icon><Setting /></el-icon>
              <span>自定义策略配置</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const loginFormRef = ref()

const loginForm = reactive({
  account: '',
  password: ''
})

const loginRules = {
  account: [
    { required: true, message: '请输入账号', trigger: 'blur' },
    { min: 3, max: 20, message: '账号长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      const success = await userStore.login(loginForm)
      if (success) {
        router.push('/')
      }
    }
  })
}
</script>

<style lang="scss" scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-wrapper {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  max-width: 1000px;
  width: 100%;
  min-height: 600px;
}

.login-form {
  flex: 1;
  padding: 60px 50px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-title {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-subtitle {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0;
}

.form {
  .login-button {
    width: 100%;
    height: 50px;
    font-size: 16px;
    font-weight: 600;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    
    &:hover {
      background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
    }
  }
}

.login-footer {
  text-align: center;
  margin-top: 30px;
}

.login-banner {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  padding: 60px 50px;
}

.banner-content {
  text-align: center;
  
  h2 {
    font-size: 28px;
    font-weight: 600;
    margin-bottom: 40px;
  }
}

.feature-list {
  list-style: none;
  padding: 0;
  
  li {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
    font-size: 16px;
    
    .el-icon {
      margin-right: 15px;
      font-size: 20px;
    }
  }
}

@media (max-width: 768px) {
  .login-wrapper {
    flex-direction: column;
    max-width: 400px;
  }
  
  .login-form {
    padding: 40px 30px;
  }
  
  .login-banner {
    padding: 40px 30px;
    
    h2 {
      font-size: 24px;
      margin-bottom: 30px;
    }
    
    .feature-list li {
      font-size: 14px;
      margin-bottom: 15px;
    }
  }
  
  .login-title {
    font-size: 24px;
  }
}
</style>


