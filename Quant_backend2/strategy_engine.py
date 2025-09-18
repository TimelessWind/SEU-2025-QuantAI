#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
策略引擎模块
实现各种量化交易策略，包括双均线策略、突破策略等
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from abc import ABC, abstractmethod
import pymysql

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


class BaseStrategy(ABC):
    """策略基类"""
    
    def __init__(self, strategy_name: str, params: Dict[str, Any]):
        self.strategy_name = strategy_name
        self.params = params

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        pass

    def validate_data(self, data: pd.DataFrame) -> bool:
        required_columns = {'trade_date', 'open_price', 'high_price', 'low_price', 'close_price'}
        return required_columns.issubset(data.columns)

class BreakoutStrategy(BaseStrategy):
    """突破策略"""
    
    def __init__(self, lookback_period: int = 20, breakout_threshold: float = 0.0, **kwargs):
        super().__init__("突破策略", {
            'lookback_period': lookback_period,
            'breakout_threshold': breakout_threshold
        })
        self.lookback_period = lookback_period
        self.breakout_threshold = breakout_threshold
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成突破策略信号"""
        if not self.validate_data(data):
            raise ValueError("数据格式不正确")
        
        df = data.copy()
        df = df.sort_values('trade_date').reset_index(drop=True)
        
        # 计算最高价和最低价的移动窗口
        df['high_max'] = df['high_price'].rolling(window=self.lookback_period).max()
        df['low_min'] = df['low_price'].rolling(window=self.lookback_period).min()
        
        # 计算突破阈值 - 修改为使用过去的收盘价作为基准
        df['upper_threshold'] = df['high_max'] * (1 + self.breakout_threshold)
        df['lower_threshold'] = df['low_min'] * (1 - self.breakout_threshold)
        
        # 初始化信号
        df['signal'] = 0
        df['position'] = 0
        
        # 生成交易信号
        for i in range(self.lookback_period, len(df)):
            # 向上突破买入 - 修改条件，使突破更容易触发
            if df.loc[i, 'close_price'] >= df.loc[i, 'high_max'] * (1 + self.breakout_threshold - 0.01):
                df.loc[i, 'signal'] = 1  # 买入
                df.loc[i, 'position'] = 1
            
            # 向下突破卖出
            elif df.loc[i, 'close_price'] <= df.loc[i, 'low_min'] * (1 - self.breakout_threshold + 0.01):
                df.loc[i, 'signal'] = -1  # 卖出
                df.loc[i, 'position'] = 0
            
            # 保持仓位
            else:
                df.loc[i, 'position'] = df.loc[i-1, 'position']
        
        return df


class MovingAverageStrategy(BaseStrategy):
    """双均线策略"""
    
    def __init__(self, short_period: int = 5, long_period: int = 20, 
                 buy_threshold: float = 1.002, sell_threshold: float = 0.998, **kwargs):
        super().__init__("双均线策略", {
            'short_period': short_period,
            'long_period': long_period,
            'buy_threshold': buy_threshold,
            'sell_threshold': sell_threshold
        })
        self.short_period = short_period
        self.long_period = long_period
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成双均线策略信号"""
        if not self.validate_data(data):
            raise ValueError("数据格式不正确")
        
        df = data.copy()
        df = df.sort_values('trade_date').reset_index(drop=True)
        
        # 计算短期和长期均线
        df['short_ma'] = df['close_price'].rolling(window=self.short_period).mean()
        df['long_ma'] = df['close_price'].rolling(window=self.long_period).mean()
        
        # 初始化信号
        df['signal'] = 0
        df['position'] = 0
        
        # 生成交易信号
        for i in range(self.long_period, len(df)):
            # 短期均线上穿长期均线且达到买入阈值，买入
            if (df.loc[i, 'short_ma'] / df.loc[i, 'long_ma'] >= self.buy_threshold and 
                df.loc[i-1, 'short_ma'] / df.loc[i-1, 'long_ma'] < self.buy_threshold):
                df.loc[i, 'signal'] = 1  # 买入
                df.loc[i, 'position'] = 1
            # 短期均线下穿长期均线且达到卖出阈值，卖出
            elif (df.loc[i, 'short_ma'] / df.loc[i, 'long_ma'] <= self.sell_threshold and 
                  df.loc[i-1, 'short_ma'] / df.loc[i-1, 'long_ma'] > self.sell_threshold):
                df.loc[i, 'signal'] = -1  # 卖出
                df.loc[i, 'position'] = 0
            # 保持仓位
            else:
                df.loc[i, 'position'] = df.loc[i-1, 'position']
        
        return df

