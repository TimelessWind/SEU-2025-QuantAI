USE quantitative_trading;

-- 向User表添加缺失的列
alter table User
add column login_attempts INT DEFAULT 0,
add column locked_until DATETIME NULL,
add column last_failed_login DATETIME NULL;

-- 添加索引以优化查询
CREATE INDEX idx_locked_until ON User(locked_until);
CREATE INDEX idx_last_failed_login ON User(last_failed_login);

-- 添加管理员用户（如果不存在）
INSERT INTO User (user_id, user_account, user_password, user_role, user_status, user_email, user_phone)
SELECT 'user_admin', 'admin', 'e10adc3949ba59abbe56e057f20f883e', 'admin', 'active', 'admin@example.com', '13800138000'
WHERE NOT EXISTS (SELECT 1 FROM User WHERE user_account = 'admin');

-- 添加测试用户（如果不存在）
INSERT INTO User (user_id, user_account, user_password, user_role, user_status, user_email, user_phone)
SELECT 'user_test', 'test_user', 'e10adc3949ba59abbe56e057f20f883e', 'analyst', 'active', 'test@example.com', '13800138001'
WHERE NOT EXISTS (SELECT 1 FROM User WHERE user_account = 'test_user');

SELECT '数据库结构已更新，已添加缺失的列和示例用户。';