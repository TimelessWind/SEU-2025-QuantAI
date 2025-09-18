<template>
  <div class="strategy-container">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-left">
        <h1>策略管理</h1>
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
              <span>交易策略</span>
              <el-button type="primary" @click="window.open('/strategy_editor_frontend.html', '_blank')">
                <el-icon><Plus /></el-icon>
                创建策略
              </el-button>
            </div>
          </template>

          <el-table :data="strategies" style="width: 100%" stripe>
            <el-table-column prop="strategyName" label="策略名称" width="200" />
            <el-table-column prop="strategyType" label="类型" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.strategyType === 'builtin' ? 'success' : 'primary'">
                  {{ scope.row.strategyType === 'builtin' ? '内置' : '自定义' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="strategyDesc" label="策略描述" />
            <el-table-column prop="createTime" label="创建时间" width="180" />
            <el-table-column label="操作" width="200">
              <template #default="scope">
                <el-button type="primary" size="small" @click="handleEdit(scope.row)">
                  编辑
                </el-button>
                <el-button type="success" size="small" @click="handleBacktest(scope.row)">
                  回测
                </el-button>
                <el-button type="danger" size="small" @click="handleDelete(scope.row)">
                  删除
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

const activeMenu = ref('/strategy')
const strategies = ref([])

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

const handleCreateStrategy = () => {
  // 打开策略编辑器页面
  window.open('/strategy_editor_frontend.html', '_blank')
}

const handleEdit = (row) => {
  ElMessage.info(`编辑策略：${row.strategyName}`)
}

const handleBacktest = async (row) => {
  try {
    // 模拟获取回测参数
    const backtestParams = {
      stock_code: '600519.SH', // 示例股票代码，实际应用中可以让用户选择
      start_date: '2024-01-01',
      end_date: '2024-12-31',
      strategy_type: row.strategyType === 'builtin' ? 'moving_average' : row.strategyName.toLowerCase(),
      strategy_params: {},
      initial_capital: 100000.0,
      commission_rate: 0.001,
      user_id: userStore.user?.user_id || 'default_user',
      strategy_id: row.strategyName
    }
    
    // 显示加载提示
    ElMessage({ message: '回测开始，正在处理数据...', type: 'info' })
    
    // 调用后端回测API
    const response = await fetch('/api/backtest/run', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userStore.token}`
      },
      body: JSON.stringify(backtestParams)
    })
    
    const data = await response.json()
    
    if (data.success) {
      // 回测成功，跳转到回测结果页面或显示结果
      ElMessage({ message: '回测完成', type: 'success' })
      
      // 获取回测结果并存储到本地，以便在回测页面显示
      localStorage.setItem('lastBacktestResult', JSON.stringify(data.data))
      
      // 跳转到回测页面
      router.push('/backtest')
    } else {
      ElMessage({ message: `回测失败：${data.message}`, type: 'error' })
    }
  } catch (error) {
    console.error('回测请求失败:', error)
    ElMessage({ message: '回测请求失败，请检查网络连接', type: 'error' })
  }
}

const handleDelete = (row) => {
  ElMessage.info(`删除策略：${row.strategyName}`)
}

onMounted(() => {
  activeMenu.value = route.path
  // 加载策略数据
  strategies.value = [
    {
      strategyName: '小市值策略',
      strategyType: 'builtin',
      strategyDesc: '筛选出市值介于20-30亿的股票，选取其中市值最小的三只股票',
      createTime: '2024-01-01 10:00:00'
    },
    {
      strategyName: '双均线策略',
      strategyType: 'builtin',
      strategyDesc: '通过5日均线和价格的关系进行买卖',
      createTime: '2024-01-01 10:00:00'
    }
  ]
})
</script>

<style scoped>
.strategy-container {
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
</style>
