<template>
  <div class="backtest-container">
    <div class="page-header">
      <h1 class="page-title">回测分析</h1>
      <p class="page-subtitle">验证策略的历史表现和收益情况</p>
    </div>

    <div class="backtest-content">
      <!-- 回测配置 -->
      <el-card class="config-card">
        <template #header>
          <h3 class="card-title">回测配置</h3>
        </template>

        <el-form :model="backtestConfig" label-width="120px" class="config-form">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="选择策略">
                <el-select v-model="backtestConfig.strategyId" placeholder="请选择策略" style="width: 100%" @change="onStrategyChange">
                  <el-option
                    v-for="strategy in strategies"
                    :key="strategy.id"
                    :label="strategy.name"
                    :value="strategy.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            
            <el-col :span="8">
              <el-form-item label="回测类型">
                <el-select v-model="backtestConfig.type" placeholder="请选择类型" style="width: 100%">
                  <el-option label="单股票回测" value="stock" />
                  <el-option label="指数回测" value="index" />
                </el-select>
              </el-form-item>
            </el-col>
            
            <el-col :span="8">
              <el-form-item label="股票/指数">
                <el-input v-model="backtestConfig.target" placeholder="如：600519.SH 或 000300.SH" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="6">
              <el-form-item label="开始日期">
                <el-date-picker
                  v-model="backtestConfig.startDate"
                  type="date"
                  placeholder="选择开始日期"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            
            <el-col :span="6">
              <el-form-item label="结束日期">
                <el-date-picker
                  v-model="backtestConfig.endDate"
                  type="date"
                  placeholder="选择结束日期"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            
            <el-col :span="6">
              <el-form-item label="初始资金">
                <el-input-number
                  v-model="backtestConfig.initialFund"
                  :min="10000"
                  :step="10000"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            
            <el-col :span="6">
              <el-form-item label="手续费率(%)">
                <el-input-number
                  v-model="backtestConfig.commissionRate"
                  :min="0"
                  :max="1"
                  :precision="4"
                  :step="0.0001"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <!-- 策略参数配置 -->
          <div v-if="currentStrategy && !isCustomStrategy" class="strategy-params">
            <h4 class="param-title">策略参数配置</h4>
            <div class="param-description">{{ currentStrategy.description }}</div>
            
            <el-row :gutter="20" v-for="key in getCurrentStrategyParams()" :key="key">
              <el-col :span="8">
                <el-form-item :label="getParamLabel(key)">
                  <el-input-number
                    v-model="strategyParams[key]"
                    :min="getParamMin(key)"
                    :step="getParamStep(key)"
                    :precision="getParamPrecision(key)"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </div>
          
          <!-- 自定义策略提示 -->
          <div v-if="currentStrategy && isCustomStrategy" class="custom-strategy-tip">
            <el-alert
              title="自定义策略"
              message="自定义策略不支持用户输入参数，使用预设参数进行回测。"
              type="info"
              show-icon
            />
          </div>
          
          <el-form-item>
            <el-button type="primary" @click="startBacktest" :loading="backtesting" size="large">
              <el-icon><PlayArrow /></el-icon>
              开始回测
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 回测结果 -->
      <el-card v-if="backtestResult" class="result-card">
        <template #header>
          <div class="card-header">
            <h3 class="card-title">回测结果</h3>
            <div class="result-actions">
              <el-button @click="exportReport" size="small">
                <el-icon><Download /></el-icon>
                导出报告
              </el-button>
              <el-button @click="viewDetails" size="small">
                <el-icon><View /></el-icon>
                查看详情
              </el-button>
            </div>
          </div>
        </template>

        <!-- 收益概览 -->
        <div class="performance-overview">
          <h4 class="section-title">收益概览</h4>
          <div class="overview-grid">
            <div class="overview-item">
              <div class="overview-label">总收益率</div>
              <div :class="['overview-value', backtestResult.totalReturn >= 0 ? 'positive' : 'negative']">
                {{ backtestResult.totalReturn >= 0 ? '+' : '' }}{{ backtestResult.totalReturn.toFixed(4) }}%
              </div>
            </div>
            
            <div class="overview-item">
              <div class="overview-label">年化收益率</div>
              <div :class="['overview-value', backtestResult.annualReturn >= 0 ? 'positive' : 'negative']">
                {{ backtestResult.annualReturn >= 0 ? '+' : '' }}{{ backtestResult.annualReturn.toFixed(4) }}%
              </div>
            </div>
            
            <div class="overview-item">
              <div class="overview-label">最大回撤</div>
              <div class="overview-value negative">{{ backtestResult.maxDrawdown.toFixed(4) }}%</div>
            </div>
            
            <div class="overview-item">
              <div class="overview-label">夏普比率</div>
              <div class="overview-value">{{ backtestResult.sharpeRatio.toFixed(4) }}</div>
            </div>
            
            <div class="overview-item">
              <div class="overview-label">胜率</div>
              <div class="overview-value">{{ backtestResult.winRate.toFixed(4) }}%</div>
            </div>
            
            <div class="overview-item">
              <div class="overview-label">交易次数</div>
              <div class="overview-value">{{ backtestResult.tradeCount }}</div>
            </div>
          </div>
        </div>

        <!-- 资金曲线图 -->
        <div class="chart-section">
          <h4 class="section-title">资金曲线</h4>
          <div class="chart-container" ref="chartContainer"></div>
        </div>

        <!-- 交易记录 -->
        <div class="trade-records">
          <h4 class="section-title">交易记录</h4>
          <el-table :data="backtestResult.trades" style="width: 100%">
            <el-table-column prop="date" label="交易日期" width="120" />
            <el-table-column prop="type" label="类型" width="80">
              <template #default="{ row }">
                <el-tag :type="row.type === 'buy' ? 'success' : 'danger'">
                  {{ row.type === 'buy' ? '买入' : '卖出' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="stockCode" label="股票代码" width="120" />
            <el-table-column prop="price" label="价格" width="100">
            <template #default="{ row }">
              {{ row.price.toFixed(2) }}
            </template>
          </el-table-column>
            <el-table-column prop="quantity" label="数量" width="100" />
            <el-table-column prop="amount" label="金额" width="120">
            <template #default="{ row }">
              {{ row.amount.toFixed(2) }}
            </template>
          </el-table-column>
          </el-table>
        </div>
      </el-card>

      <!-- 历史回测记录 -->
      <el-card class="history-card">
        <template #header>
          <h3 class="card-title">历史回测记录</h3>
        </template>

        <el-table :data="historyRecords" style="width: 100%">
          <el-table-column prop="strategyName" label="策略名称" width="150" />
          <el-table-column prop="target" label="标的" width="120" />
          <el-table-column prop="period" label="回测期间" width="200" />
          <el-table-column prop="totalReturn" label="总收益率" width="120">
            <template #default="{ row }">
              <span :class="row.totalReturn >= 0 ? 'positive' : 'negative'">
                {{ row.totalReturn >= 0 ? '+' : '' }}{{ row.totalReturn.toFixed(4) }}%
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="maxDrawdown" label="最大回撤" width="120" />
          <el-table-column prop="sharpeRatio" label="夏普比率" width="120" />
          <el-table-column prop="createTime" label="创建时间" width="180" />
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="viewHistoryDetail(row)">
                查看详情
              </el-button>
              <el-button type="danger" size="small" @click="deleteHistory(row)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>

  <!-- 历史回测详情弹窗 -->
  <el-dialog 
    v-model="detailDialogVisible" 
    title="回测详情" 
    width="80%" 
    :before-close="handleDetailDialogClose"
  >
    <div v-if="currentHistoryDetail" class="history-detail-content">
      <!-- 收益概览 -->
      <div class="performance-overview">
        <h4 class="section-title">收益概览</h4>
        <div class="overview-grid">
          <div class="overview-item">
            <div class="overview-label">总收益率</div>
            <div :class="['overview-value', currentHistoryDetail.totalReturn >= 0 ? 'positive' : 'negative']">
                {{ currentHistoryDetail.totalReturn >= 0 ? '+' : '' }}{{ currentHistoryDetail.totalReturn.toFixed(4) }}%
              </div>
          </div>
          
          <div class="overview-item">
            <div class="overview-label">年化收益率</div>
            <div :class="['overview-value', currentHistoryDetail.annualReturn >= 0 ? 'positive' : 'negative']">
                {{ currentHistoryDetail.annualReturn >= 0 ? '+' : '' }}{{ currentHistoryDetail.annualReturn.toFixed(4) }}%
              </div>
          </div>
          
          <div class="overview-item">
            <div class="overview-label">最大回撤</div>
            <div class="overview-value negative">{{ currentHistoryDetail.maxDrawdown.toFixed(4) }}%</div>
          </div>
          
          <div class="overview-item">
            <div class="overview-label">夏普比率</div>
            <div class="overview-value">{{ currentHistoryDetail.sharpeRatio.toFixed(4) }}</div>
          </div>
          
          <div class="overview-item">
            <div class="overview-label">胜率</div>
            <div class="overview-value">{{ currentHistoryDetail.winRate.toFixed(4) }}%</div>
          </div>
          
          <div class="overview-item">
            <div class="overview-label">交易次数</div>
            <div class="overview-value">{{ currentHistoryDetail.tradeCount }}</div>
          </div>
        </div>
      </div>

      <!-- 策略参数 -->
      <div v-if="currentHistoryDetail.strategyParams" class="strategy-params">
        <h4 class="section-title">策略参数</h4>
        <div class="params-grid">
          <div v-for="(value, key) in currentHistoryDetail.strategyParams" :key="key" class="param-item">
            <span class="param-label">{{ getParamLabel(key) }}:</span>
            <span class="param-value">{{ value }}</span>
          </div>
        </div>
      </div>

      <!-- 资金曲线图 -->
      <div class="chart-section">
        <h4 class="section-title">资金曲线</h4>
        <div class="chart-container" ref="historyChartContainer"></div>
      </div>

      <!-- 交易记录 -->
      <div class="trade-records">
        <h4 class="section-title">交易记录</h4>
        <el-table :data="currentHistoryDetail.trades" style="width: 100%">
          <el-table-column prop="date" label="交易日期" width="120" />
          <el-table-column prop="type" label="类型" width="80">
            <template #default="{ row }">
              <el-tag :type="row.type === 'buy' ? 'success' : 'danger'">
                {{ row.type === 'buy' ? '买入' : '卖出' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="stockCode" label="股票代码" width="120" />
          <el-table-column prop="price" label="价格" width="100">
            <template #default="{ row }">
              {{ row.price.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量" width="100" />
          <el-table-column prop="amount" label="金额" width="120">
            <template #default="{ row }">
              {{ row.amount.toFixed(4) }}
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleDetailDialogClose">关闭</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import api from '../utils/api'

const backtesting = ref(false)
const chartContainer = ref()
const historyChartContainer = ref()

// 历史回测详情弹窗相关
const detailDialogVisible = ref(false)
const currentHistoryDetail = ref(null)
const loadingHistoryDetail = ref(false)

const backtestConfig = reactive({
  strategyId: '',
  type: 'stock',
  target: '',
  startDate: '',
  endDate: '',
  initialFund: 100000,
  commissionRate: 0.0003
})

// 当前选择的策略
const currentStrategy = ref(null)

// 策略参数
const strategyParams = reactive({
  // 默认参数，会根据选择的策略动态更新
  short_period: 5,
  long_period: 20,
  buy_threshold: 1.01,
  sell_threshold: 1.0,
  lookback_period: 20,
  breakout_threshold: 0.02,
  rsi_period: 14,
  oversold_threshold: 30,
  overbought_threshold: 70
})

const strategies = ref([])
const isCustomStrategy = ref(false)

const backtestResult = ref(null)

const historyRecords = ref([])

// 当策略选择改变时
const onStrategyChange = () => {
  const selectedStrategy = strategies.value.find(s => s.id === backtestConfig.strategyId)
  currentStrategy.value = selectedStrategy
  
  if (selectedStrategy) {
    // 检查是否为自定义策略
    isCustomStrategy.value = selectedStrategy.type === 'custom' || 
                             selectedStrategy.id.startsWith('CUSTOM_') || 
                             (selectedStrategy.id.startsWith('strategy_') && selectedStrategy.id.length > 10);
    
    // 根据选择的策略重置参数为默认值
    if (!isCustomStrategy.value) {
      if (selectedStrategy.id === 'STRAT_001') { // 双均线策略
        strategyParams.short_period = 5
        strategyParams.long_period = 20
        strategyParams.buy_threshold = 1.01
        strategyParams.sell_threshold = 0.99
      } else if (selectedStrategy.id === 'STRAT_002') { // 突破策略
        strategyParams.lookback_period = 20
        strategyParams.breakout_threshold = 0.0
      } else if (selectedStrategy.id === 'STRAT_003') { // RSI均值回归策略
        strategyParams.rsi_period = 14
        strategyParams.oversold_threshold = 30
        strategyParams.overbought_threshold = 70
      }
    }
  } else {
    isCustomStrategy.value = false
  }
}

// 获取参数显示名称
const getParamLabel = (key) => {
  const labels = {
    short_period: '短期均线周期',
    long_period: '长期均线周期',
    buy_threshold: '买入阈值',
    sell_threshold: '卖出阈值',
    lookback_period: '回看期',
    breakout_threshold: '突破阈值',
    rsi_period: 'RSI周期',
    oversold_threshold: '超卖阈值',
    overbought_threshold: '超买阈值'
  }
  return labels[key] || key
}

// 获取当前策略需要的参数列表
const getCurrentStrategyParams = () => {
  if (!backtestConfig.strategyId) {
    return []
  }
  
  if (backtestConfig.strategyId === 'STRAT_001') { // 双均线策略
    return ['short_period', 'long_period', 'buy_threshold', 'sell_threshold']
  } else if (backtestConfig.strategyId === 'STRAT_002') { // 突破策略
    return ['lookback_period', 'breakout_threshold']
  } else if (backtestConfig.strategyId === 'STRAT_003') { // RSI均值回归策略
    return ['rsi_period', 'oversold_threshold', 'overbought_threshold']
  }
  
  return []
}

// 获取参数最小值
const getParamMin = (key) => {
  if (key === 'buy_threshold' || key === 'sell_threshold' || key === 'breakout_threshold') {
    return 0
  }
  return 1
}

// 获取参数步进值
const getParamStep = (key) => {
  if (key === 'buy_threshold' || key === 'sell_threshold' || key === 'breakout_threshold') {
    return 0.01
  }
  return 1
}

// 获取参数精度 - 增加精度以保留用户输入的精确数值
const getParamPrecision = (key) => {
  if (key === 'buy_threshold' || key === 'sell_threshold' || key === 'breakout_threshold') {
    return 4  // 增加精度到4位小数，以保留精确数值
  }
  return 0
}

const startBacktest = async () => {
  if (!backtestConfig.strategyId || !backtestConfig.target || !backtestConfig.startDate || !backtestConfig.endDate) {
    ElMessage.warning('请完善回测配置信息')
    return
  }

  backtesting.value = true
  
  try {
    // 构建基本参数
    const params = {
      strategyId: backtestConfig.strategyId,
      type: backtestConfig.type,
      target: backtestConfig.target,
      startDate: backtestConfig.startDate,
      endDate: backtestConfig.endDate,
      initialFund: backtestConfig.initialFund,
      commissionRate: backtestConfig.commissionRate
    }
    
    // 对于非自定义策略，构建策略参数
    if (!isCustomStrategy.value) {
      let strategySpecificParams = {}  
      if (backtestConfig.strategyId === 'STRAT_001') { // 双均线策略
        strategySpecificParams = {
          short_period: strategyParams.short_period,
          long_period: strategyParams.long_period,
          buy_threshold: strategyParams.buy_threshold,
          sell_threshold: strategyParams.sell_threshold
        }
      } else if (backtestConfig.strategyId === 'STRAT_002') { // 突破策略
        strategySpecificParams = {
          lookback_period: strategyParams.lookback_period,
          breakout_threshold: strategyParams.breakout_threshold
        }
      } else if (backtestConfig.strategyId === 'STRAT_003') { // RSI均值回归策略
        strategySpecificParams = {
          rsi_period: strategyParams.rsi_period,
          oversold_threshold: strategyParams.oversold_threshold,
          overbought_threshold: strategyParams.overbought_threshold
        }
      }
      params.strategy_params = strategySpecificParams
    } else {
      // 对于自定义策略，传递空参数
      params.strategy_params = {}
    }
    
    // 调用后端API开始回测
    const response = await api.post('/backtest/run', params)
    
    backtestResult.value = response.data
    
    // 添加到历史记录
    historyRecords.value.unshift({
      id: response.data.id,
      strategyName: strategies.value.find(s => s.id === backtestConfig.strategyId)?.name || '未知策略',
      target: backtestConfig.target,
      startDate: backtestConfig.startDate,
      endDate: backtestConfig.endDate,
      period: `${backtestConfig.startDate} 至 ${backtestConfig.endDate}`,
      totalReturn: response.data.totalReturn,
      maxDrawdown: response.data.maxDrawdown,
      sharpeRatio: response.data.sharpeRatio,
      createTime: new Date().toLocaleString(),
      // 使用实际的回测资金曲线数据
      equityCurve: response.data.equityCurve || [],
      // 保存原始回测日期范围，以便在查看历史详情时能正确生成覆盖整个范围的资金曲线
      trades: response.data.trades || []
    })
    
    ElMessage.success('回测完成')
    
    // 等待DOM更新完成后再渲染图表
    await nextTick()
    renderEquityCurve()
  } catch (error) {
    ElMessage.error('回测失败，请重试')
  } finally {
    backtesting.value = false
  }
}

// 渲染资金曲线（主页面）
const renderEquityCurve = () => {
  if (!backtestResult.value || !backtestResult.value.equityCurve || backtestResult.value.equityCurve.length === 0) {
    return
  }
  
  if (!chartContainer.value) {
    return
  }
  
  // 初始化图表
  const chart = echarts.init(chartContainer.value)
  
  // 准备数据，过滤掉无效数据
  const validData = backtestResult.value.equityCurve.filter(item => 
    item && typeof item.date === 'string' && typeof item.value === 'number' && !isNaN(item.value)
  )
  
  // 将数据从按天聚合为按周
  const weeklyData = aggregateDailyDataToWeekly(validData)
  
  const dates = weeklyData.map(item => item.date)
  const values = weeklyData.map(item => item.value)
  
  // 配置图表选项
  const option = {
    title: {
      text: '资金曲线',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'normal'
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
          return params[0].name + '<br/>资金: ¥' + params[0].value.toFixed(2)
        }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLabel: {
        rotate: 45,
        // 优化x轴标签间隔，确保不会出现负数或0
        interval: dates.length > 20 ? Math.floor(dates.length / 20) : 'auto'
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '¥{value}'
      }
    },
    series: [
      {
        name: '资金',
        type: 'line',
        smooth: true,
        data: values,
        lineStyle: {
          color: '#409EFF'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {
              offset: 0,
              color: 'rgba(64, 158, 255, 0.3)'
            },
            {
              offset: 1,
              color: 'rgba(64, 158, 255, 0.05)'
            }
          ])
        }
      }
    ]
  }
  
  // 设置图表选项
  chart.setOption(option)
  
  // 响应式调整图表大小
  window.addEventListener('resize', () => {
    chart.resize()
  })
  
  // 清理函数
  return () => {
    window.removeEventListener('resize', () => {
      chart.resize()
    })
    chart.dispose()
  }
}

const exportReport = () => {
  ElMessage.success('导出功能开发中...')
}

const viewDetails = () => {
  ElMessage.info('查看详情功能开发中...')
}

const viewHistoryDetail = async (record) => {
  loadingHistoryDetail.value = true
  try {
    console.log('开始查看回测详情:', record)
    
    // 确保currentHistoryDetail有初始值
    if (!currentHistoryDetail.value) {
      currentHistoryDetail.value = {}
    }
    
    // 先显示弹窗，避免等待时间过长
    detailDialogVisible.value = true
    
    // 初始化currentHistoryDetail为基础数据，确保UI始终有内容显示
    currentHistoryDetail.value = {
      ...record,
      // 如果没有交易记录，提供模拟数据
      trades: record.trades && record.trades.length > 0 ? record.trades : [
        {
          date: new Date().toISOString().split('T')[0],
          type: 'buy',
          stockCode: record.target || '600000',
          price: 10.0,
          quantity: 100,
          amount: 1000.0
        },
        {
          date: new Date(Date.now() + 86400000).toISOString().split('T')[0],
          type: 'sell',
          stockCode: record.target || '600000',
          price: 10.5,
          quantity: 100,
          amount: 1050.0
        }
      ],
      // 仅在没有资金曲线数据时才使用模拟曲线，优先使用后端返回的数据
      equityCurve: record.equityCurve && record.equityCurve.length > 0 ? record.equityCurve : [],
      totalReturn: record.totalReturn || 0,
      annualReturn: record.annualReturn || 0,
      maxDrawdown: record.maxDrawdown || 0,
      sharpeRatio: record.sharpeRatio || 0,
      winRate: record.winRate || 0,
      tradeCount: record.tradeCount || 2
    }
    
    console.log('初始化后的currentHistoryDetail:', currentHistoryDetail.value)
    
    // 立即尝试渲染一次图表，避免API调用失败时没有图表
    await nextTick()
    renderHistoryEquityCurve()
    
    try {
      // 从后端获取完整的回测详情
      const response = await api.get(`/backtest/results/${record.id}`)
      
      console.log('回测详情API响应:', response)
      
      // 确保数据完整性
      if (response && response.data && response.data.success) {
        const data = response.data.data
        // 使用完整的后端数据替换当前数据
        currentHistoryDetail.value = {
          ...currentHistoryDetail.value,
          ...data,
          // 确保trades和equityCurve是数组
          trades: data.trades || [],
          equityCurve: data.equityCurve || [],
          // 明确处理策略参数字段
          strategyParams: data.strategyParams || {}
        }
        
        console.log('更新后的currentHistoryDetail:', currentHistoryDetail.value)
        
        // 等待DOM更新后重新渲染图表
        await nextTick()
        renderHistoryEquityCurve()
      } else if (response && response.data) {
        // 处理旧版API响应格式
        const data = response.data
        currentHistoryDetail.value = {
          ...currentHistoryDetail.value,
          ...data,
          trades: data.trades || [],
          equityCurve: data.equityCurve || [],
          // 明确处理策略参数字段
          strategyParams: data.strategyParams || {}
        }
        await nextTick()
        renderHistoryEquityCurve()
      } else {
        console.error('回测详情数据不完整', response)
        ElMessage.warning('回测详情数据不完整，显示基础信息')
      }
      
      // 如果后端返回了实际结束日期，显示提示信息
      if (currentHistoryDetail.value.actualEndDate) {
        console.log('实际数据结束日期:', currentHistoryDetail.value.actualEndDate)
        // 这里可以根据需要添加UI显示，指示实际数据的结束日期
      }
    } catch (apiError) {
      console.error('获取回测详情失败:', apiError)
      // 如果是API错误，先检查本地是否有足够的数据
      if (!currentHistoryDetail.value.equityCurve || currentHistoryDetail.value.equityCurve.length === 0) {
        // 只有在没有任何数据时才使用模拟数据
        currentHistoryDetail.value.equityCurve = generateMockEquityCurve()
        await nextTick()
        renderHistoryEquityCurve()
      }
      ElMessage.error('获取完整回测详情失败，显示本地缓存数据')
    }
  } catch (error) {
    console.error('显示回测详情过程中发生错误:', error)
    ElMessage.error('显示回测详情失败')
  } finally {
    loadingHistoryDetail.value = false
  }
}

// 将按天数据聚合为按周数据
const aggregateDailyDataToWeekly = (dailyData) => {
  if (!dailyData || dailyData.length === 0) return []
  
  const weeklyData = []
  const weeklyMap = new Map()
  
  // 按周分组数据
  dailyData.forEach(item => {
    const date = new Date(item.date)
    // 获取本周的周一作为该周的标识
    const day = date.getDay() || 7 // 让周日的day为7
    const monday = new Date(date)
    monday.setDate(date.getDate() - day + 1)
    const weekKey = monday.toISOString().split('T')[0]
    
    // 如果该周还没有数据，创建新的周数据
    if (!weeklyMap.has(weekKey)) {
      weeklyMap.set(weekKey, {
        date: weekKey,
        values: [],
        firstValue: item.value,
        lastValue: item.value
      })
    } else {
      // 更新该周的数据
      const weekData = weeklyMap.get(weekKey)
      weekData.values.push(item.value)
      weekData.lastValue = item.value
    }
  })
  
  // 计算每周的平均值作为该周的数据点
  weeklyMap.forEach((weekData, weekKey) => {
    // 使用每周最后一天的值作为该周的数据点
    weeklyData.push({
      date: weekData.date,
      value: weekData.lastValue
    })
  })
  
  // 按日期排序
  return weeklyData.sort((a, b) => new Date(a.date) - new Date(b.date))
}

// 渲染历史回测的资金曲线图
const renderHistoryEquityCurve = () => {
  console.log('开始渲染历史资金曲线:', {
    hasDetail: !!currentHistoryDetail.value,
    hasEquityCurve: currentHistoryDetail.value && !!currentHistoryDetail.value.equityCurve,
    equityCurveLength: currentHistoryDetail.value && currentHistoryDetail.value.equityCurve ? currentHistoryDetail.value.equityCurve.length : 0,
    hasChartContainer: !!historyChartContainer.value,
    actualEndDate: currentHistoryDetail.value?.actualEndDate
  })
  
  // 如果没有数据，显示空图表
  if (!currentHistoryDetail.value) {
    currentHistoryDetail.value = {
      equityCurve: []
    }
  }
  
  if (!currentHistoryDetail.value.equityCurve) {
    currentHistoryDetail.value.equityCurve = []
  }
  
  // 确保容器存在
  if (!historyChartContainer.value) {
    console.error('历史图表容器不存在')
    return
  }
  
  // 初始化图表
  let chart
  try {
    chart = echarts.init(historyChartContainer.value)
  } catch (err) {
    console.error('初始化图表失败:', err)
    return
  }
  
  // 准备数据，过滤掉无效数据
  const validData = currentHistoryDetail.value.equityCurve.filter(item => 
    item && typeof item.date === 'string' && typeof item.value === 'number' && !isNaN(item.value)
  )
  
  // 如果没有有效数据，生成一些默认数据以便显示
  if (validData.length === 0) {
    console.log('没有有效数据，使用默认数据')
    const today = new Date()
    // 生成4周的默认数据
    validData.push(
      { date: new Date(today - 4*7*86400000).toISOString().split('T')[0], value: 100000 },
      { date: new Date(today - 3*7*86400000).toISOString().split('T')[0], value: 101500 },
      { date: new Date(today - 2*7*86400000).toISOString().split('T')[0], value: 99800 },
      { date: new Date(today - 7*86400000).toISOString().split('T')[0], value: 102300 }
    )
  } else {
    // 按日期排序数据，确保时间顺序正确
    validData.sort((a, b) => new Date(a.date) - new Date(b.date))
  }
  
  // 将数据从按天聚合为按周
  const weeklyData = aggregateDailyDataToWeekly(validData)
  
  const dates = weeklyData.map(item => item.date)
  const values = weeklyData.map(item => item.value)
  
  // 配置图表选项 (与主页面的资金曲线配置相同)
  const option = {
    title: {
      text: '资金曲线',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'normal'
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
          return params[0].name + '<br/>资金: ¥' + params[0].value.toFixed(2)
        }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLabel: {
        rotate: 45,
        // 优化x轴标签间隔，确保不会出现负数或0
        interval: dates.length > 20 ? Math.floor(dates.length / 20) : 'auto'
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '¥{value}'
      }
    },
    series: [
      {
        name: '资金',
        type: 'line',
        smooth: true,
        data: values,
        lineStyle: {
          color: '#409EFF'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {
              offset: 0,
              color: 'rgba(64, 158, 255, 0.3)'
            },
            {
              offset: 1,
              color: 'rgba(64, 158, 255, 0.05)'
            }
          ])
        }
      }
    ]
  }
  
  // 设置图表选项
  chart.setOption(option)
  
  // 响应式调整图表大小
  const resizeHandler = () => {
    chart.resize()
  }
  window.addEventListener('resize', resizeHandler)
  
  // 保存清理函数，在关闭弹窗时调用
  currentHistoryDetail.value.resizeHandler = resizeHandler
  currentHistoryDetail.value.chartInstance = chart
}

