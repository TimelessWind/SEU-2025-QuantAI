<template>
  <div class="home-container">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-left">
        <h1>量化交易选股系统</h1>
      </div>
      <div class="header-right">
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            <el-icon><User /></el-icon>
            {{ userStore.user?.user_account }}
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人资料</el-dropdown-item>
              <el-dropdown-item command="settings">系统设置</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <el-container class="main-container">
      <!-- 侧边栏 -->
      <el-aside width="250px" class="sidebar">
        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
          router
        >
          <el-menu-item index="/home">
            <el-icon><House /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/stock-filter">
            <el-icon><Filter /></el-icon>
            <span>股票筛选</span>
          </el-menu-item>
          <el-menu-item index="/strategy">
            <el-icon><TrendCharts /></el-icon>
            <span>策略管理</span>
          </el-menu-item>
          <el-menu-item index="/backtest">
            <el-icon><DataAnalysis /></el-icon>
            <span>回测分析</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区 -->
      <el-main class="main-content">
        <div class="welcome-section">
          <h2>欢迎使用量化交易选股系统</h2>
          <p>基于AI技术的智能选股平台，助您实现量化投资</p>
        </div>

        <!-- 功能卡片 -->
        <div class="feature-cards">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-card class="feature-card" @click="$router.push('/stock-filter')">
                <div class="card-icon">
                  <el-icon size="40"><Filter /></el-icon>
                </div>
                <h3>股票筛选</h3>
                <p>基于多维度指标筛选优质股票</p>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card class="feature-card" @click="$router.push('/strategy')">
                <div class="card-icon">
                  <el-icon size="40"><TrendCharts /></el-icon>
                </div>
                <h3>策略管理</h3>
                <p>创建和管理量化交易策略</p>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card class="feature-card" @click="$router.push('/backtest')">
                <div class="card-icon">
                  <el-icon size="40"><DataAnalysis /></el-icon>
                </div>
                <h3>回测分析</h3>
                <p>策略回测和性能分析</p>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <!-- 数据统计 -->
        <div class="stats-section">
          <h3>系统统计</h3>
          <el-row :gutter="20">
            <el-col :span="6">
              <el-statistic title="股票总数" :value="stats.totalStocks" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="策略数量" :value="stats.totalStrategies" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="今日信号" :value="stats.todaySignals" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="回测报告" :value="stats.totalReports" />
            </el-col>
          </el-row>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const activeMenu = ref('/home')

const stats = reactive({
  totalStocks: 0,
  totalStrategies: 0,
  todaySignals: 0,
  totalReports: 0
})

const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人资料功能开发中')
      break
    case 'settings':
      ElMessage.info('系统设置功能开发中')
      break
    case 'logout':
      userStore.logout()
      router.push('/login')
      break
  }
}

const loadStats = async () => {
  // 这里可以调用API获取统计数据
  // 暂时使用模拟数据
  stats.totalStocks = 4500
  stats.totalStrategies = 5
  stats.todaySignals = 23
  stats.totalReports = 12
}

onMounted(() => {
  activeMenu.value = route.path
  loadStats()
})
</script>

<style scoped>
.home-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-left h1 {
  color: #2c3e50;
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.main-container {
  flex: 1;
  height: calc(100vh - 60px);
}

.sidebar {
  background: #fff;
  border-right: 1px solid #e6e6e6;
}

.sidebar-menu {
  border: none;
  height: 100%;
}

.main-content {
  padding: 20px;
  background: #f5f7fa;
}

.welcome-section {
  text-align: center;
  margin-bottom: 30px;
  padding: 40px 0;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.welcome-section h2 {
  color: #2c3e50;
  margin-bottom: 10px;
  font-size: 28px;
}

.welcome-section p {
  color: #7f8c8d;
  font-size: 16px;
}

.feature-cards {
  margin-bottom: 30px;
}

.feature-card {
  cursor: pointer;
  transition: all 0.3s;
  text-align: center;
  padding: 30px 20px;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.card-icon {
  color: #409eff;
  margin-bottom: 15px;
}

.feature-card h3 {
  color: #2c3e50;
  margin-bottom: 10px;
  font-size: 18px;
}

.feature-card p {
  color: #7f8c8d;
  font-size: 14px;
}

.stats-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stats-section h3 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 18px;
}
</style>
