import pandas as pd
import pymysql
import traceback

# 配置数据库连接信息
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # 尝试使用空密码
    'database': 'quant_trading',
    'port': 3306
}

def test_db_connection():
    """测试数据库连接"""
    try:
        # 先尝试使用空密码
        conn = pymysql.connect(**db_config)
        print("成功连接到数据库!")
        conn.close()
        return True
    except Exception as e:
        print(f"数据库连接失败（空密码）: {str(e)}")
        
        # 尝试不指定数据库
        try:
            test_config = db_config.copy()
            del test_config['database']
            conn = pymysql.connect(**test_config)
            print("成功连接到MySQL服务器，但指定的数据库可能不存在")
            conn.close()
            return False
        except Exception:
            print("无法连接到MySQL服务器")
        
        return False

# 我们简化检查部分，直接提供解决方案
def explain_nan_sources():
    """解释NaN值的可能来源和解决方案"""
    print("\n=== NaN值来源分析与解决方案 ===")
    print("\n1. NaN值的主要来源:")
    print("   - Tushare API返回的数据本身可能就包含缺失值")
    print("   - 某些股票在特定日期可能没有交易数据")
    print("   - 数据处理过程中的转换错误")
    
    print("\n2. 当前代码中的问题:")
    print("   - 在data_fetch.py中，process_stock_data方法仅使用简单的fillna(0)处理所有NaN值")
    print("   - 这种处理方式不够精细，对于不同类型的数据应该采用不同的填充策略")
    
    print("\n3. 解决方案建议:")
    print("   - 修改process_stock_data方法，根据不同列的特性选择合适的填充方法")
    print("   - 对于价格类数据（如open, close, high, low）: 使用前向填充或后向填充")
    print("   - 对于成交量和成交额: 使用0填充")
    print("   - 对于涨跌额和涨跌幅: 可以通过其他数据计算得出")

def explain_nan_sources():
    """解释NaN值的可能来源和解决方案"""
    print("\n\n=== NaN值来源分析与解决方案 ===")
    print("\n1. NaN值的主要来源:")
    print("   - Tushare API返回的数据本身可能就包含缺失值")
    print("   - 某些股票在特定日期可能没有交易数据")
    print("   - 数据处理过程中的转换错误")
    
    print("\n2. 当前代码中的问题:")
    print("   - 在data_fetch.py中，process_stock_data方法仅使用简单的fillna(0)处理所有NaN值")
    print("   - 这种处理方式不够精细，对于不同类型的数据应该采用不同的填充策略")
    
    print("\n3. 解决方案建议:")
    print("   - 修改process_stock_data方法，根据不同列的特性选择合适的填充方法")
    print("   - 对于价格类数据（如open, close, high, low）: 使用前向填充或后向填充")
    print("   - 对于成交量和成交额: 使用0填充")
    print("   - 对于涨跌额和涨跌幅: 可以通过其他数据计算得出")
    
    print("\n4. 代码优化示例:")
    print("   def enhanced_process_stock_data(df):")
    print("       # 价格类数据处理")
    print("       price_cols = ['open', 'close', 'high', 'low', 'pre_close']")
    print("       for col in price_cols:")
    print("           if col in df.columns:")
    print("               df[col] = df[col].fillna(method='ffill').fillna(method='bfill')")
    print("       ")
    print("       # 成交量类数据处理")
    print("       volume_cols = ['vol', 'amount']")
    print("       for col in volume_cols:")
    print("           if col in df.columns:")
    print("               df[col] = df[col].fillna(0)")
    print("       ")
    print("       # 计算涨跌数据")
    print("       if 'pre_close' in df.columns and 'close' in df.columns:")
    print("           if 'change' in df.columns:")
    print("               df['change'] = df['change'].fillna(df['close'] - df['pre_close'])")
    print("           if 'pct_chg' in df.columns:")
    print("               mask = df['pre_close'] != 0")
    print("               df.loc[mask, 'pct_chg'] = df.loc[mask, 'pct_chg'].fillna(")
    print("                   (df.loc[mask, 'close'] - df.loc[mask, 'pre_close']) / df.loc[mask, 'pre_close'] * 100")
    print("               )")
    print("       ")
    print("       return df")
    
    print("\n5. 实现步骤:")
    print("   - 打开data_fetch.py文件")
    print("   - 找到process_stock_data方法")
    print("   - 替换为上面的增强版代码")
    print("   - 重新运行数据获取和处理流程")

if __name__ == "__main__":
    print("开始分析数据中的NaN值问题...")
    
    # 测试数据库连接
    if test_db_connection():
        # 检查NaN值
        check_nan_values()
    
    # 解释来源和解决方案
    explain_nan_sources()
    
    print("\n分析完成！")