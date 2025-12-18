#!/usr/bin/env python3
"""
v1 → v2 遷移腳本

將 v1-python-drones 遷移至 v2-multi-islands 架構。
"""

import sys
from pathlib import Path

# 添加父目錄到路徑
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from migration.migrator import Migrator


def main() -> int:
    """主程式"""
    print("=" * 50)
    print("  v1-python-drones → v2-multi-islands 遷移")
    print("=" * 50)
    print()
    
    migrator = Migrator()
    
    # 執行遷移
    result = migrator.migrate_v1_to_v2(dry_run=False)
    
    # 生成報告
    if result['success']:
        migrator.generate_report(result)
    
    return 0 if result['success'] else 1


if __name__ == '__main__':
    sys.exit(main())
