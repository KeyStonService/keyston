# SBOM (Software Bill of Materials)

此目錄包含服務的軟體物料清單（SBOM），用於追蹤所有依賴項與供應鏈安全。

## 生成 SBOM

### 使用 CycloneDX

```bash
# 安裝 CycloneDX
npm install -g @cyclonedx/cyclonedx-npm

# 生成 SBOM
cyclonedx-npm --output-file sbom.json
```

### 使用 Syft

```bash
# 從 Docker 映像生成 SBOM
syft packages docker:ghcr.io/we-can-fix/synergymesh/contracts-service:latest \
  -o cyclonedx-json=sbom.json
```

## SBOM 格式

本專案使用 CycloneDX 格式的 SBOM，符合以下規範：

- CycloneDX v1.4+
- JSON 格式
- 包含所有直接與間接依賴

## 簽章與驗證

### 簽章 SBOM

```bash
# 使用 Cosign 簽章
cosign sign-blob --key cosign.key sbom.json > sbom.json.sig
```

### 驗證 SBOM

```bash
# 驗證簽章
cosign verify-blob --key cosign.pub --signature sbom.json.sig sbom.json
```

## 自動化

SBOM 會在 CI/CD 流程中自動生成與簽章：

1. 構建階段：生成 SBOM
2. 簽章階段：使用 Cosign 簽章
3. 上傳階段：將 SBOM 作為 artifact 上傳

## 相關連結

- [CycloneDX 規範](https://cyclonedx.org/)
- [SLSA 框架](https://slsa.dev/)
- [Sigstore/Cosign](https://docs.sigstore.dev/)
