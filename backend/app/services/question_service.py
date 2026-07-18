"""
题库管理业务逻辑层
"""
from typing import Optional, List
import json
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.question import QuestionCreate, QuestionUpdate, QuestionResponse, QuestionListResponse


class QuestionService:
    """题库管理服务"""

    def __init__(self, db: Session):
        self.db = db

    # ==================== 创建题目 ====================
    def create_question(self, data: QuestionCreate) -> QuestionResponse:
        skills_json = json.dumps(data.related_skills) if data.related_skills else '[]'

        query = text("""
            INSERT INTO interview_questions 
                (category, difficulty, question, answer_points, related_skills, created_at)
            VALUES 
                (:category, :difficulty, :question, :answer_points, CAST(:related_skills AS jsonb), NOW())
            RETURNING id, category, difficulty, question, answer_points, related_skills, created_at
        """)

        result = self.db.execute(query, {
            "category": data.category,
            "difficulty": data.difficulty,
            "question": data.question,
            "answer_points": data.answer_points,
            "related_skills": skills_json
        })
        self.db.commit()
        row = result.fetchone()

        return QuestionResponse(
            id=row[0],
            category=row[1],
            difficulty=row[2],
            question=row[3],
            answer_points=row[4],
            related_skills=row[5] if row[5] else [],
            created_at=row[6]
        )

    # ==================== 查询题目列表 ====================
    def get_questions(
        self,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> QuestionListResponse:
        where_clauses = []
        params = {}

        if category:
            where_clauses.append("category = :category")
            params["category"] = category
        if difficulty:
            where_clauses.append("difficulty = :difficulty")
            params["difficulty"] = difficulty
        if keyword:
            where_clauses.append("(question ILIKE :keyword OR answer_points ILIKE :keyword)")
            params["keyword"] = f"%{keyword}%"

        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

        count_query = text(f"""
            SELECT COUNT(*) FROM interview_questions WHERE {where_sql}
        """)
        total_result = self.db.execute(count_query, params)
        total = total_result.scalar()

        offset = (page - 1) * page_size
        query = text(f"""
            SELECT 
                id, category, difficulty, question, answer_points, related_skills, created_at
            FROM interview_questions
            WHERE {where_sql}
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """)
        params["limit"] = page_size
        params["offset"] = offset

        result = self.db.execute(query, params)
        rows = result.fetchall()

        items = [
            QuestionResponse(
                id=row[0],
                category=row[1],
                difficulty=row[2],
                question=row[3],
                answer_points=row[4],
                related_skills=row[5] if row[5] else [],
                created_at=row[6]
            )
            for row in rows
        ]

        total_pages = (total + page_size - 1) // page_size if total > 0 else 0

        return QuestionListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    # ==================== 查询单道题目 ====================
    def get_question_by_id(self, question_id: int) -> Optional[QuestionResponse]:
        query = text("""
            SELECT id, category, difficulty, question, answer_points, related_skills, created_at
            FROM interview_questions
            WHERE id = :id
        """)

        result = self.db.execute(query, {"id": question_id})
        row = result.fetchone()

        if not row:
            return None

        return QuestionResponse(
            id=row[0],
            category=row[1],
            difficulty=row[2],
            question=row[3],
            answer_points=row[4],
            related_skills=row[5] if row[5] else [],
            created_at=row[6]
        )

    # ==================== 更新题目 ====================
    def update_question(self, question_id: int, data: QuestionUpdate) -> Optional[QuestionResponse]:
        existing = self.get_question_by_id(question_id)
        if not existing:
            return None

        update_fields = []
        params = {"id": question_id}

        if data.category is not None:
            update_fields.append("category = :category")
            params["category"] = data.category
        if data.difficulty is not None:
            update_fields.append("difficulty = :difficulty")
            params["difficulty"] = data.difficulty
        if data.question is not None:
            update_fields.append("question = :question")
            params["question"] = data.question
        if data.answer_points is not None:
            update_fields.append("answer_points = :answer_points")
            params["answer_points"] = data.answer_points
        if data.related_skills is not None:
            # 使用 CAST(:related_skills AS jsonb) 代替 :: 语法
            update_fields.append("related_skills = CAST(:related_skills AS jsonb)")
            params["related_skills"] = json.dumps(data.related_skills)

        if not update_fields:
            return existing

        update_sql = ", ".join(update_fields)
        query = text(f"""
            UPDATE interview_questions
            SET {update_sql}
            WHERE id = :id
            RETURNING id, category, difficulty, question, answer_points, related_skills, created_at
        """)

        result = self.db.execute(query, params)
        self.db.commit()
        row = result.fetchone()

        return QuestionResponse(
            id=row[0],
            category=row[1],
            difficulty=row[2],
            question=row[3],
            answer_points=row[4],
            related_skills=row[5] if row[5] else [],
            created_at=row[6]
        )

    # ==================== 删除题目 ====================
    def delete_question(self, question_id: int) -> bool:
        query = text("DELETE FROM interview_questions WHERE id = :id")
        result = self.db.execute(query, {"id": question_id})
        self.db.commit()
        return result.rowcount > 0
    # ==================== 获取随机题目（用于面试考试）====================
    async def get_random_questions(
        self,
        count: int = 10,
        category: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> List[dict]:
        """
        获取随机题目用于面试考试

        Args:
            count: 需要的题目数量
            category: 题目分类筛选
            difficulty: 难度筛选

        Returns:
            题目列表
        """
        where_clauses = []
        params = {"count": count}

        if category:
            where_clauses.append("category = :category")
            params["category"] = category
        if difficulty:
            where_clauses.append("difficulty = :difficulty")
            params["difficulty"] = difficulty

        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

        query = text(f"""
            SELECT
                id, category, difficulty, question, answer_points, related_skills
            FROM interview_questions
            WHERE {where_sql}
            ORDER BY RANDOM()
            LIMIT :count
        """)

        result = self.db.execute(query, params)
        rows = result.fetchall()

        return [
            {
                "id": row[0],
                "category": row[1],
                "difficulty": row[2],
                "question": row[3],
                "answer_points": row[4],
                "related_skills": row[5] if row[5] else []
            }
            for row in rows
        ]
