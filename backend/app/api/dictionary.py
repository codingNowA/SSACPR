"""
词库与权重配置 API 路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, Request
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.dictionary_service import DictionaryService
from app.services.log_service import LogService
from app.models.dictionary import (
    DictionaryCreate,
    DictionaryUpdate,
    DictionaryResponse,
    DictionaryListResponse
)

router = APIRouter(prefix="/api/v1/admin/dictionary", tags=["词库配置"])


@router.post("", response_model=DictionaryResponse, status_code=201)
def create_dictionary(
    data: DictionaryCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """1. 创建词条"""
    service = DictionaryService(db)
    result = service.create_dictionary(data)

    log_service = LogService(db)
    log_service.create_log(
        user_id=1,
        action="CREATE",
        module="dictionary",
        details={"dict_id": result.id, "word": result.word, "type": result.type},
        ip_address=request.client.host if request.client else None
    )

    return result


@router.get("", response_model=DictionaryListResponse)
def get_dictionaries(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    type: Optional[str] = Query(None, description="词条类型: skill/industry/soft_skill"),
    keyword: Optional[str] = Query(None, description="关键词搜索（词条名/描述）"),
    db: Session = Depends(get_db)
):
    """2. 获取词条列表（分页 + 筛选）"""
    service = DictionaryService(db)
    return service.get_dictionaries(page, page_size, type, keyword)


@router.get("/{dict_id}", response_model=DictionaryResponse)
def get_dictionary(
    dict_id: int,
    db: Session = Depends(get_db)
):
    """3. 获取单个词条详情"""
    service = DictionaryService(db)
    result = service.get_dictionary_by_id(dict_id)
    if not result:
        raise HTTPException(status_code=404, detail="词条不存在")
    return result


@router.put("/{dict_id}", response_model=DictionaryResponse)
def update_dictionary(
    dict_id: int,
    data: DictionaryUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """4. 更新词条"""
    service = DictionaryService(db)
    result = service.update_dictionary(dict_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="词条不存在")

    log_service = LogService(db)
    log_service.create_log(
        user_id=1,
        action="UPDATE",
        module="dictionary",
        details={"dict_id": result.id, "word": result.word},
        ip_address=request.client.host if request.client else None
    )

    return result


@router.delete("/{dict_id}", status_code=204)
def delete_dictionary(
    dict_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """5. 删除词条"""
    service = DictionaryService(db)
    existing = service.get_dictionary_by_id(dict_id)
    if not existing:
        raise HTTPException(status_code=404, detail="词条不存在")

    deleted = service.delete_dictionary(dict_id)

    log_service = LogService(db)
    log_service.create_log(
        user_id=1,
        action="DELETE",
        module="dictionary",
        details={"dict_id": dict_id, "word": existing.word},
        ip_address=request.client.host if request.client else None
    )

    return None