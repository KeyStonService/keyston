# Dependency Manager Agent

## 概述

依賴管理代理 (Dependency Manager Agent) 是 SynergyMesh 智能自動化系統的組件之一，負責管理項目依賴、檢測過時套件、分析依賴漏洞和自動化更新流程。

## 功能特性

### 1. 依賴分析

- **版本檢查**: 檢測過時的依賴項
- **漏洞掃描**: 識別已知安全漏洞 (CVE)
- **許可證分析**: 驗證開源許可證合規性
- **依賴圖譜**: 視覺化依賴關係

### 2. 支援的生態系統

- npm / Node.js (package.json)
- pip / Python (requirements.txt, pyproject.toml)
- Go Modules (go.mod)
- Maven / Gradle (pom.xml, build.gradle)
- Cargo / Rust (Cargo.toml)

### 3. 自動化更新

- **安全更新**: 自動修補安全漏洞
- **版本升級**: 智能升級策略 (major/minor/patch)
- **PR 生成**: 自動建立更新 Pull Request
- **變更日誌**: 生成更新說明文件

## 架構設計

```
dependency-manager/
├── src/
│   ├── analyzers/
│   │   ├── npm_analyzer.py
│   │   ├── pip_analyzer.py
│   │   ├── go_analyzer.py
│   │   ├── maven_analyzer.py
│   │   └── cargo_analyzer.py
│   ├── scanners/
│   │   ├── vulnerability_scanner.py
│   │   ├── license_scanner.py
│   │   └── version_scanner.py
│   ├── updaters/
│   │   ├── auto_updater.py
│   │   ├── pr_generator.py
│   │   └── changelog_generator.py
│   ├── models/
│   │   ├── dependency.py
│   │   ├── vulnerability.py
│   │   └── update.py
│   └── engine.py
├── config/
│   ├── manager.yaml
│   ├── policies/
│   └── rules/
├── tests/
│   ├── test_analyzers.py
│   └── fixtures/
└── README.md
```

## 使用方式

### 基本用法

```python
from dependency_manager import DependencyManager

# 初始化管理器
manager = DependencyManager(config_path="config/manager.yaml")

# 分析項目依賴
analysis = await manager.analyze_project(
    project_path="path/to/project",
    scan_type="full"
)

# 檢測漏洞
vulnerabilities = await manager.scan_vulnerabilities(
    manifest="package.json"
)

# 輸出結果
print(f"Total Dependencies: {analysis.total_count}")
print(f"Outdated: {analysis.outdated_count}")
print(f"Vulnerabilities: {len(vulnerabilities)}")
```

### 配置範例

```yaml
# manager.yaml
enabled: true
parallel: true
max_workers: 8

ecosystems:
  npm:
    enabled: true
    manifest: "package.json"
    lock_file: "package-lock.json"
  
  pip:
    enabled: true
    manifest: ["requirements.txt", "pyproject.toml"]
  
  go:
    enabled: true
    manifest: "go.mod"

scanning:
  vulnerabilities:
    enabled: true
    sources: ["nvd", "ghsa", "osv"]
    severity_threshold: "MEDIUM"
  
  licenses:
    enabled: true
    allowed: ["MIT", "Apache-2.0", "BSD-3-Clause"]
    blocked: ["GPL-3.0"]
  
  versions:
    enabled: true
    check_major: true
    check_minor: true
    check_patch: true

update_policy:
  auto_update:
    enabled: true
    security_only: false
    
  semver:
    patch: "auto"      # 自動更新 patch 版本
    minor: "pr"        # 建立 PR 進行 minor 更新
    major: "manual"    # major 更新需人工審查
    
  scheduling:
    enabled: true
    cron: "0 2 * * 1"  # 每週一凌晨 2 點
```

## 輸出格式

### 依賴分析報告

```json
{
  "analysis_id": "dep-123",
  "timestamp": "2025-11-25T14:47:00Z",
  "project": "synergymesh",
  "ecosystem": "npm",
  "summary": {
    "total_dependencies": 150,
    "direct_dependencies": 45,
    "transitive_dependencies": 105,
    "outdated": 12,
    "vulnerable": 3
  },
  "dependencies": [
    {
      "name": "express",
      "current_version": "4.18.0",
      "latest_version": "4.21.2",
      "type": "direct",
      "status": "outdated",
      "update_type": "minor"
    }
  ],
  "vulnerabilities": [
    {
      "package": "lodash",
      "severity": "HIGH",
      "cve": "CVE-2021-23337",
      "fixed_version": "4.17.21"
    }
  ]
}
```

## 更新策略

### 1. 安全優先更新

```python
class SecurityFirstUpdater:
    """安全優先更新策略"""
    
    async def update(self, analysis: DependencyAnalysis) -> UpdateResult:
        # 優先處理安全漏洞
        vulnerable_deps = [
            dep for dep in analysis.dependencies
            if dep.has_vulnerability
        ]
        
        # 按嚴重程度排序
        sorted_deps = sorted(
            vulnerable_deps,
            key=lambda d: d.vulnerability.severity,
            reverse=True
        )
        
        # 執行更新
        results = []
        for dep in sorted_deps:
            result = await self.update_dependency(dep)
            results.append(result)
        
        return UpdateResult(updates=results)
```

