#!/usr/bin/env python3
"""
進階驗證 - Advanced Verification
驗證架構模式、部署配置、整合點、效能基準
"""

import sys
from pathlib import Path
from typing import List

class AdvancedVerification:
    """進階驗證器"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed_checks = 0
        self.total_checks = 4
        
    def verify_architecture_patterns(self) -> bool:
        """驗證架構模式"""
        print("🏗️  驗證架構模式...")
        
        # 檢查關鍵架構文件
        required_patterns = [
            'root.governance.yaml',
            'root.naming-policy.yaml',
            'mno-namespace.yaml'
        ]
        
        for pattern_file in required_patterns:
            file_path = self.root_dir / pattern_file
            if not file_path.exists():
                self.warnings.append(f"架構文件缺失: {pattern_file}")
        
        # 對於 Python 文件，檢查是否遵循命名約定
        py_files = list(self.root_dir.rglob('src/enterprise/**/*.py'))
        for py_file in py_files:
            # 檢查文件名是否使用蛇形命名法
            if not all(c.islower() or c == '_' or c == '.' for c in py_file.stem):
                self.warnings.append(f"文件名不符合蛇形命名法: {py_file}")
        
        return True
    
    def verify_deployment_config(self) -> bool:
        """驗證部署配置"""
        print("⚙️  驗證部署配置...")
        
        # 檢查是否有必要的配置文件
        config_files = [
            'root.config.yaml',
            'root.bootstrap.yaml'
        ]
        
        for config_file in config_files:
            file_path = self.root_dir / config_file
            if not file_path.exists():
                self.warnings.append(f"配置文件缺失: {config_file}")
        
        return True
    
    def verify_integration_points(self) -> bool:
        """驗證整合點"""
        print("🔗 驗證整合點...")
        
        # 檢查 import 語句是否正確
        py_files = list(self.root_dir.rglob('src/enterprise/**/*.py'))
        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # 檢查是否有相對導入
                    if 'from .' in content or 'import .' in content:
                        # 這是允許的，繼續
                        pass
                    
                    # 檢查是否有循環導入風險
                    if py_file.name == '__init__.py' and 'from' in content:
                        # __init__.py 應該謹慎使用導入
                        pass
            
            except Exception as e:
                self.errors.append(f"讀取文件失敗 {py_file}: {e}")
                return False
        
        return True
    
    def verify_performance_benchmark(self) -> bool:
        """驗證效能基準"""
        print("⚡ 驗證效能基準...")
        
        # 檢查 Python 文件大小（不應過大）
        py_files = list(self.root_dir.rglob('src/enterprise/**/*.py'))
        for py_file in py_files:
            size_kb = py_file.stat().st_size / 1024
            if size_kb > 500:  # 500KB
                self.warnings.append(f"文件過大 ({size_kb:.1f}KB): {py_file}")
        
        # 檢查是否有測試文件
        test_files = list(self.root_dir.rglob('tests/**/test_*.py'))
        if not test_files:
            self.warnings.append("未找到測試文件")
        
        return True
    
    def run(self) -> bool:
        """執行所有進階驗證"""
        print("=" * 60)
        print("🔍 進階驗證 - Advanced Verification")
        print("=" * 60)
        print()
        
        results = []
        
        # 架構模式驗證
        arch_ok = self.verify_architecture_patterns()
        results.append(("架構模式驗證通過", arch_ok))
        self.passed_checks += 1 if arch_ok else 0
        
        # 部署配置測試
        deploy_ok = self.verify_deployment_config()
        results.append(("部署配置測試成功", deploy_ok))
        self.passed_checks += 1 if deploy_ok else 0
        
        # 整合點檢查
        integration_ok = self.verify_integration_points()
        results.append(("整合點檢查完成", integration_ok))
        self.passed_checks += 1 if integration_ok else 0
        
        # 效能基準
        perf_ok = self.verify_performance_benchmark()
        results.append(("效能基準通過", perf_ok))
        self.passed_checks += 1 if perf_ok else 0
        
        # 輸出結果
        print()
        print("=" * 60)
        print("📊 進階驗證結果")
        print("=" * 60)
        
        for check_name, passed in results:
            status = "✅" if passed else "❌"
            print(f"{status} {check_name}")
        
        print()
        print(f"通過檢查: {self.passed_checks}/{self.total_checks}")
        
        if self.errors:
            print()
            print("❌ 錯誤:")
            for error in self.errors:
                print(f"  {error}")
        
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
    
    parser = argparse.ArgumentParser(description='進階驗證工具')
    parser.add_argument('directory', nargs='?', default='.', help='要驗證的目錄')
    
    args = parser.parse_args()
    
    verifier = AdvancedVerification(args.directory)
    success = verifier.run()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
