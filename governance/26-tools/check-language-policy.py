#!/usr/bin/env python3
"""
Language Policy Checker
語言策略檢查器

檢查代碼庫是否符合語言使用策略
"""

import os
import sys
from collections import defaultdict
from pathlib import Path

import yaml


class LanguagePolicyChecker:
    """語言策略檢查器"""
    
    # 語言檔案副檔名映射
    LANGUAGE_EXTENSIONS = {
        'TypeScript': ['.ts', '.tsx'],
        'JavaScript': ['.js', '.jsx'],
        'Python': ['.py', '.pyi'],
        'C++': ['.cpp', '.cc', '.cxx', '.hpp', '.h', '.hxx'],
        'C': ['.c', '.h'],
        'Go': ['.go'],
        'Rust': ['.rs'],
        'Rego': ['.rego'],
        'Bash': ['.sh', '.bash'],
        'PHP': ['.php'],
        'Ruby': ['.rb'],
        'Lua': ['.lua'],
        'Perl': ['.pl', '.pm'],
        'Swift': ['.swift'],
        'Kotlin': ['.kt', '.kts'],
        'Java': ['.java'],
        'HCL': ['.tf', '.hcl'],
    }
    
    def __init__(self, repo_root: str, policy_file: str):
        self.repo_root = Path(repo_root)
        self.policy_file = Path(policy_file)
        self.policy = self._load_policy()
        self.violations = []
        self.stats = defaultdict(lambda: defaultdict(int))
    
    def _load_policy(self) -> dict:
        """載入語言策略配置"""
        try:
            with open(self.policy_file, encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"錯誤：無法載入策略檔案 {self.policy_file}: {e}")
            sys.exit(1)
    
    def _get_language_from_extension(self, ext: str) -> str:
        """根據副檔名判斷語言"""
        for language, extensions in self.LANGUAGE_EXTENSIONS.items():
            if ext.lower() in extensions:
                return language
        return 'Unknown'
    
    def _is_allowed_language(self, language: str, allowed_list: list[str]) -> bool:
        """檢查語言是否在允許列表中"""
        return language in allowed_list
    
    def _get_most_specific_rule(self, file_path: Path) -> tuple[str, dict]:
        """獲取最具體的目錄規則（最長匹配）"""
        directory_rules = self.policy.get('directory_rules', {})
        rel_path = file_path.relative_to(self.repo_root)
        
        best_match = None
        best_pattern = None
        best_length = -1
        
        for dir_pattern, rules in directory_rules.items():
            dir_path = dir_pattern.rstrip('/')
            
            # 檢查文件是否在這個目錄下
            try:
                rel_path.relative_to(dir_path)
                # 如果成功，這個規則匹配，檢查是否是最長匹配
                if len(dir_path) > best_length:
                    best_match = rules
                    best_pattern = dir_pattern
                    best_length = len(dir_path)
            except ValueError:
                # 文件不在這個目錄下
                continue
        
        return best_pattern, best_match
    
    def _check_directory_rules(self):
        """檢查目錄級別的語言規則"""
        directory_rules = self.policy.get('directory_rules', {})
        
        # 收集所有需要檢查的文件
        files_to_check = {}
        
        for dir_pattern, rules in directory_rules.items():
            # 移除結尾的 /
            dir_path = dir_pattern.rstrip('/')
            full_path = self.repo_root / dir_path
            
            if not full_path.exists():
                continue
            
            # 掃描目錄中的檔案
            for file_path in full_path.rglob('*'):
                if not file_path.is_file():
                    continue
                
                # 跳過 .git 目錄
                if '.git' in file_path.parts:
                    continue
                
                ext = file_path.suffix
                if not ext:
                    continue
                
                language = self._get_language_from_extension(ext)
                
                # 檢查是否為未知語言
                if language == 'Unknown':
                    continue
                
                # 記錄文件（如果尚未記錄）
                if file_path not in files_to_check:
                    files_to_check[file_path] = language
        
        # 對每個文件，使用最具體的規則進行檢查
        for file_path, language in files_to_check.items():
            best_pattern, best_rule = self._get_most_specific_rule(file_path)
            
            if best_rule is None:
                continue
            
            # 更新統計
            self.stats[best_pattern][language] += 1
            
            allowed_languages = best_rule.get('allowed_languages', [])
            forbidden_patterns = best_rule.get('forbidden_patterns', [])
            
            # 檢查是否在允許列表中
            if not self._is_allowed_language(language, allowed_languages):
                # 檢查是否為數據格式（YAML, JSON等）
                data_formats = self.policy.get('global_policy', {}).get('data_formats', [])
                if language not in data_formats:
                    self.violations.append({
                        'type': 'LANGUAGE_NOT_ALLOWED',
                        'severity': 'ERROR',
                        'file': str(file_path.relative_to(self.repo_root)),
                        'directory': best_pattern,
                        'language': language,
                        'allowed': allowed_languages,
                        'message': f'{language} 不允許在 {best_pattern} 中使用'
                    })
            
            # 檢查禁止模式
            for pattern in forbidden_patterns:
                if file_path.match(pattern):
                    self.violations.append({
                        'type': 'FORBIDDEN_PATTERN',
                        'severity': 'ERROR',
                        'file': str(file_path.relative_to(self.repo_root)),
                        'directory': best_pattern,
                        'pattern': pattern,
                        'message': f'檔案符合禁止模式 {pattern}'
                    })
    
    def _check_forbidden_languages(self):
        """檢查全域禁止的語言"""
        forbidden = self.policy.get('global_policy', {}).get('forbidden_languages', [])
        
        for file_path in self.repo_root.rglob('*'):
            if not file_path.is_file():
                continue
            
            if '.git' in file_path.parts:
                continue
            
            ext = file_path.suffix
            if not ext:
                continue
            
            language = self._get_language_from_extension(ext)
            
            if language in forbidden:
                self.violations.append({
                    'type': 'GLOBALLY_FORBIDDEN',
                    'severity': 'CRITICAL',
                    'file': str(file_path.relative_to(self.repo_root)),
                    'language': language,
                    'message': f'{language} 是全域禁止的語言'
                })
    
    def check(self) -> bool:
        """執行所有檢查"""
        print("🔍 正在檢查語言策略...\n")
        print(f"Repository: {self.repo_root}")
        print(f"Policy: {self.policy_file}\n")
        
        # 執行檢查
        self._check_directory_rules()
        self._check_forbidden_languages()
        
        return len(self.violations) == 0
    
    def report(self):
        """生成報告"""
        print("\n" + "=" * 70)
        print("📊 語言使用統計")
        print("=" * 70 + "\n")
        
        for directory, languages in self.stats.items():
            if languages:
                print(f"📁 {directory}")
                for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
                    print(f"   • {lang}: {count} 個檔案")
                print()
        
        if self.violations:
            print("\n" + "=" * 70)
            print("❌ 發現違規")
            print("=" * 70 + "\n")
            
            # 按嚴重程度分組
            by_severity = defaultdict(list)
            for v in self.violations:
                by_severity[v['severity']].append(v)
            
            for severity in ['CRITICAL', 'ERROR', 'WARNING']:
                violations = by_severity.get(severity, [])
                if violations:
                    print(f"\n{severity} ({len(violations)} 項):")
                    print("-" * 70)
                    for v in violations:
                        print(f"\n• {v['message']}")
                        print(f"  檔案: {v['file']}")
                        if 'directory' in v:
                            print(f"  目錄: {v['directory']}")
                        if 'language' in v:
                            print(f"  語言: {v['language']}")
            
            print("\n" + "=" * 70)
            print(f"❌ 總共發現 {len(self.violations)} 項違規")
            print("=" * 70)
            return False
        else:
            print("\n" + "=" * 70)
            print("✅ 所有檢查通過！")
            print("=" * 70)
            return True

def main():
    """主函數"""
    repo_root = os.getcwd()
    policy_file = os.path.join(repo_root, 'config', 'language-policy.yaml')
    
    # 檢查策略檔案是否存在
    if not os.path.exists(policy_file):
        print(f"❌ 錯誤：找不到策略檔案 {policy_file}")
        sys.exit(1)
    
    # 創建檢查器
    checker = LanguagePolicyChecker(repo_root, policy_file)
    
    # 執行檢查
    checker.check()
    
    # 生成報告
    success = checker.report()
    
    # 返回結果
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
