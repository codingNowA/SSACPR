"""
简历评分数据模型
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ScoreDimension(BaseModel):
    """评分维度"""
    name: str = Field(..., description="维度名称")
    score: float = Field(..., description="得分 (0-100)")
    max_score: float = Field(default=100.0, description="满分")
    weight: float = Field(..., description="权重 (0-1)")
    feedback: Optional[str] = Field(None, description="反馈建议")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")


class CompletenessScore(BaseModel):
    """完整性评分"""
    total_score: float = Field(..., description="总分 (0-100)")
    has_basic_info: bool = Field(..., description="是否有基本信息")
    has_education: bool = Field(..., description="是否有教育经历")
    has_work_experience: bool = Field(..., description="是否有工作经历")
    has_project_experience: bool = Field(..., description="是否有项目经验")
    has_skills: bool = Field(..., description="是否有技能标签")
    missing_fields: List[str] = Field(default_factory=list, description="缺失字段")
    feedback: str = Field(..., description="反馈建议")


class ProfessionalismScore(BaseModel):
    """专业性评分"""
    total_score: float = Field(..., description="总分 (0-100)")
    language_quality: float = Field(..., description="语言质量得分")
    format_consistency: float = Field(..., description="格式一致性得分")
    detail_richness: float = Field(..., description="细节丰富度得分")
    feedback: str = Field(..., description="反馈建议")


class QuantificationScore(BaseModel):
    """量化程度评分"""
    total_score: float = Field(..., description="总分 (0-100)")
    quantified_achievements: int = Field(..., description="量化成果数量")
    total_achievements: int = Field(..., description="总成果数量")
    quantification_rate: float = Field(..., description="量化率 (0-1)")
    examples: List[str] = Field(default_factory=list, description="量化示例")
    feedback: str = Field(..., description="反馈建议")


class ProjectDepthScore(BaseModel):
    """项目深度评分"""
    total_score: float = Field(..., description="总分 (0-100)")
    project_count: int = Field(..., description="项目数量")
    avg_tech_stack_count: float = Field(..., description="平均技术栈数量")
    avg_achievement_count: float = Field(..., description="平均成果数量")
    has_detailed_description: bool = Field(..., description="是否有详细描述")
    feedback: str = Field(..., description="反馈建议")


class JobMatchScore(BaseModel):
    """岗位匹配评分"""
    total_score: float = Field(..., description="总分 (0-100)")
    job_title: Optional[str] = Field(None, description="目标岗位")
    matched_skills: List[str] = Field(default_factory=list, description="匹配的技能")
    missing_skills: List[str] = Field(default_factory=list, description="缺失的技能")
    experience_match: float = Field(..., description="经验匹配度 (0-100)")
    education_match: float = Field(..., description="学历匹配度 (0-100)")
    feedback: str = Field(..., description="反馈建议")


class ResumeScore(BaseModel):
    """简历总评分"""
    total_score: float = Field(..., description="总分 (0-100)")
    completeness: CompletenessScore = Field(..., description="完整性评分")
    professionalism: ProfessionalismScore = Field(..., description="专业性评分")
    quantification: QuantificationScore = Field(..., description="量化程度评分")
    project_depth: ProjectDepthScore = Field(..., description="项目深度评分")
    job_match: Optional[JobMatchScore] = Field(None, description="岗位匹配评分")
    dimensions: List[ScoreDimension] = Field(default_factory=list, description="各维度得分")
    overall_feedback: str = Field(..., description="总体反馈")
    strengths: List[str] = Field(default_factory=list, description="优势")
    weaknesses: List[str] = Field(default_factory=list, description="不足")
    suggestions: List[str] = Field(default_factory=list, description="改进建议")


class ResumeScoreRequest(BaseModel):
    """简历评分请求"""
    job_title: Optional[str] = Field(None, description="目标岗位（用于岗位匹配评分）")
    job_description: Optional[str] = Field(None, description="岗位描述")
    required_skills: Optional[List[str]] = Field(None, description="岗位要求技能")


class ResumeScoreResponse(BaseModel):
    """简历评分响应"""
    score: ResumeScore = Field(..., description="评分结果")
    message: str = Field(default="评分成功", description="响应消息")
