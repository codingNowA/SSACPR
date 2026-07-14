"""
岗位难度分析功能测试
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app.schemas.job_difficulty import (
    JobDifficultyRequest,
    DifficultyLevel
)
from app.services.job_difficulty_service import job_difficulty_analyzer


class TestJobDifficultyAnalyzer:
    """岗位难度分析器测试"""

    def test_basic_analysis(self):
        """测试基础分析功能"""
        request = JobDifficultyRequest(
            job_title="Python开发工程师",
            job_description="负责后端开发",
            requirements="熟悉Python、Django框架",
            education_requirement="本科",
            experience_requirement="1-3年"
        )

        result = job_difficulty_analyzer.analyze(request)

        assert result.job_title == "Python开发工程师"
        assert result.difficulty_level in [level for level in DifficultyLevel]
        assert 0 <= result.difficulty_score <= 100
        assert len(result.difficulty_factors) > 0
        assert result.summary != ""
        assert len(result.suggestions) > 0

        # 测试新增字段
        assert result.estimated_preparation_time is not None
        assert result.target_audience is not None
        assert result.key_challenges is not None and len(result.key_challenges) > 0
        assert result.success_rate_estimate is not None
        assert result.market_demand is not None
        assert result.career_development is not None

    def test_senior_position(self):
        """测试高级岗位分析"""
        request = JobDifficultyRequest(
            job_title="高级Java架构师",
            job_description="负责系统架构设计",
            requirements="精通Java、微服务架构、分布式系统、高并发处理",
            salary_range="40k-60k",
            education_requirement="本科及以上",
            experience_requirement="5-8年"
        )

        result = job_difficulty_analyzer.analyze(request)

        # 高级岗位应该有较高难度
        assert result.difficulty_level in [DifficultyLevel.HARD, DifficultyLevel.VERY_HARD]
        assert result.difficulty_score >= 60

    def test_entry_level_position(self):
        """测试初级岗位分析"""
        request = JobDifficultyRequest(
            job_title="初级前端开发",
            job_description="负责页面开发",
            requirements="了解HTML、CSS、JavaScript",
            salary_range="8k-12k",
            education_requirement="大专及以上",
            experience_requirement="应届生"
        )

        result = job_difficulty_analyzer.analyze(request)

        # 初级岗位应该有较低难度
        assert result.difficulty_level in [DifficultyLevel.VERY_EASY, DifficultyLevel.EASY]
        assert result.difficulty_score <= 40

    def test_education_factor(self):
        """测试学历因素分析"""
        # 测试硕士要求
        request = JobDifficultyRequest(
            job_title="算法工程师",
            education_requirement="硕士及以上"
        )

        result = job_difficulty_analyzer.analyze(request)
        education_factors = [f for f in result.difficulty_factors if f.factor_name == "学历要求"]

        assert len(education_factors) > 0
        assert education_factors[0].score >= 7  # 硕士要求分数应该较高

    def test_experience_factor(self):
        """测试经验因素分析"""
        request = JobDifficultyRequest(
            job_title="资深工程师",
            experience_requirement="5-8年"
        )

        result = job_difficulty_analyzer.analyze(request)
        experience_factors = [f for f in result.difficulty_factors if f.factor_name == "工作经验"]

        assert len(experience_factors) > 0
        assert experience_factors[0].score >= 7  # 5年以上经验分数应该较高

    def test_minimal_info(self):
        """测试最小信息输入"""
        request = JobDifficultyRequest(
            job_title="软件工程师"
        )

        result = job_difficulty_analyzer.analyze(request)

        # 即使信息很少，也应该返回有效结果
        assert result.difficulty_level is not None
        assert result.difficulty_score > 0
        assert result.summary != ""

    def test_salary_factor(self):
        """测试薪资因素分析"""
        high_salary_request = JobDifficultyRequest(
            job_title="技术专家",
            salary_range="50k-80k"
        )

        result = job_difficulty_analyzer.analyze(high_salary_request)
        salary_factors = [f for f in result.difficulty_factors if f.factor_name == "薪资水平"]

        assert len(salary_factors) > 0
        assert salary_factors[0].score >= 8  # 高薪岗位分数应该很高

    def test_enhanced_fields(self):
        """测试新增的增强字段"""
        request = JobDifficultyRequest(
            job_title="高级Python开发工程师",
            requirements="熟悉Django、微服务架构",
            education_requirement="本科",
            experience_requirement="3-5年",
            salary_range="25k-40k",
            industry="互联网",
            required_skills=["Python", "Django", "Redis"]
        )

        result = job_difficulty_analyzer.analyze(request)

        # 测试预估准备时间
        assert result.estimated_preparation_time is not None
        assert "周" in result.estimated_preparation_time

        # 测试适合人群
        assert result.target_audience is not None
        assert len(result.target_audience) > 0

        # 测试主要挑战
        assert result.key_challenges is not None
        assert len(result.key_challenges) > 0
        assert isinstance(result.key_challenges, list)

        # 测试成功率估算
        assert result.success_rate_estimate is not None
        assert "%" in result.success_rate_estimate or "成功率" in result.success_rate_estimate

        # 测试市场需求
        assert result.market_demand is not None
        assert len(result.market_demand) > 0

        # 测试职业发展
        assert result.career_development is not None
        assert len(result.career_development) > 0

    def test_market_demand_by_role(self):
        """测试不同岗位的市场需求分析"""
        roles = ["Java开发工程师", "Python工程师", "前端开发", "算法工程师"]

        for role in roles:
            request = JobDifficultyRequest(job_title=role)
            result = job_difficulty_analyzer.analyze(request)
            assert result.market_demand is not None
            assert len(result.market_demand) > 10  # 应该有实质内容

    def test_career_development_by_level(self):
        """测试不同级别岗位的职业发展建议"""
        levels = ["初级Java开发", "高级Java开发", "Java架构师", "技术经理"]

        for level in levels:
            request = JobDifficultyRequest(job_title=level)
            result = job_difficulty_analyzer.analyze(request)
            assert result.career_development is not None
            assert "发展" in result.career_development or "方向" in result.career_development


if __name__ == "__main__":
    # 运行简单测试
    analyzer = job_difficulty_analyzer

    # 测试案例1：高级岗位
    print("=" * 60)
    print("测试案例1：高级Java开发工程师")
    print("=" * 60)
    request1 = JobDifficultyRequest(
        job_title="高级Java开发工程师",
        job_description="负责公司核心业务系统的开发与维护",
        requirements="3-5年Java开发经验，熟悉Spring全家桶，了解微服务架构、Redis、MySQL",
        salary_range="20k-35k",
        education_requirement="本科及以上",
        experience_requirement="3-5年"
    )
    result1 = analyzer.analyze(request1)
    print(f"岗位名称: {result1.job_title}")
    print(f"难度等级: {result1.difficulty_level.value}")
    print(f"难度得分: {result1.difficulty_score}/100")
    print(f"\n难度因素分析:")
    for factor in result1.difficulty_factors:
        print(f"  - {factor.factor_name}: {factor.score}/10 (权重: {factor.weight})")
        print(f"    说明: {factor.description}")
    print(f"\n总结: {result1.summary}")
    print(f"\n备考建议:")
    for i, suggestion in enumerate(result1.suggestions, 1):
        print(f"  {i}. {suggestion}")
    print(f"\n竞争分析: {result1.competitive_analysis}")
    print(f"\n预估准备时间: {result1.estimated_preparation_time}")
    print(f"适合人群: {result1.target_audience}")
    print(f"\n主要挑战:")
    for i, challenge in enumerate(result1.key_challenges, 1):
        print(f"  {i}. {challenge}")
    print(f"\n成功率估算: {result1.success_rate_estimate}")
    print(f"市场需求: {result1.market_demand}")
    print(f"职业发展: {result1.career_development}")

    # 测试案例2：初级岗位
    print("\n" + "=" * 60)
    print("测试案例2：初级前端开发")
    print("=" * 60)
    request2 = JobDifficultyRequest(
        job_title="初级前端开发",
        job_description="负责网站前端页面开发",
        requirements="了解HTML、CSS、JavaScript，熟悉Vue或React框架",
        salary_range="8k-12k",
        education_requirement="大专及以上",
        experience_requirement="应届生或1年经验"
    )
    result2 = analyzer.analyze(request2)
    print(f"岗位名称: {result2.job_title}")
    print(f"难度等级: {result2.difficulty_level.value}")
    print(f"难度得分: {result2.difficulty_score}/100")
    print(f"\n总结: {result2.summary}")
