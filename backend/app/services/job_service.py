"""
岗位数据管理业务逻辑层
"""
from typing import Optional, List
import json
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.job import JobCreate, JobUpdate, JobResponse, JobListResponse


class JobService:
    """岗位管理服务"""

    def __init__(self, db: Session):
        self.db = db

    # ==================== 创建岗位 ====================
    def create_job(self, data: JobCreate) -> JobResponse:
        """新增一个岗位"""
        job_profile_json = json.dumps(data.job_profile) if data.job_profile else '{}'

        query = text("""
            INSERT INTO jobs 
                (title, company, industry, location, salary_range, 
                 experience_required, education_required, description, 
                 requirements, job_profile, status, source, created_at, updated_at)
            VALUES 
                (:title, :company, :industry, :location, :salary_range,
                 :experience_required, :education_required, :description,
                 :requirements, CAST(:job_profile AS jsonb), :status, :source, NOW(), NOW())
            RETURNING 
                id, title, company, industry, location, salary_range,
                experience_required, education_required, description,
                requirements, job_profile, status, source, created_at, updated_at
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
            "job_profile": job_profile_json,
            "status": data.status or "active",
            "source": data.source
        })
        self.db.commit()
        row = result.fetchone()

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
            job_profile=row[10],
            status=row[11],
            source=row[12],
            created_at=row[13],
            updated_at=row[14]
        )

    # ==================== 查询岗位列表（分页 + 筛选） ====================
    def get_jobs(
        self,
        page: int = 1,
        page_size: int = 20,
        title: Optional[str] = None,
        company: Optional[str] = None,
        industry: Optional[str] = None,
        location: Optional[str] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> JobListResponse:
        """获取岗位列表（支持分页和筛选）"""
        where_clauses = ["1=1"]
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
            where_clauses.append("(title ILIKE :keyword OR company ILIKE :keyword OR description ILIKE :keyword)")
            params["keyword"] = f"%{keyword}%"

        where_sql = " AND ".join(where_clauses)

        # 查询总数
        count_query = text(f"""
            SELECT COUNT(*) FROM jobs WHERE {where_sql}
        """)
        total_result = self.db.execute(count_query, params)
        total = total_result.scalar()

        # 查询数据（分页）
        offset = (page - 1) * page_size
        query = text(f"""
            SELECT 
                id, title, company, industry, location, salary_range,
                experience_required, education_required, description,
                requirements, job_profile, status, source, created_at, updated_at
            FROM jobs
            WHERE {where_sql}
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """)
        params["limit"] = page_size
        params["offset"] = offset

        result = self.db.execute(query, params)
        rows = result.fetchall()

        items = [
            JobResponse(
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
                job_profile=row[10],
                status=row[11],
                source=row[12],
                created_at=row[13],
                updated_at=row[14]
            )
            for row in rows
        ]

        total_pages = (total + page_size - 1) // page_size if total > 0 else 0

        return JobListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    # ==================== 查询单个岗位 ====================
    def get_job_by_id(self, job_id: int) -> Optional[JobResponse]:
        """根据 ID 获取岗位详情"""
        query = text("""
            SELECT 
                id, title, company, industry, location, salary_range,
                experience_required, education_required, description,
                requirements, job_profile, status, source, created_at, updated_at
            FROM jobs
            WHERE id = :id
        """)

        result = self.db.execute(query, {"id": job_id})
        row = result.fetchone()

        if not row:
            return None

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
            job_profile=row[10],
            status=row[11],
            source=row[12],
            created_at=row[13],
            updated_at=row[14]
        )

    # ==================== 更新岗位 ====================
    def update_job(self, job_id: int, data: JobUpdate) -> Optional[JobResponse]:
        """更新岗位"""
        existing = self.get_job_by_id(job_id)
        if not existing:
            return None

        update_fields = []
        params = {"id": job_id}

        if data.title is not None:
            update_fields.append("title = :title")
            params["title"] = data.title
        if data.company is not None:
            update_fields.append("company = :company")
            params["company"] = data.company
        if data.industry is not None:
            update_fields.append("industry = :industry")
            params["industry"] = data.industry
        if data.location is not None:
            update_fields.append("location = :location")
            params["location"] = data.location
        if data.salary_range is not None:
            update_fields.append("salary_range = :salary_range")
            params["salary_range"] = data.salary_range
        if data.experience_required is not None:
            update_fields.append("experience_required = :experience_required")
            params["experience_required"] = data.experience_required
        if data.education_required is not None:
            update_fields.append("education_required = :education_required")
            params["education_required"] = data.education_required
        if data.description is not None:
            update_fields.append("description = :description")
            params["description"] = data.description
        if data.requirements is not None:
            update_fields.append("requirements = :requirements")
            params["requirements"] = data.requirements
        if data.job_profile is not None:
            update_fields.append("job_profile = CAST(:job_profile AS jsonb)")
            params["job_profile"] = json.dumps(data.job_profile)
        if data.status is not None:
            update_fields.append("status = :status")
            params["status"] = data.status
        if data.source is not None:
            update_fields.append("source = :source")
            params["source"] = data.source

        if not update_fields:
            return existing

        update_sql = ", ".join(update_fields)
        query = text(f"""
            UPDATE jobs
            SET {update_sql}, updated_at = NOW()
            WHERE id = :id
            RETURNING 
                id, title, company, industry, location, salary_range,
                experience_required, education_required, description,
                requirements, job_profile, status, source, created_at, updated_at
        """)

        result = self.db.execute(query, params)
        self.db.commit()
        row = result.fetchone()

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
            job_profile=row[10],
            status=row[11],
            source=row[12],
            created_at=row[13],
            updated_at=row[14]
        )

    # ==================== 删除岗位 ====================
    def delete_job(self, job_id: int) -> bool:
        """删除岗位"""
        query = text("DELETE FROM jobs WHERE id = :id")
        result = self.db.execute(query, {"id": job_id})
        self.db.commit()
        return result.rowcount > 0