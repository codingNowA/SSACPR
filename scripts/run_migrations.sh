#!/bin/bash
# 数据库迁移脚本
# 用于在 Docker 容器中执行数据库迁移

set -e

echo "===== 数据库迁移工具 ====="
echo ""

# 检查 Docker 容器是否运行
if ! docker ps | grep -q career-postgres; then
    echo "错误: PostgreSQL 容器未运行"
    echo "请先执行: make up"
    exit 1
fi

echo "PostgreSQL 容器正在运行"
echo ""

# 复制迁移脚本到容器
echo "复制迁移脚本到容器..."
docker cp scripts/migrations career-postgres:/tmp/migrations/
docker cp scripts/run_migrations.sql career-postgres:/tmp/run_migrations.sql

# 执行迁移
echo ""
echo "开始执行迁移..."
echo ""
docker exec -i career-postgres psql -U career_user -d career_planning -f /tmp/run_migrations.sql

# 清理临时文件
docker exec career-postgres rm -rf /tmp/migrations /tmp/run_migrations.sql

echo ""
echo "===== 迁移完成 ====="
