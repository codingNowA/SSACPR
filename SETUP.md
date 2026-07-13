# 项目环境搭建指南

本文档说明如何使用 Docker 搭建**本地开发环境**（一期目标）。

**注意**：本配置用于本地开发测试，不适用于生产环境。生产服务器部署将在二期实现。

## 环境要求

- Docker Desktop 29.6.1+
- Python 3.10.20
- Node.js 22.14.0
- Git

## 快速开始

### 1. 复制环境变量配置

```bash
# 在项目根目录
cp .env.example backend/.env
```

### 2. 修改配置文件

编辑 `backend/.env`，修改以下配置：

**必需修改**：
```bash
# LLM API Key（通义千问示例）
LLM_API_KEY=sk-your-real-api-key-here
EMBEDDING_API_KEY=sk-your-real-api-key-here

# JWT 密钥（生成随机密钥）
JWT_SECRET_KEY=你的随机密钥
```

**生成 JWT 密钥**（可选）：
```bash
# 使用 Python 生成
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 或使用 OpenSSL
openssl rand -hex 32
```

### 3. 启动所有服务

```bash
# 方式一：使用 docker-compose
docker-compose up -d

# 方式二：使用 Makefile（推荐）
make up
```

### 4. 等待服务启动

第一次启动需要下载镜像和构建，大约需要 5-10 分钟。

查看服务状态：
```bash
docker-compose ps

# 或
make status
```

### 5. 安装 OpenSearch IK 分词器

**重要提示**：由于容器内网络限制，需要在宿主机下载插件包后再安装。

#### 步骤 1：下载 IK 分词器插件包

在浏览器中下载以下文件到项目根目录：
```
https://release.infinilabs.com/analysis-ik/stable/opensearch-analysis-ik-2.11.1.zip
```

备用下载地址：
```
https://github.com/medcl/elasticsearch-analysis-ik/releases
```

#### 步骤 2：执行安装命令

```bash
# 使用 Makefile 自动安装（推荐）
make opensearch-ik

# 或手动执行以下命令
unzip -q opensearch-analysis-ik-2.11.1.zip -d analysis-ik-temp
docker cp analysis-ik-temp/. career-opensearch:/usr/share/opensearch/plugins/analysis-ik/
docker exec -u root career-opensearch sh -c "chown -R opensearch:opensearch /usr/share/opensearch/plugins/analysis-ik"
rm -rf analysis-ik-temp
docker-compose -p career-planning restart opensearch
```

#### 步骤 3：验证安装

等待 OpenSearch 重启完成（约 10 秒），然后验证：

```bash
# 查看已安装的插件
curl http://localhost:9200/_cat/plugins

# 测试 IK 智能分词
curl -X POST "http://localhost:9200/_analyze" -H 'Content-Type: application/json' -d'
{
  "analyzer": "ik_smart",
  "text": "我想找一份软件工程师的工作"
}'

# 测试 IK 最大分词
curl -X POST "http://localhost:9200/_analyze" -H 'Content-Type: application/json' -d'
{
  "analyzer": "ik_max_word",
  "text": "中国科学院计算技术研究所"
}'
```

预期输出应包含分词结果，如：`{"tokens":[...]}`

### 6. 初始化数据库

```bash
# 需要先创建 scripts/init_db.py 文件
make init-db
```

### 7. 访问服务

| 服务 | 地址 | 说明 |
|------|------|------|
| **后端 API** | http://localhost:8000 | FastAPI 服务 |
| **API 文档** | http://localhost:8000/docs | Swagger UI |
| **前端开发服务器** | http://localhost:5173 | React + Vite |
| **Nginx 反向代理** | http://localhost:8080 | 生产模式访问（Windows 下端口 80 受限，改用 8080） |
| **OpenSearch Dashboards** | http://localhost:5601 | 索引管理和调试 |
| **PostgreSQL** | localhost:5432 | 数据库连接 |
| **Redis** | localhost:6379 | 缓存连接 |
| **OpenSearch** | http://localhost:9200 | 搜索引擎 API |

---

## 常用命令

### 服务管理

```bash
# 启动所有服务
make up

# 停止所有服务
make down

# 重启服务
make restart

# 查看服务状态
make status

# 查看日志（所有服务）
make logs

# 查看后端日志
make logs-backend

# 查看 OpenSearch 日志
make logs-opensearch
```

### 开发调试

```bash
# 进入后端容器
make shell-backend

# 进入数据库
make shell-db

# 进入 Redis
make shell-redis

# 运行测试
make test

# 代码检查
make lint

# 代码格式化
make format
```

### 数据库操作

