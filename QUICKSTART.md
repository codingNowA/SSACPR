# 🚀 快速部署指南

## 一键部署（推荐）

```bash
# 1. 配置环境
cp backend/.env.example backend/.env
# 编辑 backend/.env

# 2. 部署
make deploy

# 3. 访问
# 前端: http://localhost:5173
# API文档: http://localhost:8000/docs

# 4. 登录
# 用户名: test_student
# 密码: admin123
```

## 常用命令

```bash
make up          # 启动服务（自动运行迁移）
make down        # 停止服务
make restart     # 重启服务
make migrate     # 运行数据库迁移
make logs        # 查看日志
make clean       # 清理所有数据（⚠️ 慎用）
```

## 已修复的问题 ✅

| 问题 | 状态 |
|------|------|
| 简历上传失败（外键错误） | ✅ 已修复 |
| 版本列表加载失败 | ✅ 已修复 |
| 密码验证失败 | ✅ 已修复 |
| 应用版本Network Error | ✅ 需登录 |

## 默认账户

所有用户默认密码：`admin123`

- `admin` - 管理员
- `test_student` - 测试学生
- `test_user` - 测试用户

## 详细文档

- [DATABASE_MIGRATION.md](docs/DATABASE_MIGRATION.md) - 迁移指南
- [DEPLOYMENT.md](DEPLOYMENT.md) - 完整部署清单
- [错误分析报告](错误原因-应用覆盖当前版本NetworkError.md)

---

**部署时间**: 约 5-10 分钟  
**难度**: ⭐⭐ 中等
