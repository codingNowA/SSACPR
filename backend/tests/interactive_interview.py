#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
交互式AI面试测试 - 命令行对话模式
支持与AI面试官进行真实的交互式对话
"""
import sys
import io
from pathlib import Path

# 修复Windows终端编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import asyncio
from app.services.langchain_interview_service import langchain_interview_service


async def interactive_interview():
    """交互式AI面试"""

    print("="*80)
    print("交互式AI面试系统")
    print("="*80)
    print("\n核心功能:")
    print("  ✓ AI智能追问 - 根据回答深度自动追问细节")
    print("  ✓ 项目深挖 - 识别项目经验自动深入询问")
    print("  ✓ 自动评价 - 判断回答完整性并打分")
    print("  ✓ 自动出题 - 评价后根据岗位自动生成下一题")
    print("="*80)

    # 输入面试信息
    print("\n请输入面试信息:")
    job_title = input("目标岗位 (默认: Python后端开发工程师): ").strip() or "Python后端开发工程师"
    candidate_name = input("候选人姓名 (默认: 张三): ").strip() or "张三"

    print("\n提示: AI会根据岗位自动生成第一个面试问题")

    # 开始会话（不提供initial_question，让AI自动生成）
    print("\n正在启动面试会话...")
    print("AI正在根据岗位生成第一个面试问题...")
    result = langchain_interview_service.start_session(
        job_title=job_title,
        candidate_name=candidate_name
        # 不传initial_question参数，让AI自动生成
    )

    if not result["success"]:
        print(f"启动失败: {result.get('message')}")
        return

    session_id = result["session_id"]

    print("\n" + "="*80)
    print("【AI面试官】")
    print(f"\n{result['interviewer_message']}\n")
    print("="*80)
    print(f"[会话ID: {session_id}]")

    print("\n使用说明:")
    print("  - 直接输入你的回答，AI会智能追问")
    print("  - AI评价后会自动提出下一个问题")
    print("  - 输入 'end' 结束面试并查看总结")
    print("  - 输入 'quit' 退出\n")

    turn = 0

    # 对话循环
    while True:
        try:
            user_input = input("你的回答: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n测试已中断")
            break

        if not user_input:
            print("请输入内容")
            continue

        if user_input.lower() == 'quit':
            print("\n感谢使用，再见！")
            break

        if user_input.lower() == 'end':
            # 结束面试
            print("\n正在生成面试总结...")
            end_result = await langchain_interview_service.end_session(session_id)

            if end_result["success"]:
                print("\n" + "="*80)
                print("面试评估报告")
                print("="*80)
                print(f"\n{end_result['interview_summary']}\n")
                print("-"*80)
                print(f"总问题数: {end_result['total_questions']}")
                print(f"面试时长: {end_result['duration_minutes']} 分钟")
                print("="*80)
            break

        # 继续对话
        print("\n【候选人】")
        print(f"{user_input}\n")
        print("AI正在思考...")

        result = await langchain_interview_service.continue_conversation(
            session_id=session_id,
            candidate_answer=user_input
        )

        if not result["success"]:
            print(f"对话失败: {result.get('message')}")
            continue

        turn = result.get("conversation_turn", turn + 1)
        response_type = result.get("response_type", "follow_up")

        # 显示AI回应
        print("\n" + "="*80)
        print("【AI面试官】")
        print(f"\n{result['interviewer_message']}\n")
        print("="*80)

        # 显示AI识别的回应类型
        type_map = {
            "question": "新问题",
            "follow_up": "追问细节",
            "project_deep_dive": "深挖项目",
            "ask_for_more": "询问补充",
            "evaluation": "评价并自动出下一题"
        }
        status = type_map.get(response_type, response_type)
        print(f"[AI识别: {status} | 对话轮次: {turn}]")

        if response_type == "evaluation":
            print("\n提示: AI已在评价后自动提出下一个问题，请继续回答\n")

    # 清理会话
    langchain_interview_service.delete_session(session_id)
    print(f"\n会话已清理")


if __name__ == "__main__":
    print("\n启动交互式AI面试系统...")
    try:
        asyncio.run(interactive_interview())
    except KeyboardInterrupt:
        print("\n\n测试已中断，再见！")
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
