"""
简历模块数据库持久化补丁

这个文件包含需要添加到简历模块的持久化功能。
将结构化提取的数据写入 resumes.parsed_data 字段，供匹配服务使用。

使用方法：
1. 将 save_parsed_data_to_db 函数添加到 app/core/resume/extractor.py
2. 在 app/api/v1/resume.py 的 extract_resume_structure 接口中调用该函数
"""

import json
from typing import Dict, Any, Optional
import asyncpg


async def get_db_pool() -> asyncpg.Pool:
    """
    获取数据库连接池

    注意：这个函数应该从你的数据库配置模块导入
    例如: from app.core.database import get_db_pool

    如果没有现成的，可以临时创建：
    """
    import os

    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", "5432"))
    db_name = os.getenv("DB_NAME", "career_planning")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "your_password")

    pool = await asyncpg.create_pool(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password,
        min_size=2,
        max_size=10,
    )
    return pool


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
        # 检查该用户是否已有简历
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
            # 插入新简历
            resume_id = await conn.fetchval(
                """
                INSERT INTO resumes (user_id, file_path, file_type, status, parsed_data)
                VALUES ($1, $2, $3, 'active', $4)
                RETURNING id
                """,
                user_id,
                file_path,
                file_type,
                json.dumps(parsed_data, ensure_ascii=False),
            )

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
        # 添加简化格式（字符串数组）
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


# ========================================
# 修改 app/api/v1/resume.py 的示例代码
# ========================================

EXAMPLE_USAGE = """
# 在 app/api/v1/resume.py 的 extract_resume_structure 函数中添加：

from app.core.resume.persistence import save_parsed_data_to_db  # 新增导入

@router.post("/extract", response_model=ApiResponse[ResumeExtractResponse])
async def extract_resume_structure(
    file: UploadFile = Depends(validate_resume_file),
    user_id: int = 1,  # TODO: 从认证中获取真实 user_id
):
    try:
        # 保存为临时文件
        file_path = await file_handler.save_temp_file(file)

        # 解析文件，提取文本
        parse_result = resume_parser.parse(file_path)
        resume_text = parse_result['text']

        # 使用 LLM 提取结构化数据
        structured_data = await resume_extractor.extract_structured_data(resume_text)

        # ========== 新增：保存到数据库 ==========
        try:
            resume_id = await save_parsed_data_to_db(
                user_id=user_id,
                file_path=file_path,
                file_type=file.content_type or "application/octet-stream",
                structured_data=structured_data.model_dump(),  # 转成字典
            )
            print(f"✅ 简历数据已保存到数据库，resume_id={resume_id}")
        except Exception as db_err:
            print(f"⚠️ 数据库保存失败（不影响返回）: {db_err}")
        # ==========================================

        response_data = ResumeExtractResponse(
            text=resume_text,
            structured_data=structured_data,
            message="提取成功"
        )

        return ApiResponse(
            code=200,
            message="提取成功",
            data=response_data
        )

    except FileHandlerError as e:
        raise HTTPException(...)
"""

if __name__ == "__main__":
    print("=" * 60)
    print("简历模块数据库持久化补丁")
    print("=" * 60)
    print()
    print("📋 需要修改的文件:")
    print("  1. app/core/resume/persistence.py (新建)")
    print("  2. app/api/v1/resume.py (修改)")
    print()
    print("📝 使用说明:")
    print(EXAMPLE_USAGE)
