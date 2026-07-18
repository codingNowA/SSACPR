"""
批量导入服务 - 支持从Excel导入题库和岗位库
"""
import logging
import io
from typing import Dict, Any, List
from fastapi import UploadFile
from sqlalchemy.orm import Session
import pandas as pd

from app.services.question_service import QuestionService
from app.services.job_admin_service import JobAdminService
from app.models.question import QuestionCreate
from app.models.job import JobCreate

logger = logging.getLogger(__name__)


class BatchImportService:
    """批量导入服务"""

    async def import_questions_from_excel(
        self,
        file: UploadFile,
        db: Session,
    ) -> Dict[str, Any]:
        """
        从Excel导入题库

        Excel格式要求：
        - 列名：content（必填）, category, difficulty, reference_answer
        - difficulty: 简单/中等/困难
        """
        try:
            # 读取Excel
            content = await file.read()
            df = pd.read_excel(io.BytesIO(content))

            # 验证列名
            required_columns = ['content']
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"缺少必需列: {col}")

            # 批量导入
            service = QuestionService(db)
            total = len(df)
            success = 0
            failed = 0
            errors = []

            for index, row in df.iterrows():
                try:
                    question_data = QuestionCreate(
                        content=str(row['content']),
                        category=str(row.get('category', '综合')) if pd.notna(row.get('category')) else '综合',
                        difficulty=str(row.get('difficulty', '中等')) if pd.notna(row.get('difficulty')) else '中等',
                        reference_answer=str(row.get('reference_answer', '')) if pd.notna(row.get('reference_answer')) else None,
                    )
                    service.create_question(question_data)
                    success += 1
                except Exception as e:
                    failed += 1
                    errors.append(f"第 {index + 2} 行: {str(e)}")
                    logger.error(f"导入题目失败（第 {index + 2} 行）: {e}")

            return {
                "total": total,
                "success": success,
                "failed": failed,
                "errors": errors[:10],  # 最多返回10条错误
                "message": f"成功导入 {success} 道题目，失败 {failed} 道"
            }

        except Exception as e:
            logger.error(f"Excel导入失败: {e}")
            raise ValueError(f"Excel解析失败: {str(e)}")

    async def import_jobs_from_excel(
        self,
        file: UploadFile,
        db: Session,
    ) -> Dict[str, Any]:
        """
        从Excel导入岗位库

        Excel格式要求：
        - 列名：title（必填）, company（必填）, industry, location, salary_range,
                experience_required, education_required, description, requirements
        """
        try:
            # 读取Excel
            content = await file.read()
            df = pd.read_excel(io.BytesIO(content))

            # 验证列名
            required_columns = ['title', 'company']
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"缺少必需列: {col}")

            # 批量导入
            service = JobAdminService(db)
            total = len(df)
            success = 0
            failed = 0
            errors = []

            for index, row in df.iterrows():
                try:
                    job_data = JobCreate(
                        title=str(row['title']),
                        company=str(row['company']),
                        industry=str(row.get('industry', '')) if pd.notna(row.get('industry')) else None,
                        location=str(row.get('location', '')) if pd.notna(row.get('location')) else None,
                        salary_range=str(row.get('salary_range', '')) if pd.notna(row.get('salary_range')) else None,
                        experience_required=str(row.get('experience_required', '')) if pd.notna(row.get('experience_required')) else None,
                        education_required=str(row.get('education_required', '')) if pd.notna(row.get('education_required')) else None,
                        description=str(row.get('description', '')) if pd.notna(row.get('description')) else None,
                        requirements=str(row.get('requirements', '')) if pd.notna(row.get('requirements')) else None,
                        status='active',
                        source='batch_import',
                    )
                    service.create_job(job_data)
                    success += 1
                except Exception as e:
                    failed += 1
                    errors.append(f"第 {index + 2} 行: {str(e)}")
                    logger.error(f"导入岗位失败（第 {index + 2} 行）: {e}")

            return {
                "total": total,
                "success": success,
                "failed": failed,
                "errors": errors[:10],
                "message": f"成功导入 {success} 个岗位，失败 {failed} 个"
            }

        except Exception as e:
            logger.error(f"Excel导入失败: {e}")
            raise ValueError(f"Excel解析失败: {str(e)}")


# 单例
batch_import_service = BatchImportService()
