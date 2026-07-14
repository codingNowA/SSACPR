"""
用户认证接口
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.core.auth import create_access_token

router = APIRouter(prefix="/auth", tags=["认证"])


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str


@router.post("/login", response_model=LoginResponse, summary="用户登录")
async def login(request: LoginRequest):
    """
    用户登录接口

    测试账号：
    - 用户名: test_user
    - 密码: test123

    返回 JWT token，用于后续 API 调用
    """
    # 这是一个简化的演示版本
    # 生产环境需要从数据库验证用户名和密码（密码需要加密存储）

    # 演示用的测试账号
    test_users = {
        "test_user": {"password": "test123", "user_id": 1, "role": "user"},
        "admin": {"password": "admin123", "user_id": 2, "role": "admin"},
    }

    # 验证用户名
    if request.username not in test_users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    user = test_users[request.username]

    # 验证密码（实际应该对比加密后的密码）
    if request.password != user["password"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 生成 JWT token
    token = create_access_token(
        user_id=user["user_id"],
        username=request.username,
        role=user["role"]
    )

    return LoginResponse(
        access_token=token,
        user_id=user["user_id"],
        username=request.username
    )


@router.get("/test", summary="测试认证（需要登录）")
async def test_auth(current_user: dict = None):
    """
    测试接口 - 需要登录后才能访问

    在 Swagger UI 中：
    1. 先调用 /auth/login 获取 token
    2. 点击右上角 🔒 Authorize
    3. 输入: Bearer <your_token>
    4. 然后才能调用这个接口
    """
    return {
        "message": "认证成功！",
        "user": current_user if current_user else "开发模式（未启用认证）"
    }
