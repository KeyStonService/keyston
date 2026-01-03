#!/usr/bin/env python3
"""
一鍵自動修復系統
One-Click Auto Fix System

功能：
1. 自動修復可修復的漏洞
2. 生成修復報告
3. 創建修復補丁
4. 修復驗證
"""

import os
import json
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
from abc import ABC, abstractmethod

@dataclass
class FixResult:
    """修復結果數據結構"""
    file_path: str
    vulnerability_type: str
    status: str  # success, failed, skipped, manual_review_required
    original_line: str
    fixed_line: str
    message: str
    requires_review: bool = False

class VulnerabilityFixer(ABC):
    """漏洞修復器基類"""
    
    @abstractmethod
    def can_fix(self, vulnerability: Dict) -> bool:
        """判斷是否可以修復此漏洞"""
        pass
    
    @abstractmethod
    def fix(self, file_path: str, vulnerability: Dict) -> Tuple[bool, str, str]:
        """
        修復漏洞
        
        返回: (success, original_line, fixed_line)
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """獲取修復器描述"""
        pass

class HardcodedPasswordFixer(VulnerabilityFixer):
    """硬編碼密碼修復器"""
    
    def can_fix(self, vulnerability: Dict) -> bool:
        vuln_type = vulnerability.get('type', '').lower()
        return 'password' in vuln_type and 'hardcoded' in vuln_type
    
    def fix(self, file_path: str, vulnerability: Dict) -> Tuple[bool, str, str]:
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            line_num = vulnerability.get('line_number', 1) - 1
            original_line = lines[line_num] if line_num < len(lines) else ""
            
            # 將硬編碼密碼替換為基於變量名的環境變量
            def _replace_password(match: re.Match) -> str:
                lhs = match.group('lhs')
                var_name = match.group('var') or 'password'
                # 將變量名轉換為環境變量名，例如 api_password -> API_PASSWORD
                env_name = re.sub(r'\W+', '_', var_name).upper()
                if not env_name:
                    env_name = 'PASSWORD'
                return f"{lhs}os.environ.get('{env_name}')"

            fixed_line = re.sub(
                r'(?P<lhs>\b(?P<var>\w*password\w*)\s*=\s*)["\'][^"\']+["\']',
                _replace_password,
                original_line
                lhs = match.group(1)
                var_name = match.group('var')
                # 將變量名轉換為環境變量名，例如 api_password -> API_PASSWORD
                env_name = re.sub(r'\W+', '_', var_name).upper()
                if not env_name or env_name == '_':
                    env_name = 'PASSWORD'
                return f"{lhs}os.environ.get('{env_name}')"
            
            fixed_line = re.sub(
                r'(?P<lhs>\b(?P<var>\w*password\w*)\s*=\s*)["\'][^"\']+["\']',
                _replace_password,
                original_line
            )
            
            # 檢查是否需要添加 import
            if fixed_line != original_line:
                lines[line_num] = fixed_line
                
                # 檢查是否需要導入 os
                needs_import = True
                for line in lines[:line_num]:
                    # 使用正則表達式精確匹配 import os，避免誤匹配註釋或字符串
                    if re.search(r'\bimport\s+os\b', line) or re.search(r'\bfrom\s+os\b', line):
                        needs_import = False
                        break
                
                if needs_import:
                    # 在文件頂部添加 import os，遵循 PEP 8 標準
                    # 在文件頂部添加 import os，遵循 PEP 8 導入順序
                    insert_pos = 0
                    
                    # 跳過 shebang
                    if lines and lines[0].startswith('#!'):
                        insert_pos = 1
                    
                    # 跳過模組 docstring（單行或多行）
                    if insert_pos < len(lines):
                        line = lines[insert_pos].lstrip()
                        if line.startswith(('"""', "'''")):
                            docstring_delim = line[:3]
                            # 檢查是否為單行 docstring（分隔符在同一行中出現至少兩次）
                            rest_of_line = line[3:]  # 移除開頭的分隔符
                            if docstring_delim in rest_of_line:
                                # 單行 docstring
                                insert_pos += 1
                            else:
                                # 多行 docstring - 尋找行首的結束分隔符
                                insert_pos += 1
                                while insert_pos < len(lines):
                                    if lines[insert_pos].lstrip().startswith(docstring_delim):
                                        insert_pos += 1
                                        break
                                    insert_pos += 1
                    
                    # 跳過 from __future__ imports（必須在所有其他導入之前）
                    while insert_pos < len(lines) and lines[insert_pos].lstrip().startswith('from __future__ import'):
                        insert_pos += 1
                    
                    # 找到標準庫導入的位置（在其他導入之前）
                    # os 是標準庫，應該在第三方庫導入之前
                    # 如果已有其他標準庫導入（如 import sys, import re），插入到它們之後
                    # 如果沒有標準庫導入但有第三方庫導入，插入到第三方庫之前
                    found_first_import = False
                    for i in range(insert_pos, len(lines)):
                        stripped = lines[i].lstrip()
                        if stripped.startswith('import ') or stripped.startswith('from '):
                            # 檢查是否已經有 import os（包括各種形式）
                            if re.search(r'\bimport\s+os\b', stripped) or re.search(r'\bfrom\s+os\b', stripped):
                                # os 已經導入，不需要再添加
                                needs_import = False
                                break
                            if not found_first_import:
                                found_first_import = True
                                insert_pos = i
                            # 繼續掃描標準庫導入
                            # 簡單啟發式：標準庫通常是單個單詞（os, sys, re 等）
                            # 第三方庫通常有下劃線或多個單詞
                            import_match = re.match(r'(?:import|from)\s+([a-zA-Z_][a-zA-Z0-9_]*)', stripped)
                            if import_match:
                                module_name = import_match.group(1)
                                # 常見標準庫模組名
                                stdlib_modules = {'os', 'sys', 're', 'json', 'pathlib', 'datetime', 
                                                'typing', 'dataclasses', 'abc', 'collections', 
                                                'itertools', 'functools', 'operator', 'copy'}
                                if module_name in stdlib_modules:
                                    # 這是標準庫導入，插入點應該在它之後
                                    insert_pos = i + 1
                                else:
                                    # 這是第三方庫導入，應該插入在它之前
                                    break
                        elif found_first_import and stripped and not stripped.startswith('#'):
                            # 找到第一個非導入、非空、非註釋行，導入區結束
                            break
                    
                    if needs_import:
                        lines.insert(insert_pos, 'import os\n')
                    # 查找最後一個標準庫導入的位置（os 是標準庫）
                    # 標準庫導入應該在第三方庫導入之前
                    last_import_pos = insert_pos
                    for i in range(insert_pos, len(lines)):
                        if lines[i].startswith('import ') or lines[i].startswith('from '):
                            # 如果是標準庫導入，記錄位置
                            if not lines[i].startswith(('import os', 'from os ')):
                                last_import_pos = i + 1
                        elif lines[i].strip() and not lines[i].startswith('#'):
                            # 遇到非空、非註釋行，導入區結束
                            break
                    
                    # 在最後一個導入後插入，如果沒有其他導入則在 docstring 後插入
                    lines.insert(last_import_pos, 'import os\n')
                
                # 寫入文件
                with open(file_path, 'w') as f:
                    f.writelines(lines)
                
                return True, original_line.strip(), fixed_line.strip()
        
        except Exception as e:
            print(f"  ⚠️ 修復硬編碼密碼時發生錯誤: {e}")
            return False, "", str(e)
        
        return False, original_line, "無法自動修復此硬編碼密碼"
    
    def get_description(self) -> str:
        return "修復硬編碼密碼問題"

