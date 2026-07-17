"""
面试模拟问答API
"""
from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import get_current_user
from app.schemas.common import ApiResponse
from app.schemas.interview_mock import (
    MockAnswerRequest,
    MockAnswerResponse,
    MockAnswerFeedback,
)
from app.services.interview_mock_service import interview_mock_service
from app.services.job_service import job_service
import asyncpg

router = APIRouter(prefix="/interview-mock", tags=["面试模拟"])


@router.post("/evaluate", response_model=ApiResponse[MockAnswerResponse], summary="评估面试答案")
async def evaluate_answer(
    request: MockAnswerRequest,
    current_user: dict = Depends(get_current_user),
) -> ApiResponse:
    """
    评估用户的面试答案

    提供：
    - 评分（0-100）
    - 总体评价
    - 优点分析
    - 不足分析
    - 改进建议
    - 参考答案
    """
    try:
        # 获取上下文信息
        job_context = None
        resume_context = None

        if request.job_id:
            try:
                job_context = await job_service.get_job(request.job_id)
                if job_context:
                    job_context = job_context.dict()
            except Exception:
                pass

        if request.resume_id:
            # TODO: 从数据库获取简历信息
            pass

        # 评估答案
        feedback_dict = await interview_mock_service.evaluate_answer(
            question=request.question,
            answer=request.answer,
            job_context=job_context,
            resume_context=resume_context,
        )

        # 构建响应
        feedback = MockAnswerFeedback(**feedback_dict)
        response_data = MockAnswerResponse(
            question=request.question,
            answer=request.answer,
            feedback=feedback,
        )

        return ApiResponse.success(data=response_data)

    except Exception as e:
        return ApiResponse.error(message=f"评估答案失败: {str(e)}")
