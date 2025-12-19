#!/usr/bin/env python3
"""
P0 安全與監控驗證工具
Verifies all P0 critical safety and monitoring items

執行此腳本以驗證：
1. 緊急停止按鈕功能
2. 安全機制配置
3. 關鍵指標監控
4. 測試覆蓋率目標
5. CI/CD 關鍵路徑
"""

import os
import sys
import yaml
import json
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class VerificationResult:
    """驗證結果"""
    item: str
    status: str  # PASS, FAIL, WARNING, SKIP
    message: str
    details: Dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class P0SafetyVerifier:
    """P0 安全驗證器"""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.results: List[VerificationResult] = []

    def verify_all(self) -> List[VerificationResult]:
        """執行所有驗證"""
        print("🔍 開始 P0 安全與監控驗證...\n")

        # 1. 驗證緊急停止機制
        self._verify_emergency_stop()

        # 2. 驗證安全機制配置
        self._verify_safety_mechanisms()

        # 3. 驗證監控配置
        self._verify_monitoring_config()

        # 4. 驗證測試覆蓋率
        self._verify_test_coverage()

        # 5. 驗證 CI/CD 配置
        self._verify_cicd_config()

        return self.results

    def _verify_emergency_stop(self):
        """驗證緊急停止按鈕功能"""
        print("1️⃣  驗證緊急停止機制...")

        # 檢查緊急停止實現文件
        emergency_files = [
            self.repo_root / "src/core/safety/emergency_stop.py",
            self.repo_root / "src/services/agents/dependency-manager/src/crossplatform/emergency_response.py",
            self.repo_root / "src/ai/agents/dependency-manager/src/crossplatform/emergency_response.py",
        ]

        found_files = [f for f in emergency_files if f.exists()]

        if not found_files:
            self.results.append(VerificationResult(
                item="緊急停止按鈕實現",
                status="FAIL",
                message="未找到緊急停止實現文件",
                details={"expected_files": [str(f) for f in emergency_files]}
            ))
            print("   ❌ FAIL: 未找到緊急停止實現")
            return

        # 檢查實現內容
        has_implementation = False
        for file_path in found_files:
            try:
                content = file_path.read_text()
                # 檢查是否有實際的實現而非僅TODO
                if "def emergency_stop" in content or "class EmergencyStop" in content:
                    if "NotImplementedError" not in content and "TODO" not in content:
                        has_implementation = True
                        break
            except Exception as e:
                print(f"   ⚠️  讀取 {file_path} 失敗: {e}")

        if has_implementation:
            self.results.append(VerificationResult(
                item="緊急停止按鈕實現",
                status="PASS",
                message=f"緊急停止機制已實現 ({len(found_files)} 個文件)",
                details={"files": [str(f) for f in found_files]}
            ))
            print("   ✅ PASS: 緊急停止機制已實現")
        else:
            self.results.append(VerificationResult(
                item="緊急停止按鈕實現",
                status="WARNING",
                message="找到緊急停止文件但實現可能不完整",
                details={"files": [str(f) for f in found_files]}
            ))
            print("   ⚠️  WARNING: 實現可能不完整")

    def _verify_safety_mechanisms(self):
        """驗證安全機制配置"""
        print("\n2️⃣  驗證安全機制配置...")

        config_files = [
            self.repo_root / "config/safety-mechanisms.yaml",
            self.repo_root / "src/autonomous/infrastructure/config/safety-mechanisms.yaml",
        ]

        found_config = None
        for config_file in config_files:
            if config_file.exists():
                found_config = config_file
                break

        if not found_config:
            self.results.append(VerificationResult(
                item="安全機制配置",
                status="FAIL",
                message="未找到安全機制配置文件",
            ))
            print("   ❌ FAIL: 未找到配置文件")
            return

        try:
            with open(found_config, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            # 檢查關鍵配置項
            checks = {
                "safety.enabled": config.get("safety", {}).get("enabled", False),
                "circuit_breaker.enabled": config.get("circuit_breaker", {}).get("enabled", False),
                "escalation_ladder.enabled": config.get("escalation_ladder", {}).get("enabled", False),
            }

            all_enabled = all(checks.values())

            if all_enabled:
                self.results.append(VerificationResult(
                    item="安全機制配置",
                    status="PASS",
                    message="所有安全機制已啟用",
                    details={"config_file": str(found_config), "checks": checks}
                ))
                print("   ✅ PASS: 所有安全機制已啟用")
            else:
                disabled = [k for k, v in checks.items() if not v]
                self.results.append(VerificationResult(
                    item="安全機制配置",
                    status="WARNING",
                    message=f"部分安全機制未啟用: {', '.join(disabled)}",
                    details={"config_file": str(found_config), "checks": checks}
                ))
                print(f"   ⚠️  WARNING: {', '.join(disabled)} 未啟用")

        except Exception as e:
            self.results.append(VerificationResult(
                item="安全機制配置",
                status="FAIL",
                message=f"配置文件解析失敗: {e}",
            ))
            print(f"   ❌ FAIL: {e}")

    def _verify_monitoring_config(self):
        """驗證監控配置"""
        print("\n3️⃣  驗證監控配置...")

        # 檢查 Prometheus 配置
        prometheus_files = list(self.repo_root.glob("**/prometheus*.{yml,yaml}"))

        # 檢查監控相關目錄
        monitoring_dirs = [
            self.repo_root / "infrastructure/monitoring",
            self.repo_root / "src/autonomous/infrastructure/monitoring",
        ]

        monitoring_exists = any(d.exists() for d in monitoring_dirs)

        if prometheus_files or monitoring_exists:
            self.results.append(VerificationResult(
                item="監控配置",
                status="PASS",
                message=f"監控配置已存在 ({len(prometheus_files)} 個 Prometheus 配置)",
                details={
                    "prometheus_files": [str(f) for f in prometheus_files],
                    "monitoring_dirs": [str(d) for d in monitoring_dirs if d.exists()]
                }
            ))
            print("   ✅ PASS: 監控配置已存在")
        else:
            self.results.append(VerificationResult(
                item="監控配置",
                status="WARNING",
                message="未找到監控配置，建議配置 Prometheus/Grafana",
            ))
            print("   ⚠️  WARNING: 建議配置監控系統")

    def _verify_test_coverage(self):
        """驗證測試覆蓋率配置"""
        print("\n4️⃣  驗證測試覆蓋率配置...")

        # 檢查 pytest 配置
        pytest_config = self.repo_root / "pyproject.toml"

        if pytest_config.exists():
            try:
                with open(pytest_config, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 檢查是否有覆蓋率配置
                has_coverage = "coverage" in content.lower() or "pytest-cov" in content

                if has_coverage:
                    # 嘗試提取覆蓋率目標
                    if "fail_under" in content:
                        import re
                        match = re.search(r'fail_under\s*=\s*(\d+)', content)
                        target = int(match.group(1)) if match else None

                        if target and target >= 80:
                            self.results.append(VerificationResult(
                                item="測試覆蓋率目標",
                                status="PASS",
                                message=f"覆蓋率目標已設置: {target}%",
                                details={"target": target, "config": str(pytest_config)}
                            ))
                            print(f"   ✅ PASS: 覆蓋率目標 {target}%")
                        else:
                            self.results.append(VerificationResult(
                                item="測試覆蓋率目標",
                                status="WARNING",
                                message=f"覆蓋率目標偏低: {target}% (建議 ≥85%)",
                                details={"target": target}
                            ))
                            print(f"   ⚠️  WARNING: 目標偏低 {target}%")
                    else:
                        self.results.append(VerificationResult(
                            item="測試覆蓋率目標",
                            status="WARNING",
                            message="已配置覆蓋率但未設置 fail_under 目標",
                        ))
                        print("   ⚠️  WARNING: 未設置fail_under目標")
                else:
                    self.results.append(VerificationResult(
                        item="測試覆蓋率目標",
                        status="WARNING",
                        message="pytest 配置中未找到覆蓋率設置",
                    ))
                    print("   ⚠️  WARNING: 未配置覆蓋率")

            except Exception as e:
                self.results.append(VerificationResult(
                    item="測試覆蓋率目標",
                    status="FAIL",
                    message=f"配置解析失敗: {e}",
                ))
                print(f"   ❌ FAIL: {e}")
        else:
            self.results.append(VerificationResult(
                item="測試覆蓋率目標",
                status="WARNING",
                message="未找到 pyproject.toml 配置",
            ))
            print("   ⚠️  WARNING: 未找到配置文件")

    def _verify_cicd_config(self):
        """驗證 CI/CD 配置"""
        print("\n5️⃣  驗證 CI/CD 配置...")

        # 檢查 GitHub Actions workflows
        workflows_dir = self.repo_root / ".github/workflows"

        if not workflows_dir.exists():
            self.results.append(VerificationResult(
                item="CI/CD 配置",
                status="FAIL",
                message="未找到 .github/workflows 目錄",
            ))
            print("   ❌ FAIL: 未找到workflows目錄")
            return

        workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))

        if not workflow_files:
            self.results.append(VerificationResult(
                item="CI/CD 配置",
                status="FAIL",
                message="workflows 目錄中無workflow文件",
            ))
            print("   ❌ FAIL: 無workflow文件")
            return

        # 檢查關鍵 workflows
        critical_workflows = {
            "build": False,
            "test": False,
            "lint": False,
        }

        for wf_file in workflow_files:
            try:
                with open(wf_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if "build" in content or "compile" in content:
                        critical_workflows["build"] = True
                    if "test" in content or "pytest" in content:
                        critical_workflows["test"] = True
                    if "lint" in content or "eslint" in content or "pylint" in content:
                        critical_workflows["lint"] = True
            except:
                pass

        missing = [k for k, v in critical_workflows.items() if not v]

        if not missing:
            self.results.append(VerificationResult(
                item="CI/CD 配置",
                status="PASS",
                message=f"所有關鍵 CI/CD workflows 已配置 ({len(workflow_files)} 個文件)",
                details={"workflows": critical_workflows, "files": [f.name for f in workflow_files]}
            ))
            print(f"   ✅ PASS: {len(workflow_files)} 個workflows已配置")
        else:
            self.results.append(VerificationResult(
                item="CI/CD 配置",
                status="WARNING",
                message=f"缺少關鍵workflows: {', '.join(missing)}",
                details={"workflows": critical_workflows}
            ))
            print(f"   ⚠️  WARNING: 缺少 {', '.join(missing)}")

    def generate_report(self) -> Dict:
        """生成驗證報告"""
        passed = sum(1 for r in self.results if r.status == "PASS")
        failed = sum(1 for r in self.results if r.status == "FAIL")
        warnings = sum(1 for r in self.results if r.status == "WARNING")
        skipped = sum(1 for r in self.results if r.status == "SKIP")

        total = len(self.results)
        pass_rate = (passed / total * 100) if total > 0 else 0

        return {
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "skipped": skipped,
                "pass_rate": f"{pass_rate:.1f}%",
            },
            "results": [
                {
                    "item": r.item,
                    "status": r.status,
                    "message": r.message,
                    "details": r.details,
                    "timestamp": r.timestamp,
                }
                for r in self.results
            ],
            "generated_at": datetime.now().isoformat(),
        }

    def print_summary(self):
        """打印驗證摘要"""
        print("\n" + "="*70)
        print("📊 驗證摘要")
        print("="*70)

        report = self.generate_report()
        summary = report["summary"]

        print(f"✅ 通過: {summary['passed']}")
        print(f"❌ 失敗: {summary['failed']}")
        print(f"⚠️  警告: {summary['warnings']}")
        print(f"⏭️  跳過: {summary['skipped']}")
        print(f"\n通過率: {summary['pass_rate']}")

        print("\n" + "="*70)

        # 顯示失敗項目
        failed_items = [r for r in self.results if r.status == "FAIL"]
        if failed_items:
            print("\n🔴 需要立即修復的項目:")
            for r in failed_items:
                print(f"   - {r.item}: {r.message}")

        # 顯示警告項目
        warning_items = [r for r in self.results if r.status == "WARNING"]
        if warning_items:
            print("\n🟡 建議改進的項目:")
            for r in warning_items:
                print(f"   - {r.item}: {r.message}")

        print()

def main():
    """主函數"""
    repo_root = Path(__file__).parent.parent

    verifier = P0SafetyVerifier(repo_root)
    verifier.verify_all()

    # 打印摘要
    verifier.print_summary()

    # 生成 JSON 報告
    report = verifier.generate_report()
    report_file = repo_root / "P0_SAFETY_VERIFICATION_REPORT.json"

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"📄 詳細報告已保存: {report_file}\n")

    # 返回退出碼
    failed_count = report["summary"]["failed"]
    sys.exit(1 if failed_count > 0 else 0)

if __name__ == "__main__":
    main()
