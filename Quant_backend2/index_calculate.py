#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pymysql
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import logging
import os
from typing import List, Dict, Any, Optional, Tuple

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

# 设置matplotlib中文字体支持
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题


class TechnicalIndicatorCalculator:
    """技术指标计算类"""
    
    def __init__(self, db_password: str = None):
        """
        初始化技术指标计算器
        
        Args:
            db_password: 数据库密码，如果为None则使用配置文件中的默认密码
        """
        self.db_password = db_password if db_password is not None else DB_DEFAULTS.get("password", "")
        self.connection = None
        self.logger = logger
        
    def connect_database(self):
        """连接数据库"""
        try:
            self.logger.info("连接数据库...")

            # 获取默认转换器并进行自定义
            conv = pymysql.converters.conversions.copy()
            conv[datetime.date] = pymysql.converters.escape_date
            conv[pymysql.FIELD_TYPE.DECIMAL] = float
            conv[pymysql.FIELD_TYPE.NEWDECIMAL] = float

            # 使用标准连接方式
            self.connection = pymysql.connect(
                host=DB_DEFAULTS["host"],
                port=DB_DEFAULTS["port"],
                user=DB_DEFAULTS["user"],
                password=self.db_password,
                database=DB_DEFAULTS["database"],
                charset=DB_DEFAULTS["charset"],
                autocommit=False,
                conv=conv,
            )

            self.logger.info("数据库连接成功")
        except Exception as e:
            self.logger.error(f"连接数据库失败: {e}")
            raise
    
    def close_database(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.logger.info("数据库连接已关闭")
    
    def get_stock_market_data(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        从数据库获取股票行情数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
        
        Returns:
            包含股票行情数据的DataFrame
        """
        try:
            self.logger.info(f"获取股票{stock_code}从{start_date}到{end_date}的行情数据")
            query = """
            SELECT stock_code, trade_date, open_price, high_price, low_price, close_price, 
                   pre_close_price, change_amount, change_percent, volume, amount
            FROM StockMarketData 
            WHERE stock_code = %s AND trade_date BETWEEN %s AND %s
            ORDER BY trade_date ASC
            """
            
            df = pd.read_sql(query, self.connection, params=(stock_code, start_date, end_date))
            
            if df.empty:
                self.logger.warning(f"未获取到股票{stock_code}的数据")
                return pd.DataFrame()
            
            # 转换日期格式
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            
            self.logger.info(f"成功获取{len(df)}条股票{stock_code}的行情数据")
            return df
        except Exception as e:
            self.logger.error(f"获取股票行情数据失败: {e}")
            return pd.DataFrame()
    
    def get_stock_valuation_data(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        从数据库获取股票估值数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
        
        Returns:
            包含股票估值数据的DataFrame
        """
        try:
            self.logger.info(f"获取股票{stock_code}从{start_date}到{end_date}的估值数据")
            query = """
            SELECT stock_code, trade_date, pe_ratio, pb_ratio, ps_ratio, 
                   market_cap, circulating_market_cap, turnover_ratio
            FROM StockValuation 
            WHERE stock_code = %s AND trade_date BETWEEN %s AND %s
            ORDER BY trade_date ASC
            """
            
            df = pd.read_sql(query, self.connection, params=(stock_code, start_date, end_date))
            
            if df.empty:
                self.logger.warning(f"未获取到股票{stock_code}的估值数据")
                return pd.DataFrame()
            
            # 转换日期格式
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            
            self.logger.info(f"成功获取{len(df)}条股票{stock_code}的估值数据")
            return df
        except Exception as e:
            self.logger.error(f"获取股票估值数据失败: {e}")
            return pd.DataFrame()
    
    def calculate_moving_average(self, df: pd.DataFrame, periods: List[int] = [5, 10, 20, 60]) -> pd.DataFrame:
        """
        计算移动平均线
        
        Args:
            df: 包含收盘价的数据框
            periods: 要计算的均线周期列表
        
        Returns:
            包含均线数据的数据框
        """
        result_df = df.copy()
        
        for period in periods:
            col_name = f"ma{period}"
            result_df[col_name] = result_df['close_price'].rolling(window=period).mean()
            
        return result_df
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        计算相对强弱指标(RSI)
        
        Args:
            df: 包含收盘价的数据框
            period: RSI计算周期
        
        Returns:
            包含RSI数据的数据框
        """
        result_df = df.copy()
        
        # 计算价格变动
        delta = result_df['close_price'].diff()
        
        # 分离上涨和下跌
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # 计算RSI
        rs = gain / loss
        result_df[f'rsi{period}'] = 100 - (100 / (1 + rs))
        
        return result_df
    
    def calculate_macd(self, df: pd.DataFrame, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> pd.DataFrame:
        """
        计算MACD指标
        
        Args:
            df: 包含收盘价的数据框
            fast_period: 快线周期
            slow_period: 慢线周期
            signal_period: 信号线周期
        
        Returns:
            包含MACD数据的数据框
        """
        result_df = df.copy()
        
        # 计算EMA
        ema_fast = result_df['close_price'].ewm(span=fast_period, adjust=False).mean()
        ema_slow = result_df['close_price'].ewm(span=slow_period, adjust=False).mean()
        
        # 计算MACD线和信号线
        result_df['macd_line'] = ema_fast - ema_slow
        result_df['signal_line'] = result_df['macd_line'].ewm(span=signal_period, adjust=False).mean()
        result_df['macd_hist'] = result_df['macd_line'] - result_df['signal_line']
        
        return result_df
    
    def calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, num_std: float = 2) -> pd.DataFrame:
        """
        计算布林带
        
        Args:
            df: 包含收盘价的数据框
            period: 计算周期
            num_std: 标准差倍数
        
        Returns:
            包含布林带数据的数据框
        """
        result_df = df.copy()
        
        # 计算中轨（移动平均线）
        result_df['bb_mid'] = result_df['close_price'].rolling(window=period).mean()
        
        # 计算标准差
        std = result_df['close_price'].rolling(window=period).std()
        
        # 计算上轨和下轨
        result_df['bb_upper'] = result_df['bb_mid'] + (std * num_std)
        result_df['bb_lower'] = result_df['bb_mid'] - (std * num_std)
        
        return result_df
    
    def calculate_kdj(self, df: pd.DataFrame, n: int = 9, m1: int = 3, m2: int = 3) -> pd.DataFrame:
        """
        计算KDJ指标
        
        Args:
            df: 包含最高价、最低价、收盘价的数据框
            n: RSV计算周期
            m1: K值平滑周期
            m2: D值平滑周期
        
        Returns:
            包含KDJ数据的数据框
        """
        result_df = df.copy()
        
        # 计算RSV
        low_min = result_df['low_price'].rolling(window=n).min()
        high_max = result_df['high_price'].rolling(window=n).max()
        result_df['rsv'] = (result_df['close_price'] - low_min) / (high_max - low_min) * 100
        
        # 计算K值和D值
        result_df['kdj_k'] = result_df['rsv'].ewm(com=m1-1, adjust=False).mean()
        result_df['kdj_d'] = result_df['kdj_k'].ewm(com=m2-1, adjust=False).mean()
        
        # 计算J值
        result_df['kdj_j'] = 3 * result_df['kdj_k'] - 2 * result_df['kdj_d']
        
        return result_df
    
    def visualize_price_and_ma(self, df: pd.DataFrame, stock_code: str, save_path: Optional[str] = None):
        """
        可视化价格和移动平均线
        
        Args:
            df: 包含价格和均线数据的数据框
            stock_code: 股票代码
            save_path: 图片保存路径，None则不保存
        """
        plt.figure(figsize=(14, 7))
        
        # 绘制价格和均线
        plt.plot(df['trade_date'], df['close_price'], label='收盘价', linewidth=2)
        
        # 查找所有均线列并绘制
        ma_columns = [col for col in df.columns if col.startswith('ma')]
        for col in ma_columns:
            plt.plot(df['trade_date'], df[col], label=col.upper())
        
        plt.title(f'{stock_code} 价格和移动平均线')
        plt.xlabel('日期')
        plt.ylabel('价格')
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        
        # 格式化日期显示
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
        plt.xticks(rotation=45)
        
        if save_path:
            plt.savefig(save_path)
            self.logger.info(f"价格和均线图已保存至: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def visualize_rsi(self, df: pd.DataFrame, stock_code: str, save_path: Optional[str] = None):
        """
        可视化RSI指标
        
        Args:
            df: 包含RSI数据的数据框
            stock_code: 股票代码
            save_path: 图片保存路径，None则不保存
        """
        plt.figure(figsize=(14, 5))
        
        # 查找所有RSI列并绘制
        rsi_columns = [col for col in df.columns if col.startswith('rsi')]
        for col in rsi_columns:
            plt.plot(df['trade_date'], df[col], label=col.upper())
        
        # 添加超买超卖线
        plt.axhline(y=70, color='r', linestyle='--', label='超买线(70)')
        plt.axhline(y=30, color='g', linestyle='--', label='超卖线(30)')
        
        plt.title(f'{stock_code} RSI指标')
        plt.xlabel('日期')
        plt.ylabel('RSI值')
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        
        # 格式化日期显示
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
        plt.xticks(rotation=45)
        
        if save_path:
            plt.savefig(save_path)
            self.logger.info(f"RSI指标图已保存至: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def visualize_macd(self, df: pd.DataFrame, stock_code: str, save_path: Optional[str] = None):
        """
        可视化MACD指标
        
        Args:
            df: 包含MACD数据的数据框
            stock_code: 股票代码
            save_path: 图片保存路径，None则不保存
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9), gridspec_kw={'height_ratios': [3, 1]})
        
        # 绘制价格图
        ax1.plot(df['trade_date'], df['close_price'], label='收盘价')
        ax1.set_title(f'{stock_code} 价格和MACD指标')
        ax1.set_ylabel('价格')
        ax1.grid(True)
        ax1.legend()
        
        # 绘制MACD图
        ax2.plot(df['trade_date'], df['macd_line'], label='MACD线')
        ax2.plot(df['trade_date'], df['signal_line'], label='信号线')
        ax2.bar(df['trade_date'], df['macd_hist'], label='MACD柱状图', alpha=0.5)
        ax2.set_xlabel('日期')
        ax2.set_ylabel('MACD值')
        ax2.grid(True)
        ax2.legend()
        
        # 格式化日期显示
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            self.logger.info(f"MACD指标图已保存至: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def visualize_bollinger_bands(self, df: pd.DataFrame, stock_code: str, save_path: Optional[str] = None):
        """
        可视化布林带
        
        Args:
            df: 包含布林带数据的数据框
            stock_code: 股票代码
            save_path: 图片保存路径，None则不保存
        """
        plt.figure(figsize=(14, 7))
        
        # 绘制价格和布林带
        plt.plot(df['trade_date'], df['close_price'], label='收盘价', linewidth=2)
        plt.plot(df['trade_date'], df['bb_upper'], label='上轨', linestyle='--', color='r')
        plt.plot(df['trade_date'], df['bb_mid'], label='中轨', linestyle='--', color='g')
        plt.plot(df['trade_date'], df['bb_lower'], label='下轨', linestyle='--', color='r')
        
        # 填充布林带区域
        plt.fill_between(df['trade_date'], df['bb_upper'], df['bb_lower'], alpha=0.1, color='gray')
        
        plt.title(f'{stock_code} 布林带指标')
        plt.xlabel('日期')
        plt.ylabel('价格')
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        
        # 格式化日期显示
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
        plt.xticks(rotation=45)
        
        if save_path:
            plt.savefig(save_path)
            self.logger.info(f"布林带指标图已保存至: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def visualize_kdj(self, df: pd.DataFrame, stock_code: str, save_path: Optional[str] = None):
        """
        可视化KDJ指标
        
        Args:
            df: 包含KDJ数据的数据框
            stock_code: 股票代码
            save_path: 图片保存路径，None则不保存
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9), gridspec_kw={'height_ratios': [3, 1]})
        
        # 绘制价格图
        ax1.plot(df['trade_date'], df['close_price'], label='收盘价')
        ax1.set_title(f'{stock_code} 价格和KDJ指标')
        ax1.set_ylabel('价格')
        ax1.grid(True)
        ax1.legend()
        
        # 绘制KDJ图
        ax2.plot(df['trade_date'], df['kdj_k'], label='K线')
        ax2.plot(df['trade_date'], df['kdj_d'], label='D线')
        ax2.plot(df['trade_date'], df['kdj_j'], label='J线')
        ax2.axhline(y=80, color='r', linestyle='--', label='超买线(80)')
        ax2.axhline(y=20, color='g', linestyle='--', label='超卖线(20)')
        ax2.set_xlabel('日期')
        ax2.set_ylabel('KDJ值')
        ax2.grid(True)
        ax2.legend()
        
        # 格式化日期显示
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            self.logger.info(f"KDJ指标图已保存至: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def visualize_valuation(self, df: pd.DataFrame, stock_code: str, save_path: Optional[str] = None):
        """
        可视化估值指标(PE、PB等)
        
        Args:
            df: 包含估值数据的数据框
            stock_code: 股票代码
            save_path: 图片保存路径，None则不保存
        """
        # 确保有数据
        if df.empty:
            self.logger.warning("没有估值数据可以可视化")
            return
        
        plt.figure(figsize=(14, 7))
        
        # 创建双Y轴
        ax1 = plt.subplot(111)
        ax2 = ax1.twinx()
        
        # 绘制PE和PB
        if 'pe_ratio' in df.columns:
            ax1.plot(df['trade_date'], df['pe_ratio'], label='PE市盈率', color='blue')
        if 'pb_ratio' in df.columns:
            ax1.plot(df['trade_date'], df['pb_ratio'], label='PB市净率', color='green')
        
        # 绘制换手率(使用右侧Y轴)
        if 'turnover_ratio' in df.columns:
            ax2.plot(df['trade_date'], df['turnover_ratio'], label='换手率', color='red', linestyle='--')
        
        # 设置标签和标题
        ax1.set_title(f'{stock_code} 估值指标')
        ax1.set_xlabel('日期')
        ax1.set_ylabel('PE/PB值')
        ax2.set_ylabel('换手率(%)')
        
        # 合并图例
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        ax1.grid(True)
        plt.tight_layout()
        
        # 格式化日期显示
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax1.xaxis.set_major_locator(mdates.MonthLocator())
        plt.xticks(rotation=45)
        
        if save_path:
            plt.savefig(save_path)
            self.logger.info(f"估值指标图已保存至: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def run_indicator_analysis(self, stock_code: str, start_date: str, end_date: str, 
                              indicators: List[str] = None, save_plots: bool = False):
        """
        运行完整的指标分析流程
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            indicators: 要计算的指标列表，None则计算所有指标
            save_plots: 是否保存图表
        """
        try:
            # 连接数据库
            self.connect_database()
            
            # 创建保存图表的目录
            if save_plots:
                plot_dir = f"indicator_plots_{stock_code}"
                os.makedirs(plot_dir, exist_ok=True)
            
            # 获取行情数据
            market_df = self.get_stock_market_data(stock_code, start_date, end_date)
            if market_df.empty:
                self.logger.warning("没有足够的行情数据进行分析")
                return
            
            # 获取估值数据
            valuation_df = self.get_stock_valuation_data(stock_code, start_date, end_date)
            
            # 确定要计算的指标
            default_indicators = ['ma', 'rsi', 'macd', 'bollinger', 'kdj']
            indicators_to_calculate = indicators if indicators else default_indicators
            
            # 计算各项指标
            result_df = market_df.copy()
            
            if 'ma' in indicators_to_calculate:
                result_df = self.calculate_moving_average(result_df)
                
            if 'rsi' in indicators_to_calculate:
                result_df = self.calculate_rsi(result_df)
                
            if 'macd' in indicators_to_calculate:
                result_df = self.calculate_macd(result_df)
                
            if 'bollinger' in indicators_to_calculate:
                result_df = self.calculate_bollinger_bands(result_df)
                
            if 'kdj' in indicators_to_calculate:
                result_df = self.calculate_kdj(result_df)
            
            # 可视化结果
            if 'ma' in indicators_to_calculate or 'bollinger' in indicators_to_calculate:
                save_path = os.path.join(plot_dir, f'{stock_code}_price_ma.png') if save_plots else None
                self.visualize_price_and_ma(result_df, stock_code, save_path)
            
            if 'rsi' in indicators_to_calculate:
                save_path = os.path.join(plot_dir, f'{stock_code}_rsi.png') if save_plots else None
                self.visualize_rsi(result_df, stock_code, save_path)
            
            if 'macd' in indicators_to_calculate:
                save_path = os.path.join(plot_dir, f'{stock_code}_macd.png') if save_plots else None
                self.visualize_macd(result_df, stock_code, save_path)
            
            if 'bollinger' in indicators_to_calculate:
                save_path = os.path.join(plot_dir, f'{stock_code}_bollinger.png') if save_plots else None
                self.visualize_bollinger_bands(result_df, stock_code, save_path)
            
            if 'kdj' in indicators_to_calculate:
                save_path = os.path.join(plot_dir, f'{stock_code}_kdj.png') if save_plots else None
                self.visualize_kdj(result_df, stock_code, save_path)
            
            # 可视化估值指标
            if not valuation_df.empty:
                save_path = os.path.join(plot_dir, f'{stock_code}_valuation.png') if save_plots else None
                self.visualize_valuation(valuation_df, stock_code, save_path)
            
            self.logger.info(f"股票{stock_code}的指标分析完成")
            
        except Exception as e:
            self.logger.error(f"指标分析过程中发生错误: {e}")
            raise
        finally:
            # 关闭数据库连接
            self.close_database()


if __name__ == "__main__":
    # 示例用法
    try:
        # 从命令行参数获取数据库密码，如果不提供则使用配置中的默认密码
        db_password = sys.argv[1] if len(sys.argv) > 1 else None
        
        # 创建指标计算器实例
        calculator = TechnicalIndicatorCalculator(db_password)
        
        # 运行指标分析
        # 可以修改股票代码、日期范围、指标列表和是否保存图表
        calculator.run_indicator_analysis(
            stock_code="600519.SH",  # 贵州茅台
            start_date="2024-01-01",
            end_date="2024-12-31",
            indicators=['ma', 'rsi', 'macd', 'bollinger', 'kdj'],
            save_plots=True
        )
        
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
        sys.exit(1)