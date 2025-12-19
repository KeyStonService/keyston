# AXIOM 是 machinenativeops 的核心成員，受到嚴格的 machinenativeops 治理與命名規範

AXIOM 是一個涵蓋 AI、量子計算與全域治理的自主演化雲端環境，整合 L00~L99 級結構與 48G Gate 制，支援 Kubernetes、GitOps、Cloudflare Zero Trust、SLSA、Cosign、Kyverno、OPA、QPU 增強與向量索引系統。

平台具備自我驗證、自我修復與量子強化運算能力，命名空間治理僅為冰山一角，核心包含自動部署、供應鏈簽章、跨層調度、AI 智能決策與量子混合模組，打造具備零信任、可證明安全與可演化架構的企業級總環境。

## 📚 文檔

```bash
# 安裝依賴
pip install -r docs/requirements.txt

# 構建 HTML 文檔
cd docs
make html

# 查看文檔
open _build/html/index.html  # macOS
xdg-open _build/html/index.html  # Linux
```

## ✨ 核心功能

- **多層級架構**: L00~L99 完整的分層設計
- **48G Gate 制**: 全域策略與治理系統
- **零信任安全**: Cloudflare Zero Trust 整合
- **供應鏈安全**: SLSA、Cosign、Sigstore 整合
- **策略引擎**: Kyverno 與 OPA 雙引擎
- **量子增強**: QPU 混合運算能力
- **AI 智能**: 向量索引與智能決策
- **自主演化**: 自我驗證與自我修復

## 🚀 快速開始

```bash
# 克隆儲存庫
git clone https://github.com/axmops/axiom-enterprise-platform.git
cd axiom-enterprise-platform

# 配置環境
export AXIOM_ENV=production
export AXIOM_NAMESPACE=axiom-system

# 部署平台
kubectl create namespace $AXIOM_NAMESPACE
helm install axiom-infra charts/axiom-infrastructure \
  --namespace $AXIOM_NAMESPACE
```

詳細安裝步驟請參閱[快速開始指南](docs/intro/getting-started.rst)。

## 📖 版本管理

AXIOM 平台支援多版本文檔：

- `latest` - 最新開發版本
- `stable` - 當前穩定版本
- `v2r1`, `v2r2` - 特定發布版本

查看[版本管理文檔](docs/versions.rst)了解更多。

## 🏗️ 架構概覽

### Layer 結構

| Layer | 功能 | 主要組件 |
|-------|------|----------|
| L00-L09 | 基礎設施層 | Kubernetes, 網路, 儲存 |
| L10-L19 | 零信任安全層 | Cloudflare Zero Trust, mTLS |
| L20-L29 | 供應鏈安全層 | SLSA, Cosign, Sigstore |
| L30-L39 | 策略與治理層 | Kyverno, OPA, 48G Gate |
| L40-L49 | AI/ML 層 | 向量索引, 智能決策 |
| L50-L59 | 量子計算層 | QPU 增強, 混合運算 |
| L60-L99 | 自主演化層 | 自我驗證, 自我修復 |

### 48G Gate 系統

48G Gate 系統提供全域策略與治理能力：

- **Gate 映射**: 定義資源到 Gate 的對應關係
- **Gate 策略**: Kyverno/OPA 策略引擎
- **Gate 驗證**: 自動化驗證與報告
- **Gate 簽章**: SLSA 供應鏈簽章

## 🔒 安全性

AXIOM 平台實施多層次安全策略：

- ✅ 零信任網路架構 (Cloudflare Zero Trust)
- ✅ 供應鏈完整性驗證 (SLSA Level 3)
- ✅ 容器映像簽章 (Cosign)
- ✅ 策略即代碼 (Kyverno + OPA)
- ✅ 持續安全掃描
- ✅ 自動化合規檢查

## 🤝 貢獻

歡迎貢獻！請閱讀 [貢獻指南](CONTRIBUTING.md) 了解如何參與。

## 📝 授權

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案。

## 🔗 相關連結

- Gate bundle baseline: `ops/axiom-axm-gate-fused-v2r1.yaml.txt`
