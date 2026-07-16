"""
API 路由初始化
"""
from fastapi import APIRouter
from app.api import job_difficulty, job_extraction, interview_questions, interactive_interview

# 创建主路由
api_router = APIRouter()

# 注册各个模块的路由
api_router.include_router(job_difficulty.router)
api_router.include_router(job_extraction.router)
api_router.include_router(interview_questions.router)
api_router.include_router(interactive_interview.router)

__all__ = ["api_router"]