```bash
# 初始化数据库
make init-db

# 填充测试数据
make seed-data

# 备份数据库
make backup

# 恢复数据库
make restore
```

---

## 目录结构

```
project-root/
├── backend/               # 后端代码
│   ├── Dockerfile        # 后端镜像构建
│   ├── requirements.txt  # Python 依赖
│   ├── main.py           # 应用入口（需要创建）
│   ├── config/           # 配置文件
│   ├── app/              # 应用代码
│   └── .env              # 环境变量（本地，不提交）
├── frontend/             # 前端代码
│   ├── Dockerfile.dev    # 前端开发镜像
│   └── package.json      # Node 依赖（需要创建）
├── deploy/               # 部署配置
│   └── nginx.conf        # Nginx 配置
├── docker/               # Docker 相关
│   └── opensearch/       # OpenSearch 配置
├── scripts/              # 脚本文件
├── uploads/              # 上传文件目录
├── logs/                 # 日志目录
├── docker-compose.yml    # Docker 编排
├── .env.example          # 环境变量模板
├── .dockerignore         # Docker 忽略文件
└── Makefile              # 快捷命令
```

---

## 数据库配置

### PostgreSQL

- **用户名**: career_user
- **密码**: career_password（生产环境请修改）
- **数据库**: career_planning
- **端口**: 5432

**连接字符串**：
```
postgresql://career_user:career_password@localhost:5432/career_planning
```

### Redis

- **端口**: 6379
- **密码**: 无（开发环境）
- **最大内存**: 512MB
- **淘汰策略**: allkeys-lru

### OpenSearch

- **端口**: 9200（HTTP）、9600（性能监控）
- **用户名**: admin（已禁用安全插件）
- **密码**: admin
- **集群名**: career-cluster

**测试连接**：
```bash
curl http://localhost:9200/_cluster/health?pretty
```

---

## LLM 服务商配置

### 通义千问（默认）

```bash
LLM_PROVIDER=qwen
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_API_KEY=sk-your-api-key
LLM_MODEL=qwen-turbo

EMBEDDING_PROVIDER=qwen
EMBEDDING_MODEL=text-embedding-v2
```

### 智谱 AI

```bash
LLM_PROVIDER=zhipu
LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
LLM_API_KEY=your-api-key
LLM_MODEL=glm-4

EMBEDDING_PROVIDER=zhipu
EMBEDDING_MODEL=embedding-2
```

### DeepSeek

```bash
LLM_PROVIDER=deepseek
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_API_KEY=your-api-key
LLM_MODEL=deepseek-chat

EMBEDDING_PROVIDER=local
EMBEDDING_LOCAL_MODEL=BAAI/bge-large-zh-v1.5
```

### 月之暗面（Moonshot）

```bash
LLM_PROVIDER=moonshot
LLM_BASE_URL=https://api.moonshot.cn/v1
LLM_API_KEY=your-api-key
LLM_MODEL=moonshot-v1-8k

EMBEDDING_PROVIDER=local
EMBEDDING_LOCAL_MODEL=BAAI/bge-large-zh-v1.5
```

---

## 常见问题

### 0. Docker Compose 项目名称错误（中文目录名问题）

**错误信息**：
```
project name must not be empty
```

**原因**：项目路径包含中文字符（如"大项目"），导致 Docker Compose 无法正确识别项目名称。

**解决方案**：已在 Makefile 中显式指定项目名称

```makefile
# Makefile 中的配置
PROJECT_NAME = career-planning
COMPOSE = docker-compose -p $(PROJECT_NAME)
```

**使用方式**：
```bash
# 使用 Makefile 命令（推荐）
make up
make down
make status

# 或手动指定项目名称
docker-compose -p career-planning up -d
docker-compose -p career-planning down
```

**注意**：不要直接使用 `docker-compose up`，必须通过 `make` 命令或手动指定 `-p career-planning` 参数。

### 1. OpenSearch 启动失败

**错误**: `max virtual memory areas vm.max_map_count [65530] is too low`

**解决**（Windows + Docker Desktop）：
```powershell
# 以管理员身份运行 PowerShell
wsl -d docker-desktop
sysctl -w vm.max_map_count=262144
exit
```

**持久化配置**：
在 Docker Desktop 设置中，Resources -> WSL Integration，然后在 WSL 中配置：
```bash
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### 2. 后端无法连接数据库

**检查数据库是否启动**：
```bash
docker-compose ps postgres
```

**查看数据库日志**：
```bash
docker-compose logs postgres
```

**手动测试连接**：
```bash
docker-compose exec postgres psql -U career_user -d career_planning
```

### 3. IK 分词器安装失败

#### 问题 1：容器内无法下载插件（网络限制）

**错误信息**：
```
Exception in thread "main" java.io.FileNotFoundException: https://github.com/...
```

**原因**：容器内无法访问 GitHub 或缺少代理配置。

**解决方案**：在宿主机下载后手动安装

```bash
# 1. 下载插件包到项目根目录
# https://release.infinilabs.com/analysis-ik/stable/opensearch-analysis-ik-2.11.1.zip

