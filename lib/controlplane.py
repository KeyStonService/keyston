#!/usr/bin/env python3
"""
Controlplane 配置讀取庫
提供簡單的 API 讓其他 Python 腳本使用 controlplane 配置
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from functools import lru_cache

class ControlplaneConfig:
    """Controlplane 配置管理器"""
    
    def __init__(self, repo_root: Optional[Path] = None):
        """
        初始化配置管理器
        
        Args:
            repo_root: 儲存庫根目錄，如果為 None 則自動檢測
        """
        self.repo_root = repo_root or self._find_repo_root()
        self.baseline_path = self.repo_root / "controlplane" / "baseline"
        self.overlay_path = self.repo_root / "controlplane" / "overlay"
        self.active_path = self.repo_root / "controlplane" / "active"
        
        # 確保路徑存在
        if not self.baseline_path.exists():
            raise FileNotFoundError(f"Baseline path not found: {self.baseline_path}")
    
    @staticmethod
    def _find_repo_root() -> Path:
        """自動檢測儲存庫根目錄"""
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        return Path.cwd()
    
    @lru_cache(maxsize=128)
    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """載入並緩存 YAML 文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            raise RuntimeError(f"Failed to load {file_path}: {e}")
    
    def get_baseline_config(self, config_name: str) -> Dict[str, Any]:
        """
        獲取 baseline 配置
        
        Args:
            config_name: 配置文件名 (例如: "root.config.yaml")
        
        Returns:
            配置字典
        """
        config_file = self.baseline_path / "config" / config_name
        return self._load_yaml(config_file)
    
    def get_specification(self, spec_name: str) -> Dict[str, Any]:
        """
        獲取規範文件
        
        Args:
            spec_name: 規範文件名 (例如: "root.specs.naming.yaml")
        
        Returns:
            規範字典
        """
        spec_file = self.baseline_path / "specifications" / spec_name
        return self._load_yaml(spec_file)
    
    def get_registry(self, registry_name: str) -> Dict[str, Any]:
        """
        獲取註冊表
        
        Args:
            registry_name: 註冊表文件名 (例如: "root.registry.modules.yaml")
        
        Returns:
            註冊表字典
        """
        registry_file = self.baseline_path / "registries" / registry_name
        return self._load_yaml(registry_file)
    
    def get_modules(self) -> List[Dict[str, Any]]:
        """獲取所有模組列表"""
        registry = self.get_registry("root.registry.modules.yaml")
        return registry.get('modules', [])
    
    def get_namespaces(self) -> List[Dict[str, Any]]:
        """獲取所有命名空間列表"""
        registry = self.get_registry("root.registry.namespaces.yaml")
        return registry.get('namespaces', [])
    
    def get_devices(self) -> List[Dict[str, Any]]:
        """獲取所有設備列表"""
        registry = self.get_registry("root.registry.devices.yaml")
        return registry.get('devices', [])
    
    def get_naming_rules(self) -> Dict[str, Any]:
        """獲取命名規則"""
        return self.get_baseline_config("root.naming-policy.yaml")
    
    def get_governance_policy(self) -> Dict[str, Any]:
        """獲取治理策略"""
        return self.get_baseline_config("root.governance.yaml")
    
    def get_trust_policy(self) -> Dict[str, Any]:
        """獲取信任策略"""
        return self.get_baseline_config("root.trust.yaml")
    
    def get_integrity_policy(self) -> Dict[str, Any]:
        """獲取完整性策略"""
        return self.get_baseline_config("root.integrity.yaml")
    
    def validate_name(self, name: str, name_type: str = "file") -> tuple[bool, Optional[str]]:
        """
        驗證名稱是否符合命名規範
        
        Args:
            name: 要驗證的名稱
            name_type: 名稱類型 (file, directory, module, namespace)
        
        Returns:
            (是否有效, 錯誤訊息)
        """
        import re
        
        naming_rules = self.get_naming_rules()
        
        # 根據類型獲取規則
        if name_type == "file":
            # 特殊處理：允許 root.*.yaml 格式的文件
            if name.startswith("root.") and name.count('.') == 2:
                parts = name.split('.')
                if len(parts) == 3 and parts[2] in ['yaml', 'yml', 'map', 'sh']:
                    return True, None
            
            pattern = r'^[a-z][a-z0-9-]*(\.[a-z0-9]+)*$'
            if not re.match(pattern, name):
                return False, f"File name must be kebab-case: {name}"
            
            # 檢查雙重擴展名
            if name.count('.') > 1:
                parts = name.split('.')
                if len(parts) > 2:
                    return False, f"File has double extension: {name}"
        
        elif name_type == "directory":
            pattern = r'^[a-z][a-z0-9-]*$'
            if not re.match(pattern, name):
                return False, f"Directory name must be kebab-case: {name}"
        
        elif name_type == "namespace":
            pattern = r'^[a-z][a-z0-9-]*$'
            if not re.match(pattern, name):
                return False, f"Namespace must be kebab-case without dots: {name}"
            
            if '.' in name:
                return False, f"Namespace contains dots (use hyphens): {name}"
        
        return True, None
    
    def get_config_value(self, key_path: str, default: Any = None) -> Any:
        """
        使用點號路徑獲取配置值
        
        Args:
            key_path: 配置鍵路徑 (例如: "metadata.version")
            default: 默認值
        
        Returns:
            配置值
        """
        config = self.get_baseline_config("root.config.yaml")
        
        keys = key_path.split('.')
        value = config
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def get_workspace_mappings(self) -> Dict[str, Any]:
        """獲取工作空間映射"""
        return self.get_baseline_config("workspace.map.yaml")
    
    def get_gates_config(self) -> Dict[str, Any]:
        """獲取門控配置"""
        return self.get_baseline_config("gates.map.yaml")
    
    def is_baseline_immutable(self) -> bool:
        """檢查 baseline 是否為不可變"""
        config = self.get_baseline_config("root.config.yaml")
        metadata = config.get('metadata', {})
        annotations = metadata.get('annotations', {})
        return annotations.get('machinenativeops.io/immutable', 'false') == 'true'
    
    def get_validation_vectors(self) -> Dict[str, Any]:
        """獲取驗證向量"""
        vectors_file = self.baseline_path / "validation" / "vectors" / "root.validation.vectors.yaml"
        return self._load_yaml(vectors_file)
    
    def create_overlay_extension(self, name: str, extends: str, config: Dict[str, Any]) -> Path:
        """
        創建 overlay 擴展
        
        Args:
            name: 擴展名稱
            extends: 擴展的 baseline 配置
            config: 配置內容
        
        Returns:
            創建的文件路徑
        """
        overlay_config_dir = self.overlay_path / "config"
        overlay_config_dir.mkdir(parents=True, exist_ok=True)
        
        extension_data = {
            'metadata': {
                'name': name,
                'type': 'overlay',
                'extends': extends
            },
            'configuration': config
        }
        
        output_file = overlay_config_dir / f"{name}.yaml"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(extension_data, f, default_flow_style=False, allow_unicode=True)
        
        return output_file
    
    def synthesize_active(self):
        """合成 active 視圖"""
        # 創建 active 目錄
        self.active_path.mkdir(parents=True, exist_ok=True)
        
        # 合併 baseline 和 overlay 配置
        baseline_config_dir = self.baseline_path / "config"
        if baseline_config_dir.exists():
            baseline_configs = list(baseline_config_dir.glob("*.yaml"))
            
            for baseline_file in baseline_configs:
                baseline_data = self._load_yaml(baseline_file)
                
                # 檢查是否有對應的 overlay
                overlay_file = self.overlay_path / "config" / baseline_file.name
                if overlay_file.exists():
                    overlay_data = self._load_yaml(overlay_file)
                    # 簡單合併
                    merged_data = {**baseline_data, **overlay_data}
                else:
                    merged_data = baseline_data
                
                # 保存到 active
                active_file = self.active_path / baseline_file.name
                with open(active_file, 'w', encoding='utf-8') as f:
                    yaml.dump(merged_data, f, default_flow_style=False, allow_unicode=True)

