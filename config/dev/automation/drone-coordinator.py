#!/usr/bin/env python3
"""
SynergyMesh 主協調器 (Drone Coordinator)
作者: SynergyMesh Team
版本: 2.0.0

此腳本負責協調所有無人機系統的運作，包括:
- 智能環境分析
- 任務調度
- 資源管理
- 健康監控
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# 顏色輸出
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color


def print_color(color: str, message: str) -> None:
    """輸出帶顏色的訊息"""
    print(f"{color}{message}{Colors.NC}")


def print_info(message: str) -> None:
    print_color(Colors.BLUE, f"[INFO] {message}")


def print_success(message: str) -> None:
    print_color(Colors.GREEN, f"[SUCCESS] {message}")


def print_warn(message: str) -> None:
    print_color(Colors.YELLOW, f"[WARN] {message}")


def print_error(message: str) -> None:
    print_color(Colors.RED, f"[ERROR] {message}")


class DroneCoordinator:
    """主協調器類別"""
    
    def __init__(self) -> None:
        self.project_root = self._find_project_root()
        self.config: dict[str, Any] = {}
        self.drones: dict[str, dict[str, Any]] = {}
        
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
    
    def load_config(self) -> bool:
        """載入配置檔案"""
        config_path = self.project_root / 'drone-config.yml'
        
        if not config_path.exists():
            print_warn(f"配置檔案不存在: {config_path}")
            return False
        
        try:
            # 嘗試使用 PyYAML
            try:
                import yaml
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f)
            except ImportError:
                # 如果沒有 PyYAML，使用簡單的解析
                print_warn("PyYAML 未安裝，使用基本配置")
                self.config = {
                    'meta': {'version': '2.0.0'},
                    'drone_fleet': {},
                    'automation': {'code_generation': {'enabled': True}}
                }
            
            print_success(f"配置已載入: {config_path}")
            return True
            
        except Exception as e:
            print_error(f"載入配置失敗: {e}")
            return False
    
    def analyze_environment(self) -> dict[str, Any]:
        """分析當前環境"""
        print_info("🔍 分析環境...")
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'tools': {},
            'structure': {},
            'recommendations': []
        }
        
        # 檢查工具
        tools = ['node', 'npm', 'python3', 'docker', 'git']
        for tool in tools:
            try:
                result = subprocess.run(
                    [tool, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                analysis['tools'][tool] = {
                    'installed': result.returncode == 0,
                    'version': result.stdout.strip().split('\n')[0] if result.returncode == 0 else None
                }
            except (FileNotFoundError, subprocess.TimeoutExpired):
                analysis['tools'][tool] = {'installed': False, 'version': None}
        
        # 檢查專案結構
        required_dirs = ['config/dev', '.vscode', 'shared', 'migration']
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            analysis['structure'][dir_name] = dir_path.exists()
        
        # 生成建議
        if not analysis['tools'].get('docker', {}).get('installed'):
            analysis['recommendations'].append("建議安裝 Docker 以支援容器化開發")
        
        if not analysis['structure'].get('config/dev'):
            analysis['recommendations'].append("缺少 config/dev 目錄")
        
        print_success("環境分析完成")
        return analysis
    
    def initialize_drones(self) -> None:
        """初始化無人機編隊"""
        print_info("🤖 初始化無人機編隊...")
        
        if 'drone_fleet' not in self.config:
            print_warn("配置中無無人機編隊定義")
            return
        
        fleet = self.config['drone_fleet']
        for drone_id, drone_config in fleet.items():
            self.drones[drone_id] = {
                'name': drone_config.get('name', drone_id),
                'script': drone_config.get('script'),
                'priority': drone_config.get('priority', 99),
                'auto_start': drone_config.get('auto_start', False),
                'status': 'initialized'
            }
            print_info(f"  ✓ {drone_config.get('name', drone_id)}")
        
        print_success(f"已初始化 {len(self.drones)} 個無人機")
    
    def start_drone(self, drone_id: str) -> bool:
        """啟動指定的無人機"""
        if drone_id not in self.drones:
            print_error(f"無人機 {drone_id} 不存在")
            return False
        
        drone = self.drones[drone_id]
        script_path = self.project_root / drone['script']
        
        if not script_path.exists():
            print_warn(f"無人機腳本不存在: {script_path}")
            drone['status'] = 'script_missing'
            return False
        
        print_info(f"啟動無人機: {drone['name']}")
        drone['status'] = 'running'
        return True
    
    def auto_start_drones(self) -> None:
        """自動啟動設定為 auto_start 的無人機"""
        print_info("🚀 自動啟動無人機...")
        
        # 按優先級排序
        sorted_drones = sorted(
            self.drones.items(),
            key=lambda x: x[1].get('priority', 99)
        )
        
        for drone_id, drone in sorted_drones:
            if drone.get('auto_start'):
                self.start_drone(drone_id)
    
    def run_auto_mode(self) -> int:
        """執行自動模式"""
        print_color(Colors.CYAN, """
