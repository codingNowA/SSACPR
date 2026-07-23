"""
简历结构化数据模型
定义教育经历、实习经历、项目经验等结构
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class BasicInfo(BaseModel):
    """基本信息"""
    name: Optional[str] = Field(None, description="姓名")
    phone: Optional[str] = Field(None, description="电话")
    email: Optional[str] = Field(None, description="邮箱")
    age: Optional[int] = Field(None, description="年龄")
    gender: Optional[str] = Field(None, description="性别")
    location: Optional[str] = Field(None, description="所在地")
    job_intention: Optional[str] = Field(None, description="求职意向")


class Education(BaseModel):
    """教育经历"""
    school: Optional[str] = Field(None, description="学校名称")
    major: Optional[str] = Field(None, description="专业")
    degree: Optional[str] = Field(None, description="学历（本科/硕士/博士）")
    start_date: Optional[str] = Field(None, description="开始时间")
    end_date: Optional[str] = Field(None, description="结束时间")
    gpa: Optional[str] = Field(None, description="GPA")
    description: Optional[str] = Field(None, description="描述")


class WorkExperience(BaseModel):
    """工作/实习经历"""
    company: Optional[str] = Field(None, description="公司名称")
    position: Optional[str] = Field(None, description="职位")
    start_date: Optional[str] = Field(None, description="开始时间")
    end_date: Optional[str] = Field(None, description="结束时间")
    description: Optional[str] = Field(None, description="工作内容")
    achievements: Optional[List[str]] = Field(default_factory=list, description="工作成果")


class ProjectExperience(BaseModel):
    """项目经验"""
    name: Optional[str] = Field(None, description="项目名称")
    role: Optional[str] = Field(None, description="项目角色")
    start_date: Optional[str] = Field(None, description="开始时间")
    end_date: Optional[str] = Field(None, description="结束时间")
    description: Optional[str] = Field(None, description="项目描述")
    tech_stack: Optional[List[str]] = Field(default_factory=list, description="技术栈")
    achievements: Optional[List[str]] = Field(default_factory=list, description="项目成果")


class SkillTag(BaseModel):
    """技能标签"""
    category: Optional[str] = Field(None, description="技能分类（编程语言/框架/工具等）")
    name: str = Field(..., description="技能名称")
    level: Optional[str] = Field(None, description="熟练度（熟练/精通/了解）")


class ResumeStructuredData(BaseModel):
    """简历结构化数据"""
    basic_info: Optional[BasicInfo] = Field(None, description="基本信息")
    education: List[Education] = Field(default_factory=list, description="教育经历")
    work_experience: List[WorkExperience] = Field(default_factory=list, description="工作/实习经历")
    project_experience: List[ProjectExperience] = Field(default_factory=list, description="项目经验")
    skills: List[SkillTag] = Field(default_factory=list, description="技能标签")


class ResumeExtractResponse(BaseModel):
    """简历结构化提取响应"""
    text: str = Field(..., description="原始文本")
    structured_data: ResumeStructuredData = Field(..., description="结构化数据")
    message: str = Field(default="提取成功", description="响应消息")
