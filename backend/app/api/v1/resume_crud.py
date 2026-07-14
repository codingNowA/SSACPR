"""
简历 CRUD 和诊断相关 API（缺失的路由）
"""
from fastapi import APIRouter, HTTPException, status
from app.schemas.common import ApiResponse
from app.services.job_service import get_db_pool
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resume", tags=["简历管理"])


@router.get("/{resume_id}")
async def get_resume(resume_id: int):
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
                "parsed_data": row['parsed_data'],
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
async def parse_resume_by_id(resume_id: int):
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
async def diagnose_resume_by_id(resume_id: int):
    """
    诊断已上传的简历

    Args:
        resume_id: 简历ID

    Returns:
        诊断结果（评分和建议）
    """
    try:
        from app.core.resume.scorer import resume_scorer
        from app.core.resume import resume_parser

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

            # 重新解析文件以获取文本
            parse_result = resume_parser.parse(file_path)
            resume_text = parse_result.get('text', '')

            # 将 parsed_data 转换为 Pydantic 模型
            import json
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
