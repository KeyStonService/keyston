# config

## 目錄職責

此目錄為 MachineNativeOps 的**統一配置中心**，管理所有環境配置、工具設定和系統參數。

## 子目錄說明

| 子目錄 | 職責 |
|--------|------|
| `dev/` | 開發環境配置 |
| `prod/` | 生產環境配置 |
| `environments/` | 環境變數定義 |
| `agents/` | AI 代理配置 |
| `autofix/` | 自動修復機器人配置 |
| `automation/` | 自動化流程配置 |
| `ci-cd/` | CI/CD 管道配置 |
| `deployment/` | 部署相關配置 |
| `docker/` | Docker 配置 |
| `governance/` | 治理配置 |
| `integrations/` | 外部整合配置 |
| `monitoring/` | 監控配置 |
| `pipelines/` | 管道配置 |
| `security/` | 安全配置 |
| `templates/` | 配置模板 |
| `conftest/` | OPA/Conftest 策略 |
| `build-tools/` | 構建工具配置 |

## 核心配置文件

### unified-config-index.yaml
- **職責**：統一配置索引（v2.1.0）
- **功能**：所有配置的單一真實來源，對齊 governance/00-vision-strategy

### .auto-fix-bot.yml
- **職責**：Auto-Fix Bot 配置
- **功能**：自動修復 CI 失敗的規則和行為定義

### .pre-commit-config.yaml
- **職責**：Pre-commit hooks 配置
- **功能**：定義提交前執行的檢查腳本

### .eslintrc.yaml / .prettierrc / .markdownlint.json
- **職責**：Linter 配置
- **功能**：代碼風格和格式檢查規則

### cloud-agent-delegation.yml
- **職責**：雲端代理委派配置
- **功能**：定義雲端代理的任務委派規則

### dependencies.yaml
- **職責**：依賴管理配置
- **功能**：定義專案依賴和版本約束

### integrations-index.yaml
- **職責**：整合索引
- **功能**：外部系統整合的配置映射

### island-control.yml
- **職責**：Island 控制配置
- **功能**：多島嶼系統的控制參數

### yaml-module-system.yaml
- **職責**：YAML 模組系統配置
- **功能**：YAML 為基礎的模組定義和載入

## 配置層級

```
machinenativeops.yaml (根配置)
    ↓
config/unified-config-index.yaml (統一索引)
    ↓
config/{dev,prod}/*.yaml (環境配置)
    ↓
config/{module}/*.yaml (模組配置)
```

## 設計原則

1. **單一真實來源**：`unified-config-index.yaml` 為所有配置的入口
2. **環境分離**：dev/prod 配置獨立，透過環境變數切換
3. **可繼承覆蓋**：子配置可繼承父配置並覆蓋特定值
4. **敏感資訊分離**：密鑰和憑證不存放於此，使用環境變數或密鑰管理服務

## 與其他目錄的關係

- **machinenativeops.yaml**：根目錄的主配置
- **governance/**：治理相關的政策定義
- **deploy/**：使用這裡的配置進行部署
