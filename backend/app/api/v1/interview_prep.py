"""
面试准备API
"""
from fastapi import APIRouter, HTTPException
from app.services.interview_prep_service import InterviewPrepService
from app.services.job_service import get_db_pool

router = APIRouter()


@router.get("/prepare")
async def prepare_interview(
    job_id: int,
    resume_id: int,
):
    """
    生成面试准备方案

    Args:
        job_id: 岗位ID
        resume_id: 简历ID

    Returns:
        面试准备方案
    """
    try:
        db_pool = await get_db_pool()
        service = InterviewPrepService(db_pool)
        result = await service.prepare_interview(job_id, resume_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成面试准备方案失败: {str(e)}")
