@echo off
REM 数据库迁移脚本 - Windows 批处理版本
echo ===== 运行数据库迁移 =====

REM 检查容器是否运行
docker ps | findstr career-postgres >nul
if errorlevel 1 (
    echo 错误: PostgreSQL 容器未运行
    echo 请先执行: make up 或 docker-compose up -d
    exit /b 1
)

echo 复制迁移脚本到容器...
docker cp scripts/migrations career-postgres:/tmp/migrations
if errorlevel 1 (
    echo 错误: 复制迁移脚本失败
    exit /b 1
)

echo 执行迁移 001: 添加 current_version_id 字段...
docker exec career-postgres psql -U career_user -d career_planning -f /tmp/migrations/001_add_current_version_id.sql
if errorlevel 1 (
    echo 警告: 迁移 001 执行失败，继续下一个迁移...
)

echo 执行迁移 002: 修复用户密码哈希...
docker exec career-postgres psql -U career_user -d career_planning -f /tmp/migrations/002_fix_user_passwords.sql
if errorlevel 1 (
    echo 警告: 迁移 002 执行失败，继续下一个迁移...
)

echo 执行迁移 003: 创建测试用户...
docker exec career-postgres psql -U career_user -d career_planning -f /tmp/migrations/003_create_test_user.sql
if errorlevel 1 (
    echo 警告: 迁移 003 执行失败
)

echo 清理临时文件...
docker exec career-postgres rm -rf /tmp/migrations

echo ===== 迁移完成 =====