# 2. 使用 Makefile 安装
make opensearch-ik

# 3. 验证安装
curl http://localhost:9200/_cat/plugins
```

#### 问题 2：插件安装权限被拒绝

**错误信息**：
```
java.nio.file.AccessDeniedException: /usr/share/opensearch/plugins/.installing-xxx -> /usr/share/opensearch/plugins/analysis-ik
```

**原因**：plugins 目录权限不正确。

**解决方案**：

```bash
# 1. 修复权限
docker exec -u root career-opensearch sh -c "chown -R opensearch:opensearch /usr/share/opensearch/plugins/"

# 2. 使用手动安装方式（推荐）
unzip -q opensearch-analysis-ik-2.11.1.zip -d analysis-ik-temp
docker cp analysis-ik-temp/. career-opensearch:/usr/share/opensearch/plugins/analysis-ik/
docker exec -u root career-opensearch sh -c "chown -R opensearch:opensearch /usr/share/opensearch/plugins/analysis-ik"
rm -rf analysis-ik-temp
docker-compose -p career-planning restart opensearch

# 3. 验证安装
sleep 10
curl http://localhost:9200/_cat/plugins
```

#### 问题 3：插件需要确认权限但无法交互

**错误信息**：
```
java.lang.IllegalStateException: unable to read from standard input; is standard input open and a tty attached?
```

**原因**：在非交互式环境下安装插件需要确认权限。

**解决方案**：使用 `--batch` 参数或采用手动解压方式（推荐）

```bash
# 方式 1：使用 --batch 参数（可能仍有权限问题）
docker-compose -p career-planning exec opensearch bin/opensearch-plugin install --batch file:///tmp/plugin.zip

# 方式 2：手动解压安装（推荐，避免所有交互式问题）
# 参考上面"问题 2"的解决方案
```

#### 验证 IK 分词器是否安装成功

三种验证方法：

```bash
# 1. 查看插件列表（应显示 analysis-ik 2.11.1）
curl http://localhost:9200/_cat/plugins

# 2. 测试 ik_smart 智能分词
curl -X POST "http://localhost:9200/_analyze" -H 'Content-Type: application/json' -d'
{
  "analyzer": "ik_smart",
  "text": "我是一名Java开发工程师"
}'

# 3. 测试 ik_max_word 最大分词
curl -X POST "http://localhost:9200/_analyze" -H 'Content-Type: application/json' -d'
{
  "analyzer": "ik_max_word",
  "text": "中国科学院计算技术研究所"
}'
```

**ik_smart vs ik_max_word 的区别**：
- `ik_smart`：智能分词，粗粒度切分，适合短语匹配和查询
- `ik_max_word`：最大分词，细粒度切分，适合全文搜索和建立索引

**推荐用法**：
- 建立索引时使用 `ik_max_word`（提高召回率）
- 查询时使用 `ik_smart`（提高准确率）

### 4. 前端无法访问后端 API

**检查 CORS 配置**：
确保 `backend/.env` 中包含前端地址：
```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:80
```

**重启后端服务**：
```bash
docker-compose restart backend
```

### 5. 端口被占用

#### Windows 下端口 80 被占用

**错误信息**：
```
Error response from daemon: Ports are not available: exposing port TCP 0.0.0.0:80 -> 127.0.0.1:0: listen tcp 0.0.0.0:80: bind: An attempt was made to access a socket in a way forbidden by its access permissions
```

**原因**：Windows 系统进程（通常是 IIS 或 HTTP.sys）占用端口 80。

**解决方案**：修改 Nginx 端口为 8080

已在 `docker-compose.yml` 中修改：
```yaml
nginx:
  ports:
    - "8080:80"  # 使用 8080 代替 80
```

访问地址变更为：http://localhost:8080

#### 其他端口被占用

**查看端口占用**（Windows）：
```powershell
netstat -ano | findstr :8000
```

**修改端口**（docker-compose.yml）：
```yaml
backend:
  ports:
    - "8001:8000"  # 改成 8001
```

---

## 下一步

1. 创建 `backend/main.py` - FastAPI 应用入口
2. 创建 `scripts/init_db.py` - 数据库初始化脚本
3. 实现核心业务逻辑
4. 搭建前端项目

参考 [ARCHITECTURE.md](./ARCHITECTURE.md) 了解详细的代码架构。
