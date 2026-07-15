"""
日志查询 API 路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.log_service import LogService
from app.models.log import LogResponse, LogListResponse

router = APIRouter(prefix="/api/v1/admin/logs", tags=["日志查询"])


@router.get("", response_model=LogListResponse)
def get_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: Optional[int] = Query(None, description="用户ID"),
    action: Optional[str] = Query(None, description="操作类型: CREATE/UPDATE/DELETE/LOGIN/LOGOUT"),
    module: Optional[str] = Query(None, description="模块: job/question/user/analytics"),
    start_date: Optional[str] = Query(None, description="开始时间 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束时间 (YYYY-MM-DD)"),
    keyword: Optional[str] = Query(None, description="关键词搜索（details/action/module）"),
    db: Session = Depends(get_db)
):
    """1. 获取日志列表（分页 + 筛选）"""
    service = LogService(db)
    return service.get_logs(page, page_size, user_id, action, module, start_date, end_date, keyword)


@router.get("/{log_id}", response_model=LogResponse)
def get_log(
    log_id: int,
    db: Session = Depends(get_db)
):
    """2. 获取单条日志详情"""
    service = LogService(db)
    result = service.get_log_by_id(log_id)
    if not result:
        raise HTTPException(status_code=404, detail="日志不存在")
    return result