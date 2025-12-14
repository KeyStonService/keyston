# Auto Repair Agent

## 概述

自動修復代理 (Auto Repair Agent) 是智能代碼修復系統，能夠自動識別並修復代碼問題，包括安全漏洞、性能瓶頸和代碼質量問題。

## 功能特性

### 1. 智能修復引擎
- **規則基礎修復**: 基於預定義規則的快速修復
- **AST 轉換**: 基於抽象語法樹的精確修復
- **ML 驅動修復**: 機器學習輔助的智能修復
- **上下文感知**: 理解代碼上下文進行修復

### 2. 修復類型
- **安全修復**: 修復安全漏洞
- **性能優化**: 優化代碼性能
- **代碼重構**: 改善代碼結構
- **依賴更新**: 更新不安全的依賴

### 3. 驗證機制
- **測試驗證**: 自動運行測試
- **安全掃描**: 修復後重新掃描
- **性能基準**: 性能對比測試
- **回滾機制**: 自動回滾失敗修復

## 架構設計

```
auto-repair/
├── src/
│   ├── repairers/
│   │   ├── security_repairer.py
│   │   ├── performance_repairer.py
│   │   ├── quality_repairer.py
│   │   └── dependency_repairer.py
│   ├── strategies/
│   │   ├── rule_based.py
│   │   ├── ast_based.py
│   │   └── ml_based.py
│   ├── validators/
│   │   ├── test_validator.py
│   │   ├── security_validator.py
│   │   └── performance_validator.py
│   ├── models/
│   │   ├── repair.py
│   │   └── result.py
│   └── engine.py
├── config/
│   ├── repairer.yaml
│   └── strategies/
├── templates/
│   ├── security-fixes/
│   ├── performance-fixes/
│   └── quality-fixes/
├── tests/
└── README.md
```

## 使用方式

### 基本用法

```python
from auto_repair import AutoRepairer

# 初始化修復器
repairer = AutoRepairer(config_path="config/repairer.yaml")

# 修復單個問題
result = await repairer.repair_issue(
    issue=code_issue,
    strategy="rule_based"
)

# 批量修復
results = await repairer.repair_batch(
    issues=issue_list,
    auto_apply=False
)

# 驗證修復
validation = await repairer.validate_repair(
    result=result,
    run_tests=True
)
```

### 配置範例

```yaml
# repairer.yaml
enabled: true
auto_apply: false
require_review: true

strategies:
  rule_based:
    enabled: true
    priority: 1
    rules_dir: "config/rules"
  
  ast_based:
    enabled: true
    priority: 2
    transformations_dir: "config/transformations"
  
  ml_based:
    enabled: true
    priority: 3
    model_path: "models/repair-model.pkl"
    confidence_threshold: 0.85

verification:
  run_tests: true
  test_timeout: 300
  security_rescan: true
  performance_check: true
  rollback_on_failure: true

repair_rules:
  security_fixes:
    priority: 1
    auto_apply: false
    require_review: true
  
  performance_optimization:
    priority: 2
    auto_apply: false
    require_review: true
  
  code_style:
    priority: 3
    auto_apply: true
    require_review: false
```

## 修復策略

### 1. 規則基礎修復

```python
class RuleBasedRepairer:
    """規則基礎修復器"""
    
    async def repair(self, issue: CodeIssue) -> RepairResult:
        # 載入修復規則
        rule = self.load_rule(issue.id)
        
        # 應用修復模板
        fixed_code = self.apply_template(
            original_code=issue.code,
            template=rule.template
        )
        
        # 驗證修復
        if await self.validate(fixed_code):
            return RepairResult(
                status="success",
                fixed_code=fixed_code
            )
        else:
            return RepairResult(
                status="failed",
                error="Validation failed"
            )
```

### 2. AST 基礎修復

```python
import ast

class ASTBasedRepairer:
    """AST 基礎修復器"""
    
    async def repair(self, issue: CodeIssue) -> RepairResult:
        # 解析代碼為 AST
        tree = ast.parse(issue.code)
        
        # 找到需要修復的節點
        node = self.find_node(tree, issue.line)
        
        # 應用 AST 轉換
        transformer = self.get_transformer(issue.type)
        new_tree = transformer.visit(tree)
        
        # 生成修復後的代碼
        fixed_code = ast.unparse(new_tree)
        
        return RepairResult(
            status="success",
            fixed_code=fixed_code
        )
```

### 3. ML 基礎修復

```python
class MLBasedRepairer:
    """機器學習基礎修復器"""
    
    def __init__(self, model_path: str):
        self.model = self.load_model(model_path)
    
    async def repair(self, issue: CodeIssue) -> RepairResult:
        # 提取特徵
        features = self.extract_features(issue)
        
        # 預測修復方案
        prediction = self.model.predict(features)
        
        # 生成修復代碼
        fixed_code = self.generate_fix(
            original=issue.code,
            prediction=prediction
        )
        
        # 計算信心度
        confidence = self.model.predict_proba(features).max()
        
        if confidence >= 0.85:
            return RepairResult(
                status="success",
                fixed_code=fixed_code,
                confidence=confidence
            )
        else:
            return RepairResult(
                status="low_confidence",
                fixed_code=fixed_code,
                confidence=confidence
            )
```

