import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import traceback
from data_fetch import StockDataManager
from tushare_init import TushareCacheClient
import pymysql

# 设置中文字体
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

# 简单的数据库连接测试

def test_db_connection():
    """测试数据库连接是否正常"""
    print("\n===== 测试数据库连接 =====")
    try:
        # 尝试直接连接数据库
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='root',  # 假设密码是root，如果不是请修改
            database='quant_trading',
            port=3306
        )
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()[0]
        print(f"成功连接到数据库: {db_name}")
        
        # 检查stock_basic表是否存在
        cursor.execute("SHOW TABLES LIKE 'stock_basic'")
        if cursor.fetchone():
            # 查询表中的记录数
            cursor.execute("SELECT COUNT(*) FROM stock_basic")
            count = cursor.fetchone()[0]
            print(f"stock_basic表存在，有 {count} 条记录")
        else:
            print("stock_basic表不存在")
        
        # 检查daily表是否存在
        cursor.execute("SHOW TABLES LIKE 'daily'")
        if cursor.fetchone():
            # 查询表中的记录数
            cursor.execute("SELECT COUNT(*) FROM daily")
            count = cursor.fetchone()[0]
            print(f"daily表存在，有 {count} 条记录")
        else:
            print("daily表不存在")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"数据库连接测试失败: {str(e)}")
        print("错误详情:")
        traceback.print_exc()
        return False

def direct_query_sample_data():
    """直接从数据库查询样本数据进行分析"""
    print("\n===== 直接从数据库查询样本数据 =====")
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='root',  # 假设密码是root，如果不是请修改
            database='quant_trading',
            port=3306
        )
        
        # 查询一些股票代码
        query_stocks = "SELECT ts_code FROM stock_basic LIMIT 5"
        stock_df = pd.read_sql(query_stocks, conn)
        
        if stock_df.empty:
            print("未查询到股票代码")
            conn.close()
            return
        
        sample_codes = stock_df['ts_code'].tolist()
        print(f"查询到的样本股票代码: {sample_codes}")
        
        # 为每只股票查询最近10条数据
        for ts_code in sample_codes:
            print(f"\n查询股票 {ts_code} 的最近10条数据:")
            query_data = f"SELECT * FROM daily WHERE ts_code='{ts_code}' ORDER BY trade_date DESC LIMIT 10"
            try:
                df = pd.read_sql(query_data, conn)
                
                if df.empty:
                    print(f"  未查询到 {ts_code} 的数据")
                    continue
                
                # 计算NaN值统计
                total_cells = df.size
                # 注意：MySQL返回的None在pandas中会被转换为NaN
                nan_cells = df.isna().sum().sum()
                nan_percentage = (nan_cells / total_cells) * 100
                
                print(f"  数据形状: {df.shape}")
                print(f"  总单元格数: {total_cells}")
                print(f"  NaN单元格数: {nan_cells}")
                print(f"  NaN百分比: {nan_percentage:.2f}%")
                
                # 显示前几行数据供参考
                print("  数据前3行示例:")
                print(df.head(3))
            except Exception as e:
                print(f"  查询 {ts_code} 数据出错: {str(e)}")
                traceback.print_exc()
        
        conn.close()
    except Exception as e:
        print(f"直接查询数据库出错: {str(e)}")
        traceback.print_exc()

def propose_solutions():
    """提出解决NaN值问题的方案"""
    print("\n===== 解决NaN值问题的建议方案 =====")
    
    # 创建增强版的数据处理函数示例代码
    enhanced_processing_code = """# 增强版的process_stock_data函数示例
import pandas as pd
import numpy as np

def enhanced_process_stock_data(df):
    """增强版的数据处理函数，根据不同列的特性处理NaN值"""
    if df.empty:
        return df
    
    # 确保trade_date是字符串格式
    if 'trade_date' in df.columns:
        df['trade_date'] = df['trade_date'].astype(str)
    
    # 价格类数据（使用前向填充或后向填充）
    price_columns = ['open', 'close', 'high', 'low', 'pre_close']
    for col in price_columns:
        if col in df.columns:
            # 首先尝试前向填充，然后后向填充
            df[col] = df[col].fillna(method='ffill').fillna(method='bfill')
            # 如果还有NaN，使用列的均值填充
            if df[col].isna().any():
                df[col] = df[col].fillna(df[col].mean())
    
    # 成交量和成交额（用0填充）
    volume_columns = ['vol', 'amount']
    for col in volume_columns:
        if col in df.columns:
            df[col] = df[col].fillna(0)
    
    # 涨跌额和涨跌幅（使用计算值填充）
    if 'pre_close' in df.columns and 'close' in df.columns:
        if 'change' in df.columns:
            df['change'] = df['change'].fillna(df['close'] - df['pre_close'])
        if 'pct_chg' in df.columns:
            # 避免除零错误
            mask = df['pre_close'] != 0
            df.loc[mask, 'pct_chg'] = df.loc[mask, 'pct_chg'].fillna(
                (df.loc[mask, 'close'] - df.loc[mask, 'pre_close']) / df.loc[mask, 'pre_close'] * 100
            )
            # 处理pre_close为0的情况
            df['pct_chg'] = df['pct_chg'].fillna(0)
    
    return df"""
    
    print("\n根据对代码的分析，NaN值的主要来源和解决方法如下：")
    print("\n1. 数据获取阶段：")
    print("   - Tushare API返回的数据本身可能就包含NaN值")
    print("   - 某些股票在特定日期可能没有交易数据")
    print("   - 数据库中可能缺少某些股票的完整数据")
    
    print("\n2. 数据处理阶段：")
    print("   - 当前代码中`process_stock_data`方法仅使用简单的`fillna(0)`处理所有NaN值")
    print("   - 这种处理方式不够精细，对于不同类型的数据应该采用不同的填充策略")
    
    print("\n3. 解决方案示例：")
    print("   - 以下是一个增强版的数据处理函数示例，根据不同列的特性处理NaN值：")
    print(enhanced_processing_code)
    
    print("\n4. 数据完整性检查建议：")
    print("   - 在数据获取后添加自动的数据完整性检查")
    print("   - 对于缺失严重的数据，可以考虑重新获取")
    print("   - 使用时间序列插值方法处理连续型数据")
    
    print("\n5. 实现建议：")
    print("   - 修改`data_fetch.py`文件中的`process_stock_data`方法")
    print("   - 替换为上面的增强版处理函数，根据实际需求调整参数")
    print("   - 在数据获取过程中增加日志记录，追踪NaN值的来源")

if __name__ == "__main__":
    print("开始分析数据中的NaN值问题...")
    
    # 首先测试数据库连接
    db_connected = test_db_connection()
    
    # 如果数据库连接正常，尝试直接查询数据
    if db_connected:
        direct_query_sample_data()
    else:
        print("数据库连接失败，无法直接查询数据")
    
    # 提出解决方案
    propose_solutions()
    
    print("\n分析完成！")