-- Migration: 修复用户密码哈希
-- Date: 2026-07-18
-- Description: 确保所有用户都有有效的 bcrypt 密码哈希

-- 修复无效的密码哈希（长度不足60字符或为空）
UPDATE users
SET password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lWN6U8fMU1FK'
WHERE password_hash IS NULL
   OR password_hash = ''
   OR LENGTH(password_hash) < 50
   OR password_hash = '$2b$12$placeholder_hash';

-- 注意：上述哈希对应的明文密码是 admin123
-- 用户首次登录后应该修改密码

-- 提示信息
DO $$
DECLARE
    updated_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO updated_count
    FROM users
    WHERE password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lWN6U8fMU1FK';

    RAISE NOTICE '✅ Migration 002 完成：已修复密码哈希';
    RAISE NOTICE '受影响的用户数量: %', updated_count;
    RAISE NOTICE '默认密码: admin123（建议用户登录后修改）';
END $$;
