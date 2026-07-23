import asyncio, asyncpg

async def check():
    pool = await asyncpg.create_pool(
        host='postgres', port=5432,
        user='career_user', password='career_password',
        database='career_planning'
    )
    async with pool.acquire() as conn:
        rows = await conn.fetch('SELECT id, username, email, role, is_active, created_at FROM users ORDER BY id')
        if not rows:
            print('没有用户记录')
        else:
            print(f'共 {len(rows)} 个用户：')
            for r in rows:
                print(f'ID:{r["id"]} | 用户名:{r["username"]} | 邮箱:{r["email"]} | 角色:{r["role"]} | 活跃:{r["is_active"]} | 创建时间:{r["created_at"]}')
    await pool.close()

asyncio.run(check())
