# 測試策略 / Testing Strategy

## Testing Pyramid

1. **Unit**：ts-jest, pytest, go test；要求 70%+ 覆蓋。
2. **Integration**：Contract tests, API
   tests，連接 core/contract_service 與 agents。
3. **E2E**：`npm run dev:stack` + Cypress/Playwright。
4. **Chaos & Resilience**：參考 `chaos-engineering.md`。

## 角色與責任

- Feature Team：撰寫單元 + 整合測試。
- Platform Team：維護共用測試工具與資料集。
- Reliability Guild：策劃 chaos/game day。

## 追蹤指標

- 測試覆蓋率
- 平均修復時間 (MTTR)
- 缺陷密度
- Chaos 演練完成率
