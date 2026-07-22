"""
简历版本管理 API 路由
"""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from fastapi.responses import Response
from app.core.auth import get_current_user

from app.schemas.common import ApiResponse
from app.services.job_service import get_db_pool

router = APIRouter(prefix="/resume", tags=["简历版本快照"])


@router.post("/{resume_id}/snapshots", summary="保存简历快照")
async def create_resume_snapshot(resume_id: int, _user: dict = Depends(get_current_user), version_data: dict = Body(..., description="版本数据"),
) -> ApiResponse[dict]:
    """
    保存当前简历状态为新版本

    - 保存简历的 parsed_data、scores、optimization 快照
    - 便于后续查看历史版本和对比

    请求体格式:
    {
        "version_name": "版本名称",
        "parsed_data": {...},  // 可选，如果提供则使用这个数据，否则使用数据库中的当前数据
        "scores": {...},  // 可选，评分数据
        "optimization": {...},  // 可选，优化建议数据
        "summary": "..."  // 可选，简历摘要
    }
    """
    try:
        version_name = version_data.get("version_name")
        if not version_name:
            raise HTTPException(status_code=400, detail="版本名称不能为空")

        scores = version_data.get("scores")
        optimization = version_data.get("optimization")
        summary = version_data.get("summary")
        parsed_data_override = version_data.get("parsed_data")

        pool = await get_db_pool()
        async with pool.acquire() as conn:
            # 检查简历是否存在并获取数据
            resume = await conn.fetchrow(
                "SELECT id, parsed_data FROM resumes WHERE id = $1",
                resume_id,
            )
            if not resume:
                raise HTTPException(status_code=404, detail="简历不存在")

            import json

            # 如果提供了新的 parsed_data，使用它；否则使用数据库中的
            parsed_data_to_save = json.dumps(parsed_data_override) if parsed_data_override else resume["parsed_data"]

            # 合并诊断数据到 scores 字段（包含评分、摘要等）
            scores_data = None
            if scores or summary:
                scores_data = {
                    **(scores if isinstance(scores, dict) else {}),
                    "summary": summary
                }

            # 保存版本
            version = await conn.fetchrow(
                """
                INSERT INTO resume_versions
                (resume_id, version_name, parsed_data, scores, optimization)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id, version_name, created_at
                """,
                resume_id,
                version_name,
                parsed_data_to_save,
                json.dumps(scores_data) if scores_data else None,
                json.dumps(optimization) if optimization else None,
            )

            return ApiResponse.success(
                data={
                    "id": version["id"],
                    "version_name": version["version_name"],
                    "created_at": version["created_at"].isoformat(),
                },
                message="版本保存成功",
            )

    except HTTPException:
        raise
    except Exception as e:
        return ApiResponse.error(message=f"保存版本失败: {e}")


@router.get("/{resume_id}/snapshots", summary="获取快照列表")
async def get_resume_snapshots(resume_id: int, _user: dict = Depends(get_current_user), page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=10, ge=1, le=50, description="每页数量"),
) -> ApiResponse[dict]:
    """查询简历的所有历史版本"""
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            # 获取当前版本ID
            current_version_id = await conn.fetchval(
                "SELECT current_version_id FROM resumes WHERE id = $1",
                resume_id,
            )

            # 获取总数
            total = await conn.fetchval(
                "SELECT COUNT(*) FROM resume_versions WHERE resume_id = $1",
                resume_id,
            )

            # 获取版本列表
            offset = (page - 1) * page_size
            rows = await conn.fetch(
                """
                SELECT id, version_name, created_at, updated_at
                FROM resume_versions
                WHERE resume_id = $1
                ORDER BY created_at DESC
                LIMIT $2 OFFSET $3
                """,
                resume_id,
                page_size,
                offset,
            )

            versions = [
                {
                    "id": row["id"],
                    "version_name": row["version_name"],
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                    "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
                    "is_current": row["id"] == current_version_id,  # 标记是否为当前版本
                }
                for row in rows
            ]

            return ApiResponse.success(
                data={
                    "versions": versions,
                    "current_version_id": current_version_id,  # 返回当前版本ID
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                }
            )

    except Exception as e:
        return ApiResponse.error(message=f"获取版本列表失败: {e}")


