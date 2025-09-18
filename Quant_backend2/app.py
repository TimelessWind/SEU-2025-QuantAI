#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import hashlib
import jwt
from functools import wraps
from flask import send_from_directory

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['JWT_EXPIRATION_DELTA'] = 86400  # 24小时

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

def token_required(f):
    """JWT token验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': '缺少访问令牌'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
        except:
            return jsonify({'message': '无效的访问令牌'}), 401
        
        return f(current_user_id, *args, **kwargs)
    return decorated

def role_required(allowed_roles):
    """角色权限验证装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated(current_user_id, *args, **kwargs):
            try:
                connection = get_db_connection()
                cursor = connection.cursor()
                
                # 获取用户角色
                cursor.execute("SELECT user_role FROM User WHERE user_id = %s", (current_user_id,))
                result = cursor.fetchone()
                
                cursor.close()
                connection.close()
                
                if not result:
                    return jsonify({'message': '用户不存在'}), 404
                
                user_role = result[0]
                
                if user_role not in allowed_roles:
                    return jsonify({'message': '权限不足，只有分析师和管理员可以执行此操作'}), 403
                
                return f(current_user_id, *args, **kwargs)
                
            except Exception as e:
                logger.error(f"角色验证失败: {e}")
                return jsonify({'message': '权限验证失败'}), 500
                
        return decorated
    return decorator

def hash_password(password: str) -> str:
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

# ==================== 用户认证相关 ====================

