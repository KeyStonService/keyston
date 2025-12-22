#!/usr/bin/env python3
"""
MachineNativeOps Namespace Validator
驗證所有配置文件是否符合 MachineNativeOps 命名空間標準
"""

import os
import sys
import yaml
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass, field

@dataclass
class ValidationResult:
    """驗證結果"""
    total_files: int = 0
    valid_files: int = 0
    invalid_files: int = 0
    errors: List[Tuple[str, str]] = field(default_factory=list)  # (file, error_message)
    warnings: List[Tuple[str, str]] = field(default_factory=list)  # (file, warning_message)

class NamespaceValidator:
    """命名空間驗證器"""
    
    # 標準規範
    REQUIRED_API_VERSION = "machinenativeops.io/v2"
    REQUIRED_KIND = "MachineNativeOpsGlobalBaseline"
    REQUIRED_NAMESPACE = "machinenativeops"
    REQUIRED_URN_PREFIX = "urn:machinenativeops:"
    REQUIRED_LABEL_PREFIX = "machinenativeops.io/"
    
    # 禁止的舊字串模式（用於檢測但不顯示）
    FORBIDDEN_PATTERNS = [
        # 在這裡添加需要檢測的舊前綴模式
        # 例如: r'old-prefix', r'legacy-namespace'
    ]
    
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.result = ValidationResult()
        
        # 排除目錄
        self.exclude_dirs = {
            '.git', '.github', 'node_modules', '__pycache__', 
            'dist', 'build', '.venv', 'venv', 'archive'
        }
    
    def validate_yaml_file(self, file_path: Path) -> bool:
        """驗證單個 YAML 文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 檢查禁止的模式
            for pattern in self.FORBIDDEN_PATTERNS:
                if pattern in content.lower():
                    self.result.errors.append((
                        str(file_path),
                        "檢測到禁止的舊命名空間引用"
                    ))
                    return False
            
            # 嘗試解析 YAML
            try:
                docs = list(yaml.safe_load_all(content))
                file_valid = True
                
                for doc_idx, doc in enumerate(docs):
                    if not isinstance(doc, dict):
                        continue
                    
                    # 檢查 apiVersion
                    if 'apiVersion' in doc:
                        if doc['apiVersion'] != self.REQUIRED_API_VERSION:
                            self.result.errors.append((
                                str(file_path),
                                f"Document {doc_idx}: apiVersion 應為 {self.REQUIRED_API_VERSION}"
                            ))
                            file_valid = False
                    
                    # 檢查 kind
                    if 'kind' in doc:
                        if 'GlobalBaseline' in doc['kind'] and doc['kind'] != self.REQUIRED_KIND:
                            self.result.errors.append((
                                str(file_path),
                                f"Document {doc_idx}: kind 應為 {self.REQUIRED_KIND}"
                            ))
                            file_valid = False
                    
                    # 檢查 metadata
                    if 'metadata' in doc and isinstance(doc['metadata'], dict):
                        metadata = doc['metadata']
                        
                        # 檢查 namespace
                        if 'namespace' in metadata:
                            if metadata['namespace'] != self.REQUIRED_NAMESPACE:
                                self.result.errors.append((
                                    str(file_path),
                                    f"Document {doc_idx}: namespace 應為 {self.REQUIRED_NAMESPACE}"
                                ))
                                file_valid = False
                        
                        # 檢查 labels
                        if 'labels' in metadata and isinstance(metadata['labels'], dict):
                            for key in metadata['labels'].keys():
                                if '/' in key and not key.startswith(self.REQUIRED_LABEL_PREFIX):
                                    self.result.warnings.append((
                                        str(file_path),
                                        f"Document {doc_idx}: label key '{key}' 應使用前綴 {self.REQUIRED_LABEL_PREFIX}"
                                    ))
                        
                        # 檢查 annotations
                        if 'annotations' in metadata and isinstance(metadata['annotations'], dict):
                            for key, value in metadata['annotations'].items():
                                # 檢查 URN
                                if 'urn' in key.lower() and isinstance(value, str):
                                    if value.startswith('urn:') and not value.startswith(self.REQUIRED_URN_PREFIX):
                                        self.result.errors.append((
                                            str(file_path),
                                            f"Document {doc_idx}: URN 應使用前綴 {self.REQUIRED_URN_PREFIX}"
                                        ))
                                        file_valid = False
                                
                                # 檢查 annotation key
                                if '/' in key and not key.startswith(self.REQUIRED_LABEL_PREFIX):
                                    self.result.warnings.append((
                                        str(file_path),
                                        f"Document {doc_idx}: annotation key '{key}' 應使用前綴 {self.REQUIRED_LABEL_PREFIX}"
                                    ))
                
                return file_valid
                
            except yaml.YAMLError as e:
                # YAML 解析錯誤
                self.result.errors.append((
                    str(file_path),
                    f"YAML 解析錯誤: {str(e)}"
                ))
                return False
            
        except Exception as e:
            self.result.errors.append((
                str(file_path),
                f"文件讀取錯誤: {str(e)}"
            ))
            return False
    
    def validate_directory(self) -> bool:
        """驗證整個目錄"""
        print(f"🔍 驗證目錄: {self.root_dir}")
        print()
        
        # 掃描所有 YAML 文件
        yaml_files = []
        for ext in ['*.yaml', '*.yml']:
            yaml_files.extend(self.root_dir.rglob(ext))
        
        # 過濾排除目錄
        yaml_files = [
            f for f in yaml_files 
            if not any(excluded in f.parts for excluded in self.exclude_dirs)
        ]
        
        print(f"📁 找到 {len(yaml_files)} 個 YAML 文件")
        print()
        
        # 驗證每個文件
        for file_path in yaml_files:
            self.result.total_files += 1
            relative_path = file_path.relative_to(self.root_dir)
            
            if self.validate_yaml_file(file_path):
                self.result.valid_files += 1
                print(f"✅ {relative_path}")
            else:
                self.result.invalid_files += 1
                print(f"❌ {relative_path}")
        
        # 輸出結果
        self.print_result()
        
        # 返回驗證是否通過
        return self.result.invalid_files == 0 and len(self.result.errors) == 0
    
    def print_result(self):
        """輸出驗證結果"""
        print()
        print("=" * 60)
        print("📊 驗證結果")
        print("=" * 60)
        print(f"總文件數: {self.result.total_files}")
        print(f"✅ 有效文件: {self.result.valid_files}")
        print(f"❌ 無效文件: {self.result.invalid_files}")
        print()
        
        if self.result.errors:
            print("❌ 錯誤:")
            for file_path, error in self.result.errors[:20]:
                print(f"  📄 {Path(file_path).name}")
                print(f"     {error}")
            
            if len(self.result.errors) > 20:
                print(f"  ... 還有 {len(self.result.errors) - 20} 個錯誤")
            print()
        
        if self.result.warnings:
            print("⚠️  警告:")
            for file_path, warning in self.result.warnings[:20]:
                print(f"  📄 {Path(file_path).name}")
                print(f"     {warning}")
            
            if len(self.result.warnings) > 20:
                print(f"  ... 還有 {len(self.result.warnings) - 20} 個警告")
            print()
        
        if self.result.invalid_files == 0 and len(self.result.errors) == 0:
            print("✅ 所有文件都符合 MachineNativeOps 命名空間標準！")
        else:
            print("❌ 發現不符合標準的文件，請執行轉換工具修正")
            print("   python scripts/migration/namespace-converter.py .")
        
        print("=" * 60)

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='MachineNativeOps 命名空間驗證工具'
    )
    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='要驗證的目錄路徑（默認為當前目錄）'
    )
    parser.add_argument(
        '--staged',
        action='store_true',
        help='只驗證 git staged 文件'
    )
    
    args = parser.parse_args()
    
    # 執行驗證
    validator = NamespaceValidator(args.directory)
    
    if args.staged:
        # TODO: 實現 git staged 文件驗證
        print("⚠️  --staged 選項尚未實現，驗證所有文件")
    
    success = validator.validate_directory()
    
    # 返回適當的退出碼
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()