"""
批量计算岗位难度脚本
"""
import asyncio
import asyncpg
import json
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.job_difficulty_service import job_difficulty_service


async def main():
    # 连接数据库
    conn = await asyncpg.connect(
        host=os.getenv('POSTGRES_HOST', 'career-postgres'),
        port=int(os.getenv('POSTGRES_PORT', 5432)),
        user=os.getenv('POSTGRES_USER', 'career_user'),
        password=os.getenv('POSTGRES_PASSWORD', 'career123'),
        database=os.getenv('POSTGRES_DB', 'career_planning')
    )

    print("开始计算岗位难度...")

    # 获取所有岗位
    jobs = await conn.fetch("""
        SELECT id, title, company, company_type, salary_range,
               experience_required, education_required,
               description, requirements
        FROM jobs
        WHERE status = 'active'
    """)

    print(f"找到 {len(jobs)} 个活跃岗位")

    updated_count = 0
    for job in jobs:
        job_dict = dict(job)

        # 计算难度
        difficulty = job_difficulty_service.calculate_difficulty(job_dict)

        # 更新数据库
        await conn.execute("""
            UPDATE jobs
            SET difficulty = $1
            WHERE id = $2
        """, json.dumps(difficulty), job['id'])

        updated_count += 1
        if updated_count % 10 == 0:
            print(f"已处理 {updated_count}/{len(jobs)} 个岗位...")

    print(f"完成！共更新 {updated_count} 个岗位的难度信息")

    await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
