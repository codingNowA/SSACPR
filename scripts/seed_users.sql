-- 初始化测试用户
-- 密码：admin123 和 user123 的bcrypt哈希值

-- 清除旧的测试用户（如果存在）
DELETE FROM users WHERE username IN ('admin', 'testuser');

-- 插入管理员账户
-- 用户名: admin, 密码: admin123
INSERT INTO users (username, password_hash, email, role, real_name)
VALUES ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU0k0TUrzZUC', 'admin@example.com', 'admin', '系统管理员')
ON CONFLICT (username) DO UPDATE
SET password_hash = EXCLUDED.password_hash,
    email = EXCLUDED.email,
    role = EXCLUDED.role,
    real_name = EXCLUDED.real_name;

-- 插入测试用户账户
-- 用户名: testuser, 密码: user123
INSERT INTO users (username, password_hash, email, role, real_name)
VALUES ('testuser', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'user@example.com', 'student', '测试用户')
ON CONFLICT (username) DO UPDATE
SET password_hash = EXCLUDED.password_hash,
    email = EXCLUDED.email,
    role = EXCLUDED.role,
    real_name = EXCLUDED.real_name;

-- 提示信息
DO $$
BEGIN
    RAISE NOTICE '测试用户创建成功！';
    RAISE NOTICE '管理员账户：username=admin, password=admin123';
    RAISE NOTICE '普通用户：username=testuser, password=user123';
END $$;
