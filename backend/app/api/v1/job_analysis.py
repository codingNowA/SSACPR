"""
岗位分析 API 路由

提供岗位详细解读和市场分析功能
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.auth import get_current_user
from app.schemas.common import ApiResponse
from app.services.job_analysis_service import job_analysis_service
from app.services.job_service import job_service

router = APIRouter(prefix="/job-analysis", tags=["岗位解读"])


@router.get("/interpret/{job_id}", summary="岗位详细解读")
async def interpret_job(
    job_id: int,
    _user: dict = Depends(get_current_user),
) -> ApiResponse:
    """
    对指定岗位进行详细解读

    返回：
    - 核心信息（职责、技能、要求）
    - 市场分析（薪资竞争力、技能热度）
    - 职业发展路径
    - 适合人群画像
    """
    try:
        # 获取岗位数据
        job_response = await job_service.get_job(job_id)
        if not job_response:
            raise HTTPException(status_code=404, detail="岗位不存在")

        # 转换为字典格式供分析服务使用
        job_data = job_response.dict()

        # 分析岗位
        result = await job_analysis_service.analyze_job(job_id, job_data)

        return ApiResponse.success(data=result)
    except HTTPException:
        raise
    except Exception as e:
        return ApiResponse.error(message=f"岗位解读失败: {e}")