@router.get("/snapshots/{version_id}", summary="获取快照详情")
async def get_snapshot_detail(version_id: int, _user: dict = Depends(get_current_user)) -> ApiResponse[dict]:
    """查询特定快照的详细信息"""
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"查询版本详情，version_id={version_id}")

        pool = await get_db_pool()
        async with pool.acquire() as conn:
            version = await conn.fetchrow(
                """
                SELECT id, resume_id, version_name, parsed_data,
                       scores, optimization, created_at, updated_at
                FROM resume_versions
                WHERE id = $1
                """,
                version_id,
            )

            logger.info(f"查询结果: version={version}")

            if not version:
                logger.warning(f"版本不存在: version_id={version_id}")
                raise HTTPException(status_code=404, detail="版本不存在")

            import json

            # 解析JSONB字段
            parsed_data = version["parsed_data"]
            if isinstance(parsed_data, str):
                parsed_data = json.loads(parsed_data)

            scores = version["scores"]
            if isinstance(scores, str):
                scores = json.loads(scores)

            optimization = version["optimization"]
            if isinstance(optimization, str):
                optimization = json.loads(optimization)

            return ApiResponse.success(
                data={
                    "id": version["id"],
                    "resume_id": version["resume_id"],
                    "version_name": version["version_name"],
                    "parsed_data": parsed_data,
                    "scores": scores,
                    "optimization": optimization,
                    "created_at": version["created_at"].isoformat() if version["created_at"] else None,
                    "updated_at": version["updated_at"].isoformat() if version["updated_at"] else None,
                }
            )

    except HTTPException:
        raise
    except Exception as e:
        return ApiResponse.error(message=f"获取版本详情失败: {e}")


@router.delete("/snapshots/{version_id}", summary="删除快照")
async def delete_snapshot(version_id: int, _user: dict = Depends(get_current_user)) -> ApiResponse[None]:
    """删除指定快照"""
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM resume_versions WHERE id = $1",
                version_id,
            )

            if result == "DELETE 0":
                raise HTTPException(status_code=404, detail="版本不存在")

            return ApiResponse.success(message="版本删除成功")

    except HTTPException:
        raise
    except Exception as e:
        return ApiResponse.error(message=f"删除版本失败: {e}")


