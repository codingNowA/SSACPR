#!/bin/bash
# 加载面试题数据（如果表为空）

# 检查表中是否有数据
COUNT=$(docker exec career-postgres psql -U career_user -d career_planning -t -c "SELECT COUNT(*) FROM interview_questions;" 2>/dev/null | tr -d ' ')

if [ "$COUNT" = "0" ] || [ -z "$COUNT" ]; then
    echo "加载面试题数据..."
    docker exec -i career-postgres psql -U career_user -d career_planning < scripts/seed_questions.sql > /dev/null 2>&1
    echo "✓ 面试题数据加载完成"
else
    echo "✓ 面试题数据已存在 ($COUNT 条)"
fi
