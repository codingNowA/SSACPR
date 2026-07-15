"""
岗位数据管理业务逻辑层（同步 SQLAlchemy 版，供 /api/v1/admin/jobs 使用）

注意：本类与 app.services.job_service.JobService（异步 + OpenSearch 召回）不同，
后者服务于 /api/v1/job 的匹配召回；此处仅负责后台岗位的 CRUD。
"""
from typing import Optional
import json
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.job import JobCreate, JobUpdate, JobResponse, JobListResponse

# 与 jobs 表结构一致的返回列
_SELECT_COLUMNS = (
    "id, title, company, industry, location, salary_range, "
    "experience_required, education_required, description, requirements, "
    "job_profile, status, source, created_at, updated_at"
)


def _row_to_response(row) -> JobResponse:
    return JobResponse(
        id=row[0],
        title=row[1],
        company=row[2],
        industry=row[3],
        location=row[4],
        salary_range=row[5],
        experience_required=row[6],
        education_required=row[7],
        description=row[8],
        requirements=row[9],
        job_profile=row[10] if row[10] else None,
        status=row[11],
        source=row[12],
        created_at=row[13],
        updated_at=row[14],
    )


class JobAdminService:
    """后台岗位管理服务（同步）"""

    def __init__(self, db: Session):
        self.db = db

    # ==================== 创建岗位 ====================
    def create_job(self, data: JobCreate) -> JobResponse:
        profile_json = json.dumps(data.job_profile) if data.job_profile is not None else None

        query = text(f"""
            INSERT INTO jobs
                (title, company, industry, location, salary_range,
                 experience_required, education_required, description, requirements,
                 job_profile, status, source, created_at, updated_at)
            VALUES
                (:title, :company, :industry, :location, :salary_range,
                 :experience_required, :education_required, :description, :requirements,
                 CAST(:job_profile AS jsonb), :status, :source, NOW(), NOW())
            RETURNING {_SELECT_COLUMNS}
        """)

        result = self.db.execute(query, {
            "title": data.title,
            "company": data.company,
            "industry": data.industry,
            "location": data.location,
            "salary_range": data.salary_range,
            "experience_required": data.experience_required,
            "education_required": data.education_required,
            "description": data.description,
            "requirements": data.requirements,
            "job_profile": profile_json,
            "status": data.status or "active",
            "source": data.source,
        })
        self.db.commit()
        return _row_to_response(result.fetchone())

    # ==================== 查询岗位列表 ====================
    def get_jobs(
        self,
        page: int = 1,
        page_size: int = 20,
        title: Optional[str] = None,
        company: Optional[str] = None,
        industry: Optional[str] = None,
        location: Optional[str] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> JobListResponse:
        where_clauses = []
        params = {}

        if title:
            where_clauses.append("title ILIKE :title")
            params["title"] = f"%{title}%"
        if company:
            where_clauses.append("company ILIKE :company")
            params["company"] = f"%{company}%"
        if industry:
            where_clauses.append("industry = :industry")
            params["industry"] = industry
        if location:
            where_clauses.append("location = :location")
            params["location"] = location
        if status:
            where_clauses.append("status = :status")
            params["status"] = status
        if keyword:
            where_clauses.append(
                "(title ILIKE :keyword OR company ILIKE :keyword OR description ILIKE :keyword)"
            )
            params["keyword"] = f"%{keyword}%"

        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

        count_query = text(f"SELECT COUNT(*) FROM jobs WHERE {where_sql}")
        total = self.db.execute(count_query, params).scalar() or 0

        offset = (page - 1) * page_size
        query = text(f"""
            SELECT {_SELECT_COLUMNS}
            FROM jobs
            WHERE {where_sql}
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """)
        params["limit"] = page_size
        params["offset"] = offset

        rows = self.db.execute(query, params).fetchall()
        items = [_row_to_response(row) for row in rows]

        total_pages = (total + page_size - 1) // page_size if total > 0 else 0

        return JobListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    # ==================== 查询单个岗位 ====================
    def get_job_by_id(self, job_id: int) -> Optional[JobResponse]:
        query = text(f"SELECT {_SELECT_COLUMNS} FROM jobs WHERE id = :id")
        row = self.db.execute(query, {"id": job_id}).fetchone()
        if not row:
            return None
        return _row_to_response(row)

    # ==================== 更新岗位 ====================
    def update_job(self, job_id: int, data: JobUpdate) -> Optional[JobResponse]:
        existing = self.get_job_by_id(job_id)
        if not existing:
            return None

        update_fields = []
        params = {"id": job_id}

        simple_fields = [
            "title", "company", "industry", "location", "salary_range",
            "experience_required", "education_required", "description",
            "requirements", "status", "source",
        ]
        for field in simple_fields:
            value = getattr(data, field, None)
            if value is not None:
                update_fields.append(f"{field} = :{field}")
                params[field] = value

        if data.job_profile is not None:
            update_fields.append("job_profile = CAST(:job_profile AS jsonb)")
            params["job_profile"] = json.dumps(data.job_profile)

        if not update_fields:
            return existing

        update_fields.append("updated_at = NOW()")
        update_sql = ", ".join(update_fields)
        query = text(f"""
            UPDATE jobs
            SET {update_sql}
            WHERE id = :id
            RETURNING {_SELECT_COLUMNS}
        """)

        result = self.db.execute(query, params)
        self.db.commit()
        return _row_to_response(result.fetchone())

    # ==================== 删除岗位 ====================
    def delete_job(self, job_id: int) -> bool:
        query = text("DELETE FROM jobs WHERE id = :id")
        result = self.db.execute(query, {"id": job_id})
        self.db.commit()
        return result.rowcount > 0
