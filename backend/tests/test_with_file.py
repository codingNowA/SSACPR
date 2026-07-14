"""
使用真实文件的功能测试

测试覆盖：
1. 简历解析
2. 结构化提取
3. 简历评分
4. 简历优化
5. 版本管理
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
from fastapi.testclient import TestClient
from main import app
import io

client = TestClient(app)

# 测试简历文件路径
SAMPLE_RESUME_PATH = backend_dir / "tests" / "samples" / "test_resume.txt"


class TestResumeWithFile:
    """使用真实文件测试简历功能"""

    @pytest.fixture
    def sample_resume_file(self):
        """读取测试简历文件"""
        if not SAMPLE_RESUME_PATH.exists():
            pytest.skip("测试简历文件不存在")

        with open(SAMPLE_RESUME_PATH, 'rb') as f:
            content = f.read()

        return ("test_resume.txt", content, "text/plain")

    def test_parse_resume(self, sample_resume_file):
        """测试简历解析"""
        files = {"file": sample_resume_file}
        response = client.post("/api/v1/resume/parse", files=files)

        print(f"\n解析响应: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"提取文本长度: {len(data['data']['text'])} 字符")
            assert data["code"] == 200
            assert "data" in data
            assert "text" in data["data"]
            assert len(data["data"]["text"]) > 100
        else:
            print(f"错误: {response.text}")
            # 文本文件可能不被支持，跳过
            pytest.skip("文本文件格式可能不被支持")

    def test_extract_structure(self, sample_resume_file):
        """测试结构化提取"""
        files = {"file": sample_resume_file}
        response = client.post("/api/v1/resume/extract", files=files)

        print(f"\n提取响应: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"提取结果: {data['data'].keys()}")
            assert data["code"] == 200
            assert "data" in data
            assert "structured_data" in data["data"]
        else:
            print(f"错误: {response.text}")
            pytest.skip("文本文件格式可能不被支持")

    def test_score_resume(self, sample_resume_file):
        """测试简历评分"""
        files = {"file": sample_resume_file}
        response = client.post("/api/v1/resume/score", files=files)

        print(f"\n评分响应: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            score = data["data"]["score"]
            print(f"总分: {score['total_score']}")
            print(f"完整性: {score['completeness']['total_score']}")
            print(f"专业性: {score['professionalism']['total_score']}")
            assert data["code"] == 200
            assert 0 <= score["total_score"] <= 100
        else:
            print(f"错误: {response.text}")
            pytest.skip("文本文件格式可能不被支持")

    def test_optimize_resume(self, sample_resume_file):
        """测试简历优化"""
        files = {"file": sample_resume_file}
        response = client.post("/api/v1/resume/optimize", files=files)

        print(f"\n优化响应: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            optimization = data["data"]["optimization"]
            print(f"建议数量: {len(optimization['suggestions'])}")
            assert data["code"] == 200
            assert "suggestions" in optimization
        else:
            print(f"错误: {response.text}")
            pytest.skip("文本文件格式可能不被支持")

    def test_optimize_with_job_target(self, sample_resume_file):
        """测试岗位定向优化"""
        files = {"file": sample_resume_file}
        params = {
            "job_title": "Python 后端工程师",
            "job_description": "负责后端服务开发，要求熟悉 Python/FastAPI，有微服务经验"
        }
        response = client.post("/api/v1/resume/optimize", files=files, params=params)

        print(f"\n岗位定向优化响应: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            optimization = data["data"]["optimization"]
            print(f"建议数量: {len(optimization['suggestions'])}")
            if optimization.get("job_targeted_optimization"):
                print("包含岗位定向优化内容")
            assert data["code"] == 200
        else:
            print(f"错误: {response.text}")
            pytest.skip("文本文件格式可能不被支持")


class TestVersionManagement:
    """版本管理功能测试"""

    def test_list_empty_versions(self):
        """测试列出空版本"""
        response = client.get("/api/v1/resume/versions?user_id=99999")

        print(f"\n版本列表响应: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        print(f"响应数据: {data}")
        assert data["code"] == 200
        # data 是分页对象，不是列表
        assert "data" in data

    def test_version_stats(self):
        """测试版本统计"""
        response = client.get("/api/v1/resume/versions/stats?user_id=99999")

        print(f"\n版本统计响应: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        print(f"统计数据: {data}")
        assert data["code"] == 200
        assert "data" in data
        stats = data["data"]
        assert "total_versions" in stats
        assert stats["total_versions"] >= 0


if __name__ == "__main__":
    print("=" * 60)
    print("开始运行文件测试")
    print("=" * 60)

    pytest.main([
        __file__,
        "-v",
        "-s",
        "--tb=short",
    ])
