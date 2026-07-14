"""
直接测试 API 函数
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import asyncio
from app.api.v1.resume import list_resume_versions

async def test_list_versions():
    """测试列出版本"""
    print("直接调用 list_resume_versions 函数...")

    try:
        # 直接调用，不经过 FastAPI
        result = await list_resume_versions(
            page=1,
            page_size=10,
            active_only=False,
            user_id=1
        )
        print(f"✓ 成功: {result}")
        return True
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_list_versions())
    sys.exit(0 if success else 1)
