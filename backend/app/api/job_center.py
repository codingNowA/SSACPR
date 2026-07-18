"""
岗位中心 API 路由
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.job_difficulty_service import job_difficulty_service

router = APIRouter(prefix="/api/v1/jobs", tags=["岗位中心"])


class DifficultyInfo(BaseModel):
    """岗位难度信息"""
    level: str
    score: float
    dimensions: dict


class JobCenterItem(BaseModel):
    """岗位中心列表项"""
    id: int
    title: str
    company: str
    location: Optional[str] = None
    salary_range: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    difficulty: DifficultyInfo


class JobCenterResponse(BaseModel):
    """岗位中心响应"""
    items: list[JobCenterItem]
    total: int
    page: int
    page_size: int


@router.get("/center", response_model=JobCenterResponse)
async def get_jobs_center(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    sort_by: str = Query("created_at", description="排序字段"),
    order: str = Query("desc", description="排序方向"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    location: Optional[str] = Query(None, description="地点筛选"),
    salary_min: Optional[int] = Query(None, description="最低薪资"),
    salary_max: Optional[int] = Query(None, description="最高薪资"),
):
    """
    获取岗位中心列表（带难度评估和排序）

    支持按难度排序、关键词搜索、地点筛选等
    """
    try:
        result = await job_difficulty_service.get_jobs_with_difficulty(
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            order=order,
            keyword=keyword,
            location=location,
            salary_min=salary_min,
            salary_max=salary_max,
        )

        return JobCenterResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取岗位列表失败: {str(e)}"
        )


@router.get("/{job_id}/difficulty", response_model=DifficultyInfo)
async def get_job_difficulty(job_id: int):
    """
    获取单个岗位的难度评估
    """
    try:
        difficulty = await job_difficulty_service.calculate_job_difficulty(job_id)
        if not difficulty:
            raise HTTPException(status_code=404, detail="岗位不存在")
        return DifficultyInfo(**difficulty)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取岗位难度失败: {str(e)}"
        )
