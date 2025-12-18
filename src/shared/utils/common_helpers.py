#!/usr/bin/env python3
"""
通用輔助函數

提供 v1-python-drones 和 v2-multi-islands 共用的工具函數。
"""

import subprocess
from pathlib import Path
from typing import Optional, Tuple


class Colors:
    """終端機顏色"""
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


def print_banner(title: str, subtitle: str = "") -> None:
    """輸出橫幅"""
    print(f"{Colors.CYAN}")
    print("╔═══════════════════════════════════════╗")
    print(f"║{title:^39}║")
    if subtitle:
        print(f"║{subtitle:^39}║")
    print("╚═══════════════════════════════════════╝")
    print(f"{Colors.NC}")


def print_info(message: str, prefix: str = "") -> None:
    """輸出資訊訊息"""
    tag = f"[{prefix}]" if prefix else ""
    print_color(Colors.BLUE, f"{tag}[INFO] {message}")


def print_success(message: str, prefix: str = "") -> None:
    """輸出成功訊息"""
    tag = f"[{prefix}]" if prefix else ""
    print_color(Colors.GREEN, f"{tag}[SUCCESS] {message}")


def print_warn(message: str, prefix: str = "") -> None:
    """輸出警告訊息"""
    tag = f"[{prefix}]" if prefix else ""
    print_color(Colors.YELLOW, f"{tag}[WARN] {message}")


def print_error(message: str, prefix: str = "") -> None:
    """輸出錯誤訊息"""
    tag = f"[{prefix}]" if prefix else ""
    print_color(Colors.RED, f"{tag}[ERROR] {message}")


def get_project_root() -> Path:
    """取得專案根目錄"""
    current = Path(__file__).resolve().parent
    
    root_markers = [
        'drone-config.yml',
        'island-control.yml',
        'package.json',
        'automation-entry.sh',
    ]
    
    while current != current.parent:
        for marker in root_markers:
            if (current / marker).exists():
                return current
        current = current.parent
    
    return Path.cwd()


def run_command(
    cmd: list[str],
    cwd: Optional[Path] = None,
    timeout: int = 60,
    capture: bool = True
) -> Tuple[int, str, str]:
    """
    執行命令
    
    Args:
        cmd: 命令和參數列表
        cwd: 工作目錄
        timeout: 超時時間（秒）
        capture: 是否捕獲輸出
        
    Returns:
        (返回碼, stdout, stderr)
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture,
            text=True,
            timeout=timeout,
            cwd=cwd
        )
        return result.returncode, result.stdout or "", result.stderr or ""
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except FileNotFoundError:
        return -1, "", f"Command not found: {cmd[0]}"
    except Exception as e:
        return -1, "", str(e)


def check_tool_available(tool: str, version_arg: str = "--version") -> Tuple[bool, Optional[str]]:
    """
    檢查工具是否可用
    
    Args:
        tool: 工具名稱
        version_arg: 版本參數
        
    Returns:
        (是否可用, 版本資訊)
    """
    returncode, stdout, _ = run_command([tool, version_arg], timeout=5)
    
    if returncode == 0:
        version = stdout.strip().split('\n')[0]
        return True, version
    
    return False, None
