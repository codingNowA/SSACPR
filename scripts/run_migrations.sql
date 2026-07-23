-- 数据库迁移执行脚本
-- 按顺序执行所有迁移

\echo '===== 开始执行数据库迁移 ====='
\echo ''

\echo '[1/3] 执行 Migration 001: 添加 current_version_id 字段'
\i scripts/migrations/001_add_current_version_id.sql
\echo ''

\echo '[2/3] 执行 Migration 002: 修复用户密码哈希'
\i scripts/migrations/002_fix_user_passwords.sql
\echo ''

\echo '[3/3] 执行 Migration 003: 创建测试用户'
\i scripts/migrations/003_create_test_user.sql
\echo ''

\echo '===== 所有迁移执行完成 ====='
\echo ''
\echo '数据库已更新到最新版本'
