"""
岗位数据管理 API 路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, Request
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.job_admin_service import JobAdminService
from app.services.log_service import LogService
from app.models.job import (
    JobCreate,
    JobUpdate,
    JobResponse,
    JobListResponse
)

router = APIRouter(prefix="/api/v1/admin/jobs", tags=["岗位管理"])


@router.post("", response_model=JobResponse, status_code=201)
def create_job(
    data: JobCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """1. 创建岗位"""
    service = JobAdminService(db)
    result = service.create_job(data)

    # 写日志
    log_service = LogService(db)
    log_service.create_log(
        user_id=1,
        action="CREATE",
        module="job",
        details={"job_id": result.id, "title": result.title},
        ip_address=request.client.host if request.client else None
    )

    return result


@router.get("", response_model=JobListResponse)
def get_jobs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    title: Optional[str] = Query(None, description="岗位标题（模糊搜索）"),
    company: Optional[str] = Query(None, description="公司名称（模糊搜索）"),
    industry: Optional[str] = Query(None, description="行业"),
    location: Optional[str] = Query(None, description="工作地点"),
    status: Optional[str] = Query(None, description="状态: active/inactive/expired"),
    keyword: Optional[str] = Query(None, description="关键词搜索（标题/公司/描述）"),
    db: Session = Depends(get_db)
):
    """2. 获取岗位列表（分页 + 筛选）"""
    service = JobAdminService(db)
    return service.get_jobs(page, page_size, title, company, industry, location, status, keyword)


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """3. 获取单个岗位详情"""
    service = JobAdminService(db)
    result = service.get_job_by_id(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="岗位不存在")
    return result


@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    data: JobUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """4. 更新岗位"""
    service = JobAdminService(db)
    result = service.update_job(job_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="岗位不存在")

    # 写日志
    log_service = LogService(db)
    log_service.create_log(
        user_id=1,
        action="UPDATE",
        module="job",
        details={"job_id": result.id, "title": result.title},
        ip_address=request.client.host if request.client else None
    )

    return result


@router.delete("/{job_id}", status_code=204)
def delete_job(
    job_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """5. 删除岗位"""
    # 先获取要删除的岗位信息（用于日志）
    job_service = JobAdminService(db)
    job = job_service.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")

    # 执行删除
    deleted = job_service.delete_job(job_id)

    # 写日志
    log_service = LogService(db)
    log_service.create_log(
        user_id=1,
        action="DELETE",
        module="job",
        details={"job_id": job_id, "title": job.title},
        ip_address=request.client.host if request.client else None
    )

    return None