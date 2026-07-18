"""
面试考试 API 路由
"""
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.interview_exam_service import interview_exam_service

router = APIRouter(prefix="/api/v1/interview/exam", tags=["面试考试"])


class AnswerItem(BaseModel):
    """单个答案"""
    question_id: int
    question: str
    answer: str
    time_spent: int


class ExamEvaluationRequest(BaseModel):
    """考试评估请求"""
    answers: List[AnswerItem]
    total_time: int


class ExamEvaluationResponse(BaseModel):
    """考试评估响应"""
    total_score: float
    content_score: float
    time_score: float
    avg_time: float
    total_time: int
    summary: str
    suggestions: List[str]
    answers: List[Dict[str, Any]]


@router.post("/evaluate", response_model=ExamEvaluationResponse)
async def evaluate_exam(request: ExamEvaluationRequest):
    """
    评估面试考试

    根据答题内容和时间综合评分，并提供详细反馈
    """
    try:
        answers_data = [ans.dict() for ans in request.answers]
        result = await interview_exam_service.evaluate_exam(
            answers=answers_data,
            total_time=request.total_time,
        )
        return ExamEvaluationResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"评估失败: {str(e)}"
        )
