#!/usr/bin/env python3
"""
MachineNativeOps 目錄重構驗證工具

這個腳本驗證目錄重構的完整性和正確性，包括：
1. 檢查目錄結構
2. 驗證文件完整性
3. 檢查導入路徑
4. 驗證配置文件
5. 生成驗證報告

使用方法：
python tools/validate_restructure.py [--detailed] [--fix-imports]
"""

import os
import sys
import json
import ast
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime
import re

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RestructureValidator:
    """目錄重構驗證器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.issues = []
        self.warnings = []
        self.fix_imports = False
        self.detailed = False
        
        # 預期的目錄結構
        self.expected_structure = {
            "src": {
                "core": {
                    "plugins": [
                        "ai_constitution", "ci_error_handler", "cloud_agent_delegation",
                        "drone_system", "execution_architecture", "execution_engine",
                        "main_system", "mcp_servers_enhanced", "mind_matrix",
                        "monitoring_system", "tech_stack", "training_system",
                        "virtual_experts", "yaml_module_system"
                    ],
                    "safety": [
                        "anomaly_detector", "autonomous_trust_engine", "checkpoint_manager",
                        "circuit_breaker", "emergency_stop", "escalation_ladder",
                        "hallucination_detector", "partial_rollback", "retry_policies",
                        "rollback_system", "safety_net"
                    ],
                    "services": [
                        "agent_registry", "capability_coordinator", "health_monitor",
                        "lifecycle_manager", "message_bus", "resource_manager",
                        "service_discovery", "state_manager", "task_scheduler"
                    ]
                },
                "platform": {
                    "agents": [
                        "ai_agent", "automation_agent", "ci_agent", "cloud_agent",
                        "data_agent", "devops_agent", "monitoring_agent", "security_agent"
                    ],
                    "automation": [
                        "pipeline_engine", "workflow_orchestrator", "task_scheduler",
                        "resource_optimizer", "auto_scaler", "health_checker"
                    ],
                    "integrations": [
                        "github", "gitlab", "jenkins", "docker", "kubernetes",
                        "aws", "azure", "gcp", "slack", "teams"
                    ]
                },
                "services": {
                    "api": [
                        "rest_api", "graphql_api", "websocket_api", "grpc_api"
                    ],
                    "data": [
                        "database", "cache", "message_queue", "file_storage",
                        "search_engine", "data_pipeline"
                    ],
                    "monitoring": [
                        "metrics", "logging", "tracing", "alerting", "dashboard"
                    ]
                },
                "shared": {
                    "types": [
                        "common_types", "api_types", "domain_types", "event_types"
                    ],
                    "utils": [
                        "helpers", "validators", "formatters", "parsers",
                        "converters", "calculators"
                    ],
                    "constants": [
                        "app_constants", "api_constants", "domain_constants",
                        "error_codes", "status_codes"
                    ]
                },
                "web": {
                    "admin": [
                        "dashboard", "user_management", "system_config",
                        "monitoring", "analytics"
                    ],
                    "client": [
                        "user_interface", "components", "pages", "services"
                    ],
                    "api": [
                        "routes", "controllers", "middleware", "handlers"
                    ]
                }
            },
            "config": {
                "ci-cd": [
                    "auto-fix-bot", "ci-agent", "ci-config", "ci-error-handler",
                    "drone-config"
                ],
                "deployment": [
                    "docker-compose", "dockerfile", "nginx", "deployment-pipelines"
                ],
                "monitoring": [
                    "prometheus", "grafana", "alerting", "dashboards"
                ],
                "environments": [
                    "env-files", "environment-configs", "secrets"
                ],
                "security": [
                    "security-policies", "safety-mechanisms", "access-control"
                ],
                "build-tools": [
                    "eslint", "jest", "postcss", "tailwind", "vite",
                    "drizzle", "typescript", "build-scripts"
                ],
                "governance": [
                    "system-manifest", "module-mapping", "architecture-specs",
                    "recovery-system", "evolution-configs"
                ]
            }
        }
        
        # 舊路徑到新路徑的映射
        self.path_mappings = {
            "src/core/modules": "src/core/plugins",
            "src/core/safety_mechanisms": "src/core/safety",
            "src/apps/web": "src/web/admin",
            "src/apps/cli": "src/platform/cli",
            "src/apps/api": "src/services/api"
        }
    
    def validate_directory_structure(self) -> Dict:
        """驗證目錄結構"""
        logger.info("🔍 驗證目錄結構...")
        
        result = {
            "valid": True,
            "missing_directories": [],
            "unexpected_directories": [],
            "details": {}
        }
        
        for main_dir, subdirs in self.expected_structure.items():
            main_path = self.project_root / main_dir
            
            if not main_path.exists():
                result["missing_directories"].append(str(main_path))
                result["valid"] = False
                continue
            
            result["details"][main_dir] = {}
            
            for subdir, categories in subdirs.items():
                subdir_path = main_path / subdir
                
                if not subdir_path.exists():
                    result["missing_directories"].append(str(subdir_path))
                    result["valid"] = False
                    result["details"][main_dir][subdir] = "missing"
                    continue
                
                result["details"][main_dir][subdir] = "exists"
                
                # 檢查子目錄
                if isinstance(categories, dict):
                    for category in categories.keys():
                        category_path = subdir_path / category
                        if not category_path.exists():
                            result["missing_directories"].append(str(category_path))
                            result["valid"] = False
                elif isinstance(categories, list):
                    # 對於列表，檢查是否有相應的文件或目錄
                    pass
        
        if result["missing_directories"]:
            logger.warning(f"⚠️ 缺少目錄: {len(result['missing_directories'])} 個")
            for missing in result["missing_directories"]:
                logger.warning(f"  - {missing}")
        
        return result
    
    def validate_file_integrity(self) -> Dict:
        """驗證文件完整性"""
        logger.info("📁 驗證文件完整性...")
        
        result = {
            "valid": True,
            "missing_files": [],
            "empty_files": [],
            "total_files": 0
        }
        
        # 檢查關鍵文件
        critical_files = [
            "src/core/plugins/plugin_system.py",
            "src/core/safety/autonomous_trust_engine.py",
            "src/core/safety/hallucination_detector.py",
            "src/services/index.ts",
            "src/services/routes.ts",
            "src/shared/types/naming-policy.schema.yaml"
        ]
        
        for file_path in critical_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                result["missing_files"].append(file_path)
                result["valid"] = False
            elif full_path.stat().st_size == 0:
                result["empty_files"].append(file_path)
                self.warnings.append(f"文件為空: {file_path}")
        
        # 統計文件數量
        for root_dir in ["src", "config"]:
            root_path = self.project_root / root_dir
            if root_path.exists():
                for file_path in root_path.rglob("*"):
                    if file_path.is_file() and not file_path.name.startswith('.'):
                        result["total_files"] += 1
        
        logger.info(f"📊 總文件數: {result['total_files']}")
        
        if result["missing_files"]:
            logger.error(f"❌ 缺少關鍵文件: {len(result['missing_files'])} 個")
            for missing in result["missing_files"]:
                logger.error(f"  - {missing}")
        
        return result
    
    def validate_import_paths(self) -> Dict:
        """驗證 Python 導入路徑"""
        logger.info("🔗 驗證導入路徑...")
        
        result = {
            "valid": True,
            "broken_imports": [],
            "fixed_imports": [],
            "files_checked": 0
        }
        
        # 掃描所有 Python 文件
        for py_file in self.project_root.rglob("*.py"):
            if py_file.name.startswith('.') or '__pycache__' in str(py_file):
                continue
            
            result["files_checked"] += 1
            try:
                self._check_python_imports(py_file, result)
            except Exception as e:
                logger.warning(f"⚠️ 無法分析文件 {py_file}: {e}")
        
        logger.info(f"📊 檢查了 {result['files_checked']} 個 Python 文件")
        
        if result["broken_imports"]:
            logger.error(f"❌ 發現 {len(result['broken_imports'])} 個損壞的導入")
            for broken in result["broken_imports"]:
                logger.error(f"  - {broken}")
        
        if result["fixed_imports"]:
            logger.info(f"✅ 修復了 {len(result['fixed_imports'])} 個導入")
        
        return result
    
    def _check_python_imports(self, file_path: Path, result: Dict):
        """檢查單個 Python 文件的導入"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self._validate_import(alias.name, file_path, result)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self._validate_import(node.module, file_path, result)
        
        except SyntaxError as e:
            self.issues.append(f"語法錯誤在 {file_path}: {e}")
            result["valid"] = False
    
    def _validate_import(self, module_name: str, file_path: Path, result: Dict):
        """驗證單個導入"""
        # 檢查是否是舊的路徑
        for old_path, new_path in self.path_mappings.items():
            if module_name.startswith(old_path.replace('/', '.')):
                # 發現舊路徑導入
                broken_import = f"{file_path}: {module_name}"
                result["broken_imports"].append(broken_import)
                result["valid"] = False
                
                # 嘗試修復
                if self.fix_imports:
                    new_module = module_name.replace(old_path.replace('/', '.'), new_path.replace('/', '.'))
                    self._fix_import_in_file(file_path, module_name, new_module)
                    result["fixed_imports"].append(f"{file_path}: {module_name} -> {new_module}")
    
    def _fix_import_in_file(self, file_path: Path, old_import: str, new_import: str):
        """修復文件中的導入"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替換導入語句
            content = content.replace(old_import, new_import)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            logger.error(f"❌ 無法修復導入在 {file_path}: {e}")
    
    def validate_config_files(self) -> Dict:
        """驗證配置文件"""
        logger.info("⚙️ 驗證配置文件...")
        
        result = {
            "valid": True,
            "invalid_configs": [],
            "missing_configs": []
        }
        
        # 檢查關鍵配置文件
        config_checks = [
            {
                "path": "config/governance/system-manifest.yaml",
                "required_keys": ["name", "version", "modules"]
            },
            {
                "path": "config/governance/system-module-map.yaml",
                "required_keys": ["modules", "dependencies"]
            },
            {
                "path": "package.json",
                "required_keys": ["name", "version", "scripts"]
            }
        ]
        
        for check in config_checks:
            config_path = self.project_root / check["path"]
            
            if not config_path.exists():
                result["missing_configs"].append(check["path"])
                result["valid"] = False
                continue
            
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    if config_path.suffix in ['.yaml', '.yml']:
                        config = yaml.safe_load(f)
                    elif config_path.suffix == '.json':
                        config = json.load(f)
                    else:
                        continue
                
                for key in check["required_keys"]:
                    if key not in config:
                        result["invalid_configs"].append(f"{check['path']}: 缺少鍵 '{key}'")
                        result["valid"] = False
                        
            except Exception as e:
                result["invalid_configs"].append(f"{check['path']}: 解析錯誤 - {e}")
                result["valid"] = False
        
        return result
    
    def validate_web_structure(self) -> Dict:
        """驗證 Web 應用結構"""
        logger.info("🌐 驗證 Web 應用結構...")
        
        result = {
            "valid": True,
            "missing_components": [],
            "structure_issues": []
        }
        
        # 檢查 Web 應用結構
        web_apps = ["admin", "client"]
        
        for app in web_apps:
            app_path = self.project_root / "src" / "web" / app
            
            if not app_path.exists():
                result["missing_components"].append(f"src/web/{app}")
                result["valid"] = False
                continue
            
            # 檢查關鍵文件
            key_files = ["package.json", "src/App.tsx", "src/main.tsx"]
            for file_name in key_files:
                file_path = app_path / file_name
                if not file_path.exists():
                    result["missing_components"].append(f"src/web/{app}/{file_name}")
                    result["valid"] = False
        
        return result
    
    def generate_validation_report(self) -> str:
        """生成驗證報告"""
        logger.info("📊 生成驗證報告...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "validation_results": {
                "directory_structure": self.validate_directory_structure(),
                "file_integrity": self.validate_file_integrity(),
                "import_paths": self.validate_import_paths(),
                "config_files": self.validate_config_files(),
                "web_structure": self.validate_web_structure()
            },
            "issues": self.issues,
            "warnings": self.warnings,
            "summary": {}
        }
        
        # 生成摘要
        total_issues = len(self.issues) + len(self.warnings)
        report["summary"] = {
            "total_issues": total_issues,
            "critical_issues": len(self.issues),
            "warnings": len(self.warnings),
            "overall_valid": all(
                result["valid"] 
                for result in report["validation_results"].values()
            )
        }
        
        # 保存報告
        report_file = self.project_root / "validation_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📋 驗證報告已保存到: {report_file}")
        
        # 生成摘要
        summary = self._generate_validation_summary(report)
        logger.info(f"\n📋 驗證摘要:\n{summary}")
        
        return summary
    
    def _generate_validation_summary(self, report: Dict) -> str:
        """生成驗證摘要"""
        summary = []
        summary.append(f"驗證時間: {report['timestamp']}")
        summary.append(f"項目根目錄: {report['project_root']}")
        summary.append(f"總問題數: {report['summary']['total_issues']}")
        summary.append(f"嚴重問題: {report['summary']['critical_issues']}")
        summary.append(f"警告: {report['summary']['warnings']}")
        summary.append(f"整體狀態: {'✅ 通過' if report['summary']['overall_valid'] else '❌ 失敗'}")
        
        if report["issues"]:
            summary.append("\n嚴重問題:")
            for issue in report["issues"][:10]:  # 只顯示前10個
                summary.append(f"  - {issue}")
        
        if report["warnings"]:
            summary.append("\n警告:")
            for warning in report["warnings"][:10]:  # 只顯示前10個
                summary.append(f"  - {warning}")
        
        return "\n".join(summary)
    
    def run_validation(self, detailed: bool = False, fix_imports: bool = False) -> bool:
        """運行完整驗證"""
        self.detailed = detailed
        self.fix_imports = fix_imports
        
        logger.info("🔍 開始目錄重構驗證...")
        
        try:
            # 執行所有驗證
            self.generate_validation_report()
            
            # 判斷整體結果
            total_issues = len(self.issues) + len(self.warnings)
            
            if total_issues == 0:
                logger.info("✅ 驗證通過 - 沒有發現問題!")
                return True
            elif len(self.issues) == 0:
                logger.info(f"⚠️ 驗證通過但有 {len(self.warnings)} 個警告")
                return True
            else:
                logger.error(f"❌ 驗證失敗 - 發現 {len(self.issues)} 個嚴重問題")
                return False
                
        except Exception as e:
            logger.error(f"❌ 驗證過程中發生錯誤: {e}")
            return False

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="MachineNativeOps 目錄重構驗證工具")
    parser.add_argument("--detailed", action="store_true", help="詳細輸出模式")
    parser.add_argument("--fix-imports", action="store_true", help="自動修復導入路徑")
    parser.add_argument("--project-root", default=".", help="項目根目錄路徑")
    
    args = parser.parse_args()
    
    # 創建驗證器
    validator = RestructureValidator(args.project_root)
    
    # 執行驗證
    success = validator.run_validation(args.detailed, args.fix_imports)
    
    # 退出
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
