"""
API v1 路由注册
"""
from fastapi import APIRouter

from .auth import router as auth_router
from .job import router as job_router
from .match import router as match_router
from .resume import router as resume_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth_router)
api_v1_router.include_router(resume_router)
api_v1_router.include_router(job_router)
api_v1_router.include_router(match_router)

__all__ = ["api_v1_router", "auth_router", "resume_router", "job_router", "match_router"]
