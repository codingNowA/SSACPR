"""
JWT 认证依赖

- 从 Authorization: Bearer <token> 提取并验证 JWT
- 开发环境下允许跳过认证（APP_ENV=development 且未配置 JWT_SECRET_KEY）
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# 配置
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
APP_ENV = os.getenv("APP_ENV", "development")

# Bearer scheme — swagger 自动显示锁图标
_bearer_scheme = HTTPBearer(auto_error=False)


def _is_auth_disabled() -> bool:
    """开发环境下且未配置密钥时，跳过认证"""
    return APP_ENV == "development" and not JWT_SECRET


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
) -> dict:
    """
    FastAPI 依赖注入：验证 JWT 并返回用户信息

    开发环境下未配置密钥时自动放行，返回占位用户。
    """
    if _is_auth_disabled():
        return {"user_id": 0, "username": "dev_user", "role": "admin"}

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: Optional[int] = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证令牌",
            )
        return {
            "user_id": user_id,
            "username": payload.get("username", ""),
            "role": payload.get("role", "user"),
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或已过期的认证令牌",
        )


def create_access_token(user_id: int, username: str, role: str = "user") -> str:
    """生成 JWT access token"""
    if not JWT_SECRET:
        raise RuntimeError("JWT_SECRET_KEY 未配置，无法生成令牌")
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
