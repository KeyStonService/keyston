# Agent Scripts

# 代理輔助腳本

> 存放獨立的可執行腳本，用於輔助開發、測試或操作。
> Contains standalone executable scripts for development, testing, and operations.

## 📋 Overview 概述

本目錄存放代理系統的輔助腳本，這些腳本不屬於核心功能，但對於開發流程、部署自動化和日常操作非常重要。

This directory contains helper scripts for the agent system. These scripts are not part of core functionality but are essential for development workflows, deployment automation, and daily operations.

## 📁 Directory Structure 目錄結構

```
scripts/
├── development/           # 開發腳本 - Development scripts
│   ├── setup-dev-env.sh  # 設置開發環境 - Set up development environment
│   └── lint-all.sh       # 執行所有代理的 lint - Run linting for all agents
├── deployment/            # 部署腳本 - Deployment scripts
│   ├── deploy.sh         # 部署腳本 - Deployment script
│   └── rollback.sh       # 回滾腳本 - Rollback script
├── testing/               # 測試腳本 - Testing scripts
│   ├── run-unit-tests.sh  # 運行單元測試 - Run unit tests
│   └── run-integration.sh # 運行整合測試 - Run integration tests
└── operations/            # 運維腳本 - Operations scripts
    ├── health-check.sh   # 健康檢查 - Health check
    └── cleanup.sh        # 清理腳本 - Cleanup script
```

## 🎯 Purpose 用途

### ✅ What This Directory Contains 本目錄包含

| Script Type | Purpose | Examples |
|-------------|---------|----------|
| Development | 開發環境設置、代碼檢查 | `setup-dev-env.sh`, `lint-all.sh` |
| Deployment  | 自動化部署、回滾 | `deploy.sh`, `rollback.sh` |
| Testing     | 批量測試執行 | `run-unit-tests.sh`, `run-integration.sh` |
| Operations  | 日常運維、健康檢查 | `health-check.sh`, `cleanup.sh` |

### ❌ What This Directory Does NOT Contain 本目錄不包含

- Core agent logic (屬於 `src/`)
- Test files (屬於 `tests/`)
- Configuration files (屬於 `config/`)

## 🚀 Usage 使用方式

### Development Scripts 開發腳本

```bash
# 設置所有代理的開發環境
./scripts/development/setup-dev-env.sh

# 執行所有代理的 lint 檢查
./scripts/development/lint-all.sh
```

### Deployment Scripts 部署腳本

```bash
# 部署所有代理
./scripts/deployment/deploy.sh --env production

# 回滾到上一個版本
./scripts/deployment/rollback.sh --version v1.2.3
```

### Testing Scripts 測試腳本

```bash
# 運行所有代理的單元測試
./scripts/testing/run-unit-tests.sh

# 運行整合測試
./scripts/testing/run-integration.sh
```

## 📝 Script Guidelines 腳本準則

### Naming Convention 命名規範

- Use lowercase with hyphens: `setup-dev-env.sh`
- Include action verb: `run-`, `deploy-`, `check-`
- Be descriptive: `run-integration-tests.sh` not `test.sh`

### Script Requirements 腳本要求

1. **Shebang**: All scripts must start with `#!/bin/bash` or `#!/usr/bin/env python3`
2. **Documentation**: Include usage comments at the top
3. **Error Handling**: Use `set -e` for bash scripts
4. **Exit Codes**: Return appropriate exit codes (0 for success, non-zero for failure)

### Example Script Template 範例腳本模板

```bash
#!/bin/bash
# =============================================================================
# Script: example-script.sh
# Description: Brief description of what this script does
# Usage: ./example-script.sh [options]
# =============================================================================

set -e

# Script logic here
echo "Running example script..."
```

## 📖 Related Documentation 相關文檔

- [Agent README](../README.md) - 代理服務總覽
- [Deployment Guide](../../docs/DEPLOYMENT_GUIDE.md) - 部署指南
- [Development Guide](../../CONTRIBUTING.md) - 開發指南

---

**Owner 負責人**: Agent Team  
**Last Updated 最後更新**: 2025-12-15
