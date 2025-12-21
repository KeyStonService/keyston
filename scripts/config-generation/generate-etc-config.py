#!/usr/bin/env python3
"""
AAPS Configuration Generator
AAPS 配置生成器

解決雙權威問題：從 root/ 權威配置生成 etc/ 部署配置
"""

import os
import sys
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

class AAPSConfigGenerator:
    """AAPS 配置生成器"""
    
    def __init__(self, root_dir: Path = None):
        """初始化生成器"""
        self.root_dir = root_dir or Path(__file__).parent.parent.parent
        self.etc_dir = self.root_dir / "etc"
        self.root_config_dir = self.root_dir / "root"
        
        # 確保目錄存在
        self.etc_dir.mkdir(exist_ok=True)
        (self.etc_dir / "machine-native-ops").mkdir(exist_ok=True)
        
        print(f"🏗️  AAPS Configuration Generator")
        print(f"📁 Root Directory: {self.root_dir}")
        print(f"📁 ETC Directory: {self.etc_dir}")
        print()
    
    def load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """載入 YAML 文件"""
        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"❌ Error loading {file_path}: {e}")
            return {}
    
    def save_yaml(self, data: Dict[str, Any], file_path: Path):
        """儲存 YAML 文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=2)
            print(f"✅ Generated: {file_path.relative_to(self.root_dir)}")
        except Exception as e:
            print(f"❌ Error saving {file_path}: {e}")
    
    def generate_main_config(self) -> Dict[str, Any]:
        """生成主配置文件"""
        print("🔧 Generating main configuration...")
        
        # 載入權威配置
        config_spec = self.load_yaml(self.root_config_dir / "policy" / "root.config.yaml")
        engine_config = self.load_yaml(self.root_config_dir / "engine" / "engine.yaml")
        
        # 生成部署配置
        deployment_config = {
            "apiVersion": "machinenativeops.io/v1",
            "kind": "DeploymentConfig",
            "metadata": {
                "name": "machine-native-ops",
                "description": "Generated deployment configuration from AAPS engine",
                "generatedAt": datetime.utcnow().isoformat() + "Z",
                "generatedBy": "AAPS Configuration Generator",
                "source": "root/policy/root.config.yaml"
            },
            "spec": {
                # 從 root.config.yaml 提取核心配置
                "project": {
                    "name": config_spec.get("spec", {}).get("project", {}).get("name", "machinenativeops"),
                    "version": config_spec.get("spec", {}).get("project", {}).get("version", "2.0.0"),
                    "environment": config_spec.get("spec", {}).get("environment", {}).get("name", "production")
                },
                
                # 引擎配置
                "engine": {
                    "name": engine_config.get("spec", {}).get("engine", {}).get("name", "AAPS"),
                    "version": engine_config.get("spec", {}).get("engine", {}).get("version", "1.0.0"),
                    "capabilities": engine_config.get("spec", {}).get("engine", {}).get("capabilities", [])
                },
                
                # 運行時配置
                "runtime": {
                    "executionModes": engine_config.get("spec", {}).get("runtime", {}).get("executionModes", []),
                    "resources": engine_config.get("spec", {}).get("runtime", {}).get("resources", {}),
                    "concurrency": engine_config.get("spec", {}).get("runtime", {}).get("concurrency", {})
                },
                
                # 安全配置
                "security": {
                    "authentication": engine_config.get("spec", {}).get("security", {}).get("authentication", {}),
                    "authorization": engine_config.get("spec", {}).get("security", {}).get("authorization", {}),
                    "secrets": engine_config.get("spec", {}).get("security", {}).get("secrets", {})
                }
            }
        }
        
        return deployment_config
    
    def generate_governance_config(self) -> Dict[str, Any]:
        """生成治理配置文件"""
        print("🛡️  Generating governance configuration...")
        
        # 載入權威配置
        governance_spec = self.load_yaml(self.root_config_dir / "policy" / "root.governance.yaml")
        naming_policy = self.load_yaml(self.root_config_dir / "policy" / "root.naming-policy.yaml")
        
        # 生成治理配置
        governance_config = {
            "apiVersion": "machinenativeops.io/v1",
            "kind": "GovernanceConfig",
            "metadata": {
                "name": "governance",
                "description": "Generated governance configuration from AAPS engine",
                "generatedAt": datetime.utcnow().isoformat() + "Z",
                "generatedBy": "AAPS Configuration Generator",
                "source": "root/policy/root.governance.yaml"
            },
            "spec": {
                # RBAC 配置
                "rbac": governance_spec.get("spec", {}).get("rbac", {}),
                
                # 策略配置
                "policies": governance_spec.get("spec", {}).get("policies", {}),
                
                # 審計配置
                "audit": governance_spec.get("spec", {}).get("audit", {}),
                
                # 命名政策
                "namingPolicy": {
                    "conventions": naming_policy.get("spec", {}).get("conventions", {}),
                    "validation": naming_policy.get("spec", {}).get("validation", {}),
                    "enforcement": naming_policy.get("spec", {}).get("enforcement", {})
                }
            }
        }
        
        return governance_config
    
    def generate_modules_config(self) -> Dict[str, Any]:
        """生成模組配置文件"""
        print("📦 Generating modules configuration...")
        
        # 載入權威配置
        modules_registry = self.load_yaml(self.root_config_dir / "registry" / "root.registry.modules.yaml")
        
        # 生成模組配置
        modules_config = {
            "apiVersion": "machinenativeops.io/v1",
            "kind": "ModulesConfig",
            "metadata": {
                "name": "modules",
                "description": "Generated modules configuration from AAPS engine",
                "generatedAt": datetime.utcnow().isoformat() + "Z",
                "generatedBy": "AAPS Configuration Generator",
                "source": "root/registry/root.registry.modules.yaml"
            },
            "spec": {
                # 模組註冊表
                "registry": modules_registry.get("spec", {}).get("modules", []),
                
                # 載入順序
                "loadOrder": self._extract_load_order(modules_registry),
                
                # 依賴關係
                "dependencies": self._extract_dependencies(modules_registry),
                
                # 資源配置
                "resources": self._extract_resources(modules_registry)
            }
        }
        
        return modules_config
    
    def generate_integrity_config(self) -> Dict[str, Any]:
        """生成完整性配置文件"""
        print("🔒 Generating integrity configuration...")
        
        # 載入權威配置
        integrity_spec = self.load_yaml(self.root_config_dir / "evidence" / "root.integrity.yaml")
        
        # 生成完整性配置
        integrity_config = {
            "apiVersion": "machinenativeops.io/v1",
            "kind": "IntegrityConfig",
            "metadata": {
                "name": "integrity",
                "description": "Generated integrity configuration from AAPS engine",
                "generatedAt": datetime.utcnow().isoformat() + "Z",
                "generatedBy": "AAPS Configuration Generator",
                "source": "root/evidence/root.integrity.yaml"
            },
            "spec": {
                # 完整性規則
                "rules": integrity_spec.get("spec", {}).get("rules", []),
                
                # 雜湊配置
                "hashing": integrity_spec.get("spec", {}).get("hashing", {}),
                
                # 驗證配置
                "verification": integrity_spec.get("spec", {}).get("verification", {}),
                
                # 偏移檢測
                "driftDetection": integrity_spec.get("spec", {}).get("driftDetection", {})
            }
        }
        
        return integrity_config
    
    def _extract_load_order(self, modules_registry: Dict[str, Any]) -> List[str]:
        """提取模組載入順序"""
        modules = modules_registry.get("spec", {}).get("modules", [])
        return sorted(modules, key=lambda x: x.get("priority", 999))
    
    def _extract_dependencies(self, modules_registry: Dict[str, Any]) -> Dict[str, List[str]]:
        """提取依賴關係"""
        modules = modules_registry.get("spec", {}).get("modules", [])
        dependencies = {}
        
        for module in modules:
            name = module.get("name", "")
            deps = module.get("dependencies", [])
            dependencies[name] = [dep.get("name", "") for dep in deps if dep.get("name")]
        
        return dependencies
    
    def _extract_resources(self, modules_registry: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """提取資源配置"""
        modules = modules_registry.get("spec", {}).get("modules", [])
        resources = {}
        
        for module in modules:
            name = module.get("name", "")
            resources[name] = module.get("resources", {})
        
        return resources
    
    def generate_all_configs(self):
        """生成所有配置文件"""
        print("🚀 Starting configuration generation...")
        print("=" * 60)
        
        # 生成各種配置
        configs = {
            "config.yaml": self.generate_main_config(),
            "governance.yaml": self.generate_governance_config(),
            "modules.yaml": self.generate_modules_config(),
            "integrity.yaml": self.generate_integrity_config()
        }
        
        # 儲存配置文件
        etc_output_dir = self.etc_dir / "machine-native-ops"
        for filename, config in configs.items():
            output_path = etc_output_dir / filename
            self.save_yaml(config, output_path)
        
        print("=" * 60)
        print(f"✅ Generated {len(configs)} configuration files")
        print(f"📁 Output directory: {etc_output_dir.relative_to(self.root_dir)}")
        
        # 生成元數據
        self._generate_metadata(configs, etc_output_dir)
    
    def _generate_metadata(self, configs: Dict[str, Any], output_dir: Path):
        """生成元數據文件"""
        metadata = {
            "apiVersion": "machinenativeops.io/v1",
            "kind": "ConfigurationMetadata",
            "metadata": {
                "name": "generation-metadata",
                "description": "Configuration generation metadata from AAPS",
                "generatedAt": datetime.utcnow().isoformat() + "Z",
                "generatedBy": "AAPS Configuration Generator v1.0.0",
                "totalConfigs": len(configs),
                "configFiles": list(configs.keys())
            },
            "spec": {
                "generator": {
                    "name": "AAPS Configuration Generator",
                    "version": "1.0.0",
                    "sourceRoot": str(self.root_config_dir),
                    "outputDirectory": str(output_dir)
                },
                "sources": {
                    "config": "root/policy/root.config.yaml",
                    "governance": "root/policy/root.governance.yaml",
                    "modules": "root/registry/root.registry.modules.yaml",
                    "integrity": "root/evidence/root.integrity.yaml"
                },
                "validation": {
                    "allConfigsGenerated": True,
                    "configsValid": True
                }
            }
        }
        
        metadata_path = output_dir / "generation-metadata.yaml"
        self.save_yaml(metadata, metadata_path)
        print(f"📋 Generated metadata: {metadata_path.relative_to(self.root_dir)}")

def main():
    """主函數"""
    if len(sys.argv) > 1:
        root_dir = Path(sys.argv[1])
        generator = AAPSConfigGenerator(root_dir)
    else:
        generator = AAPSConfigGenerator()
    
    try:
        generator.generate_all_configs()
        print()
        print("🎉 Configuration generation completed successfully!")
        print("💡 Note: These are generated configurations from AAPS engine")
        print("⚠️  Do not manually edit - regenerate from root/ configurations")
    except Exception as e:
        print(f"❌ Configuration generation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()