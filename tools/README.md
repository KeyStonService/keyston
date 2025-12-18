# 📦 Tools - 工具層 / Tools Layer

## 概述 / Overview

`tools/` 目錄包含構建、驗證、生成和運維工具，支持整個開發和部署流程。

The `tools/` directory contains build, validation, generation, and operations tools that support the entire development and deployment process.

---

## 📁 目錄結構 / Directory Structure

```
tools/
├── README.md                           # 工具層說明
│
├── 🔍 docs/                            # 文檔與知識圖工具
│   ├── README.md
│   ├── validate_index.py               # Schema 驗證器
│   ├── scan_repo_generate_index.py    # 倉庫掃描與索引生成
│   ├── generate_mndoc_from_readme.py  # MN-DOC 生成器
│   ├── generate_knowledge_graph.py    # 知識圖生成器
│   ├── project_to_superroot.py        # SuperRoot 投影
│   ├── provenance_injector.py         # SLSA 溯源注入器
│   ├── pr_comment_summary.py          # PR 註解摘要生成器
│   └── requirements.txt                # Python 依賴
│
├── 🔧 cli/                             # Admin Copilot CLI
│   ├── README.md
│   ├── package.json
│   ├── bin/
│   │   └── admin-copilot.js            # CLI 入口
│   ├── src/
│   │   ├── commands/
│   │   ├── validators/
│   │   └── reporters/
│   └── tests/
│
├── 📋 ci/                              # CI 工具
│   ├── README.md
│   ├── contract-checker.js             # 合約檢查器
│   ├── language-checker.js             # 語言檢查器
│   ├── policy-simulate.yml             # 策略模擬配置
│   ├── comprehensive-validator.js      # 綜合驗證器
│   ├── deployment-validator.js         # 部署驗證器
│   ├── doc-generator.js                # 文件生成器
│   ├── logic-validator.js              # 邏輯驗證器
│   ├── performance-analyzer.js         # 效能分析器
│   └── security-validator.js           # 安全驗證器
│
├── 🛠️ scripts/                         # 運維腳本
│   ├── README.md
│   ├── setup.sh                        # 環境設置
│   ├── check-env.sh                    # 環境檢查
│   ├── analyze.sh                      # 分析腳本
│   ├── backup.sh                       # 備份腳本
│   ├── restore.sh                      # 復原腳本
│   ├── deploy.sh                       # 部署腳本
│   ├── healthcheck.sh                  # 健康檢查
│   └── cleanup.sh                      # 清理腳本
│
├── 🚀 artifacts/                       # 構件工具
│   ├── build.sh                        # 構建腳本
│   ├── sign.sh                         # 簽名腳本
│   ├── upload.sh                       # 上傳腳本
│   └── publish.sh                      # 發佈腳本
│
├── 🔐 security/                        # 安全工具
│   ├── secret-scan.sh                  # 密鑰掃描
│   ├── dependency-check.sh             # 依賴檢查
│   ├── codeql-analyze.sh               # CodeQL 分析
│   └── slsa-verify.sh                  # SLSA 驗證
│
├── 📈 monitoring/                      # 監控工具
│   ├── metrics-exporter.js             # 指標導出器
│   ├── alert-webhook.js                # 告警 Webhook
│   └── health-check.js                 # 健康檢查
│
├── 🧪 testing/                         # 測試工具
│   ├── test-reporter.js                # 測試報告器
│   ├── coverage-analyzer.js            # 覆蓋率分析器
│   └── performance-profiler.js         # 效能分析器
│
└── 📚 documentation/                   # 文檔工具
    ├── markdown-linter.js              # Markdown 檢查
    ├── link-checker.js                 # 鏈接檢查
    └── api-doc-generator.js            # API 文檔生成器
```

---

## 🔑 核心工具 / Core Tools

### 文檔與知識圖工具 (Documentation & Knowledge Graph)

#### Schema 驗證器

```bash
python3 tools/docs/validate_index.py --verbose
python3 tools/docs/validate_index.py --config config/system-manifest.yaml
```

#### 知識圖生成

```bash
python3 tools/docs/generate_knowledge_graph.py \
  --repo-root . \
  --output docs/knowledge-graph.yaml \
  --verbose
```

#### MN-DOC 生成

```bash
python3 tools/docs/generate_mndoc_from_readme.py \
  --readme README.md \
  --output docs/generated-mndoc.yaml
```

### Admin Copilot CLI

```bash
# 安裝
npm install -g ./tools/cli

# 使用
admin-copilot analyze --repo .
admin-copilot validate --config machinenativeops.yaml
admin-copilot generate-docs --output docs/
admin-copilot deploy --environment production
```

### CI 工具

