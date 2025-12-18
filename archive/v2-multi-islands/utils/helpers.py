#!/usr/bin/env python3
"""
通用輔助函數
"""


class Colors:
    """終端機顏色"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'


def print_color(color: str, message: str) -> None:
    """輸出帶顏色的訊息"""
    print(f"{color}{message}{Colors.NC}")


def print_info(message: str) -> None:
    """輸出資訊訊息"""
    print_color(Colors.BLUE, f"[INFO] {message}")


def print_success(message: str) -> None:
    """輸出成功訊息"""
    print_color(Colors.GREEN, f"[SUCCESS] {message}")


def print_warn(message: str) -> None:
    """輸出警告訊息"""
    print_color(Colors.YELLOW, f"[WARN] {message}")


def print_error(message: str) -> None:
    """輸出錯誤訊息"""
    print_color(Colors.RED, f"[ERROR] {message}")
