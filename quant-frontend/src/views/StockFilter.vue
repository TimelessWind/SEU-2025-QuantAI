<template>
  <div class="stock-filter">
    <el-card class="filter-card">
      <template #header>
        <div class="card-header">
          <span>股票筛选器</span>
        </div>
      </template>
      
      <el-form :model="filterForm" label-width="120px" class="filter-form">
        <!-- 基本信息筛选 -->
        <el-divider content-position="left">基本信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="股票代码">
              <el-input v-model="filterForm.stockCode" placeholder="请输入股票代码" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="行业分类">
              <el-select v-model="filterForm.industry" placeholder="请选择行业" clearable>
                <el-option label="全部" value="" />
                <el-option 
                  v-for="industry in industries" 
                  :key="industry" 
                  :label="industry" 
                  :value="industry" 
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="地区分布">
              <el-select v-model="filterForm.area" placeholder="请选择地区" clearable>
                <el-option label="全部" value="" />
                <el-option label="北京" value="北京" />
                <el-option label="上海" value="上海" />
                <el-option label="广东" value="广东" />
                <el-option label="浙江" value="浙江" />
                <el-option label="江苏" value="江苏" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 估值指标筛选 -->
        <el-divider content-position="left">估值指标</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="市盈率(PE)">
              <el-input-number v-model="filterForm.peMin" placeholder="最小值" :min="0" />
              <span style="margin: 0 10px">-</span>
              <el-input-number v-model="filterForm.peMax" placeholder="最大值" :min="0" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="市净率(PB)">
              <el-input-number v-model="filterForm.pbMin" placeholder="最小值" :min="0" />
              <span style="margin: 0 10px">-</span>
              <el-input-number v-model="filterForm.pbMax" placeholder="最大值" :min="0" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="市值(万元)">
              <el-input-number v-model="filterForm.marketCapMin" placeholder="最小值" :min="0" />
              <span style="margin: 0 10px">-</span>
              <el-input-number v-model="filterForm.marketCapMax" placeholder="最大值" :min="0" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 技术指标筛选 -->
        <el-divider content-position="left">技术指标</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="RSI相对强弱">
              <el-input-number v-model="filterForm.rsiMin" placeholder="最小值" :min="0" :max="100" />
              <span style="margin: 0 10px">-</span>
              <el-input-number v-model="filterForm.rsiMax" placeholder="最大值" :min="0" :max="100" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="均线关系">
              <el-select v-model="filterForm.maRelation" placeholder="请选择均线关系" clearable>
                <el-option label="全部" value="" />
                <el-option label="价格上穿5日均线" value="price_above_ma5" />
                <el-option label="价格下穿5日均线" value="price_below_ma5" />
                <el-option label="5日均线上穿20日均线" value="ma5_above_ma20" />
                <el-option label="5日均线下穿20日均线" value="ma5_below_ma20" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 财务指标筛选 -->
        <el-divider content-position="left">财务指标</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="资产负债率(%)">
              <el-input-number v-model="filterForm.debtRatioMin" placeholder="最小值" :min="0" :max="100" />
              <span style="margin: 0 10px">-</span>
              <el-input-number v-model="filterForm.debtRatioMax" placeholder="最大值" :min="0" :max="100" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="流动比率">
              <el-input-number v-model="filterForm.currentRatioMin" placeholder="最小值" :min="0" />
              <span style="margin: 0 10px">-</span>
              <el-input-number v-model="filterForm.currentRatioMax" placeholder="最大值" :min="0" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 显示选项 -->
        <el-form-item label-width="120px">
          <el-switch
            v-model="showRawData"
            active-text="精确显示"
            inactive-text="格式化显示"
            active-color="#13ce66"
            inactive-color="#ff4949"
          />
        </el-form-item>
    
    <!-- 操作按钮 -->
        <el-form-item>
          <el-button type="primary" @click="handleFilter" :loading="loading">
            <el-icon><Search /></el-icon>
            筛选股票
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置条件
          </el-button>
          <el-button type="success" @click="handleExport" :disabled="!hasResults">
            <el-icon><Download /></el-icon>
            导出结果
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 筛选结果 -->
    <el-card v-if="hasResults" class="result-card">
      <template #header>
        <div class="card-header">
          <span>筛选结果 ({{ filteredStocks.length }} 只股票)</span>
        </div>
      </template>
      
      <el-table :data="displayStocks" stripe style="width: 100%">
        <el-table-column prop="stockCode" label="股票代码" width="120" />
        <el-table-column prop="stockName" label="股票名称" width="150" />
        <el-table-column prop="industry" label="行业" width="120" />
        <el-table-column prop="area" label="地区" width="100" />
        <el-table-column prop="peRatio" label="市盈率" width="100" />
        <el-table-column prop="pbRatio" label="市净率" width="100" />
        <el-table-column label="市值(万)" width="120">
          <template #default="scope">
            {{ scope.row.marketCap ? 
               (showRawData ? (scope.row.marketCap * 10000) : (scope.row.marketCap * 10000).toFixed(2)) 
               : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="rsi" label="RSI" width="80" />
        <el-table-column label="资产负债率%" width="120">
          <template #default="scope">
            {{ scope.row.debtRatio ? 
               (showRawData ? scope.row.debtRatio : scope.row.debtRatio.toFixed(2)) 
               : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="流动比率" width="100">
          <template #default="scope">
            {{ scope.row.currentRatio ? 
               (showRawData ? scope.row.currentRatio : scope.row.currentRatio.toFixed(2)) 
               : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button size="small" @click="handleViewDetail(scope.row)">详情</el-button>
            <el-button size="small" type="primary" @click="handleAddToStrategy(scope.row)">加入策略</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Download } from '@element-plus/icons-vue'
import api from '../utils/api'

// 筛选表单数据
const filterForm = ref({
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

// 筛选结果
const filteredStocks = ref([])
const loading = ref(false)
const showRawData = ref(false) // 是否精确显示原始数据

// 计算属性
const hasResults = computed(() => filteredStocks.value.length > 0)

// 用于表格显示的数据计算属性
const displayStocks = computed(() => {
  // 直接使用原始数据，在模板中根据showRawData的值决定显示方式
  return filteredStocks.value
})

// 筛选股票
const handleFilter = async () => {
  loading.value = true
  try {
    // 创建筛选条件的副本，并将市值从万元转换为亿元
    const filterParams = { ...filterForm.value }
    if (filterParams.marketCapMin !== null) {
      filterParams.marketCapMin = filterParams.marketCapMin / 10000
    }
    if (filterParams.marketCapMax !== null) {
      filterParams.marketCapMax = filterParams.marketCapMax / 10000
    }
    // 调用后端API进行筛选
    const response = await api.post('/stocks/filter', filterParams)
    filteredStocks.value = response.data.stocks
    
    ElMessage.success(`筛选完成，找到 ${filteredStocks.value.length} 只符合条件的股票`)
  } catch (error) {
    ElMessage.error('筛选失败，请重试')
    console.error('筛选错误:', error)
  } finally {
    loading.value = false
  }
}

// 重置筛选条件
const handleReset = () => {
  Object.keys(filterForm.value).forEach(key => {
    if (typeof filterForm.value[key] === 'string') {
      filterForm.value[key] = ''
    } else {
      filterForm.value[key] = null
    }
  })
  filteredStocks.value = []
  ElMessage.info('筛选条件已重置')
}

// 导出结果
const handleExport = () => {
  ElMessage.success('导出功能开发中...')
}

// 查看股票详情
const handleViewDetail = (row) => {
  ElMessage.info(`查看 ${row.stockName} 详情`)
}

// 加入策略
const handleAddToStrategy = (row) => {
  ElMessage.success(`已将 ${row.stockName} 加入策略`)
}

// 加载行业列表
const industries = ref([])

onMounted(async () => {
  try {
    const response = await api.get('/stocks/industries')
    industries.value = response.data.industries
  } catch (error) {
    console.error('加载行业列表失败:', error)
  }
})
</script>

<style scoped>
.stock-filter {
  padding: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.result-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  font-size: 16px;
}

.filter-form {
  margin-top: 20px;
}

.el-divider {
  margin: 20px 0;
}

.el-form-item {
  margin-bottom: 20px;
}
</style>
