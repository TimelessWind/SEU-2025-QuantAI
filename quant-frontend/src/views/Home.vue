<template>
  <div class="home-container">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <div class="welcome-content">
        <h1 class="welcome-title">欢迎使用量化交易选股系统</h1>
        <p class="welcome-subtitle">基于AI和大数据的智能投资决策平台</p>
        <div class="welcome-stats">
          <div class="stat-item">
            <div class="stat-number">{{ stats.totalStocks }}</div>
            <div class="stat-label">股票总数</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.activeStrategies }}</div>
            <div class="stat-label">活跃策略</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.totalBacktests }}</div>
            <div class="stat-label">回测次数</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.avgReturn }}</div>
            <div class="stat-label">平均收益率</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <h2 class="section-title">快速操作</h2>
      <div class="action-grid">
        <el-card class="action-card" @click="$router.push('/stock-filter')">
          <div class="action-content">
            <el-icon class="action-icon"><Filter /></el-icon>
            <h3>股票筛选</h3>
            <p>根据多维度条件筛选优质股票</p>
          </div>
        </el-card>
        
        <el-card class="action-card" @click="$router.push('/strategy')">
          <div class="action-content">
            <el-icon class="action-icon"><Setting /></el-icon>
            <h3>策略管理</h3>
            <p>创建和管理投资策略</p>
          </div>
        </el-card>
        
        <el-card class="action-card" @click="$router.push('/backtest')">
          <div class="action-content">
            <el-icon class="action-icon"><DataAnalysis /></el-icon>
            <h3>回测分析</h3>
            <p>验证策略的历史表现</p>
          </div>
        </el-card>
        
        <el-card class="action-card">
          <div class="action-content">
            <el-icon class="action-icon"><TrendCharts /></el-icon>
            <h3>实时监控</h3>
            <p>监控投资组合实时表现</p>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 市场概览 -->
    <div class="market-overview">
      <h2 class="section-title">市场概览</h2>
      <div class="market-grid">
        <el-card class="market-card">
          <div class="card-header">
            <h3>上证指数</h3>
            <el-tag type="success">+1.23%</el-tag>
          </div>
          <div class="market-value">3,245.67</div>
          <div class="market-change">+39.45</div>
        </el-card>
        
        <el-card class="market-card">
          <div class="card-header">
            <h3>深证成指</h3>
            <el-tag type="danger">-0.87%</el-tag>
          </div>
          <div class="market-value">12,156.89</div>
          <div class="market-change">-106.78</div>
        </el-card>
        
        <el-card class="market-card">
          <div class="card-header">
            <h3>创业板指</h3>
            <el-tag type="success">+2.15%</el-tag>
          </div>
          <div class="market-value">2,678.34</div>
          <div class="market-change">+56.42</div>
        </el-card>
        
        <el-card class="market-card">
          <div class="card-header">
            <h3>科创50</h3>
            <el-tag type="warning">+0.34%</el-tag>
          </div>
          <div class="market-value">1,234.56</div>
          <div class="market-change">+4.18</div>
        </el-card>
      </div>
    </div>

    <!-- 热门股票 -->
    <div class="hot-stocks">
      <h2 class="section-title">热门股票</h2>
      <el-table :data="hotStocks" style="width: 100%">
        <el-table-column prop="code" label="股票代码" width="120" />
        <el-table-column prop="name" label="股票名称" width="150" />
        <el-table-column prop="price" label="当前价格" width="100">
          <template #default="{ row }">
            ¥{{ row.price }}
          </template>
        </el-table-column>
        <el-table-column prop="change" label="涨跌幅" width="100">
          <template #default="{ row }">
            <span :class="row.change >= 0 ? 'positive' : 'negative'">
              {{ row.change >= 0 ? '+' : '' }}{{ row.change }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="volume" label="成交量" />
        <el-table-column prop="marketCap" label="市值" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewStockDetail(row)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 最近回测 -->
    <div class="recent-backtests">
      <h2 class="section-title">最近回测</h2>
      <div class="backtest-list">
        <div v-for="backtest in recentBacktests" :key="backtest.id" class="backtest-item">
          <div class="backtest-info">
            <h4>{{ backtest.strategyName }}</h4>
            <p>{{ backtest.period }}</p>
          </div>
          <div class="backtest-results">
            <div class="result-item">
              <span class="label">收益率:</span>
              <span :class="backtest.return >= 0 ? 'positive' : 'negative'">
                {{ backtest.return >= 0 ? '+' : '' }}{{ backtest.return }}%
              </span>
            </div>
            <div class="result-item">
              <span class="label">夏普比率:</span>
              <span>{{ backtest.sharpe }}</span>
            </div>
          </div>
          <div class="backtest-actions">
            <el-button type="text" size="small">查看详情</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../utils/api'

const stats = ref({
  totalStocks: 0,
  activeStrategies: 0,
  totalBacktests: 0,
  avgReturn: '0.00%'
})

const hotStocks = ref([])

const recentBacktests = ref([])

const viewStockDetail = (stock) => {
  // 跳转到股票详情页面
  console.log('查看股票详情:', stock)
}

onMounted(async () => {
  // 加载统计数据
  try {
    const response = await api.get('/stats/overview')
    stats.value = response.data
  } catch (error) {
    console.error('加载统计数据失败:', error)
    // 使用默认数据
    stats.value = {
      totalStocks: 4523,
      activeStrategies: 8,
      totalBacktests: 156,
      avgReturn: '12.45%'
    }
  }
  
  // 加载热门股票
  try {
    const response = await api.get('/stocks/hot')
    hotStocks.value = response.data.stocks
  } catch (error) {
    console.error('加载热门股票失败:', error)
  }
  
  // 加载最近回测记录
  try {
    const response = await api.get('/backtest/recent')
    recentBacktests.value = response.data.backtests
  } catch (error) {
    console.error('加载最近回测失败:', error)
  }
})
</script>

<style lang="scss" scoped>
.home-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 40px;
  color: white;
  margin-bottom: 30px;
  text-align: center;
}

