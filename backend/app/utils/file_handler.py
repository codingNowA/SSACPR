"""
文件处理工具模块
负责文件上传、验证、存储等基础操作
"""
import os
import uuid
from pathlib import Path
from typing import Optional, Tuple

from fastapi import UploadFile
from config.settings import get_setting


class FileHandlerError(Exception):
    """文件处理异常"""
    pass


class FileHandler:
    """文件处理器"""

    # 支持的简历文件类型
    ALLOWED_EXTENSIONS = {
        'pdf': ['application/pdf'],
        'doc': ['application/msword'],
        'docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
        'png': ['image/png'],
        'jpg': ['image/jpeg'],
        'jpeg': ['image/jpeg'],
    }

    # 最大文件大小（10MB）
    MAX_FILE_SIZE = int(get_setting('MAX_UPLOAD_SIZE', '10485760'))

    def __init__(self, upload_dir: Optional[str] = None):
        self.upload_dir = Path(upload_dir or get_setting('UPLOAD_DIR', './uploads'))
        self.resume_dir = self.upload_dir / 'resumes'
        self.temp_dir = self.upload_dir / 'temp'

        # 创建目录
        self.resume_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def validate_file(self, file: UploadFile) -> Tuple[bool, str]:
        """
        验证文件是否符合要求

        Args:
            file: 上传的文件对象

        Returns:
            (是否有效, 错误信息)
        """
        if not file.filename:
            return False, "文件名不能为空"

        # 检查文件扩展名
        ext = self._get_file_extension(file.filename)
        if ext not in self.ALLOWED_EXTENSIONS:
            return False, f"不支持的文件类型: {ext}，支持的类型: {', '.join(self.ALLOWED_EXTENSIONS.keys())}"

        # 检查 MIME 类型
        if file.content_type not in self.ALLOWED_EXTENSIONS[ext]:
            return False, f"文件 MIME 类型不匹配: {file.content_type}"

        return True, ""

    async def save_resume(self, file: UploadFile, user_id: Optional[int] = None) -> Tuple[str, str]:
        """
        保存简历文件

        Args:
            file: 上传的文件对象
            user_id: 用户ID（可选）

        Returns:
            (文件路径, 文件类型)

        Raises:
            FileHandlerError: 文件处理失败
        """
        # 验证文件
        is_valid, error_msg = self.validate_file(file)
        if not is_valid:
            raise FileHandlerError(error_msg)

        # 生成唯一文件名
        ext = self._get_file_extension(file.filename)
        unique_filename = self._generate_unique_filename(ext, user_id)

        # 保存文件
        file_path = self.resume_dir / unique_filename
        try:
            content = await file.read()

            # 检查文件大小
            if len(content) > self.MAX_FILE_SIZE:
                raise FileHandlerError(f"文件大小超过限制: {len(content)} > {self.MAX_FILE_SIZE}")

            with open(file_path, 'wb') as f:
                f.write(content)

            return str(file_path), ext

        except Exception as e:
            # 清理失败的文件
            if file_path.exists():
                file_path.unlink()
            raise FileHandlerError(f"文件保存失败: {str(e)}")

    async def save_temp_file(self, file: UploadFile) -> str:
        """
        保存临时文件

        Args:
            file: 上传的文件对象

        Returns:
            临时文件路径
        """
        ext = self._get_file_extension(file.filename)
        unique_filename = f"temp_{uuid.uuid4().hex}.{ext}"
        file_path = self.temp_dir / unique_filename

        try:
            content = await file.read()
            with open(file_path, 'wb') as f:
                f.write(content)
            return str(file_path)
        except Exception as e:
            raise FileHandlerError(f"临时文件保存失败: {str(e)}")

    def delete_file(self, file_path: str) -> bool:
        """
        删除文件

        Args:
            file_path: 文件路径

        Returns:
            是否删除成功
        """
        try:
            path = Path(file_path)
            if path.exists() and path.is_file():
                path.unlink()
                return True
            return False
        except Exception:
            return False

    def get_file_info(self, file_path: str) -> dict:
        """
        获取文件信息

        Args:
            file_path: 文件路径

        Returns:
            文件信息字典
        """
        path = Path(file_path)
        if not path.exists():
            raise FileHandlerError(f"文件不存在: {file_path}")

        return {
            'filename': path.name,
            'extension': path.suffix[1:],
            'size': path.stat().st_size,
            'created_at': path.stat().st_ctime,
            'modified_at': path.stat().st_mtime,
        }

    @staticmethod
    def _get_file_extension(filename: str) -> str:
        """获取文件扩展名（小写）"""
        return filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

    @staticmethod
    def _generate_unique_filename(ext: str, user_id: Optional[int] = None) -> str:
        """生成唯一文件名"""
        unique_id = uuid.uuid4().hex
        if user_id:
            return f"resume_{user_id}_{unique_id}.{ext}"
        return f"resume_{unique_id}.{ext}"


# 全局文件处理器实例
file_handler = FileHandler()
