import asyncio, asyncpg

async def reset_passwords():
    pool = await asyncpg.create_pool(
        host='postgres', port=5432,
        user='career_user', password='your_strong_password_here',
        database='career_planning'
    )
    # admin123 的正确bcrypt哈希
    new_hash = '$2b$12$CBpo230WZKanBHRQCK8eL.hWbPBXIcX.lNS3KIQAminnRrseP3mkO'
    
    async with pool.acquire() as conn:
        # 重置 admin, test_user, test_student 的密码
        result = await conn.execute(
            "UPDATE users SET password_hash = $1 WHERE username IN ('admin', 'test_user', 'test_student')",
            new_hash
        )
        print(f"更新结果: {result}")
        
        # 验证
        rows = await conn.fetch("SELECT id, username, password_hash FROM users WHERE username IN ('admin', 'test_user', 'test_student') ORDER BY id")
        for r in rows:
            print(f"ID:{r['id']} 用户名:{r['username']} 哈希:{r['password_hash'][:30]}...")
    await pool.close()

asyncio.run(reset_passwords())
