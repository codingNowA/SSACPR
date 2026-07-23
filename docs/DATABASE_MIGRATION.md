# 数据库迁移指南

## 概述

本项目使用SQL迁移脚本来管理数据库schema的变更。所有迁移脚本位于 `scripts/migrations/` 目录。

## 已有的迁移

### Migration 001: 添加 current_version_id 字段
- **文件**: `scripts/migrations/001_add_current_version_id.sql`
- **目的**: 为 `resumes` 表添加 `current_version_id` 字段，用于跟踪当前应用的简历版本
- **操作**:
  - 添加 `current_version_id` 列
  - 添加外键约束到 `resume_versions` 表
  - 为现有简历初始化该字段（设置为最新版本）
  - 创建索引以提高查询性能

### Migration 002: 修复用户密码哈希
- **文件**: `scripts/migrations/002_fix_user_passwords.sql`
- **目的**: 确保所有用户都有有效的 bcrypt 密码哈希
- **操作**:
  - 修复无效或为空的密码哈希
  - 将占位符密码更新为有效的bcrypt哈希
  - 默认密码: `admin123`

### Migration 003: 创建测试用户
- **文件**: `scripts/migrations/003_create_test_user.sql`
- **目的**: 创建 id=3 的测试用户，解决简历上传时的外键约束问题
- **操作**:
  - 插入或更新 id=3 的用户
  - 用户名: `test_user`
  - 密码: `admin123`
  - 角色: `student`

## 运行迁移

### 方法1：使用 Makefile（推荐）

```bash
# 运行所有迁移
make migrate
```

### 方法2：使用脚本

**Linux/macOS/Git Bash:**
```bash
bash scripts/migrate.sh
```

**Windows CMD/PowerShell:**
```cmd
scripts\migrate.bat
```

### 方法3：手动执行

```bash
# 1. 复制迁移脚本到容器
docker cp scripts/migrations career-postgres://tmp/migrations

# 2. 执行迁移
docker exec career-postgres bash -c "psql -U career_user -d career_planning -f /tmp/migrations/001_add_current_version_id.sql"
docker exec career-postgres bash -c "psql -U career_user -d career_planning -f /tmp/migrations/002_fix_user_passwords.sql"
docker exec career-postgres bash -c "psql -U career_user -d career_planning -f /tmp/migrations/003_create_test_user.sql"

# 3. 清理
docker exec career-postgres rm -rf /tmp/migrations
```

## 自动执行迁移

迁移会在以下命令中自动执行：

- `make deploy` - 一键部署时
- `make up` - 启动服务时
- `make restart` - 重启服务时

## 创建新的迁移

1. 在 `scripts/migrations/` 目录下创建新文件
2. 命名格式: `XXX_description.sql` (例如: `004_add_new_table.sql`)
3. 编写SQL语句
4. 在迁移脚本中添加该文件的执行步骤

### 迁移模板

```sql
-- Migration: 迁移描述
-- Date: YYYY-MM-DD
-- Description: 详细说明

-- 在这里编写SQL语句
-- 使用 IF NOT EXISTS 来确保幂等性

ALTER TABLE your_table
ADD COLUMN IF NOT EXISTS your_column VARCHAR(100);

-- 提示信息
DO $$
BEGIN
    RAISE NOTICE '✅ Migration XXX 完成：迁移描述';
END $$;
```

## 迁移最佳实践

1. **幂等性**: 迁移应该可以多次执行而不会出错
   - 使用 `IF NOT EXISTS`
   - 使用 `ON CONFLICT DO NOTHING`
   - 检查约束是否已存在

2. **向后兼容**: 尽可能保持向后兼容
   - 添加列时使用 `DEFAULT` 或 `NULL`
   - 不要随意删除列或表

3. **事务性**: PostgreSQL会自动将DDL包装在事务中

4. **测试**: 在开发环境中充分测试迁移

5. **回滚**: 如果需要回滚，创建反向迁移

## 部署到新设备

当部署到新设备时：

1. **首次部署**:
   ```bash
   make deploy
   ```
   这会自动：
   - 启动所有服务
   - 初始化数据库（通过 `init_db.sql`）
   - 运行所有迁移
   - 填充测试数据

2. **已有数据库**:
   ```bash
   make up      # 启动服务并自动运行迁移
   # 或
   make migrate # 仅运行迁移
   ```

## 验证迁移

检查迁移是否成功：

```bash
# 检查 resumes 表是否有 current_version_id 列
docker exec career-postgres psql -U career_user -d career_planning -c "\d resumes"

# 检查用户密码哈希
docker exec career-postgres psql -U career_user -d career_planning -c "SELECT id, username, LENGTH(password_hash) as hash_length FROM users;"

# 检查测试用户是否存在
docker exec career-postgres psql -U career_user -d career_planning -c "SELECT * FROM users WHERE id=3;"
```

## 故障排除

### 迁移失败

如果迁移失败：

1. 查看错误信息
2. 检查数据库状态
3. 如果需要，手动修复
4. 重新运行迁移

### 重置数据库

如果需要完全重置：

```bash
# 警告：这会删除所有数据！
make clean    # 删除所有容器和数据卷
make deploy   # 重新部署
```

## 已修复的问题

通过这些迁移，我们修复了以下问题：

1. ✅ **简历上传成功但解析失败**: 创建了id=3的测试用户
2. ✅ **获取版本列表失败**: 添加了 `current_version_id` 字段
3. ✅ **bcrypt密码验证失败**: 修复了所有用户的密码哈希
4. ✅ **应用版本Network Error**: 用户需要登录（认证问题）

## 默认账户

所有用户的默认密码都是: `admin123`

- `admin` - 管理员
- `test_student` - 测试学生
- `test_user` - 测试用户 (id=3)

**建议用户首次登录后修改密码。**
