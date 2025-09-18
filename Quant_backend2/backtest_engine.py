#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
回测引擎模块
实现历史数据回测和性能指标计算
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import pymysql
from strategy_engine import StrategyEngine, BaseStrategy

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


class BacktestResult:
    """回测结果类"""
    
    def __init__(self):
        self.initial_capital = 0.0
        self.final_capital = 0.0
        self.total_return = 0.0
        self.annual_return = 0.0
        self.max_drawdown = 0.0
        self.sharpe_ratio = 0.0
        self.win_rate = 0.0
        self.profit_loss_ratio = 0.0
        self.trade_count = 0
        self.trades = []
        self.equity_curve = []
        self.daily_returns = []
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'initial_capital': self.initial_capital,
            'final_capital': self.final_capital,
            'total_return': self.total_return,
            'annual_return': self.annual_return,
            'max_drawdown': self.max_drawdown,
            'sharpe_ratio': self.sharpe_ratio,
            'win_rate': self.win_rate,
            'profit_loss_ratio': self.profit_loss_ratio,
            'trade_count': self.trade_count,
            'trades': self.trades,
            'equity_curve': self.equity_curve,
            'daily_returns': self.daily_returns
        }


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, db_password: str = None):
        self.db_password = db_password if db_password is not None else DB_DEFAULTS.get("password", "")
        self.connection = None
        self.logger = logger
        self.strategy_engine = StrategyEngine(db_password)
    
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
    
    def calculate_performance_metrics(self, equity_curve: List[float], 
                                    daily_returns: List[float], 
                                    initial_capital: float) -> Dict[str, float]:
        """计算性能指标"""
        if not equity_curve or not daily_returns:
            return {}
        
        equity_series = pd.Series(equity_curve).astype(float)
        returns_series = pd.Series(daily_returns).astype(float)

        # 清理异常值
        returns_series = returns_series.replace([np.inf, -np.inf], np.nan).dropna()
        if returns_series.empty:
            return {
                'total_return': 0.0,
                'annual_return': 0.0,
                'max_drawdown': 0.0,
                'sharpe_ratio': 0.0,
                'win_rate': 0.0,
                'profit_loss_ratio': 0.0,
            }
        
        # 总收益率
        total_return = (equity_series.iloc[-1] - initial_capital) / initial_capital
        
        # 年化收益率
        trading_days = len(equity_curve)
        years = trading_days / 252  # 假设一年252个交易日
        annual_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        
        # 最大回撤
        peak = equity_series.expanding().max()
        drawdown = (equity_series - peak) / peak
        max_drawdown = abs(drawdown.min())
        
        # 夏普比率
        risk_free_rate = 0.03  # 假设无风险利率3%
        excess_returns = returns_series - risk_free_rate / 252
        std = excess_returns.std()
        if std is None or np.isnan(std) or std < 1e-8:
            sharpe_ratio = 0.0
        else:
            sharpe_ratio = excess_returns.mean() / std * np.sqrt(252)
        
        # 胜率
        positive_returns = returns_series[returns_series > 0]
        win_rate = len(positive_returns) / len(returns_series) if len(returns_series) > 0 else 0
        
        # 盈亏比
        avg_win = positive_returns.mean() if len(positive_returns) > 0 else 0
        negative_returns = returns_series[returns_series < 0]
        avg_loss = abs(negative_returns.mean()) if len(negative_returns) > 0 else 0
        profit_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 0
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'win_rate': win_rate,
            'profit_loss_ratio': profit_loss_ratio
        }
    
    def simulate_trading(self, signals: pd.DataFrame, initial_capital: float = 100000.0,
                        commission_rate: float = 0.001) -> BacktestResult:
        """模拟交易过程"""
        result = BacktestResult()
        result.initial_capital = initial_capital
        
        # 初始化
        capital = initial_capital
        position = 0  # 持仓数量
        entry_price = 0.0
        trades = []
        equity_curve = [initial_capital]
        daily_returns = [0.0]
        
        for i, row in signals.iterrows():
            current_price = row['close_price']
            signal = row['signal']
            
            # 计算当前市值
            current_value = capital + position * current_price
            equity_curve.append(current_value)
            
            # 计算日收益率
            if i > 0:
                daily_return = (current_value - equity_curve[-2]) / equity_curve[-2]
                daily_returns.append(daily_return)
            
            # 处理交易信号
            if signal == 1 and position == 0:  # 买入信号且无持仓
                # 计算可买入数量
                available_capital = capital * 0.95  # 保留5%现金
                shares_to_buy = int(available_capital / current_price)
                
                if shares_to_buy > 0:
                    # 计算手续费
                    commission = shares_to_buy * current_price * commission_rate
                    total_cost = shares_to_buy * current_price + commission
                    
                    if total_cost <= capital:
                        position = shares_to_buy
                        capital -= total_cost
                        entry_price = current_price
                        
                        trades.append({
                            'date': row['trade_date'],
                            'action': 'buy',
                            'price': current_price,
                            'shares': shares_to_buy,
                            'commission': commission,
                            'capital_after': capital
                        })
            
            elif signal == -1 and position > 0:  # 卖出信号且有持仓
                # 卖出所有持仓
                proceeds = position * current_price
                commission = proceeds * commission_rate
                net_proceeds = proceeds - commission
                
                capital += net_proceeds
                
                # 记录交易
                trade_return = (current_price - entry_price) / entry_price
                trades.append({
                    'date': row['trade_date'],
                    'action': 'sell',
                    'price': current_price,
                    'shares': position,
                    'commission': commission,
                    'trade_return': trade_return,
                    'capital_after': capital
                })
                
                position = 0
                entry_price = 0.0
        
        # 最后一天如果还有持仓，按收盘价卖出
        if position > 0:
            final_price = signals.iloc[-1]['close_price']
            proceeds = position * final_price
            commission = proceeds * commission_rate
            net_proceeds = proceeds - commission
            capital += net_proceeds
            
            trade_return = (final_price - entry_price) / entry_price
            trades.append({
                'date': signals.iloc[-1]['trade_date'],
                'action': 'sell',
                'price': final_price,
                'shares': position,
                'commission': commission,
                'trade_return': trade_return,
                'capital_after': capital
            })
        
        # 计算最终结果
        result.final_capital = capital
        result.trades = trades
        result.equity_curve = equity_curve
        result.daily_returns = daily_returns
        result.trade_count = len(trades)  # 统计所有交易次数，包括买入和卖出
        
        # 计算性能指标
        metrics = self.calculate_performance_metrics(equity_curve, daily_returns, initial_capital)
        result.total_return = metrics.get('total_return', 0)
        result.annual_return = metrics.get('annual_return', 0)
        result.max_drawdown = metrics.get('max_drawdown', 0)
        result.sharpe_ratio = metrics.get('sharpe_ratio', 0)
        result.win_rate = metrics.get('win_rate', 0)
        result.profit_loss_ratio = metrics.get('profit_loss_ratio', 0)
        
        return result
    
    def run_backtest(self, stock_code: str, start_date: str, end_date: str, strategy_type: str, initial_capital: float = 100000.0, commission_rate: float = 0.001, strategy_params=None):
        try:
            self.logger.info(f"开始回测: {stock_code} {strategy_type} {start_date} 到 {end_date}")
            
            # 运行策略生成信号
            if strategy_params:
                signals = self.strategy_engine.run_strategy(
                    stock_code=stock_code,
                    start_date=start_date,
                    end_date=end_date,
                    strategy_type=strategy_type,
                    **strategy_params
                )
            else:
                signals = self.strategy_engine.run_strategy(
                    stock_code=stock_code,
                    start_date=start_date,
                    end_date=end_date,
                    strategy_type=strategy_type
                )
            
            if signals.empty:
                raise ValueError("未生成任何交易信号")
            
            # 模拟交易
            result = self.simulate_trading(signals, initial_capital, commission_rate)
            
            self.logger.info(f"回测完成: 总收益率 {result.total_return:.2%}, "
                           f"年化收益率 {result.annual_return:.2%}, "
                           f"最大回撤 {result.max_drawdown:.2%}, "
                           f"夏普比率 {result.sharpe_ratio:.2f}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"回测失败: {e}")
            raise
    
    def save_backtest_result(self, result: BacktestResult, strategy_id: str, 
                           user_id: str, stock_code: str, start_date: str, 
                           end_date: str, backtest_type: str = 'STOCK',
                           strategy_params: dict = None) -> str:
        """保存回测结果到数据库"""
        try:
            self.connect_database()
            
            # 生成报告ID
            report_id = f"RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{stock_code}"
            
            # 将equity_curve和trades数据转换为JSON格式
            import json
            equity_curve_json = json.dumps(result.equity_curve) if hasattr(result, 'equity_curve') and result.equity_curve else json.dumps([])
            
            # 处理trades数据，确保日期格式正确
            formatted_trades = []
            if hasattr(result, 'trades') and result.trades:
                for trade in result.trades:
                    formatted_trade = trade.copy()
                    # 确保日期可序列化
                    if 'date' in formatted_trade and hasattr(formatted_trade['date'], 'strftime'):
                        formatted_trade['date'] = formatted_trade['date'].strftime('%Y-%m-%d')
                    formatted_trades.append(formatted_trade)
            trades_json = json.dumps(formatted_trades)
            
            # 将策略参数转换为JSON格式
            strategy_params_json = json.dumps(strategy_params) if strategy_params else json.dumps({})
            
            # 插入回测报告
            cursor = self.connection.cursor()
            insert_sql = """
            INSERT INTO BacktestReport (
                report_id, strategy_id, user_id, backtest_type, stock_code,
                start_date, end_date, initial_fund, final_fund, total_return,
                annual_return, max_drawdown, sharpe_ratio, win_rate,
                profit_loss_ratio, trade_count, report_status, equity_curve_data, trade_records,
                strategy_params
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(insert_sql, (
                report_id, strategy_id, user_id, backtest_type, stock_code,
                start_date, end_date, result.initial_capital, result.final_capital,
                result.total_return, result.annual_return, result.max_drawdown,
                result.sharpe_ratio, result.win_rate, result.profit_loss_ratio,
                result.trade_count, 'completed', equity_curve_json, trades_json,
                strategy_params_json
            ))
            
            self.connection.commit()
            cursor.close()
            
            self.logger.info(f"回测结果已保存: {report_id}")
            return report_id
            
        except Exception as e:
            self.logger.error(f"保存回测结果失败: {e}")
            if self.connection:
                self.connection.rollback()
            raise
        finally:
            self.close_database()
    
    def get_backtest_results(self, user_id: str = None, strategy_id: str = None,
                           limit: int = 100) -> List[Dict[str, Any]]:
        """获取回测结果列表"""
        try:
            self.connect_database()
            
            query = """
            SELECT report_id, strategy_id, user_id, backtest_type, stock_code,
                   start_date, end_date, initial_fund, final_fund, total_return,
                   annual_return, max_drawdown, sharpe_ratio, win_rate,
                   profit_loss_ratio, trade_count, report_generate_time, report_status
            FROM BacktestReport
            WHERE 1=1
            """
            params = []
            
            if user_id:
                query += " AND user_id = %s"
                params.append(user_id)
            
            if strategy_id:
                query += " AND strategy_id = %s"
                params.append(strategy_id)
            
            query += " ORDER BY report_generate_time DESC LIMIT %s"
            params.append(limit)
            
            df = pd.read_sql(query, self.connection, params=params)
            
            return df.to_dict('records')
            
        except Exception as e:
            self.logger.error(f"获取回测结果失败: {e}")
            return []
        finally:
            self.close_database()
    
    def compare_strategies(self, stock_code: str, start_date: str, end_date: str,
                         strategies: List[Dict[str, Any]], 
                         initial_capital: float = 100000.0) -> Dict[str, BacktestResult]:
        """比较多个策略的表现"""
        results = {}
        
        for strategy_config in strategies:
            strategy_type = strategy_config['type']
            strategy_params = strategy_config.get('params', {})
            
            try:
                result = self.run_backtest(
                    stock_code=stock_code,
                    start_date=start_date,
                    end_date=end_date,
                    strategy_type=strategy_type,
                    initial_capital=initial_capital,
                    **strategy_params
                )
                results[strategy_type] = result
                
            except Exception as e:
                self.logger.error(f"策略 {strategy_type} 回测失败: {e}")
                continue
        
        return results


if __name__ == "__main__":
    # 示例用法
    try:
        # 创建回测引擎
        engine = BacktestEngine()
        
        # 运行单个策略回测
        result = engine.run_backtest(
            stock_code="600519.SH",
            start_date="2024-01-01",
            end_date="2024-12-31",
            strategy_type="moving_average",
            initial_capital=100000.0,
            short_period=5,
            long_period=20,
            buy_threshold=1.01,
            sell_threshold=1.0
        )
        
        print("回测结果:")
        print(f"初始资金: {result.initial_capital:,.2f}")
        print(f"最终资金: {result.final_capital:,.2f}")
        print(f"总收益率: {result.total_return:.2%}")
        print(f"年化收益率: {result.annual_return:.2%}")
        print(f"最大回撤: {result.max_drawdown:.2%}")
        print(f"夏普比率: {result.sharpe_ratio:.2f}")
        print(f"胜率: {result.win_rate:.2%}")
        print(f"盈亏比: {result.profit_loss_ratio:.2f}")
        print(f"交易次数: {result.trade_count}")
        
        # 比较多个策略
        strategies = [
            {'type': 'moving_average', 'params': {'short_period': 5, 'long_period': 20}},
            {'type': 'breakout', 'params': {'lookback_period': 20, 'breakout_threshold': 0.02}},
            {'type': 'rsi_mean_reversion', 'params': {'rsi_period': 14}}
        ]
        
        comparison_results = engine.compare_strategies(
            stock_code="600519.SH",
            start_date="2024-01-01",
            end_date="2024-12-31",
            strategies=strategies
        )
        
        print("\n策略比较结果:")
        for strategy_name, result in comparison_results.items():
            print(f"{strategy_name}: 年化收益率 {result.annual_return:.2%}, "
                  f"夏普比率 {result.sharpe_ratio:.2f}, "
                  f"最大回撤 {result.max_drawdown:.2%}")
        
    except Exception as e:
        logger.error(f"程序运行出错: {e}")