class RSIMeanReversionStrategy(BaseStrategy):
    """RSI均值回归策略"""
    
    def __init__(self, rsi_period: int = 14, oversold_threshold: float = 30, 
                 overbought_threshold: float = 70, **kwargs):
        super().__init__("RSI均值回归策略", {
            'rsi_period': rsi_period,
            'oversold_threshold': oversold_threshold,
            'overbought_threshold': overbought_threshold
        })
        self.rsi_period = rsi_period
        self.oversold_threshold = oversold_threshold
        self.overbought_threshold = overbought_threshold
    
    def calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """计算RSI指标"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成RSI均值回归策略信号"""
        if not self.validate_data(data):
            raise ValueError("数据格式不正确")
        
        df = data.copy()
        df = df.sort_values('trade_date').reset_index(drop=True)
        
        # 计算RSI
        df['rsi'] = self.calculate_rsi(df['close_price'], self.rsi_period)
        
        # 初始化信号
        df['signal'] = 0
        df['position'] = 0
        
        # 生成交易信号
        for i in range(self.rsi_period, len(df)):
            # 超卖买入
            if df.loc[i, 'rsi'] < self.oversold_threshold:
                df.loc[i, 'signal'] = 1  # 买入
                df.loc[i, 'position'] = 1
            
            # 超买卖出
            elif df.loc[i, 'rsi'] > self.overbought_threshold:
                df.loc[i, 'signal'] = -1  # 卖出
                df.loc[i, 'position'] = 0
            
            # 保持仓位
            else:
                df.loc[i, 'position'] = df.loc[i-1, 'position']
        
        return df


class StrategyEngine:
    """策略引擎"""
    
    def __init__(self, db_password: str = None):
        self.db_password = db_password if db_password is not None else DB_DEFAULTS.get("password", "")
        self.connection = None
        self.logger = logger
        self.strategies = {
            'moving_average': MovingAverageStrategy,
            'breakout': BreakoutStrategy,
            'rsi_mean_reversion': RSIMeanReversionStrategy
        }
    
    def connect_database(self):
        """连接数据库"""
        try:
            self.logger.info("连接数据库...")
            self.connection = pymysql.connect(
                host=DB_DEFAULTS["host"],
                port=DB_DEFAULTS["port"],
                user=DB_DEFAULTS["user"],
                password=self.db_password,
                database=DB_DEFAULTS["database"],
                charset=DB_DEFAULTS["charset"],
                autocommit=False
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
    
    def get_stock_data(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取股票数据"""
        try:
            self.logger.info(f"获取股票{stock_code}从{start_date}到{end_date}的数据")
            query = """
            SELECT stock_code, trade_date, open_price, high_price, low_price, close_price, volume
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
            
            self.logger.info(f"成功获取{len(df)}条股票{stock_code}的数据")
            return df
        except Exception as e:
            self.logger.error(f"获取股票数据失败: {e}")
            return pd.DataFrame()
    
    def create_strategy(self, strategy_type: str, **kwargs) -> BaseStrategy:
        """创建策略实例"""
        if strategy_type not in self.strategies:
            raise ValueError(f"不支持的策略类型: {strategy_type}")
        
        strategy_class = self.strategies[strategy_type]
        return strategy_class(**kwargs)
    
    def run_strategy(self, stock_code: str, start_date: str, end_date: str, 
                    strategy_type: str, **strategy_params) -> pd.DataFrame:
        """运行策略"""
        try:
            # 连接数据库
            self.connect_database()
            
            # 获取数据
            data = self.get_stock_data(stock_code, start_date, end_date)
            if data.empty:
                raise ValueError(f"未获取到股票{stock_code}的数据")
            
            # 创建策略
            strategy = self.create_strategy(strategy_type, **strategy_params)
            
            # 生成信号
            signals = strategy.generate_signals(data)
            
            self.logger.info(f"策略{strategy_type}运行完成，生成{len(signals)}条信号")
            return signals
            
        except Exception as e:
            self.logger.error(f"策略运行失败: {e}")
            raise
        finally:
            self.close_database()
    
    def get_available_strategies(self) -> List[Dict[str, Any]]:
        """获取可用策略列表"""
        strategies = []
        for name, strategy_class in self.strategies.items():
            # 获取策略参数信息
            import inspect
            sig = inspect.signature(strategy_class.__init__)
            params = {}
            for param_name, param in sig.parameters.items():
                if param_name != 'self':
                    params[param_name] = {
                        'default': param.default if param.default != inspect.Parameter.empty else None,
                        'annotation': param.annotation.__name__ if hasattr(param.annotation, '__name__') else str(param.annotation)
                    }
            
            strategies.append({
                'name': name,
                'class_name': strategy_class.__name__,
                'description': strategy_class.__doc__ or f"{strategy_class.__name__}策略",
                'parameters': params
            })
        
        return strategies


if __name__ == "__main__":
    # 示例用法
    try:
        # 创建策略引擎
        engine = StrategyEngine()
        
        # 运行双均线策略
        signals = engine.run_strategy(
            stock_code="600519.SH",
            start_date="2024-01-01",
            end_date="2024-12-31",
            strategy_type="moving_average",
            short_period=5,
            long_period=20,
            buy_threshold=1.01,
            sell_threshold=1.0
        )
        
        print("策略信号生成完成")
        print(f"总信号数: {len(signals)}")
        print(f"买入信号数: {len(signals[signals['signal'] == 1])}")
        print(f"卖出信号数: {len(signals[signals['signal'] == -1])}")
        
        # 显示前几条信号
        print("\n前10条信号:")
        print(signals[['trade_date', 'close_price', 'signal', 'position']].head(10))
        
    except Exception as e:
        logger.error(f"程序运行出错: {e}")

