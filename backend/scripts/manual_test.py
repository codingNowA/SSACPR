"""
手动功能测试脚本 - 测试所有已实现的功能

直接使用 requests 库测试 API
"""
import requests
import json
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
BASE_URL = "http://127.0.0.1:8000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")

def print_result(name, success, details=""):
    status = "✓" if success else "✗"
    print(f"{status} {name}")
    if details:
        print(f"  {details}")

def test_health():
    """测试健康检查"""
    print_section("1. 健康检查")

    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print_result("根路径", True, f"版本: {data.get('version')}")
            return True
        else:
            print_result("根路径", False, f"状态码: {response.status_code}")
            return False
    except Exception as e:
        print_result("根路径", False, f"错误: {e}")
        return False

def test_version_management():
    """测试版本管理"""
    print_section("2. 版本管理功能")

    # 测试列出版本
    try:
        response = requests.get(f"{BASE_URL}/api/v1/resume/versions?user_id=1")
        if response.status_code == 200:
            data = response.json()
            versions = data.get('data', {}).get('versions', [])
            print_result("列出版本", True, f"找到 {len(versions)} 个版本")
        else:
            print_result("列出版本", False, f"状态码: {response.status_code}")
    except Exception as e:
        print_result("列出版本", False, f"错误: {e}")

    # 测试版本统计（不传 user_id，让服务器使用默认值）
    try:
        response = requests.get(f"{BASE_URL}/api/v1/resume/versions/stats")
        if response.status_code == 200:
            data = response.json()
            stats = data.get('data', {})
            print_result("版本统计", True, f"总版本数: {stats.get('total_versions', 0)}")
            return True
        else:
            print_result("版本统计", False, f"状态码: {response.status_code}")
            return False
    except Exception as e:
        print_result("版本统计", False, f"错误: {e}")
        return False

def test_api_docs():
    """测试 API 文档"""
    print_section("3. API 文档")

    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print_result("Swagger 文档", True, "可访问")
        else:
            print_result("Swagger 文档", False, f"状态码: {response.status_code}")
    except Exception as e:
        print_result("Swagger 文档", False, f"错误: {e}")

    try:
        response = requests.get(f"{BASE_URL}/redoc")
        if response.status_code == 200:
            print_result("ReDoc 文档", True, "可访问")
            return True
        else:
            print_result("ReDoc 文档", False, f"状态码: {response.status_code}")
            return False
    except Exception as e:
        print_result("ReDoc 文档", False, f"错误: {e}")
        return False

def test_endpoint_availability():
    """测试端点可用性"""
    print_section("4. API 端点可用性测试")

    endpoints = [
        ("简历上传", "POST", "/api/v1/resume/upload"),
        ("简历解析", "POST", "/api/v1/resume/parse"),
        ("路径解析", "POST", "/api/v1/resume/parse-by-path"),
        ("结构化提取", "POST", "/api/v1/resume/extract"),
        ("简历评分", "POST", "/api/v1/resume/score"),
        ("简历优化", "POST", "/api/v1/resume/optimize"),
        ("版本列表", "GET", "/api/v1/resume/versions?user_id=1"),
        ("版本统计", "GET", "/api/v1/resume/versions/stats"),
    ]

    success_count = 0
    for name, method, endpoint in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            if method == "GET":
                response = requests.get(url, timeout=5)
            else:
                response = requests.post(url, json={}, timeout=5)

            # 端点存在即可（200, 400, 422 都表示端点可访问）
            if response.status_code in [200, 400, 422]:
                print_result(f"{name} ({method})", True, f"端点可访问")
                success_count += 1
            else:
                print_result(f"{name} ({method})", False, f"状态码: {response.status_code}")
        except Exception as e:
            print_result(f"{name} ({method})", False, f"错误: {e}")

    return success_count == len(endpoints)

def test_schema_validation():
    """测试数据模型验证"""
    print_section("5. 数据模型验证")

    # 测试缺少必需参数的请求
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/resume/parse-by-path",
            json={}
        )
        if response.status_code == 422:
            print_result("参数验证", True, "正确拒绝无效请求")
        else:
            print_result("参数验证", False, f"应返回 422，实际: {response.status_code}")
    except Exception as e:
        print_result("参数验证", False, f"错误: {e}")

    # 测试不支持的文件类型
    try:
        files = {"file": ("test.txt", b"test", "text/plain")}
        response = requests.post(
            f"{BASE_URL}/api/v1/resume/upload",
            files=files
        )
        if response.status_code in [400, 422]:
            print_result("文件类型验证", True, "正确拒绝不支持的文件类型")
            return True
        else:
            print_result("文件类型验证", False, f"应返回 400/422，实际: {response.status_code}")
            return False
    except Exception as e:
        print_result("文件类型验证", False, f"错误: {e}")
        return False

def main():
    print("="*60)
    print("简历智能诊断系统 - 功能测试")
    print("="*60)

    # 检查服务器
    print("\n检查服务器状态...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=3)
        if response.status_code != 200:
            print(f"✗ 服务器未正常运行 (状态码: {response.status_code})")
            print("\n请先启动服务器:")
            print("  cd backend")
            print("  python main.py")
            return 1
        print("✓ 服务器运行正常")
    except Exception as e:
        print(f"✗ 无法连接到服务器: {e}")
        print("\n请先启动服务器:")
        print("  cd backend")
        print("  python main.py")
        return 1

    # 运行测试
    results = []
    results.append(("健康检查", test_health()))
    results.append(("版本管理", test_version_management()))
    results.append(("API 文档", test_api_docs()))
    results.append(("端点可用性", test_endpoint_availability()))
    results.append(("数据验证", test_schema_validation()))

    # 总结
    print_section("测试总结")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status}: {name}")

    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
