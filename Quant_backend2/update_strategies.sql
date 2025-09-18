-- 调整字段长度
ALTER TABLE `strategy` MODIFY COLUMN `strategy_type` VARCHAR(50) NOT NULL;

-- 同步策略类型与代码定义
REPLACE INTO `strategy` (strategy_type, strategy_name, strategy_desc, creator_id, create_time)
VALUES
  ('moving_average', '双均线策略', '基于短期和长期移动平均线交叉的交易策略', 0, NOW()),
  ('breakout', '突破策略', '基于价格突破历史高低点的交易策略', 0, NOW()),
  ('rsi_mean_reversion', 'RSI均值回归策略', '基于RSI指标超买超卖的均值回归策略', 0, NOW());

-- 验证更新结果
SELECT * FROM strategy WHERE strategy_type IN ('moving_average','breakout','rsi_mean_reversion');