import pandas as pd
import numpy as np
import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入后端相关模块
try:
    from Quant_backend2.strategy_engine import StrategyEngine
    from Quant_backend2.backtest_engine import BacktestEngine
    from Quant_backend2.strategy_editor import CustomStrategy, StrategyValidator
    print("成功导入后端模块")
except Exception as e:
    print(f"导入后端模块失败: {e}")
    # 如果导入失败，创建简化版的测试函数
def test_signal_generation():
    print("=== 开始详细调试分析 ==="
          "\n问题：前端显示交易次数为0，可能的原因分析：")
    
    # 1. 检查数据格式和字段名
    print("\n1. 检查数据库数据格式和字段名...")
    try:
        import sqlite3
        conn = sqlite3.connect('stock_data.db')
        
        # 检查表结构
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"数据库中的表: {tables}")
        
        # 检查stock_daily表结构
        if any('stock_daily' in table[0] for table in tables):
            cursor.execute("PRAGMA table_info(stock_daily);")
            columns = cursor.fetchall()
            print("stock_daily表的字段:")
            for col in columns:
                print(f"- {col[1]} ({col[2]})")
            
            # 检查数据量
            cursor.execute("SELECT COUNT(*) FROM stock_daily WHERE stock_code='600519.SH';")
            count = cursor.fetchone()[0]
            print(f"股票600519.SH的数据条数: {count}")
            
            # 查看部分数据
            cursor.execute("SELECT trade_date, close_price, open, high, low, volume FROM stock_daily WHERE stock_code='600519.SH' ORDER BY trade_date DESC LIMIT 5;")
            recent_data = cursor.fetchall()
            print("最近5条数据:")
            for row in recent_data:
                print(row)
        else:
            print("未找到stock_daily表")
        
        conn.close()
    except Exception as e:
        print(f"检查数据库失败: {e}")
    
    # 2. 模拟策略执行过程
    print("\n2. 模拟策略执行过程...")
    try:
        # 创建模拟数据
        dates = pd.date_range('2025-01-02', periods=117)
        np.random.seed(42)  # 设置随机种子，确保结果可复现
        prices = 100 + np.cumsum(np.random.normal(0.1, 1, size=117))
        
        df = pd.DataFrame({
            'trade_date': dates,
            'close_price': prices
        })
        
        # 设置索引为整数索引
        df.index = range(len(df))
        
        print(f"模拟数据: {len(df)}条记录")
        print(f"价格范围: {min(prices):.2f} - {max(prices):.2f}")
        
        # 执行策略函数
        print("\n执行修复后的策略函数:")
        result_df = execute_strategy(df.copy())
        
        # 分析结果
        signals = result_df[result_df['signal'] != 0]
        print(f"\n策略测试结果:")
        print(f"生成的交易信号数量: {len(signals)}")
        print("信号详情:")
        if len(signals) > 0:
            print(signals[['trade_date', 'close_price', 'signal', 'position', 'short_ma', 'long_ma']])
            
            # 计算交易次数
            trade_count = len(signals)
            print(f"\n交易次数: {trade_count}")
        else:
            print("未生成任何交易信号")
            
            # 检查均线数据
            print("\n检查均线数据:")
            print(f"短期均线缺失值数量: {result_df['short_ma'].isna().sum()}")
            print(f"长期均线缺失值数量: {result_df['long_ma'].isna().sum()}")
            
            # 打印部分数据查看均线关系
            print("\n部分数据查看均线关系:")
            print(result_df[['trade_date', 'close_price', 'short_ma', 'long_ma']].iloc[20:30])
            
            # 分析为何没有生成信号
            print("\n分析为何没有生成信号:")
            start_idx = max(5, 20)
            for i in range(start_idx, min(start_idx + 10, len(df))):
                if not np.isnan(result_df.loc[i, 'short_ma']) and not np.isnan(result_df.loc[i, 'long_ma']):
                    short_ma = result_df.loc[i, 'short_ma']
                    long_ma = result_df.loc[i, 'long_ma']
                    print(f"索引{i}: 短期均线={short_ma:.2f}, 长期均线={long_ma:.2f}, 差值={short_ma-long_ma:.2f}")
    except Exception as e:
        print(f"模拟策略执行失败: {e}")
    
    # 3. 检查前后端数据交互可能的问题
    print("\n3. 前后端数据交互可能的问题分析:")
    print("可能的原因:")
    print("- 数据类型不匹配：前端期望的字段名或数据格式与后端返回不一致")
    print("- 空数据处理：某些情况下返回的DataFrame可能为空")
    print("- 信号阈值问题：实际数据中可能很少出现短期均线上穿/下穿长期均线的情况")
    print("- 时间范围问题：当前选择的时间范围内可能没有满足条件的交易信号")
    print("- 前端显示逻辑问题：可能后端生成了信号但前端没有正确展示")
    
    print("\n=== 调试分析完成 ===")
    
# 修复后的策略函数
def execute_strategy(df):
    # 计算短期均线和长期均线 - 注意数据库中字段名为close_price
    df['short_ma'] = df['close_price'].rolling(window=5).mean()
    df['long_ma'] = df['close_price'].rolling(window=20).mean()
    
    # 初始化信号和持仓列
    df['signal'] = 0  # 0: 无操作, 1: 买入, -1: 卖出
    df['position'] = 0  # 0: 空仓, 1: 持仓
    
    # 生成交易信号：使用简化逻辑
    # 避免使用未来函数：确保有足够的数据计算均线
    start_idx = max(5, 20)  # 使用较大的窗口长度作为起始索引
    
    # 初始化持仓状态
    current_position = 0
    
    # 记录每一步的判断
    print("信号生成过程记录:")
    for i in range(start_idx, len(df)):
        # 检查均线值是否有效
        if not np.isnan(df.loc[i, 'short_ma']) and not np.isnan(df.loc[i, 'long_ma']):
            # 打印判断条件
            short_ma = df.loc[i, 'short_ma']
            long_ma = df.loc[i, 'long_ma']
            ma_cross = "上穿" if short_ma > long_ma else "下穿" if short_ma < long_ma else "持平"
            
            # 简化的信号生成逻辑
            if short_ma > long_ma and current_position == 0:
                df.loc[i, 'signal'] = 1  # 买入信号
                current_position = 1
                print(f"索引 {i}: 短期均线{ma_cross}长期均线，当前空仓，生成买入信号")
            elif short_ma < long_ma and current_position == 1:
                df.loc[i, 'signal'] = -1  # 卖出信号
                current_position = 0
                print(f"索引 {i}: 短期均线{ma_cross}长期均线，当前持仓，生成卖出信号")
            else:
                if i % 20 == 0:  # 每20条记录打印一次，避免输出过多
                    print(f"索引 {i}: 短期均线{ma_cross}长期均线，持仓状态{current_position}，不生成信号")
    
    # 根据信号调整持仓 - 使用.loc索引
    for i in range(1, len(df)):
        if df.loc[i, 'signal'] == 1:
            df.loc[i, 'position'] = 1  # 买入并持有
        elif df.loc[i, 'signal'] == -1:
            df.loc[i, 'position'] = 0  # 卖出并空仓
        else:
            df.loc[i, 'position'] = df.loc[i-1, 'position']  # 保持之前的持仓
    
    return df

# 如果是独立运行，执行测试
if __name__ == "__main__":
    test_signal_generation()