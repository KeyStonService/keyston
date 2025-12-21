#!/usr/bin/env python3
"""
DIRECTORY.md 驗證工具

此工具驗證 DIRECTORY.md 文檔的完整性、準確性和質量。
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
import json

# SECTION_GROUPS: 每組代表一個必填的「章節類別」，組內採 OR 檢查 (alternative headings per required category)
SECTION_GROUPS = [
    ['## 為什麼會來這裡 / 入口', '## 目錄職責'],
    ['## 推薦閱讀路線', '## 設計原則'],
    ['## 輸入 / 輸出（直覺版）'],
    ['## 變更影響範圍（Blast radius）', '## 職責分離說明'],
    ['## 檔案速覽（人話版）', '## 檔案說明'],
    ['## 待釐清 / TODO'],
    ['## 未來可轉 JSON 的錨點']
]

MIN_SECTION_CONTENT_LENGTH = 50
OLD_FIELDS = ['**職責**', '**功能**', '**依賴**']
NEW_FIELDS = [
    ('**一句話摘要**', '一句話摘要'),
    ('**我不確定/待釐清**', '待釐清欄位'),
    ('**相關連結**', '相關連結欄位')
]
MISSING_SECTION_GROUP_MSG = "缺少必要章節組: {options}"


class DirectoryDocValidator:
    """DIRECTORY.md 文檔驗證器"""
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.section_groups = SECTION_GROUPS
        self.validation_results = []
    
    def validate_file(self, doc_path: Path) -> Dict:
        """驗證單個 DIRECTORY.md 文件"""
        result = {
            'path': str(doc_path.relative_to(self.root_path)),
            'exists': doc_path.exists(),
            'errors': [],
            'warnings': [],
            'score': 0
        }
        
        if not doc_path.exists():
            result['errors'].append('文件不存在')
            return result
        
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 檢查必要章節
            self.check_required_sections(content, result)
            
            # 檢查標題格式
            self.check_title_format(content, result)
            
            # 檢查檔案說明格式
            self.check_file_descriptions(content, result, doc_path.parent)
            
            # 檢查內容完整性
            self.check_content_completeness(content, result)
            
            # 檢查 Markdown 格式
            self.check_markdown_format(content, result)
            
            # 計算質量分數
            result['score'] = self.calculate_score(result)
            
        except Exception as e:
            result['errors'].append(f'讀取文件失敗: {str(e)}')
        
        return result
    
    def check_required_sections(self, content: str, result: Dict):
        """檢查必要章節"""
        for group in self.section_groups:
            if not any(section in content for section in group):
                result['errors'].append(MISSING_SECTION_GROUP_MSG.format(options=' 或 '.join(group)))
    
    def check_title_format(self, content: str, result: Dict):
        """檢查標題格式"""
        lines = content.split('\n')
        
        # 檢查第一行是否為一級標題
        if not lines[0].startswith('# '):
            result['errors'].append('第一行應該是一級標題 (# 目錄名稱)')
        
        # 檢查標題層級
        title_pattern = re.compile(r'^(#{1,6})\s+(.+)$')
        prev_level = 0
        
        for i, line in enumerate(lines, 1):
            match = title_pattern.match(line)
            if match:
                level = len(match.group(1))
                title = match.group(2)
                
                # 檢查標題層級跳躍
                if level > prev_level + 1:
                    result['warnings'].append(
                        f'第 {i} 行: 標題層級跳躍 (從 {prev_level} 跳到 {level})'
                    )
                
                # 檢查標題是否為空
                if not title.strip():
                    result['errors'].append(f'第 {i} 行: 標題內容為空')
                
                prev_level = level
    
    def check_file_descriptions(self, content: str, result: Dict, dir_path: Path):
        """檢查檔案說明格式"""
        # 提取檔案說明章節
        file_section_match = re.search(
            r'(## 檔案說明|## 檔案速覽（人話版）)\s*\n(.*?)(?=\n## |$)',
            content,
            re.DOTALL
        )
        
        if not file_section_match:
            result['errors'].append('找不到檔案說明章節')
            return
        
        file_section = file_section_match.group(2)
        
        # 檢查每個檔案是否有完整的說明
        file_entries = re.findall(r'### (.+?)\n', file_section)
        
        for file_name in file_entries:
            # 檢查是否有職責、功能、依賴三項
            file_desc_pattern = re.compile(
                rf'### {re.escape(file_name)}\s*\n'
                r'(.*?)(?=\n### |\n## |$)',
                re.DOTALL
            )
            
            match = file_desc_pattern.search(file_section)
            if match:
                desc = match.group(1)
                
                has_old_fields = any(field in desc for field in OLD_FIELDS)
                has_new_fields = any(field in desc for field, _ in NEW_FIELDS)

                if not (has_old_fields or has_new_fields):
                    result['warnings'].append(f'檔案 {file_name} 缺少基本說明欄位')

                if has_old_fields:
                    for field in OLD_FIELDS:
                        if field not in desc:
                            result['warnings'].append(f'檔案 {file_name} 缺少{field.strip("*")}說明')

                if has_new_fields:
                    for field, label in NEW_FIELDS:
                        if field not in desc:
                            result['warnings'].append(f'檔案 {file_name} 缺少{label}')
                
                # 檢查是否有待補充標記
                if '[待補充' in desc:
                    result['warnings'].append(f'檔案 {file_name} 有待補充內容')
        
        # 檢查實際目錄中的檔案是否都有說明
        try:
            actual_files = [
                f.name for f in dir_path.iterdir() 
                if f.is_file() and f.name != 'DIRECTORY.md' and not f.name.startswith('.')
            ]
            
            documented_files = set(file_entries)
            actual_files_set = set(actual_files)
            
            missing = actual_files_set - documented_files
            extra = documented_files - actual_files_set
            
            if missing:
                result['warnings'].append(
                    f'以下檔案未在文檔中說明: {", ".join(missing)}'
                )
            
            if extra:
                result['warnings'].append(
                    f'文檔中說明了不存在的檔案: {", ".join(extra)}'
                )
        except Exception as e:
            result['warnings'].append(f'無法檢查實際檔案: {str(e)}')
    
    def check_content_completeness(self, content: str, result: Dict):
        """檢查內容完整性"""
        # 檢查是否有待補充標記
        todo_pattern = re.compile(r'\[待補充[：:][^\]]*\]')
        todos = todo_pattern.findall(content)
        
        if todos:
            result['warnings'].append(f'發現 {len(todos)} 處待補充內容')
        
        # 檢查章節是否為空
        for group in self.section_groups:
            for section in group:
                section_pattern = re.compile(
                    rf'{re.escape(section)}\s*\n(.*?)(?=\n## |$)',
                    re.DOTALL
                )
                match = section_pattern.search(content)
                
                if match:
                    section_content = match.group(1).strip()
                    if not section_content or len(section_content) < MIN_SECTION_CONTENT_LENGTH:
                        result['warnings'].append(f'章節 {section} 內容過少或為空')
    
    def check_markdown_format(self, content: str, result: Dict):
        """檢查 Markdown 格式"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # 檢查列表格式
            if line.strip().startswith('-') or line.strip().startswith('*'):
                if not line.startswith('  ') and not line.startswith('- ') and not line.startswith('* '):
                    if i > 1 and lines[i-2].strip():  # 不是第一行且前一行不為空
                        result['warnings'].append(f'第 {i} 行: 列表格式可能不正確')
            
            # 檢查代碼塊
            if line.strip().startswith('```'):
                # 檢查是否有語言標識
                if line.strip() == '```':
                    result['warnings'].append(f'第 {i} 行: 代碼塊缺少語言標識')
    
    def calculate_score(self, result: Dict) -> int:
        """計算質量分數 (0-100)"""
        score = 100
        
        # 錯誤扣分
        score -= len(result['errors']) * 10
        
        # 警告扣分
        score -= len(result['warnings']) * 2
        
        return max(0, min(100, score))
    
    def validate_all(self) -> List[Dict]:
        """驗證所有 DIRECTORY.md 文件"""
        results = []
        
        for root, dirs, files in os.walk(self.root_path):
            if 'DIRECTORY.md' in files:
                doc_path = Path(root) / 'DIRECTORY.md'
                result = self.validate_file(doc_path)
                results.append(result)
        
        return results
    
    def generate_report(self, results: List[Dict]) -> str:
        """生成驗證報告"""
        total = len(results)
        passed = sum(1 for r in results if r['score'] >= 90)
        warnings = sum(1 for r in results if 70 <= r['score'] < 90)
        failed = sum(1 for r in results if r['score'] < 70)
        
        avg_score = sum(r['score'] for r in results) / total if total > 0 else 0
        
        report = f"""
# DIRECTORY.md 驗證報告

## 總體統計
- 總文檔數: {total}
- 優秀 (≥90分): {passed} ({passed/total*100:.1f}%)
- 良好 (70-89分): {warnings} ({warnings/total*100:.1f}%)
- 需改進 (<70分): {failed} ({failed/total*100:.1f}%)
- 平均分數: {avg_score:.1f}/100

## 詳細結果

### ✅ 優秀文檔 (≥90分)
"""
        
        for r in sorted(results, key=lambda x: x['score'], reverse=True):
            if r['score'] >= 90:
                report += f"- {r['path']} ({r['score']}分)\n"
        
        report += "\n### ⚠️  良好文檔 (70-89分)\n"
        for r in sorted(results, key=lambda x: x['score'], reverse=True):
            if 70 <= r['score'] < 90:
                report += f"- {r['path']} ({r['score']}分)\n"
                if r['warnings']:
                    for warning in r['warnings'][:3]:  # 只顯示前3個警告
                        report += f"  - ⚠️  {warning}\n"
        
        report += "\n### ❌ 需改進文檔 (<70分)\n"
        for r in sorted(results, key=lambda x: x['score']):
            if r['score'] < 70:
                report += f"- {r['path']} ({r['score']}分)\n"
                if r['errors']:
                    for error in r['errors']:
                        report += f"  - ❌ {error}\n"
                if r['warnings']:
                    for warning in r['warnings'][:3]:
                        report += f"  - ⚠️  {warning}\n"
        
        report += "\n## 改進建議\n\n"
        
        # 統計常見問題
        all_errors = []
        all_warnings = []
        for r in results:
            all_errors.extend(r['errors'])
            all_warnings.extend(r['warnings'])
        
        if all_errors:
            report += "### 常見錯誤\n"
            error_counts = {}
            for error in all_errors:
                error_counts[error] = error_counts.get(error, 0) + 1
            
            for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                report += f"- {error} ({count}次)\n"
        
        if all_warnings:
            report += "\n### 常見警告\n"
            warning_counts = {}
            for warning in all_warnings:
                warning_counts[warning] = warning_counts.get(warning, 0) + 1
            
            for warning, count in sorted(warning_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                report += f"- {warning} ({count}次)\n"
        
        return report


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='DIRECTORY.md 驗證工具')
    parser.add_argument('path', nargs='?', default='.', help='要驗證的根目錄路徑')
    parser.add_argument('--report', '-r', type=str, help='生成報告文件路徑')
    parser.add_argument('--json', '-j', type=str, help='生成 JSON 格式報告')
    parser.add_argument('--min-score', type=int, default=0, help='最低分數閾值')
    
    args = parser.parse_args()
    
    validator = DirectoryDocValidator(args.path)
    
    print(f"🔍 驗證目錄: {args.path}")
    print("-" * 60)
    
    results = validator.validate_all()
    
    report = validator.generate_report(results)
    print(report)
    
    if args.report:
        with open(args.report, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n📄 報告已保存到: {args.report}")
    
    if args.json:
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n📄 JSON 報告已保存到: {args.json}")
    
    # 檢查是否有文檔低於最低分數
    low_score_docs = [r for r in results if r['score'] < args.min_score]
    if low_score_docs:
        print(f"\n❌ {len(low_score_docs)} 個文檔低於最低分數 {args.min_score}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
