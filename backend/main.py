"""
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import analytics
from app.api import questions
from app.api import jobs
from app.api import logs
from app.api import dictionary

app = FastAPI(
    title="职业规划智能体系统",
    description="基于 LLM 的职业规划智能助手 API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== 注册路由 ==========
app.include_router(analytics.router)  # ← 这一行是新加的
app.include_router(questions.router)
app.include_router(jobs.router)
app.include_router(logs.router)
app.include_router(dictionary.router)


@app.get("/")
async def root():
    """健康检查"""
    return {
        "status": "ok",
        "message": "职业规划智能体系统 API",
        "version": "0.1.0"
    }


@app.get("/health")
async def health_check():
    """详细健康检查"""
    return {
        "status": "healthy",
        "services": {
            "api": "running",
            "database": "pending",
            "redis": "pending",
            "opensearch": "pending"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)