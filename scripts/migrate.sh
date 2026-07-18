#!/bin/bash
# 数据库迁移脚本 - Linux/macOS/Git Bash 版本
set -e

echo "===== 运行数据库迁移 ====="

# 检查容器是否运行
if ! docker ps | grep -q career-postgres; then
    echo "错误: PostgreSQL 容器未运行"
    echo "请先执行: make up 或 docker-compose up -d"
    exit 1
fi

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "复制迁移脚本到容器..."
docker cp "$PROJECT_DIR/scripts/migrations" career-postgres://tmp/migrations

echo "执行迁移 001: 添加 current_version_id 字段..."
docker exec career-postgres bash -c "psql -U career_user -d career_planning -f /tmp/migrations/001_add_current_version_id.sql" 2>&1 | grep -E "NOTICE|ERROR" || echo "  ✓ 迁移 001 完成"

echo "执行迁移 002: 修复用户密码哈希..."
docker exec career-postgres bash -c "psql -U career_user -d career_planning -f /tmp/migrations/002_fix_user_passwords.sql" 2>&1 | grep -E "NOTICE|ERROR" || echo "  ✓ 迁移 002 完成"

echo "执行迁移 003: 创建测试用户..."
docker exec career-postgres bash -c "psql -U career_user -d career_planning -f /tmp/migrations/003_create_test_user.sql" 2>&1 | grep -E "NOTICE|ERROR" || echo "  ✓ 迁移 003 完成"

echo "清理临时文件..."
docker exec career-postgres rm -rf /tmp/migrations

echo "===== 迁移完成 ====="
