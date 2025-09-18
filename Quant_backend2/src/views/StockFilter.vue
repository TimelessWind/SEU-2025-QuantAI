<template>
  <div class="stock-filter-container">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-left">
        <h1>股票筛选器</h1>
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
        <!-- 筛选条件 -->
        <el-card class="filter-card">
          <template #header>
            <div class="card-header">
              <span>筛选条件</span>
              <el-button type="primary" @click="handleSearch" :loading="loading">
                <el-icon><Search /></el-icon>
                筛选
              </el-button>
            </div>
          </template>

          <el-form :model="filterForm" label-width="120px" class="filter-form">
            <el-row :gutter="20">
              <!-- 基本信息 -->
              <el-col :span="12">
                <h4>基本信息</h4>
                <el-form-item label="股票代码">
                  <el-input
                    v-model="filterForm.stockCode"
                    placeholder="如：000001.SZ"
                    clearable
                  />
                </el-form-item>
                
                <el-form-item label="行业">
                  <el-select
                    v-model="filterForm.industry"
                    placeholder="请选择行业"
                    clearable
                    style="width: 100%"
                  >
                    <el-option
                      v-for="item in industryOptions"
                      :key="item.value"
                      :label="item.label"
                      :value="item.value"
                    />
                  </el-select>
                </el-form-item>

                <el-form-item label="地区">
                  <el-select
                    v-model="filterForm.area"
                    placeholder="请选择地区"
                    clearable
                    style="width: 100%"
                  >
                    <el-option
                      v-for="item in areaOptions"
                      :key="item.value"
                      :label="item.label"
                      :value="item.value"
                    />
                  </el-select>
                </el-form-item>
              </el-col>

              <!-- 估值指标 -->
              <el-col :span="12">
                <h4>估值指标</h4>
                <el-form-item label="市盈率(PE)">
                  <el-row :gutter="10">
                    <el-col :span="11">
                      <el-input-number
                        v-model="filterForm.peMin"
                        placeholder="最小值"
                        :min="0"
                        :precision="2"
                        style="width: 100%"
                      />
                    </el-col>
                    <el-col :span="2" style="text-align: center; line-height: 32px;">-</el-col>
                    <el-col :span="11">
                      <el-input-number
                        v-model="filterForm.peMax"
                        placeholder="最大值"
                        :min="0"
                        :precision="2"
                        style="width: 100%"
                      />
                    </el-col>
                  </el-row>
                </el-form-item>

                <el-form-item label="市净率(PB)">
                  <el-row :gutter="10">
                    <el-col :span="11">
                      <el-input-number
                        v-model="filterForm.pbMin"
                        placeholder="最小值"
                        :min="0"
                        :precision="2"
                        style="width: 100%"
                      />
                    </el-col>
                    <el-col :span="2" style="text-align: center; line-height: 32px;">-</el-col>
                    <el-col :span="11">
                      <el-input-number
                        v-model="filterForm.pbMax"
                        placeholder="最大值"
                        :min="0"
                        :precision="2"
                        style="width: 100%"
                      />
                    </el-col>
                  </el-row>
                </el-form-item>

                <el-form-item label="市值(亿元)">
                  <el-row :gutter="10">
                    <el-col :span="11">
                      <el-input-number
                        v-model="filterForm.marketCapMin"
                        placeholder="最小值"
                        :min="0"
                        :precision="2"
                        style="width: 100%"
                      />
                    </el-col>
                    <el-col :span="2" style="text-align: center; line-height: 32px;">-</el-col>
                    <el-col :span="11">
                      <el-input-number
                        v-model="filterForm.marketCapMax"
                        placeholder="最大值"
                        :min="0"
                        :precision="2"
                        style="width: 100%"
                      />
                    </el-col>
                  </el-row>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <!-- 技术指标 -->
              <el-col :span="12">
                <h4>技术指标</h4>
                <el-form-item label="RSI">
                  <el-row :gutter="10">
                    <el-col :span="11">
                      <el-input-number
                        v-model="filterForm.rsiMin"
                        placeholder="最小值"
                        :min="0"
                        :max="100"
                        :precision="2"
                        style="width: 100%"
                      />
                    </el-col>
                    <el-col :span="2" style="text-align: center; line-height: 32px;">-</el-col>
                    <el-col :span="11">
                      <el-input-number
                        v-model="filterForm.rsiMax"
                        placeholder="最大值"
                        :min="0"
                        :max="100"
                        :precision="2"
                        style="width: 100%"
                      />
                    </el-col>
                  </el-row>
                </el-form-item>

                <el-form-item label="均线关系">
                  <el-select
                    v-model="filterForm.maRelation"
                    placeholder="请选择均线关系"
                    clearable
                    style="width: 100%"
                  >
                    <el-option label="价格上穿5日均线" value="price_above_ma5" />
                    <el-option label="价格下穿5日均线" value="price_below_ma5" />
                    <el-option label="5日均线上穿20日均线" value="ma5_above_ma20" />
                    <el-option label="5日均线下穿20日均线" value="ma5_below_ma20" />
                  </el-select>
                </el-form-item>
              </el-col>

              <!-- 财务指标 -->
              <el-col :span="12">
                <h4>财务指标</h4>
                <el-form-item label="资产负债率(%)">
                  <el-row :gutter="10">
                    <el-col :span="11">
                      <el-input-number
                        v-model="filterForm.debtRatioMin"
                        placeholder="最小值"
                        :min="0"
                        :max="100"
                        :precision="2"
                        style="width: 100%"
                      />
                    </el-col>
                    <el-col :span="2" style="text-align: center; line-height: 32px;">-</el-col>
                    <el-col :span="11">
                      <el-input-number
                        v-model="filterForm.debtRatioMax"
                        placeholder="最大值"
                        :min="0"
                        :max="100"
                        :precision="2"
                        style="width: 100%"
                      />
                    </el-col>
                  </el-row>
                </el-form-item>

                <el-form-item label="流动比率">
                  <el-row :gutter="10">
                    <el-col :span="11">
                      <el-input-number
                        v-model="filterForm.currentRatioMin"
                        placeholder="最小值"
                        :min="0"
                        :precision="2"
                        style="width: 100%"
                      />
                    </el-col>
                    <el-col :span="2" style="text-align: center; line-height: 32px;">-</el-col>
                    <el-col :span="11">
                      <el-input-number
                        v-model="filterForm.currentRatioMax"
                        placeholder="最大值"
                        :min="0"
                        :precision="2"
                        style="width: 100%"
                      />
                    </el-col>
                  </el-row>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row>
              <el-col :span="24" style="text-align: center; margin-top: 20px;">
                <el-button @click="handleReset">重置条件</el-button>
                <el-button type="primary" @click="handleSearch" :loading="loading">
                  <el-icon><Search /></el-icon>
                  开始筛选
                </el-button>
              </el-col>
            </el-row>
          </el-form>
        </el-card>

        <!-- 筛选结果 -->
        <el-card class="result-card" v-if="searchResults.length > 0">
          <template #header>
            <div class="card-header">
              <span>筛选结果 ({{ searchResults.length }} 只股票)</span>
              <el-button type="success" @click="handleExport">
                <el-icon><Download /></el-icon>
                导出结果
              </el-button>
            </div>
          </template>

          <el-table
            :data="searchResults"
            style="width: 100%"
            stripe
            border
            height="400"
          >
            <el-table-column prop="stockCode" label="股票代码" width="120" />
            <el-table-column prop="stockName" label="股票名称" width="120" />
            <el-table-column prop="industry" label="行业" width="100" />
            <el-table-column prop="peRatio" label="市盈率" width="100" />
            <el-table-column prop="pbRatio" label="市净率" width="100" />
            <el-table-column prop="marketCap" label="市值(亿)" width="120" />
            <el-table-column prop="rsi" label="RSI" width="80" />
            <el-table-column prop="currentPrice" label="当前价格" width="100" />
            <el-table-column prop="changePercent" label="涨跌幅%" width="100" />
            <el-table-column label="操作" width="120">
              <template #default="scope">
                <el-button type="primary" size="small" @click="handleViewDetail(scope.row)">
                  查看详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-main>
    </el-container>
  </div>

  <!-- 股票详情弹窗 -->
  <el-dialog
    v-model="detailDialogVisible"
    :title="`${stockDetail.basicInfo.stockName || currentStock?.stockName}(${stockDetail.basicInfo.stockCode || currentStock?.stockCode}) 详情`"
    width="800px"
    :before-close="() => { detailDialogVisible.value = false }"
  >
    <div v-if="detailLoading" class="loading-container">
      <el-progress type="circular" :percentage="0" status="warning" />
      <p>加载中...</p>
    </div>
    <div v-else class="stock-detail-content">
      <el-tabs type="card" style="height: 100%;">
        <!-- 基本信息 -->
        <el-tab-pane label="基本信息">
          <el-row :gutter="20" class="info-row">
            <el-col :span="12">
              <div class="info-item">
                <span class="info-label">股票代码：</span>
                <span class="info-value">{{ stockDetail.basicInfo.stockCode }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">股票名称：</span>
                <span class="info-value">{{ stockDetail.basicInfo.stockName }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">所属行业：</span>
                <span class="info-value">{{ stockDetail.basicInfo.industry }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">地区：</span>
                <span class="info-value">{{ stockDetail.basicInfo.area }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">上市日期：</span>
                <span class="info-value">{{ stockDetail.basicInfo.listDate }}</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="info-item">
                <span class="info-label">当前价格：</span>
                <span class="info-value price">{{ stockDetail.priceInfo.currentPrice }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">涨跌幅：</span>
                <span class="info-value" :class="stockDetail.priceInfo.changePercent >= 0 ? 'up' : 'down'">
                  {{ stockDetail.priceInfo.changePercent > 0 ? '+' : '' }}{{ stockDetail.priceInfo.changePercent }}%
                </span>
              </div>
              <div class="info-item">
                <span class="info-label">成交量：</span>
                <span class="info-value">{{ (stockDetail.priceInfo.volume / 10000).toFixed(2) }}万手</span>
              </div>
              <div class="info-item">
                <span class="info-label">成交额：</span>
                <span class="info-value">{{ (stockDetail.priceInfo.amount / 100000000).toFixed(2) }}亿元</span>
              </div>
            </el-col>
          </el-row>
        </el-tab-pane>

        <!-- 估值指标 -->
        <el-tab-pane label="估值指标">
          <el-row :gutter="20" class="info-row">
            <el-col :span="12">
              <div class="info-item">
                <span class="info-label">市盈率(PE)：</span>
                <span class="info-value">{{ stockDetail.valuationInfo.peRatio }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">市净率(PB)：</span>
                <span class="info-value">{{ stockDetail.valuationInfo.pbRatio }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">市销率(PS)：</span>
                <span class="info-value">{{ stockDetail.valuationInfo.psRatio }}</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="info-item">
                <span class="info-label">总市值：</span>
                <span class="info-value">{{ stockDetail.valuationInfo.marketCap }}亿元</span>
              </div>
              <div class="info-item">
                <span class="info-label">换手率：</span>
                <span class="info-value">{{ stockDetail.valuationInfo.turnoverRatio }}%</span>
              </div>
            </el-col>
          </el-row>
        </el-tab-pane>

        <!-- 技术指标 -->
        <el-tab-pane label="技术指标">
          <el-row :gutter="20" class="info-row">
            <el-col :span="12">
              <div class="info-item">
                <span class="info-label">RSI指标：</span>
                <span class="info-value">{{ stockDetail.technicalIndicators.rsi.toFixed(2) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">MACD值：</span>
                <span class="info-value">{{ stockDetail.technicalIndicators.macd.toFixed(4) }}</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="info-item">
                <span class="info-label">KDJ-K值：</span>
                <span class="info-value">{{ stockDetail.technicalIndicators.kdj.k.toFixed(2) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">KDJ-D值：</span>
                <span class="info-value">{{ stockDetail.technicalIndicators.kdj.d.toFixed(2) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">KDJ-J值：</span>
                <span class="info-value">{{ stockDetail.technicalIndicators.kdj.j.toFixed(2) }}</span>
              </div>
            </el-col>
          </el-row>
          
          <div class="separator"></div>
          
          <h4 class="indicator-title">布林带指标</h4>
          <el-row :gutter="20" class="info-row">
            <el-col :span="8">
              <div class="info-item">
                <span class="info-label">上轨：</span>
                <span class="info-value">{{ stockDetail.technicalIndicators.bollinger.upper.toFixed(2) }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="info-item">
                <span class="info-label">中轨：</span>
                <span class="info-value">{{ stockDetail.technicalIndicators.bollinger.middle.toFixed(2) }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="info-item">
                <span class="info-label">下轨：</span>
                <span class="info-value">{{ stockDetail.technicalIndicators.bollinger.lower.toFixed(2) }}</span>
              </div>
            </el-col>
          </el-row>
        </el-tab-pane>
      </el-tabs>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="detailDialogVisible.value = false">关闭</el-button>
      </span>
    </template>
  </el-dialog>

  <style scoped>
  .loading-container {
    text-align: center;
    padding: 50px 0;
  }
  
  .loading-container p {
    margin-top: 20px;
    color: #606266;
  }
  
  .stock-detail-content {
    max-height: 500px;
    overflow-y: auto;
  }
  
  .info-row {
    margin-bottom: 20px;
  }
  
  .info-item {
    margin-bottom: 15px;
    padding: 8px 0;
    border-bottom: 1px dashed #e6e6e6;
  }
  
  .info-label {
    display: inline-block;
    width: 100px;
    font-weight: 500;
    color: #606266;
  }
  
  .info-value {
    color: #303133;
    font-size: 14px;
  }
  
  .info-value.price {
    font-size: 16px;
    font-weight: 600;
  }
  
  .info-value.up {
    color: #f56c6c;
  }
  
  .info-value.down {
    color: #67c23a;
  }
  
  .separator {
    height: 1px;
    background-color: #e6e6e6;
    margin: 20px 0;
  }
  
  .indicator-title {
    margin-bottom: 15px;
    color: #303133;
    font-size: 14px;
    font-weight: 500;
  }
  </style>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const activeMenu = ref('/stock-filter')
const loading = ref(false)

// 筛选表单
const filterForm = reactive({
  stockCode: '',
  industry: '',
  area: '',
  peMin: null,
  peMax: null,
  pbMin: null,
  pbMax: null,
  marketCapMin: null,
  marketCapMax: null,
  rsiMin: null,
  rsiMax: null,
  maRelation: '',
  debtRatioMin: null,
  debtRatioMax: null,
  currentRatioMin: null,
  currentRatioMax: null
})

// 选项数据
const industryOptions = ref([
  { label: '银行', value: '银行' },
  { label: '房地产', value: '房地产' },
  { label: '医药生物', value: '医药生物' },
  { label: '电子', value: '电子' },
  { label: '计算机', value: '计算机' },
  { label: '食品饮料', value: '食品饮料' },
  { label: '汽车', value: '汽车' },
  { label: '化工', value: '化工' }
])

const areaOptions = ref([
  { label: '北京', value: '北京' },
  { label: '上海', value: '上海' },
  { label: '深圳', value: '深圳' },
  { label: '广东', value: '广东' },
  { label: '浙江', value: '浙江' },
  { label: '江苏', value: '江苏' }
])

// 搜索结果
const searchResults = ref([])

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

const handleSearch = async () => {
  loading.value = true
  try {
    // 这里调用后端API进行筛选
    // 暂时使用模拟数据
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    searchResults.value = [
      {
        stockCode: '000001.SZ',
        stockName: '平安银行',
        industry: '银行',
        peRatio: 5.2,
        pbRatio: 0.8,
        marketCap: 2800,
        rsi: 45.6,
        currentPrice: 14.5,
        changePercent: 2.1
      },
      {
        stockCode: '000002.SZ',
        stockName: '万科A',
        industry: '房地产',
        peRatio: 8.3,
        pbRatio: 1.2,
        marketCap: 1200,
        rsi: 52.3,
        currentPrice: 18.2,
        changePercent: -1.5
      }
    ]
    
    ElMessage.success(`筛选完成，找到 ${searchResults.value.length} 只股票`)
  } catch (error) {
    ElMessage.error('筛选失败：' + error.message)
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  Object.keys(filterForm).forEach(key => {
    if (typeof filterForm[key] === 'string') {
      filterForm[key] = ''
    } else {
      filterForm[key] = null
    }
  })
  searchResults.value = []
}

const handleExport = () => {
  ElMessage.success('导出功能开发中')
}

// 股票详情弹窗状态
const detailDialogVisible = ref(false)
const currentStock = ref(null)
const stockDetail = ref({
  basicInfo: {},
  priceInfo: {},
  valuationInfo: {},
  technicalIndicators: {
    rsi: 0,
    macd: 0,
    kdj: {
      k: 0,
      d: 0,
      j: 0
    },
    bollinger: {
      upper: 0,
      middle: 0,
      lower: 0
    }
  }
})
const detailLoading = ref(false)

const handleViewDetail = async (row) => {
  currentStock.value = row
  detailLoading.value = true
  try {
    // 调用后端API获取股票详情
    const response = await fetch(`/stocks/${row.stockCode}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userStore.token}`
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      stockDetail.value = data
      
      // 模拟计算技术指标（在实际应用中可能需要单独的API）
      stockDetail.value.technicalIndicators = {
        rsi: row.rsi || Math.random() * 100, // 如果有RSI值就使用，否则生成随机值
        macd: (Math.random() - 0.5) * 2, // 生成-1到1之间的随机值
        kdj: {
          k: Math.random() * 100,
          d: Math.random() * 100,
          j: Math.random() * 100
        },
        bollinger: {
          upper: (row.currentPrice || 100) * (1 + Math.random() * 0.2),
          middle: row.currentPrice || 100,
          lower: (row.currentPrice || 100) * (1 - Math.random() * 0.2)
        }
      }
    } else {
      ElMessage.error('获取股票详情失败')
    }
  } catch (error) {
    ElMessage.error('获取股票详情失败：' + error.message)
  } finally {
    detailLoading.value = false
  }
  
  detailDialogVisible.value = true
}
}

onMounted(() => {
  activeMenu.value = route.path
})
</script>

<style scoped>
.stock-filter-container {
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

.filter-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-form h4 {
  color: #2c3e50;
  margin-bottom: 15px;
  padding-bottom: 8px;
  border-bottom: 2px solid #409eff;
}

.result-card {
  margin-top: 20px;
}
</style>
