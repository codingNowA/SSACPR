"""
面试题推荐功能测试
"""
import sys
from pathlib import Path

# 添加backend目录到Python路径，支持直接运行脚本
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
from app.services.interview_questions_service import interview_service


def test_recommend_java_backend():
    """测试Java后端岗位面试题推荐"""
    job_text = """
    岗位：Java后端开发工程师

    岗位要求：
    1. 本科及以上学历，计算机相关专业
    2. 3年以上Java开发经验
    3. 熟练掌握Java、Spring Boot、MyBatis
    4. 熟悉MySQL、Redis等数据库
    5. 了解微服务架构

    薪资：15k-25k
    """

    result = interview_service.recommend(job_text, max_questions=15)

    assert result.success is True
    assert result.recommendation.total_questions > 0
    assert "Java" in result.recommendation.job_title

    # 应该包含Java相关题目
    questions = result.recommendation.questions
    java_questions = [q for q in questions if "Java" in q.tags]
    assert len(java_questions) > 0

    # 应该包含数据库题目
    db_questions = [q for q in questions if any(tag in ["数据库", "MySQL", "Redis"] for tag in q.tags)]
    assert len(db_questions) > 0

    print(f"\n推荐题目数量: {result.recommendation.total_questions}")
    print(f"分类统计: {result.recommendation.questions_by_category}")


def test_recommend_python_developer():
    """测试Python开发岗位面试题推荐"""
    job_text = """
    Python开发工程师

    要求：
    - 熟悉Python、Django或Flask框架
    - 了解数据库MySQL、MongoDB
    - 有API开发经验

    待遇：12k-20k
    """

    result = interview_service.recommend(job_text, max_questions=10)

    assert result.success is True
    assert result.recommendation.total_questions > 0

    questions = result.recommendation.questions
    python_questions = [q for q in questions if "Python" in q.tags]
    assert len(python_questions) > 0

    print(f"\n推荐题目数量: {result.recommendation.total_questions}")


def test_recommend_frontend_developer():
    """测试前端开发岗位面试题推荐"""
    job_text = """
    前端开发工程师

    职责：
    - 负责公司Web前端开发
    - 使用React或Vue框架
    - 与后端API对接

    要求：
    - 熟练掌握HTML、CSS、JavaScript
    - 熟悉React或Vue
    - 了解Webpack、Node.js

    薪资：10k-18k
    """

    result = interview_service.recommend(job_text, max_questions=12)

    assert result.success is True
    questions = result.recommendation.questions

    # 应该包含前端相关题目
    frontend_questions = [q for q in questions if any(
        tag in ["前端", "JavaScript", "React", "Vue"] for tag in q.tags
    )]
    assert len(frontend_questions) > 0

    print(f"\n推荐题目数量: {result.recommendation.total_questions}")
    print(f"分类统计: {result.recommendation.questions_by_category}")


def test_recommend_ai_algorithm():
    """测试AI算法工程师面试题推荐"""
    job_text = """
    AI算法工程师

    岗位职责：
    - 负责机器学习算法研发
    - 模型训练和优化

    任职要求：
    - 硕士及以上学历
    - 熟悉Python、TensorFlow或PyTorch
    - 熟悉深度学习、NLP或计算机视觉
    - 扎实的算法和数据结构基础

    薪资：20k-35k
    """

    result = interview_service.recommend(job_text, max_questions=20)

    assert result.success is True
    questions = result.recommendation.questions

    # 应该包含机器学习和算法题目
    ml_questions = [q for q in questions if any(
        tag in ["机器学习", "深度学习", "算法"] for tag in q.tags
    )]
    assert len(ml_questions) > 0

    print(f"\n推荐题目数量: {result.recommendation.total_questions}")
    print(f"分类统计: {result.recommendation.questions_by_category}")


def test_max_questions_limit():
    """测试题目数量限制"""
    job_text = "Java开发工程师，要求熟悉Java、Spring Boot、MySQL"

    # 测试不同的数量限制
    result_5 = interview_service.recommend(job_text, max_questions=5)
    assert result_5.recommendation.total_questions <= 5

    result_20 = interview_service.recommend(job_text, max_questions=20)
    assert result_20.recommendation.total_questions <= 20

    print(f"\nmax_questions=5: {result_5.recommendation.total_questions}道题")
    print(f"max_questions=20: {result_20.recommendation.total_questions}道题")


def test_question_structure():
    """测试面试题结构完整性"""
    job_text = "Python后端开发工程师，熟悉Django、MySQL"

    result = interview_service.recommend(job_text, max_questions=5)

    for question in result.recommendation.questions:
        # 每道题必须有的字段
        assert question.question, "题目内容不能为空"
        assert question.category, "分类不能为空"
        assert question.difficulty in ["简单", "中等", "困难"], "难度必须是：简单/中等/困难"
        assert len(question.key_points) > 0, "必须有答案要点"
        assert len(question.tags) > 0, "必须有标签"

        print(f"\n题目: {question.question}")
        print(f"分类: {question.category} | 难度: {question.difficulty}")
        print(f"答案要点: {len(question.key_points)}条")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
