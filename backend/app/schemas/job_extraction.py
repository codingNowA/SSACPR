"""
岗位信息提取数据模型
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class JobExtractionRequest(BaseModel):
    """岗位信息提取请求"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "job_text": """
                高级Java开发工程师
                岗位职责：
                1. 负责公司核心业务系统的开发和维护
                2. 参与系统架构设计和技术方案制定

                任职要求：
                - 本科及以上学历，计算机相关专业
                - 3-5年Java开发经验
                - 精通Spring Boot、微服务架构
                - 熟悉MySQL、Redis等数据库
                - 有大型互联网项目经验者优先

                薪资待遇：20k-35k
                工作地点：北京-朝阳区
                """
            }
        }
    )

    job_text: str = Field(description="岗位描述文本（可以是招聘广告、JD等非结构化文本）")


class ExtractedJobInfo(BaseModel):
    """提取的岗位信息"""
    # 基础信息
    job_title: Optional[str] = Field(default=None, description="岗位名称")
    education_requirement: Optional[str] = Field(default=None, description="学历要求")
    experience_requirement: Optional[str] = Field(default=None, description="工作经验要求")
    salary_range: Optional[str] = Field(default=None, description="薪资范围")
    location: Optional[str] = Field(default=None, description="工作地点")

    # 技能要求
    required_skills: List[str] = Field(default_factory=list, description="必备技能")
    preferred_skills: List[str] = Field(default_factory=list, description="优先技能")

    # 详细信息
    job_responsibilities: Optional[str] = Field(default=None, description="岗位职责")
    job_requirements: Optional[str] = Field(default=None, description="任职要求")
    company_benefits: Optional[str] = Field(default=None, description="福利待遇")

    # 附加信息
    industry: Optional[str] = Field(default=None, description="所属行业（主要行业）")
    industry_tags: List[str] = Field(default_factory=list, description="行业标签列表（支持多个，按层级排序）")
    company_type: Optional[str] = Field(default=None, description="公司类型")
    team_size: Optional[str] = Field(default=None, description="团队规模")
    work_mode: Optional[str] = Field(default=None, description="工作模式")


class JobExtractionResponse(BaseModel):
    """岗位信息提取响应"""
    success: bool = Field(description="是否提取成功")
    extracted_info: ExtractedJobInfo = Field(description="提取的岗位信息")
    confidence_score: float = Field(description="提取置信度 0-1", ge=0, le=1)
    extraction_notes: List[str] = Field(description="提取说明")
    missing_fields: List[str] = Field(description="未能提取的字段")
