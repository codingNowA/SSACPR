"""
数据分析业务逻辑层
"""
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.orm import Session
from loguru import logger

from app.models.analytics import (
    HotWordItem,
    HotWordsResponse,
    SkillTrendResponse,
    TrendPoint,
    SalaryDistributionItem,
    SalaryDistributionResponse,
    ComparisonItem,
    ComparisonResponse,
    SkillRankItem,
    SkillRankResponse,
    TrendChangeItem,
    TrendChangeResponse,
)


class AnalyticsService:
    """数据分析服务"""

    def __init__(self, db: Session):
        self.db = db

    # ==================== 1. 岗位热词 ====================
    def get_hotwords(self, limit: int = 20, category: Optional[str] = None) -> HotWordsResponse:
        """
        获取岗位热词
        从 job_profile 的 skills 数组中提取高频技能
        """
        query = text("""
            SELECT 
                jsonb_array_elements_text(job_profile->'skills') as skill,
                COUNT(*) as count
            FROM jobs
            WHERE status = 'active'
            GROUP BY skill
            ORDER BY count DESC
            LIMIT :limit
        """)

        result = self.db.execute(query, {"limit": limit})
        rows = result.fetchall()

        hotwords = [
            HotWordItem(
                word=row[0],
                count=row[1],
                category="技能"
            )
            for row in rows
        ]

        return HotWordsResponse(
            hotwords=hotwords,
            total=len(hotwords),
            updated_at=datetime.now()
        )

    # ==================== 2. 技能趋势 ====================
    def get_skill_trend(self, skill: str, months: int = 6, period: str = "month") -> SkillTrendResponse:
        """
        获取指定技能的趋势
        """
        query = text("""
            SELECT 
                TO_CHAR(DATE_TRUNC('month', created_at), 'YYYY-MM') as month,
                COUNT(*) as count
            FROM jobs
            WHERE status = 'active'
                AND job_profile->'skills' ? :skill
                AND created_at >= NOW() - (:months || ' months')::interval
            GROUP BY month
            ORDER BY month
        """)

        result = self.db.execute(query, {"skill": skill, "months": months})
        rows = result.fetchall()

        trends = [
            TrendPoint(
                date=row[0],
                value=float(row[1]),
                skill=skill
            )
            for row in rows
        ]

        return SkillTrendResponse(
            trends=trends,
            skill=skill,
            period=period
        )

    # ==================== 3. 薪资分布 ====================
    def get_salary_distribution(self, dimension: str = "city", limit: int = 10) -> SalaryDistributionResponse:
        """
        获取薪资分布
        """
        dimension_field = {
            "city": "location",
            "industry": "industry",
            "education": "education_required"
        }.get(dimension, "location")

        query = text(f"""
            WITH parsed_salary AS (
                SELECT 
                    {dimension_field} as group_value,
                    CASE 
                        WHEN salary_range LIKE '%-%' THEN 
                            (CAST(SPLIT_PART(REPLACE(REPLACE(salary_range, 'k', ''), 'K', ''), '-', 1) AS FLOAT) +
                             CAST(SPLIT_PART(REPLACE(REPLACE(salary_range, 'k', ''), 'K', ''), '-', 2) AS FLOAT)) / 2
                        ELSE 0
                    END as avg_salary
                FROM jobs
                WHERE status = 'active' AND {dimension_field} IS NOT NULL
            )
            SELECT 
                group_value,
                COUNT(*) as count,
                AVG(avg_salary) as avg_salary
            FROM parsed_salary
            GROUP BY group_value
            ORDER BY count DESC
            LIMIT :limit
        """)

        result = self.db.execute(query, {"limit": limit})
        rows = result.fetchall()

        total_query = text("SELECT COUNT(*) FROM jobs WHERE status = 'active'")
        total_result = self.db.execute(total_query)
        total_count = total_result.scalar()

        items = []
        for row in rows:
            group_name = row[0] or "未知"
            count = row[1]
            avg_salary = round(row[2], 1) if row[2] else 0

            items.append(SalaryDistributionItem(
                range=f"{group_name} ({avg_salary}K)" if avg_salary > 0 else group_name,
                count=count,
                percentage=round((count / total_count) * 100, 2),
                cities=[row[0]] if dimension == "city" else None,
                industries=[row[0]] if dimension == "industry" else None,
            ))

        return SalaryDistributionResponse(
            distributions=items,
            total=total_count,
            dimension=dimension
        )

    # ==================== 4. 维度对比 ====================
    def get_comparison(self, dimension: str = "city", metric: str = "count", limit: int = 10) -> ComparisonResponse:
        """
        获取各维度对比数据
        """
        dimension_field = {
            "city": "location",
            "industry": "industry",
            "education": "education_required"
        }.get(dimension, "location")

        if metric == "avg_salary":
            # 计算平均薪资
            query = text(f"""
                WITH parsed_salary AS (
                    SELECT
                        {dimension_field} as name,
                        CASE
                            WHEN salary_range LIKE '%-%' THEN
                                (CAST(SPLIT_PART(REPLACE(REPLACE(salary_range, 'k', ''), 'K', ''), '-', 1) AS FLOAT) +
                                 CAST(SPLIT_PART(REPLACE(REPLACE(salary_range, 'k', ''), 'K', ''), '-', 2) AS FLOAT)) / 2
                            ELSE 0
                        END as avg_salary
                    FROM jobs
                    WHERE status = 'active' AND {dimension_field} IS NOT NULL
                )
                SELECT
                    name,
                    COUNT(*) as count,
                    AVG(avg_salary) as avg_salary
                FROM parsed_salary
                GROUP BY name
                ORDER BY avg_salary DESC
                LIMIT :limit
            """)
        else:
            # 计算岗位数量
            query = text(f"""
                SELECT
                    {dimension_field} as name,
                    COUNT(*) as count,
                    NULL as avg_salary
                FROM jobs
                WHERE status = 'active' AND {dimension_field} IS NOT NULL
                GROUP BY {dimension_field}
                ORDER BY COUNT(*) DESC
                LIMIT :limit
            """)

        result = self.db.execute(query, {"limit": limit})
        rows = result.fetchall()

        items = []
        for row in rows:
            name = row[0] or "未知"
            count = row[1]
            avg_salary = round(row[2], 1) if row[2] else None

            items.append(ComparisonItem(
                name=name,
                value=float(avg_salary if metric == "avg_salary" and avg_salary else count),
                count=count,
                avg_salary=avg_salary
            ))

        return ComparisonResponse(
            items=items,
            dimension=dimension,
            metric=metric
        )

    # ==================== 5. 技能排行 ====================
    def get_skill_rank(
        self,
        limit: int = 20,
        industry: Optional[str] = None
    ) -> SkillRankResponse:
        """
        获取技能排行榜
        """
        filter_clause = "AND industry = :industry" if industry else ""

        # 主查询：获取技能出现次数
        query = text(f"""
            SELECT 
                jsonb_array_elements_text(job_profile->'skills') as skill,
                COUNT(*) as count
            FROM jobs
            WHERE status = 'active'
                {filter_clause}
            GROUP BY skill
            ORDER BY count DESC
            LIMIT :limit
        """)

        params = {"limit": limit}
        if industry:
            params["industry"] = industry

        result = self.db.execute(query, params)
        rows = result.fetchall()

        # 修正：使用子查询统计不重复技能总数
        total_query = text(f"""
            SELECT COUNT(DISTINCT skill) FROM (
                SELECT jsonb_array_elements_text(job_profile->'skills') AS skill
                FROM jobs
                WHERE status = 'active'
                {filter_clause}
            ) sub
        """)
        total_result = self.db.execute(total_query, params)  # 注意：必须传入相同的params（包含industry）
        total = total_result.scalar() or 0

        skills = [
            SkillRankItem(
                skill=row[0],
                count=row[1],
                percentage=round((row[1] / total) * 100, 2) if total > 0 else 0,
                trend=None
            )
            for row in rows
        ]

        return SkillRankResponse(
            skills=skills,
            total=total,
            updated_at=datetime.now()
        )
    
    # ==================== 6. 趋势变化 ====================
    def get_trend_change(self, months: int = 6, metric: str = "demand", dimension: str = "overall") -> TrendChangeResponse:
        """
        获取整体趋势变化
        """
        query = text("""
            SELECT 
                TO_CHAR(DATE_TRUNC('month', created_at), 'YYYY-MM') as month,
                COUNT(*) as count
            FROM jobs
            WHERE status = 'active'
                AND created_at >= NOW() - (:months || ' months')::interval
            GROUP BY month
            ORDER BY month
        """)

        result = self.db.execute(query, {"months": months})
        rows = result.fetchall()

        data = []
        for i, row in enumerate(rows):
            change_rate = None
            if i > 0 and rows[i-1][1] > 0:
                change_rate = round(((row[1] - rows[i-1][1]) / rows[i-1][1]) * 100, 2)

            data.append(
                TrendChangeItem(
                    date=row[0],
                    value=float(row[1]),
                    change_rate=change_rate
                )
            )

        return TrendChangeResponse(
            data=data,
            metric=metric,
            dimension=dimension
        )