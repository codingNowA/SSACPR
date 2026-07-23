"""API 路由依赖注入"""
from typing import Optional
from fastapi import Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.utils.file_handler import file_handler, FileHandlerError


security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """
    获取当前用户（占位符，后续实现完整的认证）

    Returns:
        用户信息字典或 None
    """
    # TODO: 实现 JWT 验证
    # if not credentials:
    #     return None
    #
    # token = credentials.credentials
    # payload = decode_jwt(token)
    # return payload

    # 暂时返回 None（开发阶段）
    return None


async def validate_resume_file(file: UploadFile = File(...)) -> UploadFile:
    """
    验证简历文件

    Args:
        file: 上传的文件

    Returns:
        验证后的文件对象

    Raises:
        HTTPException: 文件验证失败
    """
    is_valid, error_msg = file_handler.validate_file(file)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    return file


def get_user_id(current_user: Optional[dict] = Depends(get_current_user)) -> Optional[int]:
    """
    获取用户 ID

    Args:
        current_user: 当前用户信息

    Returns:
        用户 ID 或 None
    """
    if current_user:
        return current_user.get('user_id')
    return None
