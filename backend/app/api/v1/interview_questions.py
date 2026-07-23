"""
面试题目接口 - 随机抽取 + 分页浏览
"""
import json
import logging
from fastapi import APIRouter, Query

from app.services.job_service import get_db_pool

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/interview-exam", tags=["面试题库"])


@router.get("/questions", summary="随机抽取面试题")
async def get_random_questions(
    count: int = Query(10, ge=1, le=100, description="抽取数量"),
):
    """随机抽取面试题，题不足时返回实际数量不报错"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT id, category, question, answer_points, related_skills, difficulty, created_at FROM interview_questions ORDER BY RANDOM() LIMIT $1",
            count,
        )
    result = []
    for r in rows:
        item = {
            "id": r["id"],
            "category": r["category"],
            "question_text": r["question"],
            "difficulty": r["difficulty"],
            "answer_points": r["answer_points"],
        }
        if r["related_skills"]:
            try:
                item["related_skills"] = json.loads(r["related_skills"]) if isinstance(r["related_skills"], str) else r["related_skills"]
            except (json.JSONDecodeError, TypeError):
                item["related_skills"] = []
        else:
            item["related_skills"] = []
        result.append(item)
    return {"data": result, "total": len(result)}


@router.get("/questions/list", summary="分页浏览面试题")
async def list_questions(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    category: str = Query(None, description="按类别筛选"),
    difficulty: str = Query(None, description="按难度筛选"),
):
    """分页浏览面试题库"""
    pool = await get_db_pool()

    conditions = []
    params = []
    idx = 1

    if category:
        conditions.append(f"category = ${idx}")
        params.append(category)
        idx += 1
    if difficulty:
        conditions.append(f"difficulty = ${idx}")
        params.append(difficulty)
        idx += 1

    where_clause = (" WHERE " + " AND ".join(conditions)) if conditions else ""

    async with pool.acquire() as conn:
        total = await conn.fetchval(
            f"SELECT COUNT(*) FROM interview_questions{where_clause}", *params
        )
        offset = (page - 1) * page_size
        rows = await conn.fetch(
            f"SELECT id, category, question, answer_points, related_skills, difficulty, created_at FROM interview_questions{where_clause} ORDER BY id DESC LIMIT ${idx} OFFSET ${idx+1}",
            *params, page_size, offset
        )

    result = []
    for r in rows:
        item = {
            "id": r["id"],
            "category": r["category"],
            "question_text": r["question"],
            "difficulty": r["difficulty"],
            "answer_points": r["answer_points"],
            "created_at": str(r["created_at"]) if r.get("created_at") else None,
        }
        if r["related_skills"]:
            try:
                item["related_skills"] = json.loads(r["related_skills"]) if isinstance(r["related_skills"], str) else r["related_skills"]
            except (json.JSONDecodeError, TypeError):
                item["related_skills"] = []
        else:
            item["related_skills"] = []
        result.append(item)

    return {
        "data": result,
        "total": total or 0,
        "page": page,
        "page_size": page_size,
    }
