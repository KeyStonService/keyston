# Language Dimension Mapping

# 語言維度映射

## 概述 Overview

本文檔定義了五大架構層次對應六大語言維度的治理映射，避免硬編碼依賴並確保環境差異化管理。

This document defines the governance mapping of five architectural layers to six language dimensions, avoiding hardcoded dependencies and ensuring environment differentiation.

---

## 🏗️ 五大骨架 × 六大語言維度

## Five Architectural Layers × Six Language Dimensions

### 1. 流行語言 (Popular Languages)

**代表語言 Languages:**

- Python, JavaScript/TypeScript, Go, Rust

**用途 Use Cases:**

- 快速原型開發 (Rapid prototyping)
- 治理模組自動化 (Governance automation)
- 跨平台工具鏈 (Cross-platform toolchains)

**部署提示詞 Deployment Prompt:**

```
請生成以 Python/Go 為主的治理自動化代碼，涵蓋模組責任矩陣、錯誤分類與事件追蹤。
確保代碼可在 CI/CD pipeline 中直接執行，並提供 TypeScript 範例以支援前端治理。

Generate governance automation code primarily in Python/Go, covering module responsibility 
matrix, error classification, and event tracking. Ensure code can execute directly in 
CI/CD pipeline and provide TypeScript examples for frontend governance support.
```

**示例模組 Example Modules:**

- `intelligent-automation/` - Python-based code analysis (OPTIONAL dependencies)
- `scripts/` - Shell/Python automation scripts

**治理原則 Governance Principles:**

- ✅ 不強制 Python 3.10 (No hardcoded Python 3.10)
- ✅ 支持 Python >= 3.8 (Support Python >= 3.8)
- ✅ 外部服務為可選 (External services are optional)

---

### 2. 服務器端語言 (Server-side Languages)

**代表語言 Languages:**

- Java, C#, Node.js, Kotlin, Scala

**用途 Use Cases:**

- 後端 API (Backend APIs)
- 微服務治理 (Microservices governance)
- 企業級系統 (Enterprise systems)

**部署提示詞 Deployment Prompt:**

```
請生成以 Java/C# 為主的服務器端治理代碼，定義 API 邊界、錯誤容忍策略與安全模組。
確保代碼能與微服務架構整合，並支援事件驅動治理。

Generate server-side governance code primarily in Java/C#, defining API boundaries, 
error tolerance strategies, and security modules. Ensure code integrates with 
microservices architecture and supports event-driven governance.
```

**示例模組 Example Modules:**

- `core/contract_service/` - TypeScript/Node.js contract services
- `mcp-servers/` - TypeScript MCP server implementations

**治理原則 Governance Principles:**

- ✅ Node.js >= 18.0.0 (明確版本需求)
- ✅ 使用 npm >= 8.0.0 作為包管理器
- ✅ TypeScript 嚴格模式

---

### 3. Web語言 (Web Languages)

**代表語言 Languages:**

- JavaScript, TypeScript, HTML, CSS

**用途 Use Cases:**

- UI 治理觀測 (UI governance observation)
- 前端 SDK 封裝 (Frontend SDK encapsulation)
- 治理可視化 (Governance visualization)

**部署提示詞 Deployment Prompt:**

```
請生成以 TypeScript/HTML 為主的 Web 治理代碼，將 PR/Workflow 視窗轉化為治理觀測儀。
代碼必須標示模組狀態、角色互動與錯誤分類，並支援語言邊界強制。

Generate Web governance code primarily in TypeScript/HTML, transforming PR/Workflow 
views into governance observability dashboards. Code must display module status, 
role interactions, error classification, and enforce language boundary consistency.
```

**示例模組 Example Modules:**

- `auto-fix-bot-dashboard.html` - Web dashboard
- `advanced-system-src/` - TypeScript frontend

**治理原則 Governance Principles:**

- ✅ 使用 TypeScript 進行類型安全
- ✅ 遵循 Web 標準和可訪問性
- ✅ 前後端語言邊界明確

---

### 4. 移動語言 (Mobile Languages)

**代表語言 Languages:**

- Swift, Kotlin, Dart (Flutter), React Native (JS/TS)

**用途 Use Cases:**

- 移動端治理 SDK (Mobile governance SDK)
- 觀測模組 (Observation modules)
- 跨平台治理工具 (Cross-platform governance tools)

**部署提示詞 Deployment Prompt:**

```
請生成以 Swift/Kotlin 為主的移動端治理代碼，封裝 SDK 模組並支援跨平台。
代碼必須包含 Quickstart 範例，並強制語言邊界一致性。

Generate mobile governance code primarily in Swift/Kotlin, encapsulating SDK modules 
with cross-platform support. Code must include Quickstart examples and enforce 
language boundary consistency.
```

**示例模組 Example Modules:**

- (Future) Mobile SDK modules

**治理原則 Governance Principles:**

- ✅ 平台特定依賴隔離
- ✅ 共享核心邏輯
- ✅ 跨平台兼容性驗證

---

### 5. 數據表示語言 (Data Representation Languages)

**代表語言 Languages:**

- JSON, YAML, XML, Protocol Buffers

**用途 Use Cases:**

- 治理邊界文件 (Governance boundary documents)
- 責任矩陣 (Responsibility matrix)
- 事件日誌 (Event logs)
- 配置管理 (Configuration management)

**部署提示詞 Deployment Prompt:**

```
請生成以 JSON/YAML 為主的治理數據表示文件，定義模組責任矩陣、API 規格與事件追蹤日誌。
文件必須可被自動化工具解析，並支援版本兼容性驗證。

Generate governance data representation files primarily in JSON/YAML, defining module 
responsibility matrix, API specs, and event tracking logs. Files must be parseable 
by automation tools and support version compatibility verification.
```

