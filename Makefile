.PHONY: help install dev up start down logs clean test lint format init-db seed-data

# Docker Compose 命令（env_file 统一从 backend/.env 读取）
COMPOSE = docker-compose

# 默认目标
help:
	@echo "可用命令："
	@echo "  make deploy         - 一键部署（构建+启动+初始化+测试数据）"
	@echo "  make install        - 安装依赖（Python + Node.js）"
	@echo "  make dev            - 启动开发环境"
	@echo "  make up             - 启动所有 Docker 服务"
	@echo "  make down           - 停止所有服务"
	@echo "  make logs           - 查看服务日志"
	@echo "  make clean          - 清理所有容器和数据卷"
	@echo "  make test           - 运行测试"
	@echo "  make lint           - 代码检查"
	@echo "  make format         - 代码格式化"
	@echo "  make init-db        - 初始化数据库"
	@echo "  make seed-data      - 填充测试数据"
	@echo "  make opensearch-ik  - 安装 OpenSearch IK 分词器"

# 一键部署
deploy:
	@echo "===== SSACPR 一键部署 ====="
	@test -f backend/.env || (echo "[!] backend/.env 不存在，请先复制 .env.example 到 backend/.env 并填写配置" && exit 1)
	@$(COMPOSE) up -d --build
	@echo "等待服务就绪..."
	@sleep 15
	@echo "检查数据库表..."
	@$(COMPOSE) exec -T postgres psql -U career_user -d career_planning -c "SELECT count(*) as table_count FROM information_schema.tables WHERE table_schema='public';"
	@echo "检查岗位数据..."
	@$(COMPOSE) exec -T postgres psql -U career_user -d career_planning -c "SELECT count(*) as job_count FROM jobs;"
	@echo "录入测试岗位数据（如不足）..."
	@docker cp scripts/seed_jobs.sql career-postgres:/tmp/seed_jobs.sql
	@docker exec career-postgres psql -U career_user -d career_planning -t -c "SELECT COUNT(*) FROM jobs WHERE source='seed_test';" 2>/dev/null | grep -q "^ *0$$" && \
		$(COMPOSE) exec -T postgres psql -U career_user -d career_planning -f /tmp/seed_jobs.sql || echo "测试数据已存在"
	@echo "===== 部署完成 ====="
	@echo "API 文档: http://localhost:8000/docs"
	@echo "前端:     http://localhost:5173"

# 安装依赖
install:
	@echo "安装 Python 依赖..."
	cd backend && pip install -r requirements.txt
	@echo "安装 Node.js 依赖..."
	cd frontend && npm install

# 启动开发环境
dev: up
	@echo "开发环境已启动"
	@echo "后端: http://localhost:8000"
	@echo "前端: http://localhost:5173"
	@echo "API 文档: http://localhost:8000/docs"
	@echo "OpenSearch Dashboards: http://localhost:5601"
	@echo "Nginx: http://localhost:80"

# 启动所有服务（跨平台兼容）
up:
	@echo ===== 启动 SSACPR 系统 =====
	@echo [1/3] 启动 Docker 服务...
	@$(COMPOSE) up -d --build
	@echo [2/3] 等待服务就绪...
	@sleep 15 2>nul || timeout /t 15 /nobreak >nul 2>&1 || exit 0
	@echo [3/3] 运行数据库迁移...
	@python scripts/migrate.py
	@bash scripts/load_questions.sh 2>nul || echo 面试题数据检查完成
	@echo 检查并导入日志测试数据...
	@docker cp scripts/seed_logs.sql career-postgres:/tmp/seed_logs.sql 2>nul || echo "跳过日志数据复制"
	@docker exec career-postgres psql -U career_user -d career_planning -f /tmp/seed_logs.sql 2>nul || echo "日志数据已存在"
	@echo ===== 启动完成 =====
	@echo
	@echo 访问地址:
	@echo   API 文档: http://localhost:8000/docs
	@echo   前端:     http://localhost:5173
	@echo   Nginx:    http://localhost:8080
	@echo
	@echo 提示: 数据库和测试数据会在首次启动时自动初始化

