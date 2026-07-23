-- Migration: 添加 current_version_id 字段到 resumes 表
-- Date: 2026-07-18
-- Description: 为简历表添加 current_version_id 字段，用于跟踪当前应用的版本

-- 1. 添加 current_version_id 列
ALTER TABLE resumes
ADD COLUMN IF NOT EXISTS current_version_id INTEGER;

-- 2. 添加外键约束
DO $$
BEGIN
    -- 检查约束是否已存在
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'resumes_current_version_fkey'
    ) THEN
        ALTER TABLE resumes
        ADD CONSTRAINT resumes_current_version_fkey
        FOREIGN KEY (current_version_id)
        REFERENCES resume_versions(id)
        ON DELETE SET NULL;
    END IF;
END $$;

-- 3. 为现有简历初始化 current_version_id（设置为最新版本）
UPDATE resumes r
SET current_version_id = (
    SELECT rv.id
    FROM resume_versions rv
    WHERE rv.resume_id = r.id
    ORDER BY rv.created_at DESC
    LIMIT 1
)
WHERE current_version_id IS NULL
AND EXISTS (
    SELECT 1 FROM resume_versions rv
    WHERE rv.resume_id = r.id
);

-- 4. 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_resumes_current_version_id
ON resumes(current_version_id);

-- 提示信息
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 001 完成：已添加 current_version_id 字段';
END $$;
