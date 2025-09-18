#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
策略API接口模块
提供策略管理和回测结果查询的REST API
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import uuid
import pymysql

from strategy_engine import StrategyEngine
from backtest_engine import BacktestEngine, BacktestResult
from strategy_editor import StrategyEditor
# 导入认证装饰器
from app import token_required

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 全局变量
strategy_engine = None
backtest_engine = None
strategy_editor = None

def init_engines(db_password: str = None):
    """初始化策略引擎和回测引擎"""
    global strategy_engine, backtest_engine, strategy_editor
    strategy_engine = StrategyEngine(db_password)
    backtest_engine = BacktestEngine(db_password)
    strategy_editor = StrategyEditor(db_password)
    logger.info("策略引擎、回测引擎和策略编辑器初始化完成")

def register_routes(app):
    """注册所有API路由"""
    from flask import request, jsonify
    import pymysql
    
    @app.route('/strategies', methods=['GET'])
    def get_api_strategies():
        """获取所有可用的策略"""
        try:
            # 直接从策略引擎获取可用策略
            engine = StrategyEngine()
            available_strategies = engine.get_available_strategies()
            
            # 格式化策略数据为前端需要的格式
            strategies = []
            strategy_names = {
                'moving_average': '双均线策略',
                'breakout': '突破策略',
                'rsi_mean_reversion': 'RSI均值回归策略'
            }
            
            # 返回策略引擎支持的策略
            for i, strategy_type in enumerate(['moving_average', 'breakout', 'rsi_mean_reversion'], 1):
                # 查找对应策略的详细信息
                strategy_detail = next((s for s in available_strategies if s['name'] == strategy_type), None)
                
                if strategy_detail:
                    strategies.append({
                        'id': f'strategy_{i}',
                        'name': strategy_names.get(strategy_type, strategy_type),
                        'description': strategy_detail['description'] or f'{strategy_names.get(strategy_type, strategy_type)}',
                        'type': strategy_type,
                        'parameters': strategy_detail['parameters']
                    })
            
            # 从数据库加载自定义策略（优先）
            try:
                connection = pymysql.connect(
                    host='localhost',
                    port=3306,
                    user='root',
                    password='123456',
                    database='quantitative_trading',
                    charset='utf8mb4'
                )
                
                cursor = connection.cursor()
                
                # 查询自定义策略
                sql = "SELECT strategy_id, strategy_name, strategy_desc, strategy_params FROM strategy WHERE strategy_type = 'custom'";
                cursor.execute(sql)
                
                # 处理查询结果
                custom_strategies = cursor.fetchall()
                for strategy in custom_strategies:
                    strategy_id, strategy_name, strategy_desc, strategy_params = strategy
                    try:
                        # 解析策略参数
                        params = json.loads(strategy_params) if strategy_params else {}
                        strategies.append({
                            'id': strategy_id,
                            'name': strategy_name,
                            'description': strategy_desc or '自定义策略',
                            'type': 'custom',  # 标记为自定义策略
                            'parameters': params
                        })
                    except json.JSONDecodeError as json_error:
                        logger.warning(f"解析策略参数失败 (ID: {strategy_id}): {json_error}")
                        strategies.append({
                            'id': strategy_id,
                            'name': strategy_name,
                            'description': strategy_desc or '自定义策略',
                            'type': 'custom',
                            'parameters': {}
                        })
                
                connection.close()
                logger.info(f"从数据库加载了 {len(custom_strategies)} 个自定义策略")
            except Exception as db_error:
                logger.warning(f"从数据库加载自定义策略失败: {db_error}")
                
                # 如果数据库加载失败，从文件加载作为备选
                try:
                    import os
                    custom_strategies_dir = "custom_strategies"
                    if os.path.exists(custom_strategies_dir):
                        for filename in os.listdir(custom_strategies_dir):
                            if filename.endswith('.json'):
                                with open(os.path.join(custom_strategies_dir, filename), 'r', encoding='utf-8') as f:
                                    custom_strategy = json.load(f)
                                    strategies.append({
                                        'id': custom_strategy['strategy_id'],
                                        'name': custom_strategy['name'],
                                        'description': custom_strategy['description'],
                                        'type': 'custom',  # 标记为自定义策略
                                        'parameters': custom_strategy['parameters']
                                    })
                except Exception as e:
                    logger.warning(f"从文件加载自定义策略也失败: {e}")
            
            return jsonify({
                'success': True,
                'strategies': strategies
            })
        except Exception as e:
            logger.error(f"获取策略列表失败: {e}")
            return jsonify({'success': False, 'error': '获取策略列表失败'}), 500

    @app.route('/strategies/<strategy_type>/run', methods=['POST'])
    def run_strategy():
        """运行策略生成信号"""
        try:
            # 获取请求数据
            data = request.get_json()
            if not data:
                return jsonify({'message': '请求数据不能为空'}), 400

            # 验证必要参数
            required_fields = ['stock_code', 'start_date', 'end_date']
            for field in required_fields:
                if field not in data:
                    return jsonify({'message': f'缺少必要参数: {field}'}), 400

            # 解析参数
            strategy_type = request.view_args.get('strategy_type')
            stock_code = data['stock_code']
            start_date = data['start_date']
            end_date = data['end_date']
            params = data.get('params', {})

            # 运行策略
            result = strategy_engine.run_strategy(
                strategy_type=strategy_type,
                stock_code=stock_code,
                start_date=start_date,
                end_date=end_date,
                **params  # 展开params参数，而不是作为单独的参数传递
            )

            return jsonify({'success': True, 'data': result}), 200
        except Exception as e:
            logger.error(f"运行策略失败: {e}")
            return jsonify({'message': '运行策略失败', 'error': str(e)}), 500

    @app.route('/backtest/run', methods=['POST'])
    @token_required
    def run_backtest(current_user_id):
        """运行回测"""
        try:
            # 获取请求数据
            data = request.get_json()
            if not data:
                return jsonify({'message': '请求数据不能为空'}), 400

            # 验证必要参数（匹配前端发送的参数名称）
            required_fields = ['strategyId', 'type', 'target', 'startDate', 'endDate', 'initialFund']
            for field in required_fields:
                if field not in data:
                    return jsonify({'message': f'缺少必要参数: {field}'}), 400

            # 解析参数
            strategy_id = data['strategyId']
            stock_code = data['target']
            start_date = data['startDate']
            end_date = data['endDate']
            initial_capital = data['initialFund']
            front_end_type = data['type']
            commission_rate = data.get('commissionRate', 0.0003)  # 默认手续费率
            
            # 添加日志记录
            logger.info(f"接收到回测请求 - 策略ID: {strategy_id}, 前端类型: {front_end_type}")
            
            # 定义系统支持的策略类型映射
            strategy_mapping = {
                'strategy_1': 'moving_average',  # 双均线策略
                'strategy_2': 'breakout',        # 突破策略
                'strategy_3': 'rsi_mean_reversion',  # RSI均值回归策略
                'STRAT_001': 'moving_average',   # 双均线策略（新格式）
                'STRAT_002': 'breakout',         # 突破策略（新格式）
                'STRAT_003': 'rsi_mean_reversion'  # RSI均值回归策略（新格式）
            }
            
            # 设置策略参数
            strategy_params = data.get('strategy_params', {})
            risk_management = data.get('risk_management', {})
            
            # 检查是否为自定义策略
            is_custom_strategy = False
            custom_strategy_data = None
            
            # 首先从数据库加载自定义策略
            if strategy_id.startswith('CUSTOM_') or strategy_id.startswith('strategy_'):
                try:
                    # 从数据库加载自定义策略
                    connection = pymysql.connect(
                        host='localhost',
                        port=3306,
                        user='root',
                        password='123456',
                        database='quantitative_trading',
                        charset='utf8mb4'
                    )
                    
                    cursor = connection.cursor()
                    
                    # 查询自定义策略
                    sql = "SELECT strategy_code, strategy_params FROM strategy WHERE strategy_id = %s AND strategy_type = 'custom'";
                    cursor.execute(sql, (strategy_id,))
                    
                    result = cursor.fetchone()
                    if result:
                        strategy_code, strategy_params_str = result
                        
                        # 解析策略参数
                        try:
                            params = json.loads(strategy_params_str) if strategy_params_str else {}
                        except json.JSONDecodeError:
                            params = {}
                        
                        custom_strategy_data = {
                            'code': strategy_code,
                            'parameters': params
                        }
                        is_custom_strategy = True
                        logger.info(f"成功从数据库加载自定义策略: {strategy_id}")
                    
                    connection.close()
                except Exception as db_error:
                    logger.error(f"从数据库加载自定义策略失败: {db_error}")
                    
                    # 如果数据库加载失败，尝试从文件加载作为备选
                    try:
                        import os
                        custom_strategies_dir = "custom_strategies"
                        strategy_file = os.path.join(custom_strategies_dir, f"{strategy_id}.json")
                        
                        if os.path.exists(strategy_file):
                            with open(strategy_file, 'r', encoding='utf-8') as f:
                                custom_strategy_data = json.load(f)
                                is_custom_strategy = True
                                logger.info(f"成功从文件加载自定义策略: {strategy_id}")
                        else:
                            # 尝试遍历目录查找匹配的策略文件
                            for filename in os.listdir(custom_strategies_dir):
                                if filename.endswith('.json'):
                                    with open(os.path.join(custom_strategies_dir, filename), 'r', encoding='utf-8') as f:
                                        temp_strategy = json.load(f)
                                        if temp_strategy.get('strategy_id') == strategy_id:
                                            custom_strategy_data = temp_strategy
                                            is_custom_strategy = True
                                            logger.info(f"成功从文件加载自定义策略: {strategy_id}")
                                            break
                    except Exception as e:
                        logger.error(f"从文件加载自定义策略也失败: {e}")
            
            # 根据策略ID获取对应的策略类型
            if not is_custom_strategy:
                strategy_type = strategy_mapping.get(strategy_id)
                
                if not strategy_type:
                    # 首先检查数据库中是否存在该策略ID
                    try:
                        connection = pymysql.connect(
                            host='localhost',
                            port=3306,
                            user='root',
                            password='123456',
                            database='quantitative_trading',
                            charset='utf8mb4'
                        )
                        
                        cursor = connection.cursor()
                        
                        # 查询策略
                        sql = "SELECT strategy_type, strategy_code, strategy_params FROM strategy WHERE strategy_id = %s";
                        cursor.execute(sql, (strategy_id,))
                        
                        result = cursor.fetchone()
                        if result:
                            # 这是一个存在的策略，可能是之前保存的自定义策略
                            db_strategy_type, strategy_code, strategy_params_str = result
                            
                            # 解析策略参数
                            try:
                                params = json.loads(strategy_params_str) if strategy_params_str else {}
                            except json.JSONDecodeError:
                                params = {}
                            
                            # 标记为自定义策略
                            is_custom_strategy = True
                            custom_strategy_data = {
                                'code': strategy_code,
                                'parameters': params
                            }
                            logger.info(f"发现数据库中存在的策略ID: {strategy_id}，标记为自定义策略")
                        
                        connection.close()
                    except Exception as db_error:
                        logger.error(f"查询数据库策略失败: {db_error}")
                    
                    # 如果数据库中也不存在，则返回无效策略ID
                    if not is_custom_strategy:
                        logger.warning(f"无效的策略ID: {strategy_id}")
                        return jsonify({'message': f'无效的策略ID: {strategy_id}', 'supported_strategies': list(strategy_mapping.keys())}), 400
                
                if strategy_type:
                    logger.info(f"使用的策略类型: {strategy_type}")

            # 添加日志记录
            logger.info(f"准备运行回测 - 股票代码: {stock_code}, 策略类型: {'custom' if is_custom_strategy else strategy_type}")
            
            # 运行回测 - 确保参数类型正确
            try:
                # 将initial_capital转换为浮点数
                initial_capital_float = float(initial_capital)
                commission_rate_float = float(commission_rate)
                
                if is_custom_strategy and custom_strategy_data:
                    # 运行自定义策略
                    logger.info(f"运行自定义策略回测")
                    result = strategy_editor.run_custom_strategy(
                        stock_code=stock_code,
                        start_date=start_date,
                        end_date=end_date,
                        code=custom_strategy_data['code'],
                        parameters=custom_strategy_data['parameters'],
                        initial_capital=initial_capital_float,
                        commission_rate=commission_rate_float
                    )
                    
                    if not result['success']:
                        logger.error(f"自定义策略回测失败: {result.get('message')}")
                        return jsonify({'message': f'回测失败: {result.get('message')}'}), 500
                    
                    # 将结果转换为BacktestResult对象格式
                    backtest_result = BacktestResult()
                    backtest_result.initial_capital = initial_capital_float
                    backtest_result.final_capital = result['data'].get('final_capital', initial_capital_float)
                    backtest_result.total_return = result['data'].get('total_return', 0)
                    backtest_result.annual_return = result['data'].get('annual_return', 0)
                    backtest_result.max_drawdown = result['data'].get('max_drawdown', 0)
                    backtest_result.sharpe_ratio = result['data'].get('sharpe_ratio', 0)
                    backtest_result.win_rate = result['data'].get('win_rate', 0)
                    backtest_result.profit_loss_ratio = result['data'].get('profit_loss_ratio', 0)
                    backtest_result.trade_count = result['data'].get('trade_count', 0)
                    backtest_result.trades = result['data'].get('trades', [])
                    backtest_result.equity_curve = result['data'].get('equity_curve', [])
                    backtest_result.daily_returns = result['data'].get('daily_returns', [])
                    
                    result = backtest_result
                else:
                    # 将strategy_params作为单独的参数传递，而不是展开
                    result = backtest_engine.run_backtest(
                        stock_code=stock_code,
                        start_date=start_date,
                        end_date=end_date,
                        initial_capital=initial_capital_float,
                        strategy_type=strategy_type,
                        commission_rate=commission_rate_float,
                        strategy_params=strategy_params  # 作为单独的字典参数传递
                    )
            except ValueError as e:
                logger.error(f"参数类型转换失败: {e}")
                return jsonify({'message': f'参数格式错误: {str(e)}'}), 400

            # 保存回测结果到数据库
            # 现在使用从JWT token中获取的实际用户ID
            user_id = current_user_id  # 从装饰器中获取的登录用户ID
            
            # 处理日期格式 - 将ISO格式的日期字符串转换为数据库可接受的格式
            # 从 '2024-09-15T07:50:04.063Z' 转换为 '2024-09-15 07:50:04'
            try:
                # 解析ISO格式的日期字符串
                parsed_start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                parsed_end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                
                # 转换为数据库可接受的格式
                formatted_start_date = parsed_start_date.strftime('%Y-%m-%d %H:%M:%S')
                formatted_end_date = parsed_end_date.strftime('%Y-%m-%d %H:%M:%S')
            except:
                # 如果解析失败，使用简化的日期格式
                formatted_start_date = start_date.split('T')[0] + ' ' + start_date.split('T')[1].split('.')[0]
                formatted_end_date = end_date.split('T')[0] + ' ' + end_date.split('T')[1].split('.')[0]
            
            # 调用save_backtest_result方法，提供所有必要的参数
            report_id = backtest_engine.save_backtest_result(
                result=result,            # 回测结果对象
                strategy_id=strategy_id,  # 策略ID
                user_id=user_id,          # 用户ID
                stock_code=stock_code,    # 股票代码
                start_date=formatted_start_date,    # 格式化后的开始日期
                end_date=formatted_end_date,        # 格式化后的结束日期
                backtest_type=front_end_type,  # 回测类型
                strategy_params=strategy_params  # 策略参数
            )

            # 构造响应数据 - 格式与前端Backtest.vue组件期望的格式匹配
            # 格式化性能指标，保留四位小数，将百分比指标乘以100
            response = {
                'id': report_id,  # 前端使用id字段而不是report_id
                'totalReturn': round(float(result.total_return) * 100, 4),  # 保留四位小数，乘以100转换为百分比
                'annualReturn': round(float(result.annual_return) * 100, 4),  # 保留四位小数，乘以100转换为百分比
                'maxDrawdown': round(float(result.max_drawdown) * 100, 4),  # 保留四位小数，乘以100转换为百分比
                'sharpeRatio': round(float(result.sharpe_ratio), 4),
                'winRate': round(float(result.win_rate) * 100, 4),  # 保留四位小数，乘以100转换为百分比
                'tradeCount': result.trade_count if hasattr(result, 'trade_count') else 0,
                'equityCurve': [],  # 初始化资金曲线数据
                'trades': []  # 初始化交易记录列表
            }
            
            # 处理资金曲线数据，确保格式适合前端图表渲染
            if hasattr(result, 'equity_curve') and result.equity_curve:
                try:
                    import pandas as pd
                    import pymysql
                    from strategy_engine import DB_DEFAULTS
                    
                    # 直接使用pandas的to_datetime函数解析日期
                    start_date_str = formatted_start_date.split(' ')[0]
                    end_date_str = formatted_end_date.split(' ')[0]
                    
                    # 连接数据库获取实际的交易日历数据
                    connection = pymysql.connect(
                        host=DB_DEFAULTS["host"],
                        port=DB_DEFAULTS["port"],
                        user=DB_DEFAULTS["user"],
                        password=backtest_engine.db_password if hasattr(backtest_engine, 'db_password') else DB_DEFAULTS["password"],
                        database=DB_DEFAULTS["database"],
                        charset=DB_DEFAULTS["charset"]
                    )
                    
                    try:
                        # 查询实际的交易日历数据
                        query = """
                        SELECT DISTINCT trade_date 
                        FROM StockMarketData 
                        WHERE stock_code = %s AND trade_date BETWEEN %s AND %s
                        ORDER BY trade_date ASC
                        """
                        
                        # 执行查询，获取实际的交易日历
                        calendar_df = pd.read_sql(query, connection, params=(stock_code, start_date_str, end_date_str))
                        
                        if not calendar_df.empty:
                            # 将trade_date转换为datetime
                            calendar_df['trade_date'] = pd.to_datetime(calendar_df['trade_date'])
                            
                            # 获取实际的日期列表
                            actual_dates = calendar_df['trade_date'].tolist()
                            
                            # 确保日期列表长度与equity_curve长度匹配
                            min_length = min(len(actual_dates), len(result.equity_curve))
                            
                            # 构建资金曲线数据，使用实际的交易日历
                            for i in range(min_length):
                                date_str = actual_dates[i].strftime('%Y-%m-%d')
                                
                                response['equityCurve'].append({
                                    'date': date_str,
                                    'value': round(float(result.equity_curve[i]), 2)
                                })
                        else:
                            # 如果没有实际的交易日历数据，使用简化的日期格式
                            for i, value in enumerate(result.equity_curve):
                                date_str = f"{start_date_str}+{i}"
                                
                                response['equityCurve'].append({
                                    'date': date_str,
                                    'value': round(float(value), 2)
                                })
                    finally:
                        if connection:
                            connection.close()
                except Exception as e:
                    logger.error(f"处理资金曲线数据失败: {e}")
                    # 使用简化的日期格式作为备选
                    for i, value in enumerate(result.equity_curve):
                        date_str = f"{start_date_str}+{i}"
                        
                        response['equityCurve'].append({
                            'date': date_str,
                            'value': round(float(value), 2)
                        })
                    # 使用简化格式作为备选，只包含实际有数据的日期
                    start_date_str = formatted_start_date.split(' ')[0]
                    end_date_str = formatted_end_date.split(' ')[0]
                    
                    start_date_parts = list(map(int, start_date_str.split('-')))
                    end_date_parts = list(map(int, end_date_str.split('-')))
                    
                    start_date_obj = datetime(start_date_parts[0], start_date_parts[1], start_date_parts[2])
                    end_date_obj = datetime(end_date_parts[0], end_date_parts[1], end_date_parts[2])
                    
                    # 只添加实际有数据的日期点
                    for i, value in enumerate(result.equity_curve):
                        current_date = start_date_obj + timedelta(days=i)
                        
                        # 确保生成的日期不会超过用户指定的end_date
                        if current_date > end_date_obj:
                            break
                        
                        date_str = current_date.strftime('%Y-%m-%d')
                        
                        response['equityCurve'].append({
                            'date': date_str,
                            'value': round(float(value), 2)
                        })
            
            # 在返回的结果中添加标记，指示数据的实际结束日期
            if hasattr(result, 'equity_curve') and result.equity_curve:
                # 计算实际数据的结束日期
                try:
                    start_date = formatted_start_date.split(' ')[0]
                    start_date_parts = list(map(int, start_date.split('-')))
                    start_date_obj = datetime(start_date_parts[0], start_date_parts[1], start_date_parts[2])
                    actual_end_date = start_date_obj + timedelta(days=len(result.equity_curve) - 1)
                    response['actualEndDate'] = actual_end_date.strftime('%Y-%m-%d')
                except Exception as e:
                    logger.error(f"计算实际结束日期失败: {e}")
                    # 如果计算失败，使用默认值
                    response['actualEndDate'] = formatted_end_date.split(' ')[0]
            
            # 处理交易记录，确保所有字段都有值
            if hasattr(result, 'trades') and result.trades:
                for trade in result.trades:
                    # 计算金额（价格×数量）
                    price = float(trade.get('price', 0))
                    quantity = int(trade.get('shares', 0))
                    amount = price * quantity
                    
                    # 为每个交易记录提供默认值，确保所有字段都不为空
                    formatted_trade = {
                        'date': trade.get('date', ''),
                        'type': trade.get('action', ''),  # 将action重命名为type以匹配前端
                        'stockCode': stock_code,  # 添加股票代码字段
                        'price': round(price, 2),
                        'quantity': quantity,  # 将shares重命名为quantity
                        'amount': round(amount, 2),  # 添加金额字段（价格×数量）
                        'commission': round(float(trade.get('commission', 0)), 2),
                        'return': round(float(trade.get('trade_return', 0)), 2),
                        'capitalAfter': round(float(trade.get('capital_after', 0)), 2),
                        'status': 'completed'  # 添加状态字段，确保不为空
                    }
                    response['trades'].append(formatted_trade)

            # 为了兼容前端，直接返回response对象
            return jsonify(response), 200
        except ValueError as e:
            logger.error(f"回测参数验证失败: {e}")
            return jsonify({'message': '回测参数验证失败', 'error': str(e)}), 400
        except Exception as e:
            logger.error(f"回测失败: {e}")
            return jsonify({'message': '回测失败', 'error': str(e)}), 500

    @app.route('/backtest/compare', methods=['POST'])
    def compare_strategies():
        """比较多个策略"""
        try:
            # 获取请求数据
            data = request.get_json()
            if not data:
                return jsonify({'message': '请求数据不能为空'}), 400

            # 验证必要参数
            if 'strategy_comparisons' not in data:
                return jsonify({'message': '缺少必要参数: strategy_comparisons'}), 400

            strategy_comparisons = data['strategy_comparisons']
            if not isinstance(strategy_comparisons, list) or len(strategy_comparisons) < 2:
                return jsonify({'message': 'strategy_comparisons必须是包含至少两个策略的列表'}), 400

            # 运行策略比较
            comparison_result = backtest_engine.compare_strategies(strategy_comparisons)

            # 格式化比较结果
            formatted_result = {
                'strategy_performances': comparison_result,
                'best_overall_strategy': max(comparison_result, key=lambda x: x['total_return'])['strategy_name'],
                'worst_overall_strategy': min(comparison_result, key=lambda x: x['total_return'])['strategy_name']
            }

            return jsonify({'success': True, 'data': formatted_result}), 200
        except Exception as e:
            logger.error(f"策略比较失败: {e}")
            return jsonify({'message': '策略比较失败', 'error': str(e)}), 500

    @app.route('/backtest/results', methods=['GET'])
    @token_required
    def get_backtest_results(current_user_id):
        """获取回测结果列表"""
        try:
            # 获取查询参数
            limit = request.args.get('limit', default=10, type=int)
            strategy_id = request.args.get('strategy_id')

            # 查询回测结果，传入当前登录用户ID
            results = backtest_engine.get_backtest_results(
                user_id=current_user_id,
                strategy_id=strategy_id,
                limit=limit
            )

            return jsonify({'success': True, 'data': results}), 200
        except Exception as e:
            logger.error(f"获取回测结果列表失败: {e}")
            return jsonify({'message': '获取回测结果列表失败', 'error': str(e)}), 500

    @app.route('/backtest/results/<report_id>', methods=['GET'])
    @token_required
    def get_backtest_detail(current_user_id, report_id):
        """获取回测结果详情"""
        try:
            # 直接连接数据库查询回测结果详情，并验证用户权限
            import pymysql
            import json
            from strategy_engine import DB_DEFAULTS
            connection = None
            try:
                connection = pymysql.connect(
                    host=DB_DEFAULTS["host"],
                    port=DB_DEFAULTS["port"],
                    user=DB_DEFAULTS["user"],
                    password=DB_DEFAULTS["password"],
                    database=DB_DEFAULTS["database"],
                    charset=DB_DEFAULTS["charset"]
                )
                cursor = connection.cursor(pymysql.cursors.DictCursor)
                
                # 查询回测结果并验证用户ID，包含equity_curve_data、trade_records和strategy_params字段
                query = """
                SELECT report_id, strategy_id, user_id, backtest_type, stock_code,
                       start_date, end_date, initial_fund, final_fund, total_return,
                       annual_return, max_drawdown, sharpe_ratio, win_rate,
                       profit_loss_ratio, trade_count, report_generate_time, report_status,
                       equity_curve_data, trade_records, strategy_params
                FROM BacktestReport
                WHERE report_id = %s AND user_id = %s
                """
                cursor.execute(query, (report_id, current_user_id))
                result = cursor.fetchone()
                
                if not result:
                    return jsonify({'message': '回测结果不存在或无权访问'}), 404
                
                # 创建返回对象
                response = {
                    'id': result['report_id'],
                    'strategyId': result['strategy_id'],
                    'type': result['backtest_type'],
                    'target': result['stock_code'],
                    'startDate': result['start_date'],
                    'endDate': result['end_date'],
                    'initialFund': float(result['initial_fund']),
                    'finalFund': float(result['final_fund']),
                    'totalReturn': round(float(result['total_return']) * 100, 4),  # 乘以100转换为百分比
                    'annualReturn': round(float(result['annual_return']) * 100, 4),  # 乘以100转换为百分比
                    'maxDrawdown': round(float(result['max_drawdown']) * 100, 4),  # 乘以100转换为百分比
                    'sharpeRatio': round(float(result['sharpe_ratio']) if result['sharpe_ratio'] is not None else 0.0, 4),
                    'winRate': round(float(result['win_rate']) * 100 if result['win_rate'] is not None else 0.0, 4),  # 乘以100转换为百分比
                    'profitLossRatio': round(float(result['profit_loss_ratio']) if result['profit_loss_ratio'] is not None else 0.0, 4),
                    'tradeCount': int(result['trade_count']),
                    'createTime': result['report_generate_time'],
                    'status': result['report_status'],
                    'equityCurve': [],
                    'trades': []
                }
                
                try:
                    # 从数据库中读取并解析equity_curve_data
                    if result.get('equity_curve_data'):
                        try:
                            equity_curve = json.loads(result['equity_curve_data'])
                            
                            # 连接数据库获取实际的交易日历数据，确保日期与equity_curve匹配
                            calendar_conn = pymysql.connect(
                                host=DB_DEFAULTS["host"],
                                port=DB_DEFAULTS["port"],
                                user=DB_DEFAULTS["user"],
                                password=DB_DEFAULTS["password"],
                                database=DB_DEFAULTS["database"],
                                charset=DB_DEFAULTS["charset"]
                            )
                            
                            try:
                                # 查询实际的交易日历数据
                                calendar_query = """
                                SELECT DISTINCT trade_date 
                                FROM StockMarketData 
                                WHERE stock_code = %s AND trade_date BETWEEN %s AND %s
                                ORDER BY trade_date ASC
                                """
                                
                                start_date_str = result['start_date'].split(' ')[0] if isinstance(result['start_date'], str) else str(result['start_date']).split(' ')[0]
                                end_date_str = result['end_date'].split(' ')[0] if isinstance(result['end_date'], str) else str(result['end_date']).split(' ')[0]
                                
                                # 执行查询，获取实际的交易日历
                                cursor_calendar = calendar_conn.cursor()
                                cursor_calendar.execute(calendar_query, (result['stock_code'], start_date_str, end_date_str))
                                dates_result = cursor_calendar.fetchall()
                                
                                if dates_result:
                                    # 构建日期列表
                                    dates = [date[0].strftime('%Y-%m-%d') for date in dates_result]
                                    
                                    # 确保equity_curve长度与dates匹配
                                    min_length = min(len(dates), len(equity_curve))
                                    
                                    # 构建资金曲线数据，使用实际的交易日历
                                    response['equityCurve'] = [{'date': dates[i], 'value': round(float(equity_curve[i]), 4)} for i in range(min_length)]
                                
                            finally:
                                if calendar_conn:
                                    calendar_conn.close()
                        except json.JSONDecodeError as e:
                            logger.error(f"解析equity_curve_data失败: {e}")
                        
                    # 从数据库中读取并解析trade_records
                    if result.get('trade_records'):
                        try:
                            trades = json.loads(result['trade_records'])
                            
                            # 格式化交易记录，确保与前端期望的格式匹配
                            formatted_trades = []
                            for trade in trades:
                                # 计算金额（价格×数量）
                                price = float(trade.get('price', 0))
                                quantity = int(trade.get('shares', 0))
                                amount = price * quantity
                                
                                formatted_trade = {
                                    'date': trade.get('date', ''),
                                    'type': trade.get('action', ''),  # 将action重命名为type以匹配前端
                                    'stockCode': result['stock_code'],  # 添加股票代码字段
                                    'price': round(price, 2),
                                    'quantity': quantity,  # 将shares重命名为quantity
                                    'amount': round(amount, 2),  # 添加金额字段（价格×数量）
                                    'commission': round(float(trade.get('commission', 0)), 2),
                                    'return': round(float(trade.get('trade_return', 0)), 2),
                                    'capitalAfter': round(float(trade.get('capital_after', 0)), 2),
                                    'status': 'completed'  # 添加状态字段，确保不为空
                                }
                                formatted_trades.append(formatted_trade)
                            
                            response['trades'] = formatted_trades
                        except json.JSONDecodeError as e:
                            logger.error(f"解析trade_records失败: {e}")
                    
                    # 从数据库中读取并解析strategy_params
                    if result.get('strategy_params'):
                        try:
                            strategy_params = json.loads(result['strategy_params'])
                            response['strategyParams'] = strategy_params
                        except json.JSONDecodeError as e:
                            logger.error(f"解析strategy_params失败: {e}")
                            response['strategyParams'] = {}
                except Exception as e:
                    logger.error(f"处理回测详情数据时出错: {e}")
                    # 即使处理失败，也要保证返回格式正确
                    response['equityCurve'] = []
                    response['trades'] = []
                
                logger.info(f"成功获取回测详情，包含{len(response['equityCurve'])}个资金曲线数据点和{len(response['trades'])}条交易记录")
                return jsonify({'success': True, 'data': response}), 200
                
            except Exception as e:
                logger.error(f"查询回测结果详情数据库错误: {e}")
                return jsonify({'message': '查询回测结果详情失败', 'error': str(e)}), 500
            finally:
                if connection:
                    connection.close()
        except Exception as e:
            logger.error(f"获取回测结果详情失败: {e}")
            return jsonify({'message': '获取回测结果详情失败', 'error': str(e)}), 500
    
    @app.route('/backtest/history', methods=['GET'])
    @token_required
    def get_backtest_history(current_user_id):
        """获取历史回测记录（为前端提供兼容接口）"""
        try:
            logger.info(f"用户 {current_user_id} 请求获取历史回测记录")
            
            # 调用现有接口获取数据
            results = backtest_engine.get_backtest_results(
                user_id=current_user_id,
                limit=20  # 返回最近20条记录
            )
            
            logger.info(f"获取到 {len(results)} 条历史回测记录")
            
            # 转换数据格式为前端期望的结构
            formatted_records = []
            import pymysql
            from strategy_engine import DB_DEFAULTS
            connection = None
            
            try:
                connection = pymysql.connect(
                    host=DB_DEFAULTS["host"],
                    port=DB_DEFAULTS["port"],
                    user=DB_DEFAULTS["user"],
                    password=DB_DEFAULTS["password"],
                    database=DB_DEFAULTS["database"],
                    charset=DB_DEFAULTS["charset"]
                )
                
                with connection.cursor() as cursor:
                    for record in results:
                        # 查询策略名称
                        cursor.execute("SELECT strategy_name FROM Strategy WHERE strategy_id = %s", (record.get('strategy_id'),))
                        strategy_result = cursor.fetchone()
                        strategy_name = strategy_result[0] if strategy_result else '未知策略'
                        
                        # 格式化日期为前端需要的格式
                        start_date_str = record.get('start_date', '')
                        end_date_str = record.get('end_date', '')
                        
                        # 转换格式，确保正确显示
                        from datetime import datetime as dt_type
                        if isinstance(start_date_str, dt_type):
                            start_date_str = start_date_str.strftime('%Y-%m-%d')
                        elif isinstance(start_date_str, str) and ' ' in start_date_str:
                            start_date_str = start_date_str.split(' ')[0]
                            
                        if isinstance(end_date_str, dt_type):
                            end_date_str = end_date_str.strftime('%Y-%m-%d')
                        elif isinstance(end_date_str, str) and ' ' in end_date_str:
                            end_date_str = end_date_str.split(' ')[0]
                            
                        # 转换创建时间格式
                        create_time_str = record.get('report_generate_time', '')
                        if isinstance(create_time_str, dt_type):
                            create_time_str = create_time_str.strftime('%Y-%m-%d %H:%M:%S')
                        elif isinstance(create_time_str, str):
                            # 尝试格式化
                            try:
                                dt = datetime.strptime(create_time_str, '%Y-%m-%d %H:%M:%S')
                                create_time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                            except:
                                pass
                            
                        # 构建前端需要的记录格式
                        formatted_record = {
                            'id': record.get('report_id'),
                            'strategyName': strategy_name,
                            'target': record.get('stock_code'),
                            'period': f"{start_date_str} 至 {end_date_str}",
                            'totalReturn': round(float(record.get('total_return', 0)), 4),
                            'maxDrawdown': round(float(record.get('max_drawdown', 0)), 4),
                            'sharpeRatio': round(float(record.get('sharpe_ratio', 0)), 4),
                            'createTime': create_time_str
                        }
                        
                        formatted_records.append(formatted_record)
            except Exception as e:
                logger.error(f"格式化回测历史记录失败: {e}")
                # 使用简化的记录格式作为备选方案
                formatted_records = []
                for record in results:
                    formatted_record = {
                        'id': record.get('report_id'),
                        'strategyName': '未知策略',
                        'target': record.get('stock_code'),
                        'period': '未知期间',
                        'totalReturn': round(float(record.get('total_return', 0)), 4),
                        'maxDrawdown': round(float(record.get('max_drawdown', 0)), 4),
                        'sharpeRatio': round(float(record.get('sharpe_ratio', 0)), 4),
                        'createTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    formatted_records.append(formatted_record)
            finally:
                if connection:
                    connection.close()
            
            # 返回格式化后的数据
            return jsonify({'success': True, 'records': formatted_records}), 200
        except Exception as e:
            logger.error(f"获取历史回测记录失败: {e}")
            return jsonify({'message': '获取历史回测记录失败', 'error': str(e)}), 500
    
    @app.route('/backtest/<string:report_id>', methods=['DELETE'])
    @token_required
    def delete_backtest_result(current_user_id, report_id):
        """删除指定的回测结果"""
        try:
            logger.info(f"用户 {current_user_id} 请求删除回测记录 {report_id}")
            
            # 连接数据库
            import pymysql
            from strategy_engine import DB_DEFAULTS
            connection = None
            try:
                connection = pymysql.connect(
                    host=DB_DEFAULTS["host"],
                    port=DB_DEFAULTS["port"],
                    user=DB_DEFAULTS["user"],
                    password=backtest_engine.db_password if hasattr(backtest_engine, 'db_password') else DB_DEFAULTS["password"],
                    database=DB_DEFAULTS["database"],
                    charset=DB_DEFAULTS["charset"]
                )
                
                # 验证记录是否属于当前用户
                with connection.cursor() as cursor:
                    # 先检查记录是否存在且属于当前用户
                    check_sql = "SELECT COUNT(*) FROM BacktestReport WHERE report_id = %s AND user_id = %s"
                    cursor.execute(check_sql, (report_id, current_user_id))
                    count = cursor.fetchone()[0]
                    
                    if count == 0:
                        logger.warning(f"回测记录 {report_id} 不属于用户 {current_user_id} 或不存在")
                        return jsonify({'message': '回测记录不存在或您无权删除'}), 404
                    
                    # 删除记录
                    delete_sql = "DELETE FROM BacktestReport WHERE report_id = %s AND user_id = %s"
                    cursor.execute(delete_sql, (report_id, current_user_id))
                    connection.commit()
                    
                    logger.info(f"成功删除回测记录 {report_id}")
                    return jsonify({'success': True, 'message': '删除成功'}), 200
            except Exception as e:
                logger.error(f"删除回测记录失败: {e}")
                if connection:
                    connection.rollback()
                raise
            finally:
                if connection:
                    connection.close()
        except Exception as e:
            logger.error(f"删除回测记录时发生错误: {e}")
            return jsonify({'message': '删除失败', 'error': str(e)}), 500

    @app.route('/api/strategy-editor/templates', methods=['GET'])
    def get_strategy_templates():
        """获取策略模板"""
        try:
            templates = strategy_editor.get_strategy_templates()
            return jsonify(templates), 200
        except Exception as e:
            logger.error(f"获取策略模板失败: {e}")
            return jsonify({'message': '获取策略模板失败', 'error': str(e)}), 500

    @app.route('/api/strategy-editor/validate', methods=['POST'])
    def validate_strategy():
        """验证策略代码"""
        try:
            # 获取请求数据
            data = request.get_json()
            if not data or 'code' not in data:
                return jsonify({'message': '缺少必要参数: code'}), 400

            code = data['code']
            parameters = data.get('parameters', {})

            # 验证策略代码
            result = strategy_editor.validate_strategy(code, parameters)

            return jsonify(result), 200
        except Exception as e:
            logger.error(f"验证策略代码失败: {e}")
            return jsonify({'message': '验证策略代码失败', 'error': str(e)}), 500

    @app.route('/api/strategy-editor/run', methods=['POST'])
    def run_custom_strategy():
        """运行自定义策略"""
        try:
            # 获取请求数据
            data = request.get_json()
            if not data:
                return jsonify({'message': '请求数据不能为空'}), 400

            # 验证必要参数
            required_fields = ['code', 'stock_code', 'start_date', 'end_date']
            for field in required_fields:
                if field not in data:
                    return jsonify({'message': f'缺少必要参数: {field}'}), 400

            code = data['code']
            stock_code = data['stock_code']
            start_date = data['start_date']
            end_date = data['end_date']
            parameters = data.get('parameters', {})
            initial_capital = data.get('initial_capital', 100000)
            commission_rate = data.get('commission_rate', 0.001)

            # 检查并修正日期范围 - 基于数据库中600519.SH的实际日期范围
            # 目前数据库中600519.SH的数据范围是2025-01-02到2025-06-30
            # 这里添加一个临时修复，确保日期范围在有效范围内
            min_valid_date = '2025-01-02'
            max_valid_date = '2025-06-30'
            
            # 如果用户请求的日期范围超出有效范围，进行调整
            if start_date < min_valid_date:
                start_date = min_valid_date
                logger.info(f"调整起始日期至有效范围: {start_date}")
            
            if end_date > max_valid_date:
                end_date = max_valid_date
                logger.info(f"调整结束日期至有效范围: {end_date}")

            # 确保数据库连接已建立 - 同时为全局strategy_engine和strategy_editor内部的strategy_engine建立连接
            try:
                # 连接全局strategy_engine
                strategy_engine.connect_database()
                # 连接strategy_editor内部的strategy_engine
                strategy_editor.strategy_engine.connect_database()
            except Exception as conn_error:
                logger.error(f"连接数据库失败: {conn_error}")
                return jsonify({'message': '连接数据库失败', 'error': str(conn_error)}), 500

            # 运行自定义策略
            result = strategy_editor.run_custom_strategy(
                stock_code=stock_code,
                start_date=start_date,
                end_date=end_date,
                code=code,
                parameters=parameters,
                initial_capital=initial_capital,
                commission_rate=commission_rate
            )

            # 确保交易记录正确传递 - 检查trades字段并格式化日期
            if result.get('success') and result.get('data') and result['data'].get('trades'):
                formatted_trades = []
                for trade in result['data']['trades']:
                    formatted_trade = trade.copy()
                    # 确保日期格式正确可显示
                    if 'date' in formatted_trade:
                        # 尝试将日期对象转换为字符串（如果需要）
                        if hasattr(formatted_trade['date'], 'strftime'):
                            formatted_trade['date'] = formatted_trade['date'].strftime('%Y-%m-%d')
                        # 确保是字符串格式
                        elif not isinstance(formatted_trade['date'], str):
                            formatted_trade['date'] = str(formatted_trade['date'])
                    formatted_trades.append(formatted_trade)
                result['data']['trades'] = formatted_trades

            return jsonify(result), 200
        except Exception as e:
            logger.error(f"运行自定义策略失败: {e}")
            return jsonify({'message': '运行自定义策略失败', 'error': str(e)}), 500

    @app.route('/api/strategy-editor/save', methods=['POST'])
    def save_custom_strategy():
        """保存自定义策略"""
        try:
            # 获取请求数据
            data = request.get_json()
            if not data:
                return jsonify({'message': '请求数据不能为空'}), 400

            # 验证必要参数
            required_fields = ['code', 'name', 'description']
            for field in required_fields:
                if field not in data:
                    return jsonify({'message': f'缺少必要参数: {field}'}), 400

            code = data['code']
            name = data['name']
            description = data['description']
            params = data.get('params', {})
            strategy_type = data.get('strategy_type', 'custom')

            # 保存自定义策略
            # 调用策略编辑器保存策略
            save_result = strategy_editor.save_custom_strategy(
                code=code,
                name=name,
                description=description,
                parameters=params  # 使用从请求中获取的params参数
            )

            # 检查保存结果并返回前端期望的格式
            if save_result.get('success'):
                return jsonify(save_result), 200
            else:
                return jsonify(save_result), 500
        except Exception as e:
            logger.error(f"保存自定义策略失败: {e}")
            return jsonify({'message': '保存自定义策略失败', 'error': str(e)}), 500

    @app.route('/strategies/<strategy_id>', methods=['DELETE'])
    def delete_strategy(strategy_id):
        """删除策略"""
        try:
            logger.info(f"接收到删除策略请求: {strategy_id}")
            
            # 连接数据库删除策略
            connection = pymysql.connect(
                host='localhost',
                port=3306,
                user='root',
                password='123456',
                database='quantitative_trading',
                charset='utf8mb4'
            )
            
            cursor = connection.cursor()
            
            # 检查策略是否存在且为自定义策略
            check_sql = "SELECT COUNT(*) FROM strategy WHERE strategy_id = %s AND strategy_type = 'custom'"
            cursor.execute(check_sql, (strategy_id,))
            count = cursor.fetchone()[0]
            
            if count == 0:
                logger.warning(f"自定义策略不存在: {strategy_id}")
                connection.close()
                return jsonify({'message': '策略不存在'}), 404
            
            # 删除策略
            delete_sql = "DELETE FROM strategy WHERE strategy_id = %s AND strategy_type = 'custom'"
            cursor.execute(delete_sql, (strategy_id,))
            connection.commit()
            
            # 同时删除策略文件（如果存在）
            try:
                import os
                strategy_file = os.path.join("custom_strategies", f"{strategy_id}.json")
                if os.path.exists(strategy_file):
                    os.remove(strategy_file)
                    logger.info(f"已删除策略文件: {strategy_file}")
            except Exception as e:
                logger.warning(f"删除策略文件失败: {e}")
                # 继续执行，不影响数据库操作
            
            connection.close()
            logger.info(f"策略删除成功: {strategy_id}")
            return jsonify({'success': True, 'message': '策略删除成功'}), 200
            
        except Exception as e:
            logger.error(f"删除策略失败: {e}")
            return jsonify({'message': '删除失败', 'error': str(e)}), 500

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """健康检查接口"""
        try:
            # 检查数据库连接
            if strategy_engine and strategy_engine.check_connection():
                db_status = 'connected'
            else:
                db_status = 'disconnected'
                
            # 检查各引擎状态
            engines_status = {
                'strategy_engine': strategy_engine is not None,
                'backtest_engine': backtest_engine is not None,
                'strategy_editor': strategy_editor is not None
            }

            # 构造健康检查结果
            health_result = {
                'status': 'healthy' if db_status == 'connected' and all(engines_status.values()) else 'unhealthy',
                'db_status': db_status,
                'engines': engines_status,
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0'
            }

            return jsonify(health_result), 200
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500

    @app.errorhandler(404)
    def not_found(error):
        """404错误处理"""
        return jsonify({'message': '请求的资源不存在'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        """500错误处理"""
        logger.error(f"服务器内部错误: {error}")
        return jsonify({'message': '服务器内部错误'}), 500

    return app


# 如果作为独立脚本运行
if __name__ == '__main__':
    from flask import Flask
    from flask_cors import CORS
    
    app = Flask(__name__)
    CORS(app)
    
    register_routes(app)
    init_engines()
    app.run(host='0.0.0.0', port=8001, debug=True)