# 全局單例實例
_global_config: Optional[ControlplaneConfig] = None

def get_config() -> ControlplaneConfig:
    """獲取全局配置實例"""
    global _global_config
    if _global_config is None:
        _global_config = ControlplaneConfig()
    return _global_config

# 便捷函數
def get_modules() -> List[Dict[str, Any]]:
    """快速獲取模組列表"""
    return get_config().get_modules()

def get_namespaces() -> List[Dict[str, Any]]:
    """快速獲取命名空間列表"""
    return get_config().get_namespaces()

def validate_name(name: str, name_type: str = "file") -> tuple[bool, Optional[str]]:
    """快速驗證名稱"""
    return get_config().validate_name(name, name_type)

def get_naming_rules() -> Dict[str, Any]:
    """快速獲取命名規則"""
    return get_config().get_naming_rules()

# 使用示例
if __name__ == "__main__":
    # 示例用法
    config = ControlplaneConfig()
    
    print("📋 Controlplane 配置庫測試")
    print("=" * 60)
    
    # 測試獲取配置
    print("\n1. 獲取 root 配置:")
    root_config = config.get_baseline_config("root.config.yaml")
    print(f"   名稱: {root_config.get('metadata', {}).get('name')}")
    print(f"   命名空間: {root_config.get('metadata', {}).get('namespace')}")
    
    # 測試獲取模組
    print("\n2. 獲取模組列表:")
    modules = config.get_modules()
    print(f"   模組數量: {len(modules)}")
    
    # 測試命名驗證
    print("\n3. 測試命名驗證:")
    test_names = [
        ("my-file.yaml", "file"),
        ("MyFile.yaml", "file"),
        ("my-directory", "directory"),
        ("my.namespace", "namespace"),
        ("my-namespace", "namespace")
    ]
    
    for name, name_type in test_names:
        is_valid, error = config.validate_name(name, name_type)
        status = "✅" if is_valid else "❌"
        print(f"   {status} {name} ({name_type}): {error or 'Valid'}")
    
    # 測試配置值獲取
    print("\n4. 獲取配置值:")
    version = config.get_config_value("metadata.annotations.machinenativeops.io/version")
    print(f"   版本: {version}")
    
    print("\n✅ 測試完成")