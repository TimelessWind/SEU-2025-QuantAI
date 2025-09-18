<template>
  <div class="register-container">
    <div class="register-wrapper">
      <div class="register-form">
        <div class="register-header">
          <h1 class="register-title">创建账号</h1>
          <p class="register-subtitle">加入量化交易选股系统</p>
        </div>
        
        <el-form
          ref="registerFormRef"
          :model="registerForm"
          :rules="registerRules"
          class="form"
          size="large"
        >
          <el-form-item prop="account">
            <el-input
              v-model="registerForm.account"
              placeholder="请输入账号"
              prefix-icon="User"
              clearable
            />
          </el-form-item>
          
          <el-form-item prop="email">
            <el-input
              v-model="registerForm.email"
              placeholder="请输入邮箱"
              prefix-icon="Message"
              clearable
            />
          </el-form-item>
          
          <el-form-item prop="phone">
            <el-input
              v-model="registerForm.phone"
              placeholder="请输入手机号"
              prefix-icon="Phone"
              clearable
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input
              v-model="registerForm.password"
              type="password"
              placeholder="请输入密码"
              prefix-icon="Lock"
              show-password
              clearable
            />
          </el-form-item>
          
          <el-form-item prop="confirmPassword">
            <el-input
              v-model="registerForm.confirmPassword"
              type="password"
              placeholder="请确认密码"
              prefix-icon="Lock"
              show-password
              clearable
            />
          </el-form-item>
          
          <el-form-item prop="role">
            <el-select
              v-model="registerForm.role"
              placeholder="请选择角色"
              style="width: 100%"
            >
              <el-option label="管理员" value="admin" />
              <el-option label="分析师" value="analyst" />
              <el-option label="普通用户" value="viewer" />
            </el-select>
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="userStore.loading"
              @click="handleRegister"
              class="register-button"
            >
              注册
            </el-button>
          </el-form-item>
        </el-form>
        
        <div class="register-footer">
          <el-link @click="$router.push('/login')" type="primary">
            已有账号？立即登录
          </el-link>
        </div>
      </div>
      
      <div class="register-banner">
        <div class="banner-content">
          <h2>开启智能投资之旅</h2>
          <div class="benefit-list">
            <div class="benefit-item">
              <el-icon><Star /></el-icon>
              <div>
                <h3>专业分析</h3>
                <p>基于大数据和AI算法的智能选股</p>
              </div>
            </div>
            <div class="benefit-item">
              <el-icon><Shield /></el-icon>
              <div>
                <h3>风险控制</h3>
                <p>多维度风险评估和实时监控</p>
              </div>
            </div>
            <div class="benefit-item">
              <el-icon><TrendCharts /></el-icon>
              <div>
                <h3>策略回测</h3>
                <p>历史数据验证，提升投资成功率</p>
              </div>
            </div>
          </div>
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
const registerFormRef = ref()

const registerForm = reactive({
  account: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: '',
  role: 'viewer'
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const registerRules = {
  account: [
    { required: true, message: '请输入账号', trigger: 'blur' },
    { min: 3, max: 20, message: '账号长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      const { confirmPassword, ...userData } = registerForm
      const success = await userStore.register(userData)
      if (success) {
        router.push('/login')
      }
    }
  })
}
</script>

<style lang="scss" scoped>
.register-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.register-wrapper {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  max-width: 1000px;
  width: 100%;
  min-height: 700px;
}

.register-form {
  flex: 1;
  padding: 50px 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.register-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.register-subtitle {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0;
}

.form {
  .register-button {
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

.register-footer {
  text-align: center;
  margin-top: 20px;
}

.register-banner {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  padding: 50px 40px;
}

.banner-content {
  h2 {
    font-size: 26px;
    font-weight: 600;
    margin-bottom: 40px;
    text-align: center;
  }
}

.benefit-list {
  .benefit-item {
    display: flex;
    align-items: flex-start;
    margin-bottom: 30px;
    
    .el-icon {
      margin-right: 15px;
      font-size: 24px;
      margin-top: 5px;
    }
    
    h3 {
      font-size: 18px;
      font-weight: 600;
      margin-bottom: 8px;
    }
    
    p {
      font-size: 14px;
      opacity: 0.9;
      margin: 0;
      line-height: 1.5;
    }
  }
}

@media (max-width: 768px) {
  .register-wrapper {
    flex-direction: column;
    max-width: 400px;
  }
  
  .register-form {
    padding: 30px 25px;
  }
  
  .register-banner {
    padding: 30px 25px;
    
    h2 {
      font-size: 22px;
      margin-bottom: 30px;
    }
    
    .benefit-list .benefit-item {
      margin-bottom: 20px;
      
      h3 {
        font-size: 16px;
      }
      
      p {
        font-size: 13px;
      }
    }
  }
  
  .register-title {
    font-size: 24px;
  }
}
</style>


