"""
岗位匹配相关的 Pydantic 数据模型
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ============================================================
# 枚举
# ============================================================

class MatchCategory(str, Enum):
    """匹配分层"""
    highly_matched = "highly_matched"              # 高度匹配 >= 80
    fairly_matched = "fairly_matched"              # 较为匹配 60-79
    development_direction = "development_direction"  # 发展方向 < 60


class JobStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    expired = "expired"


# ============================================================
# 用户偏好
# ============================================================

class MatchPreferences(BaseModel):
    """用户筛选偏好"""
    industries: Optional[List[str]] = Field(
        default=None, description="目标行业列表，如 ['互联网', '金融']"
    )
    cities: Optional[List[str]] = Field(
        default=None, description="目标城市列表，如 ['北京', '上海']"
    )
    salary_min: Optional[int] = Field(
        default=None, description="最低月薪（K），如 10 表示 10K"
    )
    salary_max: Optional[int] = Field(
        default=None, description="最高月薪（K），如 30 表示 30K"
    )
    company_types: Optional[List[str]] = Field(
        default=None, description="公司性质，如 ['国企', '外企', '民营']"
    )
    experience: Optional[str] = Field(
        default=None, description="经验要求，如 '应届', '1-3年'"
    )
    education: Optional[str] = Field(
        default=None, description="学历要求，如 '本科', '硕士'"
    )


# ============================================================
# 简历画像（从 resumes.parsed_data 中提取）
# ============================================================

class EducationItem(BaseModel):
    school: Optional[str] = None
    major: Optional[str] = None
    degree: Optional[str] = None       # 本科/硕士/博士
    gpa: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class ExperienceItem(BaseModel):
    company: Optional[str] = None
    position: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class ProjectItem(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    description: Optional[str] = None
    technologies: Optional[List[str]] = None


class ResumeProfile(BaseModel):
    """简历画像——匹配算法的核心输入"""
    name: Optional[str] = None
    skills: List[str] = Field(default_factory=list, description="技能标签列表")
    education: List[EducationItem] = Field(default_factory=list)
    experience: List[ExperienceItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    summary: Optional[str] = Field(default=None, description="简历摘要/自我评价")
    target_position: Optional[str] = None
    target_industry: Optional[str] = None


# ============================================================
# 岗位相关
# ============================================================

class JobCreate(BaseModel):
    """创建岗位"""
    title: str = Field(..., description="岗位名称")
    company: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = Field(
        default=None, description="薪资范围，如 '15K-25K' 或 '8K-12K'"
    )
    experience_required: Optional[str] = None
    education_required: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    skills: Optional[List[str]] = Field(default=None, description="岗位要求技能列表")
    company_type: Optional[str] = Field(
        default=None, description="公司性质，如 '国企', '外企', '民营'"
    )
    source: Optional[str] = None
    job_profile: Optional[Dict[str, Any]] = Field(default=None, description='岗位画像 JSON')


class JobResponse(BaseModel):
    """岗位详情响应"""
    id: int
    title: str
    company: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    experience_required: Optional[str] = None
    education_required: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    skills: Optional[List[str]] = None
    company_type: Optional[str] = None
    status: str = "active"
    source: Optional[str] = None
    created_at: Optional[datetime] = None
    job_profile: Optional[Dict[str, Any]] = None
    updated_at: Optional[datetime] = None


class JobListResponse(BaseModel):
    '''岗位列表响应'''
    total: int
    items: List[JobResponse]
    page: int = 1
    page_size: int = 20
    total_pages: int = 0


class JobUpdate(BaseModel):
    '''更新岗位（所有字段可选）'''
    title: Optional[str] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    experience_required: Optional[str] = None
    education_required: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    skills: Optional[List[str]] = None
    company_type: Optional[str] = None
    job_profile: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    source: Optional[str] = None

# ============================================================
# 匹配相关
# ============================================================

class JobMatchRequest(BaseModel):
    """岗位匹配请求"""
    resume_id: int = Field(..., description="简历 ID")
    preferences: Optional[MatchPreferences] = Field(default=None, description="筛选偏好")
    top_k: int = Field(default=20, ge=1, le=100, description="返回结果数量上限")


class JobMatchResult(BaseModel):
    """单个岗位的匹配结果"""
    job_id: int
    job_title: str
    company: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    match_score: float = Field(..., ge=0, le=100, description="匹配度分数 0-100")
    matched_skills: List[str] = Field(default_factory=list, description="命中技能")
    missing_skills: List[str] = Field(default_factory=list, description="缺失技能")
    match_reason: str = Field(default="", description="推荐理由")
    category: MatchCategory = Field(..., description="匹配分层")


class JobMatchResponse(BaseModel):
    """岗位匹配响应——按分层返回"""
    resume_id: int
    total: int = 0
    highly_matched: List[JobMatchResult] = Field(
        default_factory=list, description="高度匹配（>=80分）"
    )
    fairly_matched: List[JobMatchResult] = Field(
        default_factory=list, description="较为匹配（60-79分）"
    )
    development_direction: List[JobMatchResult] = Field(
        default_factory=list, description="发展方向（<60分）"
    )


class MatchHistoryItem(BaseModel):
    """匹配历史记录"""
    id: int
    resume_id: int
    job_id: int
    job_title: Optional[str] = None
    company: Optional[str] = None
    match_score: float
    matched_skills: Optional[List[str]] = None
    missing_skills: Optional[List[str]] = None
    reason: Optional[str] = None
    created_at: Optional[datetime] = None


class MatchHistoryResponse(BaseModel):
    """匹配历史响应"""
    total: int
    items: List[MatchHistoryItem]
