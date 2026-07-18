# PowerShell 迁移脚本
Write-Host "===== 运行数据库迁移 ====="

# 检查容器是否运行
$containerRunning = docker ps | Select-String "career-postgres"
if (-not $containerRunning) {
    Write-Host "错误: PostgreSQL 容器未运行"
    Write-Host "请先执行: make up 或 docker-compose up -d"
    exit 1
}

Write-Host "复制迁移脚本到容器..."
docker cp scripts/migrations career-postgres://tmp/migrations
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 复制迁移脚本失败"
    exit 1
}

Write-Host "执行迁移 001: 添加 current_version_id 字段..."
docker exec career-postgres bash -c "psql -U career_user -d career_planning -f /tmp/migrations/001_add_current_version_id.sql" 2>&1 | Select-String "NOTICE|ERROR"

Write-Host "执行迁移 002: 修复用户密码哈希..."
docker exec career-postgres bash -c "psql -U career_user -d career_planning -f /tmp/migrations/002_fix_user_passwords.sql" 2>&1 | Select-String "NOTICE|ERROR"

Write-Host "执行迁移 003: 创建测试用户..."
docker exec career-postgres bash -c "psql -U career_user -d career_planning -f /tmp/migrations/003_create_test_user.sql" 2>&1 | Select-String "NOTICE|ERROR"

Write-Host "清理临时文件..."
docker exec career-postgres rm -rf /tmp/migrations

Write-Host "===== 迁移完成 ====="
