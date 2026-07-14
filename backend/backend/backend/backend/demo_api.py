#!/usr/bin/env python3
"""
简历解析功能演示脚本
使用实际的 API 调用演示功能
"""
import requests
import json
from pathlib import Path


API_BASE = "http://localhost:8000"


def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_api_health():
    """测试 API 健康状态"""
    print_section("1. API 健康检查")

    try:
        response = requests.get(f"{API_BASE}/")
        data = response.json()

        print(f"✅ API 状态: {data['status']}")
        print(f"📌 版本: {data['version']}")
        print(f"🎯 功能:")
        for key, value in data.get('features', {}).items():
            print(f"   • {key}: {value}")

        return True
    except Exception as e:
        print(f"❌ API 健康检查失败: {e}")
        return False


def test_get_formats():
    """测试获取支持的格式"""
    print_section("2. 获取支持的文件格式")

    try:
        response = requests.get(f"{API_BASE}/api/v1/resume/formats")
        data = response.json()

        if data['code'] == 200:
            print(f"✅ 支持的格式:")
            for fmt in data['data']['formats']:
                print(f"   • {fmt['extension']}: {fmt['description']}")

            print(f"\n📏 文件大小限制: {data['data']['max_file_size_mb']} MB")
            return True
        else:
            print(f"❌ 获取格式失败: {data['message']}")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False


def test_parse_sample(file_path=None):
    """测试解析示例文件"""
    print_section("3. 解析示例简历")

    if not file_path or not Path(file_path).exists():
        print("⚠️  未提供有效的简历文件路径")
        print("💡 使用方法:")
        print("   python demo_api.py --file path/to/resume.pdf")
        return False

    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{API_BASE}/api/v1/resume/parse",
                files=files
            )
            data = response.json()

        if data['code'] == 200:
            result = data['data']
            print(f"✅ 解析成功!")
            print(f"📄 文件类型: {result['file_type']}")
            print(f"📊 统计信息:")
            print(f"   • 总字数: {result['word_count']}")
            print(f"   • 字符数: {result['char_count']}")
            if result.get('page_count'):
                print(f"   • 页数: {result['page_count']}")

            print(f"\n📝 文本预览 (前 300 字):")
            print("-" * 60)
            print(result['text'][:300] + "...")
            print("-" * 60)
            return True
        else:
            print(f"❌ 解析失败: {data['message']}")
            return False
    except Exception as e:
        print(f"❌ 解析过程出错: {e}")
        return False


def main():
    """主函数"""
    import sys

    print("\n" + "🚀 " * 30)
    print("  简历解析功能演示")
    print("🚀 " * 30)

    # 检查 API 是否运行
    if not test_api_health():
        print("\n❌ API 服务未运行，请先启动服务:")
        print("   cd backend && uvicorn main:app --reload")
        return

    # 获取支持的格式
    test_get_formats()

    # 解析示例文件（如果提供）
    file_path = None
    if len(sys.argv) > 1 and sys.argv[1] != '--file':
        file_path = sys.argv[1]
    elif len(sys.argv) > 2 and sys.argv[1] == '--file':
        file_path = sys.argv[2]

    if file_path:
        test_parse_sample(file_path)
    else:
        print_section("3. 解析示例简历")
        print("⚠️  未提供简历文件")
        print("\n💡 使用方法:")
        print("   python demo_api.py path/to/resume.pdf")
        print("   python demo_api.py --file path/to/resume.docx")

    print("\n" + "✅ " * 30)
    print("  演示完成")
    print("✅ " * 30)

    print("\n📚 更多信息:")
    print("   • API 文档: http://localhost:8000/docs")
    print("   • 功能文档: backend/README-RESUME-PARSER.md")
    print("   • 实现总结: backend/IMPLEMENTATION-SUMMARY.md")
    print()


if __name__ == "__main__":
    main()
