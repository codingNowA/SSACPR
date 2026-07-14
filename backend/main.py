"""
FastAPI 应用入口
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_v1_router
from app.services.job_service import get_db_pool, close_db_pool
from app.utils.opensearch import get_opensearch_client

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化资源，关闭时释放资源"""
    # 启动：初始化 DB 连接池
    try:
        pool = await get_db_pool()
        logger.info("DB 连接池已初始化")
    except Exception as e:
        logger.warning(f"DB 连接池初始化失败（后续按需重试）: {e}")

    # 启动：初始化 OpenSearch
    try:
        os_client = get_opensearch_client()
        if os_client:
            logger.info("OpenSearch 客户端已初始化")
    except Exception as e:
        logger.warning(f"OpenSearch 初始化失败（后续按需重试）: {e}")

    yield

    # 关闭：释放 DB 连接池
    try:
        await close_db_pool()
        logger.info("DB 连接池已关闭")
    except Exception as e:
        logger.warning(f"DB 连接池关闭失败: {e}")


app = FastAPI(
    title="职业规划智能体系统",
    description="基于 LLM 的职业规划智能助手 API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:80", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_v1_router)


@app.get("/")
async def root():
    """根路径"""
    return {
        "status": "ok",
        "message": "职业规划智能体系统 API",
        "version": "0.1.0",
        "features": {
            "resume_parsing": "支持 PDF、Word、图片格式简历解析",
            "resume_upload": "支持简历上传和管理",
            "job_matching": "支持岗位精准匹配",
        }
    }


@app.get("/health")
async def health_check():
    """详细健康检查"""
    services = {"api": "running"}

    # 检查数据库
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        services["database"] = "healthy"
    except Exception:
        services["database"] = "unavailable"

    # 检查 Redis
    try:
        import redis.asyncio as aioredis
        redis_host = __import__("os").getenv("REDIS_HOST", "localhost")
        redis_port = int(__import__("os").getenv("REDIS_PORT", "6379"))
        r = aioredis.Redis(host=redis_host, port=redis_port)
        await r.ping()
        await r.aclose()
        services["redis"] = "healthy"
    except Exception:
        services["redis"] = "unavailable"

    # 检查 OpenSearch
    try:
        os_client = get_opensearch_client()
        if os_client and os_client.ping():
            services["opensearch"] = "healthy"
        else:
            services["opensearch"] = "unavailable"
    except Exception:
        services["opensearch"] = "unavailable"

    all_healthy = all(v == "healthy" or v == "running" for v in services.values())
    return {
        "status": "healthy" if all_healthy else "degraded",
        "services": services,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
