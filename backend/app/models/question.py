"""
题库管理数据模型
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


# ==================== 请求模型 ====================
class QuestionCreate(BaseModel):
    """创建题目请求"""
    category: Optional[str] = None
    difficulty: str  # easy / medium / hard
    question: str
    answer_points: Optional[str] = None
    related_skills: Optional[List[str]] = None


class QuestionUpdate(BaseModel):
    """更新题目请求（全部可选）"""
    category: Optional[str] = None
    difficulty: Optional[str] = None
    question: Optional[str] = None
    answer_points: Optional[str] = None
    related_skills: Optional[List[str]] = None


# ==================== 响应模型 ====================
class QuestionResponse(BaseModel):
    """题目响应"""
    id: int
    category: Optional[str]
    difficulty: str
    question: str
    answer_points: Optional[str]
    related_skills: Optional[List[str]]
    created_at: datetime

    class Config:
        from_attributes = True


class QuestionListResponse(BaseModel):
    """题目列表响应"""
    items: List[QuestionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int