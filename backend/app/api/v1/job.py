"""
岗位相关 API 路由
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import get_current_user
from app.schemas.common import ApiResponse
from app.schemas.job import JobCreate, JobListResponse, JobResponse, JobUpdate
from app.services.job_service import job_service

router = APIRouter(prefix="/job", tags=["岗位管理"])


@router.get("/list", summary="获取岗位列表")
async def list_jobs(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(default=None, description="岗位状态"),
    industry: Optional[str] = Query(default=None, description="行业"),
    location: Optional[str] = Query(default=None, description="城市"),
    title: Optional[str] = Query(default=None, description="岗位名称模糊搜索"),
    company: Optional[str] = Query(default=None, description="公司名称模糊搜索"),
    keyword: Optional[str] = Query(default=None, description="关键词搜索(标题/公司/描述)"),
    _user: dict = Depends(get_current_user),
) -> ApiResponse[JobListResponse]:
    """获取岗位列表，支持分页和多维筛选"""
    try:
        result = await job_service.list_jobs(
            page=page, page_size=page_size, status=status,
            industry=industry, location=location,
            title=title, company=company, keyword=keyword,
        )
        return ApiResponse.success(data=result)
    except Exception as e:
        return ApiResponse.error(message=f"获取岗位列表失败: {e}")


@router.get("/{job_id}", summary="获取岗位详情")
async def get_job(
    job_id: int,
    _user: dict = Depends(get_current_user),
) -> ApiResponse[JobResponse]:
    """根据 ID 获取岗位详情"""
    result = await job_service.get_job(job_id)
    if result is None:
        raise HTTPException(status_code=404, detail="岗位不存在")
    return ApiResponse.success(data=result)


@router.post("/create", summary="创建岗位")
async def create_job(
    data: JobCreate,
    _user: dict = Depends(get_current_user),
) -> ApiResponse[JobResponse]:
    """创建新岗位"""
    try:
        result = await job_service.create_job(data)
        return ApiResponse.success(data=result, message="岗位创建成功")
    except Exception as e:
        return ApiResponse.error(message=f"创建岗位失败: {e}")


@router.put("/{job_id}", summary="更新岗位")
async def update_job(
    job_id: int,
    data: JobUpdate,
    _user: dict = Depends(get_current_user),
) -> ApiResponse[JobResponse]:
    """更新岗位信息"""
    try:
        result = await job_service.update_job(job_id, data)
        if result is None:
            raise HTTPException(status_code=404, detail="岗位不存在")
        return ApiResponse.success(data=result, message="岗位更新成功")
    except Exception as e:
        return ApiResponse.error(message=f"更新岗位失败: {e}")


@router.delete("/{job_id}", summary="删除岗位")
async def delete_job(
    job_id: int,
    _user: dict = Depends(get_current_user),
) -> ApiResponse[None]:
    """删除岗位"""
    success = await job_service.delete_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="岗位不存在")
    return ApiResponse.success(message="岗位删除成功")


@router.post("/init-index", summary="初始化岗位索引")
async def init_job_index(
    _user: dict = Depends(get_current_user),
) -> ApiResponse[None]:
    """初始化 OpenSearch 岗位索引"""
    success = job_service.init_job_index()
    if success:
        return ApiResponse.success(message="岗位索引初始化成功")
    return ApiResponse.error(message="岗位索引初始化失败")