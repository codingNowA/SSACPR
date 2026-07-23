"""
数据分析 API 路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.analytics_service import AnalyticsService
from app.models.analytics import (
    HotWordsResponse,
    SkillTrendResponse,
    SalaryDistributionResponse,
    ComparisonResponse,
    SkillRankResponse,
    TrendChangeResponse,
)

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/hotwords", response_model=HotWordsResponse)
def get_hotwords(
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    category: Optional[str] = Query(None, description="分类筛选"),
    db: Session = Depends(get_db)
):
    """1. 获取岗位热词"""
    service = AnalyticsService(db)
    return service.get_hotwords(limit, category)


@router.get("/skill-trend", response_model=SkillTrendResponse)
def get_skill_trend(
    skill: str = Query(..., description="技能名称"),
    months: int = Query(6, ge=1, le=24, description="月份数"),
    period: str = Query("month", description="周期: month/quarter/year"),
    db: Session = Depends(get_db)
):
    """2. 获取技能趋势"""
    service = AnalyticsService(db)
    return service.get_skill_trend(skill, months, period)


@router.get("/salary-distribution", response_model=SalaryDistributionResponse)
def get_salary_distribution(
    dimension: str = Query("city", description="维度: city/industry/education"),
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    db: Session = Depends(get_db)
):
    """3. 获取薪资分布"""
    service = AnalyticsService(db)
    return service.get_salary_distribution(dimension, limit)


@router.get("/comparison", response_model=ComparisonResponse)
def get_comparison(
    dimension: str = Query("city", description="维度: city/industry/education"),
    metric: str = Query("count", description="指标: count/avg_salary"),
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    db: Session = Depends(get_db)
):
    """4. 获取维度对比"""
    service = AnalyticsService(db)
    return service.get_comparison(dimension, metric, limit)


@router.get("/skill-rank", response_model=SkillRankResponse)
def get_skill_rank(
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    industry: Optional[str] = Query(None, description="行业筛选"),
    db: Session = Depends(get_db)
):
    """5. 获取技能排行榜"""
    service = AnalyticsService(db)
    return service.get_skill_rank(limit, industry)


@router.get("/trend-change", response_model=TrendChangeResponse)
def get_trend_change(
    months: int = Query(6, ge=1, le=24, description="月份数"),
    metric: str = Query("demand", description="指标: demand/salary"),
    dimension: str = Query("overall", description="维度: overall/city/industry"),
    db: Session = Depends(get_db)
):
    """6. 获取趋势变化"""
    service = AnalyticsService(db)
    return service.get_trend_change(months, metric, dimension)