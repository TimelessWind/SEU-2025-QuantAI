import json
import pymysql
from strategy_engine import DB_DEFAULTS
from flask import Flask, jsonify
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 模拟get_backtest_detail函数的核心逻辑
def test_get_backtest_detail():
    # 使用已知存在的report_id和user_id
    report_id = "RPT_20250916_172014_600519.SH"
    current_user_id = "admin_001"  # 假设这个用户ID有权限访问该回测结果
    
    connection = None
    try:
        # 连接数据库
        connection = pymysql.connect(
            host=DB_DEFAULTS["host"],
            port=DB_DEFAULTS["port"],
            user=DB_DEFAULTS["user"],
            password=DB_DEFAULTS["password"],
            database=DB_DEFAULTS["database"],
            charset=DB_DEFAULTS["charset"]
        )
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # 查询回测结果
        query = """
        SELECT report_id, strategy_id, user_id, backtest_type, stock_code,
               start_date, end_date, initial_fund, final_fund, total_return,
               annual_return, max_drawdown, sharpe_ratio, win_rate,
               profit_loss_ratio, trade_count, report_generate_time, report_status,
               equity_curve_data, trade_records
        FROM BacktestReport
        WHERE report_id = %s AND user_id = %s
        """
        cursor.execute(query, (report_id, current_user_id))
        result = cursor.fetchone()
        
        if not result:
            print("回测结果不存在或无权访问")
            return
        
        # 打印原始结果
        print("原始数据库结果:")
        print(f"annual_return: {result['annual_return']}")
        print(f"win_rate: {result['win_rate']}")
        print(f"trade_count: {result['trade_count']}")
        
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
            'totalReturn': float(result['total_return']),
            'annualReturn': float(result['annual_return']),
            'maxDrawdown': float(result['max_drawdown']),
            'sharpeRatio': float(result['sharpe_ratio']) if result['sharpe_ratio'] is not None else 0.0,
            'winRate': float(result['win_rate']) if result['win_rate'] is not None else 0.0,
            'profitLossRatio': float(result['profit_loss_ratio']) if result['profit_loss_ratio'] is not None else 0.0,
            'tradeCount': int(result['trade_count']),
            'createTime': result['report_generate_time'],
            'status': result['report_status'],
            'equityCurve': [],
            'trades': []
        }
        
        # 打印处理后的响应
        print("\n处理后的响应对象:")
        print(f"annualReturn: {response['annualReturn']}")
        print(f"winRate: {response['winRate']}")
        print(f"tradeCount: {response['tradeCount']}")
        
        # 处理资金曲线数据 - 简化版
        if result.get('equity_curve_data'):
            try:
                equity_curve_data = json.loads(result['equity_curve_data'])
                print(f"\n资金曲线数据长度: {len(equity_curve_data) if isinstance(equity_curve_data, list) else '不是列表'}")
            except Exception as e:
                print(f"解析资金曲线数据出错: {e}")
        
        # 处理交易记录 - 简化版
        if result.get('trade_records'):
            try:
                trade_records = json.loads(result['trade_records'])
                print(f"交易记录数量: {len(trade_records) if isinstance(trade_records, list) else '不是列表'}")
            except Exception as e:
                print(f"解析交易记录出错: {e}")
        
    except Exception as e:
        print(f"测试过程出错: {e}")
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    test_get_backtest_detail()