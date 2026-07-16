"""
交互式AI面试对话 API 路由
"""
from typing import Dict
from fastapi import APIRouter, HTTPException, status

from app.schemas.interactive_interview import (
    StartInterviewRequest,
    StartInterviewResponse,
    ContinueConversationRequest,
    ContinueConversationResponse,
    NextQuestionRequest,
    NextQuestionResponse,
    EndInterviewRequest,
    EndInterviewResponse,
    SessionInfoResponse
)
from app.services.langchain_interview_service import langchain_interview_service

router = APIRouter(prefix="/api/v1/interactive-interview", tags=["交互式AI面试"])


@router.post(
    "/start",
    response_model=StartInterviewResponse,
    summary="开始面试会话",
    description="创建一个新的交互式AI面试会话"
)
async def start_interview(request: StartInterviewRequest) -> StartInterviewResponse:
    """
    开始面试会话

    ## 功能说明
    - 创建一个新的面试会话
    - 返回会话ID和面试官的开场白
    - 面试官会提出第一个问题

    ## 请求参数
    - job_title: 目标岗位（必填）
    - initial_question: 第一个面试题（必填）
    - candidate_name: 候选人姓名（可选）

    ## 返回结果
    - session_id: 会话ID（后续对话需要使用）
    - interviewer_message: 面试官的开场白和第一个问题
    - question_number: 当前问题编号

    ## 使用流程
    1. 调用此接口开始面试，获取session_id
    2. 使用session_id调用/continue接口进行对话
    3. 面试结束后调用/end接口获取总结
    """
    try:
        result = langchain_interview_service.start_session(
            job_title=request.job_title,
            initial_question=request.initial_question,
            candidate_name=request.candidate_name,
            resume_summary=request.resume_summary
        )
        return StartInterviewResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建面试会话失败: {str(e)}"
        )


@router.post(
    "/continue",
    response_model=ContinueConversationResponse,
    summary="继续对话",
    description="候选人回答后，面试官的自然回应（追问、深挖项目、询问补充或评价）"
)
async def continue_conversation(
    request: ContinueConversationRequest
) -> ContinueConversationResponse:
    """
    继续对话

    ## 功能说明
    - 候选人回答问题后，面试官会智能回应
    - 面试官会根据回答内容：
      - **追问细节**：回答不够深入时
      - **深挖项目**：提到项目经验时
      - **询问补充**：回答完整但可能还有其他内容
      - **给出评价**：候选人明确表示回答完毕后

    ## 请求参数
    - session_id: 会话ID（必填）
    - candidate_answer: 候选人的回答（必填，至少5个字符）

    ## 返回结果
    - interviewer_message: 面试官的回应
    - response_type: 回应类型
      - `follow_up`: 追问细节
      - `project_deep_dive`: 深挖项目经验
      - `ask_for_more`: 询问是否还有补充
      - `evaluation`: 给出评价和打分
    - conversation_turn: 当前对话轮次

    ## 使用技巧
    - 提到项目时，面试官会自动追问项目细节
    - 回答"没有了"、"回答完了"时，会触发评价
    - 可以随时补充和展开说明
    """
    try:
        result = await langchain_interview_service.continue_conversation(
            session_id=request.session_id,
            candidate_answer=request.candidate_answer
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["message"]
            )

        return ContinueConversationResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"对话生成失败: {str(e)}"
        )


@router.post(
    "/next-question",
    response_model=NextQuestionResponse,
    summary="提出下一个问题",
    description="当前问题讨论完毕，面试官提出下一个问题"
)
async def next_question(request: NextQuestionRequest) -> NextQuestionResponse:
    """
    提出下一个问题

    ## 功能说明
    - 当前问题讨论完毕后，切换到下一个问题
    - 面试官会自然过渡到新问题

    ## 请求参数
    - session_id: 会话ID（必填）
    - next_question: 下一个面试题（必填）

    ## 使用场景
    - 当前问题已经充分讨论完毕
    - 需要进入下一个话题
    """
    try:
        result = await langchain_interview_service.next_question(
            session_id=request.session_id,
            next_question=request.next_question
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["message"]
            )

        return NextQuestionResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"切换问题失败: {str(e)}"
        )


@router.post(
    "/end",
    response_model=EndInterviewResponse,
    summary="结束面试",
    description="结束面试会话，生成完整的面试评估报告"
)
async def end_interview(request: EndInterviewRequest) -> EndInterviewResponse:
    """
    结束面试

    ## 功能说明
    - 结束面试会话
    - 生成完整的面试评估报告，包括：
      - 整体评价和总分
      - 各问题表现总结
      - 优点和不足
      - 改进建议
      - 录用建议

    ## 请求参数
    - session_id: 会话ID（必填）

    ## 返回结果
    - interview_summary: 完整的面试评估报告（Markdown格式）
    - total_questions: 总共提问的数量
    - duration_minutes: 面试时长（分钟）
    - questions_asked: 提问过的所有问题列表
    """
    try:
        result = await langchain_interview_service.end_session(
            session_id=request.session_id
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["message"]
            )

        return EndInterviewResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"结束面试失败: {str(e)}"
        )


@router.get(
    "/session/{session_id}",
    response_model=SessionInfoResponse,
    summary="获取会话信息",
    description="查询面试会话的详细信息和对话历史"
)
async def get_session_info(session_id: str) -> SessionInfoResponse:
    """
    获取会话信息

    ## 功能说明
    - 查询面试会话的详细信息
    - 包含完整的对话历史

    ## 路径参数
    - session_id: 会话ID

    ## 返回结果
    - 会话基本信息
    - 对话历史记录
    """
    try:
        result = langchain_interview_service.get_session_info(session_id)

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在或已过期"
            )

        return SessionInfoResponse(success=True, **result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取会话信息失败: {str(e)}"
        )


@router.delete(
    "/session/{session_id}",
    summary="删除会话",
    description="删除面试会话（释放内存）"
)
async def delete_session(session_id: str) -> Dict:
    """
    删除会话

    ## 功能说明
    - 删除面试会话数据
    - 释放内存资源

    ## 路径参数
    - session_id: 会话ID
    """
    try:
        success = langchain_interview_service.delete_session(session_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在"
            )

        return {
            "success": True,
            "message": "会话已删除"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除会话失败: {str(e)}"
        )
