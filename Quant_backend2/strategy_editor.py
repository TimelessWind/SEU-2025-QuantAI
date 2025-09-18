#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
策略编辑器模块
支持研究员编写自定义策略并进行回测
"""

import ast
import logging
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import json
import uuid
import pymysql

from strategy_engine import BaseStrategy, StrategyEngine
from backtest_engine import BacktestEngine

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class StrategyValidator:
    """策略代码验证器"""
    
    ALLOWED_IMPORTS = {
        'pandas', 'numpy', 'np', 'pd', 'math', 'datetime'
    }
    
    ALLOWED_FUNCTIONS = {
        'len', 'range', 'enumerate', 'zip', 'min', 'max', 'sum', 'abs',
        'round', 'int', 'float', 'str', 'bool', 'list', 'dict', 'tuple',
        'print', 'len', 'sorted', 'reversed'
    }
    
    FORBIDDEN_KEYWORDS = {
        'import', 'exec', 'eval', 'open', 'file', 'input', 'raw_input',
        '__import__', 'reload', 'compile', 'globals', 'locals', 'vars',
        'dir', 'hasattr', 'getattr', 'setattr', 'delattr'
    }
    
    @classmethod
    def validate_strategy_code(cls, code: str) -> Tuple[bool, str]:
        """
        验证策略代码的安全性
        
        Args:
            code: 策略代码字符串
            
        Returns:
            (是否有效, 错误信息)
        """
        try:
            # 解析AST
            tree = ast.parse(code)
            
            # 检查导入语句
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name not in cls.ALLOWED_IMPORTS:
                            return False, f"不允许导入模块: {alias.name}"
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module not in cls.ALLOWED_IMPORTS:
                        return False, f"不允许从模块导入: {node.module}"
                
                # 检查函数调用
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in cls.FORBIDDEN_KEYWORDS:
                            return False, f"不允许调用函数: {node.func.id}"
                
                # 检查属性访问
                elif isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name) and node.value.id == 'pd':
                        # 允许pandas的基本操作
                        allowed_pd_methods = {
                            'rolling', 'mean', 'std', 'min', 'max', 'sum', 'count',
                            'shift', 'diff', 'ewm', 'expanding', 'fillna', 'dropna'
                        }
                        if node.attr not in allowed_pd_methods:
                            return False, f"不允许的pandas方法: {node.attr}"
            
            return True, "代码验证通过"
            
        except SyntaxError as e:
            return False, f"语法错误: {str(e)}"
        except Exception as e:
            return False, f"验证错误: {str(e)}"


class CustomStrategy(BaseStrategy):
    """自定义策略类"""
    
    def __init__(self, name: str, code: str, params: Dict[str, Any] = None):
        super().__init__(name, params or {})
        self.code = code
        self.compiled_code = None
        
    def compile_code(self) -> bool:
        """编译策略代码"""
        try:
            # 验证代码安全性
            is_valid, error_msg = StrategyValidator.validate_strategy_code(self.code)
            if not is_valid:
                raise ValueError(f"代码验证失败: {error_msg}")
            
            # 编译代码
            self.compiled_code = compile(self.code, '<strategy>', 'exec')
            return True
            
        except Exception as e:
            logger.error(f"策略代码编译失败: {e}")
            return False
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成交易信号"""
        if not self.validate_data(data):
            raise ValueError("数据格式不正确")
        
        if not self.compiled_code:
            if not self.compile_code():
                raise ValueError("策略代码编译失败")
        
        try:
            # 准备执行环境
            df = data.copy()
            df = df.sort_values('trade_date').reset_index(drop=True)
            
            # 初始化信号和仓位
            df['signal'] = 0
            df['position'] = 0
            
            # 创建执行环境
            exec_globals = {
                'pd': pd,
                'np': np,
                'df': df,
                'len': len,
                'range': range,
                'enumerate': enumerate,
                'zip': zip,
                'min': min,
                'max': max,
                'sum': sum,
                'abs': abs,
                'round': round,
                'int': int,
                'float': float,
                'str': str,
                'bool': bool,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'print': print,
                'sorted': sorted,
                'reversed': reversed,
            }
            
            # 执行策略代码
            exec(self.compiled_code, exec_globals)
            
            # 检查并调用用户定义的strategy函数
            if 'strategy' in exec_globals:
                # 调用用户定义的strategy函数处理DataFrame
                df = exec_globals['strategy'](df)
            else:
                # 获取修改后的DataFrame
                df = exec_globals['df']
            
            # 确保信号列存在
            if 'signal' not in df.columns:
                df['signal'] = 0
            if 'position' not in df.columns:
                df['position'] = 0
            
            return df
            
        except Exception as e:
            logger.error(f"策略执行失败: {e}")
            raise ValueError(f"策略执行失败: {str(e)}")


