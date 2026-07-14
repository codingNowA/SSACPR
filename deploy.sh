#!/bin/bash
# ============================================================
# SSACPR 一键部署脚本
# 用法: bash deploy.sh
# ============================================================
set -e

echo "=========================================="
echo "  SSACPR 智慧学工职业规划推荐智能体 - 部署"
echo "=========================================="

# ---- 1. 检查 backend/.env ----
if [ ! -f backend/.env ]; then
    if [ -f .env.example ]; then
        echo "[1/6] 从 .env.example 创建 backend/.env ..."
        cp .env.example backend/.env
        echo "  ⚠️  请编辑 backend/.env 填入真实配置（LLM_API_KEY、POSTGRES_PASSWORD 等）"
        echo "  填好后重新运行 bash deploy.sh"
        exit 1
    else
        echo "  ❌ 未找到 backend/.env 文件"
        exit 1
    fi
else
    echo "[1/6] backend/.env 已存在 ✓"
fi

# ---- 2. 构建 & 启动容器 ----
echo "[2/6] 构建并启动 Docker 容器..."
docker-compose up -d --build
echo "  等待服务就绪..."
sleep 10

# ---- 3. 初始化数据库 ----
echo "[3/6] 检查数据库表..."
TABLE_COUNT=$(docker exec career-postgres psql -U career_user -d career_planning -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema='public';" 2>/dev/null || echo "0")
if [ "$TABLE_COUNT" -lt 5 ]; then
    echo "  表数量不足，执行 init_db.sql ..."
    docker exec career-postgres psql -U career_user -d career_planning -f /docker-entrypoint-initdb.d/init.sql
    echo "  数据库表创建完成 ✓"
else
    echo "  数据库表已存在 ($TABLE_COUNT 张表) ✓"
fi

# ---- 4. 录入测试岗位数据 ----
echo "[4/6] 检查岗位数据..."
JOB_COUNT=$(docker exec career-postgres psql -U career_user -d career_planning -t -c "SELECT count(*) FROM jobs;" 2>/dev/null || echo "0")
if [ "$JOB_COUNT" -lt 3 ]; then
    echo "  岗位数据不足，录入测试数据..."
    docker cp scripts/seed_jobs.sql career-postgres:/tmp/seed_jobs.sql
    docker exec career-postgres psql -U career_user -d career_planning -f /tmp/seed_jobs.sql
    echo "  测试岗位数据录入完成 ✓"
else
    echo "  岗位数据已存在 ($JOB_COUNT 条) ✓"
fi

# ---- 5. 健康检查 ----
echo "[5/6] 服务健康检查..."
HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null || echo "unavailable")
echo "  API: $HEALTH"

# ---- 6. 完成 ----
echo "[6/6] 部署完成！"
echo "=========================================="
echo "  服务地址："
echo "    API 文档:  http://localhost:8000/docs"
echo "    前端:      http://localhost:5173"
echo "    Nginx:     http://localhost:8080"
echo "    OpenSearch: http://localhost:5601"
echo "=========================================="
echo "  测试流程："
echo "    1. Swagger UI → POST /api/v1/resume/upload 上传简历"
echo "    2. Swagger UI → POST /api/v1/match/calculate 岗位匹配"
echo "    3. Swagger UI → POST /api/v1/match/explain 匹配解释"
echo "=========================================="
