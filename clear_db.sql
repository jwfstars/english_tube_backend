-- 清空数据库的 SQL 命令
-- 删除所有表和重置 schema

-- 删除 public schema 并重新创建
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

-- 恢复权限
GRANT ALL ON SCHEMA public TO english_tube;
GRANT ALL ON SCHEMA public TO public;

-- 显示完成信息
\echo '✅ 数据库已清空！'
