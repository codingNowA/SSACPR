"""
岗位匹配 API 路由
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import get_current_user
from app.schemas.common import ApiResponse
from app.schemas.job import JobMatchRequest, JobMatchResponse, MatchHistoryResponse
from app.services.match_service import job_matcher

router = APIRouter(prefix="/match", tags=["岗位匹配"])


@router.post("/calculate", summary="计算岗位匹配")
async def calculate_match(request: JobMatchRequest, _user: dict = Depends(get_current_user),) -> ApiResponse[JobMatchResponse]:
    """
    根据简历和用户偏好计算岗位匹配度

    - 输入简历 ID 和可选的筛选偏好
    - 返回按匹配度分层的岗位推荐列表
    - 包含命中技能、缺失技能和推荐理由
    """
    try:
        result = await job_matcher.match(request)
        return ApiResponse.success(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        return ApiResponse.error(message=f"岗位匹配失败: {e}")


@router.get("/history", summary="获取匹配历史")
async def get_match_history(_user: dict = Depends(get_current_user), resume_id: Optional[int] = Query(default=None, description="简历 ID"),
    user_id: Optional[int] = Query(default=None, description="用户 ID"),
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
) -> ApiResponse[MatchHistoryResponse]:
    """查询匹配历史记录"""
    if resume_id is None and user_id is None:
        raise HTTPException(status_code=400, detail="请至少提供 resume_id 或 user_id")
    try:
        result = await job_matcher.get_match_history(
            resume_id=resume_id, user_id=user_id,
            page=page, page_size=page_size,
        )
        return ApiResponse.success(data=result)
    except Exception as e:
        return ApiResponse.error(message=f"获取匹配历史失败: {e}")


@router.post("/explain", summary="解释匹配原因")
async def explain_match(
    match_id: int = Query(..., description="匹配记录 ID"),
    _user: dict = Depends(get_current_user),
) -> ApiResponse[dict]:
    """
    对已有的匹配记录生成更详细的匹配解释

    与 calculate 接口的简要理由不同，此接口生成更详细的解释文本
    """
    try:
        from app.ai.llm.prompts import EXPLAIN_SYSTEM_PROMPT, build_explain_user_prompt
        from app.ai.llm.chain import llm_service
        from app.services.job_service import get_db_pool

        pool = await get_db_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT m.match_score, m.matched_skills, m.missing_skills, m.reason,
                       j.title as job_title, j.company
                FROM matches m
                LEFT JOIN jobs j ON m.job_id = j.id
                WHERE m.id = $1
                """,
                match_id,
            )

        if row is None:
            raise HTTPException(status_code=404, detail="匹配记录不存在")

        matched_skills = row["matched_skills"]
        if isinstance(matched_skills, str):
            import json
            matched_skills = json.loads(matched_skills)
        missing_skills = row["missing_skills"]
        if isinstance(missing_skills, str):
            import json
            missing_skills = json.loads(missing_skills)

        explanation = await llm_service.generate_text(
            prompt=build_explain_user_prompt(
                job_title=row["job_title"] or "",
                company=row["company"],
                match_score=float(row["match_score"]),
                matched_skills=matched_skills or [],
                missing_skills=missing_skills or [],
            ),
            system_prompt=EXPLAIN_SYSTEM_PROMPT,
        )

        return ApiResponse.success(data={
            "match_id": match_id,
            "explanation": explanation,
            "original_reason": row["reason"],
        })
    except HTTPException:
        raise
    except Exception as e:
        return ApiResponse.error(message=f"生成匹配解释失败: {e}")
