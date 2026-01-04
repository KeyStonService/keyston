# Root Control Plane - 治理層宣告

本目錄包含 Machine Native Ops 控制面的核心治理宣告，採用聲明式配置管理整個平台的運行。

## 檔案概覽

### 核心治理檔案 (.root.*.yaml)

| 檔案 | Kind | 描述 | Schema |
|------|------|------|--------|
| `.root.config.yaml` | RootConfig | 系統基本配置 | `schemas/root.config.schema.json` |
| `.root.governance.yaml` | RootGovernance | 治理模型與角色 | `schemas/root.governance.schema.json` |
| `.root.modules.yaml` | RootModuleRegistry | 模組註冊表 | `schemas/root.modules.schema.json` |
| `.root.super-execution.yaml` | RootSuperExecution | 執行流程定義 | `schemas/root.super-execution.schema.json` |
| `.root.trust.yaml` | RootTrust | 信任模型管理 | `schemas/root.trust.schema.json` |
| `.root.provenance.yaml` | RootProvenance | 來源追蹤配置 | `schemas/root.provenance.schema.json` |
| `.root.integrity.yaml` | RootIntegrity | 完整性保護 | `schemas/root.integrity.schema.json` |
| `.root.bootstrap.yaml` | RootBootstrap | 初始化序列 | `schemas/root.bootstrap.schema.json` |
| `.root.gates.map.yaml` | RootGatesMap | 驗證閘門映射 | `schemas/root.gates.map.schema.json` |

### 作業定義 (jobs/)

| 檔案 | 描述 | 觸發閘門 |
|------|------|----------|
| `index.yaml` | 作業索引清單 | schema, attestation |
| `attestation-provenance.bundle.v1.yaml` | 來源證明捆包 | provenance, sign |
| `canonical-hash-lock.bundle.v1.yaml` | 雜湊鎖定捆包 | integrity, hash |

### 初始化腳本 (init/steps/)

| 腳本 | 描述 | 執行順序 |
|------|------|----------|
| `00-init.sh` | 環境初始化 | 00 |
| `01-governance-init.sh` | 治理初始化 | 01 |
| `02-modules-init.sh` | 模組初始化 | 02 |
| `03-super-execution-init.sh` | 執行引擎初始化 | 03 |
| `04-trust-init.sh` | 信任初始化 | 04 |
| `05-provenance-init.sh` | 來源追蹤初始化 | 05 |
| `99-finalize.sh` | 最終檢查 | 99 |

### 驗證工具 (scripts/)

| 腳本 | 功能 | 輸出 |
|------|------|------|
| `fmt.sh` | 格式化檢查 | 格式化報告 |
| `lint.sh` | 代碼檢查 | Lint 報告 |
| `schema_validate.py` | Schema 驗證 | `dist/evidence/schema.report.json` |
| `vector_test.py` | 測試向量 | `dist/evidence/vectors.report.json` |
| `policy_check.sh` | 政策檢查 | `dist/evidence/policy.report.json` |
| `render_kustomize.sh` | 資源渲染 | `dist/manifests.yaml` |

### 測試向量 (tests/vectors/)

