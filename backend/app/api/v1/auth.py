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
        role="user",  # 新注册用户默认为普通用户
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
        role=current_user.get("role", "user"),
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


class UserStatsResponse(BaseModel):
    """用户统计信息响应"""
    user_id: int
    username: str
    role: str
    email: str = ""
    real_name: str = ""
    resume_count: int = 0
    version_count: int = 0
    match_count: int = 0
    created_at: str = ""
    last_login: str = ""


@router.get("/stats", summary="获取用户统计信息")
async def get_user_stats(
    user_id: int = None,
    current_user: dict = Depends(get_current_user),
):
    """
    获取用户统计信息：简历数、版本数、匹配次数等
    不传 user_id 时默认查当前登录用户
    """
    from app.services.job_service import get_db_pool

    target_user_id = user_id or current_user.get("user_id", 1)

    pool = await get_db_pool()

    async with pool.acquire() as conn:
        # 查用户基本信息
        user_row = await conn.fetchrow(
            "SELECT id, username, role, email, real_name, created_at, updated_at FROM users WHERE id = $1",
            target_user_id
        )

        if not user_row:
            raise HTTPException(status_code=404, detail="用户不存在")

        # 简历数
        resume_count = await conn.fetchval(
            "SELECT COUNT(*) FROM resumes WHERE user_id = $1",
            target_user_id
        ) or 0

        # 版本数
        version_count = await conn.fetchval(
            "SELECT COUNT(*) FROM resume_versions rv JOIN resumes r ON rv.resume_id = r.id WHERE r.user_id = $1",
            target_user_id
        ) or 0

        # 匹配次数（统计不同的简历和日期组合，避免一次匹配20个岗位算20次）
        match_count = await conn.fetchval(
            """
            SELECT COUNT(DISTINCT (resume_id, DATE(m.created_at)))
            FROM matches m
            JOIN resumes r ON m.resume_id = r.id
            WHERE r.user_id = $1
            """,
            target_user_id
        ) or 0

    return UserStatsResponse(
        user_id=user_row["id"],
        username=user_row["username"],
        role=user_row["role"],
        email=user_row["email"] or "",
        real_name=user_row["real_name"] or "",
        resume_count=resume_count,
        version_count=version_count,
        match_count=match_count,
        created_at=str(user_row["created_at"]) if user_row["created_at"] else "",
        last_login=str(user_row["updated_at"]) if user_row["updated_at"] else "",
    )
