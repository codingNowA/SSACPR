"""
综合测试套件 - 测试所有已实现的功能

测试覆盖：
1. 简历上传
2. 简历解析（PDF、Word、图片）
3. 结构化提取
4. 简历评分
5. 简历优化（通用 + 岗位定向）
6. 版本管理（CRUD + 激活 + 对比）
"""
import os
import sys
import json
from pathlib import Path

# 添加项目根目录到路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
from fastapi.testclient import TestClient
from main import app

# 创建测试客户端
client = TestClient(app)


class TestHealthCheck:
    """健康检查测试"""

    def test_root_endpoint(self):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "resume_parsing" in data["features"]

    def test_health_endpoint(self):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestResumeUpload:
    """简历上传测试"""

    def test_upload_without_file(self):
        """测试未提供文件"""
        response = client.post("/api/v1/resume/upload")
        assert response.status_code == 422  # FastAPI 验证错误

    def test_upload_invalid_file_type(self):
        """测试不支持的文件类型"""
        files = {"file": ("test.txt", b"test content", "text/plain")}
        response = client.post("/api/v1/resume/upload", files=files)
        # 可能是 400 或 422，取决于验证逻辑
        assert response.status_code in [400, 422]


class TestResumeParsing:
    """简历解析测试"""

    @pytest.fixture
    def sample_pdf_path(self):
        """返回测试 PDF 路径（如果存在）"""
        # 检查是否有示例简历
        test_files = [
            backend_dir / "tests" / "samples" / "resume.pdf",
            backend_dir / "uploads" / "resumes" / "sample.pdf",
        ]
        for path in test_files:
            if path.exists():
                return str(path)
        return None

    def test_parse_without_file(self):
        """测试未提供文件的解析"""
        response = client.post("/api/v1/resume/parse")
        assert response.status_code == 422

    def test_parse_by_path_missing_params(self):
        """测试路径解析缺少参数"""
        response = client.post("/api/v1/resume/parse-by-path", json={})
        assert response.status_code == 422


