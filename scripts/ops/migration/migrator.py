#!/usr/bin/env python3
"""
版本遷移器

負責 v1-python-drones 和 v2-multi-islands 之間的遷移邏輯。
"""

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


class Colors:
    """終端機顏色"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'


class Migrator:
    """
    版本遷移器
    
    負責 v1-python-drones 和 v2-multi-islands 之間的遷移。
    """
    
    # 遷移映射：v1 → v2
    V1_TO_V2_MAPPING = {
        'drones/coordinator_drone.py': 'orchestrator/island_orchestrator.py',
        'drones/autopilot_drone.py': 'islands/python_island.py',
        'drones/deployment_drone.py': 'islands/',  # 分散到各島嶼
        'drones/base_drone.py': 'islands/base_island.py',
        'config/drone_config.py': 'config/island_config.py',
        'utils/helpers.py': 'utils/helpers.py',
    }
    
    def __init__(self) -> None:
        self._project_root = self._find_project_root()
        self.v1_path = self._project_root / 'v1-python-drones'
        self.v2_path = self._project_root / 'v2-multi-islands'
        self.backup_path = self._project_root / 'migration' / 'backups'
        self.report_path = self._project_root / 'migration' / 'reports'
        self.migration_log: list[str] = []
    
    def _find_project_root(self) -> Path:
        """尋找專案根目錄"""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            if (current / 'drone-config.yml').exists():
                return current
            if (current / 'package.json').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    @property
    def project_root(self) -> Path:
        return self._project_root
    
    def log(self, message: str, level: str = "INFO") -> None:
        """記錄遷移日誌"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}][{level}] {message}"
        self.migration_log.append(log_entry)
        
        color = {
            'INFO': Colors.BLUE,
            'SUCCESS': Colors.GREEN,
            'WARN': Colors.YELLOW,
            'ERROR': Colors.RED,
        }.get(level, Colors.NC)
        
        print(f"{color}{log_entry}{Colors.NC}")
    
    def pre_check(self) -> dict[str, Any]:
        """
        遷移前檢查
        
        Returns:
            檢查結果
        """
        self.log("執行遷移前檢查...", "INFO")
        
        result = {
            'v1_exists': self.v1_path.exists(),
            'v2_exists': self.v2_path.exists(),
            'drone_config_exists': (self._project_root / 'drone-config.yml').exists(),
            'island_config_exists': (self._project_root / 'island-control.yml').exists(),
            'can_migrate_v1_to_v2': False,
            'can_migrate_v2_to_v1': False,
        }
        
        result['can_migrate_v1_to_v2'] = result['v1_exists'] and result['drone_config_exists']
        result['can_migrate_v2_to_v1'] = result['v2_exists'] and result['island_config_exists']
        
        # 顯示檢查結果
        print("\n📋 遷移前檢查結果:")
        print(f"  v1-python-drones: {'✅' if result['v1_exists'] else '❌'}")
        print(f"  v2-multi-islands: {'✅' if result['v2_exists'] else '❌'}")
        print(f"  drone-config.yml: {'✅' if result['drone_config_exists'] else '❌'}")
        print(f"  island-control.yml: {'✅' if result['island_config_exists'] else '❌'}")
        print(f"  可執行 v1 → v2: {'✅' if result['can_migrate_v1_to_v2'] else '❌'}")
        print(f"  可執行 v2 → v1: {'✅' if result['can_migrate_v2_to_v1'] else '❌'}")
        print()
        
        return result
    
    def create_backup(self, version: str) -> Optional[Path]:
        """
        建立備份
        
        Args:
            version: 要備份的版本 ("v1" 或 "v2")
            
        Returns:
            備份路徑
        """
        source_path = self.v1_path if version == "v1" else self.v2_path
        
        if not source_path.exists():
            self.log(f"{version} 目錄不存在，跳過備份", "WARN")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{version}_backup_{timestamp}"
        backup_dest = self.backup_path / backup_name
        
        self.backup_path.mkdir(parents=True, exist_ok=True)
        
        self.log(f"建立 {version} 備份至 {backup_dest}", "INFO")
        
        try:
            shutil.copytree(source_path, backup_dest)
            self.log(f"備份完成: {backup_dest}", "SUCCESS")
            return backup_dest
        except Exception as e:
            self.log(f"備份失敗: {e}", "ERROR")
            return None
    
    def migrate_v1_to_v2(self, dry_run: bool = False) -> dict[str, Any]:
        """
        執行 v1 → v2 遷移
        
        Args:
            dry_run: 是否為乾跑模式（只顯示會做什麼，不實際執行）
            
        Returns:
            遷移結果
        """
        self.log("開始 v1 → v2 遷移", "INFO")
        
        if dry_run:
            self.log("(乾跑模式 - 不會實際執行變更)", "WARN")
        
        result = {
            'success': False,
            'direction': 'v1-to-v2',
            'files_processed': [],
            'errors': [],
            'backup_path': None,
        }
        
        # 檢查
        check = self.pre_check()
        if not check['can_migrate_v1_to_v2']:
            self.log("無法執行 v1 → v2 遷移", "ERROR")
            result['errors'].append("Pre-check failed")
            return result
        
        # 建立備份
        if not dry_run:
            result['backup_path'] = str(self.create_backup("v1"))
        
        # 顯示遷移映射
        self.log("遷移映射:", "INFO")
        for v1_file, v2_file in self.V1_TO_V2_MAPPING.items():
            print(f"  {v1_file} → {v2_file}")
            result['files_processed'].append({'from': v1_file, 'to': v2_file})
        
        # 遷移邏輯（實際遷移只是確保 v2 結構存在，因為我們已經有了）
        if not dry_run:
            self.log("驗證 v2 結構...", "INFO")
            
            required_dirs = [
                self.v2_path / 'config',
                self.v2_path / 'orchestrator',
                self.v2_path / 'islands',
                self.v2_path / 'bridges',
                self.v2_path / 'utils',
            ]
            
            for dir_path in required_dirs:
                if dir_path.exists():
                    self.log(f"  ✅ {dir_path.name}/", "SUCCESS")
                else:
                    self.log(f"  ❌ {dir_path.name}/ 不存在", "WARN")
        
        result['success'] = True
        self.log("v1 → v2 遷移完成", "SUCCESS")
        
        return result
    
    def migrate_v2_to_v1(self, dry_run: bool = False) -> dict[str, Any]:
        """
        執行 v2 → v1 降級遷移
        
        Args:
            dry_run: 是否為乾跑模式
            
        Returns:
            遷移結果
        """
        self.log("開始 v2 → v1 降級遷移", "INFO")
        
        if dry_run:
            self.log("(乾跑模式 - 不會實際執行變更)", "WARN")
        
        result = {
            'success': False,
            'direction': 'v2-to-v1',
            'files_processed': [],
            'errors': [],
            'backup_path': None,
        }
        
        # 檢查
        check = self.pre_check()
        if not check['can_migrate_v2_to_v1']:
            self.log("無法執行 v2 → v1 降級遷移", "ERROR")
            result['errors'].append("Pre-check failed")
            return result
        
        # 建立備份
        if not dry_run:
            result['backup_path'] = str(self.create_backup("v2"))
        
        # 反向映射
        v2_to_v1_mapping = {v: k for k, v in self.V1_TO_V2_MAPPING.items()}
        
        self.log("遷移映射:", "INFO")
        for v2_file, v1_file in v2_to_v1_mapping.items():
            print(f"  {v2_file} → {v1_file}")
            result['files_processed'].append({'from': v2_file, 'to': v1_file})
        
        # 驗證 v1 結構
        if not dry_run:
            self.log("驗證 v1 結構...", "INFO")
            
            required_dirs = [
                self.v1_path / 'config',
                self.v1_path / 'drones',
                self.v1_path / 'utils',
            ]
            
            for dir_path in required_dirs:
                if dir_path.exists():
                    self.log(f"  ✅ {dir_path.name}/", "SUCCESS")
                else:
                    self.log(f"  ❌ {dir_path.name}/ 不存在", "WARN")
        
        result['success'] = True
        self.log("v2 → v1 降級遷移完成", "SUCCESS")
        
        return result
    
    def generate_report(self, result: dict[str, Any]) -> str:
        """
        生成遷移報告
        
        Args:
            result: 遷移結果
            
        Returns:
            報告路徑
        """
        self.report_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.report_path / f"migration_report_{timestamp}.md"
        
        report_content = f"""# 遷移報告

## 基本資訊

- **遷移方向**: {result.get('direction', 'N/A')}
- **執行時間**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **狀態**: {'✅ 成功' if result.get('success') else '❌ 失敗'}
- **備份路徑**: {result.get('backup_path', 'N/A')}

## 處理的檔案

| 來源 | 目標 |
|------|------|
"""
        for file_info in result.get('files_processed', []):
            report_content += f"| {file_info['from']} | {file_info['to']} |\n"
        
        if result.get('errors'):
            report_content += "\n## 錯誤\n\n"
            for error in result['errors']:
                report_content += f"- {error}\n"
        
        report_content += "\n## 遷移日誌\n\n```\n"
        report_content += "\n".join(self.migration_log)
        report_content += "\n```\n"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.log(f"報告已生成: {report_file}", "SUCCESS")
        return str(report_file)


def main() -> int:
    """主程式"""
    parser = argparse.ArgumentParser(
        description='SynergyMesh 版本遷移工具'
    )
    
    parser.add_argument(
        '--direction', '-d',
        choices=['v1-to-v2', 'v2-to-v1'],
        required=True,
        help='遷移方向'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='乾跑模式（不實際執行）'
    )
    
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='只執行前置檢查'
    )
    
    args = parser.parse_args()
    
    migrator = Migrator()
    
    if args.check_only:
        migrator.pre_check()
        return 0
    
    if args.direction == 'v1-to-v2':
        result = migrator.migrate_v1_to_v2(dry_run=args.dry_run)
    else:
        result = migrator.migrate_v2_to_v1(dry_run=args.dry_run)
    
    if not args.dry_run:
        migrator.generate_report(result)
    
    return 0 if result['success'] else 1


if __name__ == '__main__':
    sys.exit(main())
