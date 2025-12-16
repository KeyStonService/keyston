#!/usr/bin/env python3
"""
清理重複腳本
Removes duplicate scripts based on analysis
"""

import os
import hashlib
from pathlib import Path
from collections import defaultdict

class DuplicatesCleaner:
    """重複文件清理器"""

    def __init__(self, repo_root: Path, dry_run: bool = True):
        self.repo_root = repo_root
        self.dry_run = dry_run
        self.removed_count = 0

    def cleanup(self):
        """執行清理"""
        print(f"{'🔍 模擬清理' if self.dry_run else '🗑️  開始清理'}重複文件...\n")

        # 1. 清理 legacy/ 目錄的重複
        self._cleanup_legacy_duplicates()

        # 2. 清理 agent/ vs services/agents/ 重複
        self._cleanup_agent_duplicates()

        # 3. 清理空 __init__.py 重複
        self._cleanup_empty_init_files()

        print(f"\n{'✅ 模擬清理完成' if self.dry_run else '✅ 清理完成'}")
        print(f"   移除文件數: {self.removed_count}")

    def _cleanup_legacy_duplicates(self):
        """清理 legacy/ 目錄中的重複文件"""
        print("1️⃣  清理 legacy/ 目錄重複...")

        legacy_dir = self.repo_root / "legacy"
        if not legacy_dir.exists():
            print("   ℹ️  legacy/ 目錄不存在")
            return

        # 收集所有 legacy/ 下的文件
        for file_path in legacy_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix in {'.py', '.sh', '.js', '.ts'}:
                # 檢查是否在根目錄也存在
                rel_path = file_path.relative_to(legacy_dir)
                root_file = self.repo_root / rel_path

                if root_file.exists() and self._files_identical(file_path, root_file):
                    self._remove_file(file_path, f"重複於 {rel_path}")

    def _cleanup_agent_duplicates(self):
        """清理 agent/ 和 services/agents/ 之間的重複"""
        print("\n2️⃣  清理 agent/ vs services/agents/ 重複...")

        agent_dir = self.repo_root / "agent"
        services_agent_dir = self.repo_root / "services" / "agents"

        if not agent_dir.exists() or not services_agent_dir.exists():
            print("   ℹ️  目錄不完整，跳過")
            return

        # 檢查相同路徑的文件
        for agent_file in agent_dir.rglob("*"):
            if agent_file.is_file():
                rel_path = agent_file.relative_to(agent_dir)
                services_file = services_agent_dir / rel_path

                if services_file.exists() and self._files_identical(agent_file, services_file):
                    # 保留 services/agents/ 版本，移除 agent/ 版本
                    self._remove_file(agent_file, f"重複於 services/agents/{rel_path}")

    def _cleanup_empty_init_files(self):
        """清理空的 __init__.py 文件重複"""
        print("\n3️⃣  清理空 __init__.py 重複...")

        empty_init_hash = hashlib.md5(b'').hexdigest()  # 空文件哈希
        init_files = list(self.repo_root.rglob("__init__.py"))

        # 按目錄分組
        by_dir = defaultdict(list)
        for init_file in init_files:
            if self._hash_file(init_file) == empty_init_hash:
                by_dir[init_file.parent].append(init_file)

        # 每個目錄只保留一個空 __init__.py
        for directory, files in by_dir.items():
            if len(files) > 1:
                # 這種情況不應該發生（一個目錄不能有多個 __init__.py）
                # 但如果發生了，記錄警告
                print(f"   ⚠️  {directory} 有多個 __init__.py")

    def _files_identical(self, file1: Path, file2: Path) -> bool:
        """檢查兩個文件是否完全相同"""
        return self._hash_file(file1) == self._hash_file(file2)

    def _hash_file(self, file_path: Path) -> str:
        """計算文件哈希"""
        try:
            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                hasher.update(f.read())
            return hasher.hexdigest()
        except:
            return ""

    def _remove_file(self, file_path: Path, reason: str):
        """移除文件"""
        rel_path = file_path.relative_to(self.repo_root)

        if self.dry_run:
            print(f"   [模擬] 移除 {rel_path}")
            print(f"          原因: {reason}")
        else:
            try:
                file_path.unlink()
                print(f"   ✓ 移除 {rel_path}")
                self.removed_count += 1
            except Exception as e:
                print(f"   ✗ 移除失敗 {rel_path}: {e}")

def main():
    import sys
    repo_root = Path(__file__).parent.parent

    # 檢查是否為實際執行模式
    dry_run = "--execute" not in sys.argv

    if not dry_run:
        response = input("⚠️  這將實際刪除文件！確定繼續嗎？ (yes/no): ")
        if response.lower() != "yes":
            print("❌ 已取消")
            return

    cleaner = DuplicatesCleaner(repo_root, dry_run=dry_run)
    cleaner.cleanup()

    if dry_run:
        print("\n💡 提示: 使用 --execute 參數來實際執行清理")

if __name__ == "__main__":
    main()
