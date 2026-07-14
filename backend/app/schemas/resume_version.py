"""
简历版本管理数据模型
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ResumeVersion(BaseModel):
    """简历版本"""
    id: Optional[int] = Field(None, description="版本ID")
    user_id: Optional[int] = Field(None, description="用户ID")
    version: int = Field(..., description="版本号")
    title: str = Field(..., description="版本标题")
    description: Optional[str] = Field(None, description="版本描述")
    file_path: str = Field(..., description="文件路径")
    file_type: str = Field(..., description="文件类型")
    parsed_text: Optional[str] = Field(None, description="解析后的文本")
    structured_data: Optional[Dict[str, Any]] = Field(None, description="结构化数据")
    score_data: Optional[Dict[str, Any]] = Field(None, description="评分数据")
    optimization_data: Optional[Dict[str, Any]] = Field(None, description="优化建议数据")
    target_job: Optional[str] = Field(None, description="目标岗位")
    is_active: bool = Field(default=True, description="是否为当前激活版本")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class ResumeVersionCreate(BaseModel):
    """创建简历版本"""
    title: str = Field(..., description="版本标题", max_length=200)
    description: Optional[str] = Field(None, description="版本描述", max_length=500)
    target_job: Optional[str] = Field(None, description="目标岗位", max_length=100)
    set_as_active: bool = Field(default=False, description="是否设为当前激活版本")


class ResumeVersionUpdate(BaseModel):
    """更新简历版本"""
    title: Optional[str] = Field(None, description="版本标题", max_length=200)
    description: Optional[str] = Field(None, description="版本描述", max_length=500)
    target_job: Optional[str] = Field(None, description="目标岗位", max_length=100)
    is_active: Optional[bool] = Field(None, description="是否为当前激活版本")


class ResumeVersionListItem(BaseModel):
    """简历版本列表项"""
    id: int = Field(..., description="版本ID")
    version: int = Field(..., description="版本号")
    title: str = Field(..., description="版本标题")
    description: Optional[str] = Field(None, description="版本描述")
    target_job: Optional[str] = Field(None, description="目标岗位")
    is_active: bool = Field(..., description="是否为当前激活版本")
    total_score: Optional[float] = Field(None, description="总分")
    created_at: datetime = Field(..., description="创建时间")


class ResumeVersionDetail(BaseModel):
    """简历版本详情"""
    id: int = Field(..., description="版本ID")
    version: int = Field(..., description="版本号")
    title: str = Field(..., description="版本标题")
    description: Optional[str] = Field(None, description="版本描述")
    file_path: str = Field(..., description="文件路径")
    file_type: str = Field(..., description="文件类型")
    target_job: Optional[str] = Field(None, description="目标岗位")
    is_active: bool = Field(..., description="是否为当前激活版本")
    parsed_text: Optional[str] = Field(None, description="解析后的文本")
    structured_data: Optional[Dict[str, Any]] = Field(None, description="结构化数据")
    score_data: Optional[Dict[str, Any]] = Field(None, description="评分数据")
    optimization_data: Optional[Dict[str, Any]] = Field(None, description="优化建议数据")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class ResumeVersionCompare(BaseModel):
    """简历版本对比"""
    version1: ResumeVersionDetail = Field(..., description="版本1")
    version2: ResumeVersionDetail = Field(..., description="版本2")
    differences: Dict[str, Any] = Field(..., description="差异分析")


class ResumeVersionStats(BaseModel):
    """简历版本统计"""
    total_versions: int = Field(..., description="总版本数")
    active_version: Optional[ResumeVersionListItem] = Field(None, description="当前激活版本")
    latest_version: Optional[ResumeVersionListItem] = Field(None, description="最新版本")
    score_trend: List[Dict[str, Any]] = Field(default_factory=list, description="评分趋势")


class ResumeVersionResponse(BaseModel):
    """简历版本响应"""
    version: ResumeVersion = Field(..., description="版本数据")
    message: str = Field(default="操作成功", description="响应消息")


class ResumeVersionListResponse(BaseModel):
    """简历版本列表响应"""
    versions: List[ResumeVersionListItem] = Field(..., description="版本列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")
    page_size: int = Field(..., description="每页大小")
    message: str = Field(default="查询成功", description="响应消息")
