"""
岗位信息提取 API 路由
"""
from fastapi import APIRouter, HTTPException, status

from app.schemas.job_extraction import JobExtractionRequest, JobExtractionResponse
from app.services.job_extraction_service import job_info_extractor

router = APIRouter(prefix="/api/v1/job-extraction", tags=["岗位信息提取"])


@router.post(
    "/extract",
    response_model=JobExtractionResponse,
    summary="提取岗位关键信息",
    description="从岗位描述文本中自动提取学历、经验、技能、地点、薪资等关键信息"
)
async def extract_job_info(request: JobExtractionRequest) -> JobExtractionResponse:
    """
    提取岗位关键信息

    ## 功能说明
    - 从非结构化的岗位描述文本中自动提取关键信息
    - 支持识别学历、经验、薪资、地点、技能等字段
    - 返回置信度评分和提取说明

    ## 请求参数
    - job_text: 岗位描述文本（必填）

    ## 返回结果
    - success: 提取是否成功
    - extracted_info: 提取的结构化信息
    - confidence_score: 提取置信度（0-1）
    - extraction_notes: 提取说明
    - missing_fields: 未能提取的字段列表
    """
    try:
        if not request.job_text or len(request.job_text.strip()) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="岗位描述文本过短，请提供更详细的信息"
            )

        result = job_info_extractor.extract(request.job_text)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"信息提取失败: {str(e)}"
        )
