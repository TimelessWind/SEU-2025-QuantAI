#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
增强版股票筛选API实现
解决问题：
1. 地区、RSI、流动比率显示结果为空
2. 资产负债率筛选条件未生效
3. 市值和资产负债率小数位数优化
"""

import pymysql
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'quantitative_trading',
    'charset': 'utf8mb4'
}

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        raise

def calculate_rsi(stock_code, period=14):
    """
    计算指定股票的RSI指标
    
    Args:
        stock_code: 股票代码
        period: RSI计算周期
        
    Returns:
        float: RSI值（0-100之间）
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 获取最近N+1个交易日的收盘价数据
        # 先获取最近的交易日期
        cursor.execute("""
            SELECT MAX(trade_date) 
            FROM StockMarketData 
            WHERE stock_code = %s
        """, (stock_code,))
        latest_date = cursor.fetchone()[0]
        
        if not latest_date:
            logger.warning(f"未找到股票 {stock_code} 的交易数据")
            return 0
        
        # 计算N个交易日之前的日期
        # 由于我们需要N+1个数据点来计算N个变化值
        cursor.execute("""
            SELECT trade_date, close_price 
            FROM StockMarketData 
            WHERE stock_code = %s 
            AND trade_date <= %s 
            ORDER BY trade_date DESC 
            LIMIT %s
        """, (stock_code, latest_date, period + 1))
        
        results = cursor.fetchall()
        
        if len(results) < period + 1:
            logger.warning(f"股票 {stock_code} 的交易数据不足，无法计算RSI")
            return 0
        
        # 转换为DataFrame并按日期升序排列
        df = pd.DataFrame(results, columns=['trade_date', 'close_price'])
        df = df.sort_values('trade_date')
        
        # 计算价格变动
        delta = df['close_price'].diff()
        
        # 分离上涨和下跌
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # 计算RSI
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # 返回最新的RSI值
        latest_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 0
        
        cursor.close()
        connection.close()
        
        return round(float(latest_rsi), 2)  # 保留两位小数
        
    except Exception as e:
        logger.error(f"计算RSI失败: {e}")
        return 0