### 2. 語義化版本更新

```python
class SemVerUpdater:
    """語義化版本更新策略"""
    
    def classify_update(
        self,
        current: str,
        latest: str
    ) -> UpdateType:
        """
        分類更新類型
        
        - PATCH: x.y.z -> x.y.z+1
        - MINOR: x.y.z -> x.y+1.0
        - MAJOR: x.y.z -> x+1.0.0
        """
        current_parts = parse_version(current)
        latest_parts = parse_version(latest)
        
        if latest_parts.major > current_parts.major:
            return UpdateType.MAJOR
        elif latest_parts.minor > current_parts.minor:
            return UpdateType.MINOR
        else:
            return UpdateType.PATCH
```

## 漏洞數據源

### 整合的數據源

- **NVD**: 美國國家漏洞數據庫
- **GHSA**: GitHub Security Advisories
- **OSV**: Open Source Vulnerabilities
- **Snyk**: Snyk 漏洞數據庫

### 漏洞掃描範例

```python
async def scan_vulnerabilities(manifest: str) -> List[Vulnerability]:
    """掃描依賴漏洞"""
    
    scanner = VulnerabilityScanner(
        sources=["nvd", "ghsa", "osv"]
    )
    
    dependencies = parse_manifest(manifest)
    vulnerabilities = []
    
    for dep in dependencies:
        vuln = await scanner.check(
            package=dep.name,
            version=dep.version,
            ecosystem=dep.ecosystem
        )
        if vuln:
            vulnerabilities.extend(vuln)
    
    return vulnerabilities
```

## 許可證合規

### 許可證檢查

```yaml
# license-policy.yaml
allowed_licenses:
  - MIT
  - Apache-2.0
  - BSD-2-Clause
  - BSD-3-Clause
  - ISC
  - CC0-1.0

warning_licenses:
  - LGPL-2.1
  - LGPL-3.0
  - MPL-2.0

blocked_licenses:
  - GPL-2.0
  - GPL-3.0
  - AGPL-3.0
  - SSPL-1.0

exceptions:
  - package: "gnu-readline"
    license: "GPL-3.0"
    reason: "用於開發環境，不納入生產部署"
```

## CI/CD 整合

### GitHub Actions

```yaml
# .github/workflows/dependency-check.yml
name: Dependency Check

on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: '0 2 * * 1'  # 每週一凌晨 2 點

jobs:
  dependency-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Dependency Manager
        run: |
          python agent/dependency-manager/src/engine.py \
            --project . \
            --scan-type full \
            --output dependency-report.json
      
      - name: Check for Critical Vulnerabilities
        run: |
          critical=$(jq '.summary.critical_vulnerabilities' dependency-report.json)
          if [ "$critical" -gt 0 ]; then
            echo "Found $critical critical vulnerabilities!"
            exit 1
          fi
      
      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: dependency-report
          path: dependency-report.json
```

### 自動更新 PR

```yaml
# .github/workflows/dependency-update.yml
name: Dependency Update

on:
  schedule:
    - cron: '0 2 * * 1'  # 每週一凌晨 2 點
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Dependency Update
        id: update
        run: |
          python agent/dependency-manager/src/engine.py \
            --action update \
            --policy security \
            --output updates.json
      
      - name: Create Pull Request
        if: steps.update.outputs.has_updates == 'true'
        uses: peter-evans/create-pull-request@v5
        with:
          title: "🔒 依賴安全更新"
          body: |
            此 PR 包含自動化安全更新。
            
            請審查變更並合併。
          branch: dependency-updates/${{ github.run_id }}
          reviewers: security-team
```

## 與其他 Agent 協作

### 1. 與 Vulnerability Detector 協作

- 接收漏洞檢測結果
- 提供依賴上下文資訊
- 協調修復優先級

### 2. 與 Auto Repair 協作

- 傳遞需要更新的依賴
- 接收更新結果和驗證狀態
- 處理更新失敗的回滾

### 3. 與 Orchestrator 協作

- 接收編排器的任務指令
- 報告任務執行狀態
- 參與工作流程協調

## 最佳實務

### 1. 定期掃描

- 每日掃描安全漏洞
- 每週檢查版本更新
- 每月審查許可證合規

### 2. 更新策略

- 安全更新優先處理
- 使用語義化版本
- 維護更新日誌

### 3. 依賴管理

- 最小化依賴數量
- 避免使用已棄用的套件
- 定期清理未使用的依賴

## 性能指標

- **掃描速度**: 100-500 依賴項/秒
- **準確率**: > 98%
- **誤報率**: < 2%
- **更新成功率**: > 95%

## 故障排除

### 常見問題

1. **掃描超時**
   - 增加超時時間設定
   - 啟用並行掃描
   - 使用快取機制

2. **漏洞誤報**
   - 更新漏洞數據庫
   - 配置例外規則
   - 驗證版本對應

3. **更新衝突**
   - 檢查依賴兼容性
   - 分階段更新
   - 啟用回滾機制

## 路線圖

- [ ] 支援更多包管理器 (NuGet, Composer)
- [ ] AI 驅動的更新影響分析
- [ ] 依賴健康評分系統
- [ ] 自動化 breaking change 檢測
- [ ] 依賴遷移助手

## 授權

MIT License
