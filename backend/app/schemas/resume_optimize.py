"""
简历优化建议和文案数据模型
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class OptimizationSuggestion(BaseModel):
    """单条优化建议"""
    category: str = Field(..., description="建议类别（基本信息/教育经历/工作经历/项目经验/技能标签）")
    priority: str = Field(..., description="优先级（高/中/低）")
    title: str = Field(..., description="建议标题")
    description: str = Field(..., description="问题描述")
    current_content: Optional[str] = Field(None, description="当前内容")
    suggested_content: str = Field(..., description="建议修改后的内容")
    reason: str = Field(..., description="修改原因")
    examples: Optional[List[str]] = Field(default_factory=list, description="示例")


class OptimizedSection(BaseModel):
    """优化后的简历章节"""
    section: str = Field(..., description="章节名称")
    original: str = Field(..., description="原始内容")
    optimized: str = Field(..., description="优化后内容")
    improvements: List[str] = Field(..., description="改进点说明")


class JobTargetedOptimization(BaseModel):
    """面向岗位的优化"""
    job_title: str = Field(..., description="目标岗位")
    match_score: float = Field(..., description="当前匹配度 (0-100)")
    key_requirements: List[str] = Field(..., description="岗位关键要求")
    matched_points: List[str] = Field(..., description="已匹配的优势")
    improvement_areas: List[str] = Field(..., description="需要改进的方面")
    optimized_sections: List[OptimizedSection] = Field(..., description="针对岗位优化的各章节")
    additional_suggestions: List[str] = Field(default_factory=list, description="额外建议")


class ResumeOptimization(BaseModel):
    """简历优化结果"""
    general_suggestions: List[OptimizationSuggestion] = Field(..., description="通用优化建议")
    job_targeted: Optional[JobTargetedOptimization] = Field(None, description="面向岗位的优化（可选）")
    priority_actions: List[str] = Field(..., description="优先行动清单")
    estimated_improvement: Dict[str, float] = Field(..., description="预估改进效果（各维度分数提升）")
    overall_summary: str = Field(..., description="优化总结")


class ResumeOptimizationRequest(BaseModel):
    """简历优化请求"""
    job_title: Optional[str] = Field(None, description="目标岗位")
    job_description: Optional[str] = Field(None, description="岗位描述")
    focus_areas: Optional[List[str]] = Field(None, description="重点关注领域")


class ResumeOptimizationResponse(BaseModel):
    """简历优化响应"""
    optimization: ResumeOptimization = Field(..., description="优化结果")
    message: str = Field(default="优化建议生成成功", description="响应消息")
