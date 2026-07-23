"""
面试模拟问答相关的Schema定义
"""
from pydantic import BaseModel, Field
from typing import Optional


class MockAnswerRequest(BaseModel):
    """模拟答题请求"""
    question_id: Optional[int] = Field(None, description="问题ID（可选）")
    question: str = Field(..., description="面试问题")
    answer: str = Field(..., description="用户的答案")
    job_id: Optional[int] = Field(None, description="岗位ID（用于上下文）")
    resume_id: Optional[int] = Field(None, description="简历ID（用于上下文）")


class MockAnswerFeedback(BaseModel):
    """答题反馈"""
    score: int = Field(..., description="答案评分(0-100)")
    overall_assessment: str = Field(..., description="总体评价")
    strengths: list[str] = Field(default_factory=list, description="优点")
    weaknesses: list[str] = Field(default_factory=list, description="不足")
    suggestions: list[str] = Field(default_factory=list, description="改进建议")
    sample_answer: Optional[str] = Field(None, description="参考答案示例")


class MockAnswerResponse(BaseModel):
    """模拟答题响应"""
    question: str
    answer: str
    feedback: MockAnswerFeedback
