#!/bin/bash
# test目录快速部署和测试脚本

echo "================================"
echo "  test目录部署测试脚本"
echo "================================"
echo ""

# 切换到test目录
cd /d/test

echo "[1/6] 停止现有服务..."
docker-compose down
echo ""

echo "[2/6] 重新构建并启动服务..."
docker-compose up -d --build
echo ""

echo "[3/6] 等待服务启动（30秒）..."
sleep 30
echo ""

echo "[4/6] 检查服务状态..."
docker ps --filter name=career --format "table {{.Names}}\t{{.Status}}"
echo ""

echo "[5/6] 检查后端健康状态..."
curl -s http://localhost:8000/health | python -m json.tool
echo ""

echo "[6/6] 测试新API端点..."
echo ""
echo "测试面试题目API:"
curl -s "http://localhost:8000/api/v1/interview-exam/questions?count=2" | python -c "import sys, json; data=json.load(sys.stdin); print('  Status: OK' if 'questions' in data else '  Status: FAIL')"
echo ""

echo "测试岗位中心API:"
curl -s "http://localhost:8000/api/v1/jobs/center?page=1&page_size=2" | python -c "import sys, json; data=json.load(sys.stdin); print('  Status: OK' if 'items' in data else '  Status: FAIL')"
echo ""

echo "================================"
echo "  部署完成！"
echo "================================"
echo ""
echo "前端地址: http://localhost:5173"
echo "API文档: http://localhost:8000/docs"
echo ""
echo "查看详细报告:"
echo "  - 代码同步报告.md"
echo "  - 代码检查清单.md"
echo ""