class SQLInjectionFixer(VulnerabilityFixer):
    """SQL 注入修復器"""
    
    def can_fix(self, vulnerability: Dict) -> bool:
        vuln_type = vulnerability.get('type', '').lower()
        return 'sql' in vuln_type and 'injection' in vuln_type
    
    def fix(self, file_path: str, vulnerability: Dict) -> Tuple[bool, str, str]:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            original_content = content
            
            # 簡單的字符串拼接查詢檢測
            # 例如: query = "SELECT * FROM users WHERE id = " + user_input
            patterns = [
                r'query\s*=\s*["\']SELECT.*?\+\s*\w+',
                r'execute\s*\(\s*["\'].*?\+.*?\)',
                r'cursor\.execute\s*\(\s*f["\'].*?\{.*?\}.*?["\']',
            ]
            
            for pattern in patterns:
                if re.search(pattern, content):
                    # 這是一個簡化的修復，實際情況需要更複雜的處理
                    # 標記為需要人工審查
                    return False, content, "SQL 注入修復需要人工審查，請使用參數化查詢"
            
            return False, original_content, "未檢測到可自動修復的 SQL 注入模式"
        
        except Exception as e:
            print(f"  ⚠️ 檢測 SQL 注入時發生錯誤: {e}")
            return False, "", str(e)
    
    def get_description(self) -> str:
        return "檢測 SQL 注入問題（需要人工審查）"

