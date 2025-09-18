# 后端2：策略与回测模块

## 概述

本模块实现了量化交易系统的策略与回测功能，包括：

1. **策略引擎** - 实现多种交易策略
2. **回测引擎** - 历史数据回测和性能指标计算
3. **API接口** - 提供策略管理和回测结果查询的REST API

## 功能特性

### 策略引擎 (strategy_engine.py)

- **双均线策略** - 基于短期和长期移动平均线的交叉信号
- **突破策略** - 基于价格突破历史高低点的交易信号
- **RSI均值回归策略** - 基于RSI指标的超买超卖信号
- **可扩展架构** - 支持自定义策略开发

### 策略编辑器 (strategy_editor.py) 🆕

- **自定义策略编写** - 研究员可以编写Python代码实现自己的策略
- **代码安全验证** - 自动验证策略代码的安全性，防止恶意代码执行
- **策略模板** - 提供常用策略模板，快速开始策略开发
- **实时验证** - 支持策略代码的实时验证和调试
- **策略保存** - 支持自定义策略的保存和管理

### 回测引擎 (backtest_engine.py)

- **历史数据回测** - 基于历史数据模拟交易过程
- **性能指标计算** - 收益率、最大回撤、夏普比率等
- **交易成本考虑** - 支持手续费和滑点设置
- **多策略比较** - 同时比较多个策略的表现

### API接口 (strategy_api.py)

- **策略管理** - 获取可用策略列表
- **信号生成** - 运行策略生成交易信号
- **回测执行** - 执行历史数据回测
- **结果查询** - 查询和比较回测结果
- **策略编辑器API** - 支持自定义策略的验证、运行和保存

## 安装依赖

```bash
pip install -r requirements_backend2.txt
```

## 前置准备（必须）

1. 初始化数据库（MySQL）
   - 打开终端进入项目根目录：`C:\Users\32948\Desktop\Quant`
   - 若使用 PowerShell，推荐以下方式（避免编码问题）：
     - 使用 mysql SOURCE（无交互密码示例）：
       ```powershell
       mysql -u root -p123456 --default-character-set=utf8mb4 -e "SOURCE C:/Users/32948/Desktop/Quant/init_mysql_compatible.sql"
       ```
     - 或 CMD 重定向：
       ```bat
       cmd /c "cd /d C:\Users\32948\Desktop\Quant && chcp 65001 >nul && mysql -u root -p123456 --default-character-set=utf8mb4 < init_mysql_compatible.sql"
       ```
   - 成功后验证：
     ```powershell
     mysql -u root -p123456 -e "SHOW DATABASES LIKE 'quantitative_trading'; USE quantitative_trading; SHOW TABLES;"
     ```

2. 准备行情数据（建议）
   - 确认 `config.json` 中配置了 `tushare_token` 和 `db_password`
   - 运行工作流导入数据：
     ```bash
     python stock_analysis_workflow.py 123456
     ```
     按提示输入日期区间与股票代码（例如：600519.SH）。该脚本会清空旧数据并重新拉取写入 `StockMarketData`。

## 使用方法

### 1. 启动API服务

```bash
python run_strategy_api.py [数据库密码]
```

服务将在 http://localhost:5000 启动（根路径不返回业务数据，若直接访问根路径出现“接口不存在”属正常，请访问 /api/* 路由）

### 2. 测试功能

```bash
python test_strategy_backtest.py
```

### 3. 策略编辑器使用 🆕

#### 前端界面使用
1. 启动API服务：`python run_strategy_api.py [数据库密码]`
2. 打开浏览器访问：`strategy_editor_frontend.html`
3. 选择策略模板或编写自定义代码
4. 设置回测参数并运行回测

#### 策略编辑器API接口

##### 获取策略模板
```bash
curl http://localhost:5000/api/strategy-editor/templates
```

