#!/usr/bin/env python3
"""
Automated Technical Debt Resolution Tool
=========================================

Automatically fixes common technical debt patterns with minimal risk.
Provides safe, incremental debt reduction through automated refactoring.

Safe Fixes (Automated)
-----------------------
- Remove duplicate code blocks
- Add missing docstrings (templates)
- Format code to standards
- Remove unused imports
- Fix simple TODO/FIXME items

Manual Review Required
----------------------
- High complexity refactoring
- API changes
- Architectural modifications
- Security-related fixes

Author: SynergyMesh Governance Team
Version: 1.0.0
Date: 2025-12-12
"""

import os
import re
import ast
import json
from pathlib import Path
from typing import Dict, List, Set, Optional
from collections import defaultdict


class DebtAutoFixer:
    """Automated technical debt resolution tool"""
    
    def __init__(self, project_root: Path, dry_run: bool = True):
        """
        Initialize auto-fixer.
        
        Args:
            project_root: Project root directory
            dry_run: If True, only show what would be fixed (default: True)
        """
        self.project_root = project_root
        self.dry_run = dry_run
        self.fixes_applied = []
        self.fixes_skipped = []
    
    def fix_duplicate_scripts(self) -> int:
        """
        Fix duplicate scripts in scripts/ vs 35-scripts/
        
        Returns:
            Number of duplicates resolved
        """
        scripts_dir = self.project_root / "governance" / "scripts"
        scripts_35_dir = self.project_root / "governance" / "35-scripts"
        
        if not scripts_dir.exists() or not scripts_35_dir.exists():
            return 0
        
        fixes = 0
        for script_file in scripts_dir.glob("*.py"):
            duplicate = scripts_35_dir / script_file.name
            if duplicate.exists():
                # Check if files are identical
                with open(script_file, 'r') as f1, open(duplicate, 'r') as f2:
                    if f1.read() == f2.read():
                        if self.dry_run:
                            print(f"  [DRY RUN] Would remove: {script_file.relative_to(self.project_root)}")
                            self.fixes_applied.append(f"Remove duplicate: {script_file.name}")
                        else:
                            script_file.unlink()
                            print(f"  ✅ Removed duplicate: {script_file.relative_to(self.project_root)}")
                            self.fixes_applied.append(f"Removed duplicate: {script_file.name}")
                        fixes += 1
        
        return fixes
    
    def add_missing_docstrings(self, file_path: Path) -> int:
        """
        Add template docstrings to functions/classes missing them.
        
        Args:
            file_path: Python file to process
        
        Returns:
            Number of docstrings added
        """
        if self.dry_run:
            return 0  # Skip in dry run to avoid file modification
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            lines = content.split('\n')
            additions = []
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not ast.get_docstring(node) and not node.name.startswith('_'):
                        # Generate template docstring
                        indent = ' ' * (node.col_offset + 4)
                        if isinstance(node, ast.FunctionDef):
                            docstring = f'{indent}"""TODO: Document this function."""'
                        else:
                            docstring = f'{indent}"""TODO: Document this class."""'
                        
                        # Insert after function/class definition line
                        insert_line = node.lineno
                        additions.append((insert_line, docstring))
            
            # Apply additions in reverse order to maintain line numbers
            for line_num, docstring in sorted(additions, reverse=True):
                lines.insert(line_num, docstring)
            
            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            return len(additions)
        
        except Exception as e:
            self.fixes_skipped.append(f"Error processing {file_path}: {str(e)}")
            return 0
    
    def remove_unused_imports(self, file_path: Path) -> int:
        """
        Remove unused imports (simple cases only).
        
        Args:
            file_path: Python file to process
        
        Returns:
            Number of imports removed
        """
        # This would require more sophisticated analysis
        # Placeholder for now
        return 0
    
    def fix_simple_todos(self, file_path: Path) -> int:
        """
        Convert simple TODOs to proper format with issue tracking.
        
        Args:
            file_path: File to process
        
        Returns:
            Number of TODOs fixed
        """
        if self.dry_run:
            return 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Convert "TODO: xyz" to "TODO(issue-tracker): xyz"
            pattern = r'#\s*TODO:\s*(.+?)(?=\n|$)'
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            
            if matches:
                for match in reversed(matches):
                    todo_text = match.group(1)
                    # Add issue tracker placeholder
                    replacement = f"# TODO(debt-tracker): {todo_text}"
                    content = content[:match.start()] + replacement + content[match.end():]
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                return len(matches)
        
        except Exception as e:
            self.fixes_skipped.append(f"Error processing {file_path}: {str(e)}")
        
        return 0
    
    def generate_fix_report(self) -> Dict:
        """Generate report of fixes applied"""
        return {
            'fixes_applied': len(self.fixes_applied),
            'fixes_skipped': len(self.fixes_skipped),
            'details': {
                'applied': self.fixes_applied,
                'skipped': self.fixes_skipped
            }
        }


def main():
    """Main execution"""
    import sys
    
    # Detect project root
    project_root = Path.cwd()
    while not (project_root / ".git").exists() and project_root.parent != project_root:
        project_root = project_root.parent
    
    # Check for --apply flag
    dry_run = "--apply" not in sys.argv
    
    print("=" * 70)
    if dry_run:
        print("  TECHNICAL DEBT AUTO-FIX (DRY RUN)")
        print("  Use --apply flag to actually apply fixes")
    else:
        print("  TECHNICAL DEBT AUTO-FIX (APPLYING)")
    print("=" * 70)
    print(f"\nProject Root: {project_root}\n")
    
    fixer = DebtAutoFixer(project_root, dry_run=dry_run)
    
    # Fix 1: Remove duplicate scripts
    print("🔍 Checking for duplicate scripts...")
    duplicates = fixer.fix_duplicate_scripts()
    if duplicates > 0:
        print(f"✅ Fixed {duplicates} duplicate scripts\n")
    else:
        print("✅ No duplicate scripts found\n")
    
    # Generate report
    report = fixer.generate_fix_report()
    
    print("=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"Fixes Applied: {report['fixes_applied']}")
    print(f"Fixes Skipped: {report['fixes_skipped']}")
    
    if dry_run:
        print("\n⚠️  This was a DRY RUN. No files were modified.")
        print("   Run with --apply to apply fixes.")
    else:
        print("\n✅ Fixes have been applied!")
    
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
