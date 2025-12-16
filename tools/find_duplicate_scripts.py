#!/usr/bin/env python3
"""
查找並分析重複腳本
Finds and analyzes duplicate scripts across the repository
"""

import hashlib
import os
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set

class ScriptDuplicateFinder:
    """腳本重複查找器"""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.script_extensions = {'.py', '.sh', '.js', '.ts'}
        self.skip_dirs = {'node_modules', '.git', '__pycache__', '.venv', 'venv', 'dist', 'build'}

    def find_duplicates(self) -> Dict[str, List[str]]:
        """查找重複腳本（基於內容哈希）"""
        hash_to_files = defaultdict(list)

        # 收集所有腳本文件
        for file_path in self._iter_scripts():
            try:
                content_hash = self._hash_file(file_path)
                rel_path = str(file_path.relative_to(self.repo_root))
                hash_to_files[content_hash].append(rel_path)
            except Exception as e:
                print(f"⚠️  處理 {file_path} 失敗: {e}")

        # 過濾出真正的重複（>1個文件有相同哈希）
        duplicates = {h: files for h, files in hash_to_files.items() if len(files) > 1}
        return duplicates

    def find_similar_names(self) -> Dict[str, List[str]]:
        """查找名稱相似的腳本"""
        name_to_files = defaultdict(list)

        for file_path in self._iter_scripts():
            name = file_path.stem  # 文件名（不含擴展名）
            rel_path = str(file_path.relative_to(self.repo_root))
            name_to_files[name].append(rel_path)

        # 過濾出名稱重複
        similar = {name: files for name, files in name_to_files.items() if len(files) > 1}
        return similar

    def _iter_scripts(self):
        """遍歷所有腳本文件"""
        for root, dirs, files in os.walk(self.repo_root):
            # 過濾跳過的目錄
            dirs[:] = [d for d in dirs if d not in self.skip_dirs]

            for file in files:
                file_path = Path(root) / file
                if file_path.suffix in self.script_extensions:
                    yield file_path

    def _hash_file(self, file_path: Path) -> str:
        """計算文件的哈希值"""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            hasher.update(f.read())
        return hasher.hexdigest()

    def analyze_and_report(self):
        """分析並生成報告"""
        print("🔍 查找重複腳本...\n")

        # 1. 基於內容的完全重複
        content_duplicates = self.find_duplicates()
        print(f"📋 發現 {len(content_duplicates)} 組完全重複的腳本（內容相同）\n")

        if content_duplicates:
            print("完全重複的腳本組:")
            for i, (hash_val, files) in enumerate(content_duplicates.items(), 1):
                print(f"\n  組 {i} ({len(files)} 個文件, hash: {hash_val[:8]}...):")
                for file in files:
                    print(f"    - {file}")

        # 2. 基於名稱的相似腳本
        name_similar = self.find_similar_names()
        print(f"\n\n📝 發現 {len(name_similar)} 組名稱相同的腳本\n")

        if name_similar:
            print("名稱相同的腳本組 (前10組):")
            for i, (name, files) in enumerate(list(name_similar.items())[:10], 1):
                print(f"\n  名稱 '{name}' ({len(files)} 個文件):")
                for file in files:
                    print(f"    - {file}")

        # 3. 統計
        total_duplicate_files = sum(len(files) - 1 for files in content_duplicates.values())
        print(f"\n\n📊 統計:")
        print(f"  可移除的重複文件數: {total_duplicate_files}")
        print(f"  名稱衝突組數: {len(name_similar)}")

        return {
            "content_duplicates": len(content_duplicates),
            "removable_files": total_duplicate_files,
            "name_conflicts": len(name_similar),
        }

def main():
    repo_root = Path(__file__).parent.parent
    finder = ScriptDuplicateFinder(repo_root)
    stats = finder.analyze_and_report()

    print(f"\n✅ 分析完成！")
    if stats["removable_files"] > 0:
        print(f"\n💡 建議: 可以移除 {stats['removable_files']} 個重複文件來清理代碼庫")

if __name__ == "__main__":
    main()