class StrategyTemplate:
    """策略模板管理器"""
    
    @staticmethod
    def get_templates() -> Dict[str, Dict[str, Any]]:
        """获取策略模板"""
        return {
            "moving_average_template": {
                "name": "双均线策略模板",
                "description": "基于移动平均线的策略模板",
                "code": """
# 双均线策略模板
# 参数: short_period, long_period, buy_threshold, sell_threshold

# 计算移动平均线
df['ma_short'] = df['close_price'].rolling(window=short_period).mean()
df['ma_long'] = df['close_price'].rolling(window=long_period).mean()

# 计算价格与均线的比率
df['price_ma_ratio'] = df['close_price'] / df['ma_short']

# 生成交易信号
for i in range(1, len(df)):
    # 买入信号：价格上穿短期均线且超过阈值
    if (df.loc[i, 'price_ma_ratio'] >= buy_threshold and 
        df.loc[i-1, 'price_ma_ratio'] < buy_threshold):
        df.loc[i, 'signal'] = 1  # 买入
        df.loc[i, 'position'] = 1
    
    # 卖出信号：价格下穿短期均线
    elif (df.loc[i, 'price_ma_ratio'] <= sell_threshold and 
          df.loc[i-1, 'price_ma_ratio'] > sell_threshold):
        df.loc[i, 'signal'] = -1  # 卖出
        df.loc[i, 'position'] = 0
    
    # 保持仓位
    else:
        df.loc[i, 'position'] = df.loc[i-1, 'position']
""",
                "parameters": {
                    "short_period": {"type": "int", "default": 5, "min": 1, "max": 100},
                    "long_period": {"type": "int", "default": 20, "min": 1, "max": 200},
                    "buy_threshold": {"type": "float", "default": 1.01, "min": 1.0, "max": 2.0},
                    "sell_threshold": {"type": "float", "default": 1.0, "min": 0.5, "max": 1.5}
                }
            },
            
            "rsi_template": {
                "name": "RSI策略模板",
                "description": "基于RSI指标的策略模板",
                "code": """
# RSI策略模板
# 参数: rsi_period, oversold_threshold, overbought_threshold

# 计算RSI
delta = df['close_price'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
rs = gain / loss
df['rsi'] = 100 - (100 / (1 + rs))

# 生成交易信号
for i in range(rsi_period, len(df)):
    # 超卖买入
    if df.loc[i, 'rsi'] < oversold_threshold:
        df.loc[i, 'signal'] = 1  # 买入
        df.loc[i, 'position'] = 1
    
    # 超买卖出
    elif df.loc[i, 'rsi'] > overbought_threshold:
        df.loc[i, 'signal'] = -1  # 卖出
        df.loc[i, 'position'] = 0
    
    # 保持仓位
    else:
        df.loc[i, 'position'] = df.loc[i-1, 'position']
""",
                "parameters": {
                    "rsi_period": {"type": "int", "default": 14, "min": 1, "max": 50},
                    "oversold_threshold": {"type": "float", "default": 30, "min": 0, "max": 50},
                    "overbought_threshold": {"type": "float", "default": 70, "min": 50, "max": 100}
                }
            },
            
            "breakout_template": {
                "name": "突破策略模板",
                "description": "基于价格突破的策略模板",
                "code": """
# 突破策略模板
# 参数: lookback_period, breakout_threshold

# 计算过去窗口的高低点（避免未来函数）
df['high_max'] = df['high_price'].rolling(window=lookback_period, min_periods=lookback_period).max().shift(1)
df['low_min'] = df['low_price'].rolling(window=lookback_period, min_periods=lookback_period).min().shift(1)

# 计算突破阈值
df['upper_threshold'] = df['high_max'] * (1 + breakout_threshold)
df['lower_threshold'] = df['low_min'] * (1 - breakout_threshold)

# 生成交易信号
start_idx = max(lookback_period, int(df['high_max'].first_valid_index() or 0) + 1)
for i in range(start_idx, len(df)):
    # 向上突破买入
    if df.loc[i, 'close_price'] > df.loc[i, 'upper_threshold']:
        df.loc[i, 'signal'] = 1  # 买入
        df.loc[i, 'position'] = 1
    
    # 向下突破卖出
    elif df.loc[i, 'close_price'] < df.loc[i, 'lower_threshold']:
        df.loc[i, 'signal'] = -1  # 卖出
        df.loc[i, 'position'] = 0
    
    # 保持仓位
    else:
        df.loc[i, 'position'] = df.loc[i-1, 'position']
""",
                "parameters": {
                    "lookback_period": {"type": "int", "default": 20, "min": 5, "max": 100},
                    "breakout_threshold": {"type": "float", "default": 0.02, "min": 0.001, "max": 0.1}
                }
            }
        }


