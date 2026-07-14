"""
简历版本管理服务

注意事项：
1. 当前使用文件系统 + JSON 存储，适用于开发阶段和小规模场景
2. 并发控制：当前实现为单进程读写，不支持多进程并发
   - 如需支持多进程，建议使用文件锁（fcntl/msvcrt）或迁移到数据库
   - 生产环境建议迁移到 PostgreSQL 以获得完整的事务支持
3. 性能考虑：频繁读写会影响性能，建议添加缓存层（Redis）
"""
import json
import os
import shutil
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.schemas.resume_version import (
    ResumeVersion,
    ResumeVersionCreate,
    ResumeVersionUpdate,
    ResumeVersionListItem,
    ResumeVersionDetail,
    ResumeVersionCompare,
    ResumeVersionStats,
)


class ResumeVersionError(Exception):
    """简历版本管理异常"""
    pass


class ResumeVersionManager:
    """简历版本管理器"""

    def __init__(self, storage_path: str = "uploads/resumes/versions"):
        """
        初始化版本管理器

        Args:
            storage_path: 版本存储路径
        """
        self.storage_path = storage_path
        self.metadata_file = "metadata.json"
        self._ensure_storage_path()

    def _ensure_storage_path(self):
        """确保存储路径存在"""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path, exist_ok=True)

    def _get_user_path(self, user_id: int) -> str:
        """获取用户版本存储路径"""
        user_path = os.path.join(self.storage_path, str(user_id))
        if not os.path.exists(user_path):
            os.makedirs(user_path, exist_ok=True)
        return user_path

    def _get_metadata_path(self, user_id: int) -> str:
        """获取元数据文件路径"""
        return os.path.join(self._get_user_path(user_id), self.metadata_file)

    def _load_metadata(self, user_id: int) -> Dict[str, Any]:
        """加载元数据"""
        metadata_path = self._get_metadata_path(user_id)
        if not os.path.exists(metadata_path):
            return {"versions": [], "next_version": 1}

        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise ResumeVersionError(f"加载元数据失败: {str(e)}")

    def _save_metadata(self, user_id: int, metadata: Dict[str, Any]):
        """保存元数据"""
        metadata_path = self._get_metadata_path(user_id)
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            raise ResumeVersionError(f"保存元数据失败: {str(e)}")

    def _get_version_file_path(
        self,
        user_id: int,
        version: int,
        file_type: str
    ) -> str:
        """获取版本文件路径"""
        user_path = self._get_user_path(user_id)
        return os.path.join(user_path, f"v{version}.{file_type}")

    def create_version(
        self,
        user_id: int,
        file_path: str,
        file_type: str,
        version_data: ResumeVersionCreate,
        parsed_text: Optional[str] = None,
        structured_data: Optional[Dict[str, Any]] = None,
        score_data: Optional[Dict[str, Any]] = None,
        optimization_data: Optional[Dict[str, Any]] = None,
    ) -> ResumeVersion:
        """
        创建新版本

        Args:
            user_id: 用户ID
            file_path: 原始文件路径
            file_type: 文件类型
            version_data: 版本数据
            parsed_text: 解析后的文本
            structured_data: 结构化数据
            score_data: 评分数据
            optimization_data: 优化建议数据

        Returns:
            创建的版本
        """
        try:
            # 加载元数据
            metadata = self._load_metadata(user_id)

            # 获取版本号
            version_num = metadata["next_version"]

            # 复制文件到版本存储路径
            new_file_path = self._get_version_file_path(user_id, version_num, file_type)
            shutil.copy2(file_path, new_file_path)

            # 如果设置为激活版本，取消其他版本的激活状态
            if version_data.set_as_active:
                for v in metadata["versions"]:
                    v["is_active"] = False

            # 创建版本记录
            now = datetime.now()
            version = {
                "id": len(metadata["versions"]) + 1,
                "user_id": user_id,
                "version": version_num,
                "title": version_data.title,
                "description": version_data.description,
                "file_path": new_file_path,
                "file_type": file_type,
                "parsed_text": parsed_text,
                "structured_data": structured_data,
                "score_data": score_data,
                "optimization_data": optimization_data,
                "target_job": version_data.target_job,
                "is_active": version_data.set_as_active,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
            }

            # 添加到元数据
            metadata["versions"].append(version)
            metadata["next_version"] = version_num + 1

            # 保存元数据
            self._save_metadata(user_id, metadata)

            return ResumeVersion(**version)

        except Exception as e:
            raise ResumeVersionError(f"创建版本失败: {str(e)}")

    def get_version(self, user_id: int, version_id: int) -> Optional[ResumeVersionDetail]:
        """
        获取版本详情

        Args:
            user_id: 用户ID
            version_id: 版本ID

        Returns:
            版本详情
        """
        try:
            metadata = self._load_metadata(user_id)

            for v in metadata["versions"]:
                if v["id"] == version_id:
                    return ResumeVersionDetail(**v)

            return None

        except Exception as e:
            raise ResumeVersionError(f"获取版本失败: {str(e)}")

    def get_version_by_number(
        self,
        user_id: int,
        version_num: int
    ) -> Optional[ResumeVersionDetail]:
        """
        根据版本号获取版本

        Args:
            user_id: 用户ID
            version_num: 版本号

        Returns:
            版本详情
        """
        try:
            metadata = self._load_metadata(user_id)

            for v in metadata["versions"]:
                if v["version"] == version_num:
                    return ResumeVersionDetail(**v)

            return None

        except Exception as e:
            raise ResumeVersionError(f"获取版本失败: {str(e)}")

    def list_versions(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 10,
        active_only: bool = False,
    ) -> tuple[List[ResumeVersionListItem], int]:
        """
        获取版本列表

        Args:
            user_id: 用户ID
            page: 页码
            page_size: 每页大小
            active_only: 只返回激活版本

        Returns:
            (版本列表, 总数)
        """
        try:
            metadata = self._load_metadata(user_id)
            versions = metadata["versions"]

            # 过滤
            if active_only:
                versions = [v for v in versions if v.get("is_active", False)]

            # 按创建时间倒序排序
            versions.sort(key=lambda x: x.get("created_at", ""), reverse=True)

            # 分页
            total = len(versions)
            start = (page - 1) * page_size
            end = start + page_size
            page_versions = versions[start:end]

            # 构建列表项
            items = []
            for v in page_versions:
                # 提取总分
                total_score = None
                if v.get("score_data"):
                    total_score = v["score_data"].get("total_score")

                items.append(ResumeVersionListItem(
                    id=v["id"],
                    version=v["version"],
                    title=v["title"],
                    description=v.get("description"),
                    target_job=v.get("target_job"),
                    is_active=v.get("is_active", False),
                    total_score=total_score,
                    created_at=v["created_at"],
                ))

            return items, total

        except Exception as e:
            raise ResumeVersionError(f"获取版本列表失败: {str(e)}")

    def update_version(
        self,
        user_id: int,
        version_id: int,
        update_data: ResumeVersionUpdate,
    ) -> Optional[ResumeVersion]:
        """
        更新版本

        Args:
            user_id: 用户ID
            version_id: 版本ID
            update_data: 更新数据

        Returns:
            更新后的版本
        """
        try:
            metadata = self._load_metadata(user_id)

            for v in metadata["versions"]:
                if v["id"] == version_id:
                    # 更新字段
                    if update_data.title is not None:
                        v["title"] = update_data.title
                    if update_data.description is not None:
                        v["description"] = update_data.description
                    if update_data.target_job is not None:
                        v["target_job"] = update_data.target_job
                    if update_data.is_active is not None:
                        # 如果设置为激活，取消其他版本的激活状态
                        if update_data.is_active:
                            for other_v in metadata["versions"]:
                                if other_v["id"] != version_id:
                                    other_v["is_active"] = False
                        v["is_active"] = update_data.is_active

                    v["updated_at"] = datetime.now().isoformat()

                    # 保存元数据
                    self._save_metadata(user_id, metadata)

                    return ResumeVersion(**v)

            return None

        except Exception as e:
            raise ResumeVersionError(f"更新版本失败: {str(e)}")

    def delete_version(self, user_id: int, version_id: int) -> bool:
        """
        删除版本

        Args:
            user_id: 用户ID
            version_id: 版本ID

        Returns:
            是否删除成功
        """
        try:
            metadata = self._load_metadata(user_id)

            for i, v in enumerate(metadata["versions"]):
                if v["id"] == version_id:
                    # 删除文件
                    file_path = v["file_path"]
                    if os.path.exists(file_path):
                        os.remove(file_path)

                    # 从元数据中删除
                    metadata["versions"].pop(i)

                    # 保存元数据
                    self._save_metadata(user_id, metadata)

                    return True

            return False

        except Exception as e:
            raise ResumeVersionError(f"删除版本失败: {str(e)}")

    def set_active_version(self, user_id: int, version_id: int) -> bool:
        """
        设置激活版本

        Args:
            user_id: 用户ID
            version_id: 版本ID

        Returns:
            是否设置成功
        """
        try:
            metadata = self._load_metadata(user_id)

            found = False
            for v in metadata["versions"]:
                if v["id"] == version_id:
                    v["is_active"] = True
                    found = True
                else:
                    v["is_active"] = False

            if found:
                self._save_metadata(user_id, metadata)

            return found

        except Exception as e:
            raise ResumeVersionError(f"设置激活版本失败: {str(e)}")

    def get_active_version(self, user_id: int) -> Optional[ResumeVersionDetail]:
        """
        获取当前激活版本

        Args:
            user_id: 用户ID

        Returns:
            激活版本
        """
        try:
            metadata = self._load_metadata(user_id)

            for v in metadata["versions"]:
                if v.get("is_active", False):
                    return ResumeVersionDetail(**v)

            return None

        except Exception as e:
            raise ResumeVersionError(f"获取激活版本失败: {str(e)}")

    def compare_versions(
        self,
        user_id: int,
        version_id1: int,
        version_id2: int,
    ) -> Optional[ResumeVersionCompare]:
        """
        对比两个版本

        Args:
            user_id: 用户ID
            version_id1: 版本1 ID
            version_id2: 版本2 ID

        Returns:
            版本对比结果
        """
        try:
            v1 = self.get_version(user_id, version_id1)
            v2 = self.get_version(user_id, version_id2)

            if not v1 or not v2:
                return None

            # 计算差异
            differences = self._calculate_differences(v1, v2)

            return ResumeVersionCompare(
                version1=v1,
                version2=v2,
                differences=differences,
            )

        except Exception as e:
            raise ResumeVersionError(f"版本对比失败: {str(e)}")

    def _calculate_differences(
        self,
        v1: ResumeVersionDetail,
        v2: ResumeVersionDetail,
    ) -> Dict[str, Any]:
        """计算版本差异"""
        differences = {
            "basic_info": {},
            "score_changes": {},
            "content_changes": {},
        }

        # 基本信息差异
        if v1.title != v2.title:
            differences["basic_info"]["title"] = {
                "from": v1.title,
                "to": v2.title,
            }

        if v1.target_job != v2.target_job:
            differences["basic_info"]["target_job"] = {
                "from": v1.target_job,
                "to": v2.target_job,
            }

        # 评分差异
        if v1.score_data and v2.score_data:
            score1 = v1.score_data.get("total_score", 0)
            score2 = v2.score_data.get("total_score", 0)
            if score1 != score2:
                differences["score_changes"]["total_score"] = {
                    "from": score1,
                    "to": score2,
                    "change": score2 - score1,
                }

            # 各维度评分变化
            dimensions = ["completeness", "professionalism", "quantification", "project_depth"]
            for dim in dimensions:
                if dim in v1.score_data and dim in v2.score_data:
                    s1 = v1.score_data[dim].get("total_score", 0)
                    s2 = v2.score_data[dim].get("total_score", 0)
                    if s1 != s2:
                        differences["score_changes"][dim] = {
                            "from": s1,
                            "to": s2,
                            "change": s2 - s1,
                        }

        # 内容差异（简化版）
        if v1.structured_data and v2.structured_data:
            # 工作经历数量变化
            work1 = len(v1.structured_data.get("work_experience", []))
            work2 = len(v2.structured_data.get("work_experience", []))
            if work1 != work2:
                differences["content_changes"]["work_experience_count"] = {
                    "from": work1,
                    "to": work2,
                    "change": work2 - work1,
                }

            # 项目经验数量变化
            proj1 = len(v1.structured_data.get("project_experience", []))
            proj2 = len(v2.structured_data.get("project_experience", []))
            if proj1 != proj2:
                differences["content_changes"]["project_experience_count"] = {
                    "from": proj1,
                    "to": proj2,
                    "change": proj2 - proj1,
                }

            # 技能数量变化
            skill1 = len(v1.structured_data.get("skills", []))
            skill2 = len(v2.structured_data.get("skills", []))
            if skill1 != skill2:
                differences["content_changes"]["skills_count"] = {
                    "from": skill1,
                    "to": skill2,
                    "change": skill2 - skill1,
                }

        return differences

    def get_stats(self, user_id: int) -> ResumeVersionStats:
        """
        获取版本统计

        Args:
            user_id: 用户ID

        Returns:
            版本统计
        """
        try:
            metadata = self._load_metadata(user_id)
            versions = metadata["versions"]

            total_versions = len(versions)

            # 获取激活版本
            active_version = None
            for v in versions:
                if v.get("is_active", False):
                    total_score = None
                    if v.get("score_data"):
                        total_score = v["score_data"].get("total_score")

                    active_version = ResumeVersionListItem(
                        id=v["id"],
                        version=v["version"],
                        title=v["title"],
                        description=v.get("description"),
                        target_job=v.get("target_job"),
                        is_active=True,
                        total_score=total_score,
                        created_at=v["created_at"],
                    )
                    break

            # 获取最新版本
            latest_version = None
            if versions:
                sorted_versions = sorted(versions, key=lambda x: x["version"], reverse=True)
                v = sorted_versions[0]
                total_score = None
                if v.get("score_data"):
                    total_score = v["score_data"].get("total_score")

                latest_version = ResumeVersionListItem(
                    id=v["id"],
                    version=v["version"],
                    title=v["title"],
                    description=v.get("description"),
                    target_job=v.get("target_job"),
                    is_active=v.get("is_active", False),
                    total_score=total_score,
                    created_at=v["created_at"],
                )

            # 评分趋势
            score_trend = []
            sorted_versions = sorted(versions, key=lambda x: x["version"])
            for v in sorted_versions:
                if v.get("score_data"):
                    score_trend.append({
                        "version": v["version"],
                        "title": v["title"],
                        "total_score": v["score_data"].get("total_score", 0),
                        "created_at": v["created_at"],
                    })

            return ResumeVersionStats(
                total_versions=total_versions,
                active_version=active_version,
                latest_version=latest_version,
                score_trend=score_trend,
            )

        except Exception as e:
            raise ResumeVersionError(f"获取统计信息失败: {str(e)}")


# 全局实例
resume_version_manager = ResumeVersionManager()
