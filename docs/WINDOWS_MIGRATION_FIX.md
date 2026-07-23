# Windows 下运行迁移的解决方案

## 问题
在 Windows PowerShell 环境下运行 `make restart` 时，迁移脚本执行失败。

## 解决方案

### 方案1：直接运行批处理脚本（推荐）
```powershell
# 在 PowerShell 中执行
.\scripts\migrate.bat
```

### 方案2：使用 PowerShell 脚本
```powershell
# 在 PowerShell 中执行
powershell -File .\scripts\migrate.ps1
```

### 方案3：使用 Git Bash
```bash
# 在 Git Bash 中执行
bash scripts/migrate.sh
```

### 方案4：手动执行迁移
```powershell
# 复制迁移脚本到容器
docker cp scripts/migrations career-postgres://tmp/migrations

# 执行迁移
docker exec career-postgres bash -c "psql -U career_user -d career_planning -f /tmp/migrations/001_add_current_version_id.sql"
docker exec career-postgres bash -c "psql -U career_user -d career_planning -f /tmp/migrations/002_fix_user_passwords.sql"
docker exec career-postgres bash -c "psql -U career_user -d career_planning -f /tmp/migrations/003_create_test_user.sql"

# 清理
docker exec career-postgres rm -rf /tmp/migrations
```

## 启动服务（跳过自动迁移）

如果 `make restart` 因为迁移失败而中断，可以：

### 方法1：手动分步执行
```powershell
# 1. 停止服务
docker-compose down

# 2. 启动服务
docker-compose up -d --build

# 3. 等待服务就绪
Start-Sleep -Seconds 15

# 4. 手动运行迁移
.\scripts\migrate.bat
```

### 方法2：修改 Makefile 暂时禁用迁移
在 Makefile 的 `restart` 目标中注释掉迁移步骤：
```makefile
restart:
	@echo "===== 重启 SSACPR 系统 ====="
	@echo "[1/3] 停止服务..."
	$(COMPOSE) down
	@echo "[2/3] 重新构建并启动..."
	$(COMPOSE) up -d --build
	@echo "[3/3] 等待服务就绪..."
	@ping 127.0.0.1 -n 16 >nul 2>&1 || sleep 15 2>/dev/null || echo ""
	# @echo "[4/4] 运行数据库迁移..."
	# @$(MAKE) migrate
	@echo "===== 重启完成 ====="
```

然后手动运行迁移：
```powershell
make restart
.\scripts\migrate.bat
```

## 已更新的 Makefile

更新后的 `migrate` 目标会自动尝试不同的执行方式：
```makefile
migrate:
	@cmd /c scripts\migrate.bat 2>nul || bash scripts/migrate.sh 2>/dev/null || powershell -File scripts/migrate.ps1
```

顺序：
1. 先尝试 Windows 批处理（`migrate.bat`）
2. 如果失败，尝试 Bash（`migrate.sh`）
3. 如果还失败，尝试 PowerShell（`migrate.ps1`）

## 验证迁移是否成功

```powershell
# 检查 current_version_id 字段
docker exec career-postgres psql -U career_user -d career_planning -c "SELECT column_name FROM information_schema.columns WHERE table_name='resumes' AND column_name='current_version_id';"

# 检查用户密码
docker exec career-postgres psql -U career_user -d career_planning -c "SELECT id, username, LENGTH(password_hash) FROM users;"

# 检查测试用户
docker exec career-postgres psql -U career_user -d career_planning -c "SELECT * FROM users WHERE id=3;"
```

## 推荐的完整部署流程（Windows）

```powershell
# 1. 配置环境
Copy-Item backend\.env.example backend\.env
# 手动编辑 backend\.env

# 2. 启动服务
docker-compose up -d --build

# 3. 等待服务就绪
Start-Sleep -Seconds 20

# 4. 运行迁移
.\scripts\migrate.bat

# 5. 验证
docker ps
docker exec career-postgres psql -U career_user -d career_planning -c "SELECT COUNT(*) FROM users;"
```

## 故障排除

### 错误：bash 找不到
**原因**：Windows 环境下 make 尝试调用 bash 但找不到

**解决**：直接运行批处理脚本而不是通过 make
```powershell
.\scripts\migrate.bat
```

### 错误：容器未运行
**原因**：PostgreSQL 容器未启动

**解决**：
```powershell
docker-compose up -d postgres
Start-Sleep -Seconds 10
.\scripts\migrate.bat
```

### 迁移重复执行
**原因**：迁移脚本设计为幂等，可以多次执行

**结果**：不会造成问题，脚本会自动跳过已执行的部分
