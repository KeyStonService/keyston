#!/usr/bin/env python3
"""
MachineNativeOps Database Migration Script
數據庫遷移腳本
"""

import asyncio
import asyncpg
import sys
from pathlib import Path

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.new.config import load_config


async def create_database():
    """創建數據庫"""
    config = load_config()
    db_config = config.database
    
    # 連接到 PostgreSQL 默認數據庫
    conn = await asyncpg.connect(
        host=db_config.host,
        port=db_config.port,
        user=db_config.user,
        password=db_config.password,
        database="postgres"  # 默認數據庫
    )
    
    try:
        # 檢查數據庫是否存在
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", 
            db_config.name
        )
        
        if not exists:
            # 創建數據庫
            await conn.execute(f'CREATE DATABASE "{db_config.name}"')
            print(f"✅ 數據庫 {db_config.name} 創建成功")
        else:
            print(f"ℹ️  數據庫 {db_config.name} 已存在")
    
    finally:
        await conn.close()


async def create_tables():
    """創建數據表"""
    config = load_config()
    db_config = config.database
    
    # 連接到目標數據庫
    conn = await asyncpg.connect(
        host=db_config.host,
        port=db_config.port,
        user=db_config.user,
        password=db_config.password,
        database=db_config.name
    )
    
    try:
        print("🔧 創建數據表...")
        
        # 項目表
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(100) NOT NULL,
                description TEXT,
                owner VARCHAR(100) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                priority VARCHAR(20) NOT NULL DEFAULT 'medium',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                deadline TIMESTAMP WITH TIME ZONE,
                tags TEXT[] DEFAULT '{}',
                metadata JSONB DEFAULT '{}'
            )
        """)
        
        # 任務表
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                assignee VARCHAR(100),
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                priority VARCHAR(20) NOT NULL DEFAULT 'medium',
                progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                started_at TIMESTAMP WITH TIME ZONE,
                completed_at TIMESTAMP WITH TIME ZONE,
                dependencies UUID[] DEFAULT '{}',
                estimated_hours REAL,
                actual_hours REAL,
                tags TEXT[] DEFAULT '{}',
                metadata JSONB DEFAULT '{}'
            )
        """)
        
        # 資源表
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(100) NOT NULL,
                type VARCHAR(50) NOT NULL,
                capacity REAL,
                availability REAL DEFAULT 1.0 CHECK (availability >= 0 AND availability <= 1),
                cost_per_hour REAL,
                location VARCHAR(100),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                metadata JSONB DEFAULT '{}'
            )
        """)
        
        # 工作流執行表
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS workflow_executions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                workflow_id VARCHAR(100) NOT NULL,
                name VARCHAR(100) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                triggered_by VARCHAR(100) NOT NULL,
                started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                completed_at TIMESTAMP WITH TIME ZONE,
                progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
                results JSONB DEFAULT '{}',
                error_message TEXT,
                metadata JSONB DEFAULT '{}'
            )
        """)
        
        # 用戶表
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(100),
                is_active BOOLEAN DEFAULT true,
                is_admin BOOLEAN DEFAULT false,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                last_login TIMESTAMP WITH TIME ZONE,
                metadata JSONB DEFAULT '{}'
            )
        """)
        
        # 索引
        print("🔧 創建索引...")
        
        # 項目索引
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_projects_owner ON projects(owner)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at)")
        
        # 任務索引
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON tasks(project_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_assignee ON tasks(assignee)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority)")
        
        # 工作流執行索引
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_workflow_executions_workflow_id ON workflow_executions(workflow_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_workflow_executions_status ON workflow_executions(status)")
        
        # 用戶索引
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        
        print("✅ 數據表創建成功")
        
    finally:
        await conn.close()


async def insert_default_data():
    """插入默認數據"""
    config = load_config()
    db_config = config.database
    
    # 連接到數據庫
    conn = await asyncpg.connect(
        host=db_config.host,
        port=db_config.port,
        user=db_config.user,
        password=db_config.password,
        database=db_config.name
    )
    
    try:
        print("🔧 插入默認數據...")
        
        # 插入默認用戶 (admin/admin123)
        admin_exists = await conn.fetchval(
            "SELECT 1 FROM users WHERE username = 'admin'"
        )
        
        if not admin_exists:
            # 實際應用中應使用 bcrypt 哈希密碼
            await conn.execute("""
                INSERT INTO users (username, email, password_hash, full_name, is_admin)
                VALUES ('admin', 'admin@machinenativeops.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5muO', 'Administrator', true)
            """)
            print("✅ 默認管理員用戶創建成功")
        
        # 插入默認資源
        resource_count = await conn.fetchval("SELECT COUNT(*) FROM resources")
        
        if resource_count == 0:
            await conn.execute("""
                INSERT INTO resources (id, name, type, capacity, cost_per_hour) VALUES
                ('compute-standard', 'Standard Compute', 'compute', 100.0, 0.50),
                ('compute-premium', 'Premium Compute', 'compute', 200.0, 1.20),
                ('storage-standard', 'Standard Storage', 'storage', 1000.0, 0.01),
                ('network-standard', 'Standard Network', 'network', 1000.0, 0.05)
            """)
            print("✅ 默認資源創建成功")
        
        print("✅ 默認數據插入完成")
        
    finally:
        await conn.close()


async def main():
    """主函數"""
    print("🚀 MachineNativeOps 數據庫遷移開始...")
    print("=" * 50)
    
    try:
        await create_database()
        await create_tables()
        await insert_default_data()
        
        print("=" * 50)
        print("🎉 數據庫遷移完成！")
        
    except Exception as e:
        print(f"❌ 遷移失敗: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())