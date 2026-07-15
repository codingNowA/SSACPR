# SSACPR 一键部署脚本 (PowerShell 版)
# 用法: .\deploy.ps1

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  SSACPR 智慧学工职业规划推荐智能体 - 部署" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# ---- 1. 检查 .env ----
Write-Host "[1/6] 检查 backend/.env 配置文件..." -NoNewline
if (-not (Test-Path backend/.env)) {
    if (Test-Path .env.example) {
        Copy-Item .env.example backend/.env
        Write-Host " 已创建" -ForegroundColor Yellow
        Write-Host "  ⚠️  请编辑 backend/.env 填入真实配置（LLM_API_KEY、POSTGRES_PASSWORD 等）" -ForegroundColor Yellow
        Write-Host "  填好后重新运行 .\deploy.ps1" -ForegroundColor Yellow
        exit 1
    } else {
        Write-Host " ❌ 未找到 backend/.env 文件" -ForegroundColor Red
        exit 1
    }
}
Write-Host " 已存在 ✓" -ForegroundColor Green

# ---- 2. 构建 & 启动容器 ----
Write-Host "[2/6] 构建并启动 Docker 容器..." -ForegroundColor Cyan
docker-compose up -d --build
Write-Host "  等待服务就绪..." -ForegroundColor DarkGray
Start-Sleep -Seconds 15

# ---- 3. 初始化数据库 ----
Write-Host "[3/6] 检查数据库表..." -NoNewline
$TABLE_COUNT = (docker exec career-postgres psql -U career_user -d career_planning -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema='public';" 2>$null | ForEach-Object { $_.Trim() } | Where-Object { $_ -match '^\d+$' } | Select-Object -First 1)
if ([int]$TABLE_COUNT -lt 5) {
    Write-Host " 表数量不足，执行初始化..." -ForegroundColor Yellow
    docker exec career-postgres psql -U career_user -d career_planning -f /docker-entrypoint-initdb.d/init.sql
    Write-Host "  数据库表创建完成 ✓" -ForegroundColor Green
} else {
    Write-Host " 已有 $TABLE_COUNT 张表 ✓" -ForegroundColor Green
}

# ---- 4. 录入测试岗位数据 ----
Write-Host "[4/6] 检查岗位数据..." -NoNewline
$JOB_COUNT = (docker exec career-postgres psql -U career_user -d career_planning -t -c "SELECT count(*) FROM jobs;" 2>$null | ForEach-Object { $_.Trim() } | Where-Object { $_ -match '^\d+$' } | Select-Object -First 1)
if ([int]$JOB_COUNT -lt 3) {
    Write-Host " 岗位数据不足，录入测试数据..." -ForegroundColor Yellow
    docker cp scripts/seed_jobs.sql career-postgres:/tmp/seed_jobs.sql
    docker exec career-postgres psql -U career_user -d career_planning -f /tmp/seed_jobs.sql
    Write-Host "  测试岗位数据录入完成 ✓" -ForegroundColor Green
} else {
    Write-Host " 已有 $JOB_COUNT 条岗位 ✓" -ForegroundColor Green
}

# ---- 5. 健康检查 ----
Write-Host "[5/6] 服务健康检查..." -NoNewline
try {
    $HEALTH = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 10
    Write-Host " API=$( $HEALTH.status )" -ForegroundColor Green
} catch {
    Write-Host " API 未就绪（可能仍在启动）" -ForegroundColor Yellow
}

# ---- 6. 完成 ----
Write-Host "[6/6] 部署完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  服务地址：" -ForegroundColor Cyan
Write-Host "    API 文档:   http://localhost:8000/docs"
Write-Host "    前端:       http://localhost:5173"
Write-Host "    Nginx:      http://localhost:8080"
Write-Host "    OpenSearch: http://localhost:5601"
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  测试流程：" -ForegroundColor Cyan
Write-Host "    1. Swagger UI → POST /api/v1/resume/upload 上传简历"
Write-Host "    2. Swagger UI → POST /api/v1/match/calculate 岗位匹配"
Write-Host "    3. Swagger UI → POST /api/v1/match/explain 匹配解释"
Write-Host "==========================================" -ForegroundColor Cyan
