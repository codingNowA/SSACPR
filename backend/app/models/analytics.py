"""
数据分析模块数据模型
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


# ==================== 热词分析 ====================
class HotWordItem(BaseModel):
    """热词项"""
    word: str
    count: int
    category: Optional[str] = None  # 技能/岗位/行业


class HotWordsResponse(BaseModel):
    """热词响应"""
    hotwords: List[HotWordItem]
    total: int
    updated_at: datetime


# ==================== 技能趋势 ====================
class TrendPoint(BaseModel):
    """趋势数据点"""
    date: str  # 格式: YYYY-MM
    value: float
    skill: Optional[str] = None


class SkillTrendResponse(BaseModel):
    """技能趋势响应"""
    trends: List[TrendPoint]
    skill: str
    period: str  # month / quarter / year


# ==================== 薪资分布 ====================
class SalaryDistributionItem(BaseModel):
    """薪资分布项"""
    range: str  # 如: "0-10k", "10-20k", "20-30k"
    count: int
    percentage: float
    cities: Optional[List[str]] = None
    industries: Optional[List[str]] = None


class SalaryDistributionResponse(BaseModel):
    """薪资分布响应"""
    distributions: List[SalaryDistributionItem]
    total: int
    dimension: str  # city / industry / education


# ==================== 维度对比 ====================
class ComparisonItem(BaseModel):
    """对比项"""
    name: str  # 维度值，如"北京"或"互联网"
    value: float
    count: int
    avg_salary: Optional[float] = None


class ComparisonResponse(BaseModel):
    """对比响应"""
    items: List[ComparisonItem]
    dimension: str  # city / industry / education
    metric: str  # count / avg_salary


# ==================== 技能排行 ====================
class SkillRankItem(BaseModel):
    """技能排行项"""
    skill: str
    count: int
    percentage: float
    trend: Optional[str] = None  # up / down / stable


class SkillRankResponse(BaseModel):
    """技能排行响应"""
    skills: List[SkillRankItem]
    total: int
    updated_at: datetime


# ==================== 趋势变化 ====================
class TrendChangeItem(BaseModel):
    """趋势变化项"""
    date: str
    value: float
    change_rate: Optional[float] = None  # 环比变化率


class TrendChangeResponse(BaseModel):
    """趋势变化响应"""
    data: List[TrendChangeItem]
    metric: str  # demand / salary
    dimension: str  # overall / city / industry