def filter_stocks(filter_params):
    """
    股票筛选功能的完整实现
    
    Args:
        filter_params: 包含所有筛选条件的字典
        
    Returns:
        dict: 包含筛选结果和总数的字典
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 构建基础查询
        base_query = """
            SELECT DISTINCT 
                sb.stock_code,
                sb.stock_name,
                sb.industry,
                sb.area,
                lsp.latest_price as current_price,
                lsp.change_percent,
                lsp.volume,
                sv.pe_ratio,
                sv.pb_ratio,
                sv.market_cap,
                bs.total_liability / bs.total_assets * 100 as debt_ratio,
                bs.total_current_assets / bs.total_current_liability as current_ratio,
                is_data.net_profit / bs.total_assets * 100 as roe
            FROM StockBasic sb
            LEFT JOIN LatestStockPrice lsp ON sb.stock_code = lsp.stock_code
            LEFT JOIN StockValuation sv ON sb.stock_code = sv.stock_code 
                AND sv.trade_date = (SELECT MAX(trade_date) FROM StockValuation WHERE stock_code = sb.stock_code)
            LEFT JOIN BalanceSheet bs ON sb.stock_code = bs.stock_code 
                AND bs.report_period = (SELECT MAX(report_period) FROM BalanceSheet WHERE stock_code = sb.stock_code)
            LEFT JOIN IncomeStatement is_data ON sb.stock_code = is_data.stock_code 
                AND is_data.report_period = (SELECT MAX(report_period) FROM IncomeStatement WHERE stock_code = sb.stock_code)
            WHERE 1=1
        """
        
        params = []
        
        # 应用筛选条件
        if filter_params.get('stockCode'):
            base_query += " AND sb.stock_code LIKE %s"
            params.append(f"%{filter_params['stockCode']}%")
        
        if filter_params.get('stockName'):
            base_query += " AND sb.stock_name LIKE %s"
            params.append(f"%{filter_params['stockName']}%")
        
        if filter_params.get('industry'):
            base_query += " AND sb.industry = %s"
            params.append(filter_params['industry'])
        
        if filter_params.get('priceMin') is not None:
            base_query += " AND lsp.latest_price >= %s"
            params.append(filter_params['priceMin'])
        
        if filter_params.get('priceMax') is not None:
            base_query += " AND lsp.latest_price <= %s"
            params.append(filter_params['priceMax'])
        
        if filter_params.get('peMin') is not None:
            base_query += " AND sv.pe_ratio >= %s"
            params.append(filter_params['peMin'])
        
        if filter_params.get('peMax') is not None:
            base_query += " AND sv.pe_ratio <= %s"
            params.append(filter_params['peMax'])
        
        if filter_params.get('pbMin') is not None:
            base_query += " AND sv.pb_ratio >= %s"
            params.append(filter_params['pbMin'])
        
        if filter_params.get('pbMax') is not None:
            base_query += " AND sv.pb_ratio <= %s"
            params.append(filter_params['pbMax'])
        
        if filter_params.get('marketCapMin') is not None:
            base_query += " AND sv.market_cap >= %s"
            params.append(filter_params['marketCapMin'] * 100000000)  # 转换为元
        
        if filter_params.get('marketCapMax') is not None:
            base_query += " AND sv.market_cap <= %s"
            params.append(filter_params['marketCapMax'] * 100000000)  # 转换为元
        
        # 资产负债率筛选
        if filter_params.get('debtRatioMin') is not None:
            base_query += " AND (bs.total_liability / bs.total_assets * 100) >= %s"
            params.append(filter_params['debtRatioMin'])
        
        if filter_params.get('debtRatioMax') is not None:
            base_query += " AND (bs.total_liability / bs.total_assets * 100) <= %s"
            params.append(filter_params['debtRatioMax'])
        
        # 地区筛选
        if filter_params.get('area'):
            base_query += " AND sb.area = %s"
            params.append(filter_params['area'])
        
        # 流动比率筛选
        if filter_params.get('currentRatioMin') is not None:
            base_query += " AND (bs.total_current_assets / bs.total_current_liability) >= %s"
            params.append(filter_params['currentRatioMin'])
        
        if filter_params.get('currentRatioMax') is not None:
            base_query += " AND (bs.total_current_assets / bs.total_current_liability) <= %s"
            params.append(filter_params['currentRatioMax'])
        
        # 添加排序和限制
        base_query += " ORDER BY sb.stock_code LIMIT 1000"
        
        cursor.execute(base_query, params)
        results = cursor.fetchall()
        
        # 格式化结果
        stocks = []
        for row in results:
            # 计算RSI值
            rsi_value = calculate_rsi(row[0])
            
            # 如果有RSI筛选条件，检查是否符合
            if filter_params.get('rsiMin') is not None and rsi_value < filter_params['rsiMin']:
                continue
            if filter_params.get('rsiMax') is not None and rsi_value > filter_params['rsiMax']:
                continue
            
            stock = {
                'stockCode': row[0],
                'stockName': row[1],
                'industry': row[2],
                'area': row[3] if row[3] else '',  # 地区信息
                'currentPrice': round(float(row[4]) if row[4] else 0, 2),
                'changePercent': round(float(row[5]) if row[5] else 0, 2),
                'volume': float(row[6]) if row[6] else 0,
                'peRatio': round(float(row[7]) if row[7] else 0, 2),
                'pbRatio': round(float(row[8]) if row[8] else 0, 2),
                'marketCap': round(float(row[9]) / 100000000, 2) if row[9] else 0,  # 转换为亿元，保留两位小数
                'debtRatio': round(float(row[10]) if row[10] else 0, 2),  # 资产负债率，保留两位小数
                'currentRatio': round(float(row[11]) if row[11] else 0, 2),  # 流动比率，保留两位小数
                'roe': round(float(row[12]) if row[12] else 0, 2),
                'rsi': rsi_value  # 计算并返回RSI值
            }
            stocks.append(stock)
        
        cursor.close()
        connection.close()
        
        return {'stocks': stocks, 'total': len(stocks)}
        
    except Exception as e:
        logger.error(f"股票筛选失败: {e}")
        return {'stocks': [], 'total': 0}

# 如果直接运行此脚本，提供一个测试功能
def test_filter():
    """测试股票筛选功能"""
    # 测试参数
    test_params = {
        'area': '上海',
        'debtRatioMin': 30,
        'debtRatioMax': 70
    }
    
    print("开始测试股票筛选功能...")
    print(f"测试参数: {test_params}")
    
    result = filter_stocks(test_params)
    
    print(f"筛选结果: 共找到 {result['total']} 只股票")
    if result['total'] > 0:
        print("前5只股票信息:")
        for stock in result['stocks'][:5]:
            print(f"代码: {stock['stockCode']}, 名称: {stock['stockName']}, \
                  地区: {stock['area']}, RSI: {stock['rsi']}, \
                  流动比率: {stock['currentRatio']}, 资产负债率: {stock['debtRatio']}%, \
                  市值: {stock['marketCap']}亿元")

if __name__ == '__main__':
    test_filter()