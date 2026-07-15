"""
岗位服务 - 岗位 CRUD、OpenSearch 索引管理与检索

合并自:
  - feature/data-analysis: update_job、增强列表筛选、job_profile 字段
  - test/merge_2-3: asyncpg 异步、OpenSearch 集成、recall_jobs、薪资解析

修复：
  - DB 连接池参数统一从 config/settings 读取
  - 新增 company_type 字段支持
  - recall_jobs 修复 filter 构建逻辑 + 薪资范围过滤
  - PG 降级查询也带偏好过滤
  - update_job 基于 asyncpg 重写
  - list_jobs 增加 title/company/keyword 筛选
  - job_profile JSONB 字段支持
"""
from __future__ import annotations

import logging
import os
import re
from typing import Any, Dict, List, Optional

import asyncpg
import json

from app.schemas.job import (
    JobCreate,
    JobUpdate,
    JobListResponse,
    JobResponse,
    MatchPreferences,
)
from app.utils.opensearch import (
    JOB_INDEX_MAPPINGS,
    OpenSearchClient,
    get_opensearch_client,
)

logger = logging.getLogger(__name__)

# ============================================================
# 数据库连接池
# ============================================================
_pool: Optional[asyncpg.Pool] = None


async def get_db_pool() -> asyncpg.Pool:
    """获取数据库连接池，参数从环境变量 / config 读取"""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            user=os.getenv("POSTGRES_USER", "career_user"),
            password=os.getenv("POSTGRES_PASSWORD", ""),
            database=os.getenv("POSTGRES_DB", "career_planning"),
            min_size=2,
            max_size=10,
        )
    return _pool


async def close_db_pool() -> None:
    """关闭数据库连接池"""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


# ============================================================
# 薪资解析工具
# ============================================================
def parse_salary_range(salary_range: Optional[str]) -> Optional[tuple]:
    """
    解析薪资范围字符串为 (min_k, max_k) 元组。

    支持格式：
      - "15K-25K", "15k-25k", "15-25K"
      - "8K-12K"
      - "面议" → None
    """
    if not salary_range:
        return None

    text = salary_range.upper().replace(" ", "")

    if "面议" in salary_range or "薪资" in salary_range:
        return None

    # 匹配 数字K-数字K 或 数字-数字K
    pattern = r"(\d+)\s*[K万]?\s*[-–—]\s*(\d+)\s*[K万]?"
    match = re.search(pattern, text)
    if match:
        low = int(match.group(1))
        high = int(match.group(2))
        if low < 100 and high < 100:
            return (low, high)
        return (low, high)

    # 匹配 "15K+" 或 "15K以上"
    pattern2 = r"(\d+)\s*K"
    match2 = re.search(pattern2, text)
    if match2:
        val = int(match2.group(1))
        return (val, val)

    return None


