-- 更新用户密码哈希
UPDATE users SET password_hash = '$2b$12$GG2mVqS3gDGuS2kKYr.jwOTKuO8NHDRVb4Jn1FSdGucHcKpiyhf1K' WHERE username = 'admin';
UPDATE users SET password_hash = '$2b$12$eZ8VP51ZIhGLLZpx.m9ZmuHBEvgY5yRjQqUl2H6nCpXuv.SAAsV3a' WHERE username = 'testuser';
SELECT username, left(password_hash, 30) as hash_start FROM users;