╔═══════════════════════════════════════╗
║   SynergyMesh 無人機協調器 v2.0       ║
║          自動模式啟動中               ║
╚═══════════════════════════════════════╝
        """)
        
        # 載入配置
        if not self.load_config():
            print_error("無法載入配置，使用預設設定")
        
        # 分析環境
        analysis = self.analyze_environment()
        
        # 顯示分析結果
        print_info("📊 環境分析報告:")
        for tool, info in analysis['tools'].items():
            status = '✅' if info.get('installed') else '❌'
            version = info.get('version', '未安裝')
            print(f"  {status} {tool}: {version}")
        
        print("")
        
        # 顯示建議
        if analysis['recommendations']:
            print_info("💡 建議:")
            for rec in analysis['recommendations']:
                print(f"  • {rec}")
            print("")
        
        # 初始化並啟動無人機
        self.initialize_drones()
        self.auto_start_drones()
        
        print_success("✅ 自動模式執行完成")
        return 0
    
    def run_status(self) -> int:
        """顯示系統狀態"""
        print_info("📊 系統狀態:")
        
        if not self.load_config():
            return 1
        
        self.initialize_drones()
        
        for drone_id, drone in self.drones.items():
            status_icon = {
                'initialized': '🔵',
                'running': '🟢',
                'stopped': '🔴',
                'script_missing': '⚠️'
            }.get(drone['status'], '❓')
            
            print(f"  {status_icon} {drone['name']} ({drone_id}): {drone['status']}")
        
        return 0
    
    def run_health_check(self) -> int:
        """執行健康檢查"""
        print_info("🏥 執行健康檢查...")
        
        checks_passed = 0
        checks_total = 0
        
        # 檢查配置檔案
        checks_total += 1
        if (self.project_root / 'drone-config.yml').exists():
            print_success("  ✓ drone-config.yml 存在")
            checks_passed += 1
        else:
            print_error("  ✗ drone-config.yml 不存在")
        
        # 檢查目錄結構
        dirs_to_check = ['config/dev', '.vscode', 'shared']
        for dir_name in dirs_to_check:
            checks_total += 1
            if (self.project_root / dir_name).exists():
                print_success(f"  ✓ {dir_name}/ 存在")
                checks_passed += 1
            else:
                print_error(f"  ✗ {dir_name}/ 不存在")
        
        # 顯示結果
        print("")
        print_info(f"健康檢查結果: {checks_passed}/{checks_total} 通過")
        
        return 0 if checks_passed == checks_total else 1


def main() -> int:
    """主程式進入點"""
    parser = argparse.ArgumentParser(
        description='SynergyMesh 無人機協調器',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--mode', '-m',
        choices=['auto', 'status', 'health'],
        default='auto',
        help='運行模式: auto(自動), status(狀態), health(健康檢查)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='詳細輸出'
    )
    
    args = parser.parse_args()
    
    coordinator = DroneCoordinator()
    
    if args.mode == 'auto':
        return coordinator.run_auto_mode()
    elif args.mode == 'status':
        return coordinator.run_status()
    elif args.mode == 'health':
        return coordinator.run_health_check()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
