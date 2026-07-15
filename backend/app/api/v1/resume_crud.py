"""
简历 CRUD 和诊断相关 API（缺失的路由）
"""
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.auth import get_current_user
from app.schemas.common import ApiResponse
from app.services.job_service import get_db_pool
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resume", tags=["简历管理"])
def _rebuild_text_from_parsed(parsed_data: dict) -> str:
    """从 parsed_data 重建文本，供 LLM 评分使用，避免重复解析文件"""
    parts = []
    bi = parsed_data.get('basic_info') or parsed_data.get('basicInfo')
    if bi:
        parts.append(f"姓名:{bi.get('name','')} 电话:{bi.get('phone','')} 邮箱:{bi.get('email','')} 求职意向:{bi.get('job_intention','')}")
    for edu in (parsed_data.get('education') or []):
        parts.append(f"教育:{edu.get('school','')} {edu.get('major','')} {edu.get('degree','')} {edu.get('start_date','')}-{edu.get('end_date','')}")
    for w in (parsed_data.get('work_experience') or parsed_data.get('workExperience') or []):
        parts.append(f"工作:{w.get('company','')} {w.get('position','')} {w.get('start_date','')}-{w.get('end_date','至今')}")
    for p in (parsed_data.get('projects') or []):
        parts.append(f"项目:{p.get('name','')} {p.get('description','')} {p.get('role','')}")
    skills = parsed_data.get('skills') or []
    if skills:
        parts.append('技能:' + ','.join(s if isinstance(s, str) else s.get('name','') for s in skills))
    return '\n'.join(parts)


@router.get("/{resume_id}")
async def get_resume(resume_id: int, _user: dict = Depends(get_current_user)):
    """
    获取简历数据

    Args:
        resume_id: 简历ID

    Returns:
        简历数据
    """
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, user_id, file_path, file_type, parsed_data, status, created_at, updated_at
                FROM resumes
                WHERE id = $1 AND status = 'active'
                """,
                resume_id
            )

            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"简历 {resume_id} 不存在"
                )

            resume_data = {
                "id": row['id'],
                "user_id": row['user_id'],
                "file_path": row['file_path'],
                "file_type": row['file_type'],
                "parsed_data": json.loads(row['parsed_data']) if isinstance(row['parsed_data'], str) else row['parsed_data'],
                "status": row['status'],
                "created_at": row['created_at'].isoformat() if row['created_at'] else None,
                "updated_at": row['updated_at'].isoformat() if row['updated_at'] else None,
            }

            return ApiResponse(
                code=200,
                message="获取成功",
                data=resume_data
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取简历失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取简历失败: {str(e)}"
        )


@router.post("/{resume_id}/parse")
async def parse_resume_by_id(resume_id: int, _user: dict = Depends(get_current_user)):
    """
    解析已上传的简历

    Args:
        resume_id: 简历ID

    Returns:
        解析后的简历数据
    """
    try:
        # 获取简历文件路径
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT file_path, parsed_data FROM resumes WHERE id = $1 AND status = 'active'",
                resume_id
            )

            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"简历 {resume_id} 不存在"
                )

            # 返回已解析的数据
            parsed_data = row['parsed_data'] or {}
            if isinstance(parsed_data, str):
                parsed_data = json.loads(parsed_data)

            return ApiResponse(
                code=200,
                message="解析成功",
                data=parsed_data
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"解析简历失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"解析简历失败: {str(e)}"
        )


@router.post("/{resume_id}/diagnose")
async def diagnose_resume_by_id(resume_id: int, _user: dict = Depends(get_current_user)):
    """
    诊断已上传的简历

    Args:
        resume_id: 简历ID

    Returns:
        诊断结果（评分和建议）
    """
    try:
        from app.core.resume.scorer import resume_scorer

        # 获取简历数据
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT file_path, parsed_data FROM resumes WHERE id = $1 AND status = 'active'",
                resume_id
            )

            if not row or not row['parsed_data']:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"简历 {resume_id} 不存在或未解析"
                )

            file_path = row['file_path']
            parsed_data = row['parsed_data']

            # 从 parsed_data 重建文本，避免重复解析文件
            _pd_raw = row['parsed_data']
            if isinstance(_pd_raw, str):
                _pd_raw = json.loads(_pd_raw)
            resume_text = _rebuild_text_from_parsed(_pd_raw)

            # 将 parsed_data 转换为 Pydantic 模型
            from app.schemas.resume_structured import ResumeStructuredData

            if isinstance(parsed_data, str):
                parsed_data_dict = json.loads(parsed_data)
            else:
                parsed_data_dict = parsed_data

            structured_data = ResumeStructuredData(**parsed_data_dict)

            # 调用评分器
            score_result = await resume_scorer.score_resume(
                structured_data=structured_data,
                resume_text=resume_text
            )

            return ApiResponse(
                code=200,
                message="诊断成功",
                data={
                    "resume_id": resume_id,
                    "scores": score_result.dict()
                }
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"诊断简历失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"诊断简历失败: {str(e)}"
        )


@router.get("/{resume_id}/scores")
async def get_resume_scores(resume_id: int, _user: dict = Depends(get_current_user)):
    """
    获取简历评分（诊断结果）

    Args:
        resume_id: 简历ID

    Returns:
        评分结果
    """
    return await diagnose_resume_by_id(resume_id, _user=_user)


@router.post("/{resume_id}/optimize")
async def optimize_resume_by_id(resume_id: int, job_title: str = None, _user: dict = Depends(get_current_user)):
    """
    优化已上传的简历

    Args:
        resume_id: 简历ID
        job_title: 目标岗位（可选）

    Returns:
        优化后的诊断结果
    """
    try:
        from app.core.resume.scorer import resume_scorer
        from app.core.resume.optimizer import resume_optimizer

        # 获取简历数据
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT file_path, parsed_data FROM resumes WHERE id = $1 AND status = 'active'",
                resume_id
            )

            if not row or not row['parsed_data']:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"简历 {resume_id} 不存在或未解析"
                )

            file_path = row['file_path']
            parsed_data = row['parsed_data']

            # 从 parsed_data 重建文本，避免重复解析文件
            _pd_raw = row['parsed_data']
            if isinstance(_pd_raw, str):
                _pd_raw = json.loads(_pd_raw)
            resume_text = _rebuild_text_from_parsed(_pd_raw)

            # 将 parsed_data 转换为 Pydantic 模型
            from app.schemas.resume_structured import ResumeStructuredData

            if isinstance(parsed_data, str):
                parsed_data_dict = json.loads(parsed_data)
            else:
                parsed_data_dict = parsed_data

            structured_data = ResumeStructuredData(**parsed_data_dict)

            # 调用评分器
            score_result = await resume_scorer.score_resume(
                structured_data=structured_data,
                resume_text=resume_text,
                job_title=job_title
            )

            # 调用优化器
            optimization_result = await resume_optimizer.optimize_resume(
                structured_data=structured_data,
                score=score_result,
                resume_text=resume_text,
                job_title=job_title
            )

            return ApiResponse(
                code=200,
                message="优化成功",
                data={
                    "resume_id": resume_id,
                    "scores": score_result.dict(),
                    "optimization": optimization_result.dict()
                }
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"优化简历失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"优化简历失败: {str(e)}"
        )
