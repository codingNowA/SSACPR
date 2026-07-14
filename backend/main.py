"""
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import resume_router

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
    allow_origins=["http://localhost:5173", "http://localhost:80", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(resume_router, prefix="/api/v1")


@app.get("/")
async def root():
    """健康检查"""
    return {
        "status": "ok",
        "message": "职业规划智能体系统 API",
        "version": "0.1.0",
        "features": {
            "resume_parsing": "支持 PDF、Word、图片格式简历解析",
            "resume_upload": "支持简历上传和管理",
        }
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