- **valid/**: 通過驗證的測試案例
- **invalid/**: 失敗的測試案例
- **README.md**: 測試執行指南

## 治理模型

### 1. 系統配置 (RootConfig)

定義系統基本運行參數：

```yaml
spec:
  system_id: "machine-native-ops"
  timezone: "UTC"
  deployment_mode: "dev"
  default_namespace: "root-system"
```

### 2. 角色與權限 (RootGovernance)

採用最小權限原則的角色模型：

```yaml
spec:
  roles:
    - name: "admin"
      permissions: ["*"]
    - name: "operator" 
      permissions: ["read", "deploy"]
    - name: "viewer"
      permissions: ["read"]
```

### 3. 模組管理 (RootModuleRegistry)

模組化架構，支援依賴管理：

```yaml
spec:
  modules:
    - name: "governance"
      version: "v1.0.0"
      dependencies: []
      entrypoint: "deploy/kustomize/overlays/dev"
```

### 4. 執行流程 (RootSuperExecution)

定義標準執行流程：

```yaml
spec:
  flows:
    - name: "deploy"
      steps: ["bootstrap", "validate", "deploy"]
      triggers: ["manual", "commit"]
```

### 5. 信任鏈 (RootTrust)

管理數位信任關係：

```yaml
spec:
  trust_roots:
    - name: "platform-ca"
      type: "x509"
      verification_policies:
        signed_only: true
```

### 6. 來源追蹤 (RootProvenance)

完整的供應鏈可追溯性：

```yaml
spec:
  sources:
    - type: "git"
      url: "https://github.com/MachineNativeOps/machine-native-ops.git"
  audit_trails:
    - type: "log"
      target: "/var/log/root-provenance.log"
```

### 7. 完整性保護 (RootIntegrity)

防止未授權變更：

```yaml
spec:
  hash_lock:
    enabled: true
    algorithm: "sha3-512"
  drift_detection:
    enabled: true
```

### 8. 初始化序列 (RootBootstrap)

系統啟動標準流程：

```yaml
spec:
  init_sequence:
    - "00-init.sh"
    - "01-governance-init.sh"
    - "99-finalize.sh"
```

### 9. 驗證閘門 (RootGatesMap)

定義所有驗證檢查點：

```yaml
spec:
  gates:
    - name: "schema"
      inputs: ["root/.root.*.yaml"]
      tool: "jsonschema"
      pass_criteria: "all_valid"
```

## 驗證流程

### 完整驗證鏈

```bash
# 執行完整驗證
make all

# 個別步驟
make schema        # Schema 驗證
make test-vectors  # 測試向量
make render        # 資源渲染
make policy        # 政策檢查
make evidence      # 證據鏈
```

### 證據鏈輸出

每次驗證後，在 `dist/evidence/` 產生：

- `gate-report.json`: 閘門執行報告
- `digests.json`: 檔案雜湊清單
- `schema.report.json`: Schema 驗證結果
- `vectors.report.json`: 測試向量結果
- `provenance.intoto.json`: 來源證明
- `attestation.intoto.json`: 證明聲明

## 檔案大小治理

### 規範要求

- **建議上限**: 64 KB / 檔
- **硬性上限**: 256 KB / 檔
- **行數建議**: ≤ 400 行

### 拆分索引

目前所有檔案都符合大小規範，無需拆分。

未來若需要拆分，將在此處記錄：

#### 拆分原因
- [ ] 檔案超過建議上限 64KB
- [ ] 功能模組責任邊界明確
- [ ] 便于維護和審查

#### 拆分方案
- [ ] 按模組拆分（governance/modules/trust）
- [ ] 按生命週期拆分（init/runtime/teardown）
- [ ] 按政策域拆分（security/compliance/audit）

#### 入口檔聚合方式
- [ ] Kustomize configMapGenerator
- [ ] JSON Schema $ref 引用
- [ ] Shell 腳本動態組合

## 測試策略

### 有效測試案例

複製完整的 `.root.*.yaml` 到 `tests/vectors/valid/`，確保：

- 所有必需欄位存在
- 版本號符合 semver 格式
- Schema 驗證通過

### 無效測試案例

在 `tests/vectors/invalid/` 建立失敗案例：

- `missing-kind.yaml`: 缺少 kind 欄位
- `invalid-version.yaml`: 版本格式錯誤
- `missing-spec.yaml`: 缺少 spec 欄位
- `empty-roles.yaml`: 角色列表為空
- `undefined-gates.yaml`: 未定義的閘門
- `circular-dependency.yaml`: 模組循環依賴

## 變更影響分析

### 高影響變更

修改以下檔案需要特別注意：

1. **`.root.config.yaml`**: 影響整個系統配置
2. **`.root.governance.yaml`**: 影響權限和安全模型
3. **`.root.gates.map.yaml`**: 影響所有驗證流程
4. **Schema 檔案**: 影響驗證邏輯

### 中影響變更

1. **`.root.modules.yaml`**: 影響模組部署
2. **`.root.super-execution.yaml`**: 影響執行流程
3. **`.root.trust.yaml`**: 影響信任關係

### 低影響變更

1. **`.root.provenance.yaml`**: 影響審計記錄
2. **`.root.integrity.yaml`**: 影響完整性檢查
3. **`.root.bootstrap.yaml`**: 影響初始化流程

## 最佳實踐

### 1. 版本管理

- 使用語意化版本 (Semantic Versioning)
- 每次變更更新版本號
- 保持向後相容性

### 2. 變更流程

1. 修改 YAML 檔案
2. 更新對應 Schema
3. 新增/更新測試向量
4. 執行完整驗證
5. 生成證據鏈
6. 提交變更

### 3. 安全考量

- 不包含敏感資訊
- 使用最小權限原則
- 定期審查權限配置
- 監控異常行為

## 故障排除

### 常見問題

#### Schema 驗證失敗
```bash
# 檢查錯誤詳情
python root/scripts/schema_validate.py --verbose

# 檢查特定檔案
python root/scripts/schema_validate.py root/.root.config.yaml
```

#### 測試向量失敗
```bash
# 查看詳細錯誤
python root/scripts/vector_test.py --verbose

# 檢查特定測試案例
python root/scripts/vector_test.py --test missing-kind
```

#### 格式化錯誤
```bash
# 自動修復格式
make fmt

# 檢查格式問題
make fmt-check
```

## 參考資源

- [JSON Schema 規範](https://json-schema.org/)
- [Kubernetes 最佳實踐](https://kubernetes.io/docs/concepts/)
- [GitOps 模式](https://www.weave.works/technologies/gitops/)
- [SLSA Framework](https://slsa.dev/)
- [in-toto 規範](https://in-toto.io/)