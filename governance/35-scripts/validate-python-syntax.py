#!/usr/bin/env python3
"""
Python Syntax Validator for SynergyMesh
Python 語法驗證器

Validates Python files in the repository to ensure:
- Valid Python syntax (AST parsing)
- Proper __all__ list formatting (comma separation)
- No missing imports in __init__.py files
- Compliance with governance standards

Usage:
    python governance/35-scripts/validate-python-syntax.py
    python governance/35-scripts/validate-python-syntax.py --target tools/
    python governance/35-scripts/validate-python-syntax.py --verbose
"""

import argparse
import ast
import re
import sys
from pathlib import Path
from typing import List, Tuple


class PythonSyntaxValidator:
    """Validator for Python syntax and code quality."""

    def __init__(self, repo_root: Path, verbose: bool = False):
        self.repo_root = repo_root
        self.verbose = verbose
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.checked_files = 0
        self.passed_files = 0

    def log_info(self, message: str) -> None:
        """Log informational message."""
        if self.verbose:
            print(f"ℹ️  {message}")

    def log_success(self, message: str) -> None:
        """Log success message."""
        print(f"✅ {message}")

    def log_error(self, message: str) -> None:
        """Log error message."""
        print(f"❌ {message}")
        self.errors.append(message)

    def log_warning(self, message: str) -> None:
        """Log warning message."""
        print(f"⚠️  {message}")
        self.warnings.append(message)

    def validate_python_syntax(self, file_path: Path) -> bool:
        """Validate Python file syntax using AST parsing."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            ast.parse(code)
            return True
        except SyntaxError as e:
            self.log_error(
                f"Syntax error in {file_path.relative_to(self.repo_root)}: "
                f"Line {e.lineno}, {e.msg}"
            )
            return False
        except Exception as e:
            self.log_error(
                f"Error parsing {file_path.relative_to(self.repo_root)}: {str(e)}"
            )
            return False

    def _validate_all_with_ast(self, file_path: Path, tree: ast.AST) -> bool:
        """Validate __all__ list using AST parsing."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == '__all__':
                        if isinstance(node.value, ast.List):
                            # Check each element in the list
                            for elt in node.value.elts:
                                # Check if element is a JoinedStr (concatenated strings)
                                if isinstance(elt, ast.JoinedStr):
                                    self.log_error(
                                        f"Unexpected string concatenation in __all__ at "
                                        f"{file_path.relative_to(self.repo_root)}:line {elt.lineno}"
                                    )
                                    return False
                                # Check if element is a BinOp (also concatenation)
                                elif isinstance(elt, ast.BinOp):
                                    self.log_error(
                                        f"String concatenation in __all__ (missing comma?) at "
                                        f"{file_path.relative_to(self.repo_root)}:line {elt.lineno}"
                                    )
                                    return False
        return True

    def _validate_all_with_text(self, file_path: Path, content: str) -> bool:
        """Validate __all__ list using text-based pattern matching."""
        all_pattern = r'__all__\s*=\s*\[(.*?)\]'
        matches = re.findall(all_pattern, content, re.DOTALL)

        if not matches:
            return True

        for match in matches:
            # Check for string literals
            items = re.findall(r'"[^"]*"|\'[^\']*\'', match)
            if not items:
                continue

            # Split by newlines and check for missing commas
            lines = match.strip().split('\n')
            for i, line in enumerate(lines):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # Check if line contains a string but doesn't end with comma
                if i < len(lines) - 1:  # Not the last line
                    has_string = bool(re.search(r'"[^"]*"|\'[^\']*\'', line))
                    ends_with_comma = line.rstrip().endswith(',')

                    if has_string and not ends_with_comma:
                        # Check if next line also has a string (missing comma)
                        next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
                        if re.search(r'"[^"]*"|\'[^\']*\'', next_line):
                            # Check if this is actually string concatenation (no comma)
                            combined_lines = line + ' ' + next_line
                            # Pattern: string followed by another string without comma
                            if re.search(r'["\'][^"\']*["\']\s+["\'][^"\']*["\']', combined_lines):
                                self.log_error(
                                    f"Possible missing comma in __all__ list "
                                    f"(or unintended string concatenation) at "
                                    f"{file_path.relative_to(self.repo_root)}"
                                )
                                return False

        return True

    def validate_all_list(self, file_path: Path) -> bool:
        """Validate __all__ list has proper comma separation."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # AST-based validation
            tree = ast.parse(content)
            if not self._validate_all_with_ast(file_path, tree):
                return False

            # Text-based validation for additional patterns
            if not self._validate_all_with_text(file_path, content):
                return False

            return True

        except SyntaxError:
            # If there's a syntax error, it will be caught by validate_python_syntax
            return True
        except Exception as e:
            self.log_warning(
                f"Could not validate __all__ in {file_path.relative_to(self.repo_root)}: {str(e)}"
            )
            return True  # Don't fail on validation errors

    def validate_init_imports(self, file_path: Path) -> bool:
        """Validate __init__.py files have proper imports for __all__ items."""
        if file_path.name != '__init__.py':
            return True

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse AST to get __all__ items
            tree = ast.parse(content)

            all_items = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == '__all__':
                            if isinstance(node.value, ast.List):
                                for elt in node.value.elts:
                                    if isinstance(elt, ast.Constant):
                                        all_items.add(elt.value)

            if not all_items:
                return True

            # Check if there's a __getattr__ function (lazy loading)
            has_getattr = any(
                isinstance(node, ast.FunctionDef) and node.name == '__getattr__'
                for node in ast.walk(tree)
            )

            if has_getattr:
                self.log_info(
                    f"{file_path.relative_to(self.repo_root)} uses lazy loading (__getattr__)"
                )
                return True

            # Check for explicit imports only if not using lazy loading
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        imports.add(alias.asname if alias.asname else alias.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.asname if alias.asname else alias.name)

            # Warn if __all__ items are not imported
            missing = all_items - imports
            if missing:
                self.log_warning(
                    f"{file_path.relative_to(self.repo_root)}: "
                    f"__all__ items not explicitly imported: {', '.join(sorted(missing))}"
                )

            return True

        except Exception as e:
            self.log_warning(
                f"Could not validate imports in {file_path.relative_to(self.repo_root)}: {str(e)}"
            )
            return True

    def validate_file(self, file_path: Path) -> bool:
        """Validate a single Python file."""
        self.checked_files += 1
        self.log_info(f"Checking {file_path.relative_to(self.repo_root)}")

        all_passed = True

        # Syntax check
        if not self.validate_python_syntax(file_path):
            all_passed = False

        # __all__ check
        if not self.validate_all_list(file_path):
            all_passed = False

        # Import check for __init__.py
        if not self.validate_init_imports(file_path):
            all_passed = False

        if all_passed:
            self.passed_files += 1

        return all_passed

    def find_python_files(self, target_dir: Path) -> List[Path]:
        """Find all Python files in target directory."""
        python_files = []

        # Exclude certain directories
        exclude_patterns = {
            '__pycache__',
            '.git',
            '.venv',
            'venv',
            'node_modules',
            'dist',
            'build',
            '.eggs',
            '*.egg-info',
            '_scratch',
        }

        for py_file in target_dir.rglob('*.py'):
            # Check if file is in excluded directory
            if any(excl in py_file.parts for excl in exclude_patterns):
                continue
            python_files.append(py_file)

        return sorted(python_files)

    def validate(self, target_path: Path = None) -> bool:
        """Run validation on target directory or entire repository."""
        if target_path is None:
            target_path = self.repo_root

        print(f"\n🔍 Python Syntax Validation")
        print(f"📁 Target: {target_path.relative_to(self.repo_root) if target_path != self.repo_root else 'Repository Root'}")
        print("=" * 70)

        python_files = self.find_python_files(target_path)

        if not python_files:
            self.log_warning(f"No Python files found in {target_path}")
            return True

        print(f"\n📝 Found {len(python_files)} Python files to validate\n")

        for py_file in python_files:
            self.validate_file(py_file)

        # Print summary
        print("\n" + "=" * 70)
        print("📊 Validation Summary")
        print("=" * 70)
        print(f"✅ Files checked: {self.checked_files}")
        print(f"✅ Files passed: {self.passed_files}")
        print(f"❌ Files failed: {self.checked_files - self.passed_files}")
        print(f"❌ Errors: {len(self.errors)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")

        if self.errors:
            print("\n❌ Errors found:")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings and self.verbose:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"  - {warning}")

        print()

        if not self.errors:
            print("✅ All checks passed! Python syntax is valid.")
            return True
        else:
            print("❌ Some checks failed. Please fix the errors above.")
            return False


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Validate Python syntax in SynergyMesh repository'
    )
    parser.add_argument(
        '--target',
        type=str,
        help='Target directory to validate (relative to repo root)',
        default=None
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Determine repository root
    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent.parent

    # Determine target path
    if args.target:
        target_path = repo_root / args.target
        if not target_path.exists():
            print(f"❌ Target path does not exist: {args.target}")
            return 1
    else:
        # Default to validating key directories
        target_path = repo_root

    # Create validator and run
    validator = PythonSyntaxValidator(repo_root, verbose=args.verbose)
    success = validator.validate(target_path)

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
