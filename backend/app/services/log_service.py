"""
日志查询与写入业务逻辑层
"""
import json
from typing import Optional, List
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.log import LogResponse, LogListResponse


class LogService:
    """日志服务"""

    def __init__(self, db: Session):
        self.db = db

    # ==================== 写入日志 ====================
    def create_log(
        self,
        user_id: Optional[int],
        action: str,
        module: str,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None
    ) -> None:
        """写入一条日志"""
        details_json = json.dumps(details) if details else '{}'

        query = text("""
            INSERT INTO logs (user_id, action, module, details, ip_address, created_at)
            VALUES (:user_id, :action, :module, CAST(:details AS jsonb), :ip_address, NOW())
        """)

        self.db.execute(query, {
            "user_id": user_id,
            "action": action,
            "module": module,
            "details": details_json,
            "ip_address": ip_address
        })
        self.db.commit()

    # ==================== 查询日志列表（分页 + 筛选） ====================
    def get_logs(
        self,
        page: int = 1,
        page_size: int = 20,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        module: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> LogListResponse:
        """获取日志列表（支持分页和筛选）"""
        where_clauses = ["1=1"]
        params = {}

        if user_id is not None:
            where_clauses.append("user_id = :user_id")
            params["user_id"] = user_id
        if action:
            where_clauses.append("action = :action")
            params["action"] = action
        if module:
            where_clauses.append("module = :module")
            params["module"] = module
        if start_date:
            where_clauses.append("created_at >= :start_date")
            params["start_date"] = start_date
        if end_date:
            where_clauses.append("created_at <= :end_date")
            params["end_date"] = end_date
        if keyword:
            where_clauses.append("(details::text ILIKE :keyword OR action ILIKE :keyword OR module ILIKE :keyword)")
            params["keyword"] = f"%{keyword}%"

        where_sql = " AND ".join(where_clauses)

        # 查询总数
        count_query = text(f"""
            SELECT COUNT(*) FROM logs WHERE {where_sql}
        """)
        total_result = self.db.execute(count_query, params)
        total = total_result.scalar()

        # 查询数据（分页）
        offset = (page - 1) * page_size
        query = text(f"""
            SELECT 
                id, user_id, action, module, details, ip_address, created_at
            FROM logs
            WHERE {where_sql}
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """)
        params["limit"] = page_size
        params["offset"] = offset

        result = self.db.execute(query, params)
        rows = result.fetchall()

        items = [
            LogResponse(
                id=row[0],
                user_id=row[1],
                action=row[2],
                module=row[3],
                details=row[4],
                ip_address=row[5],
                created_at=row[6]
            )
            for row in rows
        ]

        total_pages = (total + page_size - 1) // page_size if total > 0 else 0

        return LogListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    # ==================== 查询单条日志 ====================
    def get_log_by_id(self, log_id: int) -> Optional[LogResponse]:
        """根据 ID 获取日志详情"""
        query = text("""
            SELECT 
                id, user_id, action, module, details, ip_address, created_at
            FROM logs
            WHERE id = :id
        """)

        result = self.db.execute(query, {"id": log_id})
        row = result.fetchone()

        if not row:
            return None

        return LogResponse(
            id=row[0],
            user_id=row[1],
            action=row[2],
            module=row[3],
            details=row[4],
            ip_address=row[5],
            created_at=row[6]
        )