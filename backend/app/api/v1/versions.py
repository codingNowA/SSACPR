"""
简历版本管理 API 路由
"""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException, Query, Body

from app.schemas.common import ApiResponse
from app.services.job_service import get_db_pool

router = APIRouter(prefix="/resume", tags=["简历版本快照"])


@router.post("/{resume_id}/snapshots", summary="保存简历快照")
async def create_resume_snapshot(
    resume_id: int,
    version_data: dict = Body(..., description="版本数据"),
) -> ApiResponse[dict]:
    """
    保存当前简历状态为新版本

    - 保存简历的 parsed_data、scores、optimization 快照
    - 便于后续查看历史版本和对比

    请求体格式:
    {
        "version_name": "版本名称",
        "scores": {...},  // 可选，评分数据
        "optimization": {...}  // 可选，优化建议数据
    }
    """
    try:
        version_name = version_data.get("version_name")
        if not version_name:
            raise HTTPException(status_code=400, detail="版本名称不能为空")

        scores = version_data.get("scores")
        optimization = version_data.get("optimization")

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
                resume["parsed_data"],
                json.dumps(scores) if scores else None,
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
async def get_resume_snapshots(
    resume_id: int,
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=10, ge=1, le=50, description="每页数量"),
) -> ApiResponse[dict]:
    """查询简历的所有历史版本"""
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
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
                    "created_at": row["created_at"].isoformat(),
                    "updated_at": row["updated_at"].isoformat(),
                }
                for row in rows
            ]

            return ApiResponse.success(
                data={
                    "versions": versions,
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                }
            )

    except Exception as e:
        return ApiResponse.error(message=f"获取版本列表失败: {e}")


@router.get("/snapshots/{version_id}", summary="获取快照详情")
async def get_snapshot_detail(version_id: int) -> ApiResponse[dict]:
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
                    "created_at": version["created_at"].isoformat(),
                    "updated_at": version["updated_at"].isoformat(),
                }
            )

    except HTTPException:
        raise
    except Exception as e:
        return ApiResponse.error(message=f"获取版本详情失败: {e}")


@router.delete("/snapshots/{version_id}", summary="删除快照")
async def delete_snapshot(version_id: int) -> ApiResponse[None]:
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
