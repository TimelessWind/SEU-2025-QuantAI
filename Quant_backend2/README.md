# 量化交易选股系统前端

基于Vue 3 + Element Plus的量化交易选股系统前端界面。

## 功能特性

- 🔐 用户认证（登录/注册）
- 📊 股票筛选器（多维度筛选条件）
- 📈 策略管理
- 🔄 回测分析
- 📱 响应式设计

## 技术栈

- **框架**: Vue 3
- **UI库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP客户端**: Axios
- **构建工具**: Vite
- **图表库**: ECharts

## 筛选条件

### 基本信息
- 股票代码
- 行业分类
- 地区分布

### 估值指标
- 市盈率(PE)区间
- 市净率(PB)区间
- 市值区间

### 技术指标
- RSI相对强弱指标
- 均线关系（价格与均线、均线之间）

### 财务指标
- 资产负债率
- 流动比率

## 项目结构

```
quant-frontend/
├── src/
│   ├── components/          # 公共组件
│   ├── views/              # 页面组件
│   │   ├── Login.vue       # 登录页
│   │   ├── Register.vue    # 注册页
│   │   ├── Home.vue        # 首页
│   │   ├── StockFilter.vue # 股票筛选器
│   │   ├── Strategy.vue    # 策略管理
│   │   └── Backtest.vue    # 回测分析
│   ├── router/             # 路由配置
│   ├── stores/             # 状态管理
│   ├── utils/              # 工具函数
│   ├── assets/             # 静态资源
│   ├── App.vue             # 根组件
│   └── main.js             # 入口文件
├── package.json
├── vite.config.js
└── index.html
```

## 安装和运行

### 1. 安装依赖

```bash
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

### 3. 构建生产版本

```bash
npm run build
```

## 后端集成

前端通过代理配置连接到后端API：

```javascript
// vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

## API接口

### 认证接口
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册
- `GET /api/auth/me` - 获取用户信息

### 股票筛选接口
- `POST /api/stock/filter` - 股票筛选
- `GET /api/stock/industries` - 获取行业列表
- `GET /api/stock/areas` - 获取地区列表

### 策略管理接口
- `GET /api/strategy/list` - 获取策略列表
- `POST /api/strategy/create` - 创建策略
- `PUT /api/strategy/update` - 更新策略
- `DELETE /api/strategy/delete` - 删除策略

### 回测分析接口
- `GET /api/backtest/reports` - 获取回测报告
- `POST /api/backtest/run` - 运行回测
- `GET /api/backtest/download` - 下载报告

## 开发说明

### 添加新的筛选条件

1. 在 `StockFilter.vue` 中添加表单项
2. 在 `filterForm` 中添加对应的数据字段
3. 在后端API中实现相应的筛选逻辑

### 添加新的页面

1. 在 `src/views/` 中创建新的Vue组件
2. 在 `src/router/index.js` 中添加路由配置
3. 在侧边栏菜单中添加导航项

## 注意事项

- 确保后端服务运行在 http://localhost:8000
- 所有API请求都会自动添加认证头
- 登录状态会自动保存到localStorage
- 页面刷新时会自动检查登录状态

## 后续开发计划

- [ ] 股票详情页面
- [ ] 实时数据更新
- [ ] 图表可视化
- [ ] 策略编辑器
- [ ] 数据导出功能
- [ ] 移动端适配