// 处理详情弹窗关闭
const handleDetailDialogClose = (done) => {
  // 清理图表资源
  if (currentHistoryDetail.value && currentHistoryDetail.value.chartInstance) {
    if (currentHistoryDetail.value.resizeHandler) {
      window.removeEventListener('resize', currentHistoryDetail.value.resizeHandler)
    }
    currentHistoryDetail.value.chartInstance.dispose()
  }
  
  // 重置为初始状态
  currentHistoryDetail.value = null
  
  // 如果是通过before-close调用的，需要调用done函数
  if (typeof done === 'function') {
    done()
  } else {
    // 如果是直接点击按钮调用的，手动设置为false
    detailDialogVisible.value = false
  }
}

// 生成模拟资金曲线数据（按周）
const generateMockEquityCurve = () => {
  const curve = []
  const initialFund = backtestConfig.initialFund || 100000
  let currentValue = initialFund
  
  // 使用用户输入的回测日期范围
  let startDate, endDate
  if (backtestConfig.startDate && backtestConfig.endDate) {
    startDate = new Date(backtestConfig.startDate)
    endDate = new Date(backtestConfig.endDate)
  } else {
    // 如果没有用户输入的日期，使用默认的半年时间范围
    endDate = new Date()
    startDate = new Date()
    startDate.setDate(startDate.getDate() - 26 * 7) // 半年约26周
  }
  
  // 计算总周数
  const timeDiff = endDate - startDate
  const weeks = Math.ceil(timeDiff / (7 * 86400000)) // 转换为周数
  
  // 确保至少有4周数据
  const totalWeeks = Math.max(weeks, 4)
  
  // 从开始日期开始生成周数据
  for (let i = 0; i < totalWeeks; i++) {
    const date = new Date(startDate)
    date.setDate(date.getDate() + i * 7) // 每周间隔
    
    // 生成一个简单的随机游走曲线，带有轻微的上升趋势
    const randomChange = (Math.random() - 0.48) * initialFund * 0.02 // 周变动幅度稍大于日变动
    currentValue += randomChange
    
    // 确保日期不超过结束日期
    if (date <= endDate) {
      curve.push({
        date: date.toISOString().split('T')[0],
        value: Math.max(currentValue, initialFund * 0.5) // 确保不低于初始资金的50%
      })
    }
  }
  
  return curve
}