## 修復模板

### 安全修復模板

```yaml
# SQL 注入修復
- id: SEC-002
  name: sql-injection-fix
  pattern:
    original: |
      query = "SELECT * FROM users WHERE id = " + user_id
      cursor.execute(query)
    
    replacement: |
      query = "SELECT * FROM users WHERE id = ?"
      cursor.execute(query, (user_id,))

# 硬編碼密鑰修復
- id: SEC-001
  name: hardcoded-secret-fix
  pattern:
    original: |
      API_KEY = "sk-1234567890abcdef"
    
    replacement: |
      import os
      API_KEY = os.getenv("API_KEY")
```

### 性能優化模板

```yaml
# N+1 查詢優化
- id: PERF-001
  name: n-plus-one-fix
  pattern:
    original: |
      for item in items:
          related = db.query(Related).filter(Related.id == item.id).first()
          process(item, related)
    
    replacement: |
      item_ids = [item.id for item in items]
      related_map = {r.id: r for r in db.query(Related).filter(Related.id.in_(item_ids)).all()}
      for item in items:
          related = related_map.get(item.id)
          process(item, related)
```

## 驗證流程

### 1. 測試驗證

```python
async def validate_with_tests(repair_result: RepairResult) -> bool:
    """使用測試驗證修復"""
    
    # 應用修復
    apply_fix(repair_result.fixed_code)
    
    # 運行測試
    test_result = await run_tests(
        test_suite="all",
        timeout=300
    )
    
    # 檢查測試結果
    if test_result.passed:
        return True
    else:
        # 回滾修復
        rollback_fix(repair_result)
        return False
```

### 2. 安全驗證

```python
async def validate_security(repair_result: RepairResult) -> bool:
    """安全掃描驗證"""
    
    # 重新掃描
    scan_result = await security_scan(
        code=repair_result.fixed_code
    )
    
    # 檢查是否還有相同的漏洞
    original_issue_fixed = not any(
        issue.id == repair_result.original_issue.id
        for issue in scan_result.issues
    )
    
    # 檢查是否引入新漏洞
    no_new_issues = len(scan_result.critical_issues) == 0
    
    return original_issue_fixed and no_new_issues
```

### 3. 性能驗證

```python
async def validate_performance(repair_result: RepairResult) -> bool:
    """性能基準驗證"""
    
    # 運行性能基準測試
    before = await benchmark(repair_result.original_code)
    after = await benchmark(repair_result.fixed_code)
    
    # 計算改進率
    improvement = (before.duration - after.duration) / before.duration
    
    # 檢查是否有性能退化
    if improvement < -0.05:  # 5% 退化
        return False
    
    return True
```

## 修復報告

```json
{
  "repair_id": "repair-123",
  "timestamp": "2025-11-25T14:47:00Z",
  "issue": {
    "id": "SEC-001",
    "type": "SECURITY",
    "severity": "CRITICAL"
  },
  "repair": {
    "strategy": "rule_based",
    "status": "success",
    "confidence": 0.95,
    "changes": {
      "files_modified": 1,
      "lines_added": 2,
      "lines_removed": 1
    }
  },
  "validation": {
    "tests_passed": true,
    "security_scan_passed": true,
    "performance_check_passed": true
  },
  "diff": "...",
  "evidence_hash": "abc123..."
}
```

## CI/CD 整合

```yaml
# .github/workflows/auto-repair.yml
name: Auto Repair

on:
  workflow_run:
    workflows: ["Code Analysis"]
    types: [completed]

jobs:
  auto-repair:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Load Analysis Results
        run: |
          curl -o issues.json \
            ${{ github.event.workflow_run.artifacts_url }}/issues.json
      
      - name: Run Auto Repair
        run: |
          python agent/auto-repair/src/engine.py \
            --issues issues.json \
            --auto-apply false \
            --output repairs.json
      
      - name: Create Pull Request
        if: success()
        uses: peter-evans/create-pull-request@v5
        with:
          title: "🤖 Auto-fix: Security and quality improvements"
          body: |
            This PR contains automated fixes for detected issues.
            
            Please review the changes carefully before merging.
          branch: auto-fix/${{ github.run_id }}
```

## 最佳實務

### 1. 漸進式修復
- 從簡單問題開始
- 逐步增加修復複雜度
- 持續監控修復效果

### 2. 人工審查
- Critical 和 High 優先級問題需要人工審查
- 生成詳細的修復說明
- 提供回滾機制

### 3. 持續學習
- 收集修復反饋
- 更新修復規則
- 訓練 ML 模型

## 性能指標

- **修復成功率**: > 90%
- **修復時間**: < 5 秒/問題
- **誤修復率**: < 1%
- **測試通過率**: > 99%

## 授權

MIT License
