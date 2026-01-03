#!/usr/bin/env python3
"""
高階深度代碼掃描工具
Advanced Deep Code Scanner

功能：
1. 多層次掃描 (安全、依賴、質量、性能、合規)
2. 智能漏洞檢測
3. 結果聚合與分析
"""

import os
import sys
import json
import subprocess
import tempfile
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

@dataclass
class VulnerabilityReport:
    """漏洞報告數據結構"""
    severity: str
    type: str
    location: str
    file_path: str
    line_number: int
    code_snippet: str
    cwe_id: str
    description: str
    recommendation: str
    tool: str
    confidence: float

class AdvancedCodeScanner:
    """
    高階代碼掃描器
    
    提供全面的代碼安全、依賴、質量、性能和合規性掃描功能。
    
    Attributes:
        repo_path: 待掃描的儲存庫路徑
        output_dir: 掃描報告輸出目錄
        findings: 掃描發現的問題列表
        scan_results: 掃描結果的完整數據結構
    """
    
    def __init__(self, repo_path: str = ".", output_dir: str = ".github/code-scanning/reports") -> None:
        """
        初始化代碼掃描器
        
        Args:
            repo_path: 儲存庫根目錄路徑，默認為當前目錄
            output_dir: 掃描報告輸出目錄路徑
        """
        self.repo_path = Path(repo_path).resolve()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.findings = []
        self.scan_results = {
            "metadata": {
                "scan_time": datetime.utcnow().isoformat(),
                "repo_path": str(self.repo_path),
                "scanner_version": "1.0.0"
            },
            "security": [],
            "dependencies": [],
            "code_quality": [],
            "performance": [],
            "compliance": [],
            "summary": {}
        }
    
    def deep_scan(self) -> Dict:
        """
        執行多層次深度掃描
        
        Returns:
            包含所有掃描結果的字典，包括安全、依賴、質量、性能和合規性等類別
        """
        print("🔍 開始高階深度掃描...")
        
        # 1. 安全掃描
        print("\n🛡️ 執行安全掃描...")
        self.scan_results["security"] = self._security_scan()
        
        # 2. 依賴掃描
        print("\n📦 執行依賴掃描...")
        self.scan_results["dependencies"] = self._dependency_scan()
        
        # 3. 代碼質量掃描
        print("\n⭐ 執行代碼質量掃描...")
        self.scan_results["code_quality"] = self._quality_scan()
        
        # 4. 性能掃描
        print("\n⚡ 執行性能掃描...")
        self.scan_results["performance"] = self._performance_scan()
        
        # 5. 合規性掃描
        print("\n✅ 執行合規性掃描...")
        self.scan_results["compliance"] = self._compliance_scan()
        
        # 6. 生成摘要
        self._generate_summary()
        
        # 7. 保存結果
        self._save_results()
        
        print("\n✅ 掃描完成!")
        return self.scan_results
    
    def _security_scan(self) -> List[Dict]:
        """安全漏洞掃描"""
        findings = []
        
        # Python 安全掃描 (Bandit)
        bandit_output_path = None
        try:
            print("  - 執行 Bandit 掃描...")
            # 使用臨時文件來存儲 Bandit 輸出
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
                bandit_output_path = tmp_file.name
            
            result = subprocess.run(
                ["bandit", "-r", str(self.repo_path), "-f", "json", "-o", bandit_output_path],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if os.path.exists(bandit_output_path):
                with open(bandit_output_path) as f:
                    bandit_data = json.load(f)
                
                for issue in bandit_data.get("results", []):
                    findings.append({
                        "severity": self._map_severity(issue.get("issue_severity")),
                        "type": issue.get("issue_text"),
                        "location": f"{issue.get('filename')}:{issue.get('line_number')}",
                        "file_path": issue.get("filename"),
                        "line_number": issue.get("line_number"),
                        "code_snippet": issue.get("code", ""),
                        "cwe_id": str(issue.get("test_id", "Unknown")),
                        "description": issue.get("issue_text"),
                        "recommendation": f"參考 CWE-{issue.get('test_id')} 修復建議",
                        "tool": "bandit",
                        "confidence": issue.get("issue_confidence", "Medium")
                    })
        except Exception as e:
            print(f"  ⚠️ Bandit 掃描失敗: {e}")
        finally:
            # 確保臨時文件總是被清理
            if bandit_output_path and os.path.exists(bandit_output_path):
                try:
                    os.unlink(bandit_output_path)
                except Exception:
                    pass  # 忽略清理錯誤
        
        
        # 自定義安全規則檢查
        print("  - 執行自定義安全規則...")
        findings.extend(self._custom_security_rules())
        
        return findings
    
    def _custom_security_rules(self) -> List[Dict]:
        """自定義安全規則檢查"""
        findings = []
        
        # 檢查硬編碼密碼
        patterns = {
            "password": ["password", "passwd", "pwd"],
            "api_key": ["api_key", "apikey", "api-key"],
            "secret": ["secret", "private_key", "private-key"],
            "token": ["token", "access_token", "auth_token"]
        }
        
        python_files = list(self.repo_path.rglob("*.py"))
        
        for file_path in python_files:
            # 跳過測試/示例代碼文件
            if any(marker in str(file_path).lower() for marker in ['test', 'example', 'demo', 'sample']):
                continue
            
            try:
                # 跳過測試/示例代碼文件（移到外層以提高效能）
                if any(marker in str(file_path).lower() for marker in ['test', 'example', 'demo', 'sample']):
                    continue
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line_num, line in enumerate(lines, 1):
                    line_lower = line.lower()
                    line_stripped = line.strip()
                    
                    # 跳過註釋
                    if line_stripped.startswith("#"):
                        continue
                    
                    # 檢查硬編碼憑證
                    for key_type, keywords in patterns.items():
                        for keyword in keywords:
                            # 檢查變量賦值或字典鍵
                            if (f"{keyword} = " in line_lower or f'"{keyword}": ' in line_lower or 
                                f"'{keyword}': " in line_lower or f"{keyword}=" in line_lower):
                                # 確保是字符串賦值（有引號），而不是變量引用或函數調用
                                if '=' in line:
                                    # 查找等號後的內容
                                    after_equals = line.split('=', 1)[1]
                                    # 檢查是否為非空字符串字面量（不是 None, '', "", 變量名等）
                                    if any(pattern in after_equals for pattern in ['"', "'"]):
                                        # 排除明顯的佔位符和測試值
                                        exclude_patterns = [
                                            'your_', 'example', 'test', 'dummy', 'fake', 'placeholder',
                                            'xxx', '***', 'TODO', 'FIXME', 'changeme', 'sample'
                                        ]
                                        if any(excl.lower() in after_equals.lower() for excl in exclude_patterns):
                                            continue
                                        
                                        # 排除空字符串或明顯的環境變量引用
                                        if ('""' in after_equals or "''" in after_equals or 
                                            'os.environ' in after_equals or 'getenv' in after_equals):
                                            continue
                                        
                                # 查找等號後的內容
                                after_equals = line.split('=', 1)[1] if '=' in line else ''
                                # 檢查是否為非空字符串字面量（不是 None, '', "", 變量名等）
                                if any(pattern in after_equals for pattern in ['"', "'"]):
                                    # 排除明顯的佔位符和測試值
                                    exclude_patterns = [
                                        'your_', 'example', 'test', 'dummy', 'fake', 'placeholder',
                                        'xxx', '***', 'TODO', 'FIXME', 'changeme', 'sample'
                                    ]
                                    if any(excl.lower() in after_equals.lower() for excl in exclude_patterns):
                                        continue
                                    
                                    # 排除空字符串或明顯的環境變量引用
                                    if ('""' in after_equals or "''" in after_equals or 
                                        'os.environ' in after_equals or 'getenv' in after_equals):
                                        continue
                                    
                                    findings.append({
                                        "severity": "high",
                                        "type": "Hardcoded Credential",
                                        "location": f"{file_path}:{line_num}",
                                        "file_path": str(file_path),
                                        "line_number": line_num,
                                        "code_snippet": line.strip(),
                                        "cwe_id": "CWE-798",
                                        "description": f"檢測到可能的硬編碼 {key_type}",
                                        "recommendation": "使用環境變量或密鑰管理服務存儲敏感信息",
                                        "tool": "custom",
                                        "confidence": 0.7
                                    })
                            if f"{keyword} = " in line_lower or f'"{keyword}": ' in line_lower:
                                if '=' in line and any(c in line for c in ['"', "'"]):
                                    if not line.strip().startswith("#"):
                                        findings.append({
                                            "severity": "high",
                                            "type": "Hardcoded Credential",
                                            "location": f"{file_path}:{line_num}",
                                            "file_path": str(file_path),
                                            "line_number": line_num,
                                            "code_snippet": line.strip(),
                                            "cwe_id": "CWE-798",
                                            "description": f"檢測到可能的硬編碼 {key_type}",
                                            "recommendation": "使用環境變量或密鑰管理服務存儲敏感信息",
                                            "tool": "custom",
                                            "confidence": 0.7
                                        })
                                # 查找等號後的內容
                                after_equals = line.split('=', 1)[1] if '=' in line else ''
                                # 檢查是否為非空字符串字面量（不是 None, '', "", 變量名等）
                                if any(pattern in after_equals for pattern in ['"', "'"]):
                                    # 排除明顯的佔位符和測試值
                                    exclude_patterns = [
                                        'your_', 'example', 'test', 'dummy', 'fake', 'placeholder',
                                        'xxx', '***', 'TODO', 'FIXME', 'changeme', 'sample'
                                    ]
                                    if any(excl.lower() in after_equals.lower() for excl in exclude_patterns):
                                        continue
                                    
                                    # 排除空字符串或明顯的環境變量引用
                                    if ('""' in after_equals or "''" in after_equals or 
                                        'os.environ' in after_equals or 'getenv' in after_equals):
                                        continue
                                    
                                    findings.append({
                                        "severity": "high",
                                        "type": "Hardcoded Credential",
                                        "location": f"{file_path}:{line_num}",
                                        "file_path": str(file_path),
                                        "line_number": line_num,
                                        "code_snippet": line.strip(),
                                        "cwe_id": "CWE-798",
                                        "description": f"檢測到可能的硬編碼 {key_type}",
                                        "recommendation": "使用環境變量或密鑰管理服務存儲敏感信息",
                                        "tool": "custom",
                                        "confidence": 0.7
                                    })
            
            except Exception as e:
                continue
        
        return findings
    
    def _dependency_scan(self) -> List[Dict]:
        """依賴項掃描"""
        findings = []
        
        # 檢查 requirements.txt
        req_files = list(self.repo_path.rglob("requirements*.txt"))
        
        for req_file in req_files:
            try:
                with open(req_file, 'r') as f:
                    requirements = f.readlines()
                
                for line_num, line in enumerate(requirements, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # 檢查未固定版本
                    if not any(c in line for c in ['==', '>=', '<=', '~=', '===']):
                        findings.append({
                            "severity": "medium",
                            "type": "Unpinned Dependency Version",
                            "location": f"{req_file}:{line_num}",
                            "file_path": str(req_file),
                            "line_number": line_num,
                            "code_snippet": line,
                            "cwe_id": "CWE-1390",
                            "description": f"依賴 {line} 沒有固定版本號",
                            "recommendation": "固定依賴版本號以確保可重複性",
                            "tool": "dependency",
                            "confidence": 0.9
                        })
            
            except Exception as e:
                continue
        
        return findings
    
    def _quality_scan(self) -> List[Dict]:
        """代碼質量掃描"""
        findings = []
        
        # 檢查大文件
        for file_path in self.repo_path.rglob("*.py"):
            try:
                file_size = file_path.stat().st_size
                if file_size > 50000:  # 50KB
                    findings.append({
                        "severity": "low",
                        "type": "Large File",
                        "location": str(file_path),
                        "file_path": str(file_path),
                        "line_number": 1,
                        "code_snippet": f"文件大小: {file_size} bytes",
                        "cwe_id": "N/A",
                        "description": "文件過大，建議拆分",
                        "recommendation": "將大型文件拆分為多個模塊",
                        "tool": "quality",
                        "confidence": 1.0
                    })
            
            except Exception:
                continue
        
        # 檢查過長函數
        for file_path in self.repo_path.rglob("*.py"):
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                
                for line_num, line in enumerate(lines, 1):
                    if len(line) > 120:
                        findings.append({
                            "severity": "low",
                            "type": "Long Line",
                            "location": f"{file_path}:{line_num}",
                            "file_path": str(file_path),
                            "line_number": line_num,
                            "code_snippet": line.strip()[:80] + "...",
                            "cwe_id": "N/A",
                            "description": f"行長度 {len(line)} 字符超過 120",
                            "recommendation": "將長行拆分為多行",
                            "tool": "quality",
                            "confidence": 1.0
                        })
            
            except Exception:
                continue
        
        return findings
    
    def _performance_scan(self) -> List[Dict]:
        """性能掃描"""
        findings = []
        
        # 檢查潛在性能問題
        for file_path in self.repo_path.rglob("*.py"):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # 檢查全局變量
                if "global " in content:
                    findings.append({
                        "severity": "low",
                        "type": "Global Variable Usage",
                        "location": str(file_path),
                        "file_path": str(file_path),
                        "line_number": 1,
                        "code_snippet": "global keyword detected",
                        "cwe_id": "N/A",
                        "description": "檢測到全局變量使用",
                        "recommendation": "避免使用全局變量，使用類或函數參數代替",
                        "tool": "performance",
                        "confidence": 0.6
                    })
            
            except Exception:
                continue
        
        return findings
    
    def _compliance_scan(self) -> List[Dict]:
        """合規性掃描"""
        findings = []
        
        # 檢查 README 存在
        if not (self.repo_path / "README.md").exists():
            findings.append({
                "severity": "low",
                "type": "Missing Documentation",
                "location": "repository root",
                "file_path": "README.md",
                "line_number": 1,
                "code_snippet": "N/A",
                "cwe_id": "N/A",
                "description": "缺少 README.md 文件",
                "recommendation": "添加 README.md 文件說明項目用途",
                "tool": "compliance",
                "confidence": 1.0
            })
        
        # 檢查 LICENSE
        if not (self.repo_path / "LICENSE").exists():
            findings.append({
                "severity": "medium",
                "type": "Missing License",
                "location": "repository root",
                "file_path": "LICENSE",
                "line_number": 1,
                "code_snippet": "N/A",
                "cwe_id": "N/A",
                "description": "缺少 LICENSE 文件",
                "recommendation": "添加適當的開源許可證",
                "tool": "compliance",
                "confidence": 1.0
            })
        
        return findings
    
    def _map_severity(self, severity: str) -> str:
        """映射嚴重性級別"""
        mapping = {
            "HIGH": "critical",
            "MEDIUM": "high",
            "LOW": "medium"
        }
        return mapping.get(severity.upper(), "low")
    
    def _generate_summary(self):
        """生成掃描摘要"""
        all_findings = (
            self.scan_results["security"] +
            self.scan_results["dependencies"] +
            self.scan_results["code_quality"] +
            self.scan_results["performance"] +
            self.scan_results["compliance"]
        )
        
        severity_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for finding in all_findings:
            severity = finding.get("severity", "low").lower()
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        self.scan_results["summary"] = {
            "total_findings": len(all_findings),
            "critical": severity_counts["critical"],
            "high": severity_counts["high"],
            "medium": severity_counts["medium"],
            "low": severity_counts["low"],
            "findings_by_category": {
                "security": len(self.scan_results["security"]),
                "dependencies": len(self.scan_results["dependencies"]),
                "code_quality": len(self.scan_results["code_quality"]),
                "performance": len(self.scan_results["performance"]),
                "compliance": len(self.scan_results["compliance"])
            }
        }
    
    def _save_results(self):
        """保存掃描結果"""
        output_file = self.output_dir / f"scan-results-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        
        with open(output_file, 'w') as f:
            json.dump(self.scan_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 掃描結果已保存至: {output_file}")
        print(f"\n📈 掃描摘要:")
        print(f"  - 總計發現: {self.scan_results['summary']['total_findings']} 個問題")
        print(f"  - 嚴重: {self.scan_results['summary']['critical']} 個")
        print(f"  - 高: {self.scan_results['summary']['high']} 個")
        print(f"  - 中: {self.scan_results['summary']['medium']} 個")
        print(f"  - 低: {self.scan_results['summary']['low']} 個")

def main() -> None:
    """
    主執行函數
    
    從命令行參數讀取儲存庫路徑並執行掃描。
    如果發現嚴重或高嚴重性問題，將以非零狀態碼退出。
    """
    if len(sys.argv) > 1:
        repo_path = sys.argv[1]
    else:
        repo_path = "."
    import argparse
    
    parser = argparse.ArgumentParser(description='高階深度代碼掃描工具')
    parser.add_argument('--repo', default='.', help='待掃描的儲存庫路徑')
    parser.add_argument('--output-dir', default='.github/code-scanning/reports', 
                        help='掃描報告輸出目錄')
    parser.add_argument('repo_path', nargs='?', default=None,
                        help='待掃描的儲存庫路徑（位置參數，與 --repo 擇一使用）')
    
    args = parser.parse_args()
    
    # 優先使用命名參數，如果沒有則使用位置參數
    repo_path = args.repo if args.repo_path is None else args.repo_path
    # 優先使用位置參數，如果沒有則使用命名參數
    repo_path = args.repo_path if args.repo_path is not None else args.repo
    output_dir = args.output_dir
    
    scanner = AdvancedCodeScanner(repo_path)
    results = scanner.deep_scan()
    
    # 返回適當的退出代碼
    if results["summary"]["critical"] > 0 or results["summary"]["high"] > 0:
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()