# Python Code Quality Standards

# Python 代碼質量標準

## 📋 Overview

This document defines the Python code quality standards for the SynergyMesh
project, ensuring consistent, maintainable, and error-free Python code across
all modules.

本文檔定義了 SynergyMesh 項目的 Python 代碼質量標準，確保所有模組的 Python 代碼一致、可維護且無錯誤。

## 🎯 Quality Standards

### 1. Syntax Validation (語法驗證)

All Python files must:

- ✅ Pass AST (Abstract Syntax Tree) parsing
- ✅ Have valid syntax with no SyntaxError exceptions
- ✅ Use proper indentation (4 spaces, as per PEP 8)
- ✅ Have proper string quoting (consistent use of single or double quotes)

所有 Python 文件必須：

- ✅ 通過 AST（抽象語法樹）解析
- ✅ 具有有效語法，無 SyntaxError 異常
- ✅ 使用正確的縮進（4 個空格，符合 PEP 8）
- ✅ 使用正確的字符串引號（一致使用單引號或雙引號）

### 2. `__all__` List Standards

Package `__init__.py` files with `__all__` declarations must:

- ✅ Have all items properly separated by commas
- ✅ Use consistent string quoting
- ✅ List items in a clear, readable format
- ✅ Either use lazy loading (`__getattr__`) OR explicit imports for all items

帶有 `__all__` 聲明的包 `__init__.py` 文件必須：

- ✅ 所有項目用逗號正確分隔
- ✅ 使用一致的字符串引號
- ✅ 以清晰、可讀的格式列出項目
- ✅ 使用延遲加載（`__getattr__`）或為所有項目顯式導入

**Good Example (使用延遲加載):**

```python
def __getattr__(name):
    if name == "RefactorEngine":
        from .refactor_engine import DirectoryAnalyzer
        return DirectoryAnalyzer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "RefactorEngine",
    "CognitiveEngine",
    "LegacyScratchProcessor",
]
```

**Bad Example (缺少逗號):**

```python
__all__ = [
    "RefactorEngine"  # ❌ Missing comma!
    "CognitiveEngine",
    "LegacyScratchProcessor",
]
```

### 3. Code Formatting (代碼格式化)

Follow these formatting standards:

- **Line length**: Maximum 100 characters
- **Imports**: Sorted using isort with black profile
- **String quotes**: Prefer double quotes for consistency
- **Trailing commas**: Use in multi-line lists/dicts

遵循這些格式標準：

- **行長度**：最多 100 個字符
- **導入**：使用 isort 和 black 配置排序
- **字符串引號**：為一致性優先使用雙引號
- **尾隨逗號**：在多行列表/字典中使用

### 4. Linting Standards (代碼檢查標準)

All code must pass Ruff linting with the project configuration:

- E/W: pycodestyle errors and warnings
- F: Pyflakes checks
- I: Import order (isort)
- B: flake8-bugbear
- C4: flake8-comprehensions
- UP: pyupgrade
- ARG: flake8-unused-arguments
- SIM: flake8-simplify

所有代碼必須通過 Ruff 檢查：

- E/W：pycodestyle 錯誤和警告
- F：Pyflakes 檢查
- I：導入順序（isort）
- B：flake8-bugbear
- C4：flake8-comprehensions
- UP：pyupgrade
- ARG：flake8-unused-arguments
- SIM：flake8-simplify

## 🛠️ Validation Tools

### Automated Validation Script

Use the governance validation script:

```bash
# Validate all Python files in tools/
python governance/35-scripts/validate-python-syntax.py --target tools/

# Validate specific directory
python governance/35-scripts/validate-python-syntax.py --target core/

# Verbose output
python governance/35-scripts/validate-python-syntax.py --target tools/ --verbose
```

### Pre-commit Hooks

Install pre-commit hooks to automatically validate code:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### CI/CD Integration

Python validation runs automatically on:

- Every pull request to `main`
- Every push to `main`
- Changes to any `.py` file

GitHub Actions workflow: `.github/workflows/python-validation.yml`

## 📚 Best Practices

### 1. Module Structure

```python
"""
Module docstring describing purpose.
模組文檔字符串描述目的。
"""

__version__ = "1.0.0"
__author__ = "SynergyMesh"

# Standard library imports
import os
import sys

# Third-party imports
import yaml

# Local imports
from .local_module import LocalClass

# Lazy loading for packages
def __getattr__(name):
    # Implementation
    pass

__all__ = [
    "ExportedClass",
    "exported_function",
]
```

### 2. Error Handling

Always use specific exceptions:

```python
# Good
try:
    result = some_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
except FileNotFoundError as e:
    logger.error(f"File not found: {e}")

# Bad
try:
    result = some_operation()
except Exception:  # Too broad
    pass
```

### 3. Type Hints

Use type hints for better code clarity:

```python
from pathlib import Path
from typing import List, Dict, Optional

def validate_files(
    file_paths: List[Path],
    config: Optional[Dict[str, str]] = None
) -> bool:
    """Validate files with optional configuration."""
    pass
```

## ⚡ INSTANT Execution Compliance

To meet the project's INSTANT execution standards:

為滿足項目的即時執行標準：

1. **< 1 second understanding**: Clear, well-documented code
2. **INSTANT execution**: No blocking operations in module initialization
3. **Lazy loading**: Use `__getattr__` for expensive imports
4. **Fast validation**: Automated checks complete in < 10 seconds

5. **< 1 秒理解**：清晰、文檔完善的代碼
6. **即時執行**：模組初始化中無阻塞操作
7. **延遲加載**：對昂貴的導入使用 `__getattr__`
8. **快速驗證**：自動化檢查在 < 10 秒內完成

## 🔍 Troubleshooting

### Common Issues

#### Missing Comma in `__all__`

**Error:**

```
SyntaxError: invalid syntax
```

**Fix:** Add commas between all items in the list.

#### Import Not Found

**Error:**

```
AttributeError: module 'tools.refactor' has no attribute 'ClassName'
```

**Fix:** Either:

1. Add `__getattr__` for lazy loading, OR
2. Add explicit import: `from .module import ClassName`

#### Circular Import

**Error:**

```
ImportError: cannot import name 'X' from partially initialized module
```

**Fix:** Use lazy loading with `__getattr__` to defer imports until needed.

## 📊 Quality Metrics

Track these metrics for code quality:

| Metric             | Target | Current |
| ------------------ | ------ | ------- |
| Syntax errors      | 0      | 0 ✅    |
| Linting warnings   | < 10   | TBD     |
| Test coverage      | > 80%  | TBD     |
| Type hint coverage | > 70%  | TBD     |

## 🔄 Continuous Improvement

This standard is reviewed and updated:

- Quarterly by the platform team
- When new Python best practices emerge
- Based on team feedback

本標準定期審查和更新：

- 平台團隊每季度審查
- 新的 Python 最佳實踐出現時
- 基於團隊反饋

## 📖 References

- [PEP 8 – Style Guide for Python Code](https://pep8.org/)
- [Ruff Linter Documentation](https://docs.astral.sh/ruff/)
- [SynergyMesh Governance Matrix](../../governance/ARCHITECTURE_GOVERNANCE_MATRIX.md)
- [AI Behavior Contract](../../.github/agents/ai-behavior-contract.md)

---

**Version:** 1.0.0  
**Last Updated:** 2024-12-11  
**Owner:** Platform Engineering Team
