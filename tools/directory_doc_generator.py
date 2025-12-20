#!/usr/bin/env python3
"""
DIRECTORY.md 自動生成工具

此工具自動掃描目錄結構，分析文件內容，並生成初始的 DIRECTORY.md 文檔。
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Set
import json

# 導覽優先模板：聚焦入口、任務、影響範圍與可轉換錨點
NAV_TEMPLATE = """# {directory_name}

## 為什麼會來這裡 / 入口
- **位置**: `{directory_path}`
- **我在這裡通常要解決什麼**： [待補充]
- **首選入口**： [待補充：README、主要檔案或子目錄]
- **常見任務**：
  - [待補充：任務1]
  - [待補充：任務2]
- **子目錄速覽**：
{subdir_list}

## 推薦閱讀路線
1. [待補充：第一個要看的檔案/README]
2. [待補充：第二個步驟或檔案]
3. [待補充：第三個步驟或檔案]

## 輸入 / 輸出（直覺版）
- **輸入**：[待補充：會依賴哪些配置/資料]
- **輸出**：[待補充：會產出哪些工件/結果]
- **主要上下游/協作者**：[待補充：關聯的模組或團隊]

## 變更影響範圍（Blast radius）
- [待補充：改動這裡通常會影響到哪些模組或流程]

## 檔案速覽（人話版）
{file_list}

## 待釐清 / TODO
- [待補充：目前不確定的部分或需要補資料]
- [待補充]

## 未來可轉 JSON 的錨點
- **path**: `{directory_path}`
- **entrypoints**: [待補充：關鍵檔案或子目錄名稱]
- **status**: draft

---