class UnpinnedDependencyFixer(VulnerabilityFixer):
    """未固定版本依賴修復器"""
    
    def can_fix(self, vulnerability: Dict) -> bool:
        vuln_type = vulnerability.get('type', '').lower()
        return 'dependency' in vuln_type and 'version' in vuln_type
    
    def fix(self, file_path: str, vulnerability: Dict) -> Tuple[bool, str, str]:
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            line_num = vulnerability.get('line_number', 1) - 1
            original_line = lines[line_num] if line_num < len(lines) else ""
            
            # 提取包名
            package_name = original_line.strip().split('>=')[0].split('==')[0].split('~=')[0].strip()
            
            # 標記為需要人工審查，不自動添加版本號
            # 因為不是所有包都從 1.0.0 開始，自動添加可能導致問題
            return False, original_line.strip(), f"依賴 {package_name} 需要手動固定版本號，請查詢合適的版本並使用 == 固定"
        
        except Exception as e:
            print(f"  ⚠️ 修復未固定版本依賴時發生錯誤: {e}")
            return False, "", str(e)
    
    def get_description(self) -> str:
        return "修復未固定版本的依賴"

class LongLineFixer(VulnerabilityFixer):
    """長行修復器"""
    
    def can_fix(self, vulnerability: Dict) -> bool:
        vuln_type = vulnerability.get('type', '').lower()
        return vuln_type == 'long line'
    
    def _detect_indentation(self, lines: List[str]) -> str:
        """
        檢測文件的縮進風格
        
        Args:
            lines: 文件內容行列表
            
        Returns:
            縮進字符串（'    ' 表示4空格，'  ' 表示2空格，'\t' 表示tab）
        """
        indent_counts = {2: 0, 4: 0, 8: 0, 'tab': 0}
        
        for line in lines:
            if not line.strip():
                continue
            
            # 計算前導空格
            stripped = line.lstrip(' ')
            if stripped == line:
                # 檢查是否為 tab
                if line.startswith('\t'):
                    indent_counts['tab'] += 1
                continue
            
            spaces = len(line) - len(stripped)
            if spaces % 8 == 0 and spaces > 0:
                indent_counts[8] += 1
            elif spaces % 4 == 0 and spaces > 0:
                indent_counts[4] += 1
            elif spaces % 2 == 0 and spaces > 0:
                indent_counts[2] += 1
        
        # 返回最常用的縮進風格
        if indent_counts['tab'] > max(indent_counts[2], indent_counts[4], indent_counts[8]):
            return '\t'
        elif indent_counts[8] > max(indent_counts[2], indent_counts[4]):
            return ' ' * 8
        elif indent_counts[4] > indent_counts[2]:
            return ' ' * 4
        else:
            return '  '  # 默認2空格
    
    def fix(self, file_path: str, vulnerability: Dict) -> Tuple[bool, str, str]:
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            line_num = vulnerability.get('line_number', 1) - 1
            original_line = lines[line_num] if line_num < len(lines) else ""
            
            if len(original_line) <= 120:
                return False, original_line, "行長度已符合要求"
            
            # 檢查是否為註釋（不適合自動拆分）
            # 簡單的拆分策略（實際需要更智能的 AST 分析）
            # 在逗號或操作符處拆分
            # 檢查是否為字符串字面量或註釋（不適合自動拆分）
            stripped = original_line.lstrip()
            if stripped.startswith('#'):
                return False, original_line, "此行包含註釋，需要人工檢查"
            
            # 若此行主要為字符串字面量（可選的簡單賦值之後緊跟字符串），則跳過自動拆分
            stripped_after_assign = re.sub(r'^[\w\.\[\]\(\)\s]+= *', '', stripped)
            stripped_after_assign = re.sub(r'^\w+\s*=\s*', '', stripped)
            if stripped_after_assign.startswith('"') or stripped_after_assign.startswith("'"):
                return False, original_line, "此行主要為字符串字面量，需要人工檢查"
            
            # 檢測縮進
            indent = len(original_line) - len(stripped)
            indent_str = original_line[:indent]
            
            # 檢測文件的縮進風格
            file_indent = self._detect_indentation(lines)
            
            # 簡單的拆分策略：在逗號或操作符處拆分
            fixed_lines = []
            remaining = original_line.rstrip('\n')
            
            while len(remaining) > 120:
                # 嘗試在逗號處拆分
                split_pos = remaining[:120].rfind(',')
                if split_pos == -1:
                    # 在空格處拆分
                    split_pos = remaining[:120].rfind(' ')
                
                if split_pos == -1:
                    # 無法找到安全的拆分點，標記為需要人工審查
                    return False, original_line, "無法找到安全的拆分點，需要人工檢查"
                
                fixed_lines.append(remaining[:split_pos + 1] + '\n')
                # 使用檢測到的縮進風格
                remaining = indent_str + file_indent + remaining[split_pos + 1:].lstrip()
            
            fixed_lines.append(remaining + '\n')
            
            lines[line_num:line_num + 1] = fixed_lines
            
            # 寫入文件
            with open(file_path, 'w') as f:
                f.writelines(lines)
            
            return True, original_line.strip(), '\n'.join(fixed_lines).strip()
        
        except Exception as e:
            print(f"  ⚠️ 修復過長代碼行時發生錯誤: {e}")
            return False, "", str(e)
    
    def _detect_indentation(self, lines: List[str]) -> str:
        """檢測文件的縮進風格（空格或 Tab）"""
        # 統計文件中使用的縮進類型
        space_indent = 0
        tab_indent = 0
        
        for line in lines:
            if line.startswith('    '):
                space_indent += 1
            elif line.startswith('\t'):
                tab_indent += 1
        
        # 返回最常用的縮進風格，默認 4 個空格
        if tab_indent > space_indent:
            return '\t'
        return '    '
    
    def get_description(self) -> str:
        return "修復過長的代碼行"
    
    def _detect_indentation(self, lines: List[str]) -> str:
        """檢測文件的縮進風格（空格或制表符）"""
        # 檢查文件中的縮進模式
        space_indents = {}  # 記錄不同空格縮進的出現次數
        tab_count = 0
        
        for line in lines:
            if not line.strip():  # 跳過空行
                continue
            
            # 計算行首的空格和制表符
            stripped = line.lstrip()
            if stripped == line:  # 沒有縮進
                continue
            
            indent = line[:len(line) - len(stripped)]
            
            if '\t' in indent:
                tab_count += 1
            elif ' ' in indent:
                # 記錄空格縮進的長度
                space_len = len(indent)
                space_indents[space_len] = space_indents.get(space_len, 0) + 1
        
        # 如果制表符更常見，返回制表符
        if tab_count > sum(space_indents.values()):
            return '\t'
        
        # 否則找出最常見的空格縮進長度
        if space_indents:
            # 獲取最常見的縮進單位（2或4空格）
            common_indent = max(space_indents, key=space_indents.get)
            # 找出最大公約數作為縮進單位
            from math import gcd
            indent_unit = common_indent
            for length in space_indents.keys():
                if length > 0:
                    indent_unit = gcd(indent_unit, length)
            
            # 確保縮進單位在合理範圍內（2或4空格）
            if indent_unit in (2, 4):
                return ' ' * indent_unit
        
        # 默認返回4個空格
        return '    '

