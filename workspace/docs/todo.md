# 命名空間規範 & 驗證工具放置規範實施計劃

## Phase 1: 創建完整命名空間規範（SSOT）

- [x] 創建 root.specs.namespace.yaml（命名空間語法、層級、字元規則）
- [x] 創建 root.specs.urn.yaml（URN 格式與解析規則）
- [x] 創建 root.specs.paths.yaml（路徑與目錄分區規範）
- [x] 更新 root.specs.naming.yaml（補充完整命名規則、版本規則、10+ 格式樣例）

## Phase 2: 創建命名空間註冊表

- [x] 創建 root.registry.namespaces.yaml（已註冊命名空間清單）
- [x] 創建 root.registry.urns.yaml（已註冊 URN 清單）

## Phase 3: 創建權威驗證器（controlplane）

- [x] 創建 validators/ 子目錄
- [x] 創建 validate_naming.py（命名規則驗證器）
- [x] 創建 validate_namespace.py（命名空間驗證器）
- [x] 創建 validate_urn.py（URN 驗證器）
- [x] 創建 validate_paths.py（路徑驗證器）
- [x] 更新 validate-root-specs.py（整合所有子驗證器）
- [x] 更新 root.validation.vectors.yaml（添加命名空間測試向量）

## Phase 4: 創建開發輔助工具（workspace）

- [x] 創建 workspace/src/tooling/ 目錄結構
- [x] 創建 workspace/src/tooling/validate.py（封裝權威驗證器）
- [x] 創建 workspace/src/tooling/README.md（工具使用說明）

## Phase 5: 更新配置

- [x] 更新 controlplane/baseline/config/workspace.map.yaml（添加 toolingRoot 和 chatopsRoot）
- [x] 更新 gate-root-specs.yml（添加命名空間檢查規則）

## Phase 6: 驗證與測試

- [x] 執行 validate-root-specs.py
- [x] 驗證證據輸出到 controlplane/overlay/evidence/
- [x] 確認所有規範和驗證器正常工作（核心功能正常，部分規則需要調整）

## Phase 7: 文檔

- [x] 創建 NAMESPACE_SPECIFICATION_COMPLETE.md（完整實施報告）
