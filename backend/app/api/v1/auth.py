"""
用户认证接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.auth import create_access_token, get_current_user
from app.db import get_db
from app.services.user_service import user_service

router = APIRouter(prefix="/auth", tags=["认证"])


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class RegisterRequest(BaseModel):
    """注册请求"""
    username: str
    password: str
    email: EmailStr
    real_name: str = ""


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    role: str
    real_name: str = ""


class UserInfoResponse(BaseModel):
    """用户信息响应"""
    user_id: int
    username: str
    role: str
    email: str = ""
    real_name: str = ""


@router.post("/login", response_model=LoginResponse, summary="用户登录")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录接口

    支持从数据库验证用户
    返回 JWT token，用于后续 API 调用
    """
    # 从数据库验证用户
    user = user_service.authenticate(db, request.username, request.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 生成 JWT token
    token = create_access_token(
        user_id=user["id"],
        username=user["username"],
        role=user["role"]
    )

    return LoginResponse(
        access_token=token,
        user_id=user["id"],
        username=user["username"],
        role=user["role"],
        real_name=user.get("real_name", "")
    )


@router.post("/register", response_model=LoginResponse, summary="用户注册")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    用户注册接口

    创建新用户账号（默认角色为student）
    """
    # 检查用户名是否已存在
    existing_user = user_service.get_user_by_username(db, request.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在",
        )

    # 创建用户
    user = user_service.create_user(
        db=db,
        username=request.username,
        password=request.password,
        email=request.email,
        role="student",  # 新注册用户默认为学生
        real_name=request.real_name
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败，请稍后重试",
        )

    # 生成 JWT token
    token = create_access_token(
        user_id=user["id"],
        username=user["username"],
        role=user["role"]
    )

    return LoginResponse(
        access_token=token,
        user_id=user["id"],
        username=user["username"],
        role=user["role"],
        real_name=user.get("real_name", "")
    )


@router.get("/me", response_model=UserInfoResponse, summary="获取当前用户信息")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    获取当前登录用户信息

    需要在请求头中携带有效的 JWT token
    """
    return UserInfoResponse(
        user_id=current_user.get("user_id", 0),
        username=current_user.get("username", ""),
        role=current_user.get("role", "student"),
        email=current_user.get("email", ""),
        real_name=current_user.get("real_name", "")
    )


@router.get("/test", summary="测试认证（需要登录）")
async def test_auth(current_user: dict = Depends(get_current_user)):
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
