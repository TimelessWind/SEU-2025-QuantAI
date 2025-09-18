# 量化交易选股系统

一个基于Vue 3 + Flask的智能量化交易选股系统，支持多维度股票筛选、策略管理和回测分析。

## 系统特性

### 🎯 核心功能
- **用户管理**: 注册、登录、权限控制
- **股票筛选**: 多维度条件筛选优质股票
- **策略管理**: 创建和管理量化投资策略
- **回测分析**: 历史数据验证策略表现
- **实时数据**: 基于Tushare API的实时股票数据

### 📊 筛选维度
- **基础信息**: 股票代码、名称、行业
- **价格指标**: 当前价格、涨跌幅、成交量、成交额
- **估值指标**: PE、PB、PS、市值
- **财务指标**: 资产负债率、流动比率、ROE、净利润增长率
- **技术指标**: RSI、MACD、布林带、均线排列

### 🏗️ 技术架构
- **前端**: Vue 3 + Element Plus + Vite
- **后端**: Flask + PyMySQL + JWT
- **数据库**: MySQL
- **数据源**: Tushare API

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- MySQL 8.0+

### 1. 数据库设置

首先创建数据库并导入初始数据：

```bash
cd Quant_backend2
mysql -u root -p < init.sql
```

### 2. 后端启动

```bash
cd Quant_backend2
python start_backend.py
```

或者手动启动：

```bash
pip install -r flask_requirements.txt
python app.py
```

后端服务将在 http://localhost:8000 启动

### 3. 前端启动

Windows用户：
```bash
cd quant-frontend
start_frontend.bat
```

Linux/Mac用户：
```bash
cd quant-frontend
chmod +x start_frontend.sh
./start_frontend.sh
```

或者手动启动：

```bash
npm install
npm run dev
```

前端服务将在 http://localhost:3000 启动

### 4. 访问系统

打开浏览器访问 http://localhost:3000

默认管理员账号：
- 账号: admin
- 密码: hashed_password_here (需要在应用层设置)

## 数据准备

### 获取股票数据

使用提供的数据获取脚本：

```bash
cd Quant_backend2

# 准备单只股票数据
python data_fetch.py --start 2024-01-01 --end 2024-08-31 --stock 600519.SH

# 准备指数成分股数据
python data_fetch.py --start 2024-01-01 --end 2024-08-31 --index 000300.SH
```

### 配置Tushare API

在 `config.json` 中配置你的Tushare API Token：

```json
{
    "db_password": "123456",
    "tushare_token": "your_tushare_token_here"
}
```

## 使用指南

### 1. 用户注册/登录
- 首次使用需要注册账号
- 支持分析师和普通用户两种角色
- 使用JWT进行身份验证

### 2. 股票筛选
- 在"股票筛选"页面设置筛选条件
- 支持多维度组合筛选
- 实时查看筛选结果
- 支持导出筛选结果

### 3. 策略管理
- 查看内置策略（小市值策略、双均线策略等）
- 创建自定义策略
- 设置策略条件和参数

### 4. 回测分析
- 选择策略和回测参数
- 设置回测期间和初始资金
- 查看回测结果和收益曲线
- 分析交易记录

## API文档

### 认证接口
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `GET /auth/me` - 获取当前用户信息

### 股票接口
- `POST /stocks/filter` - 股票筛选
- `GET /stocks/industries` - 获取行业列表
- `GET /stocks/{stock_code}` - 获取股票详情

### 策略接口
- `GET /strategies` - 获取策略列表
- `POST /strategies` - 创建策略

### 统计接口
- `GET /stats/overview` - 获取统计概览

## 项目结构

```
quantAI2/
├── Quant_backend2/           # 后端目录
│   ├── app.py               # Flask主应用
│   ├── data_fetch.py        # 数据获取脚本
│   ├── init.sql            # 数据库初始化
│   ├── config.json         # 配置文件
│   └── flask_requirements.txt
├── quant-frontend/          # 前端目录
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   ├── components/     # 通用组件
│   │   ├── router/         # 路由配置
│   │   ├── stores/         # 状态管理
│   │   └── utils/          # 工具函数
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 开发说明

### 前端开发
- 使用Vue 3 Composition API
- Element Plus组件库
- Pinia状态管理
- Axios HTTP客户端

### 后端开发
- Flask RESTful API
- JWT身份验证
- MySQL数据库
- 跨域支持

### 数据库设计
- 用户表：存储用户信息和权限
- 股票基础信息表：股票基本信息
- 股票市场数据表：历史价格数据
- 股票估值数据表：PE、PB等估值指标
- 财务数据表：资产负债表、利润表
- 策略表：投资策略定义
- 回测报告表：回测结果记录

## 注意事项

1. **API限制**: Tushare API有调用频率限制，请合理使用
2. **数据更新**: 建议定期更新股票数据以保持数据新鲜度
3. **安全**: 生产环境请修改默认密码和JWT密钥
4. **性能**: 大量数据筛选时可能需要优化查询性能

## 常见问题

### Q: 如何获取Tushare API Token？
A: 访问 https://tushare.pro/register 注册账号，在个人中心获取Token

### Q: 数据库连接失败怎么办？
A: 检查MySQL服务是否启动，用户名密码是否正确

### Q: 前端页面空白怎么办？
A: 检查后端服务是否启动，API接口是否正常

### Q: 如何添加新的筛选条件？
A: 在后端`app.py`的`filter_stocks`函数中添加新的筛选逻辑

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

## 许可证

MIT License

