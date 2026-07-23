import asyncio, asyncpg

async def check():
    pool = await asyncpg.create_pool(
        host='postgres', port=5432,
        user='career_user', password='your_strong_password_here',
        database='career_planning'
    )
    async with pool.acquire() as conn:
        # 先看表结构
        cols = await conn.fetch("SELECT column_name FROM information_schema.columns WHERE table_name='users' ORDER BY ordinal_position")
        print('users表列：', [c['column_name'] for c in cols])
        
        rows = await conn.fetch('SELECT * FROM users ORDER BY id')
        if not rows:
            print('没有用户记录')
        else:
            print(f'共 {len(rows)} 个用户：')
            for r in rows:
                print(dict(r))
    await pool.close()

asyncio.run(check())
