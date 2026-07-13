# 生产环境部署指南（二期）

本文档说明如何将项目部署到生产服务器。

**注意**：此为二期目标，一期仅需本地部署。

---

## 前置条件

### 服务器要求
- **操作系统**：Ubuntu 22.04 LTS 或 CentOS 8+
- **配置**：
  - 最低：2核 4G 内存 40G 硬盘
  - 推荐：4核 8G 内存 100G 硬盘
- **网络**：
  - 公网 IP
  - 开放端口：80（HTTP）、443（HTTPS）

### 域名（可选）
- 购买域名并解析到服务器 IP
- 申请 SSL 证书（Let's Encrypt 免费）

---

## 部署步骤

### 1. 服务器初始化

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com | bash
sudo systemctl enable docker
sudo systemctl start docker

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

### 2. 配置防火墙

```bash
# Ubuntu (UFW)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# CentOS (firewalld)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 3. 上传代码

```bash
# 方式一：Git 克隆
git clone https://github.com/your-repo/career-planning-agent.git
cd career-planning-agent

# 方式二：SCP 上传
# 在本地执行
scp -r ./career-planning-agent user@your-server-ip:/home/user/
```

### 4. 配置环境变量

```bash
# 复制模板
cp .env.example backend/.env

# 编辑配置（生产环境配置）
vim backend/.env
```

**生产环境必须修改的配置**：
```bash
# 应用环境
APP_ENV=production
DEBUG=false

# 数据库密码（使用强密码）
POSTGRES_PASSWORD=your_strong_password_here

# Redis 密码
REDIS_PASSWORD=your_redis_password_here

# OpenSearch 密码
OPENSEARCH_ADMIN_PASSWORD=your_opensearch_password_here

# JWT 密钥（生成随机密钥）
JWT_SECRET_KEY=your_random_secret_key_here

# LLM API Key
LLM_API_KEY=your_real_api_key
EMBEDDING_API_KEY=your_real_api_key

# CORS（改成你的域名）
CORS_ORIGINS=https://yourdomain.com
```

### 5. 构建前端

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 构建生产版本
npm run build

# 构建完成后，dist/ 目录包含静态文件
cd ..
```

### 6. SSL 证书配置（可选）

如果使用 HTTPS，需要配置 SSL 证书：

```bash
# 使用 Let's Encrypt 免费证书
sudo apt install certbot

# 申请证书
sudo certbot certonly --standalone -d yourdomain.com

# 证书位置
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem

# 复制证书到项目目录
mkdir -p deploy/ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem deploy/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem deploy/ssl/
```

### 7. 启动生产环境

```bash
# 使用生产配置启动
docker-compose -f deploy/docker-compose.prod.yml up -d

# 查看服务状态
docker-compose -f deploy/docker-compose.prod.yml ps

# 查看日志
docker-compose -f deploy/docker-compose.prod.yml logs -f
```

### 8. 验证部署

```bash
# 检查服务健康
curl http://localhost/health

# 检查 API 文档
curl http://localhost/api/docs

# 检查前端
curl http://localhost
```

---

## 运维管理

### 日志查看

```bash
# 查看所有服务日志
docker-compose -f deploy/docker-compose.prod.yml logs -f

# 查看特定服务日志
docker-compose -f deploy/docker-compose.prod.yml logs -f backend

# 查看 Nginx 日志
docker-compose -f deploy/docker-compose.prod.yml exec nginx tail -f /var/log/nginx/access.log
```

### 数据备份

```bash
# PostgreSQL 备份
docker-compose -f deploy/docker-compose.prod.yml exec -T postgres pg_dump -U career_user career_planning > backup_$(date +%Y%m%d).sql

# 自动化备份（添加到 crontab）
0 2 * * * cd /path/to/project && docker-compose -f deploy/docker-compose.prod.yml exec -T postgres pg_dump -U career_user career_planning > /backups/backup_$(date +\%Y\%m\%d).sql
```

### 服务重启

```bash
# 重启所有服务
docker-compose -f deploy/docker-compose.prod.yml restart

# 重启特定服务
docker-compose -f deploy/docker-compose.prod.yml restart backend

# 更新代码后重启
git pull
docker-compose -f deploy/docker-compose.prod.yml up -d --build
```

### 服务停止

```bash
# 停止所有服务
docker-compose -f deploy/docker-compose.prod.yml down

# 停止并删除数据卷（谨慎操作）
docker-compose -f deploy/docker-compose.prod.yml down -v
```

---

## 监控和告警（可选）

### Prometheus + Grafana

TODO：二期实现监控告警系统

---

## 安全加固

### 1. 数据库安全
- ✅ 仅允许本地访问（127.0.0.1）
- ✅ 使用强密码
- ✅ 定期备份

### 2. API 安全
- ✅ 启用 HTTPS
- ✅ 配置 CORS 白名单
- ✅ 启用限流

### 3. 服务器安全
- ✅ 禁用 root 登录
- ✅ 使用 SSH 密钥认证
- ✅ 配置防火墙
- ✅ 定期更新系统

---

## 常见问题

### 1. 服务无法启动

**检查日志**：
```bash
docker-compose -f deploy/docker-compose.prod.yml logs
```

**检查端口占用**：
```bash
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443
```

### 2. OpenSearch 启动失败

**调整系统参数**：
```bash
sudo sysctl -w vm.max_map_count=262144
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
```

### 3. 内存不足

**增加 Swap**：
```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 成本估算

### 云服务器（月付）
| 配置 | 阿里云 | 腾讯云 | 华为云 |
|------|--------|--------|--------|
| 2核4G | ¥70 | ¥65 | ¥68 |
| 4核8G | ¥150 | ¥145 | ¥148 |

### 学生优惠
- 阿里云学生机：¥9.5/月（1核2G）
- 腾讯云学生机：¥10/月（2核4G）

### 域名
- .cn 域名：¥29/年
- .com 域名：¥55/年

### SSL 证书
- Let's Encrypt：免费
- 阿里云 SSL：免费版可用

---

## 联系方式

如有部署问题，请联系：
- 项目负责人：xxx
- 技术支持：xxx
