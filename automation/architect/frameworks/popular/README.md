# Framework 1: Popular Languages
# 流行語言治理框架

## 支持的語言 Supported Languages

- **Python**: 智能代碼分析與修復
- **TypeScript/JavaScript**: Web 和後端應用
- **Go**: 高性能服務
- **Rust**: 系統編程與安全

## 使用場景 Use Cases

1. **快速原型開發** - Rapid prototyping
2. **治理模組自動化** - Governance automation
3. **跨平台工具鏈** - Cross-platform tooling

## 功能特性 Features

### Python 支持
- **靜態分析**: Pylint, Black, Mypy
- **安全掃描**: Bandit
- **性能分析**: py-spy
- **自動修復**: 代碼格式化, 類型註解

### TypeScript/JavaScript 支持
- **靜態分析**: ESLint, TSC
- **代碼格式**: Prettier
- **安全掃描**: npm audit
- **自動修復**: 導入優化, 類型推斷

### Go 支持
- **靜態分析**: golint, go vet
- **代碼格式**: gofmt
- **安全掃描**: gosec
- **性能分析**: pprof

### Rust 支持
- **靜態分析**: Clippy
- **代碼格式**: rustfmt
- **安全掃描**: cargo-audit
- **性能分析**: cargo-flamegraph

## 配置示例 Configuration Example

```yaml
frameworks:
  popular:
    enabled: true
    
    python:
      tools:
        - pylint
        - black
        - mypy
      auto_fix: true
    
    typescript:
      tools:
        - eslint
        - prettier
      auto_fix: true
    
    go:
      tools:
        - golint
        - gofmt
      auto_fix: true
    
    rust:
      tools:
        - clippy
        - rustfmt
      auto_fix: false
```

## 快速開始 Quick Start

```python
from automation_architect.frameworks.popular import PopularLanguagesAnalyzer

analyzer = PopularLanguagesAnalyzer()

# 分析 Python 代碼
result = await analyzer.analyze_python("/path/to/code")

# 分析 TypeScript 代碼
result = await analyzer.analyze_typescript("/path/to/code")
```
