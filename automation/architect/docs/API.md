# Automation Architect API Documentation

# 企業級自動化代碼分析與修復系統 API 文檔

## 概述 Overview

本文檔描述了 Automation Architect 系統的 API 接口，包括代碼分析、自動修復和監控等功能。

This document describes the API interfaces of the Automation Architect system, including code analysis, auto-repair, and monitoring capabilities.

## 目錄 Table of Contents

1. [核心 API](#核心-api)
2. [分析 API](#分析-api)
3. [修復 API](#修復-api)
4. [監控 API](#監控-api)
5. [認證與授權](#認證與授權)
6. [錯誤處理](#錯誤處理)

---

## 核心 API

### AnalysisPipeline

完整的代碼分析管線。

#### 類初始化

```python
from automation_architect.core.orchestration.pipeline import AnalysisPipeline

# 創建管線實例
pipeline = AnalysisPipeline(config={
    'max_workers': 8,
    'timeout': 300,
    'cache_enabled': True
})
```

#### analyze()

執行完整的代碼分析流程。

**參數 Parameters:**

- `code_path` (str): 代碼文件或目錄路徑
- `scenario` (str, optional): 應用場景
  - `'general'`: 通用分析
  - `'drone-systems'`: 無人機系統
  - `'autonomous-driving'`: 自動駕駛
  - `'automation-iteration'`: 自動化迭代
- `enable_repair` (bool, optional): 是否啟用自動修復，默認 False
- `enable_verification` (bool, optional): 是否啟用驗證，默認 False

**返回 Returns:**

`PipelineResult` 對象，包含：

- `success` (bool): 執行是否成功
- `analysis_results` (dict): 分析結果
- `repair_results` (dict, optional): 修復結果
- `verification_results` (dict, optional): 驗證結果
- `execution_time_ms` (float): 執行時間（毫秒）
- `message` (str): 狀態消息

**示例 Example:**

```python
import asyncio
from automation_architect.core.orchestration.pipeline import AnalysisPipeline

async def main():
    pipeline = AnalysisPipeline()
    
    result = await pipeline.analyze(
        code_path="/path/to/code",
        scenario='drone-systems',
        enable_repair=True,
        enable_verification=True
    )
    
    if result.success:
        print(f"Analysis completed in {result.execution_time_ms:.2f}ms")
        print(f"Static Analysis: {result.analysis_results['static_analysis']}")
        print(f"Security Scan: {result.analysis_results['security_scan']}")
    else:
        print(f"Analysis failed: {result.message}")

asyncio.run(main())
```

---

## 分析 API

### StaticAnalyzer

靜態代碼分析器。

#### analyze()

執行靜態代碼分析。

**參數 Parameters:**

- `code_path` (str): 代碼路徑
- `language` (str, optional): 編程語言（自動檢測）
- `rules` (List[str], optional): 分析規則列表

**返回 Returns:**

`AnalysisResult` 對象，包含：

- `file_path` (str): 文件路徑
- `issues` (List[dict]): 問題列表
- `metrics` (dict): 代碼指標
- `severity_counts` (dict): 嚴重程度統計
- `analysis_time_ms` (float): 分析時間

**示例 Example:**

```python
from automation_architect.core.analysis import StaticAnalyzer

async def analyze_code():
    analyzer = StaticAnalyzer()
    
    result = await analyzer.analyze(
        code_path="/path/to/file.py",
        language='python'
    )
    
    print(f"Total issues: {len(result.issues)}")
    print(f"Severity counts: {result.severity_counts}")
    
    for issue in result.issues:
        print(f"  - {issue['type']}: {issue['message']} (Line {issue['line']})")
```

### SecurityScanner

安全漏洞掃描器。

#### scan()

執行安全掃描。

**參數 Parameters:**

- `code_path` (str): 代碼路徑
- `severity_filter` (List[str], optional): 嚴重程度過濾
  - `['critical']`: 僅嚴重問題
  - `['critical', 'high']`: 嚴重和高危問題

**返回 Returns:**

`List[SecurityIssue]` 安全問題列表。

每個 `SecurityIssue` 包含：

- `type` (str): 問題類型
- `severity` (str): 嚴重程度
- `message` (str): 問題描述
- `file` (str): 文件路徑
- `line` (int): 行號
- `cwe_id` (str, optional): CWE 編號
- `recommendation` (str, optional): 修復建議

**示例 Example:**

```python
from automation_architect.core.analysis import SecurityScanner

async def scan_security():
    scanner = SecurityScanner()
    
    issues = await scanner.scan(
        code_path="/path/to/code",
        severity_filter=['critical', 'high']
    )
    
    # 生成報告
    report = scanner.generate_report(issues)
    
    print(f"Total security issues: {report['total_issues']}")
    print(f"Critical issues: {report['severity_counts']['critical']}")
    print(f"High issues: {report['severity_counts']['high']}")
    
    if report['critical_files']:
        print("\nFiles with critical issues:")
        for file in report['critical_files']:
            print(f"  - {file}")
```

### PerformanceAnalyzer

性能分析器。

#### analyze()

執行性能分析。

**參數 Parameters:**

- `code_path` (str): 代碼路徑
- `profiling` (bool, optional): 是否執行性能分析，默認 False

**返回 Returns:**

`List[PerformanceIssue]` 性能問題列表。

**示例 Example:**

```python
from automation_architect.core.analysis import PerformanceAnalyzer

async def analyze_performance():
    analyzer = PerformanceAnalyzer()
    
    issues = await analyzer.analyze(
        code_path="/path/to/code",
        profiling=True
    )
    
    for issue in issues:
        print(f"{issue.type}: {issue.message}")
        print(f"  File: {issue.file}, Line: {issue.line}")
        if issue.suggestion:
            print(f"  Suggestion: {issue.suggestion}")
```

---

## 修復 API

### RuleEngine

基於規則的自動修復引擎。

#### add_rule()

添加自定義修復規則。

**參數 Parameters:**

- `rule` (RepairRule): 修復規則對象

**RepairRule 屬性:**

- `name` (str): 規則名稱
- `pattern` (str): 正則表達式模式
- `replacement` (str): 替換字符串
- `description` (str): 規則描述
- `auto_apply` (bool): 是否自動應用

**示例 Example:**

```python
from automation_architect.core.repair import RuleEngine, RepairRule

# 創建規則引擎
engine = RuleEngine()

# 添加自定義規則
rule = RepairRule(
    name='remove-print-statements',
    pattern=r'print\([^)]*\)',
    replacement='# Removed print statement',
    description='Remove print statements for production',
    auto_apply=True
)

engine.add_rule(rule)
```

#### apply_fixes()

應用修復規則到文件。

**參數 Parameters:**

- `file_path` (str): 文件路徑
- `auto_only` (bool, optional): 僅應用自動修復規則，默認 True

**返回 Returns:**

`RepairResult` 對象，包含：

- `file_path` (str): 文件路徑
- `rules_applied` (List[str]): 已應用的規則
- `changes_made` (int): 變更數量
- `success` (bool): 是否成功
- `message` (str): 狀態消息

**示例 Example:**

```python
from automation_architect.core.repair import RuleEngine

async def auto_fix():
    engine = RuleEngine()
    
    result = await engine.apply_fixes(
        file_path="/path/to/file.py",
        auto_only=True
    )
    
    if result.success:
        print(f"Applied {len(result.rules_applied)} rules")
        print(f"Made {result.changes_made} changes")
        print(f"Rules: {', '.join(result.rules_applied)}")
```

### ASTTransformer

AST 驅動的代碼變換器。

#### transform()

執行 AST 變換。

**參數 Parameters:**

- `code` (str): 源代碼
- `language` (str): 編程語言

**返回 Returns:**

`str` 變換後的代碼。

**示例 Example:**

```python
from automation_architect.core.repair import ASTTransformer

async def transform_code():
    transformer = ASTTransformer()
    
    original_code = """
    def example():
        x = 1
        return x
    """
    
    transformed = await transformer.transform(
        code=original_code,
        language='python'
    )
    
    print("Transformed code:")
    print(transformed)
```

---

## 監控 API

### get_statistics()

獲取管線統計信息。

**示例 Example:**

```python
from automation_architect.core.orchestration.pipeline import AnalysisPipeline

pipeline = AnalysisPipeline()
stats = pipeline.get_statistics()

print(f"Pipeline version: {stats['pipeline_version']}")
print(f"Analyzers: {stats['analyzers']}")
print(f"Repair tools: {stats['repair_tools']}")
```

### EventBus

事件總線用於系統內部通信。

#### subscribe()

訂閱事件。

**參數 Parameters:**

- `event_type` (str): 事件類型
- `handler` (Callable): 事件處理函數

**示例 Example:**

```python
from automation_architect.core.orchestration import EventBus, Event

bus = EventBus()

async def handle_analysis_complete(event: Event):
    print(f"Analysis completed: {event.data}")

bus.subscribe('analysis-complete', handle_analysis_complete)
```

#### publish()

發布事件。

**參數 Parameters:**

- `event` (Event): 事件對象

**示例 Example:**

```python
from automation_architect.core.orchestration import EventBus, Event
from datetime import datetime

bus = EventBus()

event = Event(
    type='analysis-complete',
    data={'file': 'example.py', 'issues': 5},
    timestamp=datetime.now(),
    source='static-analyzer'
)

await bus.publish(event)
```

---

## 認證與授權

### API Token 認證

使用 JWT token 進行 API 認證。

**請求頭 Headers:**

```http
Authorization: Bearer <your-token>
```

**獲取 Token:**

```python
import os

# 從環境變量獲取
api_token = os.environ.get('AUTOMATION_ARCHITECT_TOKEN')
```

### RBAC 權限控制

系統支持基於角色的訪問控制。

**角色 Roles:**

- `admin`: 完全訪問權限
- `developer`: 分析和修復權限
- `viewer`: 僅讀取權限

---

## 錯誤處理

### 錯誤代碼 Error Codes

| 代碼 | 描述 |
|------|------|
| 1000 | 一般錯誤 |
| 1001 | 文件未找到 |
| 1002 | 語法錯誤 |
| 1003 | 配置錯誤 |
| 2000 | 分析失敗 |
| 2001 | 掃描超時 |
| 3000 | 修復失敗 |
| 3001 | 驗證失敗 |

### 異常處理示例

```python
from automation_architect.core.orchestration.pipeline import AnalysisPipeline

async def safe_analysis():
    pipeline = AnalysisPipeline()
    
    try:
        result = await pipeline.analyze("/path/to/code")
        
        if not result.success:
            print(f"Analysis failed: {result.message}")
            return
        
        # 處理結果
        process_results(result)
        
    except FileNotFoundError:
        print("Code path not found")
    except TimeoutError:
        print("Analysis timeout")
    except Exception as e:
        print(f"Unexpected error: {e}")
```

---

## 批量操作 API

### 批量分析

```python
import asyncio
from automation_architect.core.orchestration.pipeline import AnalysisPipeline

async def batch_analyze(file_paths):
    pipeline = AnalysisPipeline()
    
    tasks = [
        pipeline.analyze(path, scenario='general')
        for path in file_paths
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for path, result in zip(file_paths, results):
        if isinstance(result, Exception):
            print(f"Failed to analyze {path}: {result}")
        elif result.success:
            print(f"Analyzed {path}: {len(result.analysis_results)} modules")
```

---

## 配置 API

### 加載配置

```python
import yaml
from automation_architect.core.orchestration.pipeline import AnalysisPipeline

# 從 YAML 加載配置
with open('config/automation-architect.yml') as f:
    config = yaml.safe_load(f)

pipeline = AnalysisPipeline(config=config['system'])
```

---

## 擴展 API

### 自定義分析器

```python
from automation_architect.core.analysis.static_analyzer import StaticAnalyzer

class CustomAnalyzer(StaticAnalyzer):
    async def _check_custom_rules(self, code: str, file_path: Path) -> List[Dict]:
        """自定義檢查邏輯"""
        issues = []
        # 添加自定義檢查
        return issues
    
    async def analyze(self, code_path: str, **kwargs):
        result = await super().analyze(code_path, **kwargs)
        # 添加自定義分析
        return result
```

---

## 參考資料 References

- [項目 README](../README.md)
- [配置文件說明](../config/automation-architect.yml)
- [應用場景文檔](../scenarios/)
- [CI/CD 集成指南](../.github/workflows/ci.yml)

---

**版本 Version**: 2.0.0  
**最後更新 Last Updated**: 2025-11-25
