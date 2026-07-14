"""
简历相关 API 路由
"""
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.api.deps import validate_resume_file, get_user_id
from app.schemas.resume import (
    ResumeUploadResponse,
    ResumeParseResponse,
    ResumeParseRequest,
)
from app.schemas.resume_structured import ResumeExtractResponse
from app.schemas.resume_score import ResumeScoreRequest, ResumeScoreResponse
from app.schemas.resume_optimize import ResumeOptimizationRequest, ResumeOptimizationResponse
from app.schemas.resume_version import (
    ResumeVersionCreate,
    ResumeVersionUpdate,
    ResumeVersionListItem,
    ResumeVersionDetail,
    ResumeVersionCompare,
    ResumeVersionStats,
    ResumeVersionResponse,
    ResumeVersionListResponse,
)
from app.schemas.common import ApiResponse
from app.utils.file_handler import file_handler, FileHandlerError
from app.core.resume import resume_parser, ResumeParserError
from app.core.resume.extractor import resume_extractor, ResumeExtractorError
from app.core.resume.scorer import resume_scorer, ResumeScorerError
from app.core.resume.optimizer import resume_optimizer, ResumeOptimizerError
from app.services.resume_version_service import resume_version_manager, ResumeVersionError


router = APIRouter(prefix="/resume", tags=["简历管理"])


@router.post("/upload", response_model=ApiResponse[ResumeUploadResponse])
async def upload_resume(
    file: UploadFile = Depends(validate_resume_file),
    user_id: Optional[int] = Depends(get_user_id),
):
    """
    上传简历文件

    支持的格式：
    - PDF (.pdf)
    - Word (.docx, 不支持 .doc)
    - 图片 (.png, .jpg, .jpeg)

    Args:
        file: 简历文件
        user_id: 用户 ID（可选）

    Returns:
        上传结果
    """
    try:
        # 保存文件
        file_path, file_type = await file_handler.save_resume(file, user_id)

        response_data = ResumeUploadResponse(
            file_path=file_path,
            file_type=file_type,
            message="文件上传成功"
        )

        return ApiResponse(
            code=200,
            message="上传成功",
            data=response_data
        )

    except FileHandlerError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传失败: {str(e)}"
        )


@router.post("/parse", response_model=ApiResponse[ResumeParseResponse])
async def parse_resume(
    file: UploadFile = Depends(validate_resume_file),
):
    """
    上传并解析简历文件

    该接口会：
    1. 保存简历文件
    2. 提取文本内容
    3. 返回解析结果

    Args:
        file: 简历文件

    Returns:
        解析结果
    """
    try:
        # 保存为临时文件
        file_path = await file_handler.save_temp_file(file)

        # 解析文件
        parse_result = resume_parser.parse(file_path)

        response_data = ResumeParseResponse(**parse_result)

        return ApiResponse(
            code=200,
            message="解析成功",
            data=response_data
        )

    except FileHandlerError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件处理失败: {str(e)}"
        )
    except ResumeParserError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"解析失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器错误: {str(e)}"
        )


@router.post("/parse-by-path", response_model=ApiResponse[ResumeParseResponse])
async def parse_resume_by_path(request: ResumeParseRequest):
    """
    根据文件路径解析简历

    用于解析已上传的简历文件

    Args:
        request: 包含文件路径和类型的请求

    Returns:
        解析结果
    """
    try:
        # 解析文件
        parse_result = resume_parser.parse(
            request.file_path,
            request.file_type
        )

        response_data = ResumeParseResponse(**parse_result)

        return ApiResponse(
            code=200,
            message="解析成功",
            data=response_data
        )

    except ResumeParserError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"解析失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器错误: {str(e)}"
        )


@router.post("/extract", response_model=ApiResponse[ResumeExtractResponse])
async def extract_resume_structure(
    file: UploadFile = Depends(validate_resume_file),
):
    """
    上传并提取简历结构化信息

    该接口会：
    1. 保存简历文件
    2. 提取文本内容
    3. 使用 LLM 提取结构化信息（基本信息、教育经历、实习经历、项目经验、技能标签）
    4. 返回结构化数据

    Args:
        file: 简历文件

    Returns:
        结构化提取结果
    """
    try:
        # 保存为临时文件
        file_path = await file_handler.save_temp_file(file)

        # 解析文件，提取文本
        parse_result = resume_parser.parse(file_path)
        resume_text = parse_result['text']

        # 使用 LLM 提取结构化数据
        structured_data = await resume_extractor.extract_structured_data(resume_text)

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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件处理失败: {str(e)}"
        )
    except ResumeParserError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文本提取失败: {str(e)}"
        )
    except ResumeExtractorError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"结构化提取失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器错误: {str(e)}"
        )


@router.post("/score", response_model=ApiResponse[ResumeScoreResponse])
async def score_resume(
    file: UploadFile = Depends(validate_resume_file),
    job_title: Optional[str] = None,
    job_description: Optional[str] = None,
):
    """
    上传简历并进行多维度评分

    该接口会：
    1. 解析简历文件
    2. 提取结构化信息
    3. 进行多维度评分：完整性、专业性、量化程度、项目深度、岗位匹配
    4. 返回评分结果和改进建议

    Args:
        file: 简历文件
        job_title: 目标岗位（可选，用于岗位匹配评分）
        job_description: 岗位描述（可选）

    Returns:
        评分结果
    """
    try:
        # 1. 保存为临时文件
        file_path = await file_handler.save_temp_file(file)

        # 2. 解析文件，提取文本
        parse_result = resume_parser.parse(file_path)
        resume_text = parse_result['text']

        # 3. 使用 LLM 提取结构化数据
        structured_data = await resume_extractor.extract_structured_data(resume_text)

        # 4. 评分
        score = await resume_scorer.score_resume(
            structured_data=structured_data,
            resume_text=resume_text,
            job_title=job_title,
            job_description=job_description,
            required_skills=None
        )

        response_data = ResumeScoreResponse(
            score=score,
            message="评分成功"
        )

        return ApiResponse(
            code=200,
            message="评分成功",
            data=response_data
        )

    except FileHandlerError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件处理失败: {str(e)}"
        )
    except ResumeParserError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文本提取失败: {str(e)}"
        )
    except ResumeExtractorError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"结构化提取失败: {str(e)}"
        )
    except ResumeScorerError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"评分失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器错误: {str(e)}"
        )


@router.post("/optimize", response_model=ApiResponse[ResumeOptimizationResponse])
async def optimize_resume(
    file: UploadFile = Depends(validate_resume_file),
    job_title: Optional[str] = None,
    job_description: Optional[str] = None,
):
    """
    上传简历并生成优化建议和文案

    该接口会：
    1. 解析简历文件
    2. 提取结构化信息
    3. 进行多维度评分
    4. 生成可执行的优化建议
    5. 如果提供岗位信息，生成面向岗位的优化文案

    Args:
        file: 简历文件
        job_title: 目标岗位（可选）
        job_description: 岗位描述（可选）

    Returns:
        优化建议和文案
    """
    try:
        # 1. 保存为临时文件
        file_path = await file_handler.save_temp_file(file)

        # 2. 解析文件，提取文本
        parse_result = resume_parser.parse(file_path)
        resume_text = parse_result['text']

        # 3. 使用 LLM 提取结构化数据
        structured_data = await resume_extractor.extract_structured_data(resume_text)

        # 4. 评分
        score = await resume_scorer.score_resume(
            structured_data=structured_data,
            resume_text=resume_text,
            job_title=job_title,
            job_description=job_description,
            required_skills=None
        )

        # 5. 生成优化建议
        optimization = await resume_optimizer.optimize_resume(
            structured_data=structured_data,
            score=score,
            resume_text=resume_text,
            job_title=job_title,
            job_description=job_description,
            focus_areas=None
        )

        response_data = ResumeOptimizationResponse(
            optimization=optimization,
            message="优化建议生成成功"
        )

        return ApiResponse(
            code=200,
            message="优化成功",
            data=response_data
        )

    except FileHandlerError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件处理失败: {str(e)}"
        )
    except ResumeParserError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文本提取失败: {str(e)}"
        )
    except ResumeExtractorError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"结构化提取失败: {str(e)}"
        )
    except ResumeScorerError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"评分失败: {str(e)}"
        )
    except ResumeOptimizerError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"优化失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器错误: {str(e)}"
        )


@router.get("/formats")
async def get_supported_formats():
    """
    获取支持的简历格式

    Returns:
        支持的格式列表
    """
    return ApiResponse(
        code=200,
        message="success",
        data={
            "formats": [
                {
                    "extension": "pdf",
                    "mime_types": ["application/pdf"],
                    "description": "PDF 文档"
                },
                {
                    "extension": "docx",
                    "mime_types": ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
                    "description": "Word 文档（仅支持 .docx）"
                },
                {
                    "extension": "png",
                    "mime_types": ["image/png"],
                    "description": "PNG 图片（需要 OCR）"
                },
                {
                    "extension": "jpg",
                    "mime_types": ["image/jpeg"],
                    "description": "JPEG 图片（需要 OCR）"
                },
                {
                    "extension": "jpeg",
                    "mime_types": ["image/jpeg"],
                    "description": "JPEG 图片（需要 OCR）"
                }
            ],
            "max_file_size": file_handler.MAX_FILE_SIZE,
            "max_file_size_mb": round(file_handler.MAX_FILE_SIZE / 1024 / 1024, 2)
        }
    )


# ==================== 简历版本管理接口 ====================

@router.post("/versions", response_model=ApiResponse[ResumeVersionResponse])
async def create_resume_version(
    file: UploadFile = Depends(validate_resume_file),
    title: str = None,
    description: str = None,
    target_job: str = None,
    set_as_active: bool = False,
    user_id: Optional[int] = Depends(get_user_id),
    auto_process: bool = True,
):
    """
    创建简历版本

    该接口会：
    1. 保存简历文件
    2. 如果 auto_process=True，自动解析、提取、评分、优化
    3. 创建版本记录
    4. 返回版本信息

    Args:
        file: 简历文件
        title: 版本标题（必需）
        description: 版本描述
        target_job: 目标岗位
        set_as_active: 是否设为当前激活版本
        user_id: 用户ID
        auto_process: 是否自动处理（解析、提取、评分、优化）

    Returns:
        版本信息
    """
    if not title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="版本标题不能为空"
        )

    if not user_id:
        user_id = 1  # 默认用户ID（开发阶段）

    try:
        # 1. 保存文件
        file_path, file_type = await file_handler.save_resume(file, user_id)

        parsed_text = None
        structured_data = None
        score_data = None
        optimization_data = None

        if auto_process:
            # 2. 解析文件
            parse_result = resume_parser.parse(file_path)
            parsed_text = parse_result['text']

            # 3. 提取结构化数据
            structured_data_obj = await resume_extractor.extract_structured_data(parsed_text)
            structured_data = structured_data_obj.dict()

            # 4. 评分
            score = await resume_scorer.score_resume(
                structured_data=structured_data_obj,
                resume_text=parsed_text,
                job_title=target_job,
                job_description=None,
                required_skills=None
            )
            score_data = score.dict()

            # 5. 生成优化建议
            optimization = await resume_optimizer.optimize_resume(
                structured_data=structured_data_obj,
                score=score,
                resume_text=parsed_text,
                job_title=target_job,
                job_description=None,
                focus_areas=None
            )
            optimization_data = optimization.dict()

        # 6. 创建版本
        version_data = ResumeVersionCreate(
            title=title,
            description=description,
            target_job=target_job,
            set_as_active=set_as_active
        )

        version = resume_version_manager.create_version(
            user_id=user_id,
            file_path=file_path,
            file_type=file_type,
            version_data=version_data,
            parsed_text=parsed_text,
            structured_data=structured_data,
            score_data=score_data,
            optimization_data=optimization_data,
        )

        response_data = ResumeVersionResponse(
            version=version,
            message="版本创建成功"
        )

        return ApiResponse(
            code=200,
            message="创建成功",
            data=response_data
        )

    except FileHandlerError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件处理失败: {str(e)}"
        )
    except ResumeVersionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"版本创建失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器错误: {str(e)}"
        )


@router.get("/versions", response_model=ApiResponse[ResumeVersionListResponse])
async def list_resume_versions(
    page: int = 1,
    page_size: int = 10,
    active_only: bool = False,
    user_id: Optional[int] = Depends(get_user_id),
):
    """
    获取简历版本列表

    Args:
        page: 页码（从1开始）
        page_size: 每页大小
        active_only: 只返回激活版本
        user_id: 用户ID

    Returns:
        版本列表
    """
    if not user_id:
        user_id = 1  # 默认用户ID（开发阶段）

    try:
        versions, total = resume_version_manager.list_versions(
            user_id=user_id,
            page=page,
            page_size=page_size,
            active_only=active_only,
        )

        response_data = ResumeVersionListResponse(
            versions=versions,
            total=total,
            page=page,
            page_size=page_size,
            message="查询成功"
        )

        return ApiResponse(
            code=200,
            message="查询成功",
            data=response_data
        )

    except ResumeVersionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"查询失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器错误: {str(e)}"
        )