@router.post("/snapshots/{version_id}/diagnose", summary="诊断指定版本")
async def diagnose_snapshot(version_id: int, _user: dict = Depends(get_current_user)) -> ApiResponse[dict]:
    """
    对指定版本的简历进行诊断评分和优化建议生成

    - 从版本的 parsed_data 中提取简历内容
    - 调用评分和优化服务
    - 将结果更新到该版本的 scores 和 optimization 字段
    """
    try:
        from app.core.resume.scorer import resume_scorer
        from app.core.resume.optimizer import resume_optimizer
        from app.schemas.resume_structured import ResumeStructuredData
        import json
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"开始诊断版本: version_id={version_id}")

        pool = await get_db_pool()
        async with pool.acquire() as conn:
            # 获取版本数据
            version = await conn.fetchrow(
                "SELECT id, resume_id, parsed_data FROM resume_versions WHERE id = $1",
                version_id,
            )

            if not version:
                raise HTTPException(status_code=404, detail="版本不存在")

            # 解析 parsed_data
            parsed_data = version["parsed_data"]
            if isinstance(parsed_data, str):
                parsed_data = json.loads(parsed_data)

            logger.info(f"parsed_data类型: {type(parsed_data)}")

            # 处理 skills 字段：如果是字符串列表，转换为 SkillTag 对象列表
            if "skills" in parsed_data and isinstance(parsed_data["skills"], list):
                skills = []
                for skill in parsed_data["skills"]:
                    if isinstance(skill, str):
                        skills.append({"name": skill})
                    elif isinstance(skill, dict):
                        skills.append(skill)
                parsed_data["skills"] = skills

            # 将字典转换为 ResumeStructuredData 对象
            try:
                structured_data = ResumeStructuredData(**parsed_data)
            except Exception as e:
                logger.error(f"转换结构化数据失败: {e}")
                raise HTTPException(status_code=400, detail=f"简历数据格式错误: {str(e)}")

            # 生成简化的文本用于评分（从结构化数据重建）
            resume_text_parts = []
            if structured_data.basic_info:
                basic = structured_data.basic_info
                resume_text_parts.append(f"姓名：{basic.name or ''}")
                resume_text_parts.append(f"电话：{basic.phone or ''}")
                resume_text_parts.append(f"邮箱：{basic.email or ''}")

            if structured_data.education:
                resume_text_parts.append("\n教育经历：")
                for edu in structured_data.education:
                    resume_text_parts.append(f"{edu.school} {edu.major or ''} {edu.degree or ''}")

            if structured_data.work_experience:
                resume_text_parts.append("\n工作经历：")
                for work in structured_data.work_experience:
                    resume_text_parts.append(f"{work.company} {work.position or ''}")
                    if work.description:
                        resume_text_parts.append(work.description)

            if structured_data.project_experience:
                resume_text_parts.append("\n项目经验：")
                for proj in structured_data.project_experience:
                    resume_text_parts.append(f"{proj.name} {proj.role or ''}")
                    if proj.description:
                        resume_text_parts.append(proj.description)

            if structured_data.skills:
                skill_names = [s.name if hasattr(s, 'name') else str(s) for s in structured_data.skills]
                resume_text_parts.append(f"\n技能：{', '.join(skill_names)}")

            if structured_data.self_evaluation:
                resume_text_parts.append(f"\n自我评价：{structured_data.self_evaluation}")

            resume_text = "\n".join(resume_text_parts)

            # 调用评分服务
            try:
                logger.warning(f"[DIAGNOSE] 开始评分 version_id={version_id}")
                scores_result = await resume_scorer.score_resume(structured_data, resume_text)
                scores_dict = scores_result.dict() if hasattr(scores_result, 'dict') else scores_result
                logger.warning(f"[DIAGNOSE] 评分完成，总分: {scores_dict.get('total_score', 'N/A')}")
            except Exception as e:
                logger.error(f"评分失败: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"评分失败: {str(e)}")

            # 调用优化建议服务
            try:
                logger.warning(f"[DIAGNOSE] 开始生成优化建议（将调用LLM）...")
                optimization_result = await resume_optimizer.optimize_resume(
                    structured_data,
                    scores_result,
                    resume_text
                )
                optimization_dict = optimization_result.dict() if hasattr(optimization_result, 'dict') else optimization_result
                logger.warning(f"[DIAGNOSE] 优化建议生成完成")
            except Exception as e:
                logger.error(f"生成优化建议失败: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"生成优化建议失败: {str(e)}")

            # 更新版本的评分和优化建议
            await conn.execute(
                """
                UPDATE resume_versions
                SET scores = $1, optimization = $2, updated_at = NOW()
                WHERE id = $3
                """,
                json.dumps(scores_dict),
                json.dumps(optimization_dict),
                version_id,
            )

            return ApiResponse.success(
                data={
                    "scores": scores_dict,
                    "optimization": optimization_dict,
                },
                message="诊断完成",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"诊断版本失败: {e}", exc_info=True)
        return ApiResponse.error(message=f"诊断版本失败: {str(e)}")


@router.get("/snapshots/{version_id}/download", summary="下载版本为PDF")
async def download_snapshot_pdf(version_id: int, _user: dict = Depends(get_current_user)):
    """
    下载指定版本的简历为PDF文件

    - 如果版本有诊断结果，生成包含诊断报告的PDF
    - 如果没有诊断结果，返回提示需要先诊断
    - 返回PDF文件供下载
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        from app.services.pdf_service import pdf_generator
        import json

        logger.info(f"开始生成PDF: version_id={version_id}")

        pool = await get_db_pool()
        async with pool.acquire() as conn:
            # 获取版本数据和诊断结果
            version = await conn.fetchrow(
                "SELECT id, version_name, parsed_data, scores, optimization FROM resume_versions WHERE id = $1",
                version_id,
            )

            if not version:
                raise HTTPException(status_code=404, detail="版本不存在")

            # 解析数据
            parsed_data = version["parsed_data"]
            if isinstance(parsed_data, str):
                parsed_data = json.loads(parsed_data)

            scores = version["scores"]
            if isinstance(scores, str):
                scores = json.loads(scores)

            optimization = version["optimization"]
            if isinstance(optimization, str):
                optimization = json.loads(optimization)

            version_name = version["version_name"]

            # 生成PDF（根据是否有诊断结果选择不同的生成方式）
            try:
                if scores:
                    # 有诊断结果，生成包含诊断的PDF
                    pdf_bytes = pdf_generator.generate_resume_pdf_with_diagnosis(
                        parsed_data, scores, version_name, optimization
                    )
                else:
                    # 没有诊断结果，只生成简历内容的PDF
                    pdf_bytes = pdf_generator.generate_resume_pdf(
                        parsed_data, version_name
                    )
            except Exception as e:
                logger.error(f"生成PDF失败: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"生成PDF失败: {str(e)}")

            # 返回PDF文件
            filename = f"resume_{version_name}_{version_id}.pdf"
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                }
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载PDF失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"下载PDF失败: {str(e)}")
