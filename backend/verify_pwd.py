from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

stored_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lWN6U8fMU1FK"

# 测试常见密码
for pwd in ["admin123", "123456", "password", "admin", "test123", "user123", "12345678"]:
    try:
        result = pwd_context.verify(pwd, stored_hash)
        print(f"{pwd}: {result}")
    except Exception as e:
        print(f"{pwd}: ERROR - {e}")

# 如果都不匹配，直接重置密码为 admin123
new_hash = pwd_context.hash("admin123")
print(f"\nadmin123 的新哈希: {new_hash}")
print("验证新哈希:", pwd_context.verify("admin123", new_hash))