# 停止所有服务
down:
	$(COMPOSE) down

# 查看日志
logs:
	$(COMPOSE) logs -f

# 清理所有容器和数据数据
clean:
	$(COMPOSE) down -v
	@echo "已清理所有容器和数据卷"

# 运行测试
test:
	cd backend && pytest tests/ -v --cov=app --cov-report=html

# 代码检查
lint:
	cd backend && ruff check .
	cd backend && mypy app/

# 代码格式化
format:
	cd backend && ruff format .

# 初始化数据库（先启动基础设施，再用临时容器执行，不依赖 backend 运行）
init-db:
	$(COMPOSE) run --rm --entrypoint python backend scripts/init_db.py

# 填充测试数据
seed-data:
	$(COMPOSE) run --rm --entrypoint python backend scripts/seed_data.py

# 安装 OpenSearch IK 分词器（需要先手动下载插件包）
opensearch-ik:
	@echo "安装 IK 分词器..."
	@echo "请先下载插件包到当前目录："
	@echo "https://release.infinilabs.com/analysis-ik/stable/opensearch-analysis-ik-2.11.1.zip"
	@if not exist opensearch-analysis-ik-2.11.1.zip (echo 错误: 未找到 opensearch-analysis-ik-2.11.1.zip && exit 1)
	unzip -q opensearch-analysis-ik-2.11.1.zip -d analysis-ik-temp
	docker cp analysis-ik-temp/. career-opensearch:/usr/share/opensearch/plugins/analysis-ik/
	docker exec -u root career-opensearch sh -c "chown -R opensearch:opensearch /usr/share/opensearch/plugins/analysis-ik"
	rm -rf analysis-ik-temp
	@echo "重启 OpenSearch..."
	$(COMPOSE) restart opensearch
	@echo "IK 分词器安装完成"

# 备份数据库
backup:
	@mkdir -p backups
	$(COMPOSE) exec -T postgres pg_dump -U career_user career_planning > backups/postgres_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "数据库备份完成"

# 恢复数据库
restore:
	@read -p "输入备份文件名: " file; \
	$(COMPOSE) exec -T postgres psql -U career_user career_planning < backups/$$file
	@echo "数据库恢复完成"

# 进入后端容器
shell-backend:
	$(COMPOSE) exec backend bash

# 进入数据库
shell-db:
	$(COMPOSE) exec postgres psql -U career_user -d career_planning

# 进入 Redis
shell-redis:
	$(COMPOSE) exec redis redis-cli

# 查看服务状态
status:
	$(COMPOSE) ps

# 重启服务
restart:
	@echo "===== 重启 SSACPR 系统 ====="
	@echo "[1/4] 停止服务..."
	@$(COMPOSE) down
	@echo "[2/4] 重新构建并启动..."
	@$(COMPOSE) up -d --build
	@echo "[3/4] 等待服务就绪..."
	@sleep 15 2>nul || timeout /t 15 /nobreak >nul 2>&1 || exit 0
	@echo "[4/4] 运行数据库迁移..."
	@python scripts/migrate.py
	@bash scripts/load_questions.sh 2>nul || echo 面试题数据检查完成
	@echo 检查并导入日志测试数据...
	@docker cp scripts/seed_logs.sql career-postgres:/tmp/seed_logs.sql 2>nul || echo "跳过日志数据复制"
	@docker exec career-postgres psql -U career_user -d career_planning -f /tmp/seed_logs.sql 2>nul || echo "日志数据已存在"
	@echo "===== 重启完成 ====="

# 查看后端日志
logs-backend:
	$(COMPOSE) logs -f backend

# 查看 OpenSearch 日志
logs-opensearch:
	$(COMPOSE) logs -f opensearch
