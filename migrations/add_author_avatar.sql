-- 添加作者头像字段
-- 运行命令: psql -U english_tube -d english_tube -f migrations/add_author_avatar.sql

ALTER TABLE videos ADD COLUMN IF NOT EXISTS author_avatar_url TEXT;

COMMENT ON COLUMN videos.author_avatar_url IS '作者/频道头像 URL';
