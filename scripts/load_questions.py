"""
加载面试题数据到数据库
"""
import os
import sys
from pathlib import Path

import psycopg2


def load_questions():
    """从 seed_questions.sql 加载面试题数据"""

    # 数据库连接配置
    db_host = os.getenv("POSTGRES_HOST", "localhost")
    db_port = int(os.getenv("POSTGRES_PORT", "5432"))
    db_user = os.getenv("POSTGRES_USER", "career_user")
    db_password = os.getenv("POSTGRES_PASSWORD", "")
    db_name = os.getenv("POSTGRES_DB", "career_planning")

    # SQL 文件路径
    sql_file = Path(__file__).parent / "seed_questions.sql"

    if not sql_file.exists():
        print(f"错误: 未找到 {sql_file}")
        sys.exit(1)

    try:
        # 连接数据库
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            dbname=db_name
        )
        cursor = conn.cursor()

        # 读取并执行 SQL 文件
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql = f.read()

        cursor.execute(sql)
        conn.commit()

        # 查询加载的数据量
        cursor.execute("SELECT COUNT(*) FROM interview_questions")
        count = cursor.fetchone()[0]

        print(f"✓ 成功加载 {count} 条面试题数据")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"✗ 加载面试题数据失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    load_questions()
