"""
数据库初始化脚本

两种使用方式：
1. Docker 首次启动时，init_db.sql 会通过 /docker-entrypoint-initdb.d/ 自动执行
2. 手动运行：python scripts/init_db.py（可在本地或容器内执行）

本脚本会：
- 连接 PostgreSQL
- 执行 init_db.sql 中的建表语句
- 创建 OpenSearch 索引
- 插入默认管理员账户
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import asyncpg


# ============================================================
# 配置
# ============================================================

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DB_USER = os.getenv("POSTGRES_USER", "career_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
DB_NAME = os.getenv("POSTGRES_DB", "career_planning")

OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "localhost")
OPENSEARCH_PORT = int(os.getenv("OPENSEARCH_PORT", "9200"))
OPENSEARCH_USER = os.getenv("OPENSEARCH_USER", "admin")
OPENSEARCH_PASSWORD = os.getenv("OPENSEARCH_PASSWORD", "admin")


# ============================================================
# SQL 建表语句（与 init_db.sql 保持同步，新增 company_type 字段）
# ============================================================

SCHEMA_SQL = """
-- 启用 UUID 扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    role VARCHAR(20) NOT NULL CHECK (role IN ('student', 'teacher', 'admin')),
    real_name VARCHAR(50),
    school VARCHAR(100),
    major VARCHAR(100),
    grade VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- 简历表
CREATE TABLE IF NOT EXISTS resumes (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    file_path VARCHAR(500),
    file_type VARCHAR(20),
    version INT DEFAULT 1,
    status VARCHAR(20) CHECK (status IN ('draft', 'active', 'archived')),
    parsed_data JSONB,
    diagnosis_result JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON resumes(user_id);
CREATE INDEX IF NOT EXISTS idx_resumes_status ON resumes(status);
CREATE INDEX IF NOT EXISTS idx_resumes_created_at ON resumes(created_at DESC);

-- 岗位表（新增 company_type 字段）
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    company VARCHAR(200),
    industry VARCHAR(100),
    location VARCHAR(100),
    salary_range VARCHAR(50),
    experience_required VARCHAR(50),
    education_required VARCHAR(50),
    description TEXT,
    requirements TEXT,
    job_profile JSONB,
    company_type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'expired')),
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_jobs_title ON jobs(title);
CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);
CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at DESC);

