"""
API 路由初始化
"""
from fastapi import APIRouter
from app.api import job_difficulty, job_extraction, interview_questions

# 创建主路由
api_router = APIRouter()

# 注册各个模块的路由
api_router.include_router(job_difficulty.router)
api_router.include_router(job_extraction.router)
api_router.include_router(interview_questions.router)

__all__ = ["api_router"]
