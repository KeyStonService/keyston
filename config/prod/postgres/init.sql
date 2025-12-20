-- MachineNativeOps PostgreSQL Initialization Script
-- PostgreSQL 初始化腳本

-- 創建擴展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 創建用戶和數據庫
CREATE USER mno_user WITH PASSWORD 'your-database-password';
CREATE DATABASE machinenativeops OWNER mno_user;

-- 授予權限
GRANT ALL PRIVILEGES ON DATABASE machinenativeops TO mno_user;

-- 連接到新數據庫
\c machinenativeops;

-- 授予 schema 權限
GRANT ALL ON SCHEMA public TO mno_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO mno_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO mno_user;

-- 設置默認權限
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO mno_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO mno_user;