-- 匹配记录表
CREATE TABLE IF NOT EXISTS matches (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    resume_id INT REFERENCES resumes(id) ON DELETE CASCADE,
    job_id INT REFERENCES jobs(id) ON DELETE CASCADE,
    match_score DECIMAL(5,2),
    matched_skills JSONB,
    missing_skills JSONB,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_matches_user_id ON matches(user_id);
CREATE INDEX IF NOT EXISTS idx_matches_resume_id ON matches(resume_id);
CREATE INDEX IF NOT EXISTS idx_matches_job_id ON matches(job_id);
CREATE INDEX IF NOT EXISTS idx_matches_score ON matches(match_score DESC);
CREATE INDEX IF NOT EXISTS idx_matches_created_at ON matches(created_at DESC);

-- 面试题表
CREATE TABLE IF NOT EXISTS interview_questions (
    id SERIAL PRIMARY KEY,
    category VARCHAR(100),
    difficulty VARCHAR(20) CHECK (difficulty IN ('easy', 'medium', 'hard')),
    question TEXT NOT NULL,
    answer_points TEXT,
    related_skills JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_questions_category ON interview_questions(category);
CREATE INDEX IF NOT EXISTS idx_questions_difficulty ON interview_questions(difficulty);

-- 收藏表
CREATE TABLE IF NOT EXISTS collections (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    job_id INT REFERENCES jobs(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, job_id)
);

CREATE INDEX IF NOT EXISTS idx_collections_user_id ON collections(user_id);
CREATE INDEX IF NOT EXISTS idx_collections_job_id ON collections(job_id);

-- 投递记录表
CREATE TABLE IF NOT EXISTS applications (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    job_id INT REFERENCES jobs(id) ON DELETE CASCADE,
    resume_id INT REFERENCES resumes(id) ON DELETE SET NULL,
    status VARCHAR(20) CHECK (status IN ('pending', 'interview', 'offer', 'rejected')),
    apply_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_applications_user_id ON applications(user_id);
CREATE INDEX IF NOT EXISTS idx_applications_job_id ON applications(job_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_apply_date ON applications(apply_date DESC);

-- 系统日志表
CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    user_id INT,
    action VARCHAR(100),
    module VARCHAR(50),
    details JSONB,
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_logs_user_id ON logs(user_id);
CREATE INDEX IF NOT EXISTS idx_logs_action ON logs(action);
CREATE INDEX IF NOT EXISTS idx_logs_module ON logs(module);
CREATE INDEX IF NOT EXISTS idx_logs_created_at ON logs(created_at DESC);

-- 更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_resumes_updated_at ON resumes;
CREATE TRIGGER update_resumes_updated_at BEFORE UPDATE ON resumes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_jobs_updated_at ON jobs;
CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_applications_updated_at ON applications;
CREATE TRIGGER update_applications_updated_at BEFORE UPDATE ON applications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 默认管理员（密码: admin123）
INSERT INTO users (username, password_hash, email, role, real_name)
VALUES ('admin', '$2b$12$OVvtXqjuGv5iuvYEQrkekOHvEdGsdlS00dLFgpa.im/tRASHANVq2', 'admin@example.com', 'admin', '系统管理员')
ON CONFLICT (username) DO NOTHING;

-- 测试用户（密码: user123）
INSERT INTO users (username, password_hash, email, role, real_name)
VALUES ('testuser', '$2b$12$iozgovWmsUYB6S9L.ccDGeRkOXc7wGNIzDT7P1QjE/C84PMy59m6W', 'user@example.com', 'student', '测试用户')
ON CONFLICT (username) DO NOTHING;
"""


# ============================================================
# 为已有表添加新字段的迁移语句（幂等）
# ============================================================

MIGRATION_SQL = """
-- 为 jobs 表添加 company_type 字段（如果不存在）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'jobs' AND column_name = 'company_type'
    ) THEN
        ALTER TABLE jobs ADD COLUMN company_type VARCHAR(50);
    END IF;
END $$;
"""


# ============================================================
# OpenSearch 索引初始化
# ============================================================

async def init_opensearch() -> None:
    """初始化 OpenSearch 索引"""
    try:
        from opensearchpy import OpenSearch

        client = OpenSearch(
            hosts=[{"host": OPENSEARCH_HOST, "port": OPENSEARCH_PORT}],
            http_auth=(OPENSEARCH_USER, OPENSEARCH_PASSWORD),
            use_ssl=False,
            scheme="http",
            timeout=30,
        )

        if not client.ping():
            print(f"[WARN] 无法连接 OpenSearch ({OPENSEARCH_HOST}:{OPENSEARCH_PORT})，跳过索引初始化")
            return

        # 岗位索引
        job_mappings = {
            "properties": {
                "id": {"type": "integer"},
                "title": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
                "company": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
                "industry": {"type": "keyword"},
                "location": {"type": "keyword"},
                "salary_range": {"type": "keyword"},
                "experience_required": {"type": "keyword"},
                "education_required": {"type": "keyword"},
                "description": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
                "requirements": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
                "skills": {"type": "keyword"},
                "company_type": {"type": "keyword"},
                "status": {"type": "keyword"},
                "source": {"type": "keyword"},
            }
        }

        index_name = "jobs"
        if not client.indices.exists(index=index_name):
            client.indices.create(index=index_name, body={"mappings": job_mappings})
            print(f"[OK] OpenSearch 索引 '{index_name}' 创建成功")
        else:
            print(f"[OK] OpenSearch 索引 '{index_name}' 已存在")

        print("[OK] OpenSearch 初始化完成")

    except ImportError:
        print("[WARN] opensearch-py 未安装，跳过 OpenSearch 初始化")
    except Exception as e:
        print(f"[WARN] OpenSearch 初始化失败: {e}，可稍后手动初始化")


# ============================================================
# 主流程
# ============================================================

async def init_database() -> None:
    """初始化 PostgreSQL 数据库"""
    print(f"正在连接 PostgreSQL ({DB_HOST}:{DB_PORT}/{DB_NAME})...")

    try:
        conn = await asyncpg.connect(
            host=DB_HOST, port=DB_PORT,
            user=DB_USER, password=DB_PASSWORD,
            database=DB_NAME,
        )
    except Exception as e:
        print(f"[ERROR] 无法连接 PostgreSQL: {e}")
        print("请确认：")
        print("  1. PostgreSQL 服务已启动 (docker-compose up -d postgres)")
        print("  2. 连接参数正确 (.env 文件中的 POSTGRES_* 配置)")
        sys.exit(1)

    try:
        # 执行建表
        print("正在创建数据库表...")
        await conn.execute(SCHEMA_SQL)
        print("[OK] 数据库表创建完成")

        # 执行迁移（幂等）
        print("正在检查数据迁移...")
        await conn.execute(MIGRATION_SQL)
        print("[OK] 数据迁移完成")

        # 验证
        tables = await conn.fetch(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"
        )
        table_names = [t["tablename"] for t in tables]
        print(f"[OK] 当前数据表: {', '.join(table_names)}")

    finally:
        await conn.close()


async def main() -> None:
    """主入口"""
    print("=" * 60)
    print("  智慧学工职业规划推荐智能体 - 数据库初始化")
    print("=" * 60)
    print()

    # 1. 初始化 PostgreSQL
    await init_database()
    print()

    # 2. 初始化 OpenSearch
    await init_opensearch()
    print()

    print("=" * 60)
    print("  初始化完成！")
    print("  测试账号:")
    print("    管理员: username=admin, password=admin123")
    print("    学生: username=testuser, password=user123")
    print("  请在生产环境中修改默认密码")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