```bash
# 檢查合約
node tools/ci/contract-checker.js --contract config/api.contract.json

# 驗證部署
node tools/ci/deployment-validator.js --manifest kubernetes/manifests/

# 綜合驗證
node tools/ci/comprehensive-validator.js --repo .
```

---

## 🚀 使用指南 / Usage Guide

### 驗證配置 / Validate Configuration

```bash
# 完整驗證
make all-kg

# 單獨驗證
python3 tools/docs/validate_index.py --verbose

# 輸出詳細報告
python3 tools/docs/validate_index.py --verbose --report validation-report.json
```

### 生成文檔 / Generate Documentation

```bash
# 生成所有文檔
make all-kg

# 或單獨生成
python3 tools/docs/generate_mndoc_from_readme.py
python3 tools/docs/generate_knowledge_graph.py
python3 tools/docs/project_to_superroot.py
```

### 運行診斷 / Run Diagnostics

```bash
# 環境檢查
bash tools/scripts/check-env.sh

# 系統分析
bash tools/scripts/analyze.sh

# 健康檢查
bash tools/scripts/healthcheck.sh
```

### 部署 / Deploy

```bash
# 備份當前版本
bash tools/scripts/backup.sh

# 部署新版本
bash tools/scripts/deploy.sh --environment production

# 失敗時回滾
bash tools/scripts/restore.sh --backup latest
```

---

## 📊 工具功能對應表 / Tool Feature Matrix

| 工具 | 功能 | 輸入 | 輸出 |
|------|------|------|------|
| validate_index.py | Schema 驗證 | YAML/JSON | 驗證報告 |
| generate_knowledge_graph.py | KG 生成 | 倉庫代碼 | knowledge-graph.yaml |
| contract-checker.js | 合約驗證 | 合約定義 | 驗證結果 |
| deployment-validator.js | 部署驗證 | K8s 清單 | 驗證報告 |
| admin-copilot | CLI 工具 | 命令行 | 分析報告 |

---

## 🔒 安全工具 / Security Tools

### 密鑰掃描

```bash
bash tools/security/secret-scan.sh --repo . --strict
```

### 依賴檢查

```bash
bash tools/security/dependency-check.sh

# 更新依賴
npm audit fix
pip install --upgrade -r requirements.txt
```

### CodeQL 分析

```bash
bash tools/security/codeql-analyze.sh --repo . --language typescript
```

### SLSA 驗證

```bash
bash tools/security/slsa-verify.sh --artifact build/release.tar.gz
```

---

## 📈 效能工具 / Performance Tools

### 效能分析

```bash
node tools/ci/performance-analyzer.js \
  --input dist/ \
  --report performance-report.json
```

### 覆蓋率分析

```bash
npm run test -- --coverage
node tools/testing/coverage-analyzer.js coverage/lcov.info
```

---

## 📚 文檔工具 / Documentation Tools

### Markdown 檢查

```bash
npm run docs:lint

# 自動修復
npx markdownlint --fix "**/*.md"
```

### 鏈接檢查

```bash
node tools/documentation/link-checker.js --repo .
```

### API 文檔生成

```bash
node tools/documentation/api-doc-generator.js \
  --source src/api/ \
  --output docs/api/
```

---

## 🔄 批量操作 / Batch Operations

### 部署清單

```bash
# 備份所有資料
bash tools/scripts/backup.sh --full

# 驗證所有清單
find infrastructure/ -name "*.yaml" -exec \
  kubectl apply -f {} --dry-run=client \;

# 部署到所有環境
for env in dev staging prod; do
  bash tools/scripts/deploy.sh --environment $env
done
```

---

## 🧪 測試工具集 / Testing Toolkit

### 測試報告

```bash
npm test -- --json --outputFile=test-results.json
node tools/testing/test-reporter.js test-results.json
```

### 效能基準

```bash
npm run test:performance -- --benchmark
node tools/testing/performance-profiler.js --output perf-report.html
```

---

## 📖 工具文檔 / Tool Documentation

- [文檔工具](./docs/README.md)
- [CLI 指南](./cli/README.md)
- [CI 工具](./ci/README.md)
- [運維腳本](./scripts/README.md)
- [安全工具](./security/README.md)

---

## 🤝 貢獻指南 / Contributing

在添加新工具時：

1. 放在適當的子目錄中
2. 編寫完整的 README
3. 添加單元測試
4. 更新本文檔

---

## 📞 支援 / Support

- 📖 [工具文檔](./README.md)
- 🐛 [報告問題](https://github.com/SynergyMesh-admin/Unmanned-Island/issues)
- 💬 [討論](https://github.com/SynergyMesh-admin/Unmanned-Island/discussions)
