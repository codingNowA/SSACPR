"""
词库与权重配置业务逻辑层
"""
from typing import Optional, List
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.dictionary import DictionaryCreate, DictionaryUpdate, DictionaryResponse, DictionaryListResponse


class DictionaryService:
    """词库服务"""

    def __init__(self, db: Session):
        self.db = db

    # ==================== 创建词条 ====================
    def create_dictionary(self, data: DictionaryCreate) -> DictionaryResponse:
        query = text("""
            INSERT INTO dictionaries (word, type, weight, description, created_at, updated_at)
            VALUES (:word, :type, :weight, :description, NOW(), NOW())
            RETURNING id, word, type, weight, description, created_at, updated_at
        """)

        result = self.db.execute(query, {
            "word": data.word,
            "type": data.type,
            "weight": data.weight,
            "description": data.description
        })
        self.db.commit()
        row = result.fetchone()

        return DictionaryResponse(
            id=row[0],
            word=row[1],
            type=row[2],
            weight=row[3],
            description=row[4],
            created_at=row[5],
            updated_at=row[6]
        )

    # ==================== 查询词条列表 ====================
    def get_dictionaries(
        self,
        page: int = 1,
        page_size: int = 20,
        type: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> DictionaryListResponse:
        where_clauses = ["1=1"]
        params = {}

        if type:
            where_clauses.append("type = :type")
            params["type"] = type
        if keyword:
            where_clauses.append("(word ILIKE :keyword OR description ILIKE :keyword)")
            params["keyword"] = f"%{keyword}%"

        where_sql = " AND ".join(where_clauses)

        count_query = text(f"""
            SELECT COUNT(*) FROM dictionaries WHERE {where_sql}
        """)
        total_result = self.db.execute(count_query, params)
        total = total_result.scalar()

        offset = (page - 1) * page_size
        query = text(f"""
            SELECT id, word, type, weight, description, created_at, updated_at
            FROM dictionaries
            WHERE {where_sql}
            ORDER BY type, word
            LIMIT :limit OFFSET :offset
        """)
        params["limit"] = page_size
        params["offset"] = offset

        result = self.db.execute(query, params)
        rows = result.fetchall()

        items = [
            DictionaryResponse(
                id=row[0],
                word=row[1],
                type=row[2],
                weight=row[3],
                description=row[4],
                created_at=row[5],
                updated_at=row[6]
            )
            for row in rows
        ]

        total_pages = (total + page_size - 1) // page_size if total > 0 else 0

        return DictionaryListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    # ==================== 查询单个词条 ====================
    def get_dictionary_by_id(self, dict_id: int) -> Optional[DictionaryResponse]:
        query = text("""
            SELECT id, word, type, weight, description, created_at, updated_at
            FROM dictionaries
            WHERE id = :id
        """)

        result = self.db.execute(query, {"id": dict_id})
        row = result.fetchone()

        if not row:
            return None

        return DictionaryResponse(
            id=row[0],
            word=row[1],
            type=row[2],
            weight=row[3],
            description=row[4],
            created_at=row[5],
            updated_at=row[6]
        )

    # ==================== 更新词条 ====================
    def update_dictionary(self, dict_id: int, data: DictionaryUpdate) -> Optional[DictionaryResponse]:
        existing = self.get_dictionary_by_id(dict_id)
        if not existing:
            return None

        update_fields = []
        params = {"id": dict_id}

        if data.word is not None:
            update_fields.append("word = :word")
            params["word"] = data.word
        if data.type is not None:
            update_fields.append("type = :type")
            params["type"] = data.type
        if data.weight is not None:
            update_fields.append("weight = :weight")
            params["weight"] = data.weight
        if data.description is not None:
            update_fields.append("description = :description")
            params["description"] = data.description

        if not update_fields:
            return existing

        update_fields.append("updated_at = NOW()")
        update_sql = ", ".join(update_fields)

        query = text(f"""
            UPDATE dictionaries
            SET {update_sql}
            WHERE id = :id
            RETURNING id, word, type, weight, description, created_at, updated_at
        """)

        result = self.db.execute(query, params)
        self.db.commit()
        row = result.fetchone()

        return DictionaryResponse(
            id=row[0],
            word=row[1],
            type=row[2],
            weight=row[3],
            description=row[4],
            created_at=row[5],
            updated_at=row[6]
        )

    # ==================== 删除词条 ====================
    def delete_dictionary(self, dict_id: int) -> bool:
        query = text("DELETE FROM dictionaries WHERE id = :id")
        result = self.db.execute(query, {"id": dict_id})
        self.db.commit()
        return result.rowcount > 0