<template>
  <div class="backtest-container">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-left">
        <h1>回测分析</h1>
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
        <el-card>
          <template #header>
            <div class="card-header">
              <span>回测报告</span>
              <el-button type="primary" @click="handleNewBacktest">
                <el-icon><Plus /></el-icon>
                新建回测
              </el-button>
            </div>
          </template>

          <el-table :data="backtestReports" style="width: 100%" stripe>
            <el-table-column prop="strategyName" label="策略名称" width="150" />
            <el-table-column prop="stockCode" label="股票代码" width="120" />
            <el-table-column prop="startDate" label="开始日期" width="120" />
            <el-table-column prop="endDate" label="结束日期" width="120" />
            <el-table-column prop="totalReturn" label="总收益率" width="100">
              <template #default="scope">
                <span :class="scope.row.totalReturn >= 0 ? 'positive' : 'negative'">
                  {{ (scope.row.totalReturn * 100).toFixed(2) }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="annualReturn" label="年化收益率" width="120">
              <template #default="scope">
                <span :class="scope.row.annualReturn >= 0 ? 'positive' : 'negative'">
                  {{ (scope.row.annualReturn * 100).toFixed(2) }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="maxDrawdown" label="最大回撤" width="100">
              <template #default="scope">
                <span class="negative">
                  {{ (scope.row.maxDrawdown * 100).toFixed(2) }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="sharpeRatio" label="夏普比率" width="100" />
            <el-table-column prop="winRate" label="胜率" width="80">
              <template #default="scope">
                {{ (scope.row.winRate * 100).toFixed(1) }}%
              </template>
            </el-table-column>
            <el-table-column prop="reportStatus" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.reportStatus)">
                  {{ getStatusText(scope.row.reportStatus) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button type="primary" size="small" @click="handleView(scope.row)">
                  查看
                </el-button>
                <el-button type="success" size="small" @click="handleDownload(scope.row)">
                  下载
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const activeMenu = ref('/backtest')
const backtestReports = ref([])

const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人资料功能开发中')
      break
    case 'logout':
      userStore.logout()
      router.push('/login')
      break
  }
}

const handleNewBacktest = () => {
  ElMessage.info('新建回测功能开发中')
}

const handleView = (row) => {
  ElMessage.info(`查看回测报告：${row.strategyName}`)
}

const handleDownload = (row) => {
  ElMessage.info(`下载回测报告：${row.strategyName}`)
}

const getStatusType = (status) => {
  const statusMap = {
    'generating': 'warning',
    'completed': 'success',
    'failed': 'danger'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    'generating': '生成中',
    'completed': '已完成',
    'failed': '失败'
  }
  return statusMap[status] || '未知'
}

onMounted(() => {
  activeMenu.value = route.path
  
  // 尝试从localStorage获取最新回测结果
  const lastBacktestResult = localStorage.getItem('lastBacktestResult')
  
  if (lastBacktestResult) {
    try {
      const result = JSON.parse(lastBacktestResult)
      
      // 将最新回测结果添加到报告列表的开头
      const newReport = {
        strategyName: result.performance?.strategyName || result.report_id,
        stockCode: result.performance?.stockCode || 'N/A',
        startDate: '2024-01-01',
        endDate: '2024-12-31',
        totalReturn: result.performance?.total_return || 0,
        annualReturn: result.performance?.annual_return || 0,
        maxDrawdown: result.performance?.max_drawdown || 0,
        sharpeRatio: result.performance?.sharpe_ratio || 0,
        winRate: result.performance?.win_rate || 0,
        reportStatus: 'completed',
        reportId: result.report_id
      }
      
      backtestReports.value = [newReport, ...backtestReports.value]
      
      // 清除localStorage中的回测结果，避免重复加载
      localStorage.removeItem('lastBacktestResult')
    } catch (error) {
      console.error('解析回测结果失败:', error)
    }
  }
  
  // 如果没有最新回测结果或解析失败，加载模拟数据
  if (backtestReports.value.length === 0) {
    backtestReports.value = [
        {
          strategyName: '小市值策略',
          stockCode: '000001.SZ',
          startDate: '2024-01-01',
          endDate: '2024-06-30',
          totalReturn: 0.15,
          annualReturn: 0.32,
          maxDrawdown: -0.08,
          sharpeRatio: 1.2,
          winRate: 0.65,
          reportStatus: 'completed'
        },
        {
          strategyName: '双均线策略',
          stockCode: '000002.SZ',
          startDate: '2024-01-01',
          endDate: '2024-06-30',
          totalReturn: -0.05,
          annualReturn: -0.10,
          maxDrawdown: -0.15,
          sharpeRatio: -0.3,
          winRate: 0.45,
          reportStatus: 'completed'
        }
      ]
})
</script>

<style scoped>
.backtest-container {
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.positive {
  color: #67c23a;
  font-weight: bold;
}

.negative {
  color: #f56c6c;
  font-weight: bold;
}
</style>
