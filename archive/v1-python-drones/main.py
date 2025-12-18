#!/usr/bin/env python3
"""
SynergyMesh v1-python-drones 主執行入口

Python 無人機系統的主要入口點，提供命令行介面。
"""

import argparse
import sys
from pathlib import Path

# 確保可以導入本地模組
_current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(_current_dir))
sys.path.insert(0, str(_current_dir.parent))

# 使用相對導入
from drones import CoordinatorDrone, AutopilotDrone, DeploymentDrone
from utils import Colors, print_info, print_success, print_error


def show_banner() -> None:
    """顯示啟動標題"""
    print(f"{Colors.CYAN}")
    print("╔═══════════════════════════════════════╗")
    print("║    SynergyMesh v1-python-drones       ║")
    print("║       Python 無人機系統 v1.1          ║")
    print("╚═══════════════════════════════════════╝")
    print(f"{Colors.NC}")


def run_coordinator() -> int:
    """執行協調器無人機"""
    drone = CoordinatorDrone()
    drone.start()
    result = drone.execute()
    return 0 if result else 1


def run_autopilot() -> int:
    """執行自動駕駛無人機"""
    drone = AutopilotDrone()
    drone.start()
    result = drone.execute()
    return 0 if result else 1


def run_deployment() -> int:
    """執行部署無人機"""
    drone = DeploymentDrone()
    drone.start()
    result = drone.execute()
    return 0 if result.get('success', False) else 1


def run_auto() -> int:
    """自動模式 - 執行所有無人機"""
    print_info("🚁 啟動自動模式...")
    
    # 啟動協調器
    coordinator = CoordinatorDrone()
    coordinator.start()
    coordinator.execute()
    
    # 啟動自動駕駛
    autopilot = AutopilotDrone()
    autopilot.start()
    autopilot.execute()
    
    print_success("✅ 自動模式執行完成")
    return 0


def main() -> int:
    """主程式"""
    parser = argparse.ArgumentParser(
        description='SynergyMesh v1-python-drones - Python 無人機系統',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  python -m v1_python_drones.main --mode=auto       # 自動模式
  python -m v1_python_drones.main --drone=coordinator  # 執行協調器
  python -m v1_python_drones.main --drone=autopilot    # 執行自動駕駛
  python -m v1_python_drones.main --drone=deployment   # 執行部署
        """
    )
    
    parser.add_argument(
        '--mode', '-m',
        choices=['auto', 'manual'],
        default='auto',
        help='運行模式: auto(自動), manual(手動)'
    )
    
    parser.add_argument(
        '--drone', '-d',
        choices=['coordinator', 'autopilot', 'deployment', 'all'],
        help='指定要執行的無人機'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='詳細輸出'
    )
    
    args = parser.parse_args()
    
    show_banner()
    
    # 根據參數執行
    if args.drone:
        drone_handlers = {
            'coordinator': run_coordinator,
            'autopilot': run_autopilot,
            'deployment': run_deployment,
            'all': run_auto,
        }
        handler = drone_handlers.get(args.drone)
        if handler:
            return handler()
        else:
            print_error(f"未知無人機: {args.drone}")
            return 1
    
    # 預設執行自動模式
    if args.mode == 'auto':
        return run_auto()
    else:
        print_info("手動模式 - 請指定 --drone 參數")
        return 0


if __name__ == '__main__':
    sys.exit(main())
