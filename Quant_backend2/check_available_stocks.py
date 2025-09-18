# -*- coding: utf-8 -*-
"""
检查数据库中可用的股票数据
"""

import pandas as pd
import pymysql
import logging
from strategy_engine import DB_DEFAULTS

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def check_available_stocks():
    """检查数据库中可用的股票数据"""
    try:
        # 连接数据库
        connection = pymysql.connect(
            host=DB_DEFAULTS["host"],
            port=DB_DEFAULTS["port"],
            user=DB_DEFAULTS["user"],
            password=DB_DEFAULTS["password"],
            database=DB_DEFAULTS["database"],
            charset=DB_DEFAULTS["charset"],
            autocommit=False
        )
        logger.info("数据库连接成功")
        
        # 查询所有可用的股票代码
        query = """
        SELECT DISTINCT stock_code 
        FROM StockMarketData 
        ORDER BY stock_code
        """
        
        stock_codes_df = pd.read_sql(query, connection)
        
        if stock_codes_df.empty:
            logger.error("数据库中没有股票数据")
            return
        
        logger.info(f"数据库中共有{len(stock_codes_df)}只股票的数据")
        logger.info(f"股票代码列表: {', '.join(stock_codes_df['stock_code'].tolist())}")
        
        # 对于每只股票，查询其数据时间范围
        for _, row in stock_codes_df.iterrows():
            stock_code = row['stock_code']
            
            # 查询时间范围
            time_range_query = """
            SELECT MIN(trade_date) as start_date, MAX(trade_date) as end_date, COUNT(*) as data_count 
            FROM StockMarketData 
            WHERE stock_code = %s
            """
            
            time_range_df = pd.read_sql(time_range_query, connection, params=(stock_code,))
            
            if not time_range_df.empty:
                start_date = time_range_df.iloc[0]['start_date']
                end_date = time_range_df.iloc[0]['end_date']
                data_count = time_range_df.iloc[0]['data_count']
                
                logger.info(f"股票 {stock_code}: 数据范围从 {start_date} 到 {end_date}, 共 {data_count} 条记录")
                
                # 检查最近的数据
                latest_data_query = """
                SELECT * 
                FROM StockMarketData 
                WHERE stock_code = %s 
                ORDER BY trade_date DESC 
                LIMIT 10
                """
                
                latest_data_df = pd.read_sql(latest_data_query, connection, params=(stock_code,))
                if not latest_data_df.empty:
                    logger.info(f"股票 {stock_code} 最近的数据: ")
                    logger.info(latest_data_df[['trade_date', 'close_price']].to_string(index=False))
                    
    except Exception as e:
        logger.error(f"检查数据库时出现错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'connection' in locals() and connection:
            connection.close()
            logger.info("数据库连接已关闭")

if __name__ == "__main__":
    check_available_stocks()