"""
岗位难度分析 API 路由
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict

from app.schemas.job_difficulty import JobDifficultyRequest, JobDifficultyResponse
from app.services.job_difficulty_service import job_difficulty_analyzer

router = APIRouter(prefix="/api/v1/job-difficulty", tags=["岗位难度分析"])


@router.post(
    "/analyze",
    response_model=JobDifficultyResponse,
    summary="分析岗位难度",
    description="根据岗位信息分析岗位难度，返回难度等级、得分、影响因素和建议"
)
async def analyze_job_difficulty(request: JobDifficultyRequest) -> JobDifficultyResponse:
    """
    分析岗位难度

    ## 功能说明
    - 分析岗位的学历要求、经验要求、技术要求等因素
    - 综合计算岗位难度得分（0-100分）
    - 给出难度等级（很容易/容易/中等/困难/很困难）
    - 提供备考建议和竞争分析

    ## 请求参数
    - job_title: 岗位名称（必填）
    - job_description: 岗位描述（可选）
    - requirements: 任职要求（可选）
    - salary_range: 薪资范围（可选）
    - education_requirement: 学历要求（可选）
    - experience_requirement: 工作经验要求（可选）

    ## 返回结果
    - difficulty_level: 难度等级
    - difficulty_score: 难度得分
    - difficulty_factors: 各难度因素详细分析
    - summary: 难度总结
    - suggestions: 备考建议
    - competitive_analysis: 竞争分析
    """
    try:
        result = job_difficulty_analyzer.analyze(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"岗位难度分析失败: {str(e)}"
        )


@router.post(
    "/batch-analyze",
    response_model=Dict[str, JobDifficultyResponse],
    summary="批量分析岗位难度",
    description="批量分析多个岗位的难度"
)
async def batch_analyze_job_difficulty(
    requests: Dict[str, JobDifficultyRequest]
) -> Dict[str, JobDifficultyResponse]:
    """
    批量分析岗位难度

    ## 功能说明
    适用于需要对比多个岗位难度的场景

    ## 请求参数
    以岗位ID或岗位名称为key，岗位信息为value的字典

    ## 返回结果
    返回对应的难度分析结果字典
    """
    try:
        results = {}
        for job_id, request in requests.items():
            results[job_id] = job_difficulty_analyzer.analyze(request)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量岗位难度分析失败: {str(e)}"
        )


@router.get(
    "/difficulty-levels",
    summary="获取难度等级说明",
    description="获取所有难度等级的详细说明"
)
async def get_difficulty_levels() -> Dict[str, Dict[str, str]]:
    """
    获取难度等级说明

    返回所有难度等级的定义和说明，供前端展示使用
    """
    return {
        "very_easy": {
            "name": "很容易",
            "score_range": "0-20",
            "description": "门槛很低，适合应届生或转行人士",
            "color": "#52c41a"
        },
        "easy": {
            "name": "容易",
            "score_range": "20-40",
            "description": "入门难度较低，有一定基础即可",
            "color": "#95de64"
        },
        "medium": {
            "name": "中等",
            "score_range": "40-60",
            "description": "难度适中，需要相关专业背景和经验",
            "color": "#faad14"
        },
        "hard": {
            "name": "困难",
            "score_range": "60-80",
            "description": "有一定门槛，需要扎实的能力和经验",
            "color": "#ff7a45"
        },
        "very_hard": {
            "name": "很困难",
            "score_range": "80-100",
            "description": "要求很高，需要深厚功底和丰富经验",
            "color": "#f5222d"
        }
    }
