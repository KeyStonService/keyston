# .github-private - Custom Agents Architecture

## 概述 (Overview)

此目錄包含 SynergyMesh 平台的私有自訂代理程式架構。這些代理程式專為組織內部使用設計，提供進階的自動化能力和智能工作流程支援。

This directory contains the private custom agents architecture for the
SynergyMesh platform. These agents are designed for internal organizational use,
providing advanced automation capabilities and intelligent workflow support.

## 目錄結構 (Directory Structure)

```
.github-private/
├── README.md                    # 此文件 (This file)
├── agents/                      # 自訂代理程式定義
│   ├── code-review.agent.md     # 代碼審查代理
│   ├── security-scanner.agent.md # 安全掃描代理
│   ├── dependency-updater.agent.md # 依賴更新代理
│   └── workflow-optimizer.agent.md # 工作流優化代理
├── config/                      # 代理配置
│   └── agent-settings.yml       # 代理設定
└── templates/                   # 代理模板
    └── agent-template.md        # 代理模板文件
```

## 代理程式類型 (Agent Types)

### 1. Code Review Agent (代碼審查代理)

- **功能**: 自動化代碼審查、風格檢查、最佳實踐建議
- **觸發**: PR 創建或更新時
- **整合**: ESLint, TypeScript, Prettier

### 2. Security Scanner Agent (安全掃描代理)

- **功能**: 安全漏洞檢測、依賴審計、密鑰洩漏檢測
- **觸發**: 代碼變更、定時掃描
- **整合**: CodeQL, Snyk, Semgrep

### 3. Dependency Updater Agent (依賴更新代理)

- **功能**: 依賴版本檢查、自動更新 PR、相容性測試
- **觸發**: 定時檢查、手動觸發
- **整合**: Dependabot, npm audit

### 4. Workflow Optimizer Agent (工作流優化代理)

- **功能**: CI/CD 優化建議、效能分析、成本優化
- **觸發**: 工作流完成後
- **整合**: GitHub Actions Analytics

## 使用方式 (Usage)

### 啟用代理

在您的工作流程中引用代理：

```yaml
# .github/workflows/your-workflow.yml
jobs:
  review:
    uses: ./.github-private/agents/code-review.agent.md
```

### 配置代理

在 `config/agent-settings.yml` 中調整代理設定：

```yaml
agents:
  code-review:
    enabled: true
    auto_approve: false
  security-scanner:
    enabled: true
    severity_threshold: HIGH
```

## 安全性考量 (Security Considerations)

- 此目錄中的代理程式包含組織專用邏輯，不應公開
- 請確保適當的存取控制和權限設定
- 定期審查代理配置和權限

## 貢獻指南 (Contributing)

1. 創建新代理時，請遵循 `templates/agent-template.md` 格式
2. 所有變更需經過代碼審查
3. 更新此 README 以反映新增的代理

## 授權 (License)

MIT License - 僅限組織內部使用