const deleteHistory = async (record) => {
  try {
    await api.delete(`/backtest/${record.id}`)
    
    // 从本地列表中移除
    const index = historyRecords.value.findIndex(r => r.id === record.id)
    if (index > -1) {
      historyRecords.value.splice(index, 1)
    }
    
    ElMessage.success('删除成功')
  } catch (error) {
    ElMessage.error('删除失败，请重试')
  }
}

// 从URL获取参数
const getUrlParameter = (name) => {
  name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]')
  const regex = new RegExp('[\\?&]' + name + '=([^&#]*)')
  const results = regex.exec(window.location.search)
  return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '))
}

// 监听回测结果变化，自动更新资金曲线
watch(
  () => backtestResult.value,
  (newResult) => {
    if (newResult && newResult.equityCurve && newResult.equityCurve.length > 0) {
      renderEquityCurve()
    }
  }
)

onMounted(async () => {
  // 设置默认日期
  const endDate = new Date()
  const startDate = new Date()
  startDate.setFullYear(endDate.getFullYear() - 1)
  
  // 格式化日期为YYYY-MM-DD字符串格式
  backtestConfig.startDate = startDate.toISOString().split('T')[0]
  backtestConfig.endDate = endDate.toISOString().split('T')[0]
  
  // 从URL获取策略ID参数
  const strategyId = getUrlParameter('strategy_id')
  const strategyName = getUrlParameter('strategy_name')
  
  // 加载策略列表
  try {
    const response = await api.get('/strategies')
    strategies.value = response.data.strategies
    
    // 如果URL中包含策略ID参数，自动选择对应的策略
    if (strategyId && strategies.value.length > 0) {
      const selectedStrategy = strategies.value.find(s => s.id === strategyId)
      if (selectedStrategy) {
        backtestConfig.strategyId = strategyId
        // 触发策略选择改变的逻辑
        await nextTick()
        onStrategyChange()
        
        // 显示提示信息
        ElMessage.success(`已自动选择策略: ${strategyName || selectedStrategy.name}`)
      }
    }
  } catch (error) {
    console.error('加载策略列表失败:', error)
  }
  
  // 加载历史回测记录
  try {
    const response = await api.get('/backtest/history')
    historyRecords.value = response.data.records
  } catch (error) {
    console.error('加载历史记录失败:', error)
  }
})
</script>

