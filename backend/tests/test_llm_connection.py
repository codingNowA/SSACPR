#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 LLM API 连接
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.ai.llm.client import LLMClient, LLMClientError


async def test_llm_connection():
    """测试 LLM 连接"""
    print("=" * 70)
    print("测试 LLM API 连接")
    print("=" * 70)

    client = LLMClient()

    print(f"\n配置信息:")
    print(f"  Provider: {client.settings.provider}")
    print(f"  Base URL: {client.settings.base_url}")
    print(f"  Model: {client.settings.model}")
    print(f"  API Key: {client.settings.api_key[:30]}...")
    print(f"  Timeout: {client.settings.timeout}s")

    # 标准化 URL
    normalized_url = client._normalize_url(client.settings.base_url)
    print(f"  Normalized URL: {normalized_url}")

    print("\n" + "=" * 70)
    print("发送测试请求...")
    print("=" * 70)

    try:
        result = await client.chat(
            user_prompt="你好，请回复：测试成功",
            system_prompt="你是一个测试助手",
            temperature=0.1
        )

        print("\n✅ LLM 调用成功！")
        print(f"\n响应内容:")
        print(f"  {result.content}")
        print(f"\n模型: {result.model}")

        return True

    except LLMClientError as e:
        print(f"\n❌ LLM 调用失败:")
        print(f"  错误: {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ 未知错误:")
        print(f"  类型: {type(e).__name__}")
        print(f"  错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    success = await test_llm_connection()

    print("\n" + "=" * 70)
    if success:
        print("✅ 测试通过 - LLM API 连接正常")
    else:
        print("❌ 测试失败 - 请检查配置或网络")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
