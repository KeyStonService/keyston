# Code Analyzer Agent

## 概述

代碼分析代理 (Code Analyzer
Agent) 是 SynergyMesh 智能自動化系統的核心組件之一，負責深度分析代碼質量、安全性和性能。

## 功能特性

### 1. 多維度代碼分析

- **靜態分析**: 語法、語義、類型檢查
- **動態分析**: 運行時行為、記憶體使用
- **安全分析**: 漏洞檢測、依賴掃描
- **性能分析**: 複雜度、效率評估

### 2. 支援的語言

- Python 3.9+
- TypeScript / JavaScript (ES6+)
- Go 1.18+
- Rust 1.60+
- Java 11+

### 3. 分析工具集成

- **SonarQube**: 代碼質量平台
- **ESLint**: JavaScript/TypeScript 靜態分析
- **Pylint**: Python 靜態分析
- **Clippy**: Rust 靜態分析
- **Golangci-lint**: Go 靜態分析

## 架構設計

```
code-analyzer/
├── src/
│   ├── analyzers/
│   │   ├── static_analyzer.py
│   │   ├── dynamic_analyzer.py
│   │   ├── security_analyzer.py
│   │   └── performance_analyzer.py
│   ├── parsers/
│   │   ├── python_parser.py
│   │   ├── typescript_parser.py
│   │   ├── go_parser.py
│   │   └── rust_parser.py
│   ├── models/
│   │   ├── issue.py
│   │   ├── result.py
│   │   └── metrics.py
│   └── engine.py
├── config/
│   ├── analyzer.yaml
│   └── rules/
├── tests/
│   ├── test_analyzers.py
│   └── fixtures/
└── README.md
```

## 使用方式

### 基本用法

```python
from code_analyzer import CodeAnalyzer

# 初始化分析器
analyzer = CodeAnalyzer(config_path="config/analyzer.yaml")

# 分析單個文件
result = await analyzer.analyze_file("path/to/file.py")

# 分析整個項目
result = await analyzer.analyze_project("path/to/project")

# 輸出結果
print(f"Quality Score: {result.quality_score}")
print(f"Issues Found: {len(result.issues)}")
```

### 配置範例

```yaml
# analyzer.yaml
enabled: true
parallel: true
max_workers: 8

analyzers:
  static:
    enabled: true
    tools: ['pylint', 'mypy']

  security:
    enabled: true
    tools: ['bandit', 'semgrep']

  performance:
    enabled: true
    complexity_threshold: 10
```

## 輸出格式

### JSON 格式

```json
{
  "analysis_id": "abc-123",
  "timestamp": "2025-11-25T14:47:00Z",
  "file_path": "src/main.py",
  "quality_score": 85.5,
  "issues": [
    {
      "id": "SEC-001",
      "type": "SECURITY",
      "severity": "HIGH",
      "line": 42,
      "message": "SQL injection risk",
      "suggestion": "Use parameterized queries"
    }
  ],
  "metrics": {
    "lines_of_code": 250,
    "cyclomatic_complexity": 8,
    "duplication_ratio": 0.02
  }
}
```

## 整合指南

### CI/CD 整合

```yaml
# .github/workflows/code-analysis.yml
name: Code Analysis

on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Code Analyzer
        run: |
          python agent/code-analyzer/src/engine.py \
            --project . \
            --output results.json
```

### 與其他 Agent 協作

1. **Vulnerability Detector**: 傳遞安全問題給漏洞檢測器進行深度分析
2. **Auto Repair**: 將檢測到的問題傳遞給自動修復器
3. **Orchestrator**: 接收編排器的任務指令

## 性能指標

- **分析速度**: 1000-5000 行代碼/秒
- **記憶體使用**: < 512 MB
- **並發能力**: 最多 16 個並行分析任務
- **準確率**: > 95%

## 開發指南

### 添加新的分析器

```python
from code_analyzer.base import BaseAnalyzer

class CustomAnalyzer(BaseAnalyzer):
    async def analyze(self, code: str, file_path: str):
        # 實現自定義分析邏輯
        issues = []
        # ... 分析代碼 ...
        return issues
```

### 測試

```bash
# 運行單元測試
pytest tests/

# 運行集成測試
pytest tests/integration/

# 生成覆蓋率報告
pytest --cov=src --cov-report=html
```

## 故障排除

### 常見問題

1. **分析速度慢**
   - 啟用增量分析
   - 增加並行工作器數量
   - 使用緩存

2. **記憶體不足**
   - 減少批次大小
   - 啟用分塊處理
   - 增加系統記憶體

3. **誤報率高**
   - 調整分析規則
   - 更新規則配置
   - 使用白名單過濾

## 路線圖

- [ ] 支援更多編程語言
- [ ] ML 驅動的智能分析
- [ ] 實時增量分析
- [ ] 分布式分析能力
- [ ] 自定義規則引擎

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 授權

MIT License
