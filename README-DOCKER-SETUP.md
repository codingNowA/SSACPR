# Docker 环境配置说明

## 已生成的文件清单

### ✅ 核心配置文件
- [x] `.env.example` - 环境变量模板
- [x] `docker-compose.yml` - Docker 服务编排
- [x] `.dockerignore` - Docker 忽略文件
- [x] `backend/Dockerfile` - 后端镜像构建
- [x] `backend/requirements.txt` - Python 依赖
- [x] `frontend/Dockerfile.dev` - 前端开发镜像
- [x] `deploy/nginx.conf` - Nginx 配置
- [x] `Makefile` - 快捷命令
- [x] `scripts/init_db.sql` - 数据库初始化脚本

### 📋 技术栈版本

**后端**：
- Python: 3.10.20
- FastAPI: 0.139.0
- Pydantic: 2.13.4
- SQLAlchemy: 2.0.51

**数据库**：
- PostgreSQL: 15-alpine
- OpenSearch: 2.11.1（含 IK 分词器）
- Redis: 7.2-alpine

**前端**：
- Node.js: 22.14.0
- React + TypeScript

**其他**：
- Nginx: 1.25-alpine
- Docker: 29.6.1

---

## 快速启动步骤

### 1. 配置环境变量

```bash
# 复制模板
cp .env.example backend/.env

# 编辑 backend/.env，修改以下内容：
# - LLM_API_KEY（必需）
# - EMBEDDING_API_KEY（必需）
# - JWT_SECRET_KEY（必需）
# - 数据库密码（生产环境必需）
```

### 2. 启动服务

```bash
# 方式一：使用 Makefile（推荐）
make up

# 方式二：使用 docker-compose
docker-compose up -d
```

### 3. 验证服务

```bash
# 查看服务状态
make status

# 查看日志
make logs
```

### 4. 安装 IK 分词器

```bash
# 等待 OpenSearch 完全启动后（约 30 秒）
make opensearch-ik
```

### 5. 初始化数据库

数据库会自动执行 `scripts/init_db.sql` 脚本创建表结构。

---

## 服务访问地址

| 服务 | 地址 | 用户名/密码 |
|------|------|------------|
| 后端 API | http://localhost:8000 | - |
| API 文档 | http://localhost:8000/docs | - |
| 前端开发 | http://localhost:5173 | - |
| Nginx 代理 | http://localhost:80 | - |
| OpenSearch | http://localhost:9200 | admin/admin（已禁用） |
| OpenSearch Dashboards | http://localhost:5601 | - |
| PostgreSQL | localhost:5432 | career_user/career_password |
| Redis | localhost:6379 | - |

---

## 国内加速配置

### Docker 镜像加速

**Docker Desktop 配置**（Settings -> Docker Engine）：
```json
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://dockerproxy.com",
    "https://mirror.baidubce.com"
  ]
}
```

### Python pip 加速

已在 `backend/Dockerfile` 中配置清华镜像源：
```dockerfile
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### Node.js npm 加速

已在 `frontend/Dockerfile.dev` 中配置淘宝镜像源：
```dockerfile
RUN npm config set registry https://registry.npmmirror.com
```

---

## LLM 服务商配置

### 通义千问（默认）

```bash
LLM_PROVIDER=qwen
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_API_KEY=sk-xxxxx
LLM_MODEL=qwen-turbo

EMBEDDING_PROVIDER=qwen
EMBEDDING_MODEL=text-embedding-v2
EMBEDDING_API_KEY=sk-xxxxx
```

**获取 API Key**：https://dashscope.console.aliyun.com/apiKey

### 智谱 AI

```bash
LLM_PROVIDER=zhipu
LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
LLM_API_KEY=xxxxx.xxxxx
LLM_MODEL=glm-4

EMBEDDING_PROVIDER=zhipu
EMBEDDING_MODEL=embedding-2
```

**获取 API Key**：https://open.bigmodel.cn/usercenter/apikeys

### DeepSeek

```bash
LLM_PROVIDER=deepseek
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_API_KEY=sk-xxxxx
LLM_MODEL=deepseek-chat

# DeepSeek 没有 Embedding 模型，使用本地模型
EMBEDDING_PROVIDER=local
EMBEDDING_LOCAL_MODEL=BAAI/bge-large-zh-v1.5
```

**获取 API Key**：https://platform.deepseek.com/api_keys

---

## 常用命令

```bash
# 查看帮助
make help

# 启动服务
make up

# 停止服务
make down

# 重启服务
make restart

# 查看日志
make logs
make logs-backend
make logs-opensearch

# 进入容器
make shell-backend
make shell-db
make shell-redis

# 数据库操作
make init-db
make seed-data
make backup
make restore

# 开发工具
make test
make lint
make format

# 清理环境（删除所有数据）
make clean
```

---

## 故障排查

### OpenSearch 启动失败

**错误信息**：
```
max virtual memory areas vm.max_map_count [65530] is too low
```

**解决方法**（Windows + Docker Desktop）：
```powershell
# 以管理员运行 PowerShell
wsl -d docker-desktop
sysctl -w vm.max_map_count=262144
exit
```

### 端口冲突

如果某个端口被占用，修改 `docker-compose.yml`：

```yaml
backend:
  ports:
    - "8001:8000"  # 改成其他端口
```

### 数据库连接失败

```bash
# 检查数据库状态
docker-compose ps postgres

# 查看数据库日志
docker-compose logs postgres

# 手动连接测试
docker-compose exec postgres psql -U career_user -d career_planning
```

### IK 分词器安装失败

```bash
# 进入容器手动安装
docker-compose exec opensearch bash

cd /tmp
curl -L -O https://github.com/aparo/opensearch-analysis-ik/releases/download/2.11.1/opensearch-analysis-ik-2.11.1.zip
/usr/share/opensearch/bin/opensearch-plugin install file:///tmp/opensearch-analysis-ik-2.11.1.zip

exit

# 重启
docker-compose restart opensearch
```

---

## 下一步

1. ✅ 环境配置完成
2. ⬜ 创建 `backend/main.py`（FastAPI 应用入口）
3. ⬜ 实现核心业务逻辑
4. ⬜ 搭建前端项目
5. ⬜ 填充测试数据

参考 [SETUP.md](./SETUP.md) 了解详细的使用说明。
