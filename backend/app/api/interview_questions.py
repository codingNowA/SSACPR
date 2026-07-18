"""
面试题目获取 API 路由
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from app.services.job_service import get_db_pool

router = APIRouter(prefix="/api/v1/interview-exam", tags=["模拟面试"])


@router.get("/questions")
async def get_exam_questions(
    count: int = Query(10, ge=1, le=50, description="题目数量"),
    category: Optional[str] = Query(None, description="题目分类"),
    difficulty: Optional[str] = Query(None, description="难度等级"),
):
    """
    获取随机面试考试题目

    题库不足时返回实际可用数量，不报错
    """
    try:
        pool = await get_db_pool()

        where_clauses = []
        params = []
        idx = 1

        if category:
            where_clauses.append(f"category = ${idx}")
            params.append(category)
            idx += 1
        if difficulty:
            where_clauses.append(f"difficulty = ${idx}")
            params.append(difficulty)
            idx += 1

        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

        async with pool.acquire() as conn:
            rows = await conn.fetch(
                f"""
                SELECT id, category, difficulty, question, answer_points
                FROM interview_questions
                WHERE {where_sql}
                ORDER BY RANDOM()
                LIMIT ${idx}
                """,
                *params, count
            )

        result = []
        for i, row in enumerate(rows, 1):
            result.append({
                "id": row["id"],
                "question_number": i,
                "question": row["question"],
                "category": row["category"] or "未分类",
                "difficulty": row["difficulty"] or "medium",
                "reference_answer": row["answer_points"] or "",
            })

        return {"questions": result, "total": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取题目失败: {str(e)}")


@router.get("/questions/list")
async def list_questions(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    category: Optional[str] = Query(None, description="题目分类"),
    difficulty: Optional[str] = Query(None, description="难度等级"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
):
    """
    分页浏览面试题库（用于题库浏览页面）

    支持分类、难度、关键词筛选
    """
    try:
        pool = await get_db_pool()

        where_clauses = []
        params = []
        idx = 1

        if category:
            where_clauses.append(f"category = ${idx}")
            params.append(category)
            idx += 1
        if difficulty:
            where_clauses.append(f"difficulty = ${idx}")
            params.append(difficulty)
            idx += 1
        if keyword:
            where_clauses.append(f"(question ILIKE ${idx} OR answer_points ILIKE ${idx})")
            params.append(f"%{keyword}%")
            idx += 1

        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

        async with pool.acquire() as conn:
            # 总数
            total = await conn.fetchval(
                f"SELECT COUNT(*) FROM interview_questions WHERE {where_sql}",
                *params
            )

            # 分页数据
            offset = (page - 1) * page_size
            rows = await conn.fetch(
                f"""
                SELECT id, category, difficulty, question, answer_points, created_at
                FROM interview_questions
                WHERE {where_sql}
                ORDER BY created_at DESC
                LIMIT ${idx} OFFSET ${idx + 1}
                """,
                *params, page_size, offset
            )

        items = []
        for row in rows:
            items.append({
                "id": row["id"],
                "category": row["category"] or "未分类",
                "difficulty": row["difficulty"] or "medium",
                "question": row["question"],
                "reference_answer": row["answer_points"] or "",
                "created_at": str(row["created_at"]) if row["created_at"] else "",
            })

        total_pages = (total + page_size - 1) // page_size if total > 0 else 0

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取题库列表失败: {str(e)}")
