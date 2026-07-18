"""
面试题目获取 API 路由
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.question_service import QuestionService

router = APIRouter(prefix="/api/v1/interview-exam", tags=["模拟面试"])


@router.get("/questions")
async def get_exam_questions(
    count: int = Query(10, ge=1, le=50, description="题目数量"),
    category: Optional[str] = Query(None, description="题目分类"),
    difficulty: Optional[str] = Query(None, description="难度等级"),
    db: Session = Depends(get_db)
):
    """
    获取面试考试题目

    返回指定数量的随机题目，用于模拟面试
    """
    try:
        question_service = QuestionService(db)
        questions = await question_service.get_random_questions(
            count=count,
            category=category,
            difficulty=difficulty,
        )

        if len(questions) < count:
            raise HTTPException(
                status_code=400,
                detail=f"题库题目不足，需要 {count} 道题，实际只有 {len(questions)} 道"
            )

        # 转换为前端需要的格式
        result = []
        for idx, q in enumerate(questions, 1):
            result.append({
                "id": q["id"],
                "question_number": idx,
                "question": q["question"],
                "category": q.get("category", "未分类"),
                "difficulty": q.get("difficulty", "medium"),
                "reference_answer": q.get("answer_points", ""),
            })

        return {"questions": result, "total": len(result)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取题目失败: {str(e)}"
        )