class StrategyEditor:
    """策略编辑器"""
    
    def __init__(self, db_password: str = None):
        self.db_password = db_password
        self.strategy_engine = StrategyEngine(db_password)
        self.backtest_engine = BacktestEngine(db_password)
        self.logger = logger
    
    def validate_strategy(self, code: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        验证策略代码
        
        Args:
            code: 策略代码
            parameters: 策略参数
            
        Returns:
            验证结果
        """
        try:
            # 创建临时策略实例进行验证
            temp_strategy = CustomStrategy("temp", code, parameters or {})
            
            # 编译代码
            if not temp_strategy.compile_code():
                return {
                    "success": False,
                    "message": "策略代码编译失败",
                    "error_type": "compile_error"
                }
            
            return {
                "success": True,
                "message": "策略代码验证通过",
                "error_type": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "error_type": "validation_error"
            }
    
    def _extract_param_metadata(self, code: str, params: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        从策略代码中提取参数的元数据
        
        Args:
            code: 策略代码
            params: 策略参数
            
        Returns:
            参数元数据字典
        """
        metadata = {}
        
        try:
            # 解析代码注释中的参数说明
            lines = code.split('\n')
            param_section = False
            param_comments = []
            
            for line in lines:
                line = line.strip()
                # 检查是否有参数说明部分
                if line.startswith('# 参数:'):
                    param_section = True
                    # 提取参数名称列表
                    param_names = line.replace('# 参数:', '').strip()
                    if param_names:
                        for param_name in param_names.split(','):
                            param_name = param_name.strip()
                            if param_name and param_name not in metadata:
                                metadata[param_name] = {
                                    'type': self._infer_param_type(params.get(param_name)),
                                    'description': '',
                                    'default': params.get(param_name)
                                }
                elif param_section and line.startswith('#'):
                    # 收集参数注释
                    param_comments.append(line.lstrip('#').strip())
                elif line and not line.startswith('#'):
                    # 结束参数注释部分
                    param_section = False
            
            # 解析代码中的实际参数使用情况
            try:
                # 简单的AST解析，尝试识别代码中使用的参数
                tree = ast.parse(code)
                
                # 收集所有变量名，然后与params比对
                variables = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                        variables.add(node.id)
                
                # 为params中的每个参数提取元数据
                for param_name, param_value in params.items():
                    if param_name not in metadata:
                        metadata[param_name] = {
                            'type': self._infer_param_type(param_value),
                            'description': '',
                            'default': param_value
                        }
                    
                    # 为参数添加默认范围建议
                    metadata[param_name] = self._add_suggested_ranges(metadata[param_name], param_value)
            except Exception as e:
                self.logger.warning(f"解析参数元数据时出错: {e}")
                # 出错时，至少为每个参数提供基本类型信息
                for param_name, param_value in params.items():
                    if param_name not in metadata:
                        metadata[param_name] = {
                            'type': self._infer_param_type(param_value),
                            'description': '',
                            'default': param_value
                        }
            
        except Exception as e:
            self.logger.error(f"提取参数元数据失败: {e}")
            
        return metadata
    
    def _infer_param_type(self, value: Any) -> str:
        """\推断参数类型"""
        if isinstance(value, int):
            return 'int'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, bool):
            return 'bool'
        elif isinstance(value, str):
            return 'str'
        elif isinstance(value, list):
            return 'list'
        elif isinstance(value, dict):
            return 'dict'
        else:
            return 'any'
    
    def _add_suggested_ranges(self, metadata: Dict[str, Any], value: Any) -> Dict[str, Any]:
        """为参数添加建议的取值范围"""
        param_type = metadata.get('type')
        
        # 根据参数类型和常用策略参数范围，添加建议值
        if param_type == 'int':
            if ('period' in metadata.get('description', '').lower() or 
                any(keyword in str(metadata).lower() for keyword in ['window', 'lookback', 'days'])):
                metadata.update({
                    'min': max(1, int(value) - 10),
                    'max': int(value) + 30,
                    'step': 1
                })
        elif param_type == 'float':
            if any(keyword in str(metadata).lower() for keyword in ['threshold', 'rate', 'ratio']):
                metadata.update({
                    'min': max(0.0, float(value) - 0.05),
                    'max': float(value) + 0.05,
                    'step': 0.01
                })
        
        return metadata
    
    def run_custom_strategy(self, stock_code: str, start_date: str, end_date: str,
                           code: str, parameters: Dict[str, Any] = None,
                           initial_capital: float = 100000.0,
                           commission_rate: float = 0.001) -> Dict[str, Any]:
        """
        运行自定义策略
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            code: 策略代码
            parameters: 策略参数
            initial_capital: 初始资金
            commission_rate: 手续费率
            
        Returns:
            回测结果
        """
        try:
            # 创建自定义策略
            strategy = CustomStrategy("custom_strategy", code, parameters or {})
            
            # 连接数据库（修复问题：确保在调用get_stock_data之前连接数据库）
            self.strategy_engine.connect_database()
            
            # 获取数据
            data = self.strategy_engine.get_stock_data(stock_code, start_date, end_date)
            if data.empty:
                raise ValueError(f"未获取到股票{stock_code}的数据")
            
            # 生成信号
            signals = strategy.generate_signals(data)
            
            # 模拟交易
            result = self.backtest_engine.simulate_trading(signals, initial_capital, commission_rate)
            
            return {
                "success": True,
                "data": result.to_dict(),
                "message": "自定义策略回测完成"
            }
            
        except Exception as e:
            self.logger.error(f"自定义策略运行失败: {e}")
            return {
                "success": False,
                "message": str(e),
                "data": None
            }
        finally:
            # 确保关闭数据库连接，避免资源泄漏
            try:
                self.strategy_engine.close_database()
            except Exception as close_error:
                self.logger.warning(f"关闭数据库连接时出错: {close_error}")
    
    def get_strategy_templates(self) -> Dict[str, Any]:
        """获取策略模板"""
        return {
            "success": True,
            "data": StrategyTemplate.get_templates(),
            "message": "获取策略模板成功"
        }
    
    def save_custom_strategy(self, name: str, code: str, parameters: Dict[str, Any] = None, 
                           description: str = "", creator_id: str = "") -> Dict[str, Any]:
        """
        保存自定义策略到数据库和文件系统
        
        Args:
            name: 策略名称
            code: 策略代码
            parameters: 策略参数
            description: 策略描述
            creator_id: 创建者ID
            
        Returns:
            保存结果
        """
        try:
            # 参数验证与清洗
            if not name or not isinstance(name, str) or len(name) > 100:
                return {
                    "success": False,
                    "message": "策略名称不能为空且长度不能超过100个字符",
                    "error_type": "validation_error"
                }
            
            if not code or not isinstance(code, str):
                return {
                    "success": False,
                    "message": "策略代码不能为空",
                    "error_type": "validation_error"
                }
            
            if description and not isinstance(description, str):
                return {
                    "success": False,
                    "message": "策略描述必须是字符串类型",
                    "error_type": "validation_error"
                }
            
            # 标准化参数格式
            params = parameters or {}
            if not isinstance(params, dict):
                params = {}
                self.logger.warning("参数格式不正确，已转换为空字典")
            
            # 验证策略代码
            validation_result = self.validate_strategy(code, params)
            if not validation_result["success"]:
                return validation_result
            
            # 生成策略ID
            strategy_id = f"strategy_{int(datetime.now().timestamp() * 1000)}"
            
            # 提取参数元数据（类型、默认值、范围等）
            param_metadata = self._extract_param_metadata(code, params)
            
            # 构建完整的策略参数对象
            strategy_params = {
                "parameters": params,
                "metadata": param_metadata,
                "created_at": datetime.now().isoformat()
            }
            
            # 将参数转换为JSON字符串，确保正确处理中文和特殊字符
            try:
                params_json = json.dumps(strategy_params, ensure_ascii=False, default=str)
            except Exception as json_error:
                self.logger.error(f"参数JSON序列化失败: {json_error}")
                # 降级处理：使用基础参数
                params_json = json.dumps(params or {}, ensure_ascii=False, default=str)
            
            # 使用上下文管理器确保数据库连接正确关闭
            with pymysql.connect(
                host='localhost',
                port=3306,
                user='root',
                password=self.db_password or '123456',
                database='quantitative_trading',
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor  # 使用字典游标便于结果处理
            ) as connection:
                with connection.cursor() as cursor:
                    # 插入策略数据
                    sql = """
                        INSERT INTO strategy 
                        (strategy_id, strategy_name, strategy_type, creator_id, 
                         strategy_desc, strategy_code, strategy_params, create_time)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                    """
                    
                    # 使用参数化查询防止SQL注入
                    cursor.execute(sql, (
                        strategy_id, 
                        name, 
                        'custom', 
                        'admin_001',  # 使用管理员用户ID以解决外键约束问题
                        description[:1000] if description else "",  # 限制描述长度
                        code,
                        params_json
                    ))
                    
                # 在上下文管理器中自动提交
                connection.commit()
                self.logger.info(f"策略 {strategy_id} 已成功保存到数据库")
            
            # 同时保存到文件作为备份
            try:
                import os
                strategies_dir = "custom_strategies"
                os.makedirs(strategies_dir, exist_ok=True)
                
                strategy_file = os.path.join(strategies_dir, f"{strategy_id}.json")
                strategy_data = {
                    "strategy_id": strategy_id,
                    "name": name,
                    "code": code,
                    "parameters": params,
                    "metadata": param_metadata,
                    "description": description,
                    "create_time": datetime.now().isoformat(),
                    "type": "custom"
                }
                with open(strategy_file, 'w', encoding='utf-8') as f:
                    json.dump(strategy_data, f, ensure_ascii=False, indent=2)
                
                self.logger.info(f"策略 {strategy_id} 已成功保存到文件")
            except Exception as file_error:
                self.logger.warning(f"保存到文件失败，但不影响功能: {str(file_error)}")
            
            return {
                "success": True,
                "data": {"strategy_id": strategy_id},
                "message": "自定义策略保存成功"
            }
            
        except Exception as e:
            self.logger.error(f"保存自定义策略失败: {e}")
            return {
                "success": False,
                "message": str(e),
                "data": None
            }


if __name__ == "__main__":
    # 示例用法
    editor = StrategyEditor()
    
    # 获取策略模板
    templates = editor.get_strategy_templates()
    print("策略模板:", json.dumps(templates, ensure_ascii=False, indent=2))
    
    # 示例自定义策略代码
    custom_code = """
# 简单的价格突破策略
df['ma_20'] = df['close_price'].rolling(window=20).mean()
df['ma_5'] = df['close_price'].rolling(window=5).mean()

for i in range(20, len(df)):
    if df.loc[i, 'ma_5'] > df.loc[i, 'ma_20'] and df.loc[i-1, 'ma_5'] <= df.loc[i-1, 'ma_20']:
        df.loc[i, 'signal'] = 1
        df.loc[i, 'position'] = 1
    elif df.loc[i, 'ma_5'] < df.loc[i, 'ma_20'] and df.loc[i-1, 'ma_5'] >= df.loc[i-1, 'ma_20']:
        df.loc[i, 'signal'] = -1
        df.loc[i, 'position'] = 0
    else:
        df.loc[i, 'position'] = df.loc[i-1, 'position']
"""
    
    # 验证策略
    validation = editor.validate_strategy(custom_code)
    print("验证结果:", validation)
