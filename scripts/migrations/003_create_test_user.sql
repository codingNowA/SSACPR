-- Migration: 创建测试用户
-- Date: 2026-07-18
-- Description: 创建 id=3 的测试用户，解决简历上传时的外键约束问题

-- 插入或更新 id=3 的测试用户
-- 密码：admin123 的 bcrypt 哈希
INSERT INTO users (id, username, real_name, password_hash, role, email, created_at)
VALUES (
    3,
    'test_user',
    '测试用户',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lWN6U8fMU1FK',
    'student',
    'test_user@example.com',
    NOW()
)
ON CONFLICT (id) DO UPDATE SET
    username = EXCLUDED.username,
    real_name = EXCLUDED.real_name,
    password_hash = EXCLUDED.password_hash,
    role = EXCLUDED.role,
    email = EXCLUDED.email;

-- 如果 id=3 之前不存在，需要调整序列
-- 这样新插入的用户 id 会从 3 之后开始
SELECT setval('users_id_seq', GREATEST(
    (SELECT MAX(id) FROM users),
    3
));

-- 提示信息
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 003 完成：已创建测试用户';
    RAISE NOTICE '用户ID: 3';
    RAISE NOTICE '用户名: test_user';
    RAISE NOTICE '密码: admin123';
    RAISE NOTICE '角色: student';
END $$;