class JobService:
    """岗位业务服务"""

    def __init__(self, os_client: Optional[OpenSearchClient] = None) -> None:
        self._os = os_client

    @property
    def os_client(self) -> OpenSearchClient:
        if self._os is None:
            self._os = get_opensearch_client()
        return self._os

    # ----------------------------------------------------------
    # 岗位 CRUD
    # ----------------------------------------------------------
    async def create_job(self, data: JobCreate) -> JobResponse:
        """创建岗位（写入 PostgreSQL + OpenSearch）"""
        pool = await get_db_pool()
        job_profile_json = json.dumps(data.job_profile) if hasattr(data, 'job_profile') and data.job_profile else None

        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO jobs (title, company, industry, location, salary_range,
                    experience_required, education_required, description, requirements,
                    source, job_profile)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
                    CAST($11 AS jsonb))
                RETURNING id, title, company, industry, location, salary_range,
                    experience_required, education_required, description, requirements,
                    job_profile, status, source, created_at, updated_at
                """,
                data.title, data.company, data.industry, data.location,
                data.salary_range, data.experience_required, data.education_required,
                data.description, data.requirements, data.source,
                job_profile_json,
            )

        result = JobResponse(**dict(row), skills=data.skills, company_type=data.company_type)

        # 同步到 OpenSearch
        self._index_job_to_opensearch(result, data.skills)
        return result

    async def get_job(self, job_id: int) -> Optional[JobResponse]:
        """获取岗位详情"""
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, title, company, industry, location, salary_range, "
                "experience_required, education_required, description, requirements, "
                "job_profile, status, source, created_at FROM jobs WHERE id = $1",
                job_id,
            )
        if row is None:
            return None

        # 从 OpenSearch 获取 skills 和 company_type
        extra = await self._get_job_os_fields(job_id)
        return JobResponse(**dict(row), **extra)

    async def list_jobs(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        industry: Optional[str] = None,
        location: Optional[str] = None,
        title: Optional[str] = None,
        company: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> JobListResponse:
        """获取岗位列表（支持分页和多维筛选）"""
        pool = await get_db_pool()
        conditions = []
        params = []
        idx = 1

        if status:
            conditions.append(f"status = ${idx}")
            params.append(status)
            idx += 1
        if industry:
            conditions.append(f"industry = ${idx}")
            params.append(industry)
            idx += 1
        if location:
            conditions.append(f"location = ${idx}")
            params.append(location)
            idx += 1
        if title:
            conditions.append(f"title ILIKE ${idx}")
            params.append(f"%{title}%")
            idx += 1
        if company:
            conditions.append(f"company ILIKE ${idx}")
            params.append(f"%{company}%")
            idx += 1
        if keyword:
            conditions.append(f"(title ILIKE ${idx} OR company ILIKE ${idx} OR description ILIKE ${idx})")
            params.append(f"%{keyword}%")
            idx += 1

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        count_row = await pool.fetchrow(
            f"SELECT COUNT(*) as cnt FROM jobs {where_clause}", *params
        )
        total = count_row["cnt"]

        offset = (page - 1) * page_size
        rows = await pool.fetch(
            f"SELECT id, title, company, industry, location, salary_range, "
            f"experience_required, education_required, description, requirements, "
            f"job_profile, status, source, created_at FROM jobs {where_clause} "
            f"ORDER BY created_at DESC LIMIT {page_size} OFFSET {offset}",
            *params,
        )

        items = [JobResponse(**dict(r)) for r in rows]
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0

        return JobListResponse(
            total=total, items=items, page=page,
            page_size=page_size, total_pages=total_pages,
        )

    async def update_job(self, job_id: int, data: JobUpdate) -> Optional[JobResponse]:
        """更新岗位"""
        pool = await get_db_pool()

        # 先检查是否存在
        existing = await self.get_job(job_id)
        if not existing:
            return None

        update_fields = []
        params = []
        idx = 1

        field_map = {
            "title": data.title,
            "company": data.company,
            "industry": data.industry,
            "location": data.location,
            "salary_range": data.salary_range,
            "experience_required": data.experience_required,
            "education_required": data.education_required,
            "description": data.description,
            "requirements": data.requirements,
            "status": data.status,
            "source": data.source,
        }

        for field, value in field_map.items():
            if value is not None:
                update_fields.append(f"{field} = ${idx}")
                params.append(value)
                idx += 1

        # job_profile 单独处理（JSONB）
        if hasattr(data, 'job_profile') and data.job_profile is not None:
            update_fields.append(f"job_profile = CAST(${idx} AS jsonb)")
            params.append(json.dumps(data.job_profile))
            idx += 1

        if not update_fields:
            return existing

        params.append(job_id)  # WHERE id = $N
        where_idx = idx

        set_sql = ", ".join(update_fields)
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                f"UPDATE jobs SET {set_sql}, updated_at = NOW() "
                f"WHERE id = ${where_idx} "
                f"RETURNING id, title, company, industry, location, salary_range, "
                f"experience_required, education_required, description, requirements, "
                f"job_profile, status, source, created_at, updated_at",
                *params,
            )

        if row is None:
            return None

        # 同步更新 OpenSearch
        result = JobResponse(**dict(row))
        self._index_job_to_opensearch(result, data.skills if hasattr(data, 'skills') else None)
        return result

    async def delete_job(self, job_id: int) -> bool:
        """删除岗位"""
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            result = await conn.execute("DELETE FROM jobs WHERE id = $1", job_id)

        try:
            self.os_client.client.delete(index="jobs", id=str(job_id))
        except Exception as e:
            logger.warning(f"从 OpenSearch 删除岗位 {job_id} 失败: {e}")

        return result == "DELETE 1"

    # ----------------------------------------------------------
    # OpenSearch 索引操作
    # ----------------------------------------------------------
    def init_job_index(self) -> bool:
        """初始化岗位索引"""
        return self.os_client.create_index("jobs", JOB_INDEX_MAPPINGS)

    def _index_job_to_opensearch(self, job: JobResponse, skills: Optional[List[str]] = None) -> None:
        """将岗位写入 OpenSearch"""
        doc = {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "industry": job.industry,
            "location": job.location,
            "salary_range": job.salary_range,
            "experience_required": job.experience_required,
            "education_required": job.education_required,
            "description": job.description,
            "requirements": job.requirements,
            "skills": skills or [],
            "company_type": job.company_type,
            "status": job.status,
            "source": job.source,
        }
        self.os_client.index_document("jobs", str(job.id), doc)

    async def _get_job_os_fields(self, job_id: int) -> Dict[str, Any]:
        """从 OpenSearch 获取岗位的 skills/company_type 等扩展字段"""
        doc = self.os_client.get_document("jobs", str(job_id))
        if doc:
            return {
                "skills": doc.get("skills"),
                "company_type": doc.get("company_type"),
            }
        return {}

    # ----------------------------------------------------------
    # 岗位检索（召回阶段）
    # ----------------------------------------------------------
    async def recall_jobs(
        self,
        keywords: Optional[List[str]] = None,
        preferences: Optional[MatchPreferences] = None,
        size: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        岗位召回：基于关键词 + 用户偏好从 OpenSearch 检索候选岗位

        策略：
          1. 关键词 multi_match 搜索
          2. 偏好过滤（industry, location, salary, education, company_type）
          3. 只查活跃岗位
        """
        if not self.os_client.is_initialized:
            # OpenSearch 未初始化，走 PG 降级
            return await self._recall_jobs_from_pg(preferences, size)

        must = []
        filters = [{"term": {"status": "active"}}]  # 始终过滤活跃岗位

        # 关键词召回
        if keywords:
            keyword_text = " ".join(keywords)
            must.append({
                "multi_match": {
                    "query": keyword_text,
                    "fields": ["title^3", "description^2", "requirements", "skills"],
                    "type": "best_fields",
                    "fuzziness": "AUTO",
                }
            })
        else:
            must.append({"match_all": {}})

        # 偏好过滤
        if preferences:
            if preferences.industries:
                filters.append({"terms": {"industry": preferences.industries}})
            if preferences.cities:
                filters.append({"terms": {"location": preferences.cities}})
            if preferences.education:
                filters.append({"term": {"education_required": preferences.education}})
            if preferences.experience:
                filters.append({"term": {"experience_required": preferences.experience}})
            if preferences.company_types:
                filters.append({"terms": {"company_type": preferences.company_types}})

        query = {"bool": {"must": must, "filter": filters}}
        result = self.os_client.search("jobs", query, size=size)
        candidates = self.os_client.parse_search_results(result)

        # 如果 OpenSearch 无结果，尝试 PG 降级
        if not candidates:
            candidates = await self._recall_jobs_from_pg(preferences, size)

        # 薪资过滤（在内存中做，因为 salary_range 是文本格式）
        if preferences and (preferences.salary_min is not None or preferences.salary_max is not None):
            candidates = self._filter_by_salary(candidates, preferences)

        return candidates

    async def _recall_jobs_from_pg(
        self,
        preferences: Optional[MatchPreferences] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """PG 降级查询"""
        try:
            pool = await get_db_pool()
            conditions = ["status = 'active'"]
            params = []
            idx = 1

            if preferences:
                if preferences.industries:
                    conditions.append(f"industry = ANY(${idx})")
                    params.append(preferences.industries)
                    idx += 1
                if preferences.cities:
                    conditions.append(f"location = ANY(${idx})")
                    params.append(preferences.cities)
                    idx += 1

            where = " AND ".join(conditions)
            rows = await pool.fetch(
                f"SELECT id, title, company, industry, location, salary_range, "
                f"experience_required, education_required, description, requirements "
                f"FROM jobs WHERE {where} ORDER BY created_at DESC LIMIT {limit}",
                *params,
            )
            return [dict(r) for r in rows]
        except Exception as e:
            logger.error(f"PG 降级查询失败: {e}")
            return []

    def _filter_by_salary(
        self,
        candidates: List[Dict[str, Any]],
        preferences: MatchPreferences,
    ) -> List[Dict[str, Any]]:
        """根据薪资偏好过滤候选岗位"""
        filtered = []
        for c in candidates:
            salary = parse_salary_range(c.get("salary_range"))
            if salary is None:
                # 无法解析薪资的岗位保留，但在打分时降低偏好分
                filtered.append(c)
                continue

            job_min, job_max = salary

            # 岗位薪资范围与用户期望有交集即可
            if preferences.salary_min is not None and job_max < preferences.salary_min:
                continue
            if preferences.salary_max is not None and job_min > preferences.salary_max:
                continue

            filtered.append(c)

        return filtered

    async def get_jobs_by_ids(self, job_ids: List[int]) -> List[JobResponse]:
        """根据 ID 列表批量获取岗位"""
        if not job_ids:
            return []
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT id, title, company, industry, location, salary_range, "
                "experience_required, education_required, description, requirements, "
                "job_profile, status, source, created_at FROM jobs WHERE id = ANY($1)",
                job_ids,
            )
        return [JobResponse(**dict(r)) for r in rows]


# 单例
job_service = JobService()