*此文檔由 directory_doc_generator.py 自動生成，請根據實際情況補充和完善內容。*
"""
NO_FILES_TEXT = "（此目錄暫無文件）"
NO_SUBDIR_TEXT = "  - （此層沒有子目錄）"
UNSURE_PLACEHOLDER = "[待補充]"
RELATED_PLACEHOLDER = "[待補充]"

class DirectoryDocGenerator:
    """DIRECTORY.md 文檔生成器"""
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.exclude_dirs = {
            '.git', '.github-private', '__pycache__', 'node_modules', 
            '.pytest_cache', '.mypy_cache', 'dist', 'build', 
            '*.egg-info', '.venv', 'venv', '.DS_Store'
        }
        self.exclude_files = {
            '.gitignore', '.gitkeep', '__init__.py', 
            '.DS_Store', 'Thumbs.db'
        }
    
    def should_exclude(self, path: Path) -> bool:
        """判斷是否應該排除此路徑"""
        name = path.name
        return any(
            name == exclude or name.startswith(exclude.rstrip('*'))
            for exclude in self.exclude_dirs
        )
    
    def scan_directory(self, dir_path: Path) -> Dict:
        """掃描目錄並收集信息"""
        if not dir_path.is_dir():
            return None
        
        info = {
            'path': str(dir_path.relative_to(self.root_path)),
            'name': dir_path.name,
            'files': [],
            'subdirs': [],
            'has_directory_md': (dir_path / 'DIRECTORY.md').exists()
        }
        
        try:
            for item in sorted(dir_path.iterdir()):
                if self.should_exclude(item):
                    continue
                
                if item.is_file() and item.name not in self.exclude_files:
                    file_info = self.analyze_file(item)
                    info['files'].append(file_info)
                elif item.is_dir():
                    info['subdirs'].append(item.name)
        except PermissionError:
            print(f"⚠️  無法訪問目錄: {dir_path}")
        
        return info
    
    def analyze_file(self, file_path: Path) -> Dict:
        """分析文件並提取信息"""
        file_info = {
            'name': file_path.name,
            'extension': file_path.suffix,
            'size': file_path.stat().st_size,
            'type': self.determine_file_type(file_path)
        }
        
        # 嘗試讀取文件的前幾行來推斷用途
        try:
            if file_path.suffix in ['.py', '.js', '.ts', '.go', '.rs']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = [f.readline() for _ in range(10)]
                    file_info['docstring'] = self.extract_docstring(lines, file_path.suffix)
        except Exception as e:
            file_info['docstring'] = None
        
        return file_info
    
    def determine_file_type(self, file_path: Path) -> str:
        """判斷文件類型"""
        ext = file_path.suffix.lower()
        name = file_path.name.lower()
        
        type_mapping = {
            '.py': 'Python 源代碼',
            '.js': 'JavaScript 源代碼',
            '.ts': 'TypeScript 源代碼',
            '.go': 'Go 源代碼',
            '.rs': 'Rust 源代碼',
            '.java': 'Java 源代碼',
            '.cpp': 'C++ 源代碼',
            '.c': 'C 源代碼',
            '.h': 'C/C++ 頭文件',
            '.md': 'Markdown 文檔',
            '.yaml': 'YAML 配置文件',
            '.yml': 'YAML 配置文件',
            '.json': 'JSON 配置文件',
            '.toml': 'TOML 配置文件',
            '.sh': 'Shell 腳本',
            '.bash': 'Bash 腳本',
            '.dockerfile': 'Dockerfile',
            '.sql': 'SQL 腳本',
            '.txt': '文本文件',
        }
        
        if 'dockerfile' in name:
            return 'Dockerfile'
        elif 'makefile' in name:
            return 'Makefile'
        elif 'requirements' in name:
            return 'Python 依賴文件'
        elif 'package.json' in name:
            return 'Node.js 包配置'
        
        return type_mapping.get(ext, '其他文件')
    
    def extract_docstring(self, lines: List[str], extension: str) -> str:
        """提取文件的文檔字符串"""
        if extension == '.py':
            # Python docstring
            for i, line in enumerate(lines):
                if '"""' in line or "'''" in line:
                    docstring = line.strip().strip('"""').strip("'''")
                    if docstring:
                        return docstring
        elif extension in ['.js', '.ts']:
            # JavaScript/TypeScript comment
            for line in lines:
                if line.strip().startswith('//'):
                    return line.strip().lstrip('//').strip()
                elif line.strip().startswith('/*'):
                    return line.strip().lstrip('/*').strip()
        
        return None
    
    def generate_directory_md(self, dir_info: Dict) -> str:
        """生成 DIRECTORY.md 內容"""
        template = self.get_navigation_template()
        return template.format(
            directory_name=dir_info['name'],
            directory_path=dir_info['path'],
            file_list=self.format_file_list(dir_info['files']),
            subdir_list=self.format_subdir_list(dir_info['subdirs'])
        )
    
    def format_file_list(self, files: List[Dict]) -> str:
        """格式化文件列表"""
        if not files:
            return NO_FILES_TEXT
        
        formatted = []
        for file in files:
            summary = self.build_file_summary(file)
            formatted.append(
                f"### {file['name']}\n"
                f"- **一句話摘要**：{summary}\n"
                f"- **我不確定/待釐清**：{UNSURE_PLACEHOLDER}\n"
                f"- **相關連結**：{RELATED_PLACEHOLDER}\n"
            )
        
        return "\n".join(formatted)
    
    def build_file_summary(self, file: Dict) -> str:
        """建構檔案摘要，優先提供類型與可用的 docstring"""
        docstring = file.get('docstring', '')
        file_type = file.get('type', '')
        return f"{file_type} - {docstring}" if docstring else file_type
    
    def format_subdir_list(self, subdirs: List[str]) -> str:
        """格式化子目錄列表"""
        if not subdirs:
            return NO_SUBDIR_TEXT
        
        return "\n".join(f"  - `{subdir}/`" for subdir in subdirs)
    
    def get_navigation_template(self) -> str:
        """導覽優先模板：聚焦入口、任務與影響範圍"""
        return NAV_TEMPLATE
    
    def process_directory(self, dir_path: Path, generate: bool = False) -> Dict:
        """處理單個目錄"""
        dir_info = self.scan_directory(dir_path)
        
        if dir_info and generate and not dir_info['has_directory_md']:
            content = self.generate_directory_md(dir_info)
            output_path = dir_path / 'DIRECTORY.md'
            
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ 已生成: {output_path}")
                dir_info['generated'] = True
            except Exception as e:
                print(f"❌ 生成失敗 {output_path}: {e}")
                dir_info['generated'] = False
        else:
            dir_info['generated'] = False
        
        return dir_info
    
    def scan_all_directories(self, generate: bool = False) -> List[Dict]:
        """掃描所有目錄"""
        results = []
        
        for root, dirs, files in os.walk(self.root_path):
            root_path = Path(root)
            
            # 排除特殊目錄
            dirs[:] = [d for d in dirs if not self.should_exclude(root_path / d)]
            
            dir_info = self.process_directory(root_path, generate)
            if dir_info:
                results.append(dir_info)
        
        return results
    
    def generate_report(self, results: List[Dict]) -> str:
        """生成掃描報告"""
        total = len(results)
        has_doc = sum(1 for r in results if r['has_directory_md'])
        generated = sum(1 for r in results if r.get('generated', False))
        
        report = f"""
# DIRECTORY.md 生成報告

## 統計信息
- 總目錄數: {total}
- 已有文檔: {has_doc} ({has_doc/total*100:.1f}%)
- 本次生成: {generated}
- 待完善: {total - has_doc}

## 詳細列表

### 已有文檔的目錄
"""
        
        for r in results:
            if r['has_directory_md']:
                report += f"- ✅ {r['path']}\n"
        
        report += "\n### 本次生成的目錄\n"
        for r in results:
            if r.get('generated', False):
                report += f"- 🆕 {r['path']}\n"
        
        report += "\n### 待生成的目錄\n"
        for r in results:
            if not r['has_directory_md'] and not r.get('generated', False):
                report += f"- ⏳ {r['path']}\n"
        
        return report


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='DIRECTORY.md 自動生成工具')
    parser.add_argument('path', nargs='?', default='.', help='要掃描的根目錄路徑')
    parser.add_argument('--generate', '-g', action='store_true', help='生成缺失的 DIRECTORY.md 文件')
    parser.add_argument('--report', '-r', type=str, help='生成報告文件路徑')
    
    args = parser.parse_args()
    
    generator = DirectoryDocGenerator(args.path)
    
    print(f"🔍 掃描目錄: {args.path}")
    print(f"{'🔧 生成模式' if args.generate else '📊 掃描模式'}")
    print("-" * 60)
    
    results = generator.scan_all_directories(generate=args.generate)
    
    report = generator.generate_report(results)
    print(report)
    
    if args.report:
        with open(args.report, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n📄 報告已保存到: {args.report}")


if __name__ == '__main__':
    main()
