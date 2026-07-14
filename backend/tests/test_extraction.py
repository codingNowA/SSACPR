#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整测试简历结构化提取流程
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.resume.parser import resume_parser
from app.core.resume.extractor import resume_extractor


# 测试简历文本
TEST_RESUME_TEXT = """
张伟
软件工程师

联系方式
电话: 138-1234-5678
邮箱: zhangwei@example.com

教育经历
四川大学 | 计算机科学与技术 | 本科 | 2018.09 - 2022.06
GPA: 3.8/4.0

工作经验
ABC科技有限公司 | 后端工程师 | 2022.07 - 至今
• 负责公司核心业务系统的后端开发和维护
• 使用 Python/FastAPI 开发 RESTful API，提升系统性能 30%

项目经验
职业规划推荐系统 | 核心开发 | 2024.01 - 2024.06
• 技术栈: Python, FastAPI, PostgreSQL, OpenSearch
• 实现简历解析功能，支持 PDF、Word、图片格式

技能清单
编程语言: Python, Java
框架: FastAPI, Django
数据库: PostgreSQL, Redis
"""


async def test_extraction():
    """测试结构化提取"""
    print("=" * 70)
    print("测试简历结构化提取")
    print("=" * 70)

    print("\n测试文本:")
    print(TEST_RESUME_TEXT[:200] + "...")

    print("\n" + "=" * 70)
    print("开始提取...")
    print("=" * 70)

    try:
        structured_data = await resume_extractor.extract_structured_data(TEST_RESUME_TEXT)

        print("\n✅ 提取成功！")

        # 基本信息
        if structured_data.basic_info:
            print("\n【基本信息】")
            basic = structured_data.basic_info
            if basic.name:
                print(f"  姓名: {basic.name}")
            if basic.phone:
                print(f"  电话: {basic.phone}")
            if basic.email:
                print(f"  邮箱: {basic.email}")

        # 教育经历
        if structured_data.education:
            print("\n【教育经历】")
            for edu in structured_data.education:
                print(f"  • {edu.school} - {edu.major} ({edu.degree})")

        # 工作经历
        if structured_data.work_experience:
            print("\n【工作经历】")
            for work in structured_data.work_experience:
                print(f"  • {work.company} - {work.position}")

        # 项目经验
        if structured_data.project_experience:
            print("\n【项目经验】")
            for proj in structured_data.project_experience:
                print(f"  • {proj.name}")
                if proj.tech_stack:
                    print(f"    技术栈: {', '.join(proj.tech_stack)}")

        # 技能标签
        if structured_data.skills:
            print("\n【技能标签】")
            for skill in structured_data.skills[:5]:  # 只显示前5个
                print(f"  • {skill.name} ({skill.category})")

        return True

    except Exception as e:
        print(f"\n❌ 提取失败:")
        print(f"  错误类型: {type(e).__name__}")
        print(f"  错误信息: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    success = await test_extraction()

    print("\n" + "=" * 70)
    if success:
        print("✅ 测试通过 - 结构化提取功能正常")
    else:
        print("❌ 测试失败 - 请检查错误信息")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