class AutoFixer:
    """
    自動修復系統
    
    提供一鍵自動修復常見代碼問題的功能，包括硬編碼密碼、
    未固定版本依賴、過長代碼行等。
    
    Attributes:
        fixers: 可用的修復器列表
        fix_report: 修復操作的詳細報告
    """
    
    def __init__(self) -> None:
        """初始化自動修復系統，註冊所有可用的修復器"""
        self.fixers = [
            HardcodedPasswordFixer(),
            SQLInjectionFixer(),
            UnpinnedDependencyFixer(),
            LongLineFixer(),
        ]
        self.fix_report = {
            "metadata": {
                "fix_time": datetime.utcnow().isoformat(),
                "fixer_version": "1.0.0"
            },
            "fixed": [],
            "failed": [],
            "skipped": [],
            "manual_review_required": [],
            "summary": {}
        }
    
    def auto_fix_all(self, scan_results: Dict) -> Dict:
        """
        一鍵修復所有可修復的漏洞
        
        Args:
            scan_results: 代碼掃描結果字典
            
        Returns:
            包含修復狀態、成功、失敗和需要審查項目的修復報告
        """
        print("🔧 開始自動修復...")
        
        # 獲取所有發現
        all_findings = self._get_all_findings(scan_results)
        
        print(f"📋 共發現 {len(all_findings)} 個問題")
        
        # 按文件分組
        files_to_fix = self._group_findings_by_file(all_findings)
        
        # 修復每個文件的問題
        for file_path, findings in files_to_fix.items():
            print(f"\n📄 處理文件: {file_path}")
            self._fix_file(file_path, findings)
        
        # 生成摘要
        self._generate_summary()
        
        # 保存報告
        self._save_report()
        
        print("\n✅ 自動修復完成!")
        return self.fix_report
    
    def _get_all_findings(self, scan_results: Dict) -> List[Dict]:
        """獲取所有發現"""
        findings = []
        for category in ['security', 'dependencies', 'code_quality', 'performance', 'compliance']:
            findings.extend(scan_results.get(category, []))
        return findings
    
    def _group_findings_by_file(self, findings: List[Dict]) -> Dict[str, List[Dict]]:
        """按文件分組發現"""
        files = {}
        for finding in findings:
            file_path = finding.get('file_path')
            if file_path and os.path.exists(file_path):
                if file_path not in files:
                    files[file_path] = []
                files[file_path].append(finding)
        return files
    
    def _fix_file(self, file_path: str, findings: List[Dict]):
        """修復單個文件的問題"""
        for vuln in findings:
            fixer = self._find_fixer(vuln)
            
            if not fixer:
                self.fix_report['skipped'].append({
                    'file': file_path,
                    'type': vuln.get('type'),
                    'reason': '無可用的修復器'
                })
                continue
            
            print(f"  - 嘗試修復: {vuln.get('type')}")
            
            try:
                success, original, fixed = fixer.fix(file_path, vuln)
                
                if success:
                    result = FixResult(
                        file_path=file_path,
                        vulnerability_type=vuln.get('type'),
                        status='success',
                        original_line=original,
                        fixed_line=fixed,
                        message=fixer.get_description(),
                        requires_review=False
                    )
                    self.fix_report['fixed'].append(asdict(result))
                    print(f"    ✅ 修復成功")
                
                else:
                    if 'manual review' in fixed.lower():
                        result = FixResult(
                            file_path=file_path,
                            vulnerability_type=vuln.get('type'),
                            status='manual_review_required',
                            original_line=original[:100] if original else '',
                            fixed_line=fixed,
                            message=fixer.get_description(),
                            requires_review=True
                        )
                        self.fix_report['manual_review_required'].append(asdict(result))
                        print(f"    ⚠️ 需要人工審查")
                    else:
                        self.fix_report['failed'].append({
                            'file': file_path,
                            'type': vuln.get('type'),
                            'error': fixed
                        })
                        print(f"    ❌ 修復失敗: {fixed}")
            
            except Exception as e:
                self.fix_report['failed'].append({
                    'file': file_path,
                    'type': vuln.get('type'),
                    'error': str(e)
                })
                print(f"    ❌ 修復異常: {e}")
    
    def _find_fixer(self, vulnerability: Dict) -> VulnerabilityFixer:
        """找到合適的修復器"""
        for fixer in self.fixers:
            if fixer.can_fix(vulnerability):
                return fixer
        return None
    
    def _generate_summary(self):
        """生成修復摘要"""
        total = len(self.fix_report['fixed']) + len(self.fix_report['failed']) + \
                len(self.fix_report['skipped']) + len(self.fix_report['manual_review_required'])
        
        self.fix_report['summary'] = {
            'total_issues': total,
            'fixed': len(self.fix_report['fixed']),
            'failed': len(self.fix_report['failed']),
            'skipped': len(self.fix_report['skipped']),
            'manual_review_required': len(self.fix_report['manual_review_required']),
            'success_rate': round(len(self.fix_report['fixed']) / total * 100, 2) if total > 0 else 0
        }
    
    def _save_report(self):
        """保存修復報告"""
        report_dir = Path(".github/code-scanning/reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = report_dir / f"fix-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        
        with open(report_path, 'w') as f:
            json.dump(self.fix_report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 修復報告已保存至: {report_path}")
        
        # 打印摘要
        print(f"\n📈 修復摘要:")
        print(f"  - 總問題數: {self.fix_report['summary']['total_issues']}")
        print(f"  - 已修復: {self.fix_report['summary']['fixed']}")
        print(f"  - 需要審查: {self.fix_report['summary']['manual_review_required']}")
        print(f"  - 失敗: {self.fix_report['summary']['failed']}")
        print(f"  - 跳過: {self.fix_report['summary']['skipped']}")
        print(f"  - 成功率: {self.fix_report['summary']['success_rate']}%")
    
    def create_fix_patches(self) -> List[str]:
        """創建修復補丁文件"""
        patches = []
        
        for fix in self.fix_report['fixed']:
            patch_content = self._generate_patch_content(fix)
            patch_file = f"patch_{fix['file_path'].replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.diff"
            
            patch_path = Path(".github/code-scanning/reports") / patch_file
            with open(patch_path, 'w') as f:
                f.write(patch_content)
            
            patches.append(str(patch_path))
        
        return patches
    
    def _generate_patch_content(self, fix: Dict) -> str:
        """生成補丁內容"""
        return f"""--- a/{fix['file_path']}
+++ b/{fix['file_path']}
@@ -1,1 +1,1 @@
-{fix['original_line']}
+{fix['fixed_line']}
"""

def main() -> None:
    """
    主執行函數
    
    從命令行讀取掃描結果並執行自動修復。
    支持 --dry-run 參數進行模擬運行。
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python auto_fixer.py <scan_results.json> [--dry-run]")
        sys.exit(1)
    
    input_path = sys.argv[1]
    dry_run = '--dry-run' in sys.argv
    
    # 讀取掃描結果
    with open(input_path) as f:
        scan_results = json.load(f)
    
    # 執行修復
    fixer = AutoFixer()
    
    if dry_run:
        print("🔍 模擬運行模式 - 不會實際修改文件")
        print("⚠️  模擬運行模式尚未完全實現，將跳過文件寫入操作")
        # Note: 完整的模擬運行模式需要在各個修復器中添加 dry_run 參數支持
    else:
        fixer.auto_fix_all(scan_results)
        print(json.dumps(fixer.fix_report, ensure_ascii=False, indent=2))
        print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()