**示例模組 Example Modules:**

- `governance/environment-matrix/module-environment-matrix.yml` - 環境需求映射
- `.auto-fix-bot.yml` - Bot 配置
- `cloud-agent-delegation.yml` - 代理委派配置

**治理原則 Governance Principles:**

- ✅ 機器可讀格式
- ✅ Schema 驗證
- ✅ 版本兼容性追蹤

---

### 6. 其它語言 (Other Languages)

**代表語言 Languages:**

- C++, Haskell, Elixir, Zig, C

**用途 Use Cases:**

- 高性能治理模組 (High-performance governance modules)
- 安全性強化 (Security hardening)
- 函數式治理邏輯 (Functional governance logic)

**部署提示詞 Deployment Prompt:**

```
請生成以 C++/Rust 為主的高性能治理代碼，專注於安全性模組與事件驅動架構。
代碼必須支援記憶體安全檢查，並提供函數式語言範例以驗證治理閉環。

Generate high-performance governance code primarily in C++/Rust, focusing on security 
modules and event-driven architecture. Code must support memory safety checks and 
provide functional language examples for governance closure verification.
```

**示例模組 Example Modules:**

- (Future) Performance-critical security modules

**治理原則 Governance Principles:**

- ✅ 記憶體安全優先
- ✅ 零成本抽象
- ✅ 明確的錯誤處理

---

## 🎯 治理實踐 Governance Practices

### 1. 避免硬編碼依賴 Avoid Hardcoded Dependencies

**問題 Problem:**

```yaml
# ❌ 錯誤：所有項目都被強制使用相同依賴
environment:
  python: "3.10"
  requires:
    - ModelScope API
    - camel-ai
```

**解決方案 Solution:**

```yaml
# ✅ 正確：根據模組類型條件式安裝
modules:
  intelligent-automation:
    runtime: "python >= 3.8"  # 靈活版本
    optional_dependencies:
      - ModelScope API  # 標記為可選
```

### 2. 環境差異化管理 Environment Differentiation

使用 `module-environment-matrix.yml` 定義每個模組的需求：

```yaml
modules:
  core:
    primary_language: "typescript"
    runtime: "nodejs >= 18.0.0"
    requires_python: false
  
  intelligent-automation:
    primary_language: "python"
    runtime: "python >= 3.8"
    requires_nodejs: false
    optional_ai_ml: true
```

### 3. 條件式部署 Conditional Deployment

使用 `scripts/conditional-deploy.sh` 進行智能部署：

```bash
# 自動檢測模組類型並安裝對應依賴
./scripts/conditional-deploy.sh

# 只安裝必要的依賴，不套用模板
```

### 4. 語言邊界強制 Language Boundary Enforcement

**內部代碼與文檔 Internal Code & Documentation:**

- ✅ 使用繁體中文 (Traditional Chinese)
- ✅ 保持一致性

**對外整合 External Integration:**

- ✅ 提供英文版本 (English version)
- ✅ 在切換點明確標註

---

## 📊 模組映射表 Module Mapping Table

| 模組 Module | 語言維度 Dimension | 主要語言 Primary | 依賴管理 Dependencies |
|-------------|-------------------|-----------------|---------------------|
| core/ | Server-side | TypeScript | npm, 必需 |
| intelligent-automation/ | Popular | Python | pip, 可選 |
| mcp-servers/ | Server-side | TypeScript | npm, 必需 |
| scripts/ | Popular | Shell/Python | 條件式 |
| governance/environment-matrix/ | Data Representation | YAML | N/A |
| advanced-system-src/ | Web | TypeScript | npm, 必需 |

---

## 🔧 使用指南 Usage Guide

### 檢查模組需求 Check Module Requirements

```bash
# 使用治理文件檢查
cat governance/environment-matrix/module-environment-matrix.yml

# 或使用自動化腳本
./scripts/conditional-deploy.sh
```

### 添加新模組 Add New Module

1. 在 `module-environment-matrix.yml` 中定義模組
2. 指定語言維度和部署提示詞
3. 標記可選依賴
4. 更新條件式部署腳本

### 驗證治理合規性 Validate Governance Compliance

檢查清單：

- [ ] 模組未硬編碼 Python 3.10
- [ ] 可選服務明確標記為 optional
- [ ] 每個模組有專屬的環境需求定義
- [ ] 部署腳本使用條件式邏輯
- [ ] 語言邊界清晰定義

---

## 🎓 最佳實踐 Best Practices

1. **分層治理 Layered Governance**
   - 在治理層定義需求映射
   - 在部署層實現條件式安裝
   - 在代碼層實現優雅降級

2. **避免一刀切 Avoid One-Size-Fits-All**
   - 不同模組有不同需求
   - 使用模組類型檢測
   - 條件式依賴安裝

3. **清晰的錯誤訊息 Clear Error Messages**
   - 當缺少必需依賴時提供明確指引
   - 當缺少可選依賴時說明降級行為
   - 提供安裝命令範例

4. **版本靈活性 Version Flexibility**
   - 使用最小版本需求 (>=)
   - 避免固定版本 (==)
   - 在需求文件中說明原因

---

## 📚 相關文檔 Related Documentation

- [Module Environment Matrix](governance/environment-matrix/module-environment-matrix.yml)
- [Conditional Deploy Script](../scripts/conditional-deploy.sh)
- [Intelligent Automation README](../intelligent-automation/README.md)
- [Auto-Fix Bot Configuration](../.auto-fix-bot.yml)

---

**維護者 Maintainer:** SynergyMesh Team  
**最後更新 Last Updated:** 2025-11-25  
**版本 Version:** 1.0
