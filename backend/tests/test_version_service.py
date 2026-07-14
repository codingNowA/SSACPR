"""
测试版本管理服务是否正常工作
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.resume_version_service import resume_version_manager

def test_version_manager():
    """测试版本管理器"""
    print("测试版本管理器...")

    try:
        # 测试获取统计
        stats = resume_version_manager.get_stats(user_id=99999)
        print(f"✓ 统计查询成功: {stats}")

        # 测试列出版本
        versions = resume_version_manager.list_versions(
            user_id=99999,
            page=1,
            page_size=10
        )
        print(f"✓ 版本列表查询成功: 找到 {len(versions)} 个版本")

        return True
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_version_manager()
    sys.exit(0 if success else 1)
