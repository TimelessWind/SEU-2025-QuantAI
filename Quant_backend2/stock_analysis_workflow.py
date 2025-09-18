# -*- coding: utf-8 -*-

import sys
import pymysql
import tushare as ts
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

# 导入已有的类
from data_fetch import StockDataManager
from index_calculate import TechnicalIndicatorCalculator

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 数据库默认设置
DB_DEFAULTS = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "database": "quantitative_trading",
    "charset": "utf8mb4",
}

class StockAnalysisWorkflow:
    """股票分析工作流类"""
    
    def __init__(self, db_password: str = None):
        """
        初始化工作流
        
        Args:
            db_password: 数据库密码，如果为None则使用默认密码
        """
        self.db_password = db_password if db_password is not None else DB_DEFAULTS.get("password", "")
        self.logger = logger
        self.data_manager = None
        self.indicator_calculator = None
    
    def get_user_input(self) -> Tuple[str, str, str]:
        """
        获取用户输入的起止日期和股票代码
        
        Returns:
            tuple: (start_date, end_date, stock_code)
        """
        print("===== 股票分析工作流 =====")
        
        # 获取开始日期
        while True:
            start_date = input("请输入开始日期 (YYYY-MM-DD): ")
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
                break
            except ValueError:
                print("日期格式不正确，请重新输入！")
        
        # 获取结束日期
        while True:
            end_date = input("请输入结束日期 (YYYY-MM-DD): ")
            try:
                datetime.strptime(end_date, "%Y-%m-%d")
                # 检查结束日期是否大于开始日期
                if datetime.strptime(end_date, "%Y-%m-%d") < datetime.strptime(start_date, "%Y-%m-%d"):
                    print("结束日期不能早于开始日期，请重新输入！")
                    continue
                break
            except ValueError:
                print("日期格式不正确，请重新输入！")
        
        # 获取股票代码，默认600519.SH
        stock_code = input("请输入股票代码 (默认600519.SH): ")
        if not stock_code:
            stock_code = "600519.SH"
        
        print(f"\n您选择的参数：")
        print(f"- 开始日期: {start_date}")
        print(f"- 结束日期: {end_date}")
        print(f"- 股票代码: {stock_code}")
        
        return start_date, end_date, stock_code
    
    def clear_database_data(self, stock_code: str):
        """
        清空指定股票在数据库中的数据
        
        Args:
            stock_code: 股票代码
        """
        try:
            self.logger.info(f"清空股票{stock_code}在数据库中的数据...")
            
            # 连接数据库
            conn = pymysql.connect(
                host=DB_DEFAULTS["host"],
                port=DB_DEFAULTS["port"],
                user=DB_DEFAULTS["user"],
                password=self.db_password,
                database=DB_DEFAULTS["database"],
                charset=DB_DEFAULTS["charset"],
                autocommit=True
            )
            
            cursor = conn.cursor()
            
            # 清空股票市场数据表
            cursor.execute("DELETE FROM StockMarketData WHERE stock_code = %s", (stock_code,))
            self.logger.info(f"已清空StockMarketData表中{stock_code}的数据，影响行数: {cursor.rowcount}")
            
            # 清空股票估值数据表
            cursor.execute("DELETE FROM StockValuation WHERE stock_code = %s", (stock_code,))
            self.logger.info(f"已清空StockValuation表中{stock_code}的数据，影响行数: {cursor.rowcount}")
            
            # 关闭连接
            cursor.close()
            conn.close()
            
            self.logger.info(f"数据库数据清空完成")
        except Exception as e:
            self.logger.error(f"清空数据库数据失败: {e}")
            raise
    
    def reimport_data(self, stock_code: str, start_date: str, end_date: str):
        """
        重新导入指定股票的行情数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
        """
        try:
            # 从config.json读取Tushare API token
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    tushare_token = config.get('tushare_token', '')
                self.logger.info("成功从config.json读取Tushare API token")
            else:
                tushare_token = ""  # 没有配置文件时使用空token
                self.logger.warning("未找到config.json文件")
            
            self.data_manager = StockDataManager(
                db_password=self.db_password,
                tushare_token=tushare_token,
                start_date=start_date,
                end_date=end_date
            )
            
            # 连接数据库
            self.data_manager.connect_database()
            
            # 获取并导入股票数据
            self.logger.info(f"开始重新导入股票{stock_code}从{start_date}到{end_date}的数据...")
            
            # 使用StockDataManager的方法获取数据
            stock_data = self.data_manager.get_stock_data([stock_code])
            if stock_data.empty:
                self.logger.warning(f"未获取到股票{stock_code}的数据")
                return
            
            # 处理数据
            processed_data = self.data_manager.process_stock_data(stock_data)
            
            # 插入数据
            # 注意：这里需要确保StockDataManager类有insert_stock_data方法
            # 如果不存在，可能需要添加或调整方法名
            if hasattr(self.data_manager, 'insert_stock_data'):
                self.data_manager.insert_stock_data(processed_data)
            else:
                self.logger.error("StockDataManager类中不存在insert_stock_data方法")
                raise AttributeError("StockDataManager类中不存在insert_stock_data方法")
            
            self.logger.info(f"数据重新导入完成")
        except Exception as e:
            self.logger.error(f"数据重新导入失败: {e}")
            raise
    
    def run_indicator_analysis(self, stock_code: str, start_date: str, end_date: str):
        """
        运行指标分析和可视化
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
        """
        try:
            # 初始化指标计算器
            self.indicator_calculator = TechnicalIndicatorCalculator(self.db_password)
            
            # 运行指标分析
            self.logger.info(f"开始对股票{stock_code}进行指标分析和可视化...")
            
            # 使用TechnicalIndicatorCalculator的方法计算指标并可视化
            self.indicator_calculator.run_indicator_analysis(
                stock_code=stock_code,
                start_date=start_date,
                end_date=end_date,
                indicators=['ma', 'rsi', 'macd', 'bollinger', 'kdj'],
                save_plots=True
            )
            
            self.logger.info(f"指标分析和可视化完成")
        except Exception as e:
            self.logger.error(f"指标分析失败: {e}")
            raise
    
    def run_workflow(self):
        """运行完整的工作流"""
        try:
            # 步骤1: 获取用户输入
            start_date, end_date, stock_code = self.get_user_input()
            
            # 步骤2: 清空数据库并重新导入数据
            self.clear_database_data(stock_code)
            self.reimport_data(stock_code, start_date, end_date)
            
            # 步骤3: 运行指标分析和可视化
            self.run_indicator_analysis(stock_code, start_date, end_date)
            
            self.logger.info("\n===== 股票分析工作流已完成！=====")
        except KeyboardInterrupt:
            self.logger.info("\n用户中断了工作流")
        except Exception as e:
            self.logger.error(f"工作流运行失败: {e}")
            raise

if __name__ == "__main__":
    try:
        # 从命令行参数获取数据库密码，如果不提供则使用默认密码
        db_password = sys.argv[1] if len(sys.argv) > 1 else None
        
        # 创建工作流实例
        workflow = StockAnalysisWorkflow(db_password)
        
        # 运行工作流
        workflow.run_workflow()
        
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
        sys.exit(1)