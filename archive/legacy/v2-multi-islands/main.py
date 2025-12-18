#!/usr/bin/env python3
"""
SynergyMesh v2-multi-islands 主執行入口

多語言自動化無人之島系統的主要入口點，提供命令行介面。
"""

import argparse
import sys
from pathlib import Path

# 確保可以導入本地模組
_current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(_current_dir))
sys.path.insert(0, str(_current_dir.parent))

from islands import GoIsland, JavaIsland, PythonIsland, RustIsland, TypeScriptIsland
from orchestrator import IslandOrchestrator
from utils import Colors, print_error, print_info, print_success


def show_banner() -> None:
    """顯示啟動標題"""
    print(f"{Colors.CYAN}")
    print("╔═══════════════════════════════════════╗")
    print("║    SynergyMesh v2-multi-islands       ║")
    print("║   多語言自動化無人之島系統 v2.0         ║")
    print("╚═══════════════════════════════════════╝")
    print(f"{Colors.NC}")


def run_orchestrator() -> int:
    """執行島嶼協調器"""
    orchestrator = IslandOrchestrator()
    orchestrator.start()
    result = orchestrator.execute()
    return 0 if result else 1


def run_island(island_id: str) -> int:
    """執行指定島嶼"""
    island_map = {
        'rust': RustIsland,
        'go': GoIsland,
        'typescript': TypeScriptIsland,
        'python': PythonIsland,
        'java': JavaIsland,
    }

    island_class = island_map.get(island_id)
    if not island_class:
        print_error(f"未知島嶼: {island_id}")
        print_info(f"可用島嶼: {', '.join(island_map.keys())}")
        return 1

    island = island_class()
    island.activate()
    result = island.execute()
    return 0 if result else 1


def run_auto() -> int:
    """自動模式 - 執行協調器和所有可用島嶼"""
    print_info("🏝️ 啟動自動模式...")

    # 啟動協調器
    orchestrator = IslandOrchestrator()
    orchestrator.start()
    orchestrator.execute()

    # 啟動 Python 島嶼 (因為我們是 Python 環境)
    print()
    python_island = PythonIsland()
    python_island.activate()
    python_island.execute()

    # 啟動 TypeScript 島嶼 (如果 Node.js 可用)
    print()
    ts_island = TypeScriptIsland()
    ts_island.activate()
    ts_island.execute()

    print_success("✅ 自動模式執行完成")
    return 0


def run_all_islands() -> int:
    """執行所有島嶼"""
    print_info("🌊 啟動所有島嶼...")

    islands = [
        RustIsland(),
        GoIsland(),
        TypeScriptIsland(),
        PythonIsland(),
        JavaIsland(),
    ]

    for island in islands:
        print()
        island.activate()
        island.execute()

    print_success("✅ 所有島嶼執行完成")
    return 0


def main() -> int:
    """主程式"""
    parser = argparse.ArgumentParser(
        description='SynergyMesh v2-multi-islands - 多語言自動化無人之島系統',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  python3 v2-multi-islands/main.py --mode=auto           # 自動模式
  python3 v2-multi-islands/main.py --island=python       # 執行 Python 島嶼
  python3 v2-multi-islands/main.py --island=rust         # 執行 Rust 島嶼
  python3 v2-multi-islands/main.py --island=go           # 執行 Go 島嶼
  python3 v2-multi-islands/main.py --island=typescript   # 執行 TypeScript 島嶼
  python3 v2-multi-islands/main.py --island=java         # 執行 Java 島嶼
  python3 v2-multi-islands/main.py --all                 # 執行所有島嶼
        """
    )

    parser.add_argument(
        '--mode', '-m',
        choices=['auto', 'manual'],
        default='auto',
        help='運行模式: auto(自動), manual(手動)'
    )

    parser.add_argument(
        '--island', '-i',
        choices=['rust', 'go', 'typescript', 'python', 'java', 'orchestrator'],
        help='指定要執行的島嶼'
    )

    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='執行所有島嶼'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='詳細輸出'
    )

    args = parser.parse_args()

    show_banner()

    # 根據參數執行
    if args.all:
        return run_all_islands()

    if args.island:
        if args.island == 'orchestrator':
            return run_orchestrator()
        return run_island(args.island)

    # 預設執行自動模式
    if args.mode == 'auto':
        return run_auto()
    else:
        print_info("手動模式 - 請指定 --island 參數")
        return 0


if __name__ == '__main__':
    sys.exit(main())
