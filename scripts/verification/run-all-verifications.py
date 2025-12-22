#!/usr/bin/env python3
"""
全面驗證 - Complete Verification Pipeline
執行基礎、進階和生產三個層級的完整驗證
"""

import sys
import subprocess
from pathlib import Path

def run_verification_stage(script_name: str, directory: str) -> bool:
    """執行單個驗證階段"""
    script_path = Path(__file__).parent / script_name
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path), directory],
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 執行 {script_name} 失敗: {e}")
        return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='完整驗證流程')
    parser.add_argument('directory', nargs='?', default='.', help='要驗證的目錄')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🚀 MachineNativeOps 完整驗證流程")
    print("=" * 70)
    print()
    
    stages = [
        ("基礎驗證", "basic-verification.py"),
        ("進階驗證", "advanced-verification.py"),
        ("生產驗證", "production-verification.py")
    ]
    
    results = []
    
    for stage_name, script_name in stages:
        print(f"\n{'=' * 70}")
        print(f"開始 {stage_name}")
        print(f"{'=' * 70}\n")
        
        success = run_verification_stage(script_name, args.directory)
        results.append((stage_name, success))
        
        if not success:
            print(f"\n❌ {stage_name} 失敗，停止後續驗證")
            break
    
    # 最終總結
    print("\n" + "=" * 70)
    print("📊 驗證總結")
    print("=" * 70)
    
    for stage_name, success in results:
        status = "✅ 通過" if success else "❌ 失敗"
        print(f"{status} - {stage_name}")
    
    all_passed = all(success for _, success in results)
    
    print("=" * 70)
    
    if all_passed and len(results) == len(stages):
        print("✅ 所有驗證階段通過！")
        print()
        print("🎉 專案已通過完整驗證：")
        print("  ✅ 基礎驗證 - YAML 語法、命名空間一致性、資源類型標準化")
        print("  ✅ 進階驗證 - 架構模式、部署配置、整合點、效能基準")
        print("  ✅ 生產驗證 - 端到端功能、安全掃描、負載測試、恢復測試")
        print()
        print("💯 100% 合規！")
        sys.exit(0)
    else:
        print("❌ 驗證未完全通過，請檢查上述錯誤")
        sys.exit(1)

if __name__ == '__main__':
    main()
