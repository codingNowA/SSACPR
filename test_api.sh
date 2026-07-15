#!/bin/bash
# 测试后端 API 功能

echo "====== SSACPR 后端 API 测试 ======"
echo ""

# 1. 健康检查
echo "1. 测试健康检查..."
curl -s http://localhost:8000/health | python -m json.tool
echo ""

# 2. 测试岗位列表
echo "2. 测试岗位列表..."
curl -s "http://localhost:8000/api/v1/job/list?page=1&page_size=3" | python -m json.tool | head -30
echo ""

# 3. 创建测试 PDF
echo "3. 创建测试简历文件..."
cat > /tmp/test_resume.pdf << 'EOF'
%PDF-1.4
测试简历内容
姓名: 张三
技能: Python, Java
EOF
echo "测试文件已创建: /tmp/test_resume.pdf"
echo ""

# 4. 测试上传
echo "4. 测试简历上传..."
UPLOAD_RESULT=$(curl -s -X POST http://localhost:8000/api/v1/resume/upload \
  -F "file=@/tmp/test_resume.pdf" \
  -F "user_id=1")
echo "$UPLOAD_RESULT" | python -m json.tool
echo ""

# 提取 resume_id（如果有）
RESUME_ID=$(echo "$UPLOAD_RESULT" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('resume_id', 'null'))" 2>/dev/null)

if [ "$RESUME_ID" != "null" ] && [ -n "$RESUME_ID" ]; then
  echo "5. 测试简历解析 (resume_id=$RESUME_ID)..."
  curl -s -X POST "http://localhost:8000/api/v1/resume/$RESUME_ID/parse" | python -m json.tool | head -20
  echo ""

  echo "6. 测试简历诊断 (resume_id=$RESUME_ID)..."
  curl -s -X POST "http://localhost:8000/api/v1/resume/$RESUME_ID/diagnose" | python -m json.tool | head -30
  echo ""
else
  echo "警告: 上传未返回 resume_id，跳过后续测试"
fi

echo "====== 测试完成 ======"