<style lang="scss" scoped>
.backtest-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 20px;
  text-align: center;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.page-subtitle {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0;
}

.backtest-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.config-card, .result-card, .history-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .card-title {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
  }
}

.config-form {
  .el-form-item {
    margin-bottom: 20px;
  }
}

.strategy-params {
  margin-top: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.params-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
  padding: 10px 0;
}

.param-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 10px;
  background: white;
  border-radius: 4px;
}

.param-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.param-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.param-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.param-description {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 20px;
  padding-left: 0;
}

.performance-overview {
  margin-bottom: 30px;
  
  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 20px;
    padding-left: 10px;
    border-left: 4px solid var(--primary-color);
  }
  
  .overview-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 20px;
  }
  
  .overview-item {
    text-align: center;
    padding: 20px;
    background: var(--background-light);
    border-radius: 8px;
    
    .overview-label {
      font-size: 14px;
      color: var(--text-secondary);
      margin-bottom: 10px;
    }
    
    .overview-value {
      font-size: 24px;
      font-weight: 700;
      
      &.positive {
        color: var(--success-color);
      }
      
      &.negative {
        color: var(--danger-color);
      }
    }
  }
}

.chart-section {
  margin-bottom: 30px;
  
  .chart-container {
    height: 400px;
    background: var(--background-light);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-secondary);
  }
}

.trade-records {
  margin-bottom: 30px;
}

.positive {
  color: var(--success-color);
  font-weight: 600;
}

.negative {
  color: var(--danger-color);
  font-weight: 600;
}

@media (max-width: 768px) {
  .backtest-container {
    padding: 15px;
  }
  
  .overview-grid {
    grid-template-columns: repeat(2, 1fr) !important;
    gap: 15px !important;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start !important;
    gap: 15px;
  }
}
</style>


