"""
题库管理 API 路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, Request, UploadFile, File
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.question_service import QuestionService
from app.services.log_service import LogService
from app.services.batch_import_service import batch_import_service
from app.models.question import (
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
    QuestionListResponse
)

router = APIRouter(prefix="/api/v1/admin/questions", tags=["题库管理"])


@router.post("", response_model=QuestionResponse, status_code=201)
def create_question(
    data: QuestionCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """1. 创建题目"""
    service = QuestionService(db)
    result = service.create_question(data)

    # 写日志
    log_service = LogService(db)
    log_service.create_log(
        user_id=1,
        action="CREATE",
        module="question",
        details={"question_id": result.id, "category": result.category},
        ip_address=request.client.host if request.client else None
    )

    return result


@router.get("", response_model=QuestionListResponse)
def get_questions(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    category: Optional[str] = Query(None, description="分类筛选"),
    difficulty: Optional[str] = Query(None, description="难度筛选: easy/medium/hard"),
    keyword: Optional[str] = Query(None, description="关键词搜索（题目或答案）"),
    db: Session = Depends(get_db)
):
    """2. 获取题目列表（分页 + 筛选）"""
    service = QuestionService(db)
    return service.get_questions(page, page_size, category, difficulty, keyword)


@router.get("/{question_id}", response_model=QuestionResponse)
def get_question(
    question_id: int,
    db: Session = Depends(get_db)
):
    """3. 获取单道题目详情"""
    service = QuestionService(db)
    result = service.get_question_by_id(question_id)
    if not result:
        raise HTTPException(status_code=404, detail="题目不存在")
    return result


@router.put("/{question_id}", response_model=QuestionResponse)
def update_question(
    question_id: int,
    data: QuestionUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """4. 更新题目"""
    service = QuestionService(db)
    result = service.update_question(question_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="题目不存在")

    # 写日志
    log_service = LogService(db)
    log_service.create_log(
        user_id=1,
        action="UPDATE",
        module="question",
        details={"question_id": result.id, "category": result.category},
        ip_address=request.client.host if request.client else None
    )

    return result


@router.delete("/{question_id}", status_code=204)
def delete_question(
    question_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """5. 删除题目"""
    # 先获取要删除的题目信息（用于日志）
    question_service = QuestionService(db)
    question = question_service.get_question_by_id(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")

    # 执行删除
    deleted = question_service.delete_question(question_id)

    # 写日志
    log_service = LogService(db)
    log_service.create_log(
        user_id=1,
        action="DELETE",
        module="question",
        details={"question_id": question_id, "category": question.category},
        ip_address=request.client.host if request.client else None
    )

    return None


@router.post("/batch-import", status_code=201)
async def batch_import_questions(
    file: UploadFile = File(...),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """6. 批量导入题目（Excel）"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="只支持 Excel 文件格式（.xlsx, .xls）")

    try:
        result = await batch_import_service.import_questions_from_excel(file, db)

        # 写日志
        log_service = LogService(db)
        log_service.create_log(
            user_id=1,
            action="BATCH_IMPORT",
            module="question",
            details={"total": result["total"], "success": result["success"], "failed": result["failed"]},
            ip_address=request.client.host if request and request.client else None
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")