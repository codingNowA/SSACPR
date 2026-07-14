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
from app.schemas.common import ApiResponse
from app.utils.file_handler import file_handler, FileHandlerError
from app.core.resume import resume_parser, ResumeParserError
from app.core.resume.extractor import resume_extractor, ResumeExtractorError


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
