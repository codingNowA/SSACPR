"""
岗位信息提取功能测试
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.schemas.job_extraction import JobExtractionRequest
from app.services.job_extraction_service import job_info_extractor


def test_extract_complete_job_info():
    """测试完整的岗位信息提取"""
    job_text = """
    高级Java开发工程师

    岗位职责：
    1. 负责公司核心业务系统的开发和维护
    2. 参与系统架构设计和技术方案制定
    3. 优化系统性能，提升用户体验

    任职要求：
    - 本科及以上学历，计算机相关专业
    - 3-5年Java开发经验
    - 精通Spring Boot、微服务架构
    - 熟悉MySQL、Redis等数据库
    - 有大型互联网项目经验者优先

    薪资待遇：20k-35k
    工作地点：北京-朝阳区
    """

    request = JobExtractionRequest(job_text=job_text)
    result = job_info_extractor.extract(request.job_text)

    print("\n" + "="*60)
    print("测试1: 完整岗位信息提取")
    print("="*60)
    print(f"提取成功: {result.success}")
    print(f"置信度: {result.confidence_score}")
    print(f"\n提取的信息:")
    print(f"  岗位名称: {result.extracted_info.job_title}")
    print(f"  学历要求: {result.extracted_info.education_requirement}")
    print(f"  经验要求: {result.extracted_info.experience_requirement}")
    print(f"  薪资范围: {result.extracted_info.salary_range}")
    print(f"  工作地点: {result.extracted_info.location}")
    print(f"  必备技能: {', '.join(result.extracted_info.required_skills)}")
    print(f"  优先技能: {', '.join(result.extracted_info.preferred_skills)}")
    print(f"  所属行业: {result.extracted_info.industry}")
    print(f"\n提取说明: {', '.join(result.extraction_notes)}")
    if result.missing_fields:
        print(f"缺失字段: {', '.join(result.missing_fields)}")

    assert result.success is True
    assert result.extracted_info.job_title == "高级Java开发工程师"
    assert result.extracted_info.education_requirement is not None
    assert result.extracted_info.experience_requirement is not None
    assert result.extracted_info.salary_range is not None
    assert result.extracted_info.location is not None
    assert len(result.extracted_info.required_skills) > 0
    assert result.confidence_score >= 0.7


def test_extract_frontend_job():
    """测试前端岗位信息提取"""
    job_text = """
    前端开发工程师（React）

    我们正在寻找一位热爱前端技术的工程师加入团队！

    工作职责：
    - 使用React、TypeScript开发Web应用
    - 与设计师和后端工程师协作

    要求：
    本科学历，1-3年前端开发经验
    熟悉React、Vue、HTML、CSS、JavaScript
    了解Webpack、Node.js优先

    月薪12k-20k，上海张江
    """

    result = job_info_extractor.extract(job_text)

    print("\n" + "="*60)
    print("测试2: 前端岗位信息提取")
    print("="*60)
    print(f"岗位名称: {result.extracted_info.job_title}")
    print(f"学历要求: {result.extracted_info.education_requirement}")
    print(f"经验要求: {result.extracted_info.experience_requirement}")
    print(f"薪资范围: {result.extracted_info.salary_range}")
    print(f"工作地点: {result.extracted_info.location}")
    print(f"必备技能: {', '.join(result.extracted_info.required_skills)}")
    print(f"优先技能: {', '.join(result.extracted_info.preferred_skills)}")
    print(f"置信度: {result.confidence_score}")

    assert "React" in result.extracted_info.required_skills
    assert result.extracted_info.experience_requirement is not None


def test_extract_ai_job():
    """测试AI算法岗位信息提取"""
    job_text = """
    高级算法工程师-深度学习方向

    岗位要求：
    硕士及以上学历，计算机、人工智能相关专业
    5年以上算法研发经验
    精通Python、PyTorch、TensorFlow
    有NLP或计算机视觉项目经验
    顶会论文发表者优先

    薪资：40万-70万/年
    地点：深圳南山区
    """

    result = job_info_extractor.extract(job_text)

    print("\n" + "="*60)
    print("测试3: AI算法岗位信息提取")
    print("="*60)
    print(f"岗位名称: {result.extracted_info.job_title}")
    print(f"学历要求: {result.extracted_info.education_requirement}")
    print(f"经验要求: {result.extracted_info.experience_requirement}")
    print(f"薪资范围: {result.extracted_info.salary_range}")
    print(f"工作地点: {result.extracted_info.location}")
    print(f"必备技能: {', '.join(result.extracted_info.required_skills)}")
    print(f"所属行业: {result.extracted_info.industry}")
    print(f"置信度: {result.confidence_score}")

    assert "硕士" in result.extracted_info.education_requirement
    assert "Python" in result.extracted_info.required_skills or "深度学习" in result.extracted_info.required_skills
    assert result.extracted_info.industry == "人工智能"


def test_extract_entry_level_job():
    """测试应届生岗位信息提取"""
    job_text = """
    Python开发实习生

    要求：
    本科在读或应届毕业生
    熟悉Python基础语法
    了解Django或Flask框架

    实习补贴：150元/天
    工作地点：杭州西湖区
    可转正
    """

    result = job_info_extractor.extract(job_text)

    print("\n" + "="*60)
    print("测试4: 应届生岗位信息提取")
    print("="*60)
    print(f"岗位名称: {result.extracted_info.job_title}")
    print(f"学历要求: {result.extracted_info.education_requirement}")
    print(f"经验要求: {result.extracted_info.experience_requirement}")
    print(f"工作地点: {result.extracted_info.location}")
    print(f"必备技能: {', '.join(result.extracted_info.required_skills)}")
    print(f"置信度: {result.confidence_score}")

    assert result.extracted_info.job_title == "Python开发实习生"
    assert "Python" in result.extracted_info.required_skills


def test_extract_minimal_info():
    """测试信息不完整的情况"""
    job_text = """
    产品经理

    负责产品规划和需求分析
    本科学历
    """

    result = job_info_extractor.extract(job_text)

    print("\n" + "="*60)
    print("测试5: 信息不完整情况")
    print("="*60)
    print(f"岗位名称: {result.extracted_info.job_title}")
    print(f"学历要求: {result.extracted_info.education_requirement}")
    print(f"置信度: {result.confidence_score}")
    print(f"缺失字段: {', '.join(result.missing_fields)}")

    assert result.extracted_info.job_title == "产品经理"
    assert len(result.missing_fields) > 0
    assert result.confidence_score < 0.7


if __name__ == "__main__":
    test_extract_complete_job_info()
    test_extract_frontend_job()
    test_extract_ai_job()
    test_extract_entry_level_job()
    test_extract_minimal_info()

    print("\n" + "="*60)
    print("All tests passed!")
    print("="*60)
