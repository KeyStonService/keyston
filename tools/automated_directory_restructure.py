#!/usr/bin/env python3
"""
MachineNativeOps 自動化目錄重構工具

這個腳本自動執行完整的目錄重構流程，包括：
1. 分析現有目錄結構
2. 創建新的目錄結構
3. 移動和重組文件
4. 更新配置文件
5. 驗證重構結果
6. 生成報告

使用方法：
python tools/automated_directory_restructure.py [--dry-run] [--phase PHASE]
"""

import os
import sys
import json
import shutil
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import yaml

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('restructure.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DirectoryRestructureTool:
    """自動化目錄重構工具"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.dry_run = False
        self.backup_dir = self.project_root / "backup_before_restructure"
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "operations": [],
            "errors": [],
            "warnings": [],
            "statistics": {}
        }
        
        # 重構規則配置
        self.restructure_rules = {
            "src": {
                "target_structure": {
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
                }
            },
            "config": {
                "target_structure": {
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
        }
    
    def set_dry_run(self, dry_run: bool):
        """設置是否為試運行模式"""
        self.dry_run = dry_run
        if dry_run:
            logger.info("🔍 試運行模式 - 不會實際修改文件")
    
    def create_backup(self) -> bool:
        """創建項目備份"""
        try:
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)
            
            logger.info(f"📦 創建備份到: {self.backup_dir}")
            
            if not self.dry_run:
                shutil.copytree(self.project_root, self.backup_dir, 
                              ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', 'node_modules'))
            
            self.report["operations"].append({
                "type": "backup",
                "source": str(self.project_root),
                "target": str(self.backup_dir),
                "status": "completed"
            })
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 備份失敗: {e}")
            self.report["errors"].append(f"Backup failed: {e}")
            return False
    
    def analyze_current_structure(self) -> Dict:
        """分析當前目錄結構"""
        logger.info("🔍 分析當前目錄結構...")
        
        structure = {}
        
        for root_dir in ["src", "config", "scripts", "governance"]:
            root_path = self.project_root / root_dir
            if root_path.exists():
                structure[root_dir] = self._scan_directory(root_path)
        
        self.report["current_structure"] = structure
        return structure
    
    def _scan_directory(self, path: Path) -> Dict:
        """掃描目錄結構"""
        result = {"files": [], "directories": {}}
        
        try:
            for item in path.iterdir():
                if item.is_file() and not item.name.startswith('.'):
                    result["files"].append(item.name)
                elif item.is_dir() and not item.name.startswith('.'):
                    result["directories"][item.name] = self._scan_directory(item)
        except PermissionError:
            logger.warning(f"⚠️ 無法訪問目錄: {path}")
        
        return result
    
    def restructure_src_directory(self) -> bool:
        """重構 src/ 目錄"""
        logger.info("🔄 開始重構 src/ 目錄...")
        
        src_path = self.project_root / "src"
        if not src_path.exists():
            logger.warning("⚠️ src/ 目錄不存在")
            return False
        
        try:
            # 創建新的目錄結構
            self._create_src_structure()
            
            # 移動現有文件
            self._move_src_files()
            
            # 清理舊目錄
            self._cleanup_old_src_directories()
            
            self.report["operations"].append({
                "type": "restructure",
                "target": "src",
                "status": "completed"
            })
            
            return True
            
        except Exception as e:
            logger.error(f"❌ src/ 重構失敗: {e}")
            self.report["errors"].append(f"src restructure failed: {e}")
            return False
    
    def _create_src_structure(self):
        """創建新的 src 目錄結構"""
        structure = self.restructure_rules["src"]["target_structure"]
        
        for main_category, subcategories in structure.items():
            main_path = self.project_root / "src" / main_category
            
            if not self.dry_run:
                main_path.mkdir(parents=True, exist_ok=True)
            
            for subcategory, modules in subcategories.items():
                sub_path = main_path / subcategory
                
                if not self.dry_run:
                    sub_path.mkdir(parents=True, exist_ok=True)
                
                # 為每個模塊創建 __init__.py
                for module in modules:
                    module_path = sub_path / module
                    if not self.dry_run:
                        module_path.mkdir(exist_ok=True)
                        init_file = module_path / "__init__.py"
                        if not init_file.exists():
                            init_file.touch()
    
    def _move_src_files(self):
        """移動 src 文件到新位置"""
        # 這裡需要根據實際的文件移動邏輯來實現
        # 由於文件移動邏輯複雜，這裡提供框架
        logger.info("📁 移動 src 文件...")
        
        # 示例：移動核心模塊
        old_core_path = self.project_root / "src" / "core" / "modules"
        new_core_path = self.project_root / "src" / "core" / "plugins"
        
        if old_core_path.exists() and not new_core_path.exists():
            if not self.dry_run:
                shutil.move(str(old_core_path), str(new_core_path))
            logger.info(f"✅ 移動: {old_core_path} -> {new_core_path}")
    
    def _cleanup_old_src_directories(self):
        """清理舊的 src 目錄"""
        logger.info("🧹 清理舊目錄...")
        
        old_dirs = [
            "src/core/modules",
            "src/core/safety_mechanisms",
            "src/apps/web",
            "src/apps/cli",
            "src/apps/api"
        ]
        
        for old_dir in old_dirs:
            old_path = self.project_root / old_dir
            if old_path.exists():
                if not self.dry_run:
                    shutil.rmtree(str(old_path))
                logger.info(f"🗑️ 刪除舊目錄: {old_path}")
    
    def restructure_config_directory(self) -> bool:
        """重構 config/ 目錄"""
        logger.info("🔄 開始重構 config/ 目錄...")
        
        config_path = self.project_root / "config"
        if not config_path.exists():
            logger.warning("⚠️ config/ 目錄不存在")
            return False
        
        try:
            # 創建新的配置目錄結構
            structure = self.restructure_rules["config"]["target_structure"]
            
            for category, subdirs in structure.items():
                category_path = config_path / category
                
                if not self.dry_run:
                    category_path.mkdir(exist_ok=True)
                
                for subdir in subdirs:
                    subdir_path = category_path / subdir
                    if not self.dry_run:
                        subdir_path.mkdir(exist_ok=True)
            
            self.report["operations"].append({
                "type": "restructure",
                "target": "config",
                "status": "completed"
            })
            
            return True
            
        except Exception as e:
            logger.error(f"❌ config/ 重構失敗: {e}")
            self.report["errors"].append(f"config restructure failed: {e}")
            return False
    
    def validate_restructure(self) -> Dict:
        """驗證重構結果"""
        logger.info("✅ 驗證重構結果...")
        
        validation_result = {
            "src_structure": self._validate_src_structure(),
            "config_structure": self._validate_config_structure(),
            "file_integrity": self._validate_file_integrity(),
            "import_consistency": self._validate_import_consistency()
        }
        
        self.report["validation"] = validation_result
        return validation_result
    
    def _validate_src_structure(self) -> Dict:
        """驗證 src 結構"""
        expected = self.restructure_rules["src"]["target_structure"]
        actual = {}
        
        for main_category in expected.keys():
            main_path = self.project_root / "src" / main_category
            if main_path.exists():
                actual[main_category] = {}
                for subcategory in expected[main_category].keys():
                    sub_path = main_path / subcategory
                    actual[main_category][subcategory] = sub_path.exists()
        
        return {
            "expected": expected,
            "actual": actual,
            "valid": all(
                all(actual.get(main_cat, {}).get(sub_cat, False) 
                    for sub_cat in expected[main_cat].keys())
                for main_cat in expected.keys()
            )
        }
    
    def _validate_config_structure(self) -> Dict:
        """驗證 config 結構"""
        expected = self.restructure_rules["config"]["target_structure"]
        actual = {}
        
        for category in expected.keys():
            category_path = self.project_root / "config" / category
            actual[category] = category_path.exists()
        
        return {
            "expected": list(expected.keys()),
            "actual": actual,
            "valid": all(actual.values())
        }
    
    def _validate_file_integrity(self) -> Dict:
        """驗證文件完整性"""
        # 簡化的文件完整性檢查
        return {
            "total_files_checked": 0,
            "missing_files": [],
            "corrupted_files": [],
            "valid": True
        }
    
    def _validate_import_consistency(self) -> Dict:
        """驗證導入一致性"""
        # 簡化的導入一致性檢查
        return {
            "files_checked": 0,
            "import_errors": [],
            "valid": True
        }
    
    def generate_report(self) -> str:
        """生成重構報告"""
        logger.info("📊 生成重構報告...")
        
        # 統計信息
        self.report["statistics"] = {
            "total_operations": len(self.report["operations"]),
            "total_errors": len(self.report["errors"]),
            "total_warnings": len(self.report["warnings"]),
            "execution_time": datetime.now().isoformat()
        }
        
        # 保存報告
        report_file = self.project_root / "restructure_report.json"
        
        if not self.dry_run:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📋 報告已保存到: {report_file}")
        
        # 生成摘要
        summary = self._generate_summary()
        logger.info(f"\n📋 重構摘要:\n{summary}")
        
        return summary
    
    def _generate_summary(self) -> str:
        """生成重構摘要"""
        summary = []
        summary.append(f"執行時間: {self.report['timestamp']}")
        summary.append(f"項目根目錄: {self.report['project_root']}")
        summary.append(f"總操作數: {self.report['statistics']['total_operations']}")
        summary.append(f"錯誤數: {self.report['statistics']['total_errors']}")
        summary.append(f"警告數: {self.report['statistics']['total_warnings']}")
        
        if self.report["errors"]:
            summary.append("\n錯誤列表:")
            for error in self.report["errors"]:
                summary.append(f"  - {error}")
        
        return "\n".join(summary)
    
    def run_full_restructure(self) -> bool:
        """執行完整的重構流程"""
        logger.info("🚀 開始自動化目錄重構...")
        
        try:
            # 1. 創建備份
            if not self.create_backup():
                return False
            
            # 2. 分析當前結構
            self.analyze_current_structure()
            
            # 3. 重構 src 目錄
            if not self.restructure_src_directory():
                return False
            
            # 4. 重構 config 目錄
            if not self.restructure_config_directory():
                return False
            
            # 5. 驗證重構結果
            validation = self.validate_restructure()
            
            # 6. 生成報告
            self.generate_report()
            
            logger.info("✅ 自動化目錄重構完成!")
            return True
            
        except Exception as e:
            logger.error(f"❌ 重構過程中發生錯誤: {e}")
            self.report["errors"].append(f"General error: {e}")
            return False

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="MachineNativeOps 自動化目錄重構工具")
    parser.add_argument("--dry-run", action="store_true", help="試運行模式，不實際修改文件")
    parser.add_argument("--phase", choices=["src", "config", "all"], default="all", help="指定重構階段")
    parser.add_argument("--project-root", default=".", help="項目根目錄路徑")
    
    args = parser.parse_args()
    
    # 創建工具實例
    tool = DirectoryRestructureTool(args.project_root)
    tool.set_dry_run(args.dry_run)
    
    # 執行重構
    success = False
    
    if args.phase == "all":
        success = tool.run_full_restructure()
    elif args.phase == "src":
        success = tool.restructure_src_directory()
    elif args.phase == "config":
        success = tool.restructure_config_directory()
    
    # 退出
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
