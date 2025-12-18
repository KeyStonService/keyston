#!/usr/bin/env python3
"""
Self-Healing Integration Validation Script
無人島整合驗證腳本

驗證無人島系統與 SynergyMesh 治理框架的整合完整性。

Author: SynergyMesh Self-Healing Team
Version: 1.0.0
Updated: 2025-12-11T12:16:00Z
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml


class ValidationResult:
    """驗證結果"""
    def __init__(self, name: str):
        self.name = name
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.checks: List[Dict[str, Any]] = []
    
    def add_pass(self, check: str, message: str = ""):
        """添加通過的檢查"""
        self.passed += 1
        self.checks.append({
            'check': check,
            'status': 'PASS',
            'message': message
        })
    
    def add_fail(self, check: str, message: str):
        """添加失敗的檢查"""
        self.failed += 1
        self.checks.append({
            'check': check,
            'status': 'FAIL',
            'message': message
        })
    
    def add_warning(self, check: str, message: str):
        """添加警告"""
        self.warnings += 1
        self.checks.append({
            'check': check,
            'status': 'WARNING',
            'message': message
        })
    
    @property
    def total(self) -> int:
        """總檢查數"""
        return self.passed + self.failed + self.warnings
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total == 0:
            return 0.0
        return (self.passed / self.total) * 100


class UnmannedIslandValidator:
    """無人島整合驗證器"""
    
    def __init__(self, project_root: Path):
        """
        初始化驗證器
        
        Args:
            project_root: 專案根目錄
        """
        self.project_root = project_root
        self.governance_root = project_root / "governance"
        self.results: Dict[str, ValidationResult] = {}
    
    def validate_all(self) -> bool:
        """
        執行所有驗證
        
        Returns:
            是否所有驗證通過
        """
        print("=" * 80)
        print("🏝️ Self-Healing Integration Validation")
        print("=" * 80)
        print()
        
        start_time = time.time()
        
        # Phase 1: 配置文件驗證
        print("📋 Phase 1: Configuration Validation")
        self._validate_configuration_files()
        
        # Phase 2: AI Agents 驗證
        print("\n🤖 Phase 2: AI Agents Validation")
        self._validate_ai_agents()
        
        # Phase 3: 治理維度整合驗證
        print("\n🔗 Phase 3: Governance Dimensions Integration")
        self._validate_governance_integration()
        
        # Phase 4: API 端點驗證
        print("\n🌐 Phase 4: API Endpoints Validation")
        self._validate_api_endpoints()
        
        # Phase 5: 性能基線驗證
        print("\n⚡ Phase 5: Performance Baselines Validation")
        self._validate_performance_baselines()
        
        elapsed_time = time.time() - start_time
        
        # 打印總結
        print("\n" + "=" * 80)
        print("📊 Validation Summary")
        print("=" * 80)
        
        total_passed = 0
        total_failed = 0
        total_warnings = 0
        
        for category, result in self.results.items():
            print(f"\n{category}:")
            print(f"  ✅ Passed:   {result.passed}")
            print(f"  ❌ Failed:   {result.failed}")
            print(f"  ⚠️  Warnings: {result.warnings}")
            print(f"  📊 Success:  {result.success_rate:.1f}%")
            
            total_passed += result.passed
            total_failed += result.failed
            total_warnings += result.warnings
        
        total_checks = total_passed + total_failed + total_warnings
        overall_success = (total_passed / total_checks * 100) if total_checks > 0 else 0
        
        print(f"\n{'=' * 80}")
        print(f"Overall Results:")
        print(f"  Total Checks: {total_checks}")
        print(f"  ✅ Passed:    {total_passed}")
        print(f"  ❌ Failed:    {total_failed}")
        print(f"  ⚠️  Warnings:  {total_warnings}")
        print(f"  📊 Success:   {overall_success:.1f}%")
        print(f"  ⏱️  Time:      {elapsed_time:.2f}s")
        print("=" * 80)
        
        # 保存詳細報告
        self._save_report()
        
        # 驗證成功條件: 失敗數為 0 且成功率 > 80%
        return total_failed == 0 and overall_success >= 80.0
    
    def _validate_configuration_files(self):
        """驗證配置文件"""
        result = ValidationResult("Configuration Files")
        
        # 檢查關鍵配置文件
        critical_files = [
            ("governance/00-vision-strategy/AI-BEHAVIOR-CONTRACT.md", "AI 行為契約"),
            ("governance/00-vision-strategy/INSTANT-EXECUTION-MANIFEST.yaml", "即時執行清單"),
            ("governance/14-improvement/self-healing-self-healing.yaml", "自我修復框架"),
            ("governance/30-integration/self-healing-integration-manifest.md", "整合清單"),
            ("governance/39-automation/self_healing_integration_engine.py", "整合引擎"),
        ]
        
        for file_path, description in critical_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                result.add_pass(f"{description} 存在", str(full_path))
                
                # 驗證 YAML 文件語法
                if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            yaml.safe_load(f)
                        result.add_pass(f"{description} YAML 語法正確")
                    except yaml.YAMLError as e:
                        result.add_fail(f"{description} YAML 語法錯誤", str(e))
                
                # 驗證 Python 文件語法
                if file_path.endswith('.py'):
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            compile(f.read(), full_path, 'exec')
                        result.add_pass(f"{description} Python 語法正確")
                    except SyntaxError as e:
                        result.add_fail(f"{description} Python 語法錯誤", str(e))
            else:
                result.add_fail(f"{description} 不存在", str(full_path))
        
        self.results['Configuration Files'] = result
    
    def _validate_ai_agents(self):
        """驗證 AI Agents"""
        result = ValidationResult("AI Agents")
        
        # 定義 7 AI Agents
        agents = [
            ("CEO Agent", "ai-agents-executive/", "戰略決策"),
            ("Architect Agent", "island-ai/src/agents/architect", "架構設計"),
            ("Developer Agent", "island-ai/src/agents/developer", "代碼實現"),
            ("Tester Agent", "island-ai/src/agents/tester", "質量保證"),
            ("Deployer Agent", "v2-multi-islands/islands/deployment", "部署管理"),
            ("Monitor Agent", "v2-multi-islands/islands/monitoring", "監控分析"),
            ("Coordinator Agent", "v2-multi-islands/orchestrator", "協調器"),
        ]
        
        for agent_name, agent_path, agent_role in agents:
            full_path = self.project_root / agent_path
            if full_path.exists():
                result.add_pass(f"{agent_name} ({agent_role}) 目錄存在", str(full_path))
            else:
                result.add_warning(f"{agent_name} ({agent_role}) 目錄不存在", 
                                   f"路徑: {full_path} (可能尚未實現)")
        
        # 檢查整合引擎是否能註冊所有 Agents
        engine_path = self.governance_root / "39-automation/self_healing_integration_engine.py"
        if engine_path.exists():
            try:
                with open(engine_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for agent_name, _, _ in agents:
                        if agent_name.replace(' ', '_').lower() in content.lower():
                            result.add_pass(f"{agent_name} 已在整合引擎中註冊")
                        else:
                            result.add_warning(f"{agent_name} 未在整合引擎中找到", 
                                             "可能使用不同命名")
            except Exception as e:
                result.add_fail("無法讀取整合引擎", str(e))
        
        self.results['AI Agents'] = result
    
    def _validate_governance_integration(self):
        """驗證治理維度整合"""
        result = ValidationResult("Governance Integration")
        
        # 檢查關鍵治理維度
        dimensions = [
            ("00-vision-strategy", "Vision & Strategy"),
            ("14-improvement", "Improvement & Learning"),
            ("28-tests", "Tests & Validation"),
            ("30-integration", "Integration & Coordination"),
            ("39-automation", "Automation & Orchestration"),
        ]
        
        for dim_id, dim_name in dimensions:
            dim_path = self.governance_root / dim_id
            if dim_path.exists():
                result.add_pass(f"{dim_name} ({dim_id}) 維度存在", str(dim_path))
                
                # 檢查是否有無人島相關文件
                legacy_files = list(dim_path.glob("*legacy*"))
                if legacy_files:
                    result.add_pass(f"{dim_name} 有無人島整合文件", 
                                  f"找到 {len(legacy_files)} 個相關文件")
                else:
                    result.add_warning(f"{dim_name} 無無人島整合文件", 
                                     "可能需要添加整合配置")
            else:
                result.add_fail(f"{dim_name} ({dim_id}) 維度不存在", str(dim_path))
        
        # 檢查 AUTONOMOUS_AGENT_STATE.md 是否包含無人島整合狀態
        state_file = self.governance_root / "00-vision-strategy/AUTONOMOUS_AGENT_STATE.md"
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'self_healing_integration' in content.lower():
                        result.add_pass("AUTONOMOUS_AGENT_STATE.md 包含無人島整合狀態")
                    else:
                        result.add_fail("AUTONOMOUS_AGENT_STATE.md 缺少無人島整合狀態", 
                                      "請更新文件以包含整合狀態")
            except Exception as e:
                result.add_fail("無法讀取 AUTONOMOUS_AGENT_STATE.md", str(e))
        
        self.results['Governance Integration'] = result
    
    def _validate_api_endpoints(self):
        """驗證 API 端點"""
        result = ValidationResult("API Endpoints")
        
        # 檢查整合清單中定義的 API 端點
        manifest_path = self.governance_root / "30-integration/self-healing-integration-manifest.md"
        if manifest_path.exists():
            result.add_pass("整合清單存在")
            
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # 檢查關鍵 API 端點定義
                    endpoints = [
                        "/api/vision/strategy",
                        "/api/improvement/heal",
                        "/api/tests/validate",
                        "/api/integration/status",
                        "/api/automation/deploy",
                        "/api/coordinator/orchestrate",
                    ]
                    
                    for endpoint in endpoints:
                        if endpoint in content:
                            result.add_pass(f"API 端點 {endpoint} 已定義")
                        else:
                            result.add_warning(f"API 端點 {endpoint} 未找到", 
                                             "可能使用不同路徑")
            except Exception as e:
                result.add_fail("無法讀取整合清單", str(e))
        else:
            result.add_fail("整合清單不存在", str(manifest_path))
        
        self.results['API Endpoints'] = result
    
    def _validate_performance_baselines(self):
        """驗證性能基線"""
        result = ValidationResult("Performance Baselines")
        
        # 檢查 INSTANT-EXECUTION-MANIFEST.yaml 中的性能定義
        manifest_path = self.governance_root / "00-vision-strategy/INSTANT-EXECUTION-MANIFEST.yaml"
        if manifest_path.exists():
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    
                    # 檢查關鍵性能指標
                    if 'instant_execution_definition' in data:
                        result.add_pass("即時執行定義存在")
                        
                        exec_def = data['instant_execution_definition']
                        
                        # 理解時間
                        if 'understanding' in exec_def:
                            target = exec_def['understanding'].get('target_time', '')
                            if '< 1 second' in target or '1 second' in target:
                                result.add_pass("理解時間目標正確設置 (< 1 秒)")
                            else:
                                result.add_fail("理解時間目標不正確", f"當前: {target}")
                        
                        # 執行時間
                        if 'execution' in exec_def:
                            target = exec_def['execution'].get('target_time', '')
                            if '2-3 minutes' in target or '3 minutes' in target:
                                result.add_pass("執行時間目標正確設置 (2-3 分鐘)")
                            else:
                                result.add_warning("執行時間目標可能需要調整", f"當前: {target}")
                    
                    # 檢查自我修復時間
                    if 'self_healing_standards' in data:
                        result.add_pass("自我修復標準定義存在")
                        
                        healing = data['self_healing_standards']
                        if 'total_mttr' in healing:
                            mttr = healing['total_mttr']
                            if '< 45 seconds' in mttr or '45 seconds' in mttr:
                                result.add_pass("MTTR 目標正確設置 (< 45 秒)")
                            else:
                                result.add_warning("MTTR 目標可能需要調整", f"當前: {mttr}")
                    
            except Exception as e:
                result.add_fail("無法解析 INSTANT-EXECUTION-MANIFEST.yaml", str(e))
        else:
            result.add_fail("INSTANT-EXECUTION-MANIFEST.yaml 不存在", str(manifest_path))
        
        self.results['Performance Baselines'] = result
    
    def _save_report(self):
        """保存詳細報告"""
        report_path = self.governance_root / "28-tests/reports/self_healing_validation_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'categories': {}
        }
        
        for category, result in self.results.items():
            report['categories'][category] = {
                'passed': result.passed,
                'failed': result.failed,
                'warnings': result.warnings,
                'total': result.total,
                'success_rate': result.success_rate,
                'checks': result.checks
            }
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n📄 Detailed report saved: {report_path}")
        except Exception as e:
            print(f"\n⚠️  Failed to save report: {e}")


def main():
    """主程序入口"""
    # 尋找專案根目錄
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / 'governance').exists():
            project_root = current
            break
        current = current.parent
    else:
        print("❌ Cannot find project root (governance directory not found)")
        sys.exit(1)
    
    # 創建驗證器並執行
    validator = UnmannedIslandValidator(project_root)
    success = validator.validate_all()
    
    # 返回適當的退出碼
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
