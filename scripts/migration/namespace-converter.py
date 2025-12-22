#!/usr/bin/env python3
"""
MachineNativeOps Namespace Converter
將所有配置文件標準化為 MachineNativeOps 命名空間
"""

import os
import re
import sys
import yaml
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, field

@dataclass
class ConversionStats:
    """轉換統計（不顯示舊字串）"""
    files_scanned: int = 0
    files_modified: int = 0
    api_version_updates: int = 0
    kind_updates: int = 0
    namespace_updates: int = 0
    urn_updates: int = 0
    label_updates: int = 0
    hash_changes: List[Tuple[str, str, str]] = field(default_factory=list)  # (file, old_hash, new_hash)

class NamespaceConverter:
    """命名空間轉換器"""
    
    # 標準化目標
    TARGET_API_VERSION = "machinenativeops.io/v2"
    TARGET_KIND = "MachineNativeOpsGlobalBaseline"
    TARGET_NAMESPACE = "machinenativeops"
    TARGET_URN_PREFIX = "urn:machinenativeops:"
    TARGET_LABEL_PREFIX = "machinenativeops.io/"
    
    def __init__(self, root_dir: str, dry_run: bool = False):
        self.root_dir = Path(root_dir)
        self.dry_run = dry_run
        self.stats = ConversionStats()
        
        # 排除目錄
        self.exclude_dirs = {
            '.git', '.github', 'node_modules', '__pycache__', 
            'dist', 'build', '.venv', 'venv'
        }
        
    def calculate_file_hash(self, content: str) -> str:
        """計算文件內容的 SHA256 hash"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def convert_yaml_file(self, file_path: Path) -> bool:
        """轉換 YAML 文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_hash = self.calculate_file_hash(content)
            modified = False
            
            # 嘗試解析 YAML
            try:
                docs = list(yaml.safe_load_all(content))
                
                for doc in docs:
                    if not isinstance(doc, dict):
                        continue
                    
                    # 轉換 apiVersion
                    if 'apiVersion' in doc:
                        old_version = doc['apiVersion']
                        # 僅當 apiVersion 的 group 不是 machinenativeops.io 時才更新
                        old_version_str = str(old_version)
                        api_group = old_version_str.split('/', 1)[0]
                        if api_group != 'machinenativeops.io':
                            doc['apiVersion'] = self.TARGET_API_VERSION
                            self.stats.api_version_updates += 1
                            modified = True
                    
                    # 轉換 kind
                    if 'kind' in doc:
                        old_kind = doc['kind']
                        if 'GlobalBaseline' in old_kind and old_kind != self.TARGET_KIND:
                            doc['kind'] = self.TARGET_KIND
                            self.stats.kind_updates += 1
                            modified = True
                    
                    # 轉換 metadata.namespace
                    if 'metadata' in doc and isinstance(doc['metadata'], dict):
                        if 'namespace' in doc['metadata']:
                            old_ns = doc['metadata']['namespace']
                            if old_ns != self.TARGET_NAMESPACE:
                                doc['metadata']['namespace'] = self.TARGET_NAMESPACE
                                self.stats.namespace_updates += 1
                                modified = True
                        
                        # 轉換 labels
                        if 'labels' in doc['metadata']:
                            labels = doc['metadata']['labels']
                            if isinstance(labels, dict):
                                new_labels = {}
                                for key, value in labels.items():
                                    if not key.startswith(self.TARGET_LABEL_PREFIX):
                                        # 提取 key 的後半部分
                                        key_suffix = key.split('/')[-1] if '/' in key else key
                                        new_key = f"{self.TARGET_LABEL_PREFIX}{key_suffix}"
                                        new_labels[new_key] = value
                                        self.stats.label_updates += 1
                                        modified = True
                                    else:
                                        new_labels[key] = value
                                doc['metadata']['labels'] = new_labels
                        
                        # 轉換 annotations
                        if 'annotations' in doc['metadata']:
                            annotations = doc['metadata']['annotations']
                            if isinstance(annotations, dict):
                                new_annotations = {}
                                for key, value in annotations.items():
                                    # 轉換 URN
                                    if 'urn' in key.lower() and isinstance(value, str):
                                        if not value.startswith(self.TARGET_URN_PREFIX):
                                            # 提取 URN 的後半部分
                                            urn_parts = value.split(':')
                                            if len(urn_parts) > 2:
                                                new_value = self.TARGET_URN_PREFIX + ':'.join(urn_parts[2:])
                                                new_annotations[key] = new_value
                                                self.stats.urn_updates += 1
                                                modified = True
                                            else:
                                                new_annotations[key] = value
                                        else:
                                            new_annotations[key] = value
                                    # 轉換 annotation key
                                    elif not key.startswith(self.TARGET_LABEL_PREFIX):
                                        key_suffix = key.split('/')[-1] if '/' in key else key
                                        new_key = f"{self.TARGET_LABEL_PREFIX}{key_suffix}"
                                        new_annotations[new_key] = value
                                        self.stats.label_updates += 1
                                        modified = True
                                    else:
                                        new_annotations[key] = value
                                doc['metadata']['annotations'] = new_annotations
                
                if modified:
                    # 重新序列化 YAML
                    new_content = yaml.dump_all(docs, default_flow_style=False, sort_keys=False, allow_unicode=True)
                    
                    if not self.dry_run:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                    
                    new_hash = self.calculate_file_hash(new_content)
                    self.stats.hash_changes.append((str(file_path), original_hash, new_hash))
                    self.stats.files_modified += 1
                    return True
                    
            except yaml.YAMLError:
                # 如果不是有效的 YAML，跳過
                pass
            
            return False
            
        except Exception as e:
            print(f"❌ 處理文件失敗 {file_path}: {e}")
            return False
    
    def convert_directory(self):
        """轉換整個目錄"""
        print(f"🔍 掃描目錄: {self.root_dir}")
        print(f"{'🔄 乾跑模式' if self.dry_run else '✅ 執行模式'}")
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
        
        # 轉換每個文件
        for file_path in yaml_files:
            self.stats.files_scanned += 1
            relative_path = file_path.relative_to(self.root_dir)
            
            if self.convert_yaml_file(file_path):
                print(f"✅ 已轉換: {relative_path}")
        
        # 輸出統計
        self.print_stats()
    
    def print_stats(self):
        """輸出轉換統計（不顯示舊字串）"""
        print()
        print("=" * 60)
        print("📊 轉換統計")
        print("=" * 60)
        print(f"掃描文件數: {self.stats.files_scanned}")
        print(f"修改文件數: {self.stats.files_modified}")
        print()
        print("詳細變更:")
        print(f"  - apiVersion 更新: {self.stats.api_version_updates}")
        print(f"  - kind 更新: {self.stats.kind_updates}")
        print(f"  - namespace 更新: {self.stats.namespace_updates}")
        print(f"  - URN 更新: {self.stats.urn_updates}")
        print(f"  - 標籤/註解更新: {self.stats.label_updates}")
        print()
        
        if self.stats.hash_changes:
            print("Hash 變化:")
            for file_path, old_hash, new_hash in self.stats.hash_changes[:10]:
                print(f"  📄 {Path(file_path).name}")
                print(f"     舊: {old_hash}")
                print(f"     新: {new_hash}")
            
            if len(self.stats.hash_changes) > 10:
                print(f"  ... 還有 {len(self.stats.hash_changes) - 10} 個文件")
        
        print()
        if self.dry_run:
            print("ℹ️  這是乾跑模式，未實際修改文件")
            print("   移除 --dry-run 參數以執行實際轉換")
        else:
            print("✅ 轉換完成！")
        print("=" * 60)

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='MachineNativeOps 命名空間轉換工具'
    )
    parser.add_argument(
        'directory',
        help='要轉換的目錄路徑'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='乾跑模式（不實際修改文件）'
    )
    
    args = parser.parse_args()
    
    # 執行轉換
    converter = NamespaceConverter(args.directory, dry_run=args.dry_run)
    converter.convert_directory()

if __name__ == '__main__':
    main()