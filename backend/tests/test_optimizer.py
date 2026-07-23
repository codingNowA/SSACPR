#!/usr/bin/env python3
"""
简历优化功能快速测试脚本
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import asyncio
from app.schemas.resume_structured import (
    ResumeStructuredData, BasicInfo, Education,
    WorkExperience, ProjectExperience, SkillTag
)
from app.schemas.resume_score import ResumeScore, CompletenessScore, ProfessionalismScore, QuantificationScore, ProjectDepthScore
from app.core.resume.optimizer import resume_optimizer


async def test_optimization():
    """测试优化功能"""
    print("=" * 80)
    print("简历优化功能测试")
    print("=" * 80)

    # 构造测试数据
    structured_data = ResumeStructuredData(
        basic_info=BasicInfo(
            name="张三",
            phone="138****1234",
            email="zhangsan@example.com",
            age=23,
            gender="男",
            location="四川成都",
            job_intention="Python 后端工程师"
        ),
        education=[
            Education(
                school="四川大学",
                major="计算机科学与技术",
                degree="本科",
                start_date="2020-09",
                end_date="2024-06",
                gpa=3.6,
                description="主修课程：数据结构、算法、数据库、操作系统"
            )
        ],
        work_experience=[
            WorkExperience(
                company="某科技公司",
                position="Python 开发实习生",
                start_date="2023-06",
                end_date="2023-09",
                description="负责后端系统开发",
                achievements=["完成了用户模块开发", "优化了系统性能"]
            )
        ],
        project_experience=[
            ProjectExperience(
                name="电商系统后端开发",
                role="后端开发",
                start_date="2023-03",
                end_date="2023-06",
                description="负责用户模块开发",
                tech_stack=["Python", "FastAPI"],
                achievements=["完成了API开发"]
            )
        ],
        skills=[
            SkillTag(category="编程语言", name="Python", proficiency="熟练"),
            SkillTag(category="框架", name="FastAPI", proficiency="了解"),
            SkillTag(category="数据库", name="PostgreSQL", proficiency="了解"),
        ]
    )

    # 构造评分数据（模拟评分结果）
    score = ResumeScore(
        total_score=68.5,
        completeness=CompletenessScore(
            total_score=85.0,
            has_basic_info=True,
            has_education=True,
            has_work_experience=True,
            has_project_experience=True,
            has_skills=True,
            missing_fields=[],
            feedback="简历信息较完整"
        ),
        professionalism=ProfessionalismScore(
            total_score=70.0,
            language_quality=75.0,
            format_consistency=80.0,
            detail_richness=55.0,
            feedback="简历专业性良好，建议增加细节描述"
        ),
        quantification=QuantificationScore(
            total_score=40.0,
            quantified_achievements=1,
            total_achievements=3,
            quantification_rate=0.33,
            examples=["优化了系统性能"],
            feedback="量化程度较低，建议用具体数字量化成果"
        ),
        project_depth=ProjectDepthScore(
            total_score=55.0,
            project_count=1,
            avg_tech_stack_count=2.0,
            avg_achievement_count=1.0,
            has_detailed_description=False,
            feedback="项目深度不足，建议增加项目数量和技术细节"
        ),
        job_match=None,
        dimensions=[],
        overall_feedback="简历有一定基础，但量化程度和项目深度需要提升",
        strengths=["信息完整"],
        weaknesses=["量化不足", "项目深度不够"],
        suggestions=["增加量化数据", "丰富项目描述"]
    )

    resume_text = "张三的简历内容..."

    print("\n【测试1：通用优化（无岗位信息）】")
    print("-" * 80)
    try:
        optimization = await resume_optimizer.optimize_resume(
            structured_data=structured_data,
            score=score,
            resume_text=resume_text
        )

        print(f"\n✅ 生成了 {len(optimization.general_suggestions)} 条优化建议")
        print(f"✅ 优先行动清单：{len(optimization.priority_actions)} 条")
        print(f"✅ 预估改进：{optimization.estimated_improvement}")
        print(f"\n优化总结：{optimization.overall_summary}")

        print("\n前3条建议：")
        for i, suggestion in enumerate(optimization.general_suggestions[:3], 1):
            print(f"\n{i}. [{suggestion.priority}] {suggestion.title}")
            print(f"   类别：{suggestion.category}")
            print(f"   问题：{suggestion.description}")
            print(f"   建议：{suggestion.suggested_content[:100]}...")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 80)
    print("\n【测试2：岗位优化（含岗位信息）】")
    print("-" * 80)
    try:
        optimization = await resume_optimizer.optimize_resume(
            structured_data=structured_data,
            score=score,
            resume_text=resume_text,
            job_title="Python 后端工程师",
            job_description="负责后端系统开发，要求熟悉Python、FastAPI、PostgreSQL、Redis、Docker"
        )

        print(f"\n✅ 生成了 {len(optimization.general_suggestions)} 条优化建议")

        if optimization.job_targeted:
            print(f"✅ 岗位优化：{optimization.job_targeted.job_title}")
            print(f"✅ 当前匹配度：{optimization.job_targeted.match_score}")
            print(f"✅ 已匹配优势：{len(optimization.job_targeted.matched_points)} 个")
            print(f"✅ 需要改进：{len(optimization.job_targeted.improvement_areas)} 个")
            print(f"✅ 优化章节：{len(optimization.job_targeted.optimized_sections)} 个")

            if optimization.job_targeted.matched_points:
                print(f"\n已匹配优势：")
                for point in optimization.job_targeted.matched_points[:3]:
                    print(f"  • {point}")

            if optimization.job_targeted.improvement_areas:
                print(f"\n需要改进：")
                for area in optimization.job_targeted.improvement_areas[:3]:
                    print(f"  • {area}")
        else:
            print("⚠️  未生成岗位优化（可能是LLM调用失败）")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 80)
    print("✅ 所有测试通过！")
    print("=" * 80)
    return True


if __name__ == "__main__":
    print("开始测试简历优化功能...\n")
    result = asyncio.run(test_optimization())
    sys.exit(0 if result else 1)
