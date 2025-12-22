#!/usr/bin/env python3
"""
基礎驗證 - Basic Verification
驗證 YAML 語法、命名空間一致性、資源類型標準化
"""

import sys
import yaml
from pathlib import Path
from typing import List, Tuple, Dict, Any

class BasicVerification:
    """基礎驗證器"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed_checks = 0
        self.total_checks = 0
        
    def check_yaml_syntax(self, file_path: Path) -> bool:
        """檢查 YAML 語法"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                list(yaml.safe_load_all(f.read()))
            return True
        except yaml.YAMLError as e:
            self.errors.append(f"YAML 語法錯誤 in {file_path}: {e}")
            return False
        except Exception as e:
            self.errors.append(f"無法讀取 {file_path}: {e}")
            return False
    
    def check_namespace_consistency(self, file_path: Path) -> bool:
        """檢查命名空間一致性"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                docs = list(yaml.safe_load_all(content))
            
            for doc in docs:
                if not isinstance(doc, dict):
                    continue
                
                # 檢查 namespace 字段
                if 'metadata' in doc and 'namespace' in doc['metadata']:
                    ns = doc['metadata']['namespace']
                    if ns != 'machinenativeops':
                        self.warnings.append(
                            f"{file_path}: namespace應為'machinenativeops'，當前為'{ns}'"
                        )
                        return False
            
            return True
        except Exception as e:
            self.errors.append(f"命名空間檢查失敗 {file_path}: {e}")
            return False
    
    def check_resource_types(self, file_path: Path) -> bool:
        """檢查資源類型標準化"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                docs = list(yaml.safe_load_all(f.read()))
            
            standard_kinds = {
                'Deployment', 'Service', 'ConfigMap', 'Secret',
                'Pod', 'ReplicaSet', 'StatefulSet', 'DaemonSet',
                'MachineNativeOpsGlobalBaseline', 'MachineNativeOpsNamespaceConfig'
            }
            
            for doc in docs:
                if not isinstance(doc, dict):
                    continue
                
                if 'kind' in doc:
                    kind = doc['kind']
                    # 這裡可以添加更多驗證邏輯
                    if kind not in standard_kinds and not kind.startswith('MachineNativeOps'):
                        self.warnings.append(
                            f"{file_path}: 非標準資源類型 '{kind}'"
                        )
            
            return True
        except Exception as e:
            self.errors.append(f"資源類型檢查失敗 {file_path}: {e}")
            return False
    
    def verify_yaml_files(self) -> bool:
        """驗證所有 YAML 文件"""
        yaml_files = list(self.root_dir.rglob('*.yaml')) + list(self.root_dir.rglob('*.yml'))
        
        # 過濾排除目錄
        exclude_dirs = {'.git', 'node_modules', '__pycache__', 'dist', 'build', '.venv', 'archive'}
        yaml_files = [
            f for f in yaml_files 
            if not any(excluded in f.parts for excluded in exclude_dirs)
        ]
        
        if not yaml_files:
            print("⚠️  未找到 YAML 文件")
            return True
        
        print(f"📁 找到 {len(yaml_files)} 個 YAML 文件")
        
        all_passed = True
        for file_path in yaml_files:
            self.total_checks += 3  # 3 checks per file
            
            # 檢查 YAML 語法
            if self.check_yaml_syntax(file_path):
                self.passed_checks += 1
            else:
                all_passed = False
            
            # 檢查命名空間
            if self.check_namespace_consistency(file_path):
                self.passed_checks += 1
            else:
                all_passed = False
            
            # 檢查資源類型
            if self.check_resource_types(file_path):
                self.passed_checks += 1
            else:
                all_passed = False
        
        return all_passed
    
    def verify_python_syntax(self) -> bool:
        """驗證 Python 語法"""
        import ast
        
        python_files = list(self.root_dir.rglob('*.py'))
        
        # 過濾排除目錄
        exclude_dirs = {'.git', 'node_modules', '__pycache__', 'dist', 'build', '.venv', 'archive'}
        python_files = [
            f for f in python_files 
            if not any(excluded in f.parts for excluded in exclude_dirs)
        ]
        
        if not python_files:
            return True
        
        print(f"🐍 找到 {len(python_files)} 個 Python 文件")
        
        all_passed = True
        for file_path in python_files:
            self.total_checks += 1
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    ast.parse(f.read())
                self.passed_checks += 1
            except SyntaxError as e:
                self.errors.append(f"Python 語法錯誤 in {file_path}: {e}")
                all_passed = False
        
        return all_passed
    
    def run(self) -> bool:
        """執行所有基礎驗證"""
        print("=" * 60)
        print("🔍 基礎驗證 - Basic Verification")
        print("=" * 60)
        print()
        
        results = []
        
        # YAML 文件驗證
        print("📋 檢查 YAML 語法...")
        yaml_ok = self.verify_yaml_files()
        results.append(("YAML 語法正確", yaml_ok))
        
        # Python 文件驗證
        print("🐍 檢查 Python 語法...")
        python_ok = self.verify_python_syntax()
        results.append(("Python 語法正確", python_ok))
        
        # 命名空間一致性（已包含在 YAML 驗證中）
        results.append(("命名空間一致性檢查通過", not any("namespace" in e for e in self.errors + self.warnings)))
        
        # 資源類型標準化（已包含在 YAML 驗證中）
        results.append(("資源類型標準化完成", not any("資源類型" in e for e in self.errors)))
        
        # 輸出結果
        print()
        print("=" * 60)
        print("📊 基礎驗證結果")
        print("=" * 60)
        
        for check_name, passed in results:
            status = "✅" if passed else "❌"
            print(f"{status} {check_name}")
        
        print()
        print(f"通過檢查: {self.passed_checks}/{self.total_checks}")
        
        if self.errors:
            print()
            print("❌ 錯誤:")
            for error in self.errors[:10]:
                print(f"  {error}")
            if len(self.errors) > 10:
                print(f"  ... 還有 {len(self.errors) - 10} 個錯誤")
        
        if self.warnings:
            print()
            print("⚠️  警告:")
            for warning in self.warnings[:10]:
                print(f"  {warning}")
            if len(self.warnings) > 10:
                print(f"  ... 還有 {len(self.warnings) - 10} 個警告")
        
        print("=" * 60)
        
        return all(passed for _, passed in results) and not self.errors

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='基礎驗證工具')
    parser.add_argument('directory', nargs='?', default='.', help='要驗證的目錄')
    
    args = parser.parse_args()
    
    verifier = BasicVerification(args.directory)
    success = verifier.run()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
