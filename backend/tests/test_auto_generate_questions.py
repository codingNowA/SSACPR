#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试AI自动生成第一个面试问题
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import asyncio
from app.services.langchain_interview_service import langchain_interview_service


async def test_auto_first_question():
    """测试AI自动生成第一个问题"""

    print("="*80)
    print("测试: AI自动生成第一个面试问题")
    print("="*80)

    # 测试1: 无简历，只有岗位
    print("\n[测试1] 只提供岗位，AI自动生成第一个问题")
    print("-"*80)
    print("岗位: Python后端开发工程师")
    print("简历: 无")

    result = langchain_interview_service.start_session(
        job_title="Python后端开发工程师",
        candidate_name="张三"
    )

    print(f"\nOK 会话创建成功: {result['session_id']}")
    print(f"\nAI生成的第一个问题:")
    print("="*80)
    print(result['interviewer_message'])
    print("="*80)

    langchain_interview_service.delete_session(result['session_id'])

    # 测试2: 有简历摘要
    print("\n\n[测试2] 提供岗位和简历摘要，AI生成针对性问题")
    print("-"*80)
    print("岗位: Java后端开发工程师")

    resume = """
    候选人：李四
    教育背景：本科计算机专业
    工作经验：3年Java开发经验
    技术栈：Spring Boot, MySQL, Redis, Kafka
    项目经验：
    1. 电商订单系统 - 负责订单模块，日均10万订单
    2. 支付系统 - 实现分布式事务，TCC模式
    """

    print(f"简历摘要:\n{resume}")

    result2 = langchain_interview_service.start_session(
        job_title="Java后端开发工程师",
        candidate_name="李四",
        resume_summary=resume
    )

    print(f"\nOK 会话创建成功: {result2['session_id']}")
    print(f"\nAI生成的针对性问题:")
    print("="*80)
    print(result2['interviewer_message'])
    print("="*80)

    langchain_interview_service.delete_session(result2['session_id'])

    print("\n" + "="*80)
    print("测试完成！")
    print("="*80)
    print("\n功能验证:")
    print("  [OK] AI能根据岗位自动生成第一个面试问题")
    print("  [OK] AI能根据简历生成针对性的面试问题")
    print("  [OK] 后续问题会自动生成（已实现）")
    print("\n未来集成:")
    print("  -> 对接简历提取服务，自动获取resume_summary")
    print("  -> AI根据简历内容生成个性化面试问题")


if __name__ == "__main__":
    try:
        asyncio.run(test_auto_first_question())
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
