"""
API v1 路由注册
"""
from fastapi import APIRouter

from app.api.v1.job import router as job_router
from app.api.v1.match import router as match_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(job_router)
api_v1_router.include_router(match_router)
