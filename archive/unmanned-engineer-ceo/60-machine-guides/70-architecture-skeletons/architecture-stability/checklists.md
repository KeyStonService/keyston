# Architecture Stability Checklist for AI

在你（AI）產生任何架構變更設計前，請依序檢查以下問題。

## 1. 分層檢查（Layering Check）

- [ ] 新增/修改的模組，是否明確隸屬於某一層（core/platform/services/agents/apps）？
- [ ] 依賴關係是否只由高層指向低層，而不是反向？
- [ ] 是否存在任何跨層的直接調用（跳層調用）？
- [ ] 所有 API 邊界是否都已明確定義？

## 2. 邊界檢查（Boundary Check）

- [ ] 是否存在跨 bounded context 的直接 DB 存取？
- [ ] 是否嘗試讓 UI/Agent 直接操作資料庫或其他內部實作細節？
- [ ] 是否在 `config/system-module-map.yaml` 中明確宣告所有跨邊界依賴？
- [ ] 是否所有跨邊界通信都透過 API 或事件驅動進行？

## 3. 不變條件檢查（Invariant Check）

- [ ] 是否破壞既有 invariants（請比對 `invariants.md` 中的規則）？
- [ ] 若必須破壞某個 invariant，你是否有在 proposal 中清楚標明原因與風險？
- [ ] 是否檢查了循環依賴？（運行 `python tools/docs/validate_index.py --check cycles`）
- [ ] 是否檢查了所有公開 API 的向後相容性？

## 4. 通信協議檢查（Communication Protocol Check）

- [ ] 所有跨服務通信是否都透過明確的協議（REST、gRPC、Event Bus 等）？
- [ ] 是否存在任何隱藏通道（如直接檔案系統存取、硬編碼 IP 直連）？
- [ ] 所有通信是否都有適當的監控和日誌記錄？
- [ ] 是否考慮了通信延遲和故障場景？

## 5. 資料流檢查（Data Flow Check）

- [ ] 敏感資訊是否已隔離到專門的秘密管理服務？
- [ ] 跨邊界的資料是否都經過驗證和清理？
- [ ] 資料存儲位置是否符合法規要求（資料本地化）？
- [ ] 所有資料修改是否都有審計日誌？

## 6. 性能檢查（Performance Check）

- [ ] 服務調用深度是否不超過 4 層？
- [ ] 單個服務的公開介面數量是否不超過 50 個？
- [ ] 是否有不必要的同步調用可改為非同步？
- [ ] 是否考慮了快取、批處理等優化手段？

## 7. 可測試性檢查（Testability Check）

- [ ] 是否可以獨立測試各個服務？
- [ ] 依賴是否都可以被 Mock？
- [ ] 跨層/跨 context 的集成測試覆蓋率是否 > 80%？
- [ ] 關鍵路徑是否包含 E2E 測試？

## 8. 文檔化檢查（Documentation Check）

- [ ] 服務邊界是否已在 README 中文檔化？
- [ ] 依賴關係是否已在 `system-module-map.yaml` 中聲明？
- [ ] API 合約是否已定義（OpenAPI/gRPC proto）？
- [ ] 架構變更是否已更新相應的設計文檔？

## 9. 安全性檢查（Security Check）

- [ ] 認證授權是否在正確的層級進行？
- [ ] 是否有適當的存取控制（RBAC/ABAC）？
- [ ] 是否考慮了非拒否性和審計要求？
- [ ] 是否進行了安全威脅分析（STRIDE 等）？

## 10. 合規性檢查（Compliance Check）

- [ ] 新增服務是否符合現有的治理政策？
- [ ] 是否需要更新 `governance/policies/` 中的策略？
- [ ] 變更是否通過了 SLSA 和 SBOM 驗證？
- [ ] 是否更新了 `config/unified-config-index.yaml`？

---

## 快速檢查表（Quick Checklist）

在提交提案前，快速檢查以下項目：

```
✅ 無層級跳躍？
✅ 無隱藏通道？
✅ 無循環依賴？
✅ 無 bounded context 直連？
✅ 所有依賴已聲明？
✅ 測試覆蓋率 > 80%？
✅ 文檔已更新？
✅ 安全性已考慮？
```

全部打勾才能提交 PR！

---

## 違反情況說明

如果任何檢查項無法通過：

1. **在 `stability_report` 中詳細說明**
2. **列出所有受影響的模組**
3. **提出修正建議**
4. **標記為 `overall_status = "fail"` 或 `"warning"`**
5. **等待人類審查員決策**
