"""
用户管理服务
"""
import logging
from typing import Optional
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """用户管理服务"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """生成密码哈希"""
        return pwd_context.hash(password)

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[dict]:
        """根据用户名获取用户"""
        try:
            result = db.execute(
                text("""
                    SELECT id, username, password_hash, email, role, real_name
                    FROM users
                    WHERE username = :username
                """),
                {"username": username}
            )
            row = result.fetchone()
            if row:
                return {
                    "id": row[0],
                    "username": row[1],
                    "password_hash": row[2],
                    "email": row[3],
                    "role": row[4],
                    "real_name": row[5],
                }
            return None
        except Exception as e:
            logger.error(f"查询用户失败: {e}")
            return None

    @staticmethod
    def authenticate(db: Session, username: str, password: str) -> Optional[dict]:
        """验证用户登录"""
        user = UserService.get_user_by_username(db, username)
        if not user:
            return None
        if not UserService.verify_password(password, user["password_hash"]):
            return None
        # 不返回密码哈希
        user.pop("password_hash", None)
        return user

    @staticmethod
    def create_user(
        db: Session,
        username: str,
        password: str,
        email: str,
        role: str = "student",
        real_name: str = ""
    ) -> Optional[dict]:
        """创建用户"""
        try:
            password_hash = UserService.get_password_hash(password)
            result = db.execute(
                text("""
                    INSERT INTO users (username, password_hash, email, role, real_name)
                    VALUES (:username, :password_hash, :email, :role, :real_name)
                    RETURNING id, username, email, role, real_name
                """),
                {
                    "username": username,
                    "password_hash": password_hash,
                    "email": email,
                    "role": role,
                    "real_name": real_name,
                }
            )
            db.commit()
            row = result.fetchone()
            if row:
                return {
                    "id": row[0],
                    "username": row[1],
                    "email": row[2],
                    "role": row[3],
                    "real_name": row[4],
                }
            return None
        except Exception as e:
            db.rollback()
            logger.error(f"创建用户失败: {e}")
            return None


# 单例
user_service = UserService()
