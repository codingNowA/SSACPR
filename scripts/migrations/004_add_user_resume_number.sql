-- Migration: 为简历添加用户级别的编号
-- Date: 2026-01-19
-- Description: 添加 user_resume_number 字段，显示用户的第N份简历

-- 添加字段
ALTER TABLE resumes 
ADD COLUMN IF NOT EXISTS user_resume_number INT;

-- 为现有数据生成编号
WITH numbered_resumes AS (
    SELECT 
        id,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at) AS rn
    FROM resumes
)
UPDATE resumes r
SET user_resume_number = nr.rn
FROM numbered_resumes nr
WHERE r.id = nr.id;

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_resumes_user_resume_number 
ON resumes(user_id, user_resume_number);

-- 添加唯一约束（每个用户的 user_resume_number 不重复）
ALTER TABLE resumes 
DROP CONSTRAINT IF EXISTS resumes_user_resume_number_unique;

ALTER TABLE resumes 
ADD CONSTRAINT resumes_user_resume_number_unique 
UNIQUE (user_id, user_resume_number);

-- 提示信息
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 004 完成：已添加用户简历编号字段';
    RAISE NOTICE '用户现在可以看到 "我的第N份简历" 而不是全局ID';
END $$;