@router.get("/versions/{version_id}", response_model=ApiResponse[ResumeVersionDetail])
async def get_resume_version(
    version_id: int,
    user_id: Optional[int] = Depends(get_user_id),
):
    """
    获取简历版本详情

    Args:
        version_id: 版本ID
        user_id: 用户ID

    Returns:
        版本详情
    """
    if not user_id:
        user_id = 1  # 默认用户ID（开发阶段）

    try:
        version = resume_version_manager.get_version(user_id, version_id)

        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="版本不存在"
            )

        return ApiResponse(
            code=200,
            message="查询成功",
            data=version
        )

    except HTTPException:
        raise
    except ResumeVersionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"查询失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器错误: {str(e)}"
        )


@router.put("/versions/{version_id}", response_model=ApiResponse[ResumeVersionResponse])
async def update_resume_version(
    version_id: int,
    update_data: ResumeVersionUpdate,
    user_id: Optional[int] = Depends(get_user_id),
):
    """
    更新简历版本

    Args:
        version_id: 版本ID
        update_data: 更新数据
        user_id: 用户ID

    Returns:
        更新后的版本
    """
    if not user_id:
        user_id = 1  # 默认用户ID（开发阶段）

    try:
        version = resume_version_manager.update_version(
            user_id=user_id,
            version_id=version_id,
            update_data=update_data,
        )

        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="版本不存在"
            )

        response_data = ResumeVersionResponse(
            version=version,
            message="更新成功"
        )

        return ApiResponse(
            code=200,
            message="更新成功",
            data=response_data
        )

    except HTTPException:
        raise
    except ResumeVersionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"更新失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器错误: {str(e)}"
        )


@router.delete("/versions/{version_id}")
async def delete_resume_version(
    version_id: int,
    user_id: Optional[int] = Depends(get_user_id),
):
    """
    删除简历版本

    Args:
        version_id: 版本ID
        user_id: 用户ID

    Returns:
        删除结果
    """
    if not user_id:
        user_id = 1  # 默认用户ID（开发阶段）

    try:
        success = resume_version_manager.delete_version(user_id, version_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="版本不存在"
            )

        return ApiResponse(
            code=200,
            message="删除成功",
            data={"deleted": True}
        )

    except HTTPException:
        raise
    except ResumeVersionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"删除失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器错误: {str(e)}"
        )


@router.post("/versions/{version_id}/activate")
async def activate_resume_version(
    version_id: int,
    user_id: Optional[int] = Depends(get_user_id),
):
    """
    设置为激活版本

    Args:
        version_id: 版本ID
        user_id: 用户ID

    Returns:
        设置结果
    """
    if not user_id:
        user_id = 1  # 默认用户ID（开发阶段）

    try:
        success = resume_version_manager.set_active_version(user_id, version_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="版本不存在"
            )

        return ApiResponse(
            code=200,
            message="设置成功",
            data={"activated": True}
        )

    except HTTPException:
        raise
    except ResumeVersionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"设置失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器错误: {str(e)}"
        )


@router.get("/versions/compare/{version_id1}/{version_id2}", response_model=ApiResponse[ResumeVersionCompare])
async def compare_resume_versions(
    version_id1: int,
    version_id2: int,
    user_id: Optional[int] = Depends(get_user_id),
):
    """
    对比两个简历版本

    Args:
        version_id1: 版本1 ID
        version_id2: 版本2 ID
        user_id: 用户ID

    Returns:
        版本对比结果
    """
    if not user_id:
        user_id = 1  # 默认用户ID（开发阶段）

    try:
        compare_result = resume_version_manager.compare_versions(
            user_id=user_id,
            version_id1=version_id1,
            version_id2=version_id2,
        )

        if not compare_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="版本不存在"
            )

        return ApiResponse(
            code=200,
            message="对比成功",
            data=compare_result
        )

    except HTTPException:
        raise
    except ResumeVersionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"对比失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器错误: {str(e)}"
        )


@router.get("/versions/stats", response_model=ApiResponse[ResumeVersionStats])
async def get_resume_version_stats(
    user_id: Optional[int] = Depends(get_user_id),
):
    """
    获取简历版本统计

    Args:
        user_id: 用户ID

    Returns:
        版本统计
    """
    if not user_id:
        user_id = 1  # 默认用户ID（开发阶段）

    try:
        stats = resume_version_manager.get_stats(user_id)

        return ApiResponse(
            code=200,
            message="查询成功",
            data=stats
        )

    except ResumeVersionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"查询失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器错误: {str(e)}"
        )
