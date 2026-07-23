"""
简历数据持久化模块

负责将结构化提取的简历数据保存到数据库
"""
import json
import logging
from typing import Dict, Any

from app.services.job_service import get_db_pool

logger = logging.getLogger(__name__)


async def save_parsed_data_to_db(
    user_id: int,
    file_path: str,
    file_type: str,
    structured_data: Dict[str, Any],
) -> int:
    """
    保存简历结构化数据到数据库

    Args:
        user_id: 用户ID
        file_path: 文件路径
        file_type: 文件类型
        structured_data: 结构化数据（ResumeStructuredData 转成的字典）

    Returns:
        resume_id: 简历ID
    """
    pool = await get_db_pool()

    # 转换数据格式：将 ResumeStructuredData 转换为兼容格式
    parsed_data = _convert_to_db_format(structured_data)

    async with pool.acquire() as conn:
        # 检查该用户是否已有相同文件路径的简历
        existing = await conn.fetchrow(
            "SELECT id FROM resumes WHERE user_id = $1 AND file_path = $2",
            user_id,
            file_path,
        )

        if existing:
            # 更新现有简历
            await conn.execute(
                """
                UPDATE resumes
                SET parsed_data = $1,
                    file_type = $2,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = $3
                """,
                json.dumps(parsed_data, ensure_ascii=False),
                file_type,
                existing['id'],
            )
            resume_id = existing['id']
        else:
            # 插入新简历，自动生成 user_resume_number
            resume_id = await conn.fetchval(
                """
                INSERT INTO resumes (
                    user_id,
                    file_path,
                    file_type,
                    status,
                    parsed_data,
                    user_resume_number
                )
                VALUES (
                    $1,
                    $2,
                    $3,
                    'active',
                    $4,
                    COALESCE((SELECT MAX(user_resume_number) FROM resumes WHERE user_id = $1), 0) + 1
                )
                RETURNING id
                """,
                user_id,
                file_path,
                file_type,
                json.dumps(parsed_data, ensure_ascii=False),
            )

    logger.info(f"简历数据已保存: resume_id={resume_id}, user_id={user_id}")
    return resume_id


def _convert_to_db_format(structured_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    将简历模块的结构化数据转换为数据库存储格式

    保留原始格式的同时，添加扁平化字段供匹配服务使用
    """
    # 保留原始数据
    db_data = structured_data.copy()

    # 添加扁平化的字段（兼容匹配服务）
    basic_info = structured_data.get("basic_info", {})
    if basic_info:
        # 将嵌套的 basic_info 字段提升到顶层
        db_data["name"] = basic_info.get("name")
        db_data["target_position"] = basic_info.get("job_intention")
        db_data["phone"] = basic_info.get("phone")
        db_data["email"] = basic_info.get("email")

    # 技能列表：同时保留对象数组和字符串数组格式
    skills = structured_data.get("skills", [])
    if skills:
        # 保留原始格式
        db_data["skills"] = skills
        # 添加简化格式（字符串数组）供匹配服务使用
        db_data["skills_flat"] = [
            skill.get("name") if isinstance(skill, dict) else skill
            for skill in skills
        ]

    # 工作经历：同时支持 work_experience 和 experience
    work_exp = structured_data.get("work_experience", [])
    if work_exp:
        db_data["work_experience"] = work_exp
        db_data["experience"] = work_exp  # 别名

    # 项目经验：同时支持 project_experience 和 projects
    projects = structured_data.get("project_experience", [])
    if projects:
        db_data["project_experience"] = projects
        db_data["projects"] = projects  # 别名

    return db_data
