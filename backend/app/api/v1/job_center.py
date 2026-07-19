"""
岗位中心 - 用户端浏览岗位（不需要认证）
"""
import logging
from fastapi import APIRouter, Query

from app.services.job_service import get_db_pool

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["岗位中心"])


@router.get("/center", summary="岗位中心列表")
async def job_center(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: str = Query(None, description="关键词搜索"),
    industry: str = Query(None, description="行业筛选"),
    location: str = Query(None, description="城市筛选"),
    sort_by: str = Query("created_at", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向 asc/desc"),
):
    """岗位中心 - 分页浏览、搜索、筛选"""
    pool = await get_db_pool()

    conditions = []
    params = []
    idx = 1

    if keyword:
        conditions.append(f"(title ILIKE ${idx} OR company ILIKE ${idx} OR description ILIKE ${idx})")
        params.append(f"%{keyword}%")
        idx += 1
    if industry:
        conditions.append(f"industry = ${idx}")
        params.append(industry)
        idx += 1
    if location:
        conditions.append(f"location = ${idx}")
        params.append(location)
        idx += 1

    where_clause = (" WHERE " + " AND ".join(conditions)) if conditions else ""

    # 安全排序
    allowed_sort = {"created_at", "title", "salary_range", "experience_required"}
    if sort_by not in allowed_sort:
        sort_by = "created_at"
    order_dir = "ASC" if sort_order.lower() == "asc" else "DESC"

    async with pool.acquire() as conn:
        total = await conn.fetchval(
            f"SELECT COUNT(*) FROM jobs{where_clause}", *params
        )
        offset = (page - 1) * page_size
        rows = await conn.fetch(
            f"SELECT id, title, company, location, industry, salary_range, experience_required, education_required, description, requirements, status, created_at FROM jobs{where_clause} ORDER BY {sort_by} {order_dir} LIMIT ${idx} OFFSET ${idx+1}",
            *params, page_size, offset
        )

    result = []
    for r in rows:
        result.append({
            "id": r["id"],
            "title": r["title"],
            "company": r["company"],
            "location": r["location"],
            "industry": r["industry"],
            "salary_range": r["salary_range"],
            "experience_required": r["experience_required"],
            "education_required": r["education_required"],
            "description": r["description"],
            "requirements": r["requirements"],
            "status": r["status"],
            "created_at": str(r["created_at"]) if r.get("created_at") else None,
        })

    return {
        "data": result,
        "total": total or 0,
        "page": page,
        "page_size": page_size,
    }