@app.route('/auth/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['account', 'email', 'phone', 'password', 'role']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'message': f'缺少必需字段: {field}'}), 400
        
        # 验证密码长度
        if len(data['password']) < 6:
            return jsonify({'message': '密码长度至少6位'}), 400
        
        # 验证邮箱格式
        if '@' not in data['email']:
            return jsonify({'message': '邮箱格式不正确'}), 400
        
        # 验证角色
        if data['role'] not in ['admin', 'analyst', 'viewer']:
            return jsonify({'message': '无效的用户角色'}), 400
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 检查账号是否已存在
        cursor.execute("SELECT user_id FROM User WHERE user_account = %s", (data['account'],))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({'message': '账号已存在'}), 400
        
        # 检查邮箱是否已存在
        cursor.execute("SELECT user_id FROM User WHERE user_email = %s", (data['email'],))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({'message': '邮箱已存在'}), 400
        
        # 创建用户
        user_id = f"user_{int(datetime.now().timestamp() * 1000)}"
        hashed_password = hash_password(data['password'])
        
        cursor.execute("""
            INSERT INTO User (user_id, user_account, user_password, user_role, user_status, user_email, user_phone)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id, data['account'], hashed_password, data['role'], 'active',
            data['email'], data['phone']
        ))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({'message': '注册成功', 'success': True}), 201
        
    except Exception as e:
        logger.error(f"注册失败: {e}")
        return jsonify({'message': '注册失败'}), 500

@app.route('/auth/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        
        if not data.get('account') or not data.get('password'):
            return jsonify({'message': '账号和密码不能为空'}), 400
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 查询用户基本信息（包括锁定状态）
        cursor.execute("""
            SELECT user_id, user_account, user_password, user_role, user_status, user_email, user_phone,
                   login_attempts, locked_until, last_failed_login
            FROM User WHERE user_account = %s
        """, (data['account'],))
        
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'message': '账号或密码错误'}), 401
        
        user_id, account, stored_password, role, status, email, phone, login_attempts, locked_until, last_failed_login = user
        
        # 检查账号状态
        if status != 'active':
            return jsonify({'message': '账号已被禁用'}), 401
        
        # 检查是否被锁定
        if locked_until and datetime.now() < locked_until:
            remaining_time = int((locked_until - datetime.now()).total_seconds() / 60)
            return jsonify({'message': f'账号已被锁定，请{remaining_time}分钟后再试'}), 423
        
        # 验证密码
        if stored_password != hash_password(data['password']):
            # 密码错误，增加失败次数
            new_attempts = login_attempts + 1
            current_time = datetime.now()
            
            if new_attempts >= 3:
                # 锁定账号30分钟
                lock_until = current_time + timedelta(minutes=30)
                cursor.execute("""
                    UPDATE User SET login_attempts = %s, locked_until = %s, last_failed_login = %s
                    WHERE user_id = %s
                """, (new_attempts, lock_until, current_time, user_id))
                connection.commit()
                cursor.close()
                connection.close()
                return jsonify({'message': '密码错误次数过多，账号已被锁定30分钟'}), 423
            else:
                # 更新失败次数
                cursor.execute("""
                    UPDATE User SET login_attempts = %s, last_failed_login = %s
                    WHERE user_id = %s
                """, (new_attempts, current_time, user_id))
                connection.commit()
                cursor.close()
                connection.close()
                return jsonify({'message': f'密码错误，还有{3-new_attempts}次机会'}), 401
        
        # 登录成功，重置失败次数和锁定状态
        cursor.execute("""
            UPDATE User SET login_attempts = 0, locked_until = NULL, last_failed_login = NULL
            WHERE user_id = %s
        """, (user_id,))
        connection.commit()
        
        # 生成JWT token
        token_payload = {
            'user_id': user_id,
            'account': account,
            'role': role,
            'exp': datetime.utcnow().timestamp() + app.config['JWT_EXPIRATION_DELTA']
        }
        token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm='HS256')
        
        user_info = {
            'user_id': user_id,
            'account': account,
            'role': role,
            'email': email,
            'phone': phone
        }
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'message': '登录成功',
            'success': True,
            'token': token,
            'user': user_info
        }), 200
        
    except Exception as e:
        logger.error(f"登录失败: {e}")
        return jsonify({'message': '登录失败'}), 500

@app.route('/auth/me', methods=['GET'])
@token_required
def get_user_info(current_user_id):
    """获取当前用户信息"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT user_id, user_account, user_role, user_status, user_email, user_phone
            FROM User WHERE user_id = %s
        """, (current_user_id,))
        
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        
        user_info = {
            'user_id': user[0],
            'account': user[1],
            'role': user[2],
            'status': user[3],
            'email': user[4],
            'phone': user[5]
        }
        
        return jsonify({
            'success': True,
            'user': user_info
        }), 200
        
    except Exception as e:
        logger.error(f"获取用户信息失败: {e}")
        return jsonify({'message': '获取用户信息失败'}), 500

# ==================== 股票数据相关 ====================

@app.route('/stocks/filter', methods=['POST'])
@token_required
def filter_stocks(current_user_id):
    """股票筛选"""
    try:
        data = request.get_json()
        
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
        if data.get('stockCode'):
            base_query += " AND sb.stock_code LIKE %s"
            params.append(f"%{data['stockCode']}%")
        
        if data.get('stockName'):
            base_query += " AND sb.stock_name LIKE %s"
            params.append(f"%{data['stockName']}%")
        
        if data.get('industry'):
            base_query += " AND sb.industry = %s"
            params.append(data['industry'])
        
        if data.get('priceMin') is not None:
            base_query += " AND lsp.latest_price >= %s"
            params.append(data['priceMin'])
        
        if data.get('priceMax') is not None:
            base_query += " AND lsp.latest_price <= %s"
            params.append(data['priceMax'])
        
        if data.get('peMin') is not None:
            base_query += " AND sv.pe_ratio >= %s"
            params.append(data['peMin'])
        
        if data.get('peMax') is not None:
            base_query += " AND sv.pe_ratio <= %s"
            params.append(data['peMax'])
        
        if data.get('pbMin') is not None:
            base_query += " AND sv.pb_ratio >= %s"
            params.append(data['pbMin'])
        
        if data.get('pbMax') is not None:
            base_query += " AND sv.pb_ratio <= %s"
            params.append(data['pbMax'])
        
        if data.get('marketCapMin') is not None:
            base_query += " AND sv.market_cap >= %s"
            params.append(data['marketCapMin'] * 100000000)  # 转换为元
        
        if data.get('marketCapMax') is not None:
            base_query += " AND sv.market_cap <= %s"
            params.append(data['marketCapMax'] * 100000000)  # 转换为元
        
        # 资产负债率筛选
        if data.get('debtRatioMin') is not None:
            base_query += " AND (bs.total_liability / bs.total_assets * 100) >= %s"
            params.append(data['debtRatioMin'])
        
        if data.get('debtRatioMax') is not None:
            base_query += " AND (bs.total_liability / bs.total_assets * 100) <= %s"
            params.append(data['debtRatioMax'])
        
        # 地区筛选
        if data.get('area'):
            base_query += " AND sb.area = %s"
            params.append(data['area'])
        
        # 添加排序和限制
        base_query += " ORDER BY sb.stock_code LIMIT 1000"
        
        cursor.execute(base_query, params)
        results = cursor.fetchall()
        
        # 格式化结果
        stocks = []
        for row in results:
            stock = {
                'stockCode': row[0],
                'stockName': row[1],
                'industry': row[2],
                'area': row[3] if row[3] else '',  # 地区信息
                'currentPrice': float(row[4]) if row[4] else 0,
                'changePercent': float(row[5]) if row[5] else 0,
                'volume': float(row[6]) if row[6] else 0,
                'peRatio': float(row[7]) if row[7] else 0,
                'pbRatio': float(row[8]) if row[8] else 0,
                'marketCap': float(row[9]) / 100000000 if row[9] else 0,  # 转换为亿元
                'debtRatio': float(row[10]) if row[10] else 0,
                'currentRatio': float(row[11]) if row[11] else 0,  # 流动比率
                'roe': float(row[12]) if row[12] else 0,
                'rsi': 0  # 由于当前数据中没有RSI，暂时返回0
            }
            stocks.append(stock)
        
        cursor.close()
        connection.close()
        
        return jsonify({'stocks': stocks, 'total': len(stocks)}), 200
        
    except Exception as e:
        logger.error(f"股票筛选失败: {e}")
        return jsonify({'message': '股票筛选失败'}), 500

@app.route('/stocks/industries', methods=['GET'])
@token_required
def get_industries(current_user_id):
    """获取行业列表"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("SELECT DISTINCT industry FROM StockBasic WHERE industry IS NOT NULL ORDER BY industry")
        results = cursor.fetchall()
        
        industries = [row[0] for row in results]
        
        cursor.close()
        connection.close()
        
        return jsonify({'industries': industries}), 200
        
    except Exception as e:
        logger.error(f"获取行业列表失败: {e}")
        return jsonify({'message': '获取行业列表失败'}), 500

@app.route('/stocks/<stock_code>', methods=['GET'])
@token_required
def get_stock_detail(current_user_id, stock_code):
    """获取股票详情"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 获取基本信息
        cursor.execute("""
            SELECT stock_code, stock_name, industry, area, list_date
            FROM StockBasic WHERE stock_code = %s
        """, (stock_code,))
        
        basic_info = cursor.fetchone()
        if not basic_info:
            cursor.close()
            connection.close()
            return jsonify({'message': '股票不存在'}), 404
        
        # 获取最新价格信息
        cursor.execute("""
            SELECT latest_price, change_percent, volume, amount
            FROM LatestStockPrice WHERE stock_code = %s
        """, (stock_code,))
        
        price_info = cursor.fetchone()
        
        # 获取最新估值信息
        cursor.execute("""
            SELECT pe_ratio, pb_ratio, ps_ratio, market_cap, turnover_ratio
            FROM StockValuation WHERE stock_code = %s 
            ORDER BY trade_date DESC LIMIT 1
        """, (stock_code,))
        
        valuation_info = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        stock_detail = {
            'basicInfo': {
                'stockCode': basic_info[0],
                'stockName': basic_info[1],
                'industry': basic_info[2],
                'area': basic_info[3],
                'listDate': str(basic_info[4]) if basic_info[4] else None
            },
            'priceInfo': {
                'currentPrice': float(price_info[0]) if price_info and price_info[0] else 0,
                'changePercent': float(price_info[1]) if price_info and price_info[1] else 0,
                'volume': float(price_info[2]) if price_info and price_info[2] else 0,
                'amount': float(price_info[3]) if price_info and price_info[3] else 0
            },
            'valuationInfo': {
                'peRatio': float(valuation_info[0]) if valuation_info and valuation_info[0] else 0,
                'pbRatio': float(valuation_info[1]) if valuation_info and valuation_info[1] else 0,
                'psRatio': float(valuation_info[2]) if valuation_info and valuation_info[2] else 0,
                'marketCap': float(valuation_info[3]) / 100000000 if valuation_info and valuation_info[3] else 0,
                'turnoverRatio': float(valuation_info[4]) if valuation_info and valuation_info[4] else 0
            }
        }
        
        return jsonify(stock_detail), 200
        
    except Exception as e:
        logger.error(f"获取股票详情失败: {e}")
        return jsonify({'message': '获取股票详情失败'}), 500

# ==================== 策略相关 ====================

@app.route('/strategies', methods=['GET'])
@token_required
def get_strategies(current_user_id):
    """获取策略列表"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT strategy_id, strategy_name, strategy_type, strategy_desc, create_time
            FROM Strategy ORDER BY create_time DESC
        """)
        
        results = cursor.fetchall()
        
        strategies = []
        for row in results:
            strategy = {
                'id': row[0],
                'name': row[1],
                'type': row[2],
                'description': row[3],
                'createTime': str(row[4])
            }
            strategies.append(strategy)
        
        cursor.close()
        connection.close()
        
        return jsonify({'strategies': strategies}), 200
        
    except Exception as e:
        logger.error(f"获取策略列表失败: {e}")
        return jsonify({'message': '获取策略列表失败'}), 500

@app.route('/strategies', methods=['POST'])
@token_required
@role_required(['admin', 'analyst'])
def create_strategy(current_user_id):
    """创建策略"""
    try:
        data = request.get_json()
        
        if not data.get('name') or not data.get('description'):
            return jsonify({'message': '策略名称和描述不能为空'}), 400
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        strategy_id = f"strategy_{int(datetime.now().timestamp() * 1000)}"
        
        cursor.execute("""
            INSERT INTO Strategy (strategy_id, strategy_name, strategy_type, creator_id, strategy_desc)
            VALUES (%s, %s, %s, %s, %s)
        """, (strategy_id, data['name'], 'custom', current_user_id, data['description']))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({'message': '策略创建成功', 'strategyId': strategy_id}), 201
        
    except Exception as e:
        logger.error(f"创建策略失败: {e}")
        return jsonify({'message': '创建策略失败'}), 500

# ==================== 统计数据相关 ====================

@app.route('/stats/overview', methods=['GET'])
@token_required
def get_stats_overview(current_user_id):
    """获取统计概览"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 股票总数
        cursor.execute("SELECT COUNT(*) FROM StockBasic")
        total_stocks = cursor.fetchone()[0]
        
        # 活跃策略数
        cursor.execute("SELECT COUNT(*) FROM Strategy WHERE strategy_type = 'builtin'")
        active_strategies = cursor.fetchone()[0]
        
        # 回测次数
        cursor.execute("SELECT COUNT(*) FROM BacktestReport")
        total_backtests = cursor.fetchone()[0]
        
        # 平均收益率（模拟数据）
        avg_return = 12.45
        
        cursor.close()
        connection.close()
        
        stats = {
            'totalStocks': total_stocks,
            'activeStrategies': active_strategies,
            'totalBacktests': total_backtests,
            'avgReturn': f"{avg_return}%"
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"获取统计概览失败: {e}")
        return jsonify({'message': '获取统计概览失败'}), 500

# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': '接口不存在'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'message': '服务器内部错误'}), 500

if __name__ == '__main__':
    # 确保必要的表存在
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 检查并创建LatestStockPrice视图（如果不存在）
        cursor.execute("""
            CREATE OR REPLACE VIEW LatestStockPrice AS
            SELECT 
                stock_code,
                trade_date as latest_date,
                close_price as latest_price,
                change_percent,
                volume,
                amount
            FROM StockMarketData
            WHERE (stock_code, trade_date) IN (
                SELECT stock_code, MAX(trade_date)
                FROM StockMarketData
                GROUP BY stock_code
            )
        """)
        
        connection.commit()
        cursor.close()
        connection.close()
        
        logger.info("数据库视图检查完成")
    except Exception as e:
        logger.warning(f"数据库视图检查失败: {e}")
    
# ==================== 用户管理相关 ====================

@app.route('/admin/users', methods=['GET'])
@token_required
@role_required(['admin'])
def get_all_users(current_user_id):
    """获取所有用户列表（仅管理员）"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT user_id, user_account, user_role, user_status, user_email, user_phone,
                   login_attempts, locked_until, last_failed_login, user_create_time, user_last_login_time
            FROM User ORDER BY user_create_time DESC
        """)
        
        users = []
        for row in cursor.fetchall():
            user = {
                'user_id': row[0],
                'account': row[1],
                'role': row[2],
                'status': row[3],
                'email': row[4],
                'phone': row[5],
                'login_attempts': row[6],
                'locked_until': row[7].isoformat() if row[7] else None,
                'last_failed_login': row[8].isoformat() if row[8] else None,
                'create_time': row[9].isoformat() if row[9] else None,
                'last_login_time': row[10].isoformat() if row[10] else None,
                'is_locked': row[7] and datetime.now() < row[7]
            }
            users.append(user)
        
        cursor.close()
        connection.close()
        
        return jsonify({'users': users}), 200
        
    except Exception as e:
        logger.error(f"获取用户列表失败: {e}")
        return jsonify({'message': '获取用户列表失败'}), 500

@app.route('/admin/users/<user_id>/unlock', methods=['POST'])
@token_required
@role_required(['admin'])
def unlock_user(current_user_id, user_id):
    """解锁用户（仅管理员）"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 检查用户是否存在
        cursor.execute("SELECT user_id FROM User WHERE user_id = %s", (user_id,))
        if not cursor.fetchone():
            return jsonify({'message': '用户不存在'}), 404
        
        # 解锁用户
        cursor.execute("""
            UPDATE User SET login_attempts = 0, locked_until = NULL, last_failed_login = NULL
            WHERE user_id = %s
        """, (user_id,))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({'message': '用户解锁成功'}), 200
        
    except Exception as e:
        logger.error(f"解锁用户失败: {e}")
        return jsonify({'message': '解锁用户失败'}), 500

@app.route('/admin/users/<user_id>/status', methods=['PUT'])
@token_required
@role_required(['admin'])
def update_user_status(current_user_id, user_id):
    """更新用户状态（仅管理员）"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['active', 'inactive', 'locked']:
            return jsonify({'message': '无效的用户状态'}), 400
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 检查用户是否存在
        cursor.execute("SELECT user_id FROM User WHERE user_id = %s", (user_id,))
        if not cursor.fetchone():
            return jsonify({'message': '用户不存在'}), 404
        
        # 更新用户状态
        cursor.execute("""
            UPDATE User SET user_status = %s
            WHERE user_id = %s
        """, (new_status, user_id))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({'message': '用户状态更新成功'}), 200
        
    except Exception as e:
        logger.error(f"更新用户状态失败: {e}")
        return jsonify({'message': '更新用户状态失败'}), 500

# 配置静态文件目录
@app.route('/static/<path:path>')
def serve_static(path):
    """提供静态文件服务"""
    return send_from_directory('src', path)

# 提供策略编辑器页面访问
@app.route('/strategy_editor_frontend.html')
def serve_strategy_editor():
    """提供策略编辑器页面"""
    if os.path.exists('strategy_editor_frontend.html'):
        return send_from_directory('.', 'strategy_editor_frontend.html')
    else:
        return jsonify({'message': '策略编辑器页面未找到'}), 404

# 为Vue应用提供SPA路由支持
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """处理所有未匹配的路由，返回index.html以支持Vue的SPA路由"""
    # 检查是否是API路由，如果是则不处理
    if path.startswith('api/'):
        return jsonify({'message': 'API endpoint not found'}), 404
    
    # 检查是否有构建好的前端文件
    if os.path.exists('dist/index.html'):
        return send_from_directory('dist', 'index.html')
    elif os.path.exists('index.html'):
        return send_from_directory('.', 'index.html')
    else:
        return jsonify({'message': '前端文件未找到'}), 404

if __name__ == '__main__':
    # 导入策略API模块并初始化
    import strategy_api
    strategy_api.register_routes(app)
    strategy_api.init_engines(db_password=DB_CONFIG['password'])
    
    app.run(host='0.0.0.0', port=8000, debug=True)


