"""
简历相关的 Pydantic 数据模型
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ResumeUploadResponse(BaseModel):
    """简历上传响应"""
    resume_id: Optional[int] = Field(None, description="简历ID（如果保存到数据库）")
    file_path: str = Field(..., description="文件路径")
    file_type: str = Field(..., description="文件类型")
    message: str = Field(..., description="响应消息")


class ResumeParseResponse(BaseModel):
    """简历解析响应"""
    text: str = Field(..., description="提取的文本内容")
    file_type: str = Field(..., description="文件类型")
    file_path: str = Field(..., description="文件路径")
    page_count: Optional[int] = Field(None, description="页数（仅PDF）")
    word_count: int = Field(..., description="总字数")
    char_count: int = Field(..., description="字符数（不含空格和换行）")
    message: str = Field(default="解析成功", description="响应消息")


class ResumeParseRequest(BaseModel):
    """简历解析请求"""
    file_path: str = Field(..., description="文件路径")
    file_type: Optional[str] = Field(None, description="文件类型（可选，自动推断）")


class ResumeStructuredData(BaseModel):
    """简历结构化数据"""
    basic_info: Dict[str, Any] = Field(default_factory=dict, description="基本信息")
    education: list = Field(default_factory=list, description="教育经历")
    work_experience: list = Field(default_factory=list, description="工作经历")
    project_experience: list = Field(default_factory=list, description="项目经验")
    skills: list = Field(default_factory=list, description="技能列表")
    certifications: list = Field(default_factory=list, description="证书")
    honors: list = Field(default_factory=list, description="荣誉奖项")
    self_evaluation: Optional[str] = Field(None, description="自我评价")


class ResumeDiagnosisResponse(BaseModel):
    """简历诊断响应"""
    resume_id: int = Field(..., description="简历ID")
    parsed_data: ResumeStructuredData = Field(..., description="结构化数据")
    scores: Dict[str, float] = Field(..., description="各维度评分")
    overall_score: float = Field(..., description="总体评分")
    suggestions: list = Field(..., description="优化建议")
    message: str = Field(default="诊断完成", description="响应消息")


class ResumeListItem(BaseModel):
    """简历列表项"""
    id: int = Field(..., description="简历ID")
    file_name: str = Field(..., description="文件名")
    file_type: str = Field(..., description="文件类型")
    status: str = Field(..., description="状态")
    version: int = Field(default=1, description="版本号")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class ResumeListResponse(BaseModel):
    """简历列表响应"""
    total: int = Field(..., description="总数")
    items: list[ResumeListItem] = Field(..., description="简历列表")
    page: int = Field(default=1, description="当前页")
    page_size: int = Field(default=10, description="每页数量")