##### 验证策略代码
```bash
curl -X POST http://localhost:5000/api/strategy-editor/validate \
  -H "Content-Type: application/json" \
  -d '{
    "code": "# 您的策略代码",
    "parameters": {}
  }'
```

##### 运行自定义策略
```bash
curl -X POST http://localhost:5000/api/strategy-editor/run \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "600519.SH",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "code": "# 您的策略代码",
    "parameters": {},
    "initial_capital": 100000.0,
    "commission_rate": 0.001
  }'
```

##### 保存自定义策略
```bash
curl -X POST http://localhost:5000/api/strategy-editor/save \
  -H "Content-Type: application/json" \
  -d '{
    "name": "我的策略",
    "code": "# 您的策略代码",
    "parameters": {},
    "description": "策略描述"
  }'
```

### 4. API接口使用示例

#### 获取策略列表
```bash
curl http://localhost:5000/api/strategies
```

PowerShell 可使用原生命令：
```powershell
Invoke-RestMethod -Method GET -Uri "http://localhost:5000/api/strategies"
```

#### 运行策略
```bash
curl -X POST http://localhost:5000/api/strategies/moving_average/run \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "600519.SH",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "strategy_type": "moving_average",
    "strategy_params": {
      "short_period": 5,
      "long_period": 20,
      "buy_threshold": 1.01,
      "sell_threshold": 1.0
    }
  }'
```

PowerShell 示例：
```powershell
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/api/strategies/moving_average/run" -ContentType "application/json" -Body '{
  "stock_code":"600519.SH","start_date":"2024-01-01","end_date":"2024-12-31",
  "strategy_type":"moving_average","strategy_params":{"short_period":5,"long_period":20}
}'
```

#### 运行回测
```bash
curl -X POST http://localhost:5000/api/backtest/run \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "600519.SH",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "strategy_type": "moving_average",
    "strategy_params": {
      "short_period": 5,
      "long_period": 20
    },
    "initial_capital": 100000.0,
    "commission_rate": 0.001,
    "user_id": "user001",
    "strategy_id": "STRAT_001"
  }'
```

注意：回测接口会将结果写入 `BacktestReport`，响应中返回 `report_id` 便于前端查询。

#### 比较策略
```bash
curl -X POST http://localhost:5000/api/backtest/compare \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "600519.SH",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "strategies": [
      {"type": "moving_average", "params": {"short_period": 5, "long_period": 20}},
      {"type": "breakout", "params": {"lookback_period": 20, "breakout_threshold": 0.02}}
    ],
    "initial_capital": 100000.0
  }'
```

Postman 使用指引：
- Method 选 POST，URL 填上述地址
- Headers: `Content-Type: application/json`
- Body: 选择 raw，粘贴 JSON 即可

## 策略参数说明

### 双均线策略 (moving_average)
- `short_period`: 短期均线周期 (默认: 5)
- `long_period`: 长期均线周期 (默认: 20)
- `buy_threshold`: 买入阈值 (默认: 1.01)
- `sell_threshold`: 卖出阈值 (默认: 1.0)

### 突破策略 (breakout)
- `lookback_period`: 回望周期 (默认: 20)
- `breakout_threshold`: 突破阈值 (默认: 0.02)

### RSI均值回归策略 (rsi_mean_reversion)
- `rsi_period`: RSI计算周期 (默认: 14)
- `oversold_threshold`: 超卖阈值 (默认: 30)
- `overbought_threshold`: 超买阈值 (默认: 70)

## 性能指标说明

- **总收益率**: 整个回测期间的总收益
- **年化收益率**: 按年计算的收益率
- **最大回撤**: 从峰值到谷值的最大跌幅
- **夏普比率**: 风险调整后的收益指标
- **胜率**: 盈利交易占总交易的比例
- **盈亏比**: 平均盈利与平均亏损的比值

## 数据库表结构

回测结果存储在 `BacktestReport` 表中，包含：
- 回测基本信息 (股票代码、时间范围、策略类型)
- 性能指标 (收益率、回撤、夏普比率等)
- 交易统计 (交易次数、胜率等)

