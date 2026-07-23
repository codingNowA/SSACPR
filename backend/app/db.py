"""
数据库连接与会话管理
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os

# 从环境变量读取数据库配置
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "career_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "career_password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "career_planning")

# 构建数据库连接 URL
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# 创建引擎，增大连接池以支持并发请求
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,          # 连接池大小从默认5增加到20
    max_overflow=40,       # 额外溢出连接从默认10增加到40
    pool_recycle=3600,     # 1小时后回收连接，防止连接过期
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """获取数据库会话（依赖注入用）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()