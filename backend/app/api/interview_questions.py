"""
面试题推荐 API 路由
"""
from fastapi import APIRouter, HTTPException, status

from app.schemas.interview_questions import (
    InterviewQuestionsRequest,
    InterviewQuestionsResponse
)
from app.services.interview_questions_service import interview_service

router = APIRouter(prefix="/api/v1/interview", tags=["面试题推荐"])


@router.post(
    "/recommend",
    response_model=InterviewQuestionsResponse,
    summary="推荐面试题",
    description="基于岗位描述推荐高频面试题和参考答案要点"
)
async def recommend_interview_questions(
    request: InterviewQuestionsRequest
) -> InterviewQuestionsResponse:
    """
    推荐面试题

    ## 功能说明
    - 基于岗位描述自动推荐相关的高频面试题
    - 提供参考答案要点，帮助用户准备面试
    - 根据岗位类型、技能要求智能匹配题目

    ## 请求参数
    - job_text: 岗位描述文本（必填，至少10个字符）
    - max_questions: 最多推荐题目数量（可选，默认15，范围5-50）

    ## 返回结果
    - success: 推荐是否成功
    - recommendation: 推荐结果
      - job_title: 目标岗位
      - total_questions: 推荐题目总数
      - questions_by_category: 按分类统计的题目数量
      - questions: 推荐的面试题列表
        - question: 面试题内容
        - category: 题目分类
        - difficulty: 难度等级
        - key_points: 参考答案要点
        - tags: 相关技术标签
    - message: 响应消息
    """
    try:
        if not request.job_text or len(request.job_text.strip()) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="岗位描述文本过短，请提供更详细的信息"
            )

        result = interview_service.recommend(
            request.job_text,
            request.max_questions
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"面试题推荐失败: {str(e)}"
        )