## 策略编写指南 🆕

### 自定义策略编写

研究员可以通过以下方式编写自定义策略：

#### 1. 使用前端编辑器
- 打开 `strategy_editor_frontend.html`
- 选择策略模板或从零开始编写
- 实时验证和回测

#### 2. 策略代码结构
```python
# 策略代码示例
# 可用的数据列: trade_date, open_price, high_price, low_price, close_price, volume

# 计算技术指标
df['ma_5'] = df['close_price'].rolling(window=5).mean()
df['ma_20'] = df['close_price'].rolling(window=20).mean()

# 生成交易信号
for i in range(20, len(df)):
    # 买入条件
    if df.loc[i, 'ma_5'] > df.loc[i, 'ma_20'] and df.loc[i-1, 'ma_5'] <= df.loc[i-1, 'ma_20']:
        df.loc[i, 'signal'] = 1  # 买入信号
        df.loc[i, 'position'] = 1  # 持仓状态
    
    # 卖出条件
    elif df.loc[i, 'ma_5'] < df.loc[i, 'ma_20'] and df.loc[i-1, 'ma_5'] >= df.loc[i-1, 'ma_20']:
        df.loc[i, 'signal'] = -1  # 卖出信号
        df.loc[i, 'position'] = 0  # 空仓状态
    
    # 保持仓位
    else:
        df.loc[i, 'position'] = df.loc[i-1, 'position']
```

#### 3. 可用的Python功能
- **数据处理**: pandas (pd), numpy (np)
- **数学函数**: math, min, max, sum, abs, round
- **类型转换**: int, float, str, bool
- **数据结构**: list, dict, tuple
- **控制流**: for, while, if, else

#### 4. 安全限制
- 禁止导入危险模块 (os, sys, subprocess等)
- 禁止执行系统命令
- 禁止文件操作
- 禁止网络访问

## 扩展开发

### 添加新策略

1. 继承 `BaseStrategy` 类
2. 实现 `generate_signals` 方法
3. 在 `StrategyEngine` 中注册新策略

### 添加策略模板

在 `StrategyTemplate.get_templates()` 方法中添加新的策略模板。

### 自定义性能指标

在 `BacktestEngine.calculate_performance_metrics` 方法中添加新的指标计算。

## 注意事项

1. 确保数据库连接正常
2. 股票数据需要预先导入到数据库（若未导入，将出现“未获取到数据”的提示）
3. 回测结果会自动保存到数据库
4. API服务支持跨域请求
5. 建议在生产环境中使用WSGI服务器部署

附加提示：
- 字体告警（findfont）仅影响中文显示，可在绘图前设置：
  ```python
  import matplotlib
  import matplotlib.pyplot as plt
  matplotlib.set_loglevel("error")
  plt.rcParams["font.family"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
  plt.rcParams["axes.unicode_minus"] = False
  ```
- 根路径返回“接口不存在”属正常，请访问 `/api/health` 验证服务状态

## 故障排除

1. **数据库连接失败**: 检查数据库配置和密码
2. **策略运行失败**: 检查股票数据是否存在（用 SQL 验证 `SELECT COUNT(*) FROM StockMarketData WHERE stock_code='600519.SH';`）
3. **API请求失败**: 检查请求参数格式
4. **回测结果异常**: 检查策略参数设置；若夏普比率极端值，多为波动率接近 0，已做安全保护
5. **执行 SQL 报编码错误**: 用 `--default-character-set=utf8mb4` 或改用 `SOURCE` 执行

## 更新日志

- v1.0.0: 初始版本，实现基础策略和回测功能
- 支持双均线、突破、RSI三种策略
- 完整的API接口和数据库存储
- v1.1.0: 新增策略编辑器功能 🆕
- 支持研究员编写自定义策略
- 提供策略模板和代码验证
- 前端可视化策略编辑器
- 自定义策略的保存和管理

