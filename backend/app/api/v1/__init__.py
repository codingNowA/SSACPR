"""
API v1 路由注册
"""
from fastapi import APIRouter

from .auth import router as auth_router
from .job import router as job_router
from .job_center import router as job_center_router
from .match import router as match_router
from .resume import router as resume_router
from .resume_crud import router as resume_crud_router
from .versions import router as versions_router
from .job_analysis import router as job_analysis_router
from .interview_prep import router as interview_prep_router
from .interview_mock import router as interview_mock_router
from .interview_questions import router as interview_questions_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth_router)
api_v1_router.include_router(resume_router)
api_v1_router.include_router(resume_crud_router)
api_v1_router.include_router(job_router)
api_v1_router.include_router(job_center_router)
api_v1_router.include_router(match_router)
api_v1_router.include_router(versions_router)
api_v1_router.include_router(job_analysis_router)
api_v1_router.include_router(interview_prep_router, prefix="/interview-prep", tags=["interview-prep"])
api_v1_router.include_router(interview_mock_router)
api_v1_router.include_router(interview_questions_router)

__all__ = ["api_v1_router", "auth_router", "resume_router", "resume_crud_router", "job_router", "job_center_router", "match_router", "versions_router", "job_analysis_router", "interview_prep_router", "interview_questions_router"]
