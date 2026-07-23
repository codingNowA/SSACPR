"""
岗位数据管理数据模型
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


# ==================== 请求模型 ====================
class JobCreate(BaseModel):
    """创建岗位请求"""
    title: str
    company: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    experience_required: Optional[str] = None
    education_required: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    job_profile: Optional[dict] = None  # JSONB
    status: Optional[str] = "active"
    source: Optional[str] = None


class JobUpdate(BaseModel):
    """更新岗位请求（全部可选）"""
    title: Optional[str] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    experience_required: Optional[str] = None
    education_required: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    job_profile: Optional[dict] = None
    status: Optional[str] = None
    source: Optional[str] = None


# ==================== 响应模型 ====================
class JobResponse(BaseModel):
    """岗位响应"""
    id: int
    title: str
    company: Optional[str]
    industry: Optional[str]
    location: Optional[str]
    salary_range: Optional[str]
    experience_required: Optional[str]
    education_required: Optional[str]
    description: Optional[str]
    requirements: Optional[str]
    job_profile: Optional[dict]
    status: str
    source: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    """岗位列表响应"""
    items: List[JobResponse]
    total: int
    page: int
    page_size: int
    total_pages: int