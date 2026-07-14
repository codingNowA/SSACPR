"""
岗位难度判断相关的数据模型
"""
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from enum import Enum


class DifficultyLevel(str, Enum):
    """难度等级枚举"""
    VERY_EASY = "very_easy"      # 很容易
    EASY = "easy"                # 容易
    MEDIUM = "medium"            # 中等
    HARD = "hard"                # 困难
    VERY_HARD = "very_hard"      # 很困难


class DifficultyFactor(BaseModel):
    """难度因素"""
    factor_name: str = Field(..., description="因素名称")
    score: float = Field(..., ge=0, le=10, description="得分(0-10)")
    weight: float = Field(..., ge=0, le=1, description="权重(0-1)")
    description: str = Field(..., description="因素说明")


class JobDifficultyRequest(BaseModel):
    """岗位难度判断请求"""
    job_title: str = Field(..., description="岗位名称", min_length=1, max_length=200)
    job_description: Optional[str] = Field(None, description="岗位描述")
    requirements: Optional[str] = Field(None, description="任职要求")
    salary_range: Optional[str] = Field(None, description="薪资范围")
    company_name: Optional[str] = Field(None, description="公司名称")
    company_size: Optional[str] = Field(None, description="公司规模")
    work_location: Optional[str] = Field(None, description="工作地点")
    education_requirement: Optional[str] = Field(None, description="学历要求")
    experience_requirement: Optional[str] = Field(None, description="工作经验要求")
    industry: Optional[str] = Field(None, description="所属行业（如：互联网、金融、教育）")
    company_type: Optional[str] = Field(None, description="公司类型（如：上市公司、创业公司、外企）")
    job_responsibilities: Optional[str] = Field(None, description="岗位职责")
    benefits: Optional[str] = Field(None, description="福利待遇")
    team_size: Optional[str] = Field(None, description="团队规模")
    work_mode: Optional[str] = Field(None, description="工作模式（如：全职、远程、混合）")
    job_highlights: Optional[List[str]] = Field(None, description="岗位亮点")
    required_skills: Optional[List[str]] = Field(None, description="必备技能列表")
    preferred_skills: Optional[List[str]] = Field(None, description="优选技能列表")
    certifications: Optional[List[str]] = Field(None, description="所需证书或资质")

    class Config:
        json_schema_extra = {
            "example": {
                "job_title": "高级Java开发工程师",
                "job_description": "负责公司核心业务系统的开发与维护",
                "requirements": "3-5年Java开发经验，熟悉Spring全家桶，了解微服务架构",
                "salary_range": "20k-35k",
                "company_name": "某科技公司",
                "company_size": "1000-5000人",
                "work_location": "北京",
                "education_requirement": "本科及以上",
                "experience_requirement": "3-5年",
                "industry": "互联网",
                "company_type": "上市公司",
                "job_responsibilities": "负责后端服务开发、系统架构设计、性能优化",
                "benefits": "五险一金、年终奖、股权激励",
                "team_size": "10-20人",
                "work_mode": "全职",
                "job_highlights": ["技术氛围好", "成长空间大", "大厂背景"],
                "required_skills": ["Java", "Spring Boot", "MySQL", "Redis"],
                "preferred_skills": ["微服务", "分布式系统", "Docker", "Kubernetes"],
                "certifications": []
            }
        }


class JobDifficultyResponse(BaseModel):
    """岗位难度判断响应"""
    job_title: str = Field(..., description="岗位名称")
    difficulty_level: DifficultyLevel = Field(..., description="难度等级")
    difficulty_score: float = Field(..., ge=0, le=100, description="难度得分(0-100)")
    difficulty_factors: List[DifficultyFactor] = Field(..., description="难度因素分析")
    summary: str = Field(..., description="难度总结")
    suggestions: List[str] = Field(default_factory=list, description="备考建议")
    competitive_analysis: Optional[str] = Field(None, description="竞争分析")
    estimated_preparation_time: Optional[str] = Field(None, description="预估准备时间")
    target_audience: Optional[str] = Field(None, description="适合人群")
    key_challenges: Optional[List[str]] = Field(None, description="主要挑战")
    success_rate_estimate: Optional[str] = Field(None, description="预估成功率")
    market_demand: Optional[str] = Field(None, description="市场需求度")
    career_development: Optional[str] = Field(None, description="职业发展前景")

    class Config:
        json_schema_extra = {
            "example": {
                "job_title": "高级Java开发工程师",
                "difficulty_level": "hard",
                "difficulty_score": 75.5,
                "difficulty_factors": [
                    {
                        "factor_name": "技术要求",
                        "score": 8.0,
                        "weight": 0.3,
                        "description": "需要3-5年Java经验，熟悉微服务架构"
                    }
                ],
                "summary": "该岗位难度较高，需要扎实的技术功底和丰富的项目经验",
                "suggestions": [
                    "深入学习Spring Cloud微服务架构",
                    "积累分布式系统开发经验"
                ],
                "competitive_analysis": "该岗位竞争激烈，建议有3年以上相关经验再投递",
                "estimated_preparation_time": "4-6周",
                "target_audience": "有3-5年Java开发经验，熟悉Spring框架的工程师",
                "key_challenges": [
                    "微服务架构设计能力",
                    "高并发系统优化经验",
                    "分布式系统问题排查能力"
                ],
                "success_rate_estimate": "有相关经验者成功率约40-50%",
                "market_demand": "市场需求旺盛，Java开发岗位占比较高",
                "career_development": "可向架构师、技术专家方向发展"
            }
        }
