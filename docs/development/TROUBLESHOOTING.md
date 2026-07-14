# 常见问题排查指南

## 认证问题

### 问题：接口返回 "未提供认证凭据"

**现象：**
```json
{
  "detail": "未提供认证凭据"
}
```

**原因：**
开发环境下应该自动跳过 JWT 认证，但 Docker 容器中的环境变量没有正确加载。

**解决方案：**

#### 方案 1：完全重启 Docker 服务（推荐）

```bash
# 停止并删除所有容器
make down

# 重新构建并启动
make up
```

#### 方案 2：仅重启后端服务

```bash
# 停止并删除后端容器
docker-compose down backend

# 重新构建并启动后端
docker-compose up -d --build backend

# 等待服务就绪（15秒）
sleep 15
```

#### 方案 3：手动清理容器和镜像

```bash
# 停止所有服务
docker-compose down

# 删除后端镜像（强制重新构建）
docker rmi ssacpr-backend

# 清理未使用的镜像和缓存
docker system prune -f

# 重新启动
make up
```

**验证配置：**

1. 检查 `backend/.env` 文件，确保 `JWT_SECRET_KEY` 被注释：
```env
# JWT_SECRET_KEY=tHXCFfEAXBmBUFweppo0N5NuGxK5Glzme7sooI_1M9U
```

2. 检查 Docker 容器环境变量：
```bash
docker exec career-backend env | grep APP_ENV
# 应该输出: APP_ENV=development

docker exec career-backend env | grep JWT_SECRET_KEY
# 应该没有输出（变量未设置）
```

3. 测试接口：
```bash
# 不带 token 直接访问（应该成功）
curl http://localhost:8000/api/v1/jobs/
```

**如果问题依然存在：**

检查是否有其他地方设置了 `APP_ENV=production` 或 `JWT_SECRET_KEY`：

```bash
# 检查系统环境变量
echo $APP_ENV
echo $JWT_SECRET_KEY

# 检查 Docker Compose 文件
grep -n "APP_ENV\|JWT_SECRET_KEY" docker-compose.yml

# 检查容器内实际环境变量
docker exec career-backend printenv | grep -E "APP_ENV|JWT_SECRET_KEY"
```

---

## 其他常见问题

### 问题：端口已被占用

**现象：**
```
Error: Bind for 0.0.0.0:8000 failed: port is already allocated
```

**解决方案：**

1. 查找占用端口的进程：
```bash
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000
```

2. 停止占用端口的进程或修改 `docker-compose.yml` 中的端口映射。

### 问题：数据库连接失败

**现象：**
```
could not connect to server: Connection refused
```

**解决方案：**

1. 检查数据库容器是否正常运行：
```bash
docker ps | grep postgres
```

2. 查看数据库日志：
```bash
docker logs career-postgres
```

3. 等待数据库健康检查通过：
```bash
docker inspect career-postgres | grep Health
```

### 问题：前端无法访问后端 API

**现象：**
前端页面显示网络错误或 CORS 错误

**解决方案：**

1. 检查后端服务是否运行：
```bash
curl http://localhost:8000/docs
```

2. 检查前端环境变量：
```bash
docker exec career-frontend env | grep VITE_API_BASE_URL
# 应该输出: VITE_API_BASE_URL=http://localhost:8000
```

3. 如果是 CORS 错误，检查 `backend/app/main.py` 中的 CORS 配置。

---

## 快速命令参考

### 查看服务状态
```bash
docker-compose ps
```

### 查看服务日志
```bash
# 所有服务
docker-compose logs

# 特定服务
docker-compose logs backend
docker-compose logs postgres

# 实时跟踪日志
docker-compose logs -f backend
```

### 进入容器调试
```bash
# 进入后端容器
docker exec -it career-backend bash

# 进入数据库容器
docker exec -it career-postgres psql -U career_user -d career_planning
```

### 清理环境
```bash
# 停止所有服务
make down

# 删除所有数据（谨慎使用）
docker-compose down -v

# 清理 Docker 系统
docker system prune -a
```