.welcome-title {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 10px;
}

.welcome-subtitle {
  font-size: 16px;
  opacity: 0.9;
  margin-bottom: 30px;
}

.welcome-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
  max-width: 600px;
  margin: 0 auto;
}

.stat-item {
  .stat-number {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 5px;
  }
  
  .stat-label {
    font-size: 14px;
    opacity: 0.8;
  }
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 20px;
}

.quick-actions {
  margin-bottom: 30px;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.action-card {
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  }
  
  .action-content {
    text-align: center;
    
    .action-icon {
      font-size: 48px;
      color: var(--primary-color);
      margin-bottom: 15px;
    }
    
    h3 {
      font-size: 18px;
      font-weight: 600;
      margin-bottom: 10px;
      color: var(--text-primary);
    }
    
    p {
      color: var(--text-secondary);
      margin: 0;
      line-height: 1.5;
    }
  }
}

.market-overview {
  margin-bottom: 30px;
}

.market-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.market-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    
    h3 {
      margin: 0;
      font-size: 16px;
      color: var(--text-primary);
    }
  }
  
  .market-value {
    font-size: 24px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 5px;
  }
  
  .market-change {
    font-size: 14px;
    color: var(--text-secondary);
  }
}

.hot-stocks {
  margin-bottom: 30px;
}

.positive {
  color: var(--success-color);
}

.negative {
  color: var(--danger-color);
}

.recent-backtests {
  .backtest-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
  }
  
  .backtest-item {
    background: var(--background-white);
    border-radius: 8px;
    padding: 20px;
    box-shadow: var(--shadow-light);
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .backtest-info {
      flex: 1;
      
      h4 {
        margin: 0 0 5px 0;
        font-size: 16px;
        color: var(--text-primary);
      }
      
      p {
        margin: 0;
        font-size: 14px;
        color: var(--text-secondary);
      }
    }
    
    .backtest-results {
      display: flex;
      gap: 20px;
      margin: 0 20px;
      
      .result-item {
        text-align: center;
        
        .label {
          display: block;
          font-size: 12px;
          color: var(--text-secondary);
          margin-bottom: 5px;
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .home-container {
    padding: 15px;
  }
  
  .welcome-section {
    padding: 30px 20px;
  }
  
  .welcome-title {
    font-size: 24px;
  }
  
  .welcome-stats {
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
  }
  
  .action-grid {
    grid-template-columns: 1fr;
  }
  
  .market-grid {
    grid-template-columns: 1fr;
  }
  
  .backtest-item {
    flex-direction: column;
    align-items: flex-start !important;
    gap: 15px;
    
    .backtest-results {
      margin: 0 !important;
    }
  }
}
</style>