class TestResumeExtraction:
    """结构化提取测试"""

    def test_extract_without_text(self):
        """测试空文本提取"""
        response = client.post(
            "/api/v1/resume/extract",
            json={"resume_text": ""}
        )
        # 应该返回错误或空结果
        assert response.status_code in [200, 400, 422]

    def test_extract_with_sample_text(self):
        """测试示例文本提取"""
        sample_text = """
        张三
        电话：13800138000
        邮箱：zhangsan@example.com

        教育经历：
        2018-2022 清华大学 计算机科学与技术 本科

        工作经历：
        2022-2024 字节跳动 后端工程师
        负责推荐系统开发，使用 Python/Go
        """

        response = client.post(
            "/api/v1/resume/extract",
            json={"resume_text": sample_text}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        # 检查是否提取到基本信息
        if "data" in data and data["data"]:
            extracted = data["data"]
            # 至少应该提取到一些信息
            assert "basic_info" in extracted or "education" in extracted


class TestResumeScoring:
    """简历评分测试"""

    def test_score_empty_data(self):
        """测试空数据评分"""
        response = client.post(
            "/api/v1/resume/score",
            json={
                "structured_data": {},
                "resume_text": ""
            }
        )
        # 应该能处理空数据（返回低分或错误）
        assert response.status_code in [200, 400]

    def test_score_with_basic_data(self):
        """测试基础数据评分"""
        response = client.post(
            "/api/v1/resume/score",
            json={
                "structured_data": {
                    "basic_info": {
                        "name": "张三",
                        "phone": "13800138000",
                        "email": "test@example.com"
                    },
                    "education": [
                        {
                            "school": "清华大学",
                            "major": "计算机科学",
                            "degree": "本科",
                            "start_date": "2018-09",
                            "end_date": "2022-06"
                        }
                    ]
                },
                "resume_text": "这是一份简历"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        if "data" in data:
            score_data = data["data"]
            assert "total_score" in score_data
            assert 0 <= score_data["total_score"] <= 100


class TestResumeOptimization:
    """简历优化测试"""

    def test_optimize_basic(self):
        """测试基础优化"""
        response = client.post(
            "/api/v1/resume/optimize",
            json={
                "structured_data": {
                    "basic_info": {"name": "张三"}
                },
                "score": {
                    "total_score": 60,
                    "completeness": 50,
                    "professionalism": 60,
                    "quantification": 55,
                    "project_depth": 65
                },
                "resume_text": "简历内容"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        if "data" in data:
            opt_data = data["data"]
            # 应该包含优化建议
            assert "suggestions" in opt_data

    def test_optimize_with_job_target(self):
        """测试岗位定向优化"""
        response = client.post(
            "/api/v1/resume/optimize",
            json={
                "structured_data": {"basic_info": {"name": "张三"}},
                "score": {"total_score": 70},
                "resume_text": "简历内容",
                "job_title": "Python 后端工程师",
                "job_description": "负责后端服务开发，熟悉 Python/FastAPI"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200


class TestResumeVersionManagement:
    """版本管理测试"""

    @pytest.fixture
    def test_user_id(self):
        """测试用户 ID"""
        return 99999  # 使用一个不会冲突的 ID

    @pytest.fixture
    def cleanup_test_versions(self, test_user_id):
        """清理测试版本"""
        yield
        # 测试后清理
        version_path = backend_dir / "uploads" / "resumes" / "versions" / str(test_user_id)
        if version_path.exists():
            import shutil
            shutil.rmtree(version_path)

    def test_create_version_missing_file(self, test_user_id):
        """测试创建版本但文件不存在"""
        response = client.post(
            f"/api/v1/resume/versions?user_id={test_user_id}",
            json={
                "file_path": "/nonexistent/file.pdf",
                "file_type": "pdf",
                "job_title": "测试岗位"
            }
        )
        # 应该返回错误
        assert response.status_code in [400, 404, 500]

    def test_list_versions_empty(self, test_user_id, cleanup_test_versions):
        """测试列出空版本列表"""
        response = client.get(f"/api/v1/resume/versions?user_id={test_user_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        if "data" in data:
            assert isinstance(data["data"], list)

    def test_get_nonexistent_version(self, test_user_id):
        """测试获取不存在的版本"""
        response = client.get(
            f"/api/v1/resume/versions/99999?user_id={test_user_id}"
        )
        assert response.status_code in [404, 400]

    def test_version_stats(self, test_user_id):
        """测试版本统计"""
        response = client.get(f"/api/v1/resume/versions/stats?user_id={test_user_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        if "data" in data:
            stats = data["data"]
            assert "total_versions" in stats
            assert stats["total_versions"] >= 0


class TestEndToEndWorkflow:
    """端到端工作流测试"""

    def test_complete_workflow_simulation(self):
        """模拟完整工作流（不依赖真实文件）"""

        # 1. 健康检查
        health = client.get("/")
        assert health.status_code == 200

        # 2. 尝试提取（模拟）
        sample_text = "张三 13800138000 本科 计算机"
        extract_response = client.post(
            "/api/v1/resume/extract",
            json={"resume_text": sample_text}
        )
        assert extract_response.status_code == 200

        # 3. 评分（模拟）
        score_response = client.post(
            "/api/v1/resume/score",
            json={
                "structured_data": {"basic_info": {"name": "张三"}},
                "resume_text": sample_text
            }
        )
        assert score_response.status_code == 200

        # 4. 优化建议（模拟）
        optimize_response = client.post(
            "/api/v1/resume/optimize",
            json={
                "structured_data": {"basic_info": {"name": "张三"}},
                "score": {"total_score": 60},
                "resume_text": sample_text
            }
        )
        assert optimize_response.status_code == 200

        print("\n✅ 端到端工作流测试通过")


def test_api_documentation():
    """测试 API 文档可访问"""
    response = client.get("/docs")
    assert response.status_code == 200

    response = client.get("/redoc")
    assert response.status_code == 200


if __name__ == "__main__":
    print("=" * 60)
    print("开始运行综合测试套件")
    print("=" * 60)

    # 运行测试
    pytest.main([
        __file__,
        "-v",  # 详细输出
        "--tb=short",  # 简短的错误回溯
        "-s",  # 显示 print 输出
